# Offline evaluation coverage audit

Frozen V43 was evaluated locally only. No Kaggle results, browser, network or submissions were accessed. No shared source files were edited.

## Findings

1. The original 80-game V43 validation contains **20 seed values, 44 distinct final shop sequences and 40 seat pairs**. Thirty-six seat pairs have identical candidate/opponent closing balances. Eighty wins therefore do not represent eighty independent environments. Twenty is the seed count, not the shop-sequence count.
2. The new independent-policy test ran V43 and recovered V42 against Barnyard Economist v5 and the repository's clean HEAD policy on seeds301–302 in both seats: **16 valid games, no invalids**. Each candidate won all eight of its games. These weak/opposite-style controls test compatibility and adaptation; the wins do not establish current leaderboard strength.
3. Against Barnyard, V43's winning margin fell by342coins on seed301 and1334coins on seed302, identically in both seats. The shop sequences matched and V43's queue optimizer never activated, so the horizon6 change is not universally profitable. Against legacy HEAD, same-shop seed302 also lost575margin in both seats. Seed301 produced different shop sequences for V42 versus V43, so its margin changes cannot isolate the timing improvement.
4. The queue optimizer is exact only for its modeled rival. In500 synthetic four-product scenarios,337 triggered a reorder. With the rival submitting the same order list but holding different hidden stock,2/337 changes reduced one-turn coin margin (worst−17). With a shuffled rival order and different hidden stock,45/337 reduced margin (worst−225). These deliberately sampled cases are counterexamples, **not estimates of real match frequency**. The public farms were identical in the synthetic observations to satisfy the similarity gate; that does not reveal private stock or the rival's action.

## Shared RNG caveat, verified against local official engine source

File: H:/Kaggriculture/work/runtime1327/kaggle_environments/envs/kaggriculture/kaggriculture.py

- Lines836–840: `_spawn_weeds` consumes `rng.random()` only for a tile whose value is `None`.
- Lines870–871: the day creates one `random.Random((seed * 1_000_003) ^ day)` instance.
- Line877: both farms consume that instance while spawning weeds.
- Line891: shop choice consumes that same instance afterward.

Thus a physical action that changes the number of empty tiles can change later shop selection despite an unchanged seed. A market action can also indirectly affect the opponent's planting decisions and thereby change RNG consumption. The pure call-sequence reproduction in `rng-coupling.json` found different next shops in54/100seeds when changing the total empty-tile count from20to21 on day2. At seed1, the draw changes fromICE_CREAM_SHOPtoBAKERY. This reproduces the official draw sequence, not a complete match.

## Next evaluation and design priorities

- Test a horizon policy that keeps4against dissimilar opponents and uses6when public board similarity plus cash-response evidence supports a shared route. Compare against frozenV43 on held-out seeds; do not adopt solely from these two seeds.
- Evaluate sale reordering across several plausible hidden stocks and rival orderings. Require useful expected gain and limit worst-case loss. Preserve the original orders when confidence is low. Any extra search must stay within the turn budget.
- Record shop sequences with each paired evaluation. For physical changes, use many seeds or a clearly labeled separate fixed-shop experimental harness; avoid treating same seed as perfectly controlled external demand.
- Track win rate by opponent family, worst-case margin, invalid games and maximum turn time. Treat repeated seat outcomes as correlated.
- Add stronger independent opponents when available. Barnyard and legacyHEAD are useful behavior diversity, but they do not substitute for current competitive opponents.

## Reproduction

Python: C:/kenv/Scripts/python.exe. Engine source is the isolated kaggle-environments1.32.7 under H:/Kaggriculture/work/runtime1327.

Run `H:/Kaggriculture/tools/benchmark_agents.py --config <this folder>/config.json --seeds 2 --seed-start 301 -j 2 --output <this folder>/coverage.jsonl`, then `analyze.py`. `barnyard.py` was extracted only from notebook cell9 in `public_kernels/strong-statr-baseline-agent-lb-950.ipynb`, stripped of the writefile magic, and wrapped to accept an optional config parameter. No notebook installation or publication cells were executed.

Run `stress.py` for the official `_process_market` counterexamples. It uses a fixed random seed391177, records all337triggered cases for each mode, and changes only rival private stock and order sequence after V43 has selected its action. The synthetic comparison scores the change in own-minus-rival coin margin, not just own revenue.

Files: coverage.jsonl, coverage-summary.json, stress.py, stress-results.json, rng-coupling.json, config.json, analyze.py and barnyard.py.
