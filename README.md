# marp-decks

Marp 幻灯片工具链：主题、构建脚本与质检流程，产出 PDF 与单文件 HTML。

仓库收工具链，技能收风格：首个主题是 `apple`，见 `skills/marp-apple/`。方法改编自廷宇的
「宇苹果」（[ttyineworld/yu-apple](https://github.com/ttyineworld/yu-apple)，MIT）——保留它关于
判断、叙事、版式与质检的部分，把成品这一层换成 Marp：**一份 Markdown 出 PDF、单文件 HTML
和逐页讲稿**。

## 安装

```
pixi install
```

`marp-cli`、`poppler`（`pdftotext`、`pdfinfo`）来自 conda-forge，`python` 用于三个小工具。

## 快速开始

```
pixi run all              # deck.md → build/deck.pdf、deck.html、deck.notes.md
DECK=proposal.md pixi run all
```

在别的工作目录里出稿，用 `bin/marp-deck`（复用本仓库的 pixi 环境，不在那里生成 `.pixi`）：

```
~/git/skills/marp-decks/bin/marp-deck all 汇报/deck.md
```

## 目录

```
deck.md                        示例稿（也可当模板）
skills/marp-apple/SKILL.md     方法入口：什么时候做什么
skills/marp-apple/references/  判据、原型、工作流、质检、构建细则
skills/marp-apple/themes/      apple.css（参数都在这里改一次）
skills/marp-apple/tools/       check_overflow / build_pdf / inline_images / extract_notes
bin/marp-deck                  在任意目录出稿的包装脚本
```

## 作为技能接入

```
ln -s ~/git/skills/marp-decks/skills/marp-apple ~/.config/opencode/skills/marp-apple
```

之后说「用 marp-apple 把这份材料做成 12 页述职」即可。其它支持 `SKILL.md` 的工具按各自的
技能目录配置。

## 文档分工

- `README.md`（本文件）：给人看的入口——它是什么、怎么装、怎么跑。
- `AGENTS.md`：给 agent 和贡献者的仓库约定——构建、验证、文档边界、上游快照与提交规则。
- `skills/marp-apple/SKILL.md` + `references/`：写稿方法本身，跟着技能一起分发。

## 范围与限制

- 不产出 PPTX；需要可编辑幻灯片请另走路线。
- 字体不随仓库分发；换机器后要重新检查断行与溢出。
- 主题参数按中文汇报场景调过，换品牌模板时改 `apple.css` 的变量与字号。

## 许可

MIT，双版权：本仓库 © 2026 胡雪松，方法与文字改编自 © 2026 廷宇（yu-apple）。
再分发请保留出处与许可声明。技能名里的「apple」只表达审美取向，与 Apple Inc. 无关。
