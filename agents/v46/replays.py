import json,sys,copy,contextlib,io,time,multiprocessing as mp
from pathlib import Path
sys.path.insert(0,r'H:\Kaggriculture\tools')
import benchmark_agents as b
ROOT=Path.cwd()
def run(job):
 name,eid=job;p=json.loads((ROOT/f'outputs/kaggle-losses/{eid}.json').read_text());seat=p['info']['TeamNames'].index('Homii_N');tick=time.time()
 with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
  from kaggle_environments import make
  act,ns=b.load_policy(ROOT/f'work/v46/{name}.py',name)
  def tape(o,c):return copy.deepcopy(p['steps'][o['step']+1][1-seat]['action'])
  env=make('kaggriculture',configuration=dict(p['configuration'],seed=p['info']['seed']),debug=True)
  env.run([act,tape] if seat==0 else [tape,act])
 final=env.steps[-1];r=[s.reward for s in final]
 return dict(candidate=name,episode=eid,seat=seat,rewards=r,margin=r[seat]-r[1-seat],baseline_margin=p['rewards'][seat]-p['rewards'][1-seat],steps=len(env.steps),status=[s.status for s in final],telemetry=act.telemetry,seconds=time.time()-tick)
if __name__=='__main__':
 names=sys.argv[1:] or ['timing','wide'];jobs=[(n,e) for n in names for e in (110250683,110241309,110236449)]
 with open(ROOT/'work/v46/replay-screen.jsonl','a') as f,mp.Pool(3) as pool:
  for r in pool.imap_unordered(run,jobs):f.write(json.dumps(r)+'\n');f.flush();print(json.dumps({k:v for k,v in r.items() if k!='telemetry'}),flush=True)
