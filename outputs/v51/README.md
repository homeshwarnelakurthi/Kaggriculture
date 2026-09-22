# V51: repair the file-loader entry point

V50's global `agent` name was repeatedly redefined. Python preserves its original dictionary position on reassignment, so Kaggle's last-callable loader selected the later `_v50_plan` helper instead. Named-function benchmarks exercised the intended strategy, while file-loader checks only asserted completion and missed an inactive agent. Those completion-only checks were insufficient.

The latest Kaggle main.py submission scored 131.4. Its validation replay 111415224 has both copies finish with 3000 coins and shows PASS actions with empty market orders at the opening. Its 365 KiB source size and behavior are consistent with local V50; the uploaded bytes have not been independently compared.

V51 appends `submission_agent = agent`, making the intended strategy the last callable without changing its decision logic. Four paired comparisons (seeds 1241 and 1251, both seats, eight full games total) verify exact action and reward equality between the original named V50 function and the corrected file-loaded V51. All games finished successfully with active market orders. V51 earned 168679, 168679, 172156, and 169391 coins against starter. This validates loading and execution, not a future leaderboard score.

Source: main.py. Submission archive: v51.tar.gz, containing main.py and the retained license/notice files. Build and validation scripts are in H:\Kaggriculture\work\v51. See validation.json for results.
