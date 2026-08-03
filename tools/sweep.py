"""Parallel self-play parameter sweep.

Runs each candidate parameter set over a fixed set of seeds against a chosen
opponent and reports mean bank plus head-to-head win rate. Ratings on the real
ladder are win/loss only, so WIN RATE is the number that matters — a config
that wins by $1 more often beats one that occasionally wins huge.

  python tools/sweep.py                      # A/B the built-in candidate list
  python tools/sweep.py --opp mirror -n 12   # mirror matches, 12 seeds
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


def _boot():
    """Import the environment once per worker; it is slow and noisy."""
    if "make" not in _ENV:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            from kaggle_environments import make
        _ENV["make"] = make
    return _ENV["make"]


def _episode(job):
    """Run one episode. `seat` says which side we occupy.

    Every config is played in BOTH seats on every seed. Market orders resolve
    in player order and hired hands spawn from a fixed NWSE preference, so the
    seats are not symmetric; without swapping, seat bias swamps the effect of
    whatever parameter is being measured.
    """
    name, overrides, opp_overrides, seed, steps, seat = job
    make = _boot()
    from kagri.agent import act

    def mine(obs):
        return act(obs, overrides)

    def theirs(obs):
        return act(obs, opp_overrides)

    opponent = theirs if opp_overrides is not None else "starter"
    line = [mine, opponent] if seat == 0 else [opponent, mine]
    with contextlib.redirect_stderr(io.StringIO()):
        env = make("kaggriculture",
                   configuration={"episodeSteps": steps, "seed": seed},
                   debug=False)
        env.run(line)
    rewards = [float(s.reward or 0) for s in env.steps[-1]]
    return name, seed, rewards[seat], rewards[1 - seat]


# Candidate configs. Keep the list short: every entry costs n_seeds episodes.
CANDIDATES = {
    "base":        {},
    # max_hands never binds: hand_value_per_action*24 caps the fib walk at 12.
    "hands13":     {"hand_value_per_action": 10.0, "max_hands": 16},
    "hands15":     {"hand_value_per_action": 26.0, "max_hands": 18},
    "geese28":     {"target_geese": 28},
    "melon16":     {"melon_tiles": 16},
    "melon6":      {"melon_tiles": 6},
    "tiles9":      {"tiles_per_unit": 9.0},
    "fatreserve":  {"ops_reserve_base": 700.0},
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opp", default="starter",
                    help="'starter' or 'mirror' (base config plays itself)")
    ap.add_argument("-n", "--seeds", type=int, default=8)
    ap.add_argument("--steps", type=int, default=720)
    ap.add_argument("-j", "--jobs", type=int, default=max(1, mp.cpu_count() - 2))
    args = ap.parse_args()

    opp_overrides = {} if args.opp == "mirror" else None
    seeds = list(range(1, args.seeds + 1))
    jobs = [(name, ov, opp_overrides, seed, args.steps, seat)
            for (name, ov), seed, seat
            in itertools.product(CANDIDATES.items(), seeds, (0, 1))]

    t0 = time.time()
    with mp.Pool(args.jobs) as pool:
        results = pool.map(_episode, jobs, chunksize=1)
    elapsed = time.time() - t0

    by_name = {}
    for name, seed, a, b in results:
        by_name.setdefault(name, []).append((a, b))

    n_ep = len(jobs)
    print(f"\n{n_ep} episodes vs {args.opp} in {elapsed:.0f}s "
          f"({args.jobs} workers, {elapsed / n_ep:.1f}s/episode), both seats\n")
    print(f"{'config':<14} {'mean $':>9} {'median $':>9} {'worst $':>9} "
          f"{'opp $':>9} {'win%':>7} {'±95%':>6}")
    print("-" * 70)
    rows = []
    for name, pairs in by_name.items():
        mine = [a for a, _ in pairs]
        opp = [b for _, b in pairs]
        wins = sum(1 for a, b in pairs if a > b)
        ties = sum(1 for a, b in pairs if a == b)
        n = len(pairs)
        wr = (wins + 0.5 * ties) / n
        # Normal-approx CI, to stop us reading noise as signal.
        ci = 196.0 * (wr * (1 - wr) / n) ** 0.5
        rows.append((wr * 100, statistics.mean(mine), name, mine, opp, ci))
    for wr, mean, name, mine, opp, ci in sorted(rows, reverse=True):
        print(f"{name:<14} {mean:>9,.0f} {statistics.median(mine):>9,.0f} "
              f"{min(mine):>9,.0f} {statistics.mean(opp):>9,.0f} "
              f"{wr:>6.0f}% {ci:>5.0f}")


if __name__ == "__main__":
    mp.freeze_support()
    main()
