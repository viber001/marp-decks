# AGENTS.md

面向在本仓库里工作的 agent 与贡献者。给读者的入口在 `README.md`，写稿方法在
`skills/marp-apple/SKILL.md`。

## 仓库职责

- 本仓库是**工具链**：主题、构建脚本、质检流程、方法文档。
- 风格与判断属于技能：改视觉参数去 `themes/apple.css`，改方法与措辞去
  `skills/marp-apple/references/`。
- `README.md` 只放人类入口（定位、安装、快速开始、目录、许可）。构建细节、验证命令、
  仓库约定写在这里，不要继续堆进 README。

## 目录约定

```
deck.md                        示例稿，必须始终能构建
bin/marp-deck                  任意目录出稿的包装脚本
skills/marp-apple/SKILL.md     技能入口（何时读哪个 reference）
skills/marp-apple/references/  deck-dna / voice-and-copy / page-archetypes /
                               full-deck-workflow / qa-checklist / tooling
skills/marp-apple/themes/      apple.css
skills/marp-apple/tools/       check_overflow / build_pdf / inline_images / extract_notes
build/                         构建产物，git 忽略
```

- 新增主题另建 `themes/<name>.css`，不要改 `apple.css` 去模拟别的品牌。
- 新增工具直接放 `skills/marp-apple/tools/`，用标准库或已有依赖，不引入新依赖而不说明。
- 构建产物（`*.pdf`、`*.html`、`build/`）一律不进库；交付目录里同样只保留
  `*.slides.md`、按需的讲稿文档与图片。

## 构建与验证

```
pixi install
pixi run all                  # 例稿 PDF + HTML + notes + 越界检查
DECK=proposal.md pixi run all
```

在别的工作目录出稿：

```
~/git/skills/marp-decks/bin/marp-deck all 汇报/deck.md
```

`bin/marp-deck` 用 `pixi run --manifest-path` 复用本仓库环境，工作目录里不生成 `.pixi`；
产物落在稿子旁边（`deck.pdf`、`deck.html`、`deck.notes.md`）。工作在别的仓库时，那里的
`.gitignore` 写 `*.pdf`、`*.html` 即可，只让 Markdown 与图片入库。

改动后的最低验证：

1. `pixi run all` 通过，页数与 `---` 数量一致，越界检查 0 异常。
2. 有封面的稿子：PDF 与 HTML 的第 2 张页码都是 1；无封面时都从 1 起不偏移。
3. 改主题或工具时，看 `deck.md` 三类样页（命题、表格、过程）没有溢出与断行异常。

## 不可回退的技术约束

- 页码起始值无法用 CSS 改：Marp 会剥掉 `section::after` 里的 `content: counter(...)`，
  只留 `attr(data-marpit-pagination)`。网页靠 `inline_images.py --renumber=auto` 重写属性，
  PDF 靠 `build_pdf.py` 拆成封面 + 正文再 `pdfunite`。不要退回「正文从 2 起」。
- 越界检查必须栅格化取墨迹包围盒；`pdftotext -bbox` 在 SVG/foreignObject 页面上坐标失真，
  会把正文判成越界。
- `build_pdf.py` 的临时稿必须写在源稿旁边，否则相对图片路径解析不到；脚本跑完会删。
- 第一页 `<!-- _class: lead -->` 同时表示「封面」与「章节页版式」；把 `lead` 用在中间页，
  那一页不会显示页码，这是有意为之。

## 上游快照与 remote

- 上游：<https://github.com/ttyineworld/yu-apple>，参照 `v0.1.0` / `0706a61`。
- 第三方快照一律放 `upstream/<仓库名>` 分支（当前 `upstream/yu-apple`），`main` 只放本仓库内容。
- `origin`（marp-decks）是默认远端，`git push` / `git pull` 都走它。
- `yu-apple` remote 只用于检查更新，不要往那里推；本地 `upstream/yu-apple` 跟踪
  `origin/upstream/yu-apple`。

```
git fetch yu-apple
git log --oneline 0706a61..yu-apple/main
git diff 0706a61..yu-apple/main -- SKILL.md references
git push origin yu-apple/main:refs/heads/upstream/yu-apple   # 跟进后更新快照
```

- 检查更新用的 remote 不要命名为 `upstream`，否则与 `upstream/xxx` 分支混淆。
- 不要把上游 clone 放进仓库工作区：技能扫描会把它当成第二个技能。

## 提交

- 内容与文档改动分开提交；一次提交只做一类事。
- 提交前自查 `git status`、`git diff`，确认没有把 `build/`、PDF、HTML 带进来。
- 未经用户明确要求不要提交或推送。
