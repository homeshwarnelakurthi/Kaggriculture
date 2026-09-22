# V48: production and worker scheduling — experimental

Built September 19, 2026. **Not submitted to Kaggle.** The new agent produces and sells more goods in the audited games, but the broader competitive tests do not justify replacing the live agent yet.

## Implemented changes

1. **Multi-day harvest scheduling.** At an existing worker's goose tile, compare the next 96 turns of scheduled care, feeding and harvesting. Replace care, idle work, or fertilizer collection with an earlier harvest only when the forecast predicts net additional eggs after accounting for foregone care and fertilizer value. This can act throughout the day, rather than only at the last turn. Existing movement, feeding and watering commands are preserved. Exact current field/storage checks reject added immediate or projected overnight spills. The forecast assumes future scheduled feeding succeeds; it is not a full opponent-aware game rollout.
2. **Fertilizer and worker investment.** Revalue the existing finite fertilizer tours using predicted extra wheat/carrot units, marginal sale prices, fertilizer purchase cost, travel time and worker hire cost. Allow productive two-tile routes and lower the economic hurdle from 1.5 times cost plus 50 coins to 1.15 times cost plus 15 coins. Retain the 3000-coin cash buffer, finite watering/harvest windows, market-order limit and input-purchase capacity checks; tighten the initial occupancy limit to 90. This expands the jobs accepted by the inherited planner; it is not a new whole-farm crop-selection system.
3. **Production telemetry.** Expose hired-worker, delivered-input and confirmed-fertilization counters alongside scheduling interventions so tests show that new work actually happens.

Harvest-only, investment-only and combined candidates were tested separately. The main artifact contains the combined candidate.

## Development replay comparisons

Margins against fixed recorded opponents, in coins. These episodes were used for development and cannot measure adaptation by the opponent.

| Candidate | Adwait | Tomohito | Minghao |
|---|---:|---:|---:|
| Actual V47 | -101 | -477 | -2129 |
| Harvest only | +474 | +81 | -1493 |
| Investment only | +160 | +253 | -1570 |
| Combined V48 | +710 | +553 | -1162 |

The final combined source was independently rerun with transaction instrumentation. Relative to V47, it sells 37/63/38 additional wheat and 10/8/6 additional eggs in these three games. Carrot sales change by +7/0/+1. Strawberry sales fall by four in each. These are measured sales quantities, not claimed forecasts. Additional production does not automatically translate to proportionate income, and storage interactions remain unresolved.

## Reactive opponent tests

| Cohort | Candidate and opponent | Wins / losses | Mean margin |
|---|---|---:|---:|
| Initial screen, seeds 1001-1002, both seats | Harvest vs V47 | 4 / 0 | +347.5 |
| Initial screen | Investment vs V47 | 4 / 0 | +394.5 |
| Initial screen | Combined vs V47 | 4 / 0 | +908.0 |
| External, seeds 1021-1022, both seats | Harvest vs wide | 0 / 4 | -419.0 |
| External | Investment vs wide | 2 / 2 | -66.0 |
| External | Combined vs wide | 2 / 2 | +134.5 |
| External | V47 vs wide | 0 / 4 | -595.0 |
| External | Combined vs independent Barnyard | 4 / 0 | +99620.0 |
| New seeds 1051-1055, both seats | Combined vs V47 | 7 / 3 | +441.7 |
| Same cohort | Combined vs wide | 3 / 7 | -318.9 |
| Fresh paired seeds 1101-1103, both seats | Combined vs wide | 0 / 6 | -847.0 |
| Fresh paired control | V47 vs wide | 0 / 6 | -912.0 |
| Fresh paired | Combined vs trader_front | 6 / 0 | +5858.0 |
| Fresh paired control | V47 vs trader_front | 6 / 0 | +5699.33 |

The combined build wins only **5 of 20** games against wide across the three cohorts, and none in the last cohort. One paired wide seed worsens by 505 coins in both seats. One Barnyard margin worsens by 842 despite still winning. These regressions are retained. Wide and trader_front are reactive derivatives of the same route family; Barnyard is independent but substantially weaker. Seat-paired games are correlated, not 20 independent samples. There is no claim of higher Kaggle rating.

## Rejected storage variant

An additional variant sold surplus wheat/fertilizer/eggs to make room for incoming production. It improved the reused 1051-1055 cohort to 5/10 wins versus wide, but still lost all six fresh wide games. Its trader_front mean margin fell to +5338.67, below V47's +5699.33 control. It also turned the Adwait replay from V48's +710 win into a -452 loss. Its separate file-loader check additionally failed with KeyError: 0 in the trailing _flow_allocate function; the benchmark harness calls the named agent directly, so its benchmark completion does not establish file-loader compatibility. It is retained only as a rejected experiment, excluded from main.py. The combined final source passed both file-loader seats.

## Correctness, packaging and limitations

- 200 forecast comparisons against the pinned official engine passed, including holding caps, delayed care and animal escape.
- All 120 games in the six completed benchmark batches have valid completion and zero nonzero error telemetry. This total includes controls, individual candidates and the rejected storage variant; it is not 120 games of final V48.
- Both seats of the actual Kaggle Python-file loader complete all 720 states for the final combined source. This proves loading/completion, not competitive strength.
- Final-source release-cohort maximum measured turn time is 300.191 ms on this machine; this is not a Kaggle runtime guarantee.
- The source in v48.tar.gz is verified byte-for-byte against the tested combined source. Original source notices and Apache license are preserved.
- A build-script filename collision caused invalid source loads during an early external batch. Extension files now have separate names. The entire external batch was rerun from frozen source; the invalid batch is retained as external-interrupted-build.jsonl and excluded from results. The 12-game initial screen predates a small escape-accounting correction; the final engine checks and subsequent cohorts use the corrected source.

## Next work

The production changes are implemented, but promotion is blocked by competitive results. Investigate the losing wide matchups and the four displaced strawberries per replay before adding more output. Measure the timing and value of overflow and sales jointly; the rejected blanket surplus-sale rule demonstrates why simply selling sooner is insufficient. The next evaluation needs stronger independent reactive opponents as well as these regression fixtures.

## Files and reproduction

main.py is the final experimental candidate; v48.tar.gz is its packaged artifact. build.json records hashes and the submission hold. validation.json contains complete cohort summaries. production-audit.json retains final-source transactions; experiments contains standalone variants. JSONL files retain individual outcomes, telemetry, shops and timings.

Canonical reproducible scripts remain under the workspace's work/v48 directory. Run build.py there using C:/kenv/Scripts/python.exe; it reads the preserved outputs/v47/main.py base. Benchmark configurations use absolute workspace paths and H:/Kaggriculture/tools/benchmark_agents.py with the pinned 1.32.7 environment. Copies of scripts here are reference artifacts and retain the canonical workspace layout assumptions.
