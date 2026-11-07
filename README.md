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

## 同事获取与运行优化版本

请阅读 [优化分支预览教程](docs/Preview_Guide.md)，包含首次下载、macOS / Windows 启动、更新、评审入口和常见问题。

## 修改与构建

### 当前版本发布检查

GitHub Pages 从 `main` 分支根目录发布已生成的静态页面。
旧的整站构建链（`scripts/build.py`、`scripts/validate.py` 及其模板）已删除；首页由下面的模块构建器维护，每个只替换自己负责的区块，重复运行结果不变。

首页按“每块只做一件事”组织：首屏与论文信息 → 三个套件 → 排行榜预览 → 30 个任务 → News / Resources / Contributors。结构与各区块的数据来源见 [首页结构说明](docs/Homepage_Structure.md)。首页模块与榜单使用对应构建器：

```sh
python3 scripts/build_home_hero_data.py
python3 scripts/build_intro_story.py
python3 scripts/build_home_leaderboard_entry.py
python3 scripts/build_home_tasks.py
python3 scripts/build_leaderboard.py
python3 scripts/validate_release.py
python3 scripts/preview.py --port 8767
```

浏览器测试需安装 Playwright，并设置 `NODE_PATH`、`CHROMIUM_EXECUTABLE`、`HERO_PREVIEW_URL=http://127.0.0.1:8767/`。
发布前检查共享导航、首页动画、首页排行榜预览、Protocol、Benchmark、90 段任务视频、排行榜与榜单动画，分别运行 `scripts/test_site_navigation_browser.cjs`、`test_hero_browser.cjs`、`test_protocol_browser.cjs`、`test_benchmark_browser.cjs`、`test_benchmark_expansion.cjs`、`test_bench30_sync.cjs`、`test_leaderboard_boards.cjs`、`test_leaderboard_motion.cjs`、`test_view_leaderboard.cjs`。


### Home 训练闭环预告

诊断卡区（`#diagnosis`）正下方的 `#model-diagnostics` 是 Coming soon 预告：harness 像医生，诊断模型、开出针对性数据（“抓药”），数据回流训练后再评测，模型一轮轮变强，harness 也随看过的模型积累经验（2026-11-05 同步会的“培养方案” loop）。不代表该服务已经开放，图中的条形和代码不是任何模型的结果。

- 内容：`scripts/home-diagnostics.html`；样式：`scripts/home-diagnostics.css`；动画：`scripts/home-diagnostics.js`。直接画在白色页面上（HTML 卡片 + SVG 连线），文字可编辑，不再使用视频。
- 流程：Your model → 1 Evaluate（Mind / Act / Mind2Act）→ 2 Diagnose（诊断卡）→ 3 Prescribe（针对性数据）→ 4 Train 回流；三轮依次补 Act、Mind2Act、Mind，每轮像素小人长大一点并换成新类型的角色，harness 经验条增长；最后停 2.4 秒展示完整类型。约 19 秒一个循环。
- 性格画像（v5 类 MBTI 字母）随训练变化：ISTJ 账房先生 → ESTJ 装配工匠（Act 数据使其偏做，I→E）→ ESTP 修理工（闭环 Mind2Act 数据使其看反馈，J→P）→ ENTP 调校师（记忆数据使其从记物转向记位，S→N）。诊断卡显示诊断时的画像，模型卡片在训练后更新并高亮变化的字母。
- 窄屏改为竖排，回流线走右侧。离屏或后台时暂停，可手动暂停；系统减少动态效果时显示第三轮的静止画面。
- 更新：`python3 scripts/build_home_diagnostics.py`，把预告区放在 `<!-- HOME_DIAGNOSIS_END -->` 之后，并同步 head 中的样式和脚本。
- 浏览器检查：`node scripts/test_home_diagnostics.cjs`。
- 诊断卡与 16 型速查表使用 v5 字母（借用 MBTI 字母，含义由本基准重新定义，见飞书交接文档“Mind2Act 模型性格分类 v5”）：定义、四大主类型、16 个昵称和像素小人都在 `scripts/profile_v5.py`。每个类型有一个手绘的 16×16 角色（账房先生拿账本、领航员戴船长帽、鉴定师拿放大镜等），颜色是所属家族色的不同深浅。网页上每个维度只显示两个字母之一（取倾向的一边），不用 X；把握度低于 80% 的轴标为“弱倾向”并写出百分比。这一点与 v5 交接文档“X 原样展示”的规则不同，harness 仍输出 X。16 个昵称仍待负责人确认。
- 钢酱的 8 秒灰银视频版（`media/diagnostics-teaser/`）在提交 80a83e3 中，可从 git 历史恢复。

### 独立 Leaderboard 页面

- 数据：`data/leaderboard-results.json`（schema 2）。每个模型记录赛道（`e2e` / `agent`）、类型、机构、logo、首批发布日期或排队序号；`results` 在官方成绩公布前为 `null`，公布后按构建器文件头的格式填入 clean / random 各视角的 Score 与 Success。
- VLA / WAM 与 Coding agent 分两张榜分别排名（每格 50 局 vs 5 局，接口与预算不同），不可横向比较。
- 模型 logo：`media/icons/models/`，取自各模型或机构官网的彩色原版。
- 页面源：`scripts/leaderboard-page.html`；样式：`scripts/leaderboard-explorer.css`、`scripts/leaderboard-boards.css`；交互：`scripts/leaderboard-boards.js`。
- 首屏：`scripts/leaderboard_stage.py`、`scripts/leaderboard-stage.css`。月球园区场景中，高度即分数：地平线 0、月球 100；每个 VLA / WAM 模型从地平线竖直升到 Clean Overall 分数的高度，左右按发布顺序；少于 3 个成绩时显示匿名占位模型和首批发布日期。
- 单独构建：`python3 scripts/build_leaderboard.py`。完整构建也会调用此构建器；不要直接修改生成的 `leaderboard.html`。
- 浏览器回归：`node scripts/test_leaderboard_boards.cjs`；首页与新榜单入口衔接：`node scripts/test_view_leaderboard.cjs`，使用现有 Playwright / `NODE_PATH` 环境。
- 此轮改版前的已保存版本：提交 `87c6ccf`，标签 `checkpoint-before-leaderboard`。首页、Benchmark 与 Documents 不属于这次独立榜单改版的修改范围。

### Benchmark 任务浏览

`benchmark.html` 为总览，`benchmark/mind.html`、`benchmark/act.html`、`benchmark/mind2act.html` 为分类页；原有 `tasks/<ID>.html#easy|medium|hard` 任务地址保持有效。

- 导航、分类说明与卡片内容：`data/benchmark-navigation.json`。
- 任务详情内容源：`scripts/benchmark/<ID>.html`；共享顶部导航：`scripts/benchmark/header.html`。
- 浏览布局与侧栏：`tasks/benchmark-workspace.css`、`scripts/benchmark-workspace.js`。
- 卡片与悬停沿用 `tasks/benchmark-catalog.css`。
- 分类页图文行样式：`tasks/benchmark-task-rows.css`；高清封面保存在 `media/benchmark-covers/`，用 `python3 scripts/export_benchmark_covers.py` 从原始视频重新提取（需要 ffmpeg），来源记录见该目录的 `sources.json`。

单独运行 `python3 scripts/build_benchmark.py` 更新总览、分类和任务详情；完整构建也会调用它。请修改上述源文件，不直接修改生成页面。浏览器回归运行 `node scripts/test_benchmark_browser.cjs`，使用与现有测试相同的 Playwright / `NODE_PATH` 环境。

- 修改任务定义、媒体路径、难度和证据说明：`data/showcase-cases.json`（封面导出使用）。
- 修改完整研究介绍：`docs/PhysCo_Showcase.md`。
- 排行榜数据与说明：`data/leaderboard-results.json`，详见 `docs/Leaderboard.md`。
- 新媒体放在 `media/videos/` 或 `media/images/`，视频封面放在 `media/posters/`。

不要只改生成后的 HTML 区块，否则下次构建会覆盖；没有构建器的区块（首屏、论文信息、News、Resources、Contributors）直接在 `index.html` 中维护。

当前任务与素材同步自 MEMbench 文档 revision 903（2026-09-25）。CP03 为动态槽架装盘，CP04 为双臂配料与温控烹饪，CP05 更新为揭防尘布与 Hard 音量调节流程。CP03 是使用仿真状态的专家运控；CP04 仅有 Easy 预览；所有演示均不代表模型测评成绩。

## 配套模型网站

[Mind2Act Harness 模型架构](mindaccord/index.html)：Contract-Guided Coordination of Cognitive and Reactive Agents for Robotic Manipulation。构建与状态边界见 [模型 README](mindaccord/README.md)。



## CP05 首屏：记忆、动作与确认

当前首页使用同一次 CP05 高清仿真录制的截图、工具位姿与触键日志。12 次示范各有独立截图；K01–K29 表示从左到右的白键编号，不是音高。记忆卡片属于解释性叠加层，不是模型内部记忆记录。

- 首屏结构直接维护在 `index.html`；`scripts/hero-demo.css`、`scripts/hero-demo.js` 负责布局和播放器，`scripts/hero-demo-data.js` 提供纯时间状态计算。
- `data/hero-demo.json`：公开的事件表、时钟映射、录制来源摘要及左右棒尖高度；由 `python3 scripts/build_home_hero_data.py` 内嵌到 `index.html`，无需 API 或运行时 JSON 请求。
- `media/images/hero-memory/`：12 张真实亮键截图，重复键占独立序列位置。

高度使用同次运行记录的实际工具位姿计算出的棒尖世界坐标 Z，单位 cm。工具位姿记录为 30 Hz，触键时钟为 120 Hz，释放依据 12 Hz 键深日志中触发后首次小于 2 mm 的采样。事件点的高度在线性插值后的曲线上定位；确认时间始终取真实触键事件，不取曲线最低点。所有原始高度采样均保留，未用目标位置替代实测位置。

首页使用 `media/videos/CP05_hero_fullframe_act.mp4`，原视频和旧版裁剪素材保留。三段依次为 Mind（源 42.4–52.1 秒，3×）、独立 Act 聚焦（源 62.5–67.0 秒，1×）、完整 Mind2Act（源 60.5–105.433333 秒，4×）。成片为 30 fps、569 帧；默认 0.75× 播放，单轮约 25.29 秒，其中 Act 聚焦约 6 秒。有效源视频倍速分别为 2.25×、0.75×、3×。`presentation.segments` 保存新的分镜时钟，原事件与运动数据的剪辑时钟保持不变，由纯函数 `presentationAt` 统一映射。只在 12 次有效触键及释放后显示 `Sequence complete`，不宣称整项任务或专家轨迹验收完成。

重新导出需要原始录制目录及 ffmpeg；普通网页构建不需要访问原始日志。导出依赖可装入独立虚拟环境：

```sh
python3 -m venv /tmp/mind2act-export
/tmp/mind2act-export/bin/pip install -r scripts/hero-export-requirements.txt
/tmp/mind2act-export/bin/python scripts/export_hero_demo.py --run /path/to/CP05-hard-hd-replay-20261009
python3 scripts/build_home_hero_data.py
node --test scripts/test_hero_demo.cjs
```

导出器只读取原始运行，使用 `trajectory.json`、`control_trace.json`、`integrated_result.json`、`collection/control.npz`、`feedback82.json` 和原生 RGB 时钟核对视频时间，并记录源文件 SHA-256。可加 `--output /tmp/hero-export-check` 导出到独立目录核对复现结果。

浏览器回归使用独立安装的 Playwright，不作为网站依赖。启动预览后运行 `node scripts/test_hero_browser.cjs`；可通过 `NODE_PATH` 指定 QA 依赖目录、`CHROMIUM_EXECUTABLE` 指定浏览器、`HERO_PREVIEW_URL` 指定地址、`HERO_SCREENSHOTS` 指定截图目录。首屏测试覆盖五种屏宽及不同桌面高度、12 次触发／释放边界、独立聚焦进度隔离、全幅坐标映射和媒体时间驱动转场、曲线与关节读数、键盘操作、循环、逐帧同步、暂停恢复、减少动态效果与媒体错误回退。首页排行榜预览由 `node scripts/test_view_leaderboard.cjs` 检查。

首屏预览播放第 4–8 次记忆示范，插入独立 Act 聚焦，再进入完整闭环段；全部 12 张截图仍随动作阶段恢复。卡片展示音名采用 C2–C6 的白键映射约定（C D E F G A B 循环），不是原始仿真的实测音高；原始 K 编号和证据数据保持不变。

执行阶段同时展示 Mind ↔ Act：`Target` 箭头从当前记忆指向执行臂的实时曲线位置；`Registered` 返回箭头从真实触键事件点指回已确认卡片。返回光点只运行 0.45 秒视频时间，暂停、回退与循环均由同一视频时钟重算；减少动态效果时不显示光点。确认回执和 ✓ 持续保留，只有日志确认释放后才推进下一目标。剩余数量按已确认触键计算，0 remaining 与最终释放后的 `Sequence complete` 是不同状态。


Act 聚焦的导出在 `scripts/export_hero_presentation.py` 中维护，主导出器自动调用。Act 段使用 1920×1080 原始完整画面；`actDetail.crop` 与 `outputRectangle` 都为 `[0, 0, 1920, 1080]`，`target` 直接使用原图坐标。`highlightRegion: [1000, 60, 920, 780]` 用于前端 SVG 聚焦层：区域内保持原亮度，外围叠加约 30% 深蓝遮罩，边缘柔化并加短角标。该区域包含右臂腕部、夹爪、棒尖和 K26。桌面三段采用相同视频缩放，手机始终保持完整 16:9 画面。独立聚焦中的确认和释放不消耗后续 12 键序列。

`presentation.transition` 记录 Mind → Act 和 Act → Mind2Act 两个边界及前后各 0.2 秒的淡出／淡入；`presentationAt` 返回由媒体时间计算的 `sceneOpacity`（smoothstep），用于视频、高亮、标题及阶段图表，品牌、月亮和控件保持可见。转场约 0.53 秒实际播放时间，不增加片段、不改变时钟映射，两个转场分别位于独立 Act 触键之前，以及 Act 释放之后、闭环首次触键之前。暂停、回退、跳转及循环直接重算透明度；减少动态效果时禁用淡变，保留静态聚焦层。

Act 的 GT 指真实下发的控制器参考目标，不是通过完整验收的专家轨迹。目标棒尖高度取 `feedback82.json` 的 `target`；实测高度取 `trajectory.json` 的 30 Hz 工具位置并线性插值到 120 Hz；六个关节目标／实测值分别取 `control.npz` 同一控制步的 `action` 与 `joint_position_after`，弧度转为度。目标在控制步前下发，关节实测在该步后采样；不使用 `feedback82.measured_tip` 的步前观测替代步后观测，也不平移曲线制造贴合。完整参考曲线预先显示，实测曲线、关节读数和事件点由播放器时间重算。


### 正式项目封面与精简介绍（2026-10-17）

首页沿用最新版 920px 版心及 Sora 标题。机构、标题、作者、贡献说明及资源入口组成居中的正式项目封面。五位作者的共同第一作者标记与 Yuzhi Huang 的 Project Lead 标记按已确认的技术报告同步；不包含占位作者、占位机构或多校占位 logo。预览日期与未开放的报告、社区邀请保持明确标注。

封面与介绍的排版样式位于 `index.html` 的 `<head>`，署名和经过确认的 212 词介绍直接在 `index.html` 中维护。正文采用本地 Source Serif 4（Regular / Semibold WOFF2，附 OFL 许可证；来源 https://github.com/adobe-fonts/source-serif/tree/release）。清华 SIGS 标识从原首页内嵌图像提取为静态 PNG；社区 SVG 来源与许可证见 `media/icons/community/README.md`。

完整 benchmark 说明在独立页面；首页的 30 个任务网格由 `scripts/build_home_tasks.py` 生成。

`test_project_browser.cjs` 覆盖 320、390、820、1440、1920px 下的版心、标题、作者标记、社区图标、按需视频加载、分享及字体加载失败回退。字体和图标均本地提供，不依赖外部 CDN。

### Evaluation Protocol

`protocol.html` presents evaluation protocol v1.0.0 (evaluation code v1.0.0, scoring
`mind2act-final-scoring-20261105`, budget `e2e-p90x1.2-v1`). Task IDs on the page use the
site's IDs (E, FR2, M, ...) rather than the protocol file's (E1, DR2, M1, ...).
Edit this standalone page directly; its layout is in `media/protocol.css`.
The hero uses the same shared typography as the rest of the site via the shared
site shell. Its approved reference artwork is documented in
`media/images/protocol/README.md`. The title and introduction remain native HTML;
the right-hand illustration is rebuilt from the approved composition rather than
using a cropped screenshot. Labels are native text and the curved arrows are SVG,
so neither is blurred by bitmap scaling. The scene uses a 1300×1210 source image with no CSS enlargement beyond its native
width. On desktop, the lunar dome and the episode are separately positioned views
of that same source: the dome keeps its approved scale while the keyboard/contact
view fits inside the viewport with space around its edges. The caption sits beneath
the keyboard, and the data block is lowered to balance the two columns. Short
windows use a narrower introduction to keep the target keyboard clear of the text. On desktop, the title has two lines
and the four data values use the reference's two-by-two layout. The overview fills
the first viewport. A thin rule and four quick links finish the first screen;
they jump to the tracks, clock conditions, metrics and the start of the full
protocol. On mobile these links form two rows below the illustration. Section
navigation is also available in the article sidebar. The complete protocol
article begins below the fold and is preserved. Its 1440px outer width, 200px
sidebar and 30px column gap follow the Benchmark explorer. Larger line spacing,
card padding and section spacing keep the protocol readable. Scroll entrances use
the existing `scripts/home-reveal.js` / `.css` shared by Home, Benchmark and other
pages, including their reduced-motion, print and keyboard-focus handling; the
sticky contents stays outside the animated targets.

Navigation entries are maintained in the `index.html` header and
`scripts/benchmark/header.html`. The leaderboard's full-protocol link is maintained
in `scripts/leaderboard-page.html`; run `python3 scripts/build_leaderboard.py` after
editing that template. The page retains the draft status and pending round parameters.

With the preview running and the existing Playwright environment configured, run
`node scripts/test_protocol_browser.cjs` to check responsive layout, all seven anchors,
scroll highlighting, the mobile menu, and the leaderboard round trip.
