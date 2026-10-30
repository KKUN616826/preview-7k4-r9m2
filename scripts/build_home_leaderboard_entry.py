#!/usr/bin/env python3
"""Replace only the homepage's old ranking section with a scenic destination link."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import re
ROOT=Path(__file__).resolve().parents[1]
class SectionBounds(HTMLParser):
    def __init__(self,source):
        super().__init__();self.source=source;self.lines=[0];self.lines.extend(m.end() for m in re.finditer('\n',source));self.depth=0;self.bounds=None
    def source_offset(self):
        line,col=self.getpos();return self.lines[line-1]+col
    def handle_starttag(self,tag,attrs):
        if tag!='section':return
        if self.depth:self.depth+=1
        elif dict(attrs).get('id')=='top-ten':self.start=self.source_offset();self.depth=1
    def handle_endtag(self,tag):
        if tag=='section' and self.depth:
            self.depth-=1
            if not self.depth:self.bounds=(self.start,self.source_offset()+len('</section>'))
def main():
    entry=(ROOT/'scripts/home-leaderboard-entry.html').read_text().strip()
    for relative in ['index.html','scripts/research_intro.html']:
        path=ROOT/relative;source=path.read_bytes().decode();parser=SectionBounds(source);parser.feed(source)
        if not parser.bounds:raise ValueError(f'Missing homepage leaderboard in {relative}')
        start,end=parser.bounds;source=source[:start]+entry+source[end:]
        source=source.replace('href="#leaderboard"','href="leaderboard.html"')
        if relative=='index.html':
            source=re.sub(r'<(?:link|script)[^>]+(?:href|src)="scripts/view-leaderboard\.(?:css|js)[^"]*"[^>]*>(?:</script>)?','',source)
            source=re.sub(r'<link[^>]+href="scripts/home-leaderboard-entry.css[^\"]*"[^>]*>','',source)
            version=hashlib.sha256((ROOT/'scripts/home-leaderboard-entry.css').read_bytes()).hexdigest()[:10]
            source=source.rstrip()+f'\n<link rel="stylesheet" href="scripts/home-leaderboard-entry.css?v={version}">\n'
        path.write_bytes(source.encode())
if __name__=='__main__':main()
