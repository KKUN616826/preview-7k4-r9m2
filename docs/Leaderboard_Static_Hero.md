# Leaderboard 首屏

全屏月球园区场景（`media/images/leaderboard-lunar-campus-v4.webp`，机械臂循环动画保留）。v4 在 v3 的月球和地球地平线之间加高了一段天空（`scripts/extend_lunar_sky.py`），让两者之间有空间放模型。

## 怎么读

- 高度就是分数：地球地平线是 0，月球下沿那条红色虚线是 100（所有 case 全部完成）；25 / 50 / 75 是横跨天空的刻度线，左侧标 "Overall score"。
- 每个已发布成绩的 VLA / WAM 模型从地平线上自己的发射点竖直升起，停在 Clean Overall 分数的高度；发射点从左到右按发布顺序排列。
- 所有模型同一种墨色，第一名用强调色，并标出名字、分数和「离月球还差多少」，一条虚线连到 100；前三名标 #1–#3。
- 首屏只排 Overall；Mind / Act / Mind2Act 和 Random 在下面的表格里。
- 少于 3 个成绩时显示匿名占位模型（Model A–N），标题下注明 "placeholder … not results" 和首批发布日期。

## 版面

- 桌面：园区始终完整显示（全宽、贴底），超宽或很矮的屏幕上首屏会加高而不是裁掉图表。
- 手机：显示月球正下方那一窄段画面（天空最高），模型在这一段里重新排开；用静态图，不播放循环视频。

## 文件

- 首屏生成：`scripts/leaderboard_stage.py`（几何参数 `TOP`、`HORIZON`、`PADS`，单位为 v4 的 1983 × 1053）
- 样式：`scripts/leaderboard-stage.css`
- 背景加高：`scripts/extend_lunar_sky.py`
- 重新生成页面：`python3 scripts/build_leaderboard.py`
