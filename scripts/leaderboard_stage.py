"""Generate the public top-three overview from the same scored model snapshot."""
from html import escape

def render(data):
    parts=['<section class="lb-stage" id="leaderboard-stage" aria-labelledby="lb-title" data-current-view="mind"><div class="lb-stage-head"><div><h1 id="lb-title">Leaderboard</h1><p>Three views of robotic manipulation.</p><div class="lb-stage-tabs" role="group" aria-label="Featured ranking">']
    for v in data['views']:
        parts.append(f'<button type="button" data-stage-select="{v["key"]}" aria-pressed="{str(v["key"]=="mind").lower()}">{escape(v["label"])}</button>')
    parts.append('</div></div></div><div class="lb-stage-visual"><div class="lb-stage-world"><p class="lb-stage-metric">Ranked by Score · 0–100</p><div class="lb-stage-caption" aria-live="polite"><strong>Mind</strong> · Top 3</div><img class="lb-stage-art" src="media/images/leaderboard-lunar-campus-v1.png" alt="Lunar robotics campus with three demonstration stations and a central first, second and third place podium." width="1983" height="793" fetchpriority="high"><video class="lb-stage-motion-video" muted loop playsinline preload="metadata" poster="media/images/leaderboard-lunar-campus-v1.png" aria-hidden="true" tabindex="-1"><source src="media/leaderboard-motion/campus-loop.mp4" type="video/mp4"></video><button type="button" class="lb-stage-motion-toggle" aria-pressed="false" aria-label="Pause mechanical arm animation" hidden>Pause animation</button><div class="lb-podium-labels">')
    mind=sorted([m for m in data['models'] if m['results']['mind']['score'] is not None],key=lambda m:m['results']['mind']['score'],reverse=True)
    for rank in [2,1,3]:
        m=mind[rank-1]
        parts.append(f'<button type="button" class="lb-podium-label lb-podium-rank-{rank}" data-podium-rank="{rank}" data-stage-model="{m["id"]}" data-stage-suite="mind"><span class="lb-podium-avatar"><img src="{escape(m["icon"])}" alt=""><span class="lb-podium-monogram" hidden></span></span><span class="lb-podium-name">{escape(m["name"])}</span><strong>{m["results"]["mind"]["score"]:.2f}</strong></button>')
    parts.append('</div><div class="lb-stage-stations"><button type="button" data-stage-select="mind" aria-label="Show Mind rankings"><span>Mind</span></button><button type="button" data-stage-select="act" aria-label="Show Act rankings"><span>Act</span></button><button type="button" data-stage-select="coupling" aria-label="Show Mind2Act rankings"><span>Mind2Act</span></button></div></div></div><div class="lb-stage-footer"><a href="#results" class="lb-stage-full">View full results ↓</a><p>Original 15-task result snapshot · Added tasks not yet evaluated</p></div></section>')
    return ''.join(parts)
