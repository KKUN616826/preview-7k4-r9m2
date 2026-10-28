#!/usr/bin/env python3
"""Import the explicitly listed expansion videos, without re-encoding their frames.
Usage: python3 scripts/import_benchmark_videos.py /path/to/downloaded/videos
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path);args=parser.parse_args()
    data=json.loads((ROOT/'data/benchmark-expansion.json').read_text());manifest=[]
    for case in data['cases']:
        for level,name in case['media'].items():
            src=args.directory/name
            if not src.is_file():raise FileNotFoundError(src)
            dst=ROOT/f'media/task-demos/{case["id"]}/{level}.mp4';dst.parent.mkdir(parents=True,exist_ok=True)
            if not dst.exists():
                subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-i',str(src),'-map','0:v:0','-map','0:a?','-c','copy','-movflags','+faststart',str(dst)],check=True)
            probe=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_format','-show_streams','-of','json',str(dst)]))
            v=next(s for s in probe['streams'] if s['codec_type']=='video')
            poster=ROOT/f'media/benchmark-expansion/{case["id"]}/{level}.jpg';poster.parent.mkdir(parents=True,exist_ok=True)
            # Preserve the complete multi-view frame in the player poster.
            if not poster.exists():subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-ss','1','-i',str(dst),'-frames:v','1','-q:v','2',str(poster)],check=True)
            cover=ROOT/f'media/benchmark-covers/{case["id"]}.jpg'
            if not cover.exists():
                filters=['crop=1280:960:0:0'] if 'triview' in name.lower() else []
                cmd=['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-ss','1','-i',str(dst),'-frames:v','1','-q:v','2']
                if filters:cmd+=['-vf',','.join(filters)]
                subprocess.run(cmd+[str(cover)],check=True)
            manifest.append({'task':case['id'],'level':level,'source_filename':name,'source_sha256':digest(src),'path':dst.relative_to(ROOT).as_posix(),'sha256':digest(dst),'bytes':dst.stat().st_size,'duration':float(probe['format']['duration']),'width':v['width'],'height':v['height'],'codec':v['codec_name'],'presentation':'multi-view' if 'triview' in name.lower() else 'head-view','processing':'stream copy; faststart; no resizing or frame re-encoding'})
    (ROOT/'data/benchmark-video-imports.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Imported {len(manifest)} videos for {len(data["cases"])} tasks, without frame re-encoding.')
if __name__=='__main__':main()
