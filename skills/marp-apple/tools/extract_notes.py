#!/usr/bin/env python3
"""把 Marp 里的逐页讲稿注释抽成「逐页文案与讲稿」文档。

约定：每页一条注释，形如
    <!-- 25s｜讲稿正文，可跨行 -->
或
    <!-- 25s | 讲稿正文 -->
页数按 `---` 分隔计算，封面同样计数。

用法:
    python extract_notes.py deck.md [-o build/notes.md]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

NOTE = re.compile(r"<!--\s*(\d+)s?\s*[｜|]\s*(.*?)\s*-->", re.S)
HEADING = re.compile(r"^(#{1,3})\s+(.*)$")
SKIP = re.compile(r"^(```|<!--|!\[|\||:?-{3,}|:::)")


def strip_md(line: str) -> str:
    line = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", line)
    line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)
    line = re.sub(r"[*_`]{1,3}", "", line)
    line = re.sub(r"<[^>]+>", "", line)
    return line.strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("-o", "--out")
    args = ap.parse_args()

    src = Path(args.md)
    text = src.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]

    slides = re.split(r"^---\s*$", text, flags=re.M)
    out = [f"> 由 `{src.name}` 生成，共 {len(slides)} 页。", ""]
    total_sec = 0

    for i, slide in enumerate(slides, start=1):
        title = f"第 {i} 页"
        body: list[str] = []
        note = ""
        secs = 0
        in_code = False
        for raw in slide.splitlines():
            line = raw.rstrip()
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            m = NOTE.search(line)
            if m:
                secs = int(m.group(1))
                note = " ".join(m.group(2).split())
                line = NOTE.sub("", line).strip()
            h = HEADING.match(line)
            if h and title.startswith("第"):
                title = strip_md(h.group(2))
                continue
            if not line.strip() or SKIP.match(line.strip()):
                continue
            body.append(strip_md(line))

        total_sec += secs
        out.append(f"## 第 {i} 页 · {title}")
        out.append("")
        if body:
            out.extend(body)
            out.append("")
        if note:
            out.append(f"**讲稿（{secs} 秒 / 约 {len(note)} 字）**")
            out.append("")
            out.append(note)
            out.append("")

    out.append(f"讲稿合计约 {total_sec} 秒（{total_sec // 60}:{total_sec % 60:02d}）。")
    dest = Path(args.out) if args.out else src.with_name(src.stem + ".notes.md")
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{len(slides)} 页，讲稿 {total_sec} 秒 → {dest}")


if __name__ == "__main__":
    main()
