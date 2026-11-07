# Leaderboard 首屏

首屏是一张紧凑的「地球 → 月球」卡片，参考 RoboDojo 的雪山榜和其他抽象榜单：卡片下沿是地球表面（0 分），上沿是月球表面（100 分，所有 case 全部完成）。每个已发布成绩的 VLA / WAM 模型按 Overall 分数（30 个任务平均，Clean 设置）飞到对应高度，从左到右按发布顺序排列，带 logo、名称和分数；第一名额外标出离月球还差多少分。卡片之后紧接完整榜单。

## 内容与交互

- 分数读取 `data/leaderboard-results.json`，不维护第二套成绩。
- 点击模型进入 `models/<id>.html`（成绩与诊断卡）。
- 少于 3 个 VLA / WAM 成绩时，显示匿名占位模型（Model A–N），并标注 "placeholder … not results" 和首批发布日期。
- 模型按发布顺序依次从地球升起；开启「减少动态效果」时直接显示最终画面。
- 手机上只标第一名的名称和分数，其余模型悬停或聚焦时显示。

## 文件

- 首屏内容生成：`scripts/leaderboard_stage.py`（月球、地球为内联 SVG，无位图）
- 样式：`scripts/leaderboard-stage.css`
- 重新生成页面：`python3 scripts/build_leaderboard.py`

## 历史

此前的月球园区全屏场景（`media/images/leaderboard-lunar-campus-v*.webp`、`media/leaderboard-motion/`）已不在页面中使用，素材保留以便复用。
