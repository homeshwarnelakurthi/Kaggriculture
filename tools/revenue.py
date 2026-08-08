"""Where the money actually comes from: revenue and spend, attributed by product.

This instrument was missing for the whole project. Every strategy argument so
far -- eggs vs milk, melon's fixed pot, whether wheat is worth its tiles -- has
been argued from the price MODEL rather than from what a run actually earned.
When two builds finish $5k apart, the model cannot say which product moved.

Method: intercept the agent's own market orders and re-price them against the
market inventory observed on that turn, using the same `sell_revenue` /
`buy_cost` the engine uses. Sales commit before the opponent's within a turn
only sometimes, so treat totals as accurate to a few percent -- more than good
enough to see which product carries a build.

  python tools/revenue.py -n 4
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

CONFIGS = {
    "v13 HEAD":  {},
    "open 3c1s": {"open_cows": 3, "open_sheep": 1},
}

# Split the season so an early-investment build can be told apart from a
# late-liquidation one. The opening variants lead HEAD at day 22 and lose by 30.
PHASES = ((0, 11), (12, 21), (22, 30))


def _boot():
    if "make" not in _ENV:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            from kaggle_environments import make
        _ENV["make"] = make
    return _ENV["make"]


def _phase(day):
    for i, (lo, hi) in enumerate(PHASES):
        if lo <= day <= hi:
            return i
    return len(PHASES) - 1


def _episode(job):
    name, ov, seed = job
    make = _boot()
    from kagri.agent import act
    from kagri.farm import View
    from kagri.market import buy_cost, sell_revenue

    # product -> [phase0, phase1, phase2] of realised dollars
    sold = {}
    bought = {}

    def mine(obs):
        a = act(obs, ov)
        v = View(obs)
        ph = _phase(v.day)
        for order in a.get("market", []):
            op = order[0]
            if op == "SELL":
                item, qty = order[1], int(order[2])
                inv = v.minv.get(item, 10000)
                sold.setdefault(item, [0] * len(PHASES))[ph] += sell_revenue(item, inv, qty)
            elif op in ("BUY_PRODUCT", "BUY_SEED"):
                item, qty = order[1], int(order[2])
                if op == "BUY_PRODUCT":
                    cost = buy_cost(item, v.minv.get(item, 10000), qty)
                else:
                    from kagri.constants import CROPS
                    cost = CROPS[item]["seed"] * qty
                bought.setdefault(f"seed:{item}" if op == "BUY_SEED" else item,
                                  [0] * len(PHASES))[ph] += cost
            elif op == "BUY_ANIMAL":
                from kagri.constants import ANIMALS
                bought.setdefault(order[1], [0] * len(PHASES))[ph] += \
                    ANIMALS[order[1]]["cost"] * int(order[2])
            elif op == "BUY_LAND":
                bought.setdefault("LAND", [0] * len(PHASES))[ph] += 0  # priced below
        return a

    with contextlib.redirect_stderr(io.StringIO()):
        env = make("kaggriculture",
                   configuration={"episodeSteps": 720, "seed": seed}, debug=False)
        env.run([mine, "starter"])
    return name, sold, bought, float(env.steps[-1][0].reward or 0)


def _merge(dicts):
    out = {}
    for d in dicts:
        for k, v in d.items():
            cur = out.setdefault(k, [0.0] * len(PHASES))
            for i, x in enumerate(v):
                cur[i] += x
    n = max(1, len(dicts))
    return {k: [x / n for x in v] for k, v in out.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--seeds", type=int, default=4)
    ap.add_argument("-j", "--jobs", type=int, default=max(1, mp.cpu_count() - 2))
    args = ap.parse_args()

    jobs = [(n, ov, s) for n, ov in CONFIGS.items() for s in range(1, args.seeds + 1)]
    with mp.Pool(args.jobs) as pool:
        results = pool.map(_episode, jobs, chunksize=1)

    per = {}
    for name, sold, bought, money in results:
        per.setdefault(name, []).append((sold, bought, money))

    tables = {}
    for name, runs in per.items():
        tables[name] = (_merge([s for s, _, _ in runs]),
                        _merge([b for _, b, _ in runs]),
                        statistics.mean(m for _, _, m in runs))

    labels = [f"d{lo}-{hi}" for lo, hi in PHASES]
    names = list(CONFIGS)
    for name in names:
        sold, bought, money = tables[name]
        print(f"\n=== {name}   final ${money:,.0f} ===")
        print(f"  {'product':<14}" + "".join(f"{l:>12}" for l in labels) + f"{'TOTAL':>12}")
        rows = sorted(sold.items(), key=lambda kv: -sum(kv[1]))
        for item, v in rows:
            print(f"  {item:<14}" + "".join(f"{x:>12,.0f}" for x in v)
                  + f"{sum(v):>12,.0f}")
        print(f"  {'SOLD':<14}" + "".join(
            f"{sum(v[i] for v in sold.values()):>12,.0f}" for i in range(len(PHASES)))
            + f"{sum(sum(v) for v in sold.values()):>12,.0f}")
        print(f"  {'-- spend --':<14}")
        for item, v in sorted(bought.items(), key=lambda kv: -sum(kv[1])):
            if sum(v) <= 0:
                continue
            print(f"  {item:<14}" + "".join(f"{-x:>12,.0f}" for x in v)
                  + f"{-sum(v):>12,.0f}")

    if len(names) == 2:
        a, b = names
        sa, ba, _ = tables[a]
        sb, bb, _ = tables[b]
        print(f"\n=== {b} MINUS {a} (revenue by product) ===")
        keys = set(sa) | set(sb)
        deltas = []
        for k in keys:
            va = sa.get(k, [0] * len(PHASES))
            vb = sb.get(k, [0] * len(PHASES))
            deltas.append((sum(vb) - sum(va), k, [y - x for x, y in zip(va, vb)]))
        print(f"  {'product':<14}" + "".join(f"{l:>12}" for l in labels) + f"{'TOTAL':>12}")
        for total, k, v in sorted(deltas):
            print(f"  {k:<14}" + "".join(f"{x:>+12,.0f}" for x in v) + f"{total:>+12,.0f}")


if __name__ == "__main__":
    mp.freeze_support()
    main()
