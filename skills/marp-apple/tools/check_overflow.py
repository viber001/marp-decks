#!/usr/bin/env python3
"""检查 Marp 导出的 PDF 是否有内容越界。

用法:
    python check_overflow.py build/deck.pdf [--margin-x 24] [--margin-y 20]

Marp 把每页放在 SVG 的 foreignObject 里，`pdftotext -bbox` 给出的文字坐标
不可信；这里改为 72 dpi 栅格化后取墨迹包围盒，与安全边距比较。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops


def ink_bbox(png: Path) -> tuple[int, int, int, int]:
    with Image.open(png) as im:
        gray = im.convert("L")
        mask = gray.point(lambda v: 255 if v < 245 else 0)
        # 右下角留给页码，不计入墨迹
        width, height = mask.size
        footer = mask.copy()
        footer.paste(0, (width - 80, height - 46, width, height))
        return footer.getbbox() or (0, 0, 0, 0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--margin-x", type=int, default=24)
    ap.add_argument("--margin-y", type=int, default=20)
    args = ap.parse_args()

    results: list[tuple[int, int, int, int, int, int]] = []
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            ["pdftoppm", "-r", "72", "-png", args.pdf, f"{tmp}/p"], check=True
        )
        for page in sorted(Path(tmp).glob("p-*.png")):
            with Image.open(page) as im:
                width, height = im.size
            results.append((*ink_bbox(page), width, height))

    problems = 0
    for index, (x0, y0, x1, y1, width, height) in enumerate(results, start=1):
        if (x0, y0, x1, y1) == (0, 0, 0, 0):
            print(f"第 {index} 页：空白")
            problems += 1
            continue
        issues = []
        if x0 < args.margin_x:
            issues.append(f"左 {x0}px")
        if y0 < args.margin_y:
            issues.append(f"上 {y0}px")
        if width - x1 < args.margin_x:
            issues.append(f"右 {width - x1}px")
        if height - y1 < args.margin_y:
            issues.append(f"下 {height - y1}px")
        if issues:
            problems += 1
            print(f"第 {index} 页：{'、'.join(issues)}（墨迹 {(x0, y0, x1, y1)}，页面 {width}×{height}）")

    print(f"共 {len(results)} 页，异常 {problems} 页")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
