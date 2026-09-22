# Kaggriculture project briefing

Self-contained handoff for another assistant or collaborator. Live figures were
pulled from Kaggle on **2026-09-14**. Everything else is from the project record
(`DEV.md`, git history, and the working sessions of 2026-08-02 to 2026-08-11).

Private project. No credentials appear in this document; the Kaggle API key lives
in `~/.kaggle/kaggle.json` and must never be committed (a pre-commit hook blocks it).

---

## 1. Status in one screen (2026-09-14)

| item | value |
|---|---|
| Team name on leaderboard | `Homii_N` |
| Leaderboard rank | **1,166 of 9,057 teams** (top ~12.9%) |
| Team score | **2278.9** |
| Top-10 cutoff (rank 10) | **2982.3** — gap **+703.4** |
| Rank 100 | 2831.5 |
| Top 1% / 5% / 10% / 25% | 2840.0 / 2644.2 / 2440.0 / 1573.3 |
| Median team | 794.2 |
| Active submissions (latest 2 count) | `56237315` (2253.5, today) and `56188391` (2278.9) |
| Days to entry + team-merger deadline | **9** (2026-09-23) |
| Days to final submission deadline | **16** (2026-09-30, 11:59 PM UTC) |
| Leaderboard convergence | ~2026-10-15 (games continue after the deadline) |

### The most important thing to know first

**The two active submissions, and the 2026-08-24 one, were not built in this
repo or in these working sessions.** The repo's last change is 2026-08-10 and
nothing after it is committed or on disk. Those three submissions have no
description and their contents are unknown to the author of this briefing. They
score far above anything the in-repo agent (`kagri/`) ever reached:

| submission | date | score | provenance |
|---|---|---|---|
| `56237315` | 2026-09-14 | 2253.5 | **unknown — made outside this repo** |
| `56188391` | 2026-09-12 | 2278.9 | **unknown — made outside this repo** |
| `55753519` | 2026-08-24 | 1317.0 | **unknown — made outside this repo** |
| best `kagri/` agent ever | 2026-08-08 | 697.7 peak, settled 624.0 | in this repo (v14) |

Anyone continuing this work should first establish what those submissions are,
because they, not `kagri/`, are the live contenders.

---

## 2. The competition

- **Kaggle Kaggriculture**, a featured simulation competition. Two players each run
  a farm and trade into one shared market. 720 turns = 24 turns/day x 30 days.
- **Prize**: $50k pool; **top 10 each win $5,000**, so 10th place is worth exactly
  as much as 1st. Optimise for reliably reaching the top 10.
- **Scoring**: win / loss / tie only, rated Bradley-Terry style. **Coin margin is
  irrelevant** — a 1-coin win equals a 50,000-coin win.
- **Limits**: 5 submissions/day; **only the latest 2 stay active** and count for
  final scoring. Bundle <= 100 MiB. Runtime box 1.6 vCPU / 6.5 GiB RAM / 8 GiB
  disk. Files unpack to `/kaggle_simulations/agent/`. **No network** during an
  episode. `actTimeout` 1 second/turn plus a 60-second overage budget.
- **Environment**: `kaggle-environments`, env `kaggriculture` v1.32.2.
- **Winners** must open-source under CC-BY 4.0.
- **Unresolved rules question**: one earlier submission (`main.py`, `55335059`)
  was a replay-tape clone of a public notebook. Rules 3.14(a) (originality
  warranty), 2.5 (licensing) and 2.8 (reproducibility) were flagged but never put
  to the hosts. If the recent high-scoring submissions are also derived from
  public notebooks, the same question applies to them.

---

## 3. Game mechanics that matter (verified against engine source)

All of these were read directly from
`kaggle_environments/envs/kaggriculture/kaggriculture.py`, not from the README,
which is wrong in places.

**Setup**: 10x10 board in four 5x5 quadrants. Start with NW unlocked and $3,000.
Extra quadrants cost NE $1,000, SW $2,000, SE $4,000.

**Crops**

| crop | seed | first yield | notes |
|---|---|---|---|
| wheat | $10 | day 2, max day 4 | one-time, max 6 units; also animal feed |
| carrot | $20 | day 2 | one-time |
| tomato | $50 | day 8 | ongoing |
| strawberry | $100 | day 10 | ongoing, every 2 days, 4 productions |
| melon | $80 | day 10, max day 12 | one-time, max 6 units |

**Animals**

| animal | cost | structure | product | first yield | interval |
|---|---|---|---|---|---|
| goose | $300 | coop | egg | day 4 | 1 |
| cow | $400 | pasture | milk | day 8 | 2 |
| sheep | $500 | pasture | wool | day 6 | 3 |

**Labour**: hiring cost follows Fibonacci per day; 12 hands cost $376 total.

**Market**
- Price = `base +/- amp * f(|inventory - 10000|)`, with product-specific shapes
  (linear, square, sqrt, log) and targets.
- **No spread.** A buy is quoted at `price(inv - 1)` and a sell at `price(inv)`,
  explicitly "so a buy/sell round-trip against an unchanged market nets zero".
  Market-making arbitrage is impossible by design.
- **Only WHEAT and FERTILIZER can be bought.** Everything else is sell-only.
- **The town drains every product except fertiliser**, twice a day, at 1x before
  day 10, 2x from day 10, 4x from day 20 (~140 units/season per product from the
  town centre alone; unlocked shops add more). With no supply, prices climb:
  wheat $25 -> $57, milk $160 -> $387, strawberry $120 -> $366, melon $250 -> $293.
- **Fertiliser is never drained.** Its lifetime pot is ~$25,045 shared by both
  players and it floors after ~400 units sold. A crash is permanent.
- A $1 floor sale does not raise market inventory.
- Market orders execute in **lockstep by list index**: both players' order #0
  resolves before #1. `HIRE` and `BUY_LAND` are atomic and handled **in player
  order, so seat 0 wins ties** — the source of measured seat asymmetry.

**Survival rules**
- **Animals produce on schedule whether or not they were fed.** Feeding only
  (a) resets the escape counter — escape needs **2 consecutive** unfed days — and
  (b) enables the CARE bonus, which requires feeding to bank and to collect.
  `fertilizer_available` is set every day regardless of feeding.
- **Plants become weeds after 2 consecutive unwatered days.** Fertiliser only
  boosts yield on a watered day. Fertiliser lasts 3 days.
- Weeds spawn only on **empty** tiles (~0.5%/day).

**Shed**: capacity 100 across all products. `DROP` into a full shed **destroys
the remainder** (`del inv[item]` runs unconditionally). At end of day all unit
inventories are force-dropped and overflow is discarded. Unit inventories have no
cap within a day. Only shed stock can be sold.

**Submission gotchas**
- Kaggle `exec`s `main.py` rather than importing it, so `__file__` is undefined.
- `kaggle_environments` passes `(observation, configuration)` to any agent callable
  with 2+ parameters, silently overwriting closures like `def mine(obs, ov=ov)`.
  Local agents must take exactly one argument.

---

## 4. Full submission history

Scores are current Kaggle values (settled, except the newest).

| date | ref | score | what it was |
|---|---|---|---|
| 2026-09-14 | 56237315 | 2253.5 | **unknown provenance**; 39 episodes, 90% wins vs avg 1,726-rated opponents — still rising |
| 2026-09-12 | 56188391 | 2278.9 | **unknown provenance**; 337 episodes, 43% wins vs avg 2,471-rated opponents |
| 2026-08-24 | 55753519 | 1317.0 | **unknown provenance**; 768 episodes, 30% wins |
| 2026-08-11 | 55418592 | 566.6 | v15: routine feed repriced (peaked 680.5; 371 episodes, 44% wins) |
| 2026-08-08 | 55359336 | 624.0 | v14: opening herd (peaked 697.7) |
| 2026-08-07 | 55335059 | 1232.8 | `main.py`: replay-tape clone of a public notebook (peaked 1358.1) |
| 2026-08-07 | 55334961 | 686.3 | v13b: v13 engine re-submitted |
| 2026-08-06 | 55305466 | 634.8 | v13: travel cost in assignment |
| 2026-08-06 | 55299529 | 621.6 | v12: labour ceiling tuned |
| 2026-08-05 | 55282602 | 616.8 | v11: constraint search (feed gate, pacing, reserve) |
| 2026-08-05 | 55279929 | 624.2 | v10: wheat -> strawberry reallocation |
| 2026-08-05 | 55270663 | 639.4 | v9: v6 mix + weed valuation fix |
| 2026-08-04 | 55244454 | 591.4 | v8: weed clearing priced by replant value |
| 2026-08-04 | 55243224 | 577.8 | v7: search-tuned mix |
| 2026-08-04 | 55226460 | 678.1 | v6: 12 cows / 0 sheep, rate-limited animal buying |
| 2026-08-04 | 55223786 | 596.6 | v5 |
| 2026-08-03 | 55202294 | 625.5 | identical agent to the next row |
| 2026-08-03 | 55202082 | 551.8 | identical agent to the row above (74-point noise) |
| 2026-08-03 | 55200991 | 544.7 | v3 |
| 2026-08-03 | 55200420 | 564.7 | v2 |
| 2026-08-03 | — | 594.6 | v1 |
| 2026-08-03 | — | ERROR | first `main.py`: `__file__` undefined under exec |

**Takeaway**: thirteen versions of the in-repo agent spent 5 weeks between ~545
and ~698. The in-repo line never left the median band.

---

## 5. The in-repo agent (`kagri/`)

A hand-written, stateless heuristic agent. Each turn:

1. `farm.View` parses the observation.
2. `plan.economics()` decides what may be bought: hire target, cash reserve,
   labour ceiling (`workable = units * tiles_per_unit`), wheat/feed gate, herd
   target, land permission, per-crop tile budgets.
3. `farm.plan_layout()` assigns a role to every unlocked tile, busiest roles
   nearest the shed.
4. `tasks.generate()` produces valued jobs: water, harvest, plant, feed, care,
   collect fertiliser, fertilise, dig weeds, build, place animals, shed ferrying.
5. `agent.plan_market()` builds market orders: sells first, emergency feed, hires,
   land, animals (rate-limited), seeds (rate-limited).
6. `agent.assign()` matches units to jobs on `value - travel_cost * distance`.

All tunables live in `kagri/params.py` as a flat dict. Entry point `main.py`
probes `/kaggle_simulations/agent` and falls back to passing on any exception.

Key shipped settings (v15): `max_hands 12`, `tiles_per_unit 6.5`,
`animal_labour_cost 4.0`, `target_cows 12`, `target_sheep 0`, `strawberry_tiles 34`,
`melon_tiles 10`, `wheat_tiles_target 10`, `travel_cost 20`, `open_cows 3`,
`open_sheep 1`, `open_land_hold True`, `feed_routine_mult 0.15`.

---

## 6. Tooling in the repo

| tool | purpose |
|---|---|
| `tools/run.py` | one episode with an end-of-game summary |
| `tools/trace.py` | day-by-day economic trace |
| `tools/gauntlet.py` | offline evaluation: candidates vs 7 opponent archetypes, many seeds, both seats; ranks on **worst matchup** |
| `tools/search.py` | two-stage random search (cheap screen, then full gauntlet) |
| `tools/opening.py` | mechanism probe: animals, escapes, quadrants, money by day |
| `tools/revenue.py` | per-product revenue attribution |
| `tools/arbitrage.py` | closed-form market analysis (round trip, carry trade, fertiliser pot) |
| `tools/tape_board.py` | replays a strong agent's recorded action tape and measures its board |
| `tools/fetch_top.py`, `tools/top_stats.py` | Kaggle API: climb the ladder, collect top teams' episode rewards |

**Environment**: venv at `C:\kenv` (short path avoids Windows MAX_PATH), installed
with `--no-deps`. Run gauntlets with `-j 8` — heavier contention once caused a
`DeadlineExceeded` crash.

**The gauntlet's blind spot**: its "opponents" are the in-repo agent itself with
different tile-mix overrides, reconstructed from mid-ladder players who beat us.
It measures us against our own ideas, never against the real top of the field.

---

## 7. What was learned (all measured)

### Findings that held

- **Tile-mix targets are inert.** Raising `target_cows` 12 -> 20 produced a
  bit-identical game. The labour ceiling and feed gate decide the board. This is
  why v7-v10 (mix tuning) did not move the ladder.
- **Travel cost in assignment** (v13): score jobs on `value - 20 * distance`, with
  a distance tie-break. Gauntlet worst matchup 45% -> 85%.
- **Opening herd** (v14): early livestock was unreachable by construction —
  `can_feed` sized capacity off wheat in the ground (zero on day 0),
  `bootstrap_days` forbade animals for 3 days, and day-0 land spent $1,000 of
  $3,000. Buying 3 cows + 1 sheep on turn 0 with land held back put 4 animals on
  the board by day 2 (previously 0 at day 8). Gauntlet worst 42% -> 75%.
  Ladder peaked 697.7, settled 624.0.
- **Top-of-ladder money** (7 teams rated 3030-3097, 630 games vs >=2500
  opponents, measured 2026-08-11): mean **$87,093**, median $83,920.
- **A strong agent's execution** (1358-rated tape replayed locally): 71 tiles in
  use at day 16 vs our ~30; 1-4 weeds vs our 24-36; action split **50% move /
  43% work / 7% idle** vs ours **66% / 23% / 10%**.

### The correction that reframed everything

The same tape earns **$190,661 against the built-in `starter` bot** and only
**$79,254 against real opponents**. Money against `starter` is a broken proxy:
the market saturates once a competent opponent contests the same pots, and
everyone compresses toward ~$85k. **Producing more is not the win condition;
taking a larger share of contested pots, sooner, is.** Opponent modelling —
their tiles are public, so their melon and strawberry maturity dates are
computable — was identified and never built.

### Findings that did not transfer to the ladder

- **Feed repricing** (v15): routine feeding had been priced at 2x product value,
  draining wheat so rescue feeds for starving animals could not be filled. v14
  lost ~6 animals per game; repricing to 0.15x cut that to ~1.5, and the gauntlet
  said worst matchup 20% -> 48%. **On the ladder v15 settled at 566.6, below
  v14's 624.0.** Real defect, real fix, no ladder gain.

### Unfinished

- **`max_quadrants 3`** (never buy the fourth quadrant): gauntlet 87% ALL / 66%
  worst vs control 75% / 56%. The confirmation run **failed with exit code 4 and
  was never re-run**. Not shipped. Code is uncommitted (see section 10).

---

## 8. Dead ends — do not retry without a new reason

| idea | result |
|---|---|
| copy top player's tile allocation (`mimic-top`) | worst candidate in the search |
| delay land (`land_first_day` 4/6/8) | -42% |
| freeze tile roles | -$30k |
| stable wheat capacity for the herd gate | -$57k |
| metered / withheld selling (two separate mechanisms) | both negative |
| fertilising wheat | negative |
| per-day planting quota | 80% worst vs 90% |
| BFS distances in assignment | net negative |
| unit territories | movement fell, work fell more |
| **hand ramp 3 -> 14 copied from the tape** | **0% worst matchup — worst change ever tested** |
| 6 sheep copied from the tape | 47% worst vs 56% |
| buy feed early (`feed_buy_days` 4 / 8) | 44% / 0% worst |
| land and herd together on day 0 | ~$24 left, animals starve, $32k death spiral |
| 1-cow and 2-cow openings | worse; 2-cow herd starved |
| DROP guard when shed is full | inert — condition never occurs |
| selling at the $1 floor | inert — nothing ever floors |

**Recurring lesson (three times):** copying a stronger player's *build order*
fails; copying their *diagnosis* works. The opening herd succeeded because it
fixed a gate. The hand ramp failed because it transplanted a number.

---

## 9. Methodology rules learned the hard way

1. **Always benchmark against git HEAD**, not a locally modified baseline.
2. **Always swap seats**; seat 0 has a structural advantage.
3. **Rank on worst matchup**, never mean money — the ladder is win/loss.
4. **Ladder noise is about +/-74 points.** Two identical agents scored 551.8 and
   625.5. Do not act on fewer than ~15 episodes.
5. **Gauntlet numbers drift across runs** when a default changes, because the
   opponent archetypes inherit defaults. The same config read 92%/75% one day and
   64%/20% the next. Always include a control in the same batch.
6. **Money vs `starter` does not predict ladder strength** (see section 7).
7. **Gauntlet wins frequently fail to transfer.** v7-v10 and v15 all won offline
   and did not improve the ladder.
8. **Kaggle episode API**: `GetEpisodeReplay` was removed (404s even on episodes
   already downloaded). `ListEpisodes` needs `{"submissionId": N}` (a bare team id
   is rejected), returns rewards and ratings, and throttles hard (HTTP 429) —
   pace requests ~30 seconds apart and checkpoint results.
9. **PowerShell 5.1** wraps native stderr as errors and reports false failures;
   push to git from bash.

---

## 10. Repository state

- Remote: private GitHub repo `homeshwarnelakurthi/Kaggriculture`, branch `master`,
  last commit `abe48ab` (2026-08-11). Local and remote are in sync on commits.
- **Uncommitted since then**: `DEV.md`, `kagri/params.py`, `kagri/plan.py`,
  `tools/gauntlet.py`, new `tools/tape_board.py`. These add `hands_ramp`,
  `hands_day0` and `max_quadrants` parameters, all defaulting to behaviour-
  preserving values (verified bit-identical), plus the tape analysis write-up.
- `DEV.md` is the long-form lab notebook with every experiment and result.

---

## 11. Where this leaves the project with 16 days left

- The in-repo `kagri/` agent peaked at 697.7. The team's current 2278.9 comes from
  submissions of unknown origin. **Identify what those are before doing anything
  else** — they define what "improving" means now.
- **Gap to top 10 is +703.4.** Rank 100 is 2831.5, so even top 100 needs +552.
- The 2026-09-14 submission has only 39 episodes and is still climbing (90% wins
  against weaker opponents so far); its settled rating is not yet known. Give it
  ~24 hours before judging it against the 2026-09-12 one.
- **Any new submission displaces the older active one** (latest 2 rule). With
  both active slots at ~2250-2280, only submit something expected to beat them.
- **Team-merger deadline is 2026-09-23** if merging with another team is under
  consideration.
- Resolve the originality / reproducibility rules question with the hosts before
  2026-09-30 if any active submission derives from public work.
- If work continues on `kagri/`, the only open lead sized like the gap was
  opponent modelling (racing contested pots), which was never built. But at
  peak ~700 vs a ~2,280 team score, it is unlikely to be the fastest path.
