from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from aiohttp.multipart import parse_content_disposition

from aiotieba.logging import get_logger

NL = b"\r\n"
DOUBLE_NL = NL + NL

LOG = get_logger()


def extract_boundary(data: bytes) -> str:
    end = data.find(NL)
    first_line = data[:end]
    if not first_line.startswith(b"--"):
        LOG.error("文件首行不是合法的multipart boundary分隔符: %s", first_line)
        return

    boundary = first_line[2:].decode("utf-8", errors="replace")

    return boundary


def parse_multipart_body(body_data: bytes, boundary: str) -> dict[str, bytes]:
    parts: dict[str, bytes] = {}
    sep = f"--{boundary}".encode()

    for chunk in body_data.split(sep):
        if chunk in (b"", b"--"):
            continue

        header_end = chunk.find(DOUBLE_NL)
        if header_end == -1:
            continue

        header_section = chunk[:header_end]
        part_body = chunk[header_end + len(DOUBLE_NL) :]

        part_body = part_body.removesuffix(NL)
        header_section = header_section.removeprefix(NL)

        for line in header_section.decode("utf-8", errors="replace").split(NL.decode()):
            if line.lower().startswith("content-disposition:"):
                _, params = parse_content_disposition(line.split(":", 1)[1].strip())
                name = params.get("name", "")
                parts[name] = part_body
                break

    return parts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="从multipart二进制文件中提取protobuf载荷并用protoc --decode_raw解码",
    )
    parser.add_argument("file", type=Path, help="包含multipart payload的二进制文件路径")

    args = parser.parse_args()

    binary_file: Path = args.file
    if not binary_file.is_file():
        LOG.error("文件不存在: %s", binary_file)
        return

    data = binary_file.read_bytes()

    boundary = extract_boundary(data)
    if not boundary:
        LOG.error("无法提取boundary分隔符")
        return
    parts = parse_multipart_body(data, boundary)

    target_data = parts.get("data")
    if target_data is None:
        LOG.error("在multipart中未找到name='data'的字段，可用字段: %s", sorted(parts.keys()))
        return

    proc = subprocess.run(
        ["protoc", "--decode_raw"],
        input=target_data,
        capture_output=True,
        timeout=60.0,
    )

    if proc.returncode != 0:
        LOG.error("protoc解码失败: %s", proc.stderr.decode("utf-8", errors="replace"))
        return

    decoded = proc.stdout.decode("utf-8", errors="replace")

    print(decoded)


if __name__ == "__main__":
    main()
