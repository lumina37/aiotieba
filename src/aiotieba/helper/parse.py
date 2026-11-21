from __future__ import annotations

import re

from lxml import etree, html

_CHARSET_EXP = re.compile(rb"""charset=["']?([\w-]+)""", re.IGNORECASE)


def _detect_encoding(body: bytes) -> str:
    match = _CHARSET_EXP.search(body[:4096])
    if match is not None:
        return match.group(1).decode("ascii")

    try:
        body.decode("utf-8")
    except UnicodeDecodeError:
        return "gb18030"

    return "utf-8"


def parse_html(body: bytes) -> etree._Element:
    """
    解析完整的HTML文档

    Args:
        body (bytes): 待解析的HTML

    Returns:
        etree._Element: 文档根节点
    """

    parser = etree.HTMLParser(encoding=_detect_encoding(body), recover=True, no_network=True)
    return html.fromstring(body, parser=parser)


def parse_html_fragment(content: str) -> etree._Element:
    """
    解析HTML片段

    Args:
        content (str): 待解析的HTML片段

    Returns:
        etree._Element: 包裹片段的div节点
    """

    return html.fragment_fromstring(content, create_parent="div")


def text_of(element: etree._Element) -> str:
    """
    获取节点及其所有子节点的文本

    Args:
        element (etree._Element): 节点

    Returns:
        str: 文本内容
    """

    return "".join(element.itertext())


def text_stripped(element: etree._Element) -> str:
    """
    获取节点及其所有子节点的文本 并去除各文本段的首尾空白

    Args:
        element (etree._Element): 节点

    Returns:
        str: 文本内容
    """

    return "".join(part.strip() for part in element.itertext())


def class_tokens(element: etree._Element) -> list[str]:
    """
    获取节点的class列表

    Args:
        element (etree._Element): 节点

    Returns:
        list[str]: class列表
    """

    return (element.get("class") or "").split()
