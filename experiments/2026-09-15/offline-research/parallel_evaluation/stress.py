"""Validate sale optimization against the official market and Kaggle exec loading."""
import contextlib, copy, io, itertools, json, random, sys
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(r'H:\Kaggriculture')
sys.path.insert(0,str(ROOT/'work/runtime1327'))
with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
    from kaggle_environments import make
    from kaggle_environments.envs.kaggriculture import kaggriculture as engine

source=(ROOT/'agents/v43/main.py').read_text()
ns={'__name__':'submission_exec_without_file'}
exec(compile(source,'submission_main','exec'),ns)
assert callable(ns['agent']) and '__file__' not in ns
rng=random.Random(391177)
ns['_HOMII_STATS'].update(queue_reorders=0,modeled_margin_gain=0,queue_errors=0)

def settle(obs,own,rival):
    farms=copy.deepcopy(obs['farms']);market=copy.deepcopy(obs['market'])
    for f in farms:f['money']=0
    states=[SimpleNamespace(action={'market':o},observation=SimpleNamespace(farms=farms,market=market,private=copy.deepcopy(obs['private']))) for o in (own,rival)]
    engine._process_market(states,SimpleNamespace(configuration={'maxMarketOrdersPerTurn':10}))
    return farms[0]['money']-farms[1]['money']


def settle_asymmetric(obs,own,rival,stock):
    farms=copy.deepcopy(obs['farms']);market=copy.deepcopy(obs['market'])
    for f in farms:f['money']=0
    states=[SimpleNamespace(action={'market':o},observation=SimpleNamespace(farms=farms,market=market,private=copy.deepcopy(obs['private']))) for o in (own,rival)]
    states[1].observation.private['shed']=dict(stock)
    engine._process_market(states,SimpleNamespace(configuration={'maxMarketOrdersPerTurn':10}))
    return farms[0]['money']-farms[1]['money']
base=make('kaggriculture',configuration={'seed':1})
base=copy.deepcopy(dict(base.state[0].observation));base.update(step=400,day=16,hour=16,player=0)
for f in base['farms']:
    for x,y in [(x,y) for y in range(2) for x in range(4)]:f['tiles'][y][x]=engine._new_plant('WHEAT',15,24)
results=[]
for trial in range(500):
    obs=copy.deepcopy(base)
    items=rng.sample(['WHEAT','CARROT','TOMATO','STRAWBERRY','MELON','EGG','MILK','WOOL'],4)
    stock={i:rng.randrange(1,26) for i in items};obs['private']['shed']=dict(stock)
    for item in engine.PRODUCTS:obs['market']['inventory'][item]=rng.randrange(9500,10400)
    engine._refresh_prices(obs['market'])
    orders=[['SELL',i,stock[i]] for i in items]
    action={'farmer':['PASS'],'hands':[],'market':copy.deepcopy(orders)}
    result=ns['_homii_sale_assignment'](obs,action)
    if result['market']==orders:continue
    rival_stock={i:rng.randrange(0,41) for i in items}
    shuffled=copy.deepcopy(orders);rng.shuffle(shuffled)
    for mode,rival,rs in [('same_order_hidden_stock',orders,rival_stock),('different_order_hidden_stock',shuffled,rival_stock)]:
        old=settle_asymmetric(obs,orders,rival,rs);new=settle_asymmetric(obs,result['market'],rival,rs)
        row=dict(trial=trial,mode=mode,gain=new-old)
        if new<old:row.update(own_stock=stock,rival_stock=rs,market_inventory=obs['market']['inventory'],original=orders,optimized=result['market'],rival=rival)
        results.append(row)
summary={}
for mode in ['same_order_hidden_stock','different_order_hidden_stock']:
    r=[x for x in results if x['mode']==mode]
    summary[mode]=dict(cases=len(r),losses=sum(x['gain']<0 for x in r),minimum_gain=min(x['gain'] for x in r),mean_gain=sum(x['gain'] for x in r)/len(r),example=next((x for x in r if x['gain']<0),None))
Path(__file__).with_name('stress-results.json').write_text(json.dumps(dict(summary=summary,results=results),indent=2))
print(json.dumps(summary),flush=True)
