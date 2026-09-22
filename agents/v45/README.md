# V45: integrated stock and market controller

V45 combines the current farm plan with a shared view of harvestable production, carried goods, shed capacity, feed/input obligations, visible rival production, shop demand and possible future prices.

## Decisions implemented

- **Hold:** defer an early sale reservation when a dissimilar rival and predicted demand favor waiting, provided storage pressure is low. This happens before future-sale debts are created.
- **Consume or reserve:** protect wheat and fertilizer needed by planned pickups until replenishment, with a bounded 48-turn lookahead and a one-day animal-feed allowance. Extra sales cannot reduce protected overnight inputs relative to the original policy.
- **Sell now:** use exact own-field and overnight-deposit simulations to clear storage for incoming goods. Rank surplus by the estimated cost of selling now instead of waiting. Fertilizer is marketable in the current engine; earlier project notes saying otherwise were incorrect.
- **Reserve a future sale:** extend eligible sales up to ten turns only when visible layout and cash-response evidence support similar production, and the forecast predicts competing supply or storage pressure. Existing pickup/purchase barriers and sale-debt accounting remain intact.
- **Avoid production that cannot pay:** block planting when the crop cannot reach its first yield before the season ends. The established crop/livestock investment controllers remain responsible for broader production choices; this is not yet a complete optimizer of farm composition.
- **Deliver earlier:** allow a final-hour idle worker beside the shed to deposit marketable goods only if the exact projection preserves protected feed and fertilizer. This branch did not activate in the holdout sample, so no measured gain is attributed to it.

Forecasts update every turn. New intervention is concentrated in the middle and late game; the inherited opening and terminal planner remain in use. Rival private stock is unknown. The rival supply forecast is a scenario based on visible harvestable yields and similar-farm evidence, not a known inventory.

## Validation

| Check | Result |
|---|---|
| Initial combined screen, seeds 501-503, both seats | 6 wins / 6 games vs V44 |
| Holdout, seeds 521-530, both seats | 20 wins / 20 games vs V44 |
| Holdout coin margin | mean +1,459.3; minimum +913 |
| External opponents, seeds 541-543, both seats | 6/6 wins vs V43 and 6/6 vs Barnyard |
| Same-batch V44 external control | also 12/12 wins |
| Errors / failed games in these suites | zero |
| Maximum holdout turn time | 436.663 ms under concurrent local load |
| Exact final source through Kaggle file loader | 2 complete games, both seats |

The holdout triggered 290 additional storage-clearing sale units and 14 held reservations over 20 games. It did not activate early-deposit changes. The storage-only ablation also won all six screening games, averaging +840 coins; the full controller averaged +1,664 in that screen.

Code review caught an early-deposit feed-priority edge case. The final patch preserves the original protected-input baseline and also gates adaptive reservations on the supported configuration. Targeted tests cover that protection, ordered overnight deposits, surplus fertilizer sales, action immutability and crop maturity. Two further full games against V44 and Barnyard confirmed action equivalence between the screened source and final safety-patched source on seeds 561 and 562. The exact final source then passed two actual file-loader games on seed 563.

The ten holdout seed pairs are correlated across seats, and two opponents share route ancestry. External winning margins improved on average, but not on every game. These results support a submission experiment, not a guaranteed Kaggle rating increase.

## Files and reproduction

`main.py` is the exact bundled policy. `flow_controller.py` exposes the added controller for review. `build.json` records source and archive hashes; `validation.json` and the JSONL files retain game-level evidence. `submission-status.json` records the observed Kaggle state after upload.

Tests were run with C:/kenv/Scripts/python.exe and the isolated official engine under H:/Kaggriculture/work/runtime1327. The benchmark harness is H:/Kaggriculture/tools/benchmark_agents.py. Saved configs use the working copies under the Codex workspace; `unit_checks.py` and `final_checks.py` record the final focused checks.
