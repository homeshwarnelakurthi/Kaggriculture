import sys,contextlib,io,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];W=Path(__file__).parent
sys.path.insert(0,r'H:\Kaggriculture\work\runtime1327')
with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
    from kaggle_environments import make
    results=[]
    for seat in [0,1]:
        env=make('kaggriculture',configuration={'seed':1241,'episodeSteps':720},debug=True)
        players=[str(W/'candidate.py'),'starter']
        if seat:players.reverse()
        env.run(players)
        assert len(env.steps)==720 and all(s.status=='DONE' for s in env.steps[-1])
        results.append(dict(seat=seat,steps=len(env.steps),status=[s.status for s in env.steps[-1]],rewards=[s.reward for s in env.steps[-1]]))
(W/'loader.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results))
