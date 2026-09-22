import sys,contextlib,io,json,copy
from pathlib import Path
R=Path.cwd();sys.path.insert(0,r'H:\Kaggriculture\work\runtime1327')
with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
 from kaggle_environments import make
 from kaggle_environments.envs.kaggriculture import kaggriculture as eng
n={'__name__':'unit'};exec((R/'work/v43-storage/main.py').read_text(),n)
env=make('kaggriculture',configuration={'seed':601,'episodeSteps':720});obs=copy.deepcopy(dict(env.state[0].observation));n['agent'](obs,env.configuration)
obs.update(step=503,day=20,hour=23,player=0)
obs['farms'][0]['hands']=[[4,4]];obs['private']['inventories']=[{'EGG':50},{'WHEAT':30}]
obs['private']['shed']={i:0 for i in eng.PRODUCTS};obs['private']['shed']['WHEAT']=40
n['_flow_forecast'](obs,env.configuration)
n['_flow_reserve']=lambda obs,item:50 if item=='WHEAT' else 0
act={'farmer':['PASS'],'hands':[['PASS']],'market':[]};before=copy.deepcopy(act)
result=n['_flow_allocate'](obs,act)
assert act==before
assert ['SELL','WHEAT',20] in result['market'],result
# Execute exact engine market and overnight drop to verify reserve and recovery.
from types import SimpleNamespace
farms=copy.deepcopy(obs['farms']);market=copy.deepcopy(obs['market']);private=copy.deepcopy(obs['private'])
st=[SimpleNamespace(action=result,observation=SimpleNamespace(farms=farms,market=market,private=private)),SimpleNamespace(action={'market':[]},observation=SimpleNamespace(farms=farms,market=market,private={'shed':{},'inventories':[{}],'seeds':{}}))]
eng._process_market(st,SimpleNamespace(configuration={'maxMarketOrdersPerTurn':10}))
eng._drop_inventories_to_shed(private,100)
assert private['shed']['WHEAT']==50 and private['shed']['EGG']==50,private
# A higher feed reservation must preserve baseline wheat even if overflow cannot be removed.
n['_flow_reserve']=lambda obs,item:60 if item=='WHEAT' else 0
obs['private']['inventories']=[{'WHEAT':30},{'EGG':50}]
result2=n['_flow_allocate'](obs,before)
assert ['SELL','WHEAT',10] in result2['market'],result2
# Fertilizer is marketable, but reserved quantities remain protected.
obs['private']['shed']={'FERTILIZER':40};obs['private']['inventories']=[{'EGG':80},{}]
n['_flow_reserve']=lambda obs,item:10 if item=='FERTILIZER' else 0
result3=n['_flow_allocate'](obs,before)
assert ['SELL','FERTILIZER',20] in result3['market'],result3

print("Passed immutable-action, official market/deposit, feed reservation, and fertilizer surplus checks.")
