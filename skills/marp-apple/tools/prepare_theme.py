#!/usr/bin/env python3
"""把主题里的相对 url() 改写成绝对路径，供跨目录出稿使用。

机构 VI 仓库（如 house-style）里的主题按人可读的方式写相对路径，
例如 background: url("../../vi/logo/x.png")。这些路径相对主题文件本身，
而 Marp 把主题内联进 deck 的 HTML 后，浏览器按 deck 所在目录解析，跨目录就断。

出稿前把主题复制一份、把相对 url() 换成绝对路径，PDF 与 HTML 都能取到文件；
单文件构建阶段再由 inline_images.py 内联成 data URI。

用法:
    prepare_theme.py <theme.css> <out.css>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

URL = re.compile(r'url\(\s*(?:&quot;|&#34;|["\'])?([^)"\'<>&\s]+?)(?:&quot;|&#34;|["\'])?\s*\)')
SKIP = ("data:", "http://", "https://", "//", "#")


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(2)
    src, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
    base = src.parent
    text = src.read_text(encoding="utf-8")

    def repl(m: re.Match) -> str:
        ref = m.group(1)
        if ref.startswith(SKIP):
            return m.group(0)
        p = Path(ref)
        if not p.is_absolute():
            p = (base / ref).resolve()
        if not p.exists():
            print(f"缺文件: {p}", file=sys.stderr)
            return m.group(0)
        return f'url("{p}")'

    out.write_text(URL.sub(repl, text), encoding="utf-8")
    print(f"主题已准备: {src} → {out}")


if __name__ == "__main__":
    main()
