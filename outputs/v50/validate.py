import json,sys,multiprocessing as mp
from pathlib import Path
R=Path(__file__).resolve().parents[2];W=Path(__file__).parent
sys.path.insert(0,r'H:\Kaggriculture\tools')
import benchmark_agents as b
if __name__=='__main__':
    jobs=[]
    refs={'v43':R/'outputs/main.py','v47':R/'outputs/v47/main.py','v48':R/'outputs/v48/main.py','wide':R/'work/v46/wide.py'}
    for seed in [1221,1222,1223]:
        for seat in [0,1]:
            for opp,path in refs.items():jobs.append(('v50',W/'candidate.py',opp,path,seed,seat,False))
            jobs.append(('v48',refs['v48'],'wide',refs['wide'],seed,seat,False))
    with (W/'fresh.jsonl').open('w') as f,mp.Pool(3) as pool:
        for r in pool.imap_unordered(b.episode,jobs):
            f.write(json.dumps(r)+'\n');f.flush()
            print(r['candidate'],r['opponent'],r['seed'],r['seat'],r['valid'],r.get('mine',0)-r.get('theirs',0),flush=True)
