from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


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


commom_proto_path = Path("src/aiotieba/api/_protobuf")

for file_path in commom_proto_path.glob("*_pb2.py"):
    file_path.unlink()

subprocess.run("protoc --python_out=. *.proto", cwd=commom_proto_path, check=True, timeout=60.0)

for file_path in commom_proto_path.glob("*_pb2.py"):
    tmp_file_path = file_path.with_suffix(".tmp")
    with (
        file_path.open("r") as file,
        tmp_file_path.open("w") as tmp_file,
    ):
        tmp_file.writelines(row_filter(file, "from . "))
    file_path.unlink()
    tmp_file_path.rename(file_path)

for api_path in Path("src/aiotieba/api").glob("*/protobuf"):
    for file_path in api_path.glob("*_pb2.py"):
        file_path.unlink()

    subprocess.run("protoc -I../../_protobuf -I. --python_out=. *.proto", cwd=api_path, check=True, timeout=60.0)

    for file_path in api_path.glob("*_pb2.py"):
        tmp_file_path = file_path.with_suffix(".tmp")
        with (
            file_path.open("r") as file,
            tmp_file_path.open("w") as tmp_file,
        ):
            tmp_file.writelines(row_filter(file, "from ..._protobuf "))
        file_path.unlink()
        tmp_file_path.rename(file_path)

subprocess.run("uvx ruff check src/**/*_pb2.py --fix --unsafe-fixes -s", timeout=60.0)
subprocess.run("uvx ruff format src/**/*_pb2.py -s", timeout=60.0)
