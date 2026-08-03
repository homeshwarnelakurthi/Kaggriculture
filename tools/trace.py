"""Day-by-day trace of our own agent, to find where the engine stalls."""

import contextlib
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    from kaggle_environments import make

from kagri.agent import act
from kagri.farm import View

LOG = {}


def my_agent(obs):
    a = act(obs)
    v = View(obs)
    if v.hour == 23:
        counts = {}
        for row in v.tiles:
            for t in row:
                if isinstance(t, dict):
                    k = t.get("animal") or (t["crop"] if t.get("kind") == "PLANT" else t.get("kind"))
                    counts[k] = counts.get(k, 0) + 1
        LOG[v.day] = dict(
            money=int(v.money), hands=v.n_units - 1, hires=v.hires_today,
            quad=len(v.unlocked), tiles=counts,
            shed={k: n for k, n in v.shed.items() if n},
            seeds={k: n for k, n in v.seeds.items() if n},
        )
    return a


env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42}, debug=True)
env.run([my_agent, "starter"])

for day in sorted(LOG):
    d = LOG[day]
    if day % 2 and day not in (1, 3, 5):
        continue
    print(f"d{day:2d} ${d['money']:7d} hands={d['hands']:2d}(hired {d['hires']:2d}) "
          f"quads={d['quad']} {d['tiles']}")
    print(f"        shed={d['shed']} seeds={d['seeds']}")
print("\nfinal:", [s.reward for s in env.steps[-1]])
