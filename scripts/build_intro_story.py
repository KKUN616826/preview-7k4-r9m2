"""Build the four-screen introduction without touching unrelated homepage modules."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def render():
    markup=(ROOT/'scripts/intro-story.html').read_text()
    count=sum(len(s['cases']) for s in json.loads((ROOT/'data/benchmark-navigation.json').read_text()))
    for name,value in {'TASK_COUNT':str(count),'OVERVIEW_FIGURE':(ROOT/'scripts/intro-story-figure.html').read_text(),'RESEARCH_BACKGROUND':(ROOT/'scripts/intro-story-background.html').read_text()}.items():markup=markup.replace('__'+name+'__',value)
    for asset in ['scripts/intro-story.css','scripts/intro-story.js']:
        markup=markup.replace(asset+'"',asset+'?v='+hashlib.sha256((ROOT/asset).read_bytes()).hexdigest()[:10]+'"')
    return markup.rstrip("\r\n")+"\n"
if __name__=='__main__':
    p=ROOT/'index.html';source=p.read_bytes().decode()
    pattern=r'<!-- INTRO_STORY_START -->.*?<!-- INTRO_STORY_END -->(?:\r?\n)?' if '<!-- INTRO_STORY_START -->' in source else r'<div id="introduction" class="research-abstract".*?</div>(?:\r?\n)?'
    source,n=re.subn(pattern,lambda _:render(),source,count=1,flags=re.S);assert n==1
    p.write_bytes(source.encode());print('Built four-screen research introduction.')
