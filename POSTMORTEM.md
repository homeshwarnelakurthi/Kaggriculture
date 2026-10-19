# Kaggriculture post-mortem: what we built, what the top built

Final standings read 2026-10-19, after the 2026-09-30 deadline and the ~2026-10-15
ladder convergence. Sources for the "them" side are public notebooks released
under Apache-2.0 on the competition Code tab, credited inline.

---

## 1. Our final result

| | |
|---|---|
| Rank | **1,910 of 10,148** (top 18.8%) |
| Final team score | **1623.2** |
| Top-10 cutoff | **2931.9** (gap **+1,308.7**) |
| #1 | 3314.1 |

Both final active submissions converged on ~1,000 games each:

| ref | eps | win% | our $ | opp $ | our rating |
|---|---|---|---|---|---|
| 56618630 | 996 | 45% | 97,122 | 97,325 | 1,662 |
| 56477819 | 997 | 45% | 97,535 | 98,458 | 1,464 |

**That is the whole result in one line: at convergence we banked the same money as
our opponents and won 45% of games.** Production was never the problem. We were
break-even in a shared market and lost the close games.

### Every high score we celebrated was a small-sample artifact

| agent | peak (few episodes) | converged |
|---|---|---|
| V43 | 2546.9 @ 176 eps | **1407.0** on resubmit |
| 56477819 | 2429.5 @ 162 eps | **1452.6** @ 997 eps |
| replay tape (`main.py`) | 1358.1 @ 6 eps | 1232.8, then decayed |

This project's standing rule was "do not act on <15 episodes". The real threshold
is **several hundred**. On 2026-09-22 I recommended resubmitting V43 to "restore"
2546.9; it converged at 1407.0. A rating is not a property of the file — it is a
property of the field the file climbs through. Two public notebooks containing
**byte-identical** V47 scored 2686.0 and 2579.3 (Tschinkel, lesson 3).

---

## 2. What the top of the ladder actually did

The decisive public artifact is Thomas Tschinkel's **"The 2945 Farm"**
(`thomastschinkel/the-2945-farm-96-vs-the-top-10-public-bots`), which open-sources
the exact file that scored **2944.7**. It beat the ten best public notebooks
**519-21** and still went **0-36 against seven of the top-10 teams**. So there are
two distinct gaps: ours to the public meta, and the public meta's to the top 10.

### 2.1 Architecture: route tape + reflex layers

Not one planner. A **recorded 720-turn action schedule** (where every worker
walks, what is planted, what is sold when), selected by which town shops unlock,
with ~20 thin **reflex layers** stacked on top. Each layer reads the public
observation, edits exactly one kind of decision, and passes the action on.

We wrote a single monolithic greedy task-assigner. Layering is why they could
accumulate dozens of small wins without regressions; our every change moved the
whole agent at once.

### 2.2 The town shops are the demand structure, and we never used them

Shops unlock every 3 days and each consumes one of every product it demands every
4 turns (single-product shops 2x). The entire route-selection decision keys on
the first shop unlocks. yhay81's contribution to the lineage is literally
"Shop Router 0908 / 0909 / 0913".

Our `View` parses `town.unlocked_shops` into `self.shops` and **never reads it
again**. We modelled the town centre's flat drain and ignored the shops.

### 2.3 The opponent's sales are computable from public data

    rival_sold = inventory' - inventory + town_draw - own_sold

Exact above the $1 floor. Their RACE layer watches that signal and pulls its own
planned sales of the same product forward, up to 40 turns, starting day 8.
PREDICT goes further and matches the rival's recent sales against a library of
**451k recorded sale events** to sell just *before* the rival does.

`DEV.md` has carried "No opponent modelling... this is the biggest unexploited
edge in the ruleset" since 2026-08-02. We never built it. It is four terms of
arithmetic.

### 2.4 The market order list is an order book

Both players' market lists run in lockstep by index: order #1 of each side first,
one unit at a time at the same quote, then order #2. So slot position decides who
sells into whose glut. Their ORDERPRI2 estimates the rival's unsold stock from
public info and moves the most-exposed product to slot 1.

**We found this exact mechanism in the engine on 2026-08-11** and wrote it up as
"Order index is a race, and seat 0 wins ties". We never implemented it. Our
`plan_market` sorts sells by `unit * qty * rush` — value, not exposure.

### 2.5 CARE is most of an animal's output

Fed **and** cared every day banks a bonus unit paid at the next production:
a cared cow gives **3 milk** instead of 1, a sheep **4 wool** instead of 1, a
goose **2 eggs** instead of 1.

We priced CARE at `prod_val * 0.9` — barely one unit of product, below most
harvests. Our own memory note said "CARE is worth 2-4x" and the task value never
reflected it. Their CAPHARV layer also harvests an animal whose stored yield
would overflow at tonight's production (+20 / -0 over 1,000 games).

### 2.6 Lifecycle arithmetic we never did

Sheep produce 6 days after placement then every 3 days, and the season ends after
day 29. Placed day 12: produces 18, 21, 24, 27 — four harvests. Placed **day 11**:
17, 20, 23, 26 **and 29** — five. One extra day of feed buys a 25% increase in
wool. Their VE1 layer commits the expansion on day 11 in yarn-store towns.

Symmetrically VT1 stops feeding and caring on day 29 (no production refresh
follows) and skips CARE on day 28 (it would bank after the last production).

### 2.7 Tomato is the hole even they could not fill

Top-10 farms buy ~9 tomato seeds from day ~12 and hold ~10 tomato tiles on day 20,
selling **71 tomatoes at $114**. The 2944 agent buys 1.6 and sells 7 (at $316,
because nobody contests that book). Every tomato program they tried lost, because
the route tape's crew is busy dawn to dusk — a tomato program needs a different
*labour* plan, not a different crop choice.

**We never planted a single tomato.** Our params have no tomato target at all.

### 2.8 Why the top 10 beat even the 2944 agent

Tschinkel's own diagnosis: the top farms **do not replay a tape — they plan the
crew around the crops**. He leads until day 10 (the melon race) and loses it all
after day 11. An adaptive planner taking over after day 12 scored 6-24 against
the tape's 24-6, and a from-scratch demand-driven planner scored 990-1,578 live.
So "be adaptive" is necessary at the top and extremely hard to get right.

---

## 3. Where we were right

Worth recording, because several of our findings match the public meta exactly
and in a few cases we found them first.

| our finding | their independent confirmation |
|---|---|
| 3 cows + 1 sheep opening (v14, read off a tape) | Rayk's cluster table: C = "3 cows + 1 sheep floor", D = "3c+1s" — the two strongest families |
| melon is a fixed pot, dump on sight (`race_products`) | "premium books fall off a cliff, so race" |
| 4th quadrant does not pay (`quad3`: 87%/66% vs 75%/56%) | Rayk section 13: **every** four-quadrant variant lost 10-0; three productive top trajectories lost by 14.6k-37.0k |
| money vs `starter` is a broken proxy | "a bot that prints 100k-170k vs starter can still sit mid-ladder" |
| rank on win/loss, never coin margin | "coin margin is irrelevant for Elo" |
| +/-74 rating noise; identical agents 551.8 vs 625.5 | "+/-100 with matchmaking luck"; identical V47 scored 2686.0 and 2579.3 |
| shed overflow is destroyed at midnight | OVERFLOW/SHEDROOM layers sell at hour 23 exactly what the drop would destroy |

Two stings in that table. **`quad3` was a real, correctly-identified win and we
never shipped it** — the confirmation gauntlet crashed with exit code 4 and was
never re-run. And our **DROP guard measured "inert"** because our build never
filled the shed; theirs does, and they monetise the same mechanic for +16 / -2.

---

## 4. What actually cost us the competition

In rough order of damage.

1. **We built alone.** The entire top of the board is one shared public lineage:
   Tschinkel's Public State Router became the chassis of Ahmed Berat Ozer's
   V25-V48 series, which absorbed yhay81's shop routes, prvsiyan's sheep and
   tomato projects, Dmitrii Gluzdov's stock reservations, and a dozen more. Our
   from-scratch `kagri/` peaked at **698**; the public baseline was 2,600-2,750.
   We were told to watch the Code tab in August and never systematically adopted
   it.
2. **We never modelled the opponent**, despite flagging it as "the biggest
   unexploited edge" on day one. Their RACE/PREDICT/ORDERPRI2 layers are exactly
   that, and the core signal is four terms of arithmetic.
3. **We optimised the wrong objective, twice.** Our gauntlet ranked worst-matchup
   win rate (right) against opponents that were our own agent in different hats
   (wrong, closed room). The later V44-V52 line ranked **coin margin** (wrong
   objective entirely) against the previous version (wrong reference), and
   shipped a 0-wins-in-8-games matchup because it lost by 132 fewer coins.
4. **We trusted ratings on 150-200 episodes.** Every peak evaporated at
   convergence.
5. **We never found the last-callable rule.** Kaggle executes `main.py` and takes
   `[v for v in ns.values() if callable(v)][-1]`. Redefining `agent` later does
   not move it, because a dict keeps a key's original position. This is why
   V48-V50 scored 165.6 (the agent did nothing) and V51 was an "entry-point
   repair". Tschinkel's lesson 1 names it precisely, and notes his own harness
   silently evaluated stale inner bots for every public file from V46 on.
6. **Engine version drift we never checked.** Kaggle's notebook image ships
   `kaggle-environments` 1.29.3, whose Kaggriculture engine is out of date — a
   mirror match of the #1 public agent ends at **$2 per farm** on it and ~$100k
   on 1.32.7. Our local venv is 1.32.2; V43's `build.json` says 1.32.7.

---

## 5. If this were run again

1. **Start from the public lineage on day one.** Fork the strongest public
   notebook, verify it reproduces, and only then add. Treat the Code tab as the
   baseline, not as inspiration.
2. **Build a layered agent.** One file, thin wrappers, each editing one decision.
   Measurable in isolation, revertible individually.
3. **Evaluate head-to-head against reactive opponents, in closed loop, on fresh
   seeds with common random numbers** — never against frozen replays (they
   flatter: their panel rose 589 -> 648 per 1,000 while live went 2956.6 ->
   2944.7) and never against a weak baseline.
4. **Count games flipped, not margin.** `+a / -b` against a fixed anchor.
5. **Model the opponent from public state.** Their tiles, their sales, their
   maturity dates. It is all visible and it decides the premium books.
6. **Do the lifecycle arithmetic** — placement days, production schedules, the
   last two days, shed caps at midnight. Several hundred rating points sit in
   pure counting.
7. **Verify the entry point the way Kaggle loads it**, and pin the engine version.

---

## 6. Credits

The "them" side of this document comes from public Apache-2.0 work, chiefly
Thomas Tschinkel's *The 2945 Farm* and *Public State Router*, and Rayk
Kretzschmar's *Findings from Zero to Top Meta*. Those notebooks in turn credit
Ahmed Berat Ozer (V25-V48), Yusuke Hayashi / yhay81 (shop routers), prvsiyan
(tomato, cattle transfer, six-sheep expansion), Dmitrii Gluzdov (stock
reservations), aurax7, tetsutani, lucifer19, leoprovorov, destbreso, Steven Lee
Hans, and the public V100.24 release. Engine from Kaggle's `kaggle-environments`
(Apache-2.0).
