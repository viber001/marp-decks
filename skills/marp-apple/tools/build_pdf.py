#!/usr/bin/env python3
"""把封面单独渲染，再把正文拼回去，让 PDF 的页码从 1 开始。

Marp 的 `paginate: true` 按幻灯片序号编号，封面也算一页，第二页固定显示 2。
CSS 改不了（Marp 会剥掉 `section::after` 里的 `content`），导出后也改不了
（数字已进内容流）。所以这里把封面切出去单独渲染，正文那份自己从 1 编号，
最后用 pdfunite 合并，网页与 PDF 的页码就一致了。

用法:
    python build_pdf.py deck.md -o build/deck.pdf \
        --marp-arg=--theme-set --marp-arg=skills/marp-apple/themes/apple.css

    封面处理默认 auto：第一页是 `lead` 页（`<!-- _class: lead -->` 或 front matter
    `class: [lead]`）才拆封面、让正文从 1 起编号；否则整份按原序号渲染。
    也可以写死：--cover=on / --cover=off。
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

SEP = "---"


def has_cover(slides: list[list[str]]) -> bool:
    """第一页是否封面：带 `_class: lead` 或 front matter 的 class 含 lead。"""
    first = "\n".join(slides[0])
    if re.search(r"_class:\s*\[?\s*['\"]?lead", first):
        return True
    return False


def split_front_matter(lines: list[str]) -> tuple[list[str], list[str]]:
    """拆出 YAML front matter；没有则返回空列表。"""
    if lines and lines[0].strip() == SEP:
        for i in range(1, len(lines)):
            if lines[i].strip() == SEP:
                return lines[: i + 1], lines[i + 1 :]
    return [], lines


def split_slides(lines: list[str]) -> list[list[str]]:
    """按 `---` 切页；代码围栏内的 `---` 不当分隔符。"""
    slides: list[list[str]] = [[]]
    fence = False
    for line in lines:
        if line.lstrip().startswith(("```", "~~~")):
            fence = not fence
        if not fence and line.strip() == SEP:
            slides.append([])
            continue
        slides[-1].append(line)
    return [s for s in slides if any(x.strip() for x in s)]


def render(md: Path, out: Path, marp_args: list[str]) -> None:
    cmd = ["marp", *marp_args, "--pdf", "--allow-local-files",
           "--pdf-outlines", "--pdf-outlines.pages", "false", str(md), "-o", str(out)]
    subprocess.run(cmd, check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--marp-arg", action="append", default=[],
                    help="透传给 marp 的参数，一次一个值，可重复")
    ap.add_argument("--cover", choices=("auto", "on", "off"), default="auto",
                    help="拆分封面：auto 看第一页是否 lead 页，on/off 强制")
    args = ap.parse_args()

    src = Path(args.md)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    text = src.read_text(encoding="utf-8").splitlines()
    front, body = split_front_matter(text)
    slides = split_slides(body)

    split = len(slides) > 1 and (args.cover == "on"
                                 or (args.cover == "auto" and has_cover(slides)))
    if not split:
        render(src, out, args.marp_arg)
        note = "无封面，页码按原序号" if args.cover != "on" else "未拆分"
        print(f"{out}（{len(slides)} 页，{note}）")
        return

    # 临时稿必须放在源稿旁边，marp 才会按源稿目录解析相对图片路径
    work = src.parent
    stem = f".{src.stem}.part"
    cover_md, body_md = work / f"{stem}-cover.md", work / f"{stem}-body.md"
    cover_pdf, body_pdf = out.parent / f"{stem}-cover.pdf", out.parent / f"{stem}-body.pdf"

    head = "\n".join(front) + "\n" if front else ""
    # 封面单独渲染时关掉分页，避免封面上出现「1」
    cover_front = [
        "paginate: false" if l.split(":")[0].strip() == "paginate" else l
        for l in front
    ]
    if cover_front and not any(l.split(":")[0].strip() == "paginate" for l in cover_front[1:-1]):
        cover_front.insert(-1, "paginate: false")
    cover_head = "\n".join(cover_front) + "\n" if cover_front else "---\npaginate: false\n---\n"
    cover_md.write_text(cover_head + "\n".join(slides[0]).strip("\n") + "\n", encoding="utf-8")
    body_md.write_text(
        head + "\n\n---\n\n".join("\n".join(s).strip("\n") for s in slides[1:]) + "\n",
        encoding="utf-8",
    )

    render(cover_md, cover_pdf, args.marp_arg)
    render(body_md, body_pdf, args.marp_arg)
    subprocess.run(["pdfunite", str(cover_pdf), str(body_pdf), str(out)], check=True)

    pages = subprocess.run(["pdfinfo", str(out)], capture_output=True, text=True).stdout
    total = next((l.split()[-1] for l in pages.splitlines() if l.startswith("Pages:")), "?")
    print(f"{out}（{total} 页：封面 + 正文，正文页码从 1 起）")
    for f in (cover_md, body_md, cover_pdf, body_pdf):
        f.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
