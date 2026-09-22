from pathlib import Path
import json,statistics,hashlib,tarfile,shutil,datetime
R=Path.cwd();W=R/'work/v46';O=R/'outputs/v46'
def read(name,n):
 a=[json.loads(l) for l in (W/(name+'.jsonl')).read_text().splitlines()];assert len(a)==n,(name,len(a),n);assert all(x['valid'] for x in a);return a
def stats(a):
 m=[x['mine']-x['theirs'] for x in a]
 return dict(games=len(a),wins=sum(v>0 for v in m),ties=sum(v==0 for v in m),losses=sum(v<0 for v in m),mean_margin=statistics.mean(m),minimum_margin=min(m),maximum_turn_ms=max(x['max_turn_ms'] for x in a),nonzero_errors=[{k:v for k,v in x['telemetry'].items() if 'error' in k and v} for x in a if any('error' in k and v for k,v in x['telemetry'].items())])
screen=read('productive-screen',24);paired=read('trade-holdout',32);fresh=read('final-holdout',20);front=read('front-trade',12)
summary={'holdout_vs_v45':stats(fresh),'screen':{},'paired_external':{},'front_trade':{}}
for op in ['v45','wide','barnyard']:summary['screen'][op]=stats([x for x in screen if x['opponent']==op])
for op in ['wide','trader']:
 a=[x for x in paired if x['candidate']=='v46' and x['opponent']==op];b=[x for x in paired if x['candidate']=='v45' and x['opponent']==op]
 bm={(x['seed'],x['seat']):x for x in b};diffs=[];shopmatches=0
 for x in a:
  y=bm[x['seed'],x['seat']];diffs.append((x['mine']-x['theirs'])-(y['mine']-y['theirs']));shopmatches+=x['shops']==y['shops']
 summary['paired_external'][op]={'v46':stats(a),'v45':stats(b),'mean_margin_change':statistics.mean(diffs),'minimum_margin_change':min(diffs),'same_shop_sequence_pairs':shopmatches}
for who in ['v46','v45']:summary['front_trade'][who]=stats([x for x in front if x['candidate']==who])
a={(x['seed'],x['seat']):x for x in front if x['candidate']=='v45'}
d=[(x['mine']-x['theirs'])-(a[x['seed'],x['seat']]['mine']-a[x['seed'],x['seat']]['theirs']) for x in front if x['candidate']=='v46']
summary['front_trade']['mean_margin_change']=statistics.mean(d)
summary['front_trade']['minimum_margin_change']=min(d)
replays=[json.loads(l) for l in (W/'replay-screen.jsonl').read_text().splitlines()];summary['replay_fixtures']=[{k:v for k,v in x.items() if k!='telemetry'} for x in replays if x['candidate']=='sync_productive']
checks=[]
for l in (W/'final-checks.log').read_text().splitlines():
 if l.startswith('{'):checks.append(json.loads(l))
assert len(checks)==5;summary['final_checks']=checks
assert '"passed"' in (W/'inherited-checks.log').read_text()
(O/'validation.json').write_text(json.dumps(summary,indent=2))
for name in ['productive-screen.jsonl','trade-holdout.jsonl','final-holdout.jsonl','front-trade.jsonl','replay-screen.jsonl','final_checks.py','final-checks.log','inherited_checks.py','inherited-checks.log','replays.py']:
 shutil.copyfile(W/name,O/name)
for name in ['wide.py','trader.py','trader_front.py']:
 (O/'validation-opponents').mkdir(exist_ok=True);shutil.copyfile(W/name,O/'validation-opponents'/name)
archive=O/'v46.tar.gz'
with tarfile.open(archive,'w:gz') as t:
 for name in ['main.py','NOTICE.txt','LICENSE-APACHE-2.0.txt']:t.add(O/name,arcname=name)
with tarfile.open(archive,'r:gz') as t:
 assert sorted(t.getnames())==sorted(['main.py','NOTICE.txt','LICENSE-APACHE-2.0.txt'])
 assert t.extractfile('main.py').read()==(O/'main.py').read_bytes()
build={'version':'V46','status':'built and locally validated; not submitted','source_sha256':hashlib.sha256((O/'main.py').read_bytes()).hexdigest(),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'archive_bytes':archive.stat().st_size,'base':'V45','change':'Stock-backed sale reservations use one full day of matching public productive tiles and worker positions; preserve V45 fallback when production diverges. No extra egg harvesting or wheat-trading strategy included.'}
(O/'build.json').write_text(json.dumps(build,indent=2));print(json.dumps(summary,indent=2))
