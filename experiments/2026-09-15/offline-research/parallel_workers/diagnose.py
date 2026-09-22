import sys,json,copy,collections,contextlib,io
from pathlib import Path
BASE=Path(r'H:\Kaggriculture'); OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'tools'))
from benchmark_agents import load_policy
with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
 from kaggle_environments import make
stats=collections.Counter(); opportunities=[]; terminal=[]
def game(seed):
 policy,ns=load_policy('agents/v43/main.py','diag'+str(seed))
 foe,_=load_policy('work/recovered/56237315/main.py','foe'+str(seed))
 def wrapped(obs,config):
  a=policy(obs,config);f,p=ns['_PLANNER_NS']['_clone_state'](obs['farms'][obs['player']],obs['private'])
  cs=[a.get('farmer') or ['PASS'],*(a.get('hands') or [])]
  demand=collections.Counter(c[1] for c in cs if len(c)>1 and c[0]=='PLANT')
  blocked={crop for crop,n in demand.items() if n>p['seeds'].get(crop,0)}
  for i in range(len(p['inventories'])):
   c=cs[i] if i<len(cs) else ['PASS'];stats['op_'+c[0]]+=1
   before=copy.deepcopy((f,p))
   if not(c[0]=='PLANT' and c[1] in blocked):
    ns['_PLANNER_NS']['_apply_unit_action'](f,p,i,c,10,int(obs['step'])//24,24,100)
   if (f,p)==before:
    stats['noop_'+c[0]]+=1
    x,y=f['farmer'] if i==0 else f['hands'][i-1];tile=f['tiles'][y][x]
    possible=[]
    if isinstance(tile,dict):
     if tile.get('kind')=='PLANT' and not tile.get('watered_today'):possible.append('WATER')
     if tile.get('animal') and not tile.get('cared_today'):possible.append('CARE')
     if tile.get('animal') and not tile.get('fed_today') and p['inventories'][i].get('WHEAT',0):possible.append('FEED')
    for op in possible:
     stats['opportunity_'+op]+=1
     opportunities.append({'seed':seed,'step':obs['step'],'actor':i,'command':c,'possible':op,'tile':copy.deepcopy(tile)})
  if obs['hour']==23:
   stock,buys,sales=ns['_r97_market_stock'](p['shed'],a.get('market') or [])
   delivered,lost=ns['_r97_delivery'](stock,p,True)
   for product,q in lost.items():stats['projected_overflow_'+product]+=q
   stats['endangered_plants']+=sum(isinstance(t,dict) and t.get('kind')=='PLANT' and not t.get('watered_today') and t.get('consecutive_unwatered',0)>=1 for row in f['tiles'] for t in row)
   stats['endangered_animals']+=sum(isinstance(t,dict) and bool(t.get('animal')) and not t.get('fed_today') and t.get('consecutive_unfed',0)>=1 for row in f['tiles'] for t in row)
   stats['unwatered_day_tiles']+=sum(isinstance(t,dict) and t.get('kind')=='PLANT' and not t.get('watered_today') for row in f['tiles'] for t in row)
   stats['unfed_day_animals']+=sum(isinstance(t,dict) and bool(t.get('animal')) and not t.get('fed_today') for row in f['tiles'] for t in row)
  if obs['step']>=718:terminal.append({'seed':seed,'farm':f,'private':p})
  return a
 env=make('kaggriculture',configuration={'seed':seed,'episodeSteps':720},debug=True)
 env.run([wrapped,foe]);return {'seed':seed,'rewards':[s.reward for s in env.steps[-1]],'status':[s.status for s in env.steps[-1]],'final_private':env.steps[-1][0].observation.private}
results=[game(s) for s in (301,302,303)]
(OUT/'diagnostics.json').write_text(json.dumps({'games':results,'counts':stats,'opportunities':opportunities,'terminal':terminal},indent=2))
print(json.dumps({'games':results,'counts':stats}))

