# 制作工具

本包将判断方法与确定性制作分开：模型负责理解、提炼和页面设计；随包工具负责加载、检查、渲染和导出。安装与依赖说明见仓库根目录的 `README.md`。

## 页面合同

复制 `assets/template.html` 创建项目源文件，保留这些约定：

- 逻辑画布为 1920×1080；每页使用 `.slide`，置于 `.viewport` 内。
- 每页具有唯一的 `data-page` 标识。页数按实际内容决定，不写死 20 页。
- `window.yuDeck.show(index)` 显示从 0 起计的页面；`window.yuDeck.fit()` 适配窗口。
- `body.capture` 用于截图，隐藏导航并移除导航占位。
- 标题与正文使用原生 HTML；关系图和几何图形优先 SVG。
- 图片使用相对路径或嵌入资源，避免个人绝对路径。保留原始素材与来源记录。

不要将模板的演示内容当作用户的事实。替换内容时保留工具所需结构，具体布局可自由修改。

## 常用操作

在技能包目录中执行。具体选项以 `node scripts/deck.mjs --help` 为准。

```bash
node scripts/deck.mjs check --input path/to/deck.html --out path/to/output
node scripts/deck.mjs render --input path/to/deck.html --out path/to/output
node scripts/deck.mjs render --input path/to/deck.html --out path/to/output --pages 1,3 --scale 2
node scripts/deck.mjs pdf --input path/to/deck.html --out path/to/output
```

- `check`：检查页面与资源，并生成报告。溢出等自动检测结果需要结合画面判断。
- `render`：渲染单页并生成总览。默认单页为 1920×1080；`--scale 2` 为 3840×2160。局部更新使用 `--pages`，全套最终总览需要完整页面缓存。
- `pdf`：导出 16:9 PDF，检查页数与页面尺寸；4K 画布对应 3840×2160 的 96 dpi 渲染尺寸。PDF 中原生文字与图形不受像素尺寸限制。

总览清晰度独立于单页导出；一张容纳很多页面的总览本来就应超过 4K。需要阅读小字时提高每个缩略页面的宽度，而非把已经模糊的总览再次放大。

## 导出注意事项

等字体与图片加载完成后再导出。打印样式必须显示所有页面、准确分页，并隐藏导航与总览界面；不能依赖浏览器当前只显示的活动页。

渐变文字可能在 PDF 中出现裁剪边缘细线。确认问题后，可将该处按高于最终目标的分辨率局部渲染，其他部分继续使用原生文字 / 矢量。局部图像清晰不代表源照片增加了真实细节。

最终 PDF 必须再渲染检查。HTML 截图正常并不能证明打印导出也正常。运行环境与字体变化后，至少复核命题页、复杂信息页和包含特殊效果的页面。

## 查看最终 PDF 的真实渲染

打开生成的 PDF，在 PDF 查看器中逐页检查；不要只检查浏览器截图。有 Poppler 的环境可生成逐页图像：

```sh
mkdir -p out/pdf-review
pdftoppm -r 96 -png out/final/deck.pdf out/pdf-review/page
```

本包的 PDF 页面在 96 dpi 下对应 3840×2160。随后检查全部页面：是否有空白、裁切、导航残留、字体替换、透明层或渐变边线。`pdftoppm` 属于可选的 Poppler 工具，不随 Node 依赖安装；没有它时可通过 PDF 查看器完成目检。渲染器的字体警告需要结合页面结果判断，不应仅凭日志宣布画面正常。
