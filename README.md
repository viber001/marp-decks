# marp-decks

Marp 幻灯片工具链：主题、构建脚本与质检流程，产出 PDF 与单文件 HTML。

仓库收工具链，技能收风格：首个主题是 `apple`，见 `skills/marp-apple/`。

把「宇苹果」（[ttyineworld/yu-apple](https://github.com/ttyineworld/yu-apple)，MIT）里关于**判断、
叙事、版式和质检**的部分搬到 Marp 上：不生成 HTML 页面，改成一份 Markdown 出 PDF、单文件 HTML
和逐页讲稿。

- 原技能的成品是手写 HTML + Playwright 截图/导出；这里丢掉这一层，保留它的方法。
- 视觉参数（字号、边距、颜色、类名）落到 `skills/marp-apple/themes/apple.css`，改一次全套生效。
- 讲稿写在页内注释里，`pixi run notes` 抽成逐页文案，页面文字与口播不互相复述。

## 目录

```
deck.md                        示例稿（也可当模板）
skills/marp-apple/
  SKILL.md                     方法入口：什么时候做什么
  references/
    deck-dna.md                视觉锚点与版式类名
    voice-and-copy.md          提炼、口径、反馈处理
    page-archetypes.md         内容 → 轮廓
    full-deck-workflow.md      页序、样页、导出
    qa-checklist.md            交付前逐条检查
    tooling.md                 构建命令与落盘规则
  themes/apple.css             Marp 主题
  tools/                       check_overflow / inline_images / extract_notes
pixi.toml                      marp-cli + poppler + python 与四个任务
```

## 安装

```
pixi install
```

`marp-cli`、`poppler`（`pdftotext`、`pdfinfo`）来自 conda-forge，`python` 用于三个小工具。

## 使用

```
pixi run pdf      # build/deck.pdf（封面单渲，正文页码从 1 起）
pixi run html     # build/deck.html（图片已内联，页码从 1 起）
pixi run notes    # build/deck.notes.md
pixi run check    # 越界检查
pixi run all
DECK=proposal.md pixi run all
```

在 OpenCode 里当技能用，把目录链接到技能目录：

```
ln -s ~/opencodev1/szbl/new/skills/marp-apple ~/.config/opencode/skills/marp-apple
```

之后说「用 marp-apple 把这份材料做成 12 页述职」即可。其它支持 `SKILL.md` 的工具
按各自的技能目录配置。

## 写法要点

- 一页一个判断；标题 1—2 行，语义处断行。
- 页面分隔只用 `---`；漏一个就会两页合一。
- 排版靠类名：`lead`（封面/章节）、`statement`（命题）、`dark`（暗页）、`figure`（图文）、
  `dense`（表格/代码）、`.cols` / `.grid3` / `.compare` / `.steps` / `.takeaway` / `.source` / `.tag`。
- 讲稿：`<!-- 25s｜…… -->`，只写口播，不重复页面文字。
- 图片放 `assets/`，相对路径引用；`pixi run html` 会内联成单文件。
- 页码：第一页写成 `<!-- _class: lead -->` 就当封面处理，封面不编号、正文从 1 起，
  网页与 PDF 一致；没有封面则按幻灯片序号 1—N。需要强制时用 `--cover=on|off`、
  `--renumber=on|off`。

## 范围与限制

- 不产出 PPTX；需要可编辑幻灯片请另走路线。
- 字体不随仓库分发；换机器后要重新检查断行与溢出。
- 主题参数是按中文汇报场景调的，换品牌模板时改 `apple.css` 的变量与字号即可。

## 许可与出处

方法改编自廷宇的「宇苹果」（MIT）。本仓库中的文字与代码同样以 MIT 发布，
再分发请保留出处与许可声明。技能名里的「apple」只表达审美取向，与 Apple Inc. 无关。

### 来源与更新检查

- 上游：<https://github.com/ttyineworld/yu-apple>
- 参照版本：`v0.1.0`，commit `0706a61`（2026-11-12，「发布宇苹果 Yu Apple v0.1.0」）
- 改编范围：只取了 `SKILL.md` 与 `references/` 里的方法（判断优先、页面原型、文案提炼、
  工作流、质检清单），丢弃其手写 HTML 与 Playwright 截图/导出链路。
- 隔一段时间回来看上游有没有更新：

  ```bash
  git -C tmp/yu-apple pull --ff-only
  git -C tmp/yu-apple log --oneline 0706a61..HEAD
  ```

  `tmp/yu-apple` 不入库（见 `.gitignore`）；没有的话重新 `git clone --depth 1` 到那里，
  然后用 `SKILL.md`、`references/*.md` 与本仓库同名文件逐节比对，判断哪些方法值得跟进。
