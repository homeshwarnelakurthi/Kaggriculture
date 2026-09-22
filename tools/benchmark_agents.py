"""Seat-balanced whole-game evaluation, isolated agent namespaces and JSONL logs."""
import argparse, contextlib, importlib.util, io, itertools, json, multiprocessing as mp
from pathlib import Path
import statistics, sys, time, traceback
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'work/runtime1327'))
sys.path.insert(0,str(ROOT))
MAKE=None

def load_policy(path, tag):
    path=ROOT/path
    if path.is_dir():
        pkg=path/'kagri'
        spec=importlib.util.spec_from_file_location(tag,pkg/'__init__.py',submodule_search_locations=[str(pkg)])
        module=importlib.util.module_from_spec(spec)
        sys.modules[tag]=module
        spec.loader.exec_module(module)
        act=importlib.import_module(tag+'.agent').act
        def policy(obs,config):return act(obs)
        return policy, None
    ns={'__name__':tag,'__file__':str(path)}
    exec(compile(path.read_text(encoding='utf-8'),str(path),'exec'),ns)
    return ns['agent'], ns

def episode(job):
    name,path,oname,opath,seed,seat,trace=job
    global MAKE
    if MAKE is None:
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            from kaggle_environments import make
        MAKE=make
    record=dict(candidate=name,opponent=oname,seed=seed,seat=seat)
    logs=io.StringIO();clock=time.perf_counter();timing=[];daily={};changes={}
    try:
        mine,ns=load_policy(path,'agent_a_'+str(seed)+'_'+str(seat))
        foe,foens=load_policy(opath,'agent_b_'+str(seed)+'_'+str(seat)) if opath!='starter' else ('starter',None)
        def measured(obs,config):
            before=time.perf_counter();a=mine(obs,config);timing.append(time.perf_counter()-before)
            if obs['hour']==23:
                f=obs['farms'][obs['player']]
                counts={}
                for row in f['tiles']:
                    for t in row:
                        if isinstance(t,dict):
                            k=t.get('animal') or t.get('crop') or t['kind'];counts[k]=counts.get(k,0)+1
                daily[str(obs['day'])]={'money':f['money'],'hands':len(f['hands']),'tiles':counts}
            return a
        with contextlib.redirect_stdout(logs),contextlib.redirect_stderr(logs):
            env=MAKE('kaggriculture',configuration={'episodeSteps':720,'seed':seed},debug=True)
            env.run([measured,foe] if seat==0 else [foe,measured])
        final=env.steps[-1];status=[x.status for x in final];rewards=[x.reward for x in final]
        valid=len(env.steps)==720 and len(timing)==719 and status==['DONE','DONE']
        record.update(valid=valid,steps=len(env.steps),status=status,mine=rewards[seat],theirs=rewards[1-seat],
                      win=(float(rewards[seat]>rewards[1-seat])+0.5*float(rewards[seat]==rewards[1-seat])) if valid else None,
                      max_turn_ms=round(1000*max(timing,default=0),3),days=daily,
                      shops=list(final[0].observation['town']['unlocked_shops']),
                      telemetry=dict(getattr(mine,'telemetry',{})))
        if trace:
            dest=ROOT/'work'/f'trace-{name}-{oname}-{seed}-{seat}.json'
            dest.write_text(json.dumps(env.toJSON()))
    except Exception:
        record.update(valid=False,error=traceback.format_exc())
    if logs.getvalue().strip():record['log']=logs.getvalue()[-2000:]
    record['seconds']=round(time.perf_counter()-clock,2)
    return record

def report(results):
    for name in dict.fromkeys(r['candidate'] for r in results):
        rows=[r for r in results if r['candidate']==name];rates={}
        for opp in dict.fromkeys(r['opponent'] for r in rows):
            cell=[r for r in rows if r['opponent']==opp and r['valid']]
            rates[opp]=round(100*statistics.mean(r['win'] for r in cell),1) if cell else None
        valid=[r for r in rows if r['valid']]
        print(json.dumps(dict(candidate=name,episodes=len(rows),invalid=len(rows)-len(valid),rates=rates,
              worst=min((v for v in rates.values() if v is not None),default=None),
              mean_margin=round(statistics.mean(r['mine']-r['theirs'] for r in valid)) if valid else None,
              max_turn_ms=max((r['max_turn_ms'] for r in valid),default=0))),flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',required=True);ap.add_argument('--seeds',type=int,default=2)
    ap.add_argument('--seed-start',type=int,default=1);ap.add_argument('-j',type=int,default=4)
    ap.add_argument('--output',required=True);ap.add_argument('--trace',action='store_true');args=ap.parse_args()
    config=json.loads((ROOT/args.config).read_text())
    jobs=[(n,p,o,q,s,seat,args.trace) for (n,p),(o,q),s,seat in itertools.product(config['candidates'].items(),config['opponents'].items(),range(args.seed_start,args.seed_start+args.seeds),(0,1))]
    results=[];start=time.time();out=ROOT/args.output;out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',encoding='utf-8') as fp,mp.Pool(args.j,maxtasksperchild=8) as pool:
        for r in pool.imap_unordered(episode,jobs,chunksize=1):
            results.append(r);fp.write(json.dumps(r)+'\n');fp.flush()
            print(f"{len(results)}/{len(jobs)} {r['candidate']} vs {r['opponent']} seed={r['seed']} seat={r['seat']} valid={r['valid']} {r.get('mine')}/{r.get('theirs')} {r['seconds']}s",flush=True)
            if not r['valid']:print(r.get('error',r.get('log',r.get('status'))),flush=True)
    report(results);print(f'Total {time.time()-start:.1f}s',flush=True)
if __name__=='__main__':
    mp.freeze_support();main()
