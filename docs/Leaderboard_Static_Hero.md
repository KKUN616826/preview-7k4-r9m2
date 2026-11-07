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

## 地平线与版面（2026-11-08）

- 原图的相机有约 2.8° 的侧倾，地平线向右下斜、弧顶偏在左边。页面把静态图和机械臂视频一起反向旋转 2.8° 并放大 3.5%（`leaderboard-stage.css` 的 `.lb-stage-art`），地平线成为左右对称的圆弧；`leaderboard_stage.py` 的 `ROLL`、`ZOOM`、`_view` 用同一变换摆放航线、标签和地球、月球。
- 桌面端只显示画面顶部到第 940 行（共 1053 行），园区最前面一圈不再出现；首屏高度等于这一段加 100px 标题空间，不再强制占满一屏。图的上沿渐隐到天空色，月球不再被直线截断。

## 小火箭与地球（2026-11-08）

- 每个模型乘一艘小火箭（logo 或名字缩写在舷窗里），沿原来的航线飞向月球，机头随航线转向；到位后轻微悬停，尾焰闪动。第一名火箭更大、红色，带光晕。
- 地球：`scripts/enhance_earth.py` 把原图里地球的海洋加深为蓝色、云层保持白色，并在地平线上画一道大气亮边；只改地平线下方偏蓝、偏亮的像素和地平线上方的天空像素，穹顶、塔、天线等建筑不受影响。同一处理应用于静态图（`leaderboard-lunar-campus-v3e.webp` → 加高天空后 `-v5.webp`）和机械臂动画的两张底图（`clean-plate-*-earth.webp`），动画已用新图重新渲染。
- 原来压在建筑上的「地球表面」发光线已去掉；"0 · Earth surface" 标签移到右侧海面上。
- Mind / Act / Mind2Act 三个标签缩小并下移，更贴近各自的机械臂。
