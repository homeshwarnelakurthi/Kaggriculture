# V47: guarded recovery of capped egg production

Built, locally validated and submitted to Kaggle. The authenticated submissions page confirms **Pending**. See `submission-status.json` for the verification timestamp.

## Diagnosis from real Kaggle losses

The missing eggs primarily came from geese reaching their four-egg holding limit before collection. More CARE commands cannot recover production discarded at that limit. Exact engine instrumentation reproduced the downloaded games and measured:

| Match | Our eggs produced | Opponent eggs produced | Our cap losses | Opponent cap losses | Shed eggs discarded, ours/opponent |
|---|---:|---:|---:|---:|---:|
| SkOnTheRocks | 78 | 78 | 16 | 16 | 0 / 0 |
| lucataco | 78 | 83 | 16 | 10 | 6 / 4 |
| Stephen Schott | 138 | 161 | 33 | 6 | 6 / 6 |

Against lucataco, five of the seven missing sale units came from lower production and two from additional shed discard. Against Stephen Schott, the 23-unit sales deficit is explained by lower production; shed discard was equal. Our potential yield before holding caps was actually higher, so simply adding care was the wrong fix.

## Final change

At the last turn of a day, V47 may replace PASS, already-completed CARE, or fertilizer collection with a harvest on the same goose tile when the upcoming production would exceed its holding limit. It does not reroute workers or replace feeding/watering. It requires adequate overnight storage, preserves planned wheat/fertilizer needs, and values the newly unblocked production against foregone fertilizer. Escaping or not-yet-productive geese do not qualify.

Harvesting changes the publicly visible egg count. V47 tracks that specific self-caused difference for at most 72 turns so V46â€™s timing controller does not mistake it for an opponent strategy change. Feeding, care, worker positions and other productive state must still match. Tracking clears on matching tiles, expiry or episode/discontinuity reset.

A conservative gate abstains when farms have similar production layouts but their detailed states are not synchronized. The initial broader harvest fix recovered four eggs in all three development replays, but interacted badly with market decisions in some reactive matchups. It is retained as an experiment, not the release. Buying replacement fertilizer did not cure that regression and is also excluded.

## Final build validation

Fresh head-to-head holdout, seeds 921â€“930, both seats: **14 wins, 4 ties, 2 losses** versus V46. Mean margin +177.3 coins; worst margin -40. The two losses are both seats of seed 923 (-40 coins each). The final policy is frozen before these seeds were tested.

Paired external results compare the same opponent, seed and seat with V46 controls. Win counts alone can hide changes in already-winning or already-losing games.

| Cohort | Opponent | V47 W/T/L | Mean margin change vs V46 | Worst paired change |
|---|---|---|---:|---:|
| Development regression | wide | 0/0/8 | +132.5 | +0 |
| Development regression | trader_front | 8/0/0 | +120.0 | +0 |
| Fresh seeds 951â€“952 | wide | 0/0/4 | +96.5 | +0 |
| Fresh seeds 951â€“952 | trader_front | 4/0/0 | +99.0 | +0 |

The wide and trading opponents are reactive derivatives of the same route family, not independent competitors. The final guarded version was not given a separate independent-Barnyard release benchmark; an earlier broader version won four games versus Barnyard, which is not counted as release validation. This remains a coverage limitation.

| Real replay used during development | V46 margin | Final V47 margin |
|---|---:|---:|
| 110241309 | -63 | -63 |
| 110236449 | -2091 | -2091 |
| 110250683 | +84 | +254 |

These are fixed recorded opponents and development fixtures, not unseen live matches. The final guard leaves two losses unresolved. The SkOnTheRocks improvement is +170 coins relative to V46, rather than the larger comparison against V45.

All release benchmark games finished normally with no nonzero error telemetry. Focused checks verify real-engine egg recovery, storage/input protection, immutability, essential-work preservation, expiry of self-change tracking, and preservation of genuine feed divergence. Two games using the actual Kaggle file loader passed. Max measured turn time in the release holdout was 714.077 ms on this machine; local timing does not guarantee Kaggle runtime.

## Artifacts and remaining work

`main.py` and `v47.tar.gz` are the final candidate. `changes.patch` shows the diff from V46. `validation.json` and release/fresh JSONL files contain the measured results. `production-diagnosis.json` and episode egg ledgers preserve the diagnosis. Earlier cap/coherent/replenishment sources are under `experiments/`; their broader benefits and adverse results are not attributed to the final guarded build.

Some earlier runs were interrupted: the first cap-only holdout has 18 of 20 games and its initial independent cohort has 4 of 8. Neither is counted as a completed release cohort. Later final cohorts are separately named and count-checked.

The larger unresolved opportunity is worker routing to collect other full geese before production. That requires preserving travel, feeding, storage and sale schedules across several turns; this release makes only a guarded one-turn substitution. No live score improvement is established until Kaggle evaluates it.

Source SHA256: `6662cf16e45f675d35cab7571cedced4622f91a5b9495bdb63d6d07677be07a0`

Archive SHA256: `fea0a1aea31cd0a7d8d0d41cc4cfce6ece88180f07205d668decebd9b506a75d`
