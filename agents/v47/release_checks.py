import sys,json,copy,contextlib,io
from pathlib import Path
sys.path.insert(0,r'H:\Kaggriculture\tools')
from benchmark_agents import load_policy
R=Path.cwd()
with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
 from kaggle_environments import make
 from kaggle_environments.envs.kaggriculture import kaggriculture as eng
act,n=load_policy(R/'outputs/v47/main.py','unit47')
env=make('kaggriculture',configuration={'seed':851,'episodeSteps':720})
obs=copy.deepcopy(dict(env.state[0].observation));act(obs,env.configuration)
obs.update(step=383,day=15,hour=23,player=0)
obs['farms'][0]['farmer']=[2,3];obs['farms'][0]['hands']=[]
obs['farms'][0]['tiles'][3][2]={'kind':'COOP','animal':'GOOSE','placed_day':0,'yield_units':4,'fed_today':True,'cared_today':True,'consecutive_unfed':0,'pending_care_bonus':1,'fertilizer_available':True}
obs['private']['inventories']=[{}];obs['private']['shed']={'WHEAT':20,'FERTILIZER':10}
obs['market']['prices'].update(EGG=50,FERTILIZER=20)
n['_V47_PRODUCTION_PARENT']=lambda o,a:a
n['_flow_reserve']=lambda o,item:10
base={'farmer':['COLLECT_FERTILIZER'],'hands':[],'market':[]}
before=copy.deepcopy(obs);old=copy.deepcopy(base)
a=n['_flow_production'](obs,base)
assert a['farmer']==['HARVEST'];assert obs==before and base==old
farm,private=n['_r127_fields'](obs,a)
eng._daily_refresh_animals(farm,15);eng._drop_inventories_to_shed(private,100)
assert farm['tiles'][3][2]['yield_units']==2 and private['shed']['EGG']==4
checks=['exact_engine_cap_recovery','action_and_observation_immutable']
# Do not trade away the last required fertilizer unit.
n['_flow_reserve']=lambda o,item:11 if item=='FERTILIZER' else 10
assert n['_flow_production'](obs,base)==base
checks.append('fertilizer_reserve_protected');n['_flow_reserve']=lambda o,item:10
full=copy.deepcopy(obs);full['private']['shed']={'WHEAT':90,'FERTILIZER':10}
assert n['_flow_production'](full,base)==base;checks.append('overflow_rejected')
for command in ['FEED','WATER','PLANT']:
 x=dict(base,farmer=[command]);assert n['_flow_production'](obs,x)==x
checks.append('essential_work_preserved')
low=copy.deepcopy(obs);low['farms'][0]['tiles'][3][2]['yield_units']=1
assert n['_flow_production'](low,base)==base;checks.append('uncapped_production_untouched')
costly=copy.deepcopy(obs);costly['market']['prices']['FERTILIZER']=200
assert n['_flow_production'](costly,base)==base;checks.append('fertilizer_value_guard')
escape=copy.deepcopy(obs);escape['farms'][0]['tiles'][3][2].update(fed_today=False,consecutive_unfed=1)
assert n['_flow_production'](escape,base)==base;checks.append('escape_not_counted_as_production')
print(json.dumps({'unit_checks':checks}),flush=True)
n['_FLOW_STATE'][0].update(similarity=1.0,synchronized=False)
assert n['_flow_production'](obs,base)==base
n['_FLOW_STATE'][0]['synchronized']=True
assert n['_flow_production'](obs,base)['farmer']==['HARVEST']
print(json.dumps({'uncertain_mirror_guard':True}),flush=True)
# Only tracked, recent self-caused egg differences may preserve timing confidence.
n['_V46_FORECAST_PARENT']=lambda o,c:{}
f=copy.deepcopy(obs);f['farms'][1]=copy.deepcopy(f['farms'][0])
n['_V46_SYNC'].clear();n['_V47_CAP_EFFECTS'].clear()
for step in range(24):
 f['step']=step;model=n['_flow_forecast'](f,{})
assert model['synchronized']
n['_V47_CAP_EFFECTS'][0][(2,3)]=25
f['farms'][0]['tiles'][3][2]['yield_units']=2
f['step']=24;frozen=copy.deepcopy(f)
assert n['_flow_forecast'](f,{})['synchronized'];assert f==frozen
f['step']=25;assert n['_flow_forecast'](f,{})['synchronized']
f['step']=26;assert not n['_flow_forecast'](f,{})['synchronized']
# Feeding differences are never explained away by our harvest.
n['_V46_SYNC'].clear();n['_V47_CAP_EFFECTS'].clear()
f['farms'][0]=copy.deepcopy(f['farms'][1])
for step in range(24):
 f['step']=step;n['_flow_forecast'](f,{})
n['_V47_CAP_EFFECTS'][0][(2,3)]=95
f['farms'][0]['tiles'][3][2].update(yield_units=2,fed_today=False)
f['step']=24;assert not n['_flow_forecast'](f,{})['synchronized']
print(json.dumps({'self_harvest_tracking':True,'tracking_expiry':True,'real_feed_divergence_preserved':True,'observation_immutable':True}),flush=True)
for seat in (0,1):
 env=make('kaggriculture',configuration={'seed':853,'episodeSteps':720},debug=True);agents=[str(R/'outputs/v47/main.py'),'starter']
 if seat:agents.reverse()
 env.run(agents)
 assert len(env.steps)==720 and all(s.status=='DONE' for s in env.steps[-1])
 print(json.dumps({'file_loader':True,'seed':853,'seat':seat,'rewards':[s.reward for s in env.steps[-1]]}),flush=True)
