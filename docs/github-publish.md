# 第一次把宇苹果发布到 GitHub

现在的本地包已能分享和安装；注册 GitHub 后可以得到一个长期下载地址、版本记录和反馈入口。

## 1. 注册账号

打开 [GitHub 注册页](https://github.com/signup)，选择用户名，完成账号创建与邮箱验证。用户名会出现在仓库地址里，可以使用自己的长期公开身份。

参考：[GitHub 官方账号创建说明](https://docs.github.com/en/account-and-profile/how-tos/account-management/creating-an-account-on-github)。

## 2. 创建公开仓库

新建仓库，名称建议 `yu-apple`，简介可用：

> 宇苹果：廷宇的演示稿技能。内容提炼、叙事节奏、克制视觉与可复用的 HTML / 4K / PDF 制作流程。

选择 Public。本地包已包含 README、MIT LICENSE 和 .gitignore，不需要另生成相同文件。

参考：[GitHub 官方创建仓库说明](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)。

## 3. 上传文件

进入仓库，通过上传文件入口，把解压后 `yu-apple` 文件夹**里面的内容**放到仓库根目录。上传后，应直接看到 `SKILL.md`、`README.md`、`scripts/`、`references/` 等。

不要只把 ZIP 当作源代码上传，也不要夹带 `node_modules`、本地输出目录或客户原稿。本包已经整理为可公开内容；后续新增材料也需要保持这个边界。

完成提交后，打开 README，确认预览图、样例与文件链接可用。

参考：[GitHub 官方文件上传说明](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository)。

## 4. 发给伙伴

把仓库地址发给伙伴即可。说明：下载整个仓库 ZIP，解压后把完整文件夹交给 AI 助手，按照 README 安装并用 `$yu-apple` 调用。

如后续使用版本发布功能，可将本次命名为 `v0.1.0`，附上同名安装包。当前目录只是发布准备包，不代表已创建远程仓库或发布版本。

## 后续维护

遇到实际失败时，记录输入材料、预期、输出与偏差，优先修正规则或工具中真正导致差异的部分。每次发布前，用公开练习材料重新完成检查、总览与 PDF；若格式或依赖改变，更新 README 和测试记录。
