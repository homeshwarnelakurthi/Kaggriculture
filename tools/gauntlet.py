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

# Distinct strategic archetypes, not parameter jitter — each stresses a
# different axis of our build.
OPPONENTS = {
    "starter":   None,                                        # built-in baseline
    "eggrush":   {"melon_tiles": 4, "target_geese": 26, "wheat_tiles_target": 0},
    "melonrush": {"melon_tiles": 32, "target_geese": 12, "wheat_tiles_target": 0},
    # Modelled on the real ladder opponent that beat us 29,790-20,698: ~35 wheat
    # tiles, ~16 melon, a small flock. Wheat is the second unbounded sink and
    # town demand keeps its price rising, so this archetype is strong and real.
    "wheatrush": {"wheat_tiles_target": 38, "melon_tiles": 16, "target_geese": 8,
                  "target_sheep": 0, "target_cows": 0},
    # Both modelled on real ladder opponents that beat us. GUILLERMO REY ran
    # 12 cows + 6 sheep for $50,011; jeon hyeon woo ran 43 strawberry for
    # $49,983. Town demand (438 milk / 335 wool / 537 strawberry per season)
    # keeps these premium goods at or above base price all game.
    "stockrush": {"target_sheep": 8, "target_cows": 14, "target_geese": 0,
                  "melon_tiles": 6, "wheat_tiles_target": 40},
    # Modelled on the top of the real ladder (39 strawberry + 8 cow + 6 sheep).
    "strawrush": {"strawberry_tiles": 38, "wheat_tiles_target": 8, "min_wheat_tiles": 6,
                  "melon_tiles": 8, "target_cows": 8, "target_sheep": 6,
                  "target_geese": 0, "carrot_fill": False},
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
    "current-v6":   {},   # melon10 cow12 sheep0 straw28 wheat16
    "m24-c10-s6":   {"melon_tiles": 24, "target_cows": 10, "target_sheep": 6,
                     "wheat_tiles_target": 12, "strawberry_tiles": 8},
    "m30-c10-s4":   {"melon_tiles": 30, "target_cows": 10, "target_sheep": 4,
                     "wheat_tiles_target": 10, "min_wheat_tiles": 6,
                     "strawberry_tiles": 6},
    "m20-c10-s5":   {"melon_tiles": 20, "target_cows": 10, "target_sheep": 5,
                     "wheat_tiles_target": 14, "strawberry_tiles": 14},
    "v6+sheep5":    {"target_sheep": 5},
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
