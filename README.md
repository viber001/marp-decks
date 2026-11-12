# 宇苹果 · Yu Apple

**让你的判断，成为一套有节奏的演示。**

作者：**廷宇** · 版本：**0.1.0** · [MIT 许可](LICENSE)

宇苹果是一套面向 AI Agent 的演示稿制作技能。它把内容提炼、叙事、Apple 式克制视觉与可重复执行的制作流程放在一起，用于客户提案、观点演讲和业务介绍。

它适合这样的需求：有材料、有判断，但还没有形成适合当面讲述的页序与页面；希望每页有变化，同时保持整套的字体、颜色、密度与语气一致。

![宇苹果公开试跑样例](examples/preview.png)

## 能做什么

- 从材料中提炼每页的主张、证据与前后连接。
- 在黑场命题、图文、流程、数字、对照与信息整合之间安排节奏。
- 合并重复前提，让文字、图标和真实素材各自承担信息。
- 交付可修改的 HTML 源稿、单页 PNG、高清总览和 16:9 PDF。
- 检查缺失图片与明显溢出，辅助逐页视觉复核；支持局部更新预览。

v0.1 的已实现路线是 **HTML → PNG / 总览 / PDF**。它没有提供可编辑 PowerPoint 文件生成器，也不把换扩展名当作 PPTX。AI 模型、输入质量、素材和人的反馈仍会影响结果。

## 给第一次使用的伙伴

1. 下载并解压整个 `yu-apple` 文件夹。
2. 把文件夹交给你使用的 AI 编程助手，说：

   > 请阅读这个文件夹的 README 和 SKILL.md，帮我安装「宇苹果」。请保留整个文件夹里的参考规则、模板和脚本。

3. 安装完成后，用一份材料开始：

   > 用 $yu-apple 把这份材料做成 10 页客户提案。受众是业务负责人，保留我的核心判断。先给我一张命题页、一张图文页和一张复杂信息页确认风格，再推进整套。最后交付高清总览和 PDF。

不需要 GitHub 账号也能使用本地包。账号用于以后托管、维护和分享项目。

## Codex 本地安装

本包提供不依赖额外库的安装器。需要 Node.js 20.9 或更高版本。在解压后的文件夹执行：

```sh
node scripts/install.mjs
```

安装器默认使用 `$CODEX_HOME/skills`；未配置时使用 `~/.codex/skills`，安装目录名为 `yu-apple`。已有同名目录时会停止；明确使用 `--replace` 才会备份旧版后替换。也可通过 `--dest` 指定其他技能目录。

新开一轮对话，通过 `$yu-apple` 调用。其他支持 `SKILL.md` 的工具可使用相同规则，但其技能目录、自动发现和工具权限需要按各自环境配置，未宣称逐一验证。

## 制作工具准备

方法规则本身不要求运行本包脚本。要实际渲染、检查和导出，在技能文件夹中安装依赖与浏览器：

```sh
npm ci
npx playwright install chromium
```

Linux 系统可能还需要 Playwright 的系统依赖。安装报错时，请让你的 AI 助手按实际系统检查，不要假定所有机器都具备中文字体。

中文优先使用苹方，兼容微软雅黑与 Noto Sans CJK SC；英文使用系统无衬线字体。**字体不随包分发**，不同字体会改变断行，换设备后应重新检查布局。

## 第一次试跑

无需自己准备材料，可以先交给 AI：

> 用 $yu-apple 完成 examples/brief.md 的要求。源材料是虚构练习，不要补造市场数据。请直接完成整套并检查后输出。

[公开试跑源材料](examples/brief.md) · [演示稿源文件](examples/nearby-library.html) · [样例 PDF](examples/nearby-library.pdf) · [测试记录](docs/validation.md)

## 手动使用工具

先复制 `assets/template.html` 作为工作文件，再修改内容与构图。模板是一个可运行起点，不限定整套必须使用固定布局。

```sh
node scripts/deck.mjs check --input examples/nearby-library.html --out out/check
node scripts/deck.mjs render --input examples/nearby-library.html --out out/preview --tile-width 1920
node scripts/deck.mjs render --input examples/nearby-library.html --out out/4k --scale 2
node scripts/deck.mjs pdf --input examples/nearby-library.html --out out/final
```

单页更新可追加 `--pages 2,5`。工具会检查缓存是否仍对应当前材料，避免把不同版本的页面混在同一张总览里。具体参数、页面约定与 PDF 再渲染方法见 [工具说明](references/tooling.md)。

4K 单页为 3840×2160 像素。PDF 使用 16:9 的 4K 等效画布，保留可行的原生文字和矢量图形；为规避浏览器导出时的渐变边线，渐变文字局部使用高分辨率渲染。照片能呈现的细节取决于原始素材，不通过扩大画布虚构细节。

## 这套方法如何使用

入口在 [SKILL.md](SKILL.md)，详细判断放在 `references/`。可以替换字体、强调色、受众和语气；在保持几何与信息层级稳定的前提下，页面可以自由变化。

新项目的反馈应沉淀成可迁移的判断，例如“共用资源只说明一次”。不要把客户名、页码、预算和某个笑话变成所有项目的固定要求。

## 分享和发布

现阶段可直接把 ZIP 发给伙伴。[GitHub 发布说明](docs/github-publish.md) 提供注册后上传仓库的步骤；本包不包含任何远程账号、访问令牌或客户项目。

本项目由廷宇提出与校准创意、审美和方法标准，借助 AI 完成规则整理、工具实现及测试。采用 MIT 许可，欢迎使用、修改与再分发，请保留版权和许可声明。

本包中的公开样例为虚构项目；图形为代码绘制。依赖包保留各自许可，使用者后续加入的照片、商标和字体按其各自授权处理。完整说明见 [作者、样例与依赖](docs/attribution.md)。项目名称中的“苹果”表达审美取向，与 Apple Inc. 无隶属关系。
