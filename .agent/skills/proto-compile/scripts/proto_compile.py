from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from aiotieba.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Iterator

LOG = get_logger()

API_ROOT = Path("src/aiotieba/api")
COMMON_PROTO_DIR = API_ROOT / "_protobuf"

GENERATED_PATTERNS = ("*_pb2.py", "*_pb2.pyi")
STUB_PATTERN = "*_pb2.pyi"


def row_filter(rows: list[str], import_perfix: str) -> Iterator[str]:
    is_runtime_checker = False
    for row in rows:
        if row.startswith("#"):
            continue
        if row.startswith('"""'):
            continue

        if not is_runtime_checker and row.startswith("_runtime"):
            is_runtime_checker = True
        if is_runtime_checker and row.startswith(")"):
            is_runtime_checker = False
            continue
        if is_runtime_checker:
            continue

        if "import runtime_version" in row:
            continue

        if row.startswith("import"):
            row = import_perfix + row

        yield row


def post_process(proto_dir: Path, import_prefix: str, stubs_only: bool = False) -> None:
    patterns = (STUB_PATTERN,) if stubs_only else GENERATED_PATTERNS
    for pattern in patterns:
        for file_path in proto_dir.glob(pattern):
            tmp_file_path = file_path.with_suffix(".tmp")
            with (
                file_path.open("r", encoding="utf-8") as file,
                tmp_file_path.open("w", encoding="utf-8", newline="\n") as tmp_file,
            ):
                tmp_file.writelines(row_filter(file, import_prefix))
            file_path.unlink()
            tmp_file_path.rename(file_path)


def remove_generated(proto_dir: Path, stubs_only: bool) -> None:
    patterns = (STUB_PATTERN,) if stubs_only else GENERATED_PATTERNS
    for pattern in patterns:
        for file_path in proto_dir.glob(pattern):
            if file_path.is_file():
                file_path.unlink()


def run_protoc(proto_dir: Path, stubs_only: bool, includes: str = "") -> None:
    out_arg = "--pyi_out=." if stubs_only else "--python_out=. --pyi_out=."
    subprocess.run(
        f"protoc {includes}{out_arg} *.proto",
        cwd=proto_dir,
        check=True,
        timeout=60.0,
    )


def compile_common(stubs_only: bool) -> None:
    remove_generated(COMMON_PROTO_DIR, stubs_only)
    run_protoc(COMMON_PROTO_DIR, stubs_only)
    post_process(COMMON_PROTO_DIR, "from . ", stubs_only)
    if not stubs_only:
        run_ruff(COMMON_PROTO_DIR)


def compile_api(api_dir: Path, stubs_only: bool) -> None:
    proto_dir = api_dir / "protobuf"
    if not proto_dir.is_dir() or not any(proto_dir.glob("*.proto")):
        return

    remove_generated(proto_dir, stubs_only)
    run_protoc(proto_dir, stubs_only, includes="-I../../_protobuf -I. ")
    post_process(proto_dir, "from ..._protobuf ", stubs_only)
    if not stubs_only:
        run_ruff(proto_dir)


def run_ruff(proto_dir: Path) -> None:
    proto_file_pattern = proto_dir / "*_pb2.py"
    subprocess.run(
        f"uvx ruff check {proto_file_pattern} --fix --unsafe-fixes -s",
        timeout=60.0,
    )
    subprocess.run(
        f"uvx ruff format {proto_file_pattern} -s",
        timeout=60.0,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="编译.proto文件",
    )
    parser.add_argument(
        "-d",
        "--directory",
        action="append",
        metavar="目录",
        help="只编译指定的API目录（例如get_posts）。可多次指定",
    )
    parser.add_argument(
        "-c",
        "--common",
        action="store_true",
        help="只编译公共_protobuf目录",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="编译所有API目录和公共_protobuf目录。会覆盖-d和-c的设置",
    )
    parser.add_argument(
        "-s",
        "--stubs",
        action="store_true",
        help="只生成类型存根(.pyi) 不重新生成_pb2.py",
    )

    args = parser.parse_args()

    if args.all:
        compile_common(args.stubs)
        for api_path in API_ROOT.iterdir():
            if api_path.is_dir() and (api_path / "protobuf").is_dir():
                compile_api(api_path, args.stubs)
    elif args.common:
        compile_common(args.stubs)
    elif args.directory:
        for dir_name in args.directory:
            api_path = API_ROOT / dir_name
            proto_dir = api_path / "protobuf"
            if not proto_dir.is_dir():
                LOG.error("目录 '%s' 不包含protobuf子目录", api_path)
                continue
            compile_api(api_path, args.stubs)
    else:
        parser.print_help()
        return


if __name__ == "__main__":
    main()
