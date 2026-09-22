import sys,json,copy,contextlib,io,collections
from pathlib import Path
sys.path.insert(0,r'H:\Kaggriculture\work\runtime1327')
with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
 from kaggle_environments import make
 from kaggle_environments.envs.kaggriculture import kaggriculture as e
sys.path.insert(0,r'H:\Kaggriculture\tools')
from benchmark_agents import load_policy
label=sys.argv[1];source=Path(sys.argv[2]).resolve()
origmarket=e._process_market;origrefresh=e._daily_refresh_animals;origdrop=e._drop_inventories_to_shed
ctx={};events=[]
def market(state,env):
 ctx.update(step=state[0].observation.step,farms=state[0].observation.farms,privates=[s.observation.private for s in state])
 return origmarket(state,env)
def refresh(farm,day):
 seat=next(i for i,f in enumerate(ctx['farms']) if f is farm)
 for y,row in enumerate(farm['tiles']):
  for x,t in enumerate(row):
   if not isinstance(t,dict) or t.get('animal')!='GOOSE':continue
   age=day+1-t['placed_day']-4
   if age>=0:
    bonus=t.get('pending_care_bonus',0) if t['fed_today'] else 0
    expected=1+bonus;before=t['yield_units'];lost=max(0,before+expected-4)
    events.append(dict(kind='production',step=ctx['step'],seat=seat,xy=[x,y],held=before,bonus=bonus,fed=t['fed_today'],cared=t['cared_today'],produced=expected-lost,cap_lost=lost))
 return origrefresh(farm,day)
def drop(private,capacity):
 seat=next(i for i,p in enumerate(ctx['privates']) if p is private)
 before=private['shed'].get('EGG',0)+sum(v.get('EGG',0) for v in private['inventories'])
 ans=origdrop(private,capacity)
 after=private['shed'].get('EGG',0)+sum(v.get('EGG',0) for v in private['inventories'])
 if before!=after:events.append(dict(kind='discard',step=ctx['step'],seat=seat,eggs=before-after))
 return ans
e._process_market=market;e._daily_refresh_animals=refresh;e._drop_inventories_to_shed=drop
for eid in ([int(sys.argv[3])] if len(sys.argv)>3 else (110250683,110241309,110236449)):
 p=json.loads(Path(f'outputs/kaggle-losses/{eid}.json').read_text());events.clear()
 def tape(seat):return lambda o,c:copy.deepcopy(p['steps'][o['step']+1][seat]['action'])
 with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
  env=make('kaggriculture',configuration=dict(p['configuration'],seed=p['info']['seed']),debug=True);policy,ns=load_policy(source,label+str(eid));seat=p['info']['TeamNames'].index('Homii_N');env.run([policy,tape(1)] if seat==0 else [tape(0),policy])
 assert len(env.steps)==720 and all(s.status=='DONE' for s in env.steps[-1])
 summary=[]
 for seat in (0,1):
  a=[x for x in events if x['seat']==seat];q=[x for x in a if x['kind']=='production']
  leftover=sum(t.get('yield_units',0) for row in env.steps[-1][0].observation.farms[seat]['tiles'] for t in row if isinstance(t,dict) and t.get('animal')=='GOOSE')
  summary.append(dict(seat=seat,name=p['info']['TeamNames'][seat],produced=sum(x['produced'] for x in q),cap_lost=sum(x['cap_lost'] for x in q),discarded=sum(x['eggs'] for x in a if x['kind']=='discard'),production_days=len(q),fed_days=sum(x['fed'] for x in q),care_days=sum(x['cared'] for x in q),bonuses=sum(x['bonus'] for x in q),left_on_animals=leftover))
 out=dict(episode=eid,candidate=label,rewards=[s.reward for s in env.steps[-1]],summary=summary,events=events);Path(f'outputs/v47/{label}-{eid}-egg-ledger.json').write_text(json.dumps(out,indent=2));print(json.dumps(dict(episode=eid,summary=summary)),flush=True)
