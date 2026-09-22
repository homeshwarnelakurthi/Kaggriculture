# V46 candidate: production-aware sale timing

Built, locally validated and **submitted to Kaggle**. The authenticated submissions page confirms `v46.tar.gz` is **Pending**. See `submission-status.json` for the verified time and archive hash.

V46 uses V45 as its base. It fixes a specific weakness exposed by the SkOnTheRocks loss: differing cash balances were treated as evidence that the opponent was no longer following the same production plan, even when all worker actions matched. That could delay sales and give the opponent better prices.

The new controller requires 24 consecutive observations with matching worker positions, unlocked land and complete productive-tile state, including yield, watering, feeding, care and fertilizer state. Random weeds on unused land are ignored. It then allows stock-backed reservations up to ten turns ahead and avoids the demand-only hold rule intended for dissimilar farms. This applies to existing mixed purchase/hire turns as well as sale-only turns. Every advanced sale retains the existing debt bookkeeping that suppresses its later scheduled sale.

A mismatch, missing observation or new episode clears confidence. When farms diverge, the controller returns to V45's existing forecast rules. Wheat/feed and fertilizer reservations, storage safeguards, order limits and the terminal planner remain in place. No hidden opponent information or episode-specific conditions are used.

## Results

| Evaluation | Result |
|---|---|
| Final holdout vs V45, seeds 771â€“780, both seats | 18 wins, 2 losses; average margin +518.2 coins; worst -338 |
| Initial screen vs V45, seeds 721â€“724, both seats | 8 wins, 0 losses |
| Aggressive timing rival, initial screen | 4 wins, 4 losses |
| Aggressive timing rival, paired seeds 741â€“744 | 0 wins, 8 losses; mean deficit 307.5 versus V45's 1,239; all eight margins improved |
| Same rival with trailing wheat round trips | 0 wins, 8 losses; mean margin improvement 931.0 over V45 |
| Rival with wheat round trips placed first, seeds 791â€“793 | 6 wins, 0 losses; V45 also wins all six; mean margin improvement 2,049.7 |
| Independent Barnyard opponent, initial screen | 8 wins, 0 losses |

The trailing-round-trip opponent produced almost identical results to the aggressive timing rival, so these are correlated checks, not independent evidence of robustness. Placing the trades first changes the interleaving of orders and gives a distinct stress case, but it is still a synthetic policy, not Stephen Schott's source.

Two extra full-game checks at seed 761 verified that cleanup of the final source preserves the screened candidate's actions in both seats. V46 loses those games by 292 coins each; they are reported separately from the 20-game holdout, not discarded. Two additional games using the actual Kaggle file loader complete normally. The maximum measured turn time in the benchmark cohorts is 268.372 ms on this machine; this is not a guarantee of Kaggle runtime.

## Actual-loss fixtures

| Recorded opponent | V45 margin | V46 margin |
|---|---:|---:|
| SkOnTheRocks, episode 110250683 | -385 | +84 |
| lucataco, episode 110241309 | -63 | -63 |
| Stephen Schott, episode 110236449 | -2,091 | -2,091 |

These episodes were used during development and are regression fixtures, not unseen holdouts. Opponent actions are fixed recordings and cannot react to our changed sales. The new version fixes one recorded loss and does not fix the other two. Local results do not establish a higher Kaggle rating.

## Rejected experiments

Extending early reservations without checking production synchrony worsened the lucataco replay. Unrestricted extra egg harvesting improved the Stephen Schott fixture by 245 coins but lost a fresh matchup against V45 by 579 coins. Neither change is included. V46 therefore improves sale timing; the remaining egg production/collection deficit and a learned model of opponent trading remain future work.

## Verification and artifacts

All reported benchmark games completed with both agents DONE and no nonzero error telemetry. Focused checks cover confidence reset on divergent production, missing observations and new games, observation immutability, protected feed, exact overnight storage, fertilizer sale handling and the inherited crop-maturity guard. Both-seat source-equivalence and file-loader checks passed.

- `main.py`: final standalone agent.
- `v46.tar.gz`: Kaggle-ready archive containing main.py, NOTICE.txt and the Apache license.
- `changes.patch`: compact diff from V45.
- `validation.json`: machine-readable summary, including adverse results.
- JSONL files: per-game results; `replay-screen.jsonl` also retains rejected experimental variants.
- `validation-opponents/`: the synthetic aggressive timing and wheat-trading opponents.
- `final_checks.py`, `inherited_checks.py` and logs: focused verification.
- `build.json`: hashes and submission status.

Source SHA256: `62fc71b3e218d4d67a7564439943da35efc68cf3570c4985d66106c91e044bf8`

Archive SHA256: `b34af5b7af8e21b78e5f1c9a281161259949ed17de623e700a6b6163be5fead5`

Reproduction uses Python at C:\kenv\Scripts\python.exe and the pinned 1.32.7 engine in H:\Kaggriculture\work\runtime1327. Benchmark runner: H:\Kaggriculture\tools\benchmark_agents.py. JSON configurations retain absolute paths for this workspace.
