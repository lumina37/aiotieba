import subprocess
from pathlib import Path

commom_proto_pth = Path("aiotieba/api/_protobuf")

for fpth in commom_proto_pth.glob('*_pb2.py'):
    fpth.unlink()

subprocess.run("protoc --python_out=. *.proto", cwd=str(commom_proto_pth), check=True, timeout=60.0)

for fpth in commom_proto_pth.glob('*_pb2.py'):
    bak_fpth = fpth.with_suffix('.bak')
    with (
        fpth.open('r') as f,
        bak_fpth.open('w') as bak_f,
    ):
        for row in f.readlines():
            if row.startswith('#'):
                continue
            if row.startswith('import'):
                row = "from . " + row
            bak_f.write(row)
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
            for row in f.readlines():
                if row.startswith('#'):
                    continue
                if row.startswith('import'):
                    row = "from ..._protobuf " + row
                bak_f.write(row)
        fpth.unlink()
        bak_fpth.rename(fpth)

subprocess.run("ruff . --fix", cwd='.', check=False, timeout=10.0)
subprocess.run("black .", cwd='.', check=False, timeout=30.0)
