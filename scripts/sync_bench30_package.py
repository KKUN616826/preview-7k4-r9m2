#!/usr/bin/env python3
"""Match the sampled bench30 package to site aliases and episode-specific instructions.
Copies video bytes without re-encoding; keeps a recoverable backup of replaced assets.
"""
import argparse,csv,hashlib,json,re,shutil,subprocess,tempfile
from html import escape,unescape
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ALIASES={'E1':'E','F1':'F','P1':'P','S1':'S','M1':'M','FR3':'DR3','PR7':'DR7','PR8':'PR6'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('videos',type=Path);parser.add_argument('instructions_csv',type=Path);args=parser.parse_args()
 assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='leaderboard-motion'
 episodes=list(csv.DictReader(args.instructions_csv.open(encoding='utf-8-sig')))
 rows=[]
 for line in (args.videos/'README.md').read_text().splitlines():
  if not re.match(r'\| (CP|E|F|M|P|S)',line):continue
  task,level,name,duration,size,instruction=[v.strip() for v in line.split('|')[1:-1]]
  episode=name.removeprefix(f'{task}_{level}_').removesuffix('.mp4');episode=re.sub(r'^.*?(episode_\d+)$',r'\1',episode)
  matches=[r for r in episodes if r['task']==task and r['difficulty']==level and r['episode_id'].split('/')[-1]==episode]
  assert len(matches)==1,(task,level,episode)
  assert matches[0]['instruction']==instruction,(task,level,'README/CSV disagreement')
  assert (args.videos/name).is_file()
  rows.append(dict(task=ALIASES.get(task,task),source_task=task,level=level,source_filename=name,instruction=instruction,episode_id=matches[0]['episode_id'],parameter_values=matches[0]['parameter_values']))
 assert len(rows)==90 and len({(r['task'],r['level']) for r in rows})==90
 suites=json.loads((ROOT/'data/benchmark-navigation.json').read_text());assert {r['task'] for r in rows}=={c['id'] for s in suites for c in s['cases']}
 backup=Path(tempfile.mkdtemp(prefix='bench30-media-backup-',dir=ROOT.parent))
 def preserve(path):
  if path.exists():
   target=backup/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
 # Source/template and metadata backups also support recovering uncommitted state.
 for folder in ['scripts/benchmark','data']:
  shutil.copytree(ROOT/folder,backup/folder,dirs_exist_ok=True)
 for i,r in enumerate(rows):
  src=args.videos/r['source_filename'];dst=ROOT/f'media/task-demos/{r["task"]}/{r["level"]}.mp4'
  r['previous_sha256']=sha(dst) if dst.exists() else None;r['source_sha256']=sha(src)
  r['audit_status']='missing' if not dst.exists() else 'same' if r['previous_sha256']==r['source_sha256'] else 'different recording/version'
  if not dst.exists() or r['previous_sha256']!=r['source_sha256']:
   preserve(dst);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
  r['path']=dst.relative_to(ROOT).as_posix();r['sha256']=sha(dst);assert r['sha256']==r['source_sha256'];r['bytes']=dst.stat().st_size
  probe=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_format','-show_streams','-of','json',str(dst)]));v=next(s for s in probe['streams'] if s['codec_type']=='video')
  r.update(duration=float(probe['format']['duration']),width=v['width'],height=v['height'],codec=v['codec_name'],presentation='multi-view',processing='exact source copy; no re-encoding')
  assert v['width']==1920 and v['height']==480
  poster=ROOT/f'media/benchmark-expansion/{r["task"]}/{r["level"]}.jpg';preserve(poster);poster.parent.mkdir(parents=True,exist_ok=True)
  subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y','-ss','1','-i',str(dst),'-frames:v','1','-q:v','2',str(poster)],check=True)
  if r['level']=='easy':
   cover=ROOT/f'media/benchmark-covers/{r["task"]}.jpg';preserve(cover)
   subprocess.run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y','-ss','1','-i',str(dst),'-vf','crop=640:480:0:0','-frames:v','1','-q:v','2',str(cover)],check=True)
  print(f'{i+1}/90 {r["source_task"]} → {r["task"]} / {r["level"]}',flush=True)
 expansion=json.loads((ROOT/'data/benchmark-expansion.json').read_text())
 for case in expansion['cases']:
  selected=[r for r in rows if r['task']==case['id']]
  case['media']={r['level']:r['source_filename'] for r in selected};case['instructions']={r['level']:r['instruction'] for r in selected}
  if case['id']=='E2':
   case['summary']='Remember entity–value associations, decode the physical expression, and enter its exact result on the keypad.'
   case['focus']=['Entity–value memory','Expression decoding','Physical keypad entry']
 (ROOT/'data/benchmark-expansion.json').write_text(json.dumps(expansion,ensure_ascii=False,indent=2)+'\n')
 for suite in suites:
  for case in suite['cases']:
   case.update(initial_level='easy',available_levels=['easy','medium','hard'],cover=f'media/benchmark-covers/{case["id"]}.jpg',row_cover=f'media/benchmark-covers/{case["id"]}.jpg')
   if case['id']=='E2':case['summary']=next(c['summary'] for c in expansion['cases'] if c['id']=='E2')
 (ROOT/'data/benchmark-navigation.json').write_text(json.dumps(suites,ensure_ascii=False,indent=2)+'\n')
 from build_benchmark_expansion import task_content
 for case in expansion['cases']:(ROOT/f'scripts/benchmark/{case["id"]}.html').write_text(task_content(case))
 for suite in suites:
  for case in suite['cases']:
   cid=case['id'];p=ROOT/f'scripts/benchmark/{cid}.html';content=p.read_text()
   for r in [r for r in rows if r['task']==cid]:
    pattern=r'(<section class="demo-panel"[^>]*data-panel="'+r['level']+r'".*?)(?=<section class="demo-panel"|<nav class="task-footer")'
    def update(m):
     panel=m[0]
     panel=re.sub(r'(<div class="instruction"><h2>Instruction</h2><p>).*?(</p>)',lambda x:x[1]+escape(r['instruction'])+x[2],panel,count=1,flags=re.S)
     panel=re.sub(r'poster="[^"]+"',f'poster="../media/benchmark-expansion/{cid}/{r["level"]}.jpg"',panel)
     panel=re.sub(r'<figcaption>.*?</figcaption>',f'<figcaption>{r["level"].title()} · Multi-view demonstration</figcaption>',panel,flags=re.S)
     return panel
    content,n=re.subn(pattern,update,content,count=1,flags=re.S);assert n==1,(cid,r['level'])
   p.write_text(content)
 (ROOT/'data/benchmark-video-imports.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
 report={'readme_sha256':sha(args.videos/'README.md'),'csv_sha256':sha(args.instructions_csv),'backup_directory':str(backup),'aliases':ALIASES,'counts':{key:sum(r['audit_status']==key for r in rows) for key in ['missing','same','different recording/version']},'instruction_matching':'All 90 selected episodes matched README and CSV exactly; PR1/PR2 targets preserved.'}
 (ROOT/'data/bench30-sync-audit.json').write_text(json.dumps(report,indent=2)+'\n')
 from build_benchmark import page,detail,category
 for suite in suites:
  (ROOT/f'benchmark/{suite["slug"]}.html').write_text(page(suites,suite['slug'],suite['name'],category(suite),'../'))
  for c in suite['cases']:(ROOT/f'tasks/{c["id"]}.html').write_text(page(suites,c['id'],c['title'],detail(suite,c),'../',True))
 print('Done. Backup:',backup)
if __name__=='__main__':main()
