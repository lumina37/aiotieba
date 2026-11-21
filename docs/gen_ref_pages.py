"""为类型定义页面生成SUMMARY并补齐缺失的数据类型页面

已有的`docs/ref/classdef/*.md`保持原样以维持既有URL
仅当某个`_classdef.py`未被任何页面引用时才自动生成新页面
"""

from __future__ import annotations

import re
from pathlib import Path

import mkdocs_gen_files

DOCS_DIR = Path("docs")
PAGE_DIR = DOCS_DIR / "ref" / "classdef"
SRC_DIR = Path("src") / "aiotieba" / "api"

_CAMEL_BOUNDARY = re.compile(r"(?<!^)(?=[A-Z])")


def _snake_case(name: str) -> str:
    return _CAMEL_BOUNDARY.sub("_", name).lower()


def _documented_pages() -> dict[str, str]:
    """收集现有页面 返回 模块名 -> 页面文件名"""
    documented: dict[str, str] = {}

    for page in PAGE_DIR.glob("*.md"):
        for line in page.read_text(encoding="utf-8").splitlines():
            if line.startswith(":::"):
                module = line[3:].strip().split(maxsplit=1)[0]
                documented[module] = page.name

    return documented


def main() -> None:
    documented = _documented_pages()
    generated: list[str] = []

    for classdef in sorted(SRC_DIR.rglob("_classdef.py")):
        module = ".".join(classdef.relative_to("src").with_suffix("").parts)
        if module in documented:
            continue

        page_name = f"{_snake_case(classdef.parent.name)}.md"
        if page_name in documented.values() or (PAGE_DIR / page_name).exists():
            continue

        with mkdocs_gen_files.open(f"ref/classdef/{page_name}", "w") as fd:
            fd.write(f"::: {module}\n")
        generated.append(page_name)

    pages = sorted({page.name for page in PAGE_DIR.glob("*.md")} | set(generated))

    with mkdocs_gen_files.open("ref/classdef/SUMMARY.md", "w") as fd:
        for page_name in pages:
            fd.write(f"* [{Path(page_name).stem}]({page_name})\n")


main()
