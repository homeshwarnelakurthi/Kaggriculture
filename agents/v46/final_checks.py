import sys,json,copy,contextlib,io
from pathlib import Path
sys.path.insert(0,r'H:\Kaggriculture\tools')
from benchmark_agents import load_policy
ROOT=Path.cwd();act,ns=load_policy(ROOT/'outputs/v46/main.py','guards')
p=json.loads((ROOT/'outputs/kaggle-losses/110250683.json').read_text());obs=copy.deepcopy(p['steps'][300][0]['observation'])
ns['_V46_FORECAST_PARENT']=lambda o,c:{}
def call(step,source=obs):
 o=copy.deepcopy(source);o['step']=step;before=copy.deepcopy(o);m=ns['_flow_forecast'](o,{})
 assert o==before,'observation mutation'
 return m['synchronized']
assert not any(call(i) for i in range(23))
assert call(23)
# Random weeds are irrelevant to productive synchrony.
weed=copy.deepcopy(obs);weed['farms'][1]['tiles'][7][7]={'kind':'WEED'}
assert call(24,weed)
# A productive-tile difference must immediately disable the extension.
changed=copy.deepcopy(obs);changed['farms'][1]['tiles'][3][3]['yield_units']+=1
assert not call(25,changed)
assert not any(call(i) for i in range(26,49))
assert call(49)
assert not call(51),'missing observations must reset confidence'
assert not call(0),'new episodes reset confidence'
print(json.dumps({'synchrony_guards':True,'mutation_guard':True,'gap_reset':True}),flush=True)
with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
 from kaggle_environments import make
for seat in (0,1):
 final,_=load_policy(ROOT/'outputs/v46/main.py','final'+str(seat));old,_=load_policy(ROOT/'work/v46/sync_productive.py','bench'+str(seat));foe,_=load_policy(ROOT/'outputs/v45/main.py','foe'+str(seat))
 def compare(o,c):
  a=final(o,c);b=old(o,c);assert a==b,(o['step'],a,b);return a
 env=make('kaggriculture',configuration={'seed':761,'episodeSteps':720},debug=True)
 env.run([compare,foe] if seat==0 else [foe,compare])
 assert len(env.steps)==720 and [s.status for s in env.steps[-1]]==['DONE','DONE']
 print(json.dumps({'final_action_equivalence':True,'seed':761,'seat':seat,'rewards':[s.reward for s in env.steps[-1]]}),flush=True)
for seat in (0,1):
 env=make('kaggriculture',configuration={'seed':762,'episodeSteps':720},debug=True)
 agents=[str(ROOT/'outputs/v46/main.py'),'starter']
 if seat:agents.reverse()
 env.run(agents)
 assert len(env.steps)==720 and [s.status for s in env.steps[-1]]==['DONE','DONE']
 print(json.dumps({'file_loader':True,'seed':762,'seat':seat,'rewards':[s.reward for s in env.steps[-1]]}),flush=True)
