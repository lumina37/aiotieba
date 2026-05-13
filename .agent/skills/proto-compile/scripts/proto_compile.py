from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


API_ROOT = Path("src/aiotieba/api")
COMMON_PROTO_DIR = API_ROOT / "_protobuf"


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


def post_process(proto_dir: Path, import_prefix: str) -> None:
    for file_path in proto_dir.glob("*_pb2.py"):
        tmp_file_path = file_path.with_suffix(".tmp")
        with (
            file_path.open("r") as file,
            tmp_file_path.open("w") as tmp_file,
        ):
            tmp_file.writelines(row_filter(file, import_prefix))
        file_path.unlink()
        tmp_file_path.rename(file_path)


def compile_common() -> None:
    for file_path in COMMON_PROTO_DIR.glob("*_pb2.py"):
        file_path.unlink()

    subprocess.run(
        "protoc --python_out=. *.proto",
        cwd=COMMON_PROTO_DIR,
        check=True,
        timeout=60.0,
    )

    post_process(COMMON_PROTO_DIR, "from . ")
    run_ruff(COMMON_PROTO_DIR)


def compile_api(api_dir: Path) -> None:
    proto_dir = api_dir / "protobuf"
    if not proto_dir.is_dir():
        return

    for file_path in proto_dir.glob("*_pb2.py"):
        file_path.unlink()

    subprocess.run(
        "protoc -I../../_protobuf -I. --python_out=. *.proto",
        cwd=proto_dir,
        check=True,
        timeout=60.0,
    )

    post_process(proto_dir, "from ..._protobuf ")
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

    args = parser.parse_args()

    if args.all:
        compile_common()
        for api_path in API_ROOT.iterdir():
            if api_path.is_dir() and (api_path / "protobuf").is_dir():
                compile_api(api_path)
    elif args.common:
        compile_common()
    elif args.directory:
        for dir_name in args.directory:
            api_path = API_ROOT / dir_name
            proto_dir = api_path / "protobuf"
            if not proto_dir.is_dir():
                print(
                    f"目录 '{api_path}' 不包含protobuf子目录",
                    file=sys.stderr,
                )
                continue
            compile_api(api_path)
    else:
        parser.print_help()
        return


if __name__ == "__main__":
    main()
