# Mind2Act World 优化分支预览教程

适用对象：希望查看、运行和评审网站优化版本的同事。

- 仓库：https://github.com/KKUN616826/preview-7k4-r9m2
- 优化分支：[website-improvements](https://github.com/KKUN616826/preview-7k4-r9m2/tree/website-improvements)
- 榜单改版前的回退标签：[checkpoint-before-leaderboard](https://github.com/KKUN616826/preview-7k4-r9m2/tree/checkpoint-before-leaderboard)
- 回退提交：`87c6ccf`

优化版本与 `main` 主分支分开。以下步骤运行的是本机预览，不会修改线上站点，也不会向仓库上传改动。

## 1. 准备环境

只需要 Git 和 Python 3，不需要 Node.js、npm、pip 依赖、模型权重或 GPU。

- Git 官方下载：https://git-scm.com/downloads/
- Python 官方下载：https://www.python.org/downloads/

安装完成后重新打开终端。macOS 使用“终端”，Windows 使用 PowerShell。

确认 Git：

```sh
git --version
```

macOS / Linux 确认 Python：

```sh
python3 --version
```

Windows 确认 Python：

```powershell
py -3 --version
```

如果 Windows 的 `py` 不可用，但 `python --version` 显示 Python 3，可以把下文的 `py -3` 替换为 `python`。

## 2. 首次下载优化版本

先进入你希望存放项目的文件夹，再依次执行以下命令（macOS、Linux 和 Windows 均可使用）：

```sh
git clone --depth 1 --filter=blob:none --sparse --branch website-improvements https://github.com/KKUN616826/preview-7k4-r9m2.git mind2act-preview
cd mind2act-preview
git sparse-checkout set data docs media mindaccord rollouts scripts tasks intro_video_hyperframes/renders
```

这套下载方式只获取当前分支的网站及相关素材，跳过大量视频制作中间文件和旧历史。网站视频素材本身仍较多，首次下载需要一定时间；请等待最后一条命令完成后再启动。

如果提示 `mind2act-preview` 已存在，请改用一个新的目录名，或者按第 7 节更新已下载的副本，不要覆盖已有文件。

确认分支：

```sh
git branch --show-current
git log -1 --oneline
```

第一条应输出 `website-improvements`。第二条显示你当前运行的提交版本，反馈问题时可附上这一行。

## 3. 启动网站

确认终端当前位于项目根目录（能看到 `index.html` 和 `scripts` 文件夹）。

macOS / Linux：

```sh
python3 scripts/preview.py
```

Windows：

```powershell
py -3 scripts/preview.py
```

看到下面的信息代表启动成功：

```text
Preview: http://127.0.0.1:8765/
```

保持这个终端窗口运行，再用浏览器打开链接。直接预览不需要运行构建脚本；仓库已经包含生成好的 HTML。也不建议双击 HTML 文件预览，因为视频跳转和部分页面资源需要本地 HTTP 服务。

## 4. 打开需要评审的页面

以下链接只有在你自己的电脑完成第 3 步后才可访问：

| 页面 | 本机预览地址 |
| --- | --- |
| 首页 | http://127.0.0.1:8765/ |
| 新版 Leaderboard | http://127.0.0.1:8765/leaderboard.html |
| Benchmark 总览 | http://127.0.0.1:8765/benchmark.html |
| Mind 分类 | http://127.0.0.1:8765/benchmark/mind.html |
| Act 分类 | http://127.0.0.1:8765/benchmark/act.html |
| Mind2Act 分类 | http://127.0.0.1:8765/benchmark/mind2act.html |
| 示例任务 | http://127.0.0.1:8765/tasks/E.html#easy |
| Documents | http://127.0.0.1:8765/resources.html |

`127.0.0.1` 指访问者自己的电脑，不能把作者电脑上的这个地址当作公网预览地址。GitHub 的分支页面用于查看和获取代码，不能直接运行 HTML。当前教程不代表已经配置了独立在线预览站点。

## 5. 本次可以重点查看什么

### Benchmark

- 左侧分类展开与收起，分类名和任务名跳转。
- 分类页的紧凑图文行、高清封面与悬停反馈。
- 任务详情中的 Easy / Medium / Hard 切换。
- 浏览器前进、后退和刷新后，任务与难度状态是否正确。

### Leaderboard

- 首屏五张摘要卡片及其导航入口。
- Mind、Act、Mind2Act 三组成绩并列显示。
- 模型搜索、范式筛选、已报告／未报告筛选、Reset。
- 表头排序和 Rank by / Metric 切换。
- Details 展开、再次关闭，以及筛选后详情状态。
- 复制带筛选参数的网址，在同一台电脑上重新打开能否恢复状态。
- 手机上默认显示当前能力指标，并通过 View all metrics 查看全表。

现有成绩来自原页面转录的 Table 6，没有新增模型测量。模型家族演示链接不等于产生该分数的评分运行。

### Documents

本轮只统一了左侧导航的宽度、字号与间距。文档内容重组、指标解释、证据说明和章节高亮尚未实施。

## 6. 如何提交反馈

建议提供：

1. 页面地址（包含任务、难度或榜单筛选参数）。
2. 当前提交版本：`git log -1 --oneline` 的输出。
3. 操作步骤、预期效果和实际效果。
4. 截图、浏览器名称、窗口宽度或设备型号；有缩放时注明缩放比例。

反馈示例：

> 页面：leaderboard.html?view=act
> 操作：切换 Act 后，点击某模型的 Details。
> 预期：展开该模型信息，并保留当前排序。
> 实际：……
> 环境：Chrome，1440px 窗口，100% 缩放。

只需要评审时，无需修改或提交任何项目文件。

## 7. 更新到后续版本

在运行服务的终端按 `Ctrl+C` 停止预览，然后在项目目录执行：

```sh
git branch --show-current
git status --short
git pull --ff-only
```

分支应为 `website-improvements`。如果你修改过文件，或更新提示有冲突／分叉，请先保留本地改动并联系项目作者，不要直接删除文件或强制重置。

更新后，重新运行第 3 步的启动命令，并刷新浏览器。

### 已经有另一个分支的项目副本

先确认没有需要保留的未提交修改，再获取远端分支：

```sh
git fetch origin website-improvements:refs/remotes/origin/website-improvements
```

如果本地尚无此分支：

```sh
git switch --track origin/website-improvements
```

如果本地已经有此分支：

```sh
git switch website-improvements
git pull --ff-only
```

然后按第 3 步启动。

## 8. 常见问题

### 浏览器显示无法连接

确认终端中的预览服务仍在运行，并使用终端显示的地址。关闭终端或按下 `Ctrl+C` 后，预览服务会停止。

### 提示找不到 preview.py

当前目录不正确。先进入下载后的 `mind2act-preview` 目录，再运行启动命令。

### 提示端口已经被占用

使用另一个端口，例如 8766：

macOS / Linux：

```sh
python3 scripts/preview.py --port 8766
```

Windows：

```powershell
py -3 scripts/preview.py --port 8766
```

然后访问 http://127.0.0.1:8766/ ，并把第 4 节其他链接中的端口同步改为 8766。

### 图片或视频缺失

先确认第 2 步的素材下载已完成，且没有移动、重命名 `media` 等文件夹。使用 Git 下载方式，不要只单独保存网页 HTML。确认后重新启动、刷新；如仍有问题，把缺失资源的页面地址发给作者。

### 更新后仍像旧版本

先用 `git log -1 --oneline` 核对版本，再强制刷新：macOS 可按 `Command+Shift+R`，Windows 可按 `Ctrl+F5`。

### 想看榜单改版前的代码

在 GitHub 切换到 `checkpoint-before-leaderboard` 标签即可查看回退点。不要把运行副本直接强制重置；需要并排运行旧版本时，请联系作者准备独立目录。

## 9. 停止预览

在运行预览的终端按 `Ctrl+C`。停止服务不会删除项目文件，下次运行相同启动命令即可继续预览。
