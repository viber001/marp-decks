#!/usr/bin/env python3
"""把 Marp 导出的 HTML 变成可单文件分发的版本。

用法:
    python inline_images.py build/deck.html [-o build/deck.inline.html] [--renumber]

做的事:
  1. 把 <img src="相对路径"> 与 CSS 里 url("相对路径") 的本地文件内联成 data URI；
  2. 给 <html> 加 lang="zh-CN"（已有则不动）；
  3. 外链加 target="_blank" rel="noopener"；
  4. --renumber=auto 时，若第一页是 `lead` 页（封面）就把页码整体减一：封面不显示、
     正文从 1 起；没有封面则不动。也可写死 on/off。
     只改网页里 section 的 data-marpit-pagination 属性；PDF 由 build_pdf.py 处理；
  5. 注入点击放大：点图片全屏、空格开关、放大后方向键/PageUp/PageDown 滚动，
     并屏蔽空格触发的 Marp 活动状态（否则右下「Page N of M」浮动条会冒出来）。
"""

from __future__ import annotations

import argparse
import base64
import mimetypes
import re
from pathlib import Path

IMG = re.compile(r'<img\b[^>]*?\bsrc="([^"]+)"[^>]*>')
# CSS 背景图、@font-face 等：url(...) 里的相对路径。允许引号被转义成 &quot; / &#34;。
CSS_URL = re.compile(
    r'url\(\s*(?:&quot;|&#34;|["\'])?([^)"\'<>&\s]+?)(?:&quot;|&#34;|["\'])?\s*\)'
)
HTML_TAG = re.compile(r"<html\b[^>]*>", re.I)
LINK = re.compile(r'<a\b[^>]*\bhref="(https?://[^"]+)"[^>]*>')
FIRST_SECTION = re.compile(r"<section\b[^>]*>", re.I)
PAGE = re.compile(r'<section\b[^>]*?\sdata-marpit-pagination="(\d+)"')

# 点击放大。来自 Slides/01_OpenCode_Intro/inline_images.py 的实测版本：
# 放大层单独盖在页面上，并用 stopImmediatePropagation 吃掉空格，
# 避免 bespoke 收到空格后把「Page N of M」浮动条唤出来。
ZOOM = """<style>
img.zoomable{cursor:zoom-in}
#zm-overlay{position:fixed;inset:0;background:rgba(0,0,0,.95);display:none;overflow:auto;z-index:99999}
#zm-overlay.on{display:block}
#zm-overlay img{display:block;width:100%;height:auto;background:#fff}
body.zm-open{overflow:hidden}
</style>
<script>
(function(){
  function init(){
    var ov=document.createElement('div');ov.id='zm-overlay';
    var big=document.createElement('img');ov.appendChild(big);
    function forceIdle(){
      var p=document.querySelector('.bespoke-marp-parent');
      if(p)p.classList.add('bespoke-marp-inactive');
    }
    function muteMarpActivity(ms){
      var stop=function(ev){ev.stopImmediatePropagation();};
      document.addEventListener('mousemove',stop,true);
      setTimeout(function(){document.removeEventListener('mousemove',stop,true);},ms);
    }
    function hide(){
      ov.classList.remove('on');document.body.classList.remove('zm-open');big.removeAttribute('src');
      muteMarpActivity(300);forceIdle();
    }
    function show(src){big.src=src;ov.classList.add('on');document.body.classList.add('zm-open');ov.scrollTop=0;}
    function activeImg(){
      var a=document.querySelector('svg.bespoke-marp-active');
      if(!a)return null;
      return a.querySelector('img.zoomable');
    }
    ov.addEventListener('click',hide);
    document.addEventListener('keydown',function(e){
      if(e.key===' '||e.key==='Spacebar'){
        if(ov.classList.contains('on')){hide();e.preventDefault();e.stopImmediatePropagation();return;}
        var im=activeImg();
        if(im){show(im.src);e.preventDefault();e.stopImmediatePropagation();}
        return;
      }
      if(!ov.classList.contains('on'))return;
      if(e.key==='Escape'){hide();return;}
      var k=e.key, d=null;
      if(k==='ArrowDown')d=64;else if(k==='ArrowUp')d=-64;
      else if(k==='PageDown')d=ov.clientHeight*0.9;
      else if(k==='PageUp')d=-ov.clientHeight*0.9;
      if(d!==null){ov.scrollTop+=d;e.preventDefault();e.stopImmediatePropagation();}
    },true);
    document.addEventListener('click',function(e){
      var t=e.target;
      if(t&&t.tagName==='IMG'&&t.classList.contains('zoomable')){e.preventDefault();e.stopPropagation();show(t.src);}
    },true);
    document.querySelectorAll('section img').forEach(function(im){
      if(!/hdr-logo|cover-logo|div-logo|emoji/.test(im.className)){im.classList.add('zoomable');}
    });
    document.body.appendChild(ov);
  }
  if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',init);}else{init();}
})();
</script>"""


def add_zoom(text: str) -> tuple[str, bool]:
    """把点击放大的样式与脚本插到 </body> 前；已插过就跳过。"""
    if "zm-overlay" in text or "</body>" not in text:
        return text, False
    return text.replace("</body>", ZOOM + "</body>", 1), True


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
    inlined_css = 0

    def resolve(url: str) -> Path | None:
        if url.startswith(("data:", "http://", "https://", "//", "#")):
            return None
        path = (root / url).resolve()
        return path if path.is_file() else None

    def repl(m: re.Match) -> str:
        nonlocal inlined
        url = m.group(1)
        path = resolve(url)
        if path is None:
            if not url.startswith(("data:", "http://", "https://", "//", "#")):
                print(f"缺图: {url}")
            return m.group(0)
        inlined += 1
        return m.group(0).replace(url, to_data_uri(path), 1)

    def repl_css(m: re.Match) -> str:
        nonlocal inlined_css
        url = m.group(1)
        path = resolve(url)
        if path is None:
            if not url.startswith(("data:", "http://", "https://", "//", "#")):
                print(f"缺文件: {url}")
            return m.group(0)
        inlined_css += 1
        return f'url("{to_data_uri(path)}")'

    text = IMG.sub(repl, text)
    text = CSS_URL.sub(repl_css, text)

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

    text, zoomed = add_zoom(text)

    out.write_text(text, encoding="utf-8")
    size = out.stat().st_size / 1024 / 1024
    extra = f"，重排 {pages} 页页码" if pages else ""
    zoom = "，加点击放大" if zoomed else ""
    css = f"，再内联 {inlined_css} 处 url()" if inlined_css else ""
    print(f"内联 {inlined} 张图片 → {out}（{size:.1f} MB）{css}{extra}{zoom}")


if __name__ == "__main__":
    main()
