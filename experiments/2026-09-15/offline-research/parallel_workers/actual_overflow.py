import sys,collections,json,contextlib,io
from pathlib import Path
BASE=Path(r'H:\Kaggriculture');OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'tools'))
from benchmark_agents import load_policy
with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
 from kaggle_environments import make
records=[];games=[]
for seed in (301,302,303):
 env=make('kaggriculture',configuration={'seed':seed,'episodeSteps':720},debug=True)
 module=sys.modules[env.interpreter.__module__]
 original_day=module._end_of_day;original_drop=module._drop_inventories_to_shed
 context={}
 def day_hook(state,env,day):
  context.update(day=day,actor=0,quotes=dict(state[0].observation.market['prices']))
  return original_day(state,env,day)
 def drop_hook(private,capacity):
  def totals(p):
   result=collections.Counter(p['shed'])
   for inv in p['inventories']:result.update(inv)
   return result
  before=totals(private);result=original_drop(private,capacity);after=totals(private)
  if context['actor']==0:
   lost={k:v-after[k] for k,v in before.items() if v>after[k]}
   if lost:records.append({'seed':seed,'day':context['day'],'discarded':lost,'quotes':{k:context['quotes'].get(k) for k in lost},'quote_marked_value':sum(q*context['quotes'].get(k,0) for k,q in lost.items())})
  context['actor']+=1
  return result
 module._end_of_day=day_hook;module._drop_inventories_to_shed=drop_hook
 try:
  mine,_=load_policy('agents/v43/main.py','mine'+str(seed));foe,_=load_policy('work/recovered/56237315/main.py','foe'+str(seed))
  env.run([mine,foe]);games.append({'seed':seed,'rewards':[s.reward for s in env.steps[-1]],'status':[s.status for s in env.steps[-1]]})
 finally:module._end_of_day=original_day;module._drop_inventories_to_shed=original_drop
counts=collections.Counter()
for r in records:counts.update(r['discarded'])
result={'games':games,'actual_discarded':dict(counts),'units':sum(counts.values()),'quote_marked_value':sum(r['quote_marked_value'] for r in records),'events':records,'valuation_caveat':'Displayed prices at overnight drop are descriptive only, not recoverable profit. Fertilizer cannot be sold, and counterfactual sale timing changes prices.'}
(OUT/'actual-overflow.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
