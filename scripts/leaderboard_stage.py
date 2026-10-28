"""Generate the public top-three overview from the same scored model snapshot."""
from html import escape

def render(data):
    parts=['<section class="lb-stage" id="leaderboard-stage" aria-labelledby="lb-title" data-current-view="mind"><div class="lb-stage-head"><div><h1 id="lb-title">Leaderboard</h1><p>Three views of robotic manipulation.</p><div class="lb-stage-tabs" role="group" aria-label="Featured ranking">']
    for v in data['views']:
        parts.append(f'<button type="button" data-stage-select="{v["key"]}" aria-pressed="{str(v["key"]=="mind").lower()}">{escape(v["label"])}</button>')
    parts.append('</div></div><p class="lb-stage-metric">Ranked by Score · 0–100</p></div><div class="lb-stage-world"><div class="lb-stage-caption" aria-live="polite"><strong>Mind</strong> · Top 3</div><img class="lb-stage-art" src="media/images/leaderboard-lunar-campus-v1.png" alt="Lunar robotics campus with three demonstration stations and a central first, second and third place podium." width="1983" height="793" fetchpriority="high"><div class="lb-podium-labels">')
    mind=sorted([m for m in data['models'] if m['results']['mind']['score'] is not None],key=lambda m:m['results']['mind']['score'],reverse=True)
    for rank in [2,1,3]:
        m=mind[rank-1]
        parts.append(f'<button type="button" class="lb-podium-label lb-podium-rank-{rank}" data-podium-rank="{rank}" data-stage-model="{m["id"]}" data-stage-suite="mind"><span class="lb-podium-avatar"><img src="{escape(m["icon"])}" alt=""><span class="lb-podium-monogram" hidden></span></span><span class="lb-podium-name">{escape(m["name"])}</span><strong>{m["results"]["mind"]["score"]:.2f}</strong></button>')
    parts.append('</div><div class="lb-stage-stations"><button type="button" data-stage-select="mind">Mind</button><button type="button" data-stage-select="act">Act</button><button type="button" data-stage-select="coupling">Mind2Act</button></div></div><div class="lb-stage-boards">')
    for v in data['views']:
        ranked=sorted([m for m in data['models'] if m['results'][v['key']]['score'] is not None],key=lambda m:m['results'][v['key']]['score'],reverse=True)[:3]
        parts.append(f'<section class="lb-stage-board" data-board-view="{v["key"]}" aria-label="{v["label"]} top three"><button type="button" class="lb-board-title" data-stage-select="{v["key"]}"><img src="{v["icon"]}" alt=""><span>{v["label"]}</span></button><ol>')
        for rank,m in enumerate(ranked,1):
            parts.append(f'<li><button type="button" data-stage-model="{m["id"]}" data-stage-suite="{v["key"]}"><span class="lb-board-rank">{rank}</span><span>{escape(m["name"])}</span><strong>{m["results"][v["key"]]["score"]:.2f}</strong></button></li>')
        parts.append('</ol></section>')
    parts.append('</div><div class="lb-stage-footer"><a href="#results" class="lb-stage-full">View full results ↓</a><p>Original 15-task result snapshot · Added tasks not yet evaluated</p></div></section>')
    return ''.join(parts)
