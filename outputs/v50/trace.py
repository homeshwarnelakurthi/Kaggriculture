import sys,json,copy,contextlib,io,importlib,multiprocessing as mp,collections
from pathlib import Path
R=Path(__file__).resolve().parents[2];W=Path(__file__).parent
sys.path.insert(0,r'H:\Kaggriculture\tools')
import benchmark_agents as b
def run(job):
    name,eid=job;p=json.loads((R/f'outputs/v47-audit/{eid}.json').read_text());seat=p['info']['TeamNames'].index('Homii_N')
    with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
        from kaggle_environments import make
        e=importlib.import_module('kaggle_environments.envs.kaggriculture.kaggriculture')
        unit,drop,market,commit=e._apply_unit_action,e._drop_inventories_to_shed,e._process_market,e._commit_unit
        ctx={'step':0,'seat':-1};events=[];totals=[collections.Counter(),collections.Counter()]
        def amounts(p):return {i:p['shed'].get(i,0)+sum(v.get(i,0) for v in p['inventories']) for i in e.PRODUCTS}
        def apply(f,p,idx,a,*args):
            if idx==0:ctx['seat']+=1
            s=ctx['seat'];before=amounts(p);pos=e._farmer_position(f,idx);xy=list(pos) if pos is not None else None
            ans=unit(f,p,idx,a,*args);after=amounts(p)
            for item in e.PRODUCTS:
                d=after[item]-before[item]
                if d and a and a[0] in ('HARVEST','DROP','PLACE'):
                    kind='harvest' if a[0]=='HARVEST' else 'field_loss'
                    if kind=='field_loss' and d>=0:continue
                    events.append(dict(step=ctx['step'],seat=s,kind=kind,item=item,units=d,actor=idx,xy=xy,shed=dict(p['shed'])))
                    totals[s][kind+' '+item]+=d
            return ans
        def mk(state,env):
            ctx['farms']=state[0].observation.farms;ctx['privates']=[s.observation.private for s in state]
            ans=market(state,env);ctx['seat']=-1;ctx['step']+=1;return ans
        def dp(p,cap):
            s=next(i for i,v in enumerate(ctx['privates']) if p is v);before=amounts(p);stock=dict(p['shed']);inv=copy.deepcopy(p['inventories'])
            ans=drop(p,cap);after=amounts(p)
            for item in e.PRODUCTS:
                loss=before[item]-after[item]
                if loss:
                    events.append(dict(step=ctx['step']-1,seat=s,kind='overnight_loss',item=item,units=loss,shed=stock,inventories=inv))
                    totals[s]['overnight_loss '+item]+=loss
            return ans
        def cm(op,item,price,f,p,m,*args):
            ans=commit(op,item,price,f,p,m,*args)
            if ans:
                s=next(i for i,v in enumerate(ctx['farms']) if f is v)
                totals[s][op+' units '+item]+=1;totals[s][op+' coins '+item]+=price
            return ans
        e._apply_unit_action,e._drop_inventories_to_shed,e._process_market,e._commit_unit=apply,dp,mk,cm
        path=R/f'outputs/{name}/main.py'
        if name=='v50':path=W/'candidate.py'
        act,ns=b.load_policy(path,name)
        def tape(o,c):return copy.deepcopy(p['steps'][o['step']+1][1-seat]['action'])
        env=make('kaggriculture',configuration=dict(p['configuration'],seed=p['info']['seed']),debug=True)
        env.run([act,tape] if seat==0 else [tape,act])
    rewards=[s.reward for s in env.steps[-1]]
    out=dict(name=name,episode=eid,seat=seat,margin=rewards[seat]-rewards[1-seat],steps=len(env.steps),status=[s.status for s in env.steps[-1]],totals=[dict(t) for t in totals],events=events,telemetry=act.telemetry)
    (W/f'{name}-{eid}.json').write_text(json.dumps(out))
    return {k:v for k,v in out.items() if k not in ('events','telemetry')}
if __name__=='__main__':
    names=sys.argv[1:] or ['v47','v48']
    with mp.Pool(3,maxtasksperchild=1) as pool:
        for r in pool.imap_unordered(run,[(n,e) for n in names for e in (110991298,110986214,110984757)]):print(json.dumps(r),flush=True)
