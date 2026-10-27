# Mind2Act

**Mind2Act World** · Benchmark

**Mind2Act Harness** · 配套模型方案

**Evaluating Reasoning–Acting Coordination in Robotic Manipulation**

研究主线：计划如何适应物理约束，前一步的实际结果如何改变后一步。展示名称为 Mind2Act World，配套方法名为 Mind2Act Harness；仓库地址、兼容文件名与任务 ID 保持不变。

打开 `index.html` 即可浏览项目介绍、15 项任务与 39 段演示及预览。请保持 media/、docs/ 和 data/ 的相对位置。

本地预览运行 `python3 scripts/preview.py`，访问 http://127.0.0.1:8765/。该服务支持视频 byte-range 请求，进度条无需等待整段视频下载完成即可跳转。

- docs/PhysCo_Cases.md：完整任务说明。
- docs/PhysCo_Technical_Report_v0.1.pdf：研究框架与评测设计。
- docs/PhysCo_Media.md：全部演示素材索引。
- data/showcase-cases.json：展示用任务数据，媒体路径相对网站根目录。

本展示包含任务定义与演示，不包含模型评测成绩。暂定参数和待补素材在具体任务中标注。

## 修改与构建

### Benchmark 任务浏览

`benchmark.html` 为总览，`benchmark/mind.html`、`benchmark/act.html`、`benchmark/mind2act.html` 为分类页；原有 `tasks/<ID>.html#easy|medium|hard` 任务地址保持有效。

- 导航、分类说明与卡片内容：`data/benchmark-navigation.json`。
- 任务详情内容源：`scripts/benchmark/<ID>.html`；共享顶部导航：`scripts/benchmark/header.html`。
- 浏览布局与侧栏：`tasks/benchmark-workspace.css`、`scripts/benchmark-workspace.js`。
- 卡片与悬停沿用 `tasks/benchmark-catalog.css`。
- 分类页图文行样式：`tasks/benchmark-task-rows.css`；高清封面保存在 `media/benchmark-covers/`，用 `python3 scripts/export_benchmark_covers.py` 从原始视频重新提取（需要 ffmpeg），来源记录见该目录的 `sources.json`。

单独运行 `python3 scripts/build_benchmark.py` 更新总览、分类和任务详情；完整构建也会调用它。请修改上述源文件，不直接修改生成页面。浏览器回归运行 `node scripts/test_benchmark_browser.cjs`，使用与现有测试相同的 Playwright / `NODE_PATH` 环境。

- 修改任务定义、媒体路径、难度和证据说明：`data/showcase-cases.json`。
- 修改核心观点与任务设计介绍：`scripts/research_intro.html`。
- 修改介绍样式：`scripts/research.css`；目录与交互：`scripts/showcase.html`。
- 修改完整研究介绍：`docs/PhysCo_Showcase.md`。
- 修改排行榜候选：`data/leaderboard.json`；表格与交互：`scripts/leaderboard.py`、`scripts/leaderboard.html`、`scripts/leaderboard.js`。当前只接受待评测占位，不能以零值代替缺失成绩；发布实测结果前须完善协议与校验，详见 `docs/Leaderboard.md`。
- 新媒体放在 `media/videos/` 或 `media/images/`，视频封面放在 `media/posters/`。

运行 `python3 scripts/build.py` 重新生成 HTML、逐任务文档及媒体索引，再用 `python3 scripts/validate.py` 检查资源一致性。不要只改生成后的 HTML，否则下次构建会覆盖。

当前任务与素材同步自 MEMbench 文档 revision 903（2026-09-25）。CP03 为动态槽架装盘，CP04 为双臂配料与温控烹饪，CP05 更新为揭防尘布与 Hard 音量调节流程。CP03 是使用仿真状态的专家运控；CP04 仅有 Easy 预览；所有演示均不代表模型测评成绩。

## 配套模型网站

[Mind2Act Harness 模型架构](mindaccord/index.html)：Contract-Guided Coordination of Cognitive and Reactive Agents for Robotic Manipulation。构建与状态边界见 [模型 README](mindaccord/README.md)。


## Current website previews

- Dark hero (current homepage): [index.html](index.html)
- Ivory hero: [hero-ivory-preview.html](hero-ivory-preview.html)
- Dark hero comparison: [hero-dark-preview.html](hero-dark-preview.html)

Both versions use the updated research introduction. Scores remain unpublished placeholders.

## CP05 首屏：记忆、动作与确认

当前首页使用同一次 CP05 高清仿真录制的截图、工具位姿与触键日志。12 次示范各有独立截图；K01–K29 表示从左到右的白键编号，不是音高。记忆卡片属于解释性叠加层，不是模型内部记忆记录。

- `scripts/hero-demo.html`、`scripts/hero-demo.css`、`scripts/hero-demo.js`：首屏结构、布局和播放器；`scripts/hero-demo-data.js` 提供纯时间状态计算。
- `data/hero-demo.json`：公开的事件表、时钟映射、录制来源摘要及左右棒尖高度；构建时内嵌到 HTML，无需 API 或运行时 JSON 请求。
- `media/images/hero-memory/`：12 张真实亮键截图，重复键占独立序列位置。
- `scripts/showcase.html` 与 `scripts/research_intro.html` 已同步当前首页；修改源模板后运行构建，不直接维护生成的 `index.html`。

高度使用同次运行记录的实际工具位姿计算出的棒尖世界坐标 Z，单位 cm。工具位姿记录为 30 Hz，触键时钟为 120 Hz，释放依据 12 Hz 键深日志中触发后首次小于 2 mm 的采样。事件点的高度在线性插值后的曲线上定位；确认时间始终取真实触键事件，不取曲线最低点。所有原始高度采样均保留，未用目标位置替代实测位置。

首页使用 `media/videos/CP05_hero_fullframe_act.mp4`，原视频和旧版裁剪素材保留。三段依次为 Mind（源 42.4–52.1 秒，3×）、独立 Act 聚焦（源 62.5–67.0 秒，1×）、完整 Mind2Act（源 60.5–105.433333 秒，4×）。成片为 30 fps、569 帧；默认 0.75× 播放，单轮约 25.29 秒，其中 Act 聚焦约 6 秒。有效源视频倍速分别为 2.25×、0.75×、3×。`presentation.segments` 保存新的分镜时钟，原事件与运动数据的剪辑时钟保持不变，由纯函数 `presentationAt` 统一映射。只在 12 次有效触键及释放后显示 `Sequence complete`，不宣称整项任务或专家轨迹验收完成。

重新导出需要原始录制目录及 ffmpeg；普通网页构建不需要访问原始日志。导出依赖可装入独立虚拟环境：

```sh
python3 -m venv /tmp/mind2act-export
/tmp/mind2act-export/bin/pip install -r scripts/hero-export-requirements.txt
/tmp/mind2act-export/bin/python scripts/export_hero_demo.py --run /path/to/CP05-hard-hd-replay-20261009
python3 scripts/build.py
python3 scripts/validate.py
node --test scripts/test_hero_demo.cjs
```

导出器只读取原始运行，使用 `trajectory.json`、`control_trace.json`、`integrated_result.json`、`collection/control.npz`、`feedback82.json` 和原生 RGB 时钟核对视频时间，并记录源文件 SHA-256。可加 `--output /tmp/hero-export-check` 导出到独立目录核对复现结果。

浏览器回归使用独立安装的 Playwright，不作为网站依赖。启动预览后运行 `node scripts/test_hero_browser.cjs`；可通过 `NODE_PATH` 指定 QA 依赖目录、`CHROMIUM_EXECUTABLE` 指定浏览器、`HERO_PREVIEW_URL` 指定地址、`HERO_SCREENSHOTS` 指定截图目录。首屏测试覆盖五种屏宽及不同桌面高度、12 次触发／释放边界、独立聚焦进度隔离、全幅坐标映射和媒体时间驱动转场、曲线与关节读数、键盘操作、循环、逐帧同步、暂停恢复、减少动态效果与媒体错误回退。相同环境下运行 `node scripts/test_lunar_browser.cjs` 检查排行榜高度、三榜配色／logo、键盘切换、模型搜索、表格列联动及完整榜单入口。

首屏预览播放第 4–8 次记忆示范，插入独立 Act 聚焦，再进入完整闭环段；全部 12 张截图仍随动作阶段恢复。卡片展示音名采用 C2–C6 的白键映射约定（C D E F G A B 循环），不是原始仿真的实测音高；原始 K 编号和证据数据保持不变。

执行阶段同时展示 Mind ↔ Act：`Target` 箭头从当前记忆指向执行臂的实时曲线位置；`Registered` 返回箭头从真实触键事件点指回已确认卡片。返回光点只运行 0.45 秒视频时间，暂停、回退与循环均由同一视频时钟重算；减少动态效果时不显示光点。确认回执和 ✓ 持续保留，只有日志确认释放后才推进下一目标。剩余数量按已确认触键计算，0 remaining 与最终释放后的 `Sequence complete` 是不同状态。

当前紧凑介绍图、月球模型图、任务分组与最新介绍视频已回填到构建源文件。修改 `scripts/lunar.js`、`scripts/research_intro.html` 或 `scripts/showcase.html` 后统一构建，避免只修改生成首页而在下次构建时丢失设计。

Act 聚焦的导出在 `scripts/export_hero_presentation.py` 中维护，主导出器自动调用。Act 段使用 1920×1080 原始完整画面；`actDetail.crop` 与 `outputRectangle` 都为 `[0, 0, 1920, 1080]`，`target` 直接使用原图坐标。`highlightRegion: [1000, 60, 920, 780]` 用于前端 SVG 聚焦层：区域内保持原亮度，外围叠加约 30% 深蓝遮罩，边缘柔化并加短角标。该区域包含右臂腕部、夹爪、棒尖和 K26。桌面三段采用相同视频缩放，手机始终保持完整 16:9 画面。独立聚焦中的确认和释放不消耗后续 12 键序列。

`presentation.transition` 记录 Mind → Act 和 Act → Mind2Act 两个边界及前后各 0.2 秒的淡出／淡入；`presentationAt` 返回由媒体时间计算的 `sceneOpacity`（smoothstep），用于视频、高亮、标题及阶段图表，品牌、月亮和控件保持可见。转场约 0.53 秒实际播放时间，不增加片段、不改变时钟映射，两个转场分别位于独立 Act 触键之前，以及 Act 释放之后、闭环首次触键之前。暂停、回退、跳转及循环直接重算透明度；减少动态效果时禁用淡变，保留静态聚焦层。

Act 的 GT 指真实下发的控制器参考目标，不是通过完整验收的专家轨迹。目标棒尖高度取 `feedback82.json` 的 `target`；实测高度取 `trajectory.json` 的 30 Hz 工具位置并线性插值到 120 Hz；六个关节目标／实测值分别取 `control.npz` 同一控制步的 `action` 与 `joint_position_after`，弧度转为度。目标在控制步前下发，关节实测在该步后采样；不使用 `feedback82.measured_tip` 的步前观测替代步后观测，也不平移曲线制造贴合。完整参考曲线预先显示，实测曲线、关节读数和事件点由播放器时间重算。

三榜图的渲染与自适应样式维护于 `scripts/lunar-worlds.js`、`scripts/lunar-worlds.css`；`scripts/lunar-embed.js` 根据桌面可视高度减去导航栏和 32px 留白设置面板高度，移动端沿用自然内容高度。Mind 对应浅色阳面、Act 对应深色阴面、Mind2Act 保留双色渐变；分类键和 `mind2act-world` 消息协议保持不变。

### 正式项目封面与精简介绍（2026-10-17）

首页沿用最新版 920px 版心及 Sora 标题。机构、标题、作者、贡献说明及资源入口组成居中的正式项目封面。五位作者的共同第一作者标记与 Yuzhi Huang 的 Project Lead 标记按已确认的技术报告同步；不包含占位作者、占位机构或多校占位 logo。预览日期与未开放的报告、社区邀请保持明确标注。

`scripts/academic-cover.css` 独立维护封面与介绍排版；`scripts/research_intro.html` 维护署名和经过确认的 212 词介绍。正文采用本地 Source Serif 4（Regular / Semibold WOFF2，附 OFL 许可证；来源 https://github.com/adobe-fonts/source-serif/tree/release）。清华 SIGS 标识从原首页内嵌图像提取为静态 PNG；社区 SVG 来源与许可证见 `media/icons/community/README.md`。

当前首页只展示 15 个 Medium 视频预览，完整 benchmark 说明已迁移到独立页面。导出器仍维护全部 30 个 Easy / Medium 预览资源，构建按模板中实际使用的预览绑定。已回填最新首页的 Feishu、News、独立 benchmark 入口、920px 样式及地月排行榜引用。正常构建只生成缺失的 rollout 页面，保留已单独更新的页面；只有显式调用 `build_rollouts(..., overwrite=True)` 才会覆盖它们。

`test_project_browser.cjs` 覆盖 320、390、820、1440、1920px 下的版心、标题、作者标记、社区图标、按需视频加载、分享及字体加载失败回退。字体和图标均本地提供，不依赖外部 CDN。
