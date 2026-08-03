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
    "v1":        {"melon_tiles": 10, "target_geese": 22},     # our own earlier build
    "eggrush":   {"melon_tiles": 4, "target_geese": 26},      # ignores melon entirely
    "melonrush": {"melon_tiles": 32, "target_geese": 12},     # contests melon hard
}

CANDIDATES = {
    "current":     {},
    "m32-geese14": {"melon_tiles": 32, "target_geese": 14},
    "m24-geese20": {"melon_tiles": 24, "target_geese": 20},
    "balanced":    {"melon_tiles": 26, "target_geese": 20},
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
