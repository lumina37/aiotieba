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


commom_proto_pth = Path("src/aiotieba/api/_protobuf")

for fpth in commom_proto_pth.glob("*_pb2.py"):
    fpth.unlink()

subprocess.run("protoc --python_out=. *.proto", cwd=commom_proto_pth, check=True, timeout=60.0)

for fpth in commom_proto_pth.glob("*_pb2.py"):
    tmp_fpth = fpth.with_suffix(".tmp")
    with (
        fpth.open("r") as f,
        tmp_fpth.open("w") as tmp_f,
    ):
        tmp_f.writelines(row_filter(f, "from . "))
    fpth.unlink()
    tmp_fpth.rename(fpth)

for api_pth in Path("src/aiotieba/api").glob("*/protobuf"):
    for fpth in api_pth.glob("*_pb2.py"):
        fpth.unlink()

    subprocess.run("protoc -I../../_protobuf -I. --python_out=. *.proto", cwd=api_pth, check=True, timeout=60.0)

    for fpth in api_pth.glob("*_pb2.py"):
        tmp_fpth = fpth.with_suffix(".tmp")
        with (
            fpth.open("r") as f,
            tmp_fpth.open("w") as tmp_f,
        ):
            tmp_f.writelines(row_filter(f, "from ..._protobuf "))
        fpth.unlink()
        tmp_fpth.rename(fpth)

subprocess.run("uvx ruff check src/**/*_pb2.py --fix --unsafe-fixes -s", timeout=60.0)
subprocess.run("uvx ruff format src/**/*_pb2.py -s", timeout=60.0)
