# Offline worker audit (V43)

Decision: do not promote the idle-care candidate. Across seeds401â€“405 in both seats, all10 games completed and tied the frozenV43 exactly. It inserted374 CARE and126 WATER commands (500 total) with no coin improvement. Maximum measured turn was308.659ms. No liveKaggle pages or results were accessed and no submission was made.

The experiment replaces only PASS commands with in-place WATER or CARE before step696. It preserves travel, purchases, feeding stock, and terminal policy. This tests whether apparently idle workers conceal easy resource-free production improvements. The result supports keeping the existing schedule: many such services are already performed later in the day, so adding commands changes activity without improving income. It does not prove every idle turn is optimal.

Files: idle_care_water.py (rejected experimental agent), config.json, screen.jsonl (10 raw games), screen-summary.json, diagnose.py, diagnostics.json.

Reproduction (PowerShell, from the workspace):

```powershell
C:\kenv\Scripts\python.exe H:\Kaggriculture\tools\benchmark_agents.py --config "$PWD\work\parallel_workers\config.json" --seeds 5 --seed-start 401 -j 2 --output "$PWD\work\parallel_workers\screen.jsonl"
C:\kenv\Scripts\python.exe .\work\parallel_workers\diagnose.py
```

Diagnostics simulate field actions using V43's extracted official1.32.7 engine. Atomic seed validation uses original seed supply for the entire action batch. Counts of unwatered or unfed tiles are observations, not automatic mistakes: crops may be abandoned deliberately and animals may survive alternating feeding. Projected overflow uses the inherited storage simulator after planned market orders, so it is a projection rather than measured actual discarded inventory. Final private inventory is read from the completed official game.

Next useful optimization: measure discarded produce by item and selling value, then schedule storage-clearing sales or delivery changes before the capacity breach. Add independent-opponent tests before changing the physical production route. Extra FEED actions require a future wheat reservation check; raw unused worker turns alone do not justify spending feed or hiring more labor.

Corrected diagnostic results (three games, seeds 301–303, V43 seat 0 against recovered V4):

- 20,824 worker commands; 1,634 PASS commands (7.8%).
- Zero no-op PLANT commands after correcting atomic validation. An earlier intermediate count of116 was a diagnostic bug, not an agent defect.
- Zero animals at risk of escaping after a second consecutive missed feeding; three plants at risk of dying after a second missed watering (not established as economically valuable).
- Projected overnight overflow:19 eggs,27 wheat,2 strawberries,1 milk,4 fertilizer (53 total units across three games); requires actual discard instrumentation before quantifying monetary value.
- All three final sheds and worker inventories contained zero sellable stock. One wheat seed remained in each game, which cannot be sold. Terminal liquidation worked in these games.

Actual engine verification completed afterward: `actual_overflow.py` hooks the official overnight inventory deposit and compares total stock before and after. The same three valid games discarded exactly53units:19eggs,27wheat,2strawberries,1milk,4fertilizer. This confirms the projection. The quote-marked total2513is descriptive, not recoverable profit; fertilizer is not sellable and counterfactual sales affect price and future input availability. Raw events are in `actual-overflow.json`.
