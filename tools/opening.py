"""Kill-switch probe for the opening: does a config actually OWN animals early?

Every previous attempt at early livestock failed silently -- `animal_reserve_frac
0.0` removed the gate entirely and still produced zero animals at day 8, because
a different gate was binding. So measure the MECHANISM before measuring money:
if the herd is not on the board by day 4, nothing downstream is worth reading.

Reference (from 38 real ladder losses): winners hold ~3.4 animals at day 8 and
sit on ~1.3 quadrants at day 4. We held 0 and 4.0.

  python tools/opening.py -n 3
"""

import argparse
import contextlib
import io
import multiprocessing as mp
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ENV = {}

PROBE_DAYS = (2, 4, 8, 12, 16, 22)

# The herd and the land compete for the same $3,000. Holding land back for the
# full 3c1s herd costs 25 tiles for eight days, which our 84-tile labour ceiling
# cannot absorb. So separate the two questions: how BIG an opening pays, and
# whether it has to displace the land at all.
CONFIGS = {
    "v13 (HEAD)":   {},
    "1 cow":        {"open_cows": 1, "open_land_hold": False},
    "2 cow":        {"open_cows": 2, "open_land_hold": False},
    "3c1s +land":   {"open_cows": 3, "open_sheep": 1, "open_land_hold": False},
    "3c1s -land":   {"open_cows": 3, "open_sheep": 1},
    "3c1s -land fd": {"open_cows": 3, "open_sheep": 1, "feed_buy_days": 5.0,
                      "feed_by_purchase": True},
}


def _boot():
    if "make" not in _ENV:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            from kaggle_environments import make
        _ENV["make"] = make
    return _ENV["make"]


def _episode(job):
    name, ov, seed = job
    make = _boot()
    from kagri.agent import act
    from kagri.farm import View

    log = {}

    def mine(obs):
        a = act(obs, ov)
        v = View(obs)
        if v.hour == 23 and v.day in PROBE_DAYS:
            # Market inventory is the cleanest proxy for what we have SOLD:
            # against `starter` the opponent supplies almost nothing, so the
            # inventory above I0 is essentially our own output.
            log[v.day] = (v.count_animals(), len(v.unlocked), int(v.money),
                          v.count_plants("STRAWBERRY"),
                          v.minv.get("FERTILIZER", 0), v.minv.get("MILK", 0))
        return a

    with contextlib.redirect_stderr(io.StringIO()):
        env = make("kaggriculture",
                   configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([mine, "starter"])
    r = [float(s.reward or 0) for s in env.steps[-1]]
    return name, log, r[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--seeds", type=int, default=3)
    ap.add_argument("-j", "--jobs", type=int, default=max(1, mp.cpu_count() - 2))
    args = ap.parse_args()

    jobs = [(n, ov, s) for n, ov in CONFIGS.items()
            for s in range(1, args.seeds + 1)]
    with mp.Pool(args.jobs) as pool:
        results = pool.map(_episode, jobs, chunksize=1)

    per = {}
    for name, log, money in results:
        per.setdefault(name, []).append((log, money))

    for name in CONFIGS:
        runs = per[name]
        print(f"\n{name}   final ${statistics.mean(m for _, m in runs):,.0f} "
              f"(min ${min(m for _, m in runs):,.0f})")
        print(f"  {'day':>4}{'animals':>9}{'quads':>7}{'money':>9}"
              f"{'straw':>7}{'fert.mkt':>10}{'milk.mkt':>10}")
        for d in PROBE_DAYS:
            rows = [log[d] for log, _ in runs if d in log]
            if not rows:
                continue
            cols = [statistics.mean(c) for c in zip(*rows)]
            print(f"  {d:>4}{cols[0]:>9.1f}{cols[1]:>7.1f}{cols[2]:>9,.0f}"
                  f"{cols[3]:>7.1f}{cols[4]:>10,.0f}{cols[5]:>10,.0f}")


if __name__ == "__main__":
    mp.freeze_support()
    main()
