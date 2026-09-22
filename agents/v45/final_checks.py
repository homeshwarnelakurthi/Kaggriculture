import sys,json,contextlib,io
from pathlib import Path
R=Path.cwd();sys.path.insert(0,r'H:\Kaggriculture\tools')
from benchmark_agents import load_policy
with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
 from kaggle_environments import make
for seed,opp in [(561,R/'outputs/v44/main.py'),(562,R/'work/parallel_evaluation/barnyard.py')]:
 final,ns=load_policy(R/'work/combined/final.py','final'+str(seed));old,_=load_policy(R/'work/combined/full.py','old'+str(seed));foe,_=load_policy(opp,'foe'+str(seed))
 def compare(obs,cfg):
  actual=final(obs,cfg);expected=old(obs,cfg)
  assert actual==expected,(obs['step'],actual,expected)
  return actual
 env=make('kaggriculture',configuration={'seed':seed,'episodeSteps':720},debug=True);env.run([compare,foe])
 assert len(env.steps)==720 and [s.status for s in env.steps[-1]]==['DONE','DONE']
 print(json.dumps({'source_patch_equivalence':True,'seed':seed,'rewards':[s.reward for s in env.steps[-1]],'steps':720}),flush=True)
# Exercise actual file loader on exact final source, both seats.
for seat in (0,1):
 env=make('kaggriculture',configuration={'seed':563,'episodeSteps':720},debug=True)
 policies=[str(R/'work/combined/final.py'),'starter']
 if seat:policies.reverse()
 env.run(policies)
 assert len(env.steps)==720 and [s.status for s in env.steps[-1]]==['DONE','DONE']
 print(json.dumps({'file_loader_passed':True,'seat':seat,'rewards':[s.reward for s in env.steps[-1]],'steps':720}),flush=True)
