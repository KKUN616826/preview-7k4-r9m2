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

## 像素小火箭与柔和配色（2026-11-08）

- 火箭改为与网站像素小人同风格的 16 × 24 像素图（`leaderboard_stage.py` 的 `_ROCKET`、`_FLAMES`）：圆胖机身、大圆舷窗放 logo、短尾翼，两帧像素尾焰交替闪动。为保持像素边缘清晰，火箭只倾斜航线角度的一半。
- 配色统一为网站色板：所有火箭奶油白机身配雾蓝灰，第一名锈红；航线从彩色改为白色尾烟。第一名的标签始终在火箭正上方，避免盖住相邻火箭。
- 地球的蓝色调淡为网站的雾蓝（`enhance_earth.py` 混合强度 0.5），大气亮边减弱；动画已重新渲染。

## 2026-11-08: one summit

- Every route converges on one landing beacon on the Moon's lower limb (`SUMMIT`, inside the narrow
  `LANDING` zone), with a pulsing rust ring, a glow and a corridor of light between the outermost
  routes. The Moon tag stands on the Moon right above the beacon.
- Launch sites are chosen by rank, not release order (`_slots`): the best model launches a little
  right of the middle, under the beacon, and the rest alternate outward, the right flank filling more
  slowly because routes lean toward the Moon there; every other pair is swapped so the flanks are not
  straight lines. The rockets stand like a mountain with the leader at its peak. The two gaps beside
  the leader are wider for its larger rocket.
- Routes climb almost straight up (first control point at 85 % of the height) and converge only near
  the Moon, so the many low scores keep their spacing. Parameters were picked by measuring rocket
  overlap over the placeholder and 60 random rosters.
- Runner-up score chips sit above their rockets, or beside them when a neighbour or the leader's label
  is in the way (`_label_sides`). The 75 contour keeps its line but not its number, which the leader's
  label would cover.

## 2026-11-08: slim rockets

- The pixel rockets read as too big and loud. Each model now rides a slim vector rocket (20 x 44):
  cream ogive hull with an ink outline, accent nose and swept fins, a round porthole holding the logo
  and a soft flickering flame. About 1.65vw wide (leader 2.2vw, rust accent, faint warm glow); 12 px
  on phones (leader 19 px).
- Calmer effects: thinner contrails (2.2), a gentle hover, a smaller and fainter summit pulse, and a
  slightly smaller leader score. `_label_sides` uses the new rocket size.

## 2026-11-08: the Moon overhead, names on every rocket

- The Moon sat in the top-right corner, so every route leaned right. It now hangs at the top centre,
  its surface a level arc facing the Earth's horizon. `extend_lunar_sky.py --no-moon` builds the sky
  without the Moon; `center_moon.py` paints it back from the artwork's own Moon texture, resampled in
  limb coordinates (craters keep their foreshortening; the texture folds back, mirrored, where the
  source runs out of arc or depth). The result is `leaderboard-lunar-campus-v6.webp` (v5 removed).
  The phone header uses a crop of the moonless sky, `leaderboard-sky.webp`.
- Routes are symmetric: launch sites 440 to 1543 around the centre, a landing zone 871 to 1112 under
  the beacon at the Moon's lowest point. The leader launches from the middle; the rest alternate
  outward by rank. The Mind tag hangs lower so the left launch sites clear it.
- Every model carries its name (desktop above 1180 px): a tag above its rocket, at most one launch
  spacing wide (`--tag`, longer names end in an ellipsis and show in full on hover); below or beside
  the rocket when the leader's label or a rocket is in the way. The top three add their score. Only the
  50 contour keeps its number.
- On narrow desktops the Moon tag sits right of the beacon; on phones above it, and the phone crop
  (artwork x 391 to 1591) is centred on the Moon.
