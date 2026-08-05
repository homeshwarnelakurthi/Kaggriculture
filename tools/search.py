"""Two-stage search over product-mix allocations.

Hand-picking five candidates per round samples a five-dimensional space far too
thinly. This screens many mixes cheaply, then spends the expensive full-gauntlet
budget only on the survivors.

  Stage 1  every candidate vs `starter` + `strawrush`, few seeds, both seats.
           Cheap and only needs to separate "plausible" from "broken".
  Stage 2  full 6-archetype gauntlet on the top N, ranked on WORST MATCHUP.

Why two stages: a full gauntlet cell is 6 archetypes x seeds x 2 seats, so ~4
minutes per candidate. Screening 40 mixes that way would take three hours;
screening them against two opponents takes about twenty minutes.

  python tools/search.py --screen 40 --finalists 5

Ranking is always on worst matchup, never mean money — ladder rating is
win/loss only, and a build with one soft archetype bleeds rating there.
"""

import argparse
import contextlib
import io
import itertools
import multiprocessing as mp
import os
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_ENV = {}

# Opponents reused from the gauntlet; keep in sync deliberately rather than
# importing, so a change there cannot silently alter a search already running.
SCREEN_OPPONENTS = {
    "starter": None,
    "strawrush": {"strawberry_tiles": 38, "wheat_tiles_target": 8, "min_wheat_tiles": 6,
                  "melon_tiles": 8, "target_cows": 8, "target_sheep": 6,
                  "target_geese": 0, "carrot_fill": False},
}

FULL_OPPONENTS = dict(SCREEN_OPPONENTS)
FULL_OPPONENTS.update({
    "eggrush": {"melon_tiles": 4, "target_geese": 26, "wheat_tiles_target": 0},
    "melonrush": {"melon_tiles": 32, "target_geese": 12, "wheat_tiles_target": 0},
    "wheatrush": {"wheat_tiles_target": 38, "melon_tiles": 16, "target_geese": 8,
                  "target_sheep": 0, "target_cows": 0},
    "stockrush": {"target_sheep": 8, "target_cows": 14, "target_geese": 0,
                  "melon_tiles": 6, "wheat_tiles_target": 40},
})


def _boot():
    if "make" not in _ENV:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            from kaggle_environments import make
        _ENV["make"] = make
    return _ENV["make"]


def _episode(job):
    cname, cov, oname, oov, seed, seat = job
    make = _boot()
    from kagri.agent import act

    # Both callables take EXACTLY one argument. kaggle_environments passes
    # (observation, configuration) to anything accepting two or more, which
    # silently replaces the overrides and makes every variant identical.
    def mine(obs):
        return act(obs, cov)

    def theirs(obs):
        return act(obs, oov)

    opponent = "starter" if oov is None else theirs
    line = [mine, opponent] if seat == 0 else [opponent, mine]
    with contextlib.redirect_stderr(io.StringIO()):
        env = make("kaggriculture",
                   configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run(line)
    r = [float(s.reward or 0) for s in env.steps[-1]]
    return cname, oname, r[seat], r[1 - seat]


def sample_mixes(n, rng):
    """Sample the CONSTRAINT parameters, not the tile mix.

    The mix is inert: asking for 20 cows instead of 12 produces a bit-identical
    game, because the labour ceiling and the feed gate decide the board, not the
    targets. A 28-mix search over tile counts produced v7, which became our worst
    ladder result. These knobs are the ones that actually bind -- relaxing the
    feed gate alone was worth +$2,806 and raised strawberry AND cows together.
    """
    out = {}
    tries = 0
    while len(out) < n and tries < n * 40:
        tries += 1
        c = {
            # feed gate: how far wheat must lead the herd before it may grow
            "wheat_lead_tiles": rng.choice([0, 1, 2, 3, 4]),
            "wheat_buffer_per_animal": rng.choice([0.5, 1.0, 2.0, 3.0]),
            # labour ceiling and what an animal tile costs against it
            "tiles_per_unit": rng.choice([6.0, 7.0, 8.0, 9.0, 11.0]),
            "animal_labour_cost": rng.choice([1.2, 1.8, 2.5, 3.2]),
            # pacing: both of these fixed real collapses, so vary them carefully
            "seed_buy_rate": rng.choice([2, 3, 5]),
            "animal_buy_rate": rng.choice([1, 2]),
            # cash discipline
            "ops_reserve_base": rng.choice([200.0, 350.0, 550.0]),
            "hire_bank_fraction": rng.choice([0.20, 0.30, 0.45]),
        }
        name = (f"lead{c['wheat_lead_tiles']}buf{c['wheat_buffer_per_animal']:g}"
                f"tpu{c['tiles_per_unit']:g}alc{c['animal_labour_cost']:g}"
                f"sr{c['seed_buy_rate']}ar{c['animal_buy_rate']}"
                f"res{int(c['ops_reserve_base'])}hbf{c['hire_bank_fraction']:g}")
        out[name] = c
    return out


def run_stage(candidates, opponents, seeds, jobs):
    work = [(cn, cv, on, ov, s, seat)
            for (cn, cv), (on, ov), s, seat
            in itertools.product(candidates.items(), opponents.items(),
                                 range(1, seeds + 1), (0, 1))]
    with mp.Pool(jobs) as pool:
        results = pool.map(_episode, work, chunksize=1)
    cells = {}
    for cn, on, a, b in results:
        cells.setdefault((cn, on), []).append((a, b))
    return cells, len(work)


def winrate(pairs):
    w = sum(1 for a, b in pairs if a > b)
    t = sum(1 for a, b in pairs if a == b)
    return 100.0 * (w + 0.5 * t) / len(pairs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--screen", type=int, default=32, help="random mixes to screen")
    ap.add_argument("--screen-seeds", type=int, default=4)
    ap.add_argument("--finalists", type=int, default=5)
    ap.add_argument("--final-seeds", type=int, default=10)
    ap.add_argument("--seed", type=int, default=7, help="RNG seed for sampling")
    ap.add_argument("-j", "--jobs", type=int, default=max(1, mp.cpu_count() - 2))
    args = ap.parse_args()

    rng = random.Random(args.seed)
    mixes = sample_mixes(args.screen, rng)
    mixes["current-v6"] = {}          # control: must appear in both stages

    t0 = time.time()
    cells, n = run_stage(mixes, SCREEN_OPPONENTS, args.screen_seeds, args.jobs)
    print(f"\nSTAGE 1 — {n} episodes in {time.time() - t0:.0f}s, {len(mixes)} mixes\n")
    scored = []
    for cn in mixes:
        per = [winrate(cells[(cn, on)]) for on in SCREEN_OPPONENTS]
        allp = [p for on in SCREEN_OPPONENTS for p in cells[(cn, on)]]
        scored.append((min(per), winrate(allp),
                       statistics.mean(a for a, _ in allp), cn))
    scored.sort(reverse=True)
    print(f"{'mix':<22}{'worst':>7}{'ALL':>7}{'mean $':>11}")
    for worst, allw, mean, cn in scored[:12]:
        mark = "  <- control" if cn == "current-v6" else ""
        print(f"{cn:<22}{worst:>6.0f}%{allw:>6.0f}%{mean:>11,.0f}{mark}")

    finalists = {cn: mixes[cn] for _, _, _, cn in scored[:args.finalists]}
    finalists["current-v6"] = {}

    t1 = time.time()
    cells, n = run_stage(finalists, FULL_OPPONENTS, args.final_seeds, args.jobs)
    print(f"\nSTAGE 2 — {n} episodes in {time.time() - t1:.0f}s, "
          f"{len(finalists)} finalists, 6 archetypes\n")
    opps = list(FULL_OPPONENTS)
    header = f"{'mix':<22}" + "".join(f"{o:>11}" for o in opps) + f"{'ALL':>7}{'worst':>7}{'mean $':>11}"
    print(header)
    print("-" * len(header))
    rows = []
    for cn in finalists:
        per = [winrate(cells[(cn, on)]) for on in opps]
        allp = [p for on in opps for p in cells[(cn, on)]]
        rows.append((min(per), winrate(allp), cn, per,
                     statistics.mean(a for a, _ in allp)))
    rows.sort(reverse=True)
    for worst, allw, cn, per, mean in rows:
        mark = "  <- control" if cn == "current-v6" else ""
        print(f"{cn:<22}" + "".join(f"{v:>10.0f}%" for v in per)
              + f"{allw:>6.0f}%{worst:>6.0f}%{mean:>11,.0f}{mark}")
    print("\nAdopt only if a mix beats the control on WORST MATCHUP.")


if __name__ == "__main__":
    mp.freeze_support()
    main()
