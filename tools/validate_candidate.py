"""Validate sale optimization against the official market and Kaggle exec loading."""
import contextlib, copy, io, itertools, json, random, sys
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
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

count=0
for trial in range(24):
    env=make('kaggriculture',configuration={'seed':trial})
    obs=copy.deepcopy(dict(env.state[0].observation));obs['step']=400;obs['day']=16;obs['hour']=16;obs['player']=0
    for f in obs['farms']:
        for x,y in [(x,y) for y in range(2) for x in range(4)]:f['tiles'][y][x]=engine._new_plant('WHEAT',15,24)
    items=rng.sample(engine.PRODUCTS,4)
    stock={i:rng.randrange(0,26) for i in items}
    obs['private']['shed']=dict(stock)
    for item in engine.PRODUCTS:obs['market']['inventory'][item]=rng.randrange(9700,10400)
    engine._refresh_prices(obs['market'])
    orders=[['SELL',i,rng.randrange(1,41)] for i in items]
    action={'farmer':['PASS'],'hands':[],'market':copy.deepcopy(orders)}
    before=copy.deepcopy(action)
    result=ns['_homii_sale_assignment'](obs,action)
    assert action==before
    assert sorted(result['market'])==sorted(orders)
    assert result['farmer']==action['farmer'] and result['hands']==action['hands']
    gain=settle(obs,result['market'],orders)
    optimum=max(settle(obs,list(p),orders) for p in itertools.permutations(orders))
    assert gain>=0,(trial,gain)
    assert gain==optimum or optimum<25,(trial,gain,optimum)
    mixed=copy.deepcopy(action);mixed['market'].append(['HIRE'])
    assert ns['_homii_sale_assignment'](obs,mixed)==mixed
    duplicate=copy.deepcopy(action);duplicate['market'].append(list(orders[0]))
    assert ns['_homii_sale_assignment'](obs,duplicate)==duplicate
    count+=1
print(json.dumps({'exec_without_file':True,'official_market_optimality_cases':count,'status':'passed'}),flush=True)
# Exercise the actual Kaggle file loader, not our custom benchmark loader.
for seat in (0,1):
    env=make('kaggriculture',configuration={'seed':701,'episodeSteps':720},debug=True)
    line=[str(ROOT/'agents/v43/main.py'),'starter']
    if seat:line.reverse()
    env.run(line)
    assert len(env.steps)==720 and [s.status for s in env.steps[-1]]==['DONE','DONE']
    print(json.dumps({'loader_game_seat':seat,'steps':len(env.steps),'status':[s.status for s in env.steps[-1]],'rewards':[s.reward for s in env.steps[-1]]}),flush=True)
