# 构建与检查

## 仓库结构

```
deck.md                      当前稿子（每次任务新建或复制模板）
skills/marp-apple/
  SKILL.md                   方法入口
  references/                判断与检查细则
  themes/apple.css           Marp 主题：参数都在这里改一次
  tools/build_pdf.py         PDF 导出（封面单渲、正文从 1 编号）
  tools/check_overflow.py    PDF 文字越界检查
  tools/inline_images.py     HTML 单文件化、页码重排、点击放大
  tools/extract_notes.py     逐页讲稿抽取
bin/marp-deck                在任意目录出稿的包装脚本
build/                       构建产物（git 忽略）
```

## pixi 任务

```
pixi run pdf          # deck.md → build/deck.pdf
pixi run html         # deck.md → build/deck.html，并内联成单文件
pixi run notes        # deck.md → build/deck.notes.md
pixi run check        # 检查 build/deck.pdf 的越界
pixi run all          # 依次跑上面四步
```

换文件不用改任务，用环境变量：

```
DECK=proposal.md pixi run all
```

## 在别的工作目录里出稿

稿子通常不在本仓库里。不要为了出稿在项目里再跑一次 `pixi install`：`bin/marp-deck`
用 `pixi run --manifest-path` 复用本仓库的环境，工作目录里不会生成 `.pixi`。

```
path/to/marp-decks/bin/marp-deck all 汇报/deck.md
path/to/marp-decks/bin/marp-deck html 汇报/deck.md
```

- 支持的子命令与 `pixi run` 一致：`pdf`、`html`、`notes`、`check`、`all`。
- 产物落在稿子旁边：`deck.pdf`、`deck.html`、`deck.notes.md`；图片路径按稿子所在目录解析。
- 项目里的 `.gitignore` 只写两行，让源稿之外的东西不进库：

```
*.pdf
*.html
```

也就是：仓库只放 Markdown（必要时加 `deck.notes.md`），图片放 `assets/` 一并入库。

## 手写命令

任务里就是下面这几条，调试时可直接跑：

```
marp --theme-set skills/marp-apple/themes/apple.css --pdf --allow-local-files deck.md -o build/deck.pdf
marp --theme-set skills/marp-apple/themes/apple.css --html --allow-local-files deck.md -o build/deck.html
python skills/marp-apple/tools/inline_images.py build/deck.html
```

- `--allow-local-files` 用于本地图片；导出的 HTML 用工具内联后即可单文件分发。
- PDF 想要书签：加 `--pdf-outlines --pdf-outlines.pages false`。
- `--theme-set` 每次都要带；主题名由 CSS 顶部的 `/* @theme apple */` 决定，
  稿子里写 `theme: apple`。

## 稿子骨架

```markdown
---
marp: true
theme: apple
paginate: true
size: 16:9
---

<!-- _class: lead -->
# 标题
副标题或汇报人

---

## 一页一个判断
- 证据一
- 证据二

<!-- 25s｜讲稿写在这里，页面文字不要重复它 -->
```

- 页面分隔只用 `---`；漏一个会把两页合并成一张幻灯片。
- `<!-- _class: statement -->` 只影响当前页；`<!-- _class: dense -->` 用于表格与代码页。
- 讲稿统一写成 `<!-- Ns｜… -->`；`pixi run notes` 依赖这个格式统计时长。
- 图片放 `assets/`，用相对路径引用；不要写本机绝对路径。

## 页码

Marp 的 `paginate: true` 按幻灯片序号编号，封面也算一页。两种模式，默认自动判断：

- **有封面**（第一页写了 `<!-- _class: lead -->`）：封面不显示页码，正文从 1 起。
  网页由 `inline_images.py --renumber=auto` 把 `data-marpit-pagination` 减一并删掉
  封面那条属性；PDF 由 `build_pdf.py` 把封面切出去单渲、正文单独从 1 编号，再
  `pdfunite` 合并，两边结果一致。
- **没有封面**：都不偏移，页码就是幻灯片序号 1—N。

强制开关：`build_pdf.py --cover=on|off`，`inline_images.py --renumber=on|off`。

主题把 `lead` 页的 `::after` 设为 `display: none`，所以封底也不出页码。
不要用 `content: counter(...)` 覆盖 `section::after`——Marp 会剥离这条声明。

## 导出 HTML 的交互

`inline_images.py` 会往单文件 HTML 里注入点击放大（实测版本来自
`Slides/01_OpenCode_Intro`）：

- 点页面上的图片全屏显示，再点一次或按空格收起；
- 放大状态下方向键滚动 64 px，PageUp/PageDown 滚一屏，Esc 收起；
- 收拾放大层时会 `stopImmediatePropagation` 吃掉空格与 mousemove，并把
  `.bespoke-marp-parent` 置回 `bespoke-marp-inactive`——不这样做，空格会唤出
  Marp 右下角的「Page N of M」浮动条；
- 只对 `section img` 生效，`hdr-logo`、`cover-logo`、`div-logo`、`emoji` 不放大；
- 只影响导出的 HTML，PDF 里没有。

## 单文件：把 HTML 当 PPTX 用

目标是拷一个 `.html` 到投屏电脑，双击就能放。`inline_images.py` 内联两类本地资源：

- `<img src="相对路径">`：页面图片、Marp `![bg]` 背景图（Marp 导出的背景也是 `<img>`）；
- CSS 里的 `url("相对路径")`：主题或页内 style 的背景图、`@font-face` 引用的本地字体文件。

不内联、仍然外链的：`http(s)://` 远程图、`data:` 本身、`<video>`/`<audio>`/PDF 等附件。
需要连网的图不要放进投屏稿；视频要么改成本地文件并接受体积，要么单独拷。

字体还有一层：系统字体（PingFang、Noto Sans CJK）不会被打进 HTML，投屏电脑没有同名字体就会
换字、断行变化。要完全可控，用 `@font-face` 指向仓库里的字体文件，`url()` 会把它内联。

## 检查手段

- 越界：`pixi run check`（阈值默认左右 24 px、上下 20 px）。它把每页按 72 dpi
  栅格化后取墨迹包围盒，右下角 80×46 px 算页码区、不计入；
  `pdftotext -bbox` 在这种 SVG/foreignObject 页面上给出的坐标不可信，不要用。
- 真实断行：`pdftotext -layout -f 3 -l 3 build/deck.pdf -`，看的是渲染后的断行，
  比肉眼看缩略图可靠。
- 中文空格：`pdftotext build/deck.pdf - | grep -nE '[\u4e00-\u9fff] +[\u4e00-\u9fff]'`
  应为空；Markdown 硬折行会被 pandoc 类工具读成空格，Marp 一般不受影响，
  但粘贴进 Word 或转 docx 时会暴露。
- 页数：`pdfinfo build/deck.pdf | grep Pages`，与源稿的 `---` 数量对得上。

## 落盘规则

构建中间产物留在 `build/`，不进同步盘、不进仓库；
最终只把 `*.slides.md`、`*.pdf`、`*.html`（按需）和讲稿文档放到交付目录。

## 用外部主题

主题可以放在别的仓库（例如机构 VI 仓库），不必搬进本仓库：

```bash
THEME=path/to/vi/themes/org.css path/to/marp-decks/bin/marp-deck all 汇报/deck.md
```

`THEME=` 交给 `bin/marp-deck`，它先调 `tools/prepare_theme.py` 把主题里的相对 `url()`
改写成绝对路径（VI 仓库里按人可读的方式写相对路径），再交给 Marp；HTML 阶段由
`inline_images.py` 内联成 data URI。所以：

- VI 仓库不需要为构建做特殊处理，也不需要绝对路径或 base64；
- 主题里的图片路径相对**主题文件**解析，与 deck 放在哪里无关；
- 直接用 marp 而不是 `bin/marp-deck` 时，需要自己先跑 `prepare_theme.py`，否则跨目录取不到图。
