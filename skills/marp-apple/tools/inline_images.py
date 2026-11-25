#!/usr/bin/env python3
"""把 Marp 导出的 HTML 变成可单文件分发的版本。

用法:
    python inline_images.py build/deck.html [-o build/deck.inline.html] [--renumber]

做的事:
  1. 把 <img src="相对路径"> 内联成 data URI；
  2. 给 <html> 加 lang="zh-CN"（已有则不动）；
  3. 外链加 target="_blank" rel="noopener"；
  4. --renumber=auto 时，若第一页是 `lead` 页（封面）就把页码整体减一：封面不显示、
     正文从 1 起；没有封面则不动。也可写死 on/off。
     只改网页里 section 的 data-marpit-pagination 属性；PDF 由 build_pdf.py 处理。
"""

from __future__ import annotations

import argparse
import base64
import mimetypes
import re
from pathlib import Path

IMG = re.compile(r'<img\b[^>]*?\bsrc="([^"]+)"[^>]*>')
HTML_TAG = re.compile(r"<html\b[^>]*>", re.I)
LINK = re.compile(r'<a\b[^>]*\bhref="(https?://[^"]+)"[^>]*>')
FIRST_SECTION = re.compile(r"<section\b[^>]*>", re.I)
PAGE = re.compile(r'<section\b[^>]*?\sdata-marpit-pagination="(\d+)"')


def has_cover(text: str) -> bool:
    m = FIRST_SECTION.search(text)
    if not m:
        return False
    cls = re.search(r'class="([^"]*)"', m.group(0))
    return bool(cls and "lead" in cls.group(1).split())


def renumber(text: str) -> tuple[str, int]:
    """页码减一；结果 <= 0 的页（封面）去掉该属性。"""
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        n = int(m.group(1)) - 1
        count += 1
        if n <= 0:
            return m.group(0).replace(f' data-marpit-pagination="{m.group(1)}"', "", 1)
        return m.group(0).replace(f'data-marpit-pagination="{m.group(1)}"',
                                  f'data-marpit-pagination="{n}"', 1)

    return PAGE.sub(repl, text), count


def to_data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("-o", "--out")
    ap.add_argument("--renumber", choices=("auto", "on", "off"), default="off",
                    help="页码处理：auto 看第一页是否封面，on/off 强制（只影响网页）")
    args = ap.parse_args()

    src = Path(args.html)
    out = Path(args.out) if args.out else src.with_suffix(".inline.html")
    text = src.read_text(encoding="utf-8")
    root = src.parent

    inlined = 0

    def repl(m: re.Match) -> str:
        nonlocal inlined
        url = m.group(1)
        if url.startswith(("data:", "http://", "https://")):
            return m.group(0)
        path = (root / url).resolve()
        if not path.is_file():
            print(f"缺图: {url}")
            return m.group(0)
        inlined += 1
        return m.group(0).replace(url, to_data_uri(path), 1)

    text = IMG.sub(repl, text)

    def html_tag(m: re.Match) -> str:
        tag = m.group(0)
        if re.search(r'\blang="', tag):
            return tag
        return tag[:-1] + ' lang="zh-CN">'

    text = HTML_TAG.sub(html_tag, text, count=1)

    def link(m: re.Match) -> str:
        tag = m.group(0)
        if "target=" in tag:
            return tag
        return tag[:-1] + ' target="_blank" rel="noopener">'

    text = LINK.sub(link, text)

    pages = 0
    if args.renumber == "on" or (args.renumber == "auto" and has_cover(text)):
        text, pages = renumber(text)

    out.write_text(text, encoding="utf-8")
    size = out.stat().st_size / 1024 / 1024
    extra = f"，重排 {pages} 页页码" if pages else ""
    print(f"内联 {inlined} 张图片 → {out}（{size:.1f} MB）{extra}")


if __name__ == "__main__":
    main()
