# V43 storage-only experiment

Status: complete, not submitted. V43's six-turn planned sale reservations and existing field controllers are retained. The added controller only sells current shed surplus at the end of a day to make room for carried goods, while protecting projected wheat/fertilizer input reserves. Adaptive sale reservations and production edits are disabled.

## Results

| Matchup | Candidate W / T / L | V43 control W / T / L |
|---|---|---|
| Against V43, seeds 621-628, both seats | 10 / 4 / 2 | Not applicable |
| Against V45, seeds 601-604, both seats | 0 / 0 / 8 | 0 / 0 / 8 |
| Against Barnyard, seeds 601-604, both seats | 8 / 0 / 0 | 8 / 0 / 0 |

The direct V43 comparison averaged +266 coins, with a worst result of -67. External comparisons averaged +67 coins relative to V43 against V45, and -22 against Barnyard. Every external candidate/control pair had the same final shop sequence. The Barnyard regression was concentrated in seed 604 (-220 coins in both seats). These are eight and four independent seed values respectively, with correlated seat swaps.

All 48 completed games were valid and recorded no error/fallback diagnostics. Maximum candidate decision time was 403.292 ms. Focused checks passed for action immutability, official market and overnight deposits, feed reservation limits, and fertilizer surplus sales.

An initial source line-ending packaging error produced 32 invalid candidate attempts before any game turns ran. They remain recorded in the original logs/JSONL and are excluded from completed-game results. The corrected reruns are explicitly named holdout-valid and external-valid. The original external run supplies only its 16 valid V43 control games. The corrected source hash is in experiment.json.

## Decision

Do not promote this candidate automatically. It is a measurable local improvement in some situations but neither dominates V43 nor converts losses against the other tested agents into wins. The previous competition result already showed that local head-to-head gains do not reliably predict leaderboard performance.

The next useful investigation is to inspect actual competitive losses and compare stronger independent opponents. Reducing discarded stock alone is not enough: extra commodity sales affect the shared market and can change both players' future costs and returns. That is a mechanism to investigate, not an established explanation of these particular losses.

No Kaggle submission was made in this experiment. The existing V43/V44/V45 files were preserved. main.py is an experimental source, not a release archive.

## Reproduce

Use C:/kenv/Scripts/python.exe with H:/Kaggriculture/tools/benchmark_agents.py and the saved configs. The isolated engine is H:/Kaggriculture/work/runtime1327. Configs point to the working candidate under the Codex workspace. summarize.py documents exactly which records enter the report; unit_checks.py contains the targeted checks.
