"""Evaluate configs against a DIVERSE opponent pool, not just a mirror.

Why this exists: in a mirror match melon is zero-sum (fixed ~$26.5k pot, no
shop demand, barely regenerates) while eggs are positive-sum (log price curve,
effectively unbounded). So mirror self-play structurally rewards contesting
melon, and tuning against it alone will happily overfit us into a melon-rush
build that is only correct against another melon rusher.

The real ladder is a mixed field. This plays each candidate against several
distinct archetypes and reports the per-opponent breakdown, so a config that
wins overall by crushing one archetype while losing to another is visible
rather than hidden inside an average.

  python tools/gauntlet.py -n 15
"""

import argparse
import contextlib
import io
import itertools
import multiprocessing as mp
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ENV = {}

# Opponents reconstructed from the ACTUAL day-20 boards of players who beat us,
# taken from 30 real ladder losses. Previously every archetype here was our own
# agent with different parameters, so the pool could only ever test our build
# against our own ideas -- and it saturated at 100%, losing all discriminating
# power. These are the real field's allocations instead.
OPPONENTS = {
    "starter": None,
    # Mikey Marszewski $154,856 -- top score observed
    "real_mikey":  {"target_cows": 8, "target_sheep": 6, "target_geese": 0,
                    "melon_tiles": 9, "strawberry_tiles": 39,
                    "wheat_tiles_target": 3, "min_wheat_tiles": 3,
                    "wheat_lead_tiles": 0, "carrot_fill": False},
    # Kazuta MIZUTA $130,458
    "real_kazuta": {"target_cows": 10, "target_sheep": 2, "target_geese": 0,
                    "melon_tiles": 9, "strawberry_tiles": 37,
                    "wheat_tiles_target": 2, "min_wheat_tiles": 2,
                    "wheat_lead_tiles": 0, "carrot_fill": False},
    # Somasundar V $93,150 -- cow-heavy, no melon
    "real_somas":  {"target_cows": 14, "target_sheep": 4, "target_geese": 0,
                    "melon_tiles": 0, "strawberry_tiles": 13,
                    "wheat_tiles_target": 6, "min_wheat_tiles": 6,
                    "wheat_lead_tiles": 0, "carrot_fill": False},
    # Josh Hipps $87,882 -- mixed herd incl. geese, melon+wheat, no strawberry
    "real_josh":   {"target_cows": 9, "target_sheep": 4, "target_geese": 4,
                    "melon_tiles": 10, "strawberry_tiles": 0,
                    "wheat_tiles_target": 12, "wheat_lead_tiles": 0,
                    "carrot_fill": False},
    # Yuelin Bai $84,086 -- huge herd, no crops but wheat
    "real_yuelin": {"target_cows": 15, "target_sheep": 11, "target_geese": 9,
                    "melon_tiles": 0, "strawberry_tiles": 0,
                    "wheat_tiles_target": 14, "wheat_lead_tiles": 0,
                    "carrot_fill": False},
    # Sam kramer $55,395 -- wheat-heavy generalist
    "real_sam":    {"target_cows": 6, "target_sheep": 10, "target_geese": 0,
                    "melon_tiles": 3, "strawberry_tiles": 20,
                    "wheat_tiles_target": 37, "wheat_lead_tiles": 0,
                    "carrot_fill": False},
}

# `current` is melon32/geese14 (round-4 winner). It sits next to a cliff --
# melon28/geese14 collapses outright -- so the point of this run is robustness
# across archetypes, not another point on the melon curve.
# Probing how far the wheat pivot goes. `current` is wheat30/melon24/geese20.
# `current` is the livestock pivot: sheep6 / cow10 / goose4, wheat38, melon16.
# Strawberry needs capital the livestock has already spent, so test it only
# alongside a smaller herd that leaves room to actually buy the seed.
# `current` is the strawberry build: 34 straw / 12 wheat / 10 melon / 8 cow
# 6 sheep, carrot_fill off, rate-limited seed buying.
# Testing melon+cow+wheat+sheep against the strawberry-heavy v6. The public
# coins-per-action table ranks melon watering ~250, cow ~95, sheep ~86 against
# strawberry ~37 and wheat ~17 — and v6 runs 28 strawberry / 16 wheat / 10 melon.
# Melon and strawberry compete for the same tiles, so melon only rises as
# strawberry falls.
CANDIDATES = {
    "v9-current":  {},                                    # 12cow 0shp 10mel 28str 16wht
    # Mirror the top two real winners: low wheat, high strawberry, some sheep.
    # wheat_lead_tiles must drop or the herd never expands behind 3 wheat tiles.
    "mimic-top":   {"target_cows": 9, "target_sheep": 4, "melon_tiles": 9,
                    "strawberry_tiles": 36, "wheat_tiles_target": 4,
                    "min_wheat_tiles": 4, "wheat_lead_tiles": 0},
    "mimic-soft":  {"target_cows": 10, "target_sheep": 3, "melon_tiles": 10,
                    "strawberry_tiles": 32, "wheat_tiles_target": 8,
                    "min_wheat_tiles": 6, "wheat_lead_tiles": 1},
    "v9+sheep4":   {"target_sheep": 4},
    "v9-lowwheat": {"wheat_tiles_target": 8, "min_wheat_tiles": 6,
                    "wheat_lead_tiles": 1},
}


def _boot():
    if "make" not in _ENV:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            from kaggle_environments import make
        _ENV["make"] = make
    return _ENV["make"]


def _episode(job):
    cname, cov, oname, oov, seed, steps, seat = job
    make = _boot()
    from kagri.agent import act

    def mine(obs):
        return act(obs, cov)

    def theirs(obs):
        return act(obs, oov)

    opponent = "starter" if oov is None else theirs
    line = [mine, opponent] if seat == 0 else [opponent, mine]
    with contextlib.redirect_stderr(io.StringIO()):
        env = make("kaggriculture",
                   configuration={"episodeSteps": steps, "seed": seed}, debug=False)
        env.run(line)
    r = [float(s.reward or 0) for s in env.steps[-1]]
    return cname, oname, r[seat], r[1 - seat]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--seeds", type=int, default=15)
    ap.add_argument("--steps", type=int, default=720)
    ap.add_argument("-j", "--jobs", type=int, default=max(1, mp.cpu_count() - 2))
    args = ap.parse_args()

    seeds = range(1, args.seeds + 1)
    jobs = [(cn, cv, on, ov, s, args.steps, seat)
            for (cn, cv), (on, ov), s, seat
            in itertools.product(CANDIDATES.items(), OPPONENTS.items(), seeds, (0, 1))]

    t0 = time.time()
    with mp.Pool(args.jobs) as pool:
        results = pool.map(_episode, jobs, chunksize=1)
    elapsed = time.time() - t0

    cells = {}
    for cn, on, a, b in results:
        cells.setdefault((cn, on), []).append((a, b))

    def winrate(pairs):
        w = sum(1 for a, b in pairs if a > b)
        t = sum(1 for a, b in pairs if a == b)
        return 100.0 * (w + 0.5 * t) / len(pairs)

    opps = list(OPPONENTS)
    print(f"\n{len(jobs)} episodes in {elapsed:.0f}s, both seats\n")
    header = f"{'config':<14}" + "".join(f"{o:>11}" for o in opps) + f"{'ALL':>8}{'worst':>8}{'mean $':>10}"
    print(header)
    print("-" * len(header))
    rows = []
    for cn in CANDIDATES:
        per = [winrate(cells[(cn, on)]) for on in opps]
        allp = [p for on in opps for p in cells[(cn, on)]]
        rows.append((winrate(allp), min(per), cn, per, statistics.mean(a for a, _ in allp)))
    for overall, worst, cn, per, mean in sorted(rows, reverse=True):
        print(f"{cn:<14}" + "".join(f"{v:>10.0f}%" for v in per)
              + f"{overall:>7.0f}%{worst:>7.0f}%{mean:>10,.0f}")
    print("\n'worst' is the weakest single matchup — on a ladder that is the "
          "matchup that costs you rating, so prefer a flat profile over a "
          "high average with a soft spot.")


if __name__ == "__main__":
    mp.freeze_support()
    main()
