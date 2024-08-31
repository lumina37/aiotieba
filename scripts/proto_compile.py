from __future__ import annotations

import subprocess
from collections.abc import Iterator
from pathlib import Path

commom_proto_pth = Path("aiotieba/api/_protobuf")

for fpth in commom_proto_pth.glob('*_pb2.py'):
    fpth.unlink()

subprocess.run("protoc --python_out=. *.proto", cwd=str(commom_proto_pth), check=True, timeout=60.0)


def row_filter(rows: list[str], import_perfix: str) -> Iterator[str]:
    is_runtime_checker = False
    for row in rows:
        if row.startswith('#'):
            continue

        if not is_runtime_checker and row.startswith("_runtime"):
            is_runtime_checker = True
        if is_runtime_checker and row.startswith(')'):
            is_runtime_checker = False
            continue
        if is_runtime_checker:
            continue

        if "import runtime_version" in row:
            continue

        if row.startswith("import"):
            row = import_perfix + row

        yield row


for fpth in commom_proto_pth.glob('*_pb2.py'):
    bak_fpth = fpth.with_suffix('.bak')
    with (
        fpth.open('r') as f,
        bak_fpth.open('w') as bak_f,
    ):
        bak_f.writelines(row_filter(f, "from . "))
    fpth.unlink()
    bak_fpth.rename(fpth)

for mod_pth in Path("aiotieba/api").glob('*/protobuf'):
    for fpth in mod_pth.glob('*_pb2.py'):
        fpth.unlink()

    subprocess.run("protoc -I../../_protobuf -I. --python_out=. *.proto", cwd=str(mod_pth), check=True, timeout=10.0)

    for fpth in mod_pth.glob('*_pb2.py'):
        bak_fpth = fpth.with_suffix('.bak')
        with (
            fpth.open('r') as f,
            bak_fpth.open('w') as bak_f,
        ):
            bak_f.writelines(row_filter(f, "from ..._protobuf "))
        fpth.unlink()
        bak_fpth.rename(fpth)

subprocess.run("rye lint . --fix -- --unsafe-fixes", cwd='.', check=False, timeout=10.0)
subprocess.run("rye fmt .", cwd='.', check=False, timeout=30.0)
