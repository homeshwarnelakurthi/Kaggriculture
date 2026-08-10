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
# FEED PRICING. The engine adds base production on schedule regardless of
# fed_today and sets fertilizer_available daily regardless, and the escape rule
# tolerates exactly ONE missed day. So routine feeding buys the CARE bonus plus
# insurance -- not a day of production. We have been paying 1 wheat + 1 action
# per animal per day for it. `escaped` is the kill switch: if animals start
# vanishing, the saving is fake.
CONFIGS = {
    "v14 (HEAD)":   {},
    "feed x0.5":    {"feed_routine_mult": 0.5},
    "feed x0.15":   {"feed_routine_mult": 0.15},
    "feed x0.15 +herd": {"feed_routine_mult": 0.15, "feed_per_animal_day": 0.6,
                         "wheat_buffer_per_animal": 1.2},
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
    # Escapes are the kill switch. An animal that starves vanishes and the
    # structure stays, so a herd that merely stops growing looks identical to a
    # herd that is being eaten -- count the drops explicitly.
    state = {"peak": 0, "escaped": 0, "prev": 0, "fed_actions": 0}

    def mine(obs):
        a = act(obs, ov)
        v = View(obs)
        now = v.count_animals()
        held = sum(v.shed.get(k, 0) + v.carried(k) for k in ("COW", "SHEEP", "GOOSE"))
        if v.hour == 0 and now < state["prev"]:
            state["escaped"] += state["prev"] - now
        if v.hour == 0:
            state["prev"] = now
        state["peak"] = max(state["peak"], now + held)
        state["fed_actions"] += sum(
            1 for act_list in [a["farmer"]] + list(a["hands"])
            if act_list and act_list[0] == "FEED")
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
    return name, log, r[0], state


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
    for name, log, money, state in results:
        per.setdefault(name, []).append((log, money, state))

    for name in CONFIGS:
        runs = per[name]
        print(f"\n{name}   final ${statistics.mean(m for _, m, _ in runs):,.0f} "
              f"(min ${min(m for _, m, _ in runs):,.0f})   "
              f"ESCAPED {statistics.mean(s['escaped'] for _, _, s in runs):.1f}  "
              f"peak herd {statistics.mean(s['peak'] for _, _, s in runs):.1f}  "
              f"feed actions {statistics.mean(s['fed_actions'] for _, _, s in runs):.0f}")
        print(f"  {'day':>4}{'animals':>9}{'quads':>7}{'money':>9}"
              f"{'straw':>7}{'fert.mkt':>10}{'milk.mkt':>10}")
        for d in PROBE_DAYS:
            rows = [log[d] for log, _, _ in runs if d in log]
            if not rows:
                continue
            cols = [statistics.mean(c) for c in zip(*rows)]
            print(f"  {d:>4}{cols[0]:>9.1f}{cols[1]:>7.1f}{cols[2]:>9,.0f}"
                  f"{cols[3]:>7.1f}{cols[4]:>10,.0f}{cols[5]:>10,.0f}")


if __name__ == "__main__":
    mp.freeze_support()
    main()
