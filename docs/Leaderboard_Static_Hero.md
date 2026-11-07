# Leaderboard 首屏

全屏月球园区场景（`media/images/leaderboard-lunar-campus-v4.webp`，机械臂循环动画保留）。v4 在 v3 的月球和地球地平线之间加高了一段天空（`scripts/extend_lunar_sky.py`），让两者之间有空间放模型。

## 模型怎么摆

- 每个已发布成绩的 VLA / WAM 模型一条航线：从地球地平线上的发射点（地球表面，0 分）飞向月球下沿的着陆点（月球表面，100 分 = 所有 case 全部完成）。
- 发射点从左到右按发布顺序排列；航线先竖直上升再转向月球，各自独立，不会挤成一条线。
- 模型停在航线全长的「Overall 分数 %」处：已飞部分是彩色实线，剩下到月球的部分是虚线。25 / 50 / 75 的等高线连接所有航线上的同一比例。
- 第一名放大并标出名字、分数和「离月球还差多少」，前三名标分数，其余悬停或聚焦时显示。
- 少于 3 个成绩时显示匿名占位模型（Model A–N），标题下注明 "placeholder … not results" 和首批发布日期。

## 文件

- 首屏生成：`scripts/leaderboard_stage.py`（几何参数 `MOON`、`HORIZON`、`LAUNCH`、`LANDING`，单位为 v4 的 1983 × 1053）
- 样式：`scripts/leaderboard-stage.css`
- 背景加高：`scripts/extend_lunar_sky.py`
- 重新生成页面：`python3 scripts/build_leaderboard.py`
