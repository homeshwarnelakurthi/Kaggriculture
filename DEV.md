# Kaggriculture agent — developer notes

## Setup

The environment installs into an isolated venv at `C:\kenv`, **not** into this
folder and **not** into Anaconda base. Two Windows-specific reasons:

- `kaggle-environments` pulls in `orbax`, which ships a test fixture whose path
  is 227 characters. Any venv root longer than ~33 chars breaks `pip` on a
  machine without long-path support enabled.
- pip also unpacks through `%TEMP%`, so that has to be short too.

```bash
python -m venv C:\kenv
C:\kenv\Scripts\python.exe -m pip install --no-deps kaggle-environments kaggle
```

`--no-deps` skips `orbax` entirely; the kaggriculture env does not need it.

Run everything with `C:\kenv\Scripts\python.exe`.

## Commands

```bash
C:/kenv/Scripts/python.exe tools/run.py starter 720 42
```
One episode with an end-of-game summary.

```bash
C:/kenv/Scripts/python.exe tools/trace.py
```
Day-by-day trace: money, hands, tile census, shed. This is the tool that finds
economic bugs — every failure so far showed up as a visible pattern here
(money pinned at a floor, weed count climbing, livestock oscillating).

```bash
C:/kenv/Scripts/python.exe tools/sweep.py --opp mirror -n 24
```
Parallel parameter sweep. Every config plays **both seats** on every seed;
market orders resolve in player order, so seat bias otherwise swamps the
effect being measured. Reports a 95% CI on win rate — at n=16 the noise band
is roughly ±25 points, which is wide enough to invent results that aren't there.

## Strategy in one paragraph

`EGG` and `WHEAT` are the only products whose price curve above equilibrium is
`log`; everything else floors at $1 after a few hundred units. So the farm is an
egg engine: geese in coops, fed by an in-house wheat field, with `FERTILIZER`
sold as a free byproduct (the README claims fertilizer cannot be sold — the
source disagrees, and the installed package agrees with the source). Melon is a
capped side bet worth roughly $26k total, shared with the opponent.

## Hard-won constraints

These are all things that cost a rewrite when violated:

1. **Never spend below the operating reserve.** Broke → no hands → no watering
   → the field rots to weeds → livestock starves. Every early version died here.
2. **Hiring must be gated on a bank *fraction*, not just a floor.** A 13-hand
   crew costs $609/day, which looks affordable against $640 and then bankrupts
   the farm. Without this guard the median final bank was $30.
3. **Cap tile roles by labour, not by land.** A planted tile you cannot water is
   worse than a fallow one: you paid for seed and still owe a `DIG` later.
4. **Logistics must be valued tasks, not idle-unit fallbacks.** With a full
   field no unit is ever idle, so feed never gets fetched and the flock starves.
5. **Size the feed reserve off animals *owned*, not animals *placed*.** Birds
   waiting in the shed still need wheat waiting for them on the day they land.
6. **Reserve carriers.** The one unit holding a $300 goose will otherwise be
   grabbed for the nearest watering job and the bird never reaches its coop.

## Known gaps

- Cows and sheep are not bought at all yet. Their pots are small ($6.3k / $7.8k)
  but nearly free — 1–2 of each is likely worth adding.
- No opponent modelling. Their farm tiles are public, so their melon and
  strawberry maturity dates are computable, and those goods are a race to sell
  before the price floors. This is the biggest unexploited edge in the ruleset.
- Weed clearing and carrot filling still lose the labour auction late-game;
  worth checking whether that is correct or just mispriced.
- `actTimeout` is 1 second/turn with a 60s episode budget. Current agent is far
  under, but any search-based addition has to respect it.

## Gotcha that has bitten twice

`kaggle_environments` inspects an agent's signature and passes
`(observation, configuration)` to anything accepting 2+ args. So this is wrong:

```python
def mine(obs, ov=ov):      # BROKEN: framework passes configuration into `ov`
    return act(obs, ov)
```

The overrides are silently replaced by the env config, every variant runs
identical params, and the sweep looks like it has a bug. Always close over the
overrides with a strictly one-argument agent:

```python
def make_agent(ov):
    def mine(obs):
        return act(obs, ov)
    return mine
```

## Where the real ladder stands (2026-08-03)

Three submissions, all below the 600 start: v1 594.6, v2 564.7, v3 544.7.
Rating fell while absolute money ROSE (v2 mean $35,899 -> v3 $47,978, +34%),
because matchmaking promoted us into a stronger pool: opponent mean went
$41,634 -> $60,011. Both facts are true; the rating alone is misleading.

The top of the ladder runs **strawberry + livestock + fertiliser together**:

    Mikey Marszewski  $154,856   39 strawberry + 9 melon + 8 cow + 6 sheep
    simmons1025        $91,197   35 strawberry + 5 sheep + 5 cow
    naphthalene        $82,128   18 strawberry + 4 sheep + 5 cow

Fertiliser doubles an ongoing crop's yield (strawberry 4 -> 8 units/tile,
$480 -> $960) and animals produce it free, so those three pieces compound.

**We cannot currently express that build.** Measured, 6 seeds vs starter:

    strawberry 0 tiles   $61,929      <- current default
    strawberry 8 tiles   $23,989
    strawberry 10 tiles  $44,555

Strawberry does not merely underperform, it destabilises the allocator: the
day-20 board collapses to carrot filler with the livestock and melon squeezed
out. That is a planner defect, not a parameter to tune. FERTILIZE is
implemented and correct but inert until an ongoing crop exists to use it on.

This is the single biggest known gap and the next thing to fix.

## Why we cannot run the top build (investigated 2026-08-03)

Replayed Mikey Marszewski's $154,856 game turn by turn. Their build order:

    day  2:  11 wheat,  7 melon, 1 sheep, 3 cow      (bank $131)
    day  6:   6 wheat, 10 melon,  2 straw, 4 cow
    day 10:   7 wheat, 11 melon, 16 straw, 6 cow 6 sheep
    day 16:   3 wheat, 10 melon, 39 straw, 8 cow 6 sheep

Both sides hire 12 hands, so labour is NOT the difference (an earlier read of
"they hire zero" was a sampling artifact — `hands` is empty at hour 0, before
hiring resolves; always sample mid-day).

Two real differences:
1. They run 3-11 wheat tiles and BUY the feed shortfall. We run 38. Topping up
   100-200 units costs a few hundred dollars; the "never buy feed" rule priced
   900 units at $40k and over-generalised. Each tile freed is worth ~$960 as
   fertilised strawberry.
2. They sit at $131-689 for ten days, buying seed continuously as cash trickles
   in. Our reserve (~$936 with 14 animals) forbids that entire window.

Ported their allocation directly, 6 seeds vs starter:

    current (ours)                       $60,219
    mikey allocation                      $8,368   (only 3 straw planted;
                                                    24 tiles of carrot filler)
    + carrot_fill off                    $30,688   (30 straw planted — fill WAS
                                                    squatting on the tiles)
    + seed_reserve_frac 0.3              $    24   (death spiral)
    + seed_reserve_frac 0.0              $     4   (death spiral)

Conclusions, all negative and all worth keeping:
- `carrot_fill` genuinely blocks strawberry by occupying tiles it never returns.
- Even with 30 strawberry planted we earn HALF the current build, so our
  strawberry pipeline itself is weak (likely: planted too late for all four
  productions, and unfertilised because the small herd makes little fertiliser).
- The reserve is NOT a conservatism dial. Relaxing it does not buy an aggressive
  opening, it reproduces the original bankruptcy spiral exactly. Any fix has to
  make the opening cheaper, not the guard looser.

Nothing from this investigation was shipped; defaults are unchanged and verified
at $61,929.

## Milk is the biggest uncollected opportunity (diagnosed 2026-08-03, NOT fixed)

Milk is the single largest product in the game: ~438 units of town demand per
season at a $160 base = ~$70k sustainable, and a cow returns ~$208/day for the
same actions and same 1 wheat/day as a $94/day goose.

We collect none of it. Measured on the v5 build, seed 42:

    day   cows  sheep  empty pasture   milk price
      6      0      0              2        190
     14      2      6              1        231
     22      0      5              4        276
     29      0      5              4        325

Milk market inventory ended at -387: the town drained 387 units and NOBODY
supplied any, so price rose from $160 to $331. Four pastures stood empty all
game. At the 8-cow target that is roughly $50k left on the table.

**Mechanism.** `pl.want_animals` is derived from `wheat_flow`, which is derived
from `view.count_plants("WHEAT")` — the count currently IN THE GROUND. Wheat is
a 4-day crop, so that number oscillates between 0 and ~25 as the field rotates.
Every time it dips, the animal target collapses; sheep are filled first, so cows
absorb the entire shortfall. And because the target is `max(animals_now, ...)`,
a starved animal ratchets the target permanently downward.

**Attempted fix that FAILED.** Sizing capacity off allocated wheat tiles instead
of planted count stabilised the target at 6 sheep / 8 cows correctly — and
dropped results from $72,776 to ~$15,400 (6 seeds), regardless of the
feed-purchase setting. Front-loading $2,000 of livestock starves strawberry of
the capital it needs.

**The lesson, now seen three times.** What looks like a conservatism gate is
usually acting as a PACING mechanism. The reserve, the seed budget, and now the
wheat-flow oscillation all turned out to be pacing spend over time. Removing any
of them causes a collapse; the working fix each time is a RATE limit, not a
level change (cf. seed_buy_rate, which is what unlocked strawberry).

**So the real fix is an animal purchase rate limit**, mirroring seed_buy_rate,
combined with the stable capacity measure. Not attempted yet.

Nothing shipped from this investigation; v5 defaults verified restored at
$72,776 mean / $65,624 worst.

## Backlog from the public LB 950+ notebook (2026-08-04, NOT yet implemented)

Source: `romanrozen/strong-statr-baseline-agent-lb-950`, "Barnyard Economist v5".
Publicly shared on Kaggle under rule 2.6b. Insights taken and to be re-derived in
our own design; no code copied.

It independently confirms our town-demand model, melon ripening at day 10, the
$376 twelve-hand cost, and CARE banking daily. It also states that concluding
"play the log products, eggs and wheat" is "exactly backwards, and it cost about
40 000 points" -- the same error this project made and corrected.

**Their coins-per-action table, which indicts our current allocation:**

    melon in-window watering  ~250     we run 10 tiles
    cow fed + cared            ~95
    sheep                      ~86
    COLLECT_FERTILIZER         ~85
    strawberry                 ~37     we run 28 tiles
    wheat                      ~17     we run 16 tiles

We built v5/v6 around the 5th and 6th ranked uses of a tile.

**Four fixes to try, in priority order:**

1. FREEZE THE ROLE MAP. Theirs is a pure function of which quadrants are
   unlocked. Ours recomputes every turn from want_* values that depend on money
   and herd size, so a tile can be melon on day 8 and wheat on day 9 -- the melon
   is then never watered again and rots. This is almost certainly the cause of
   our persistent 43-50 weed tiles, a symptom reported for days without a
   diagnosis. NOTE: they found freezing ALONE made it worse (77k -> 71k) because
   pen tiles sat idle; a self-clearing filler crop (wheat, 4-day cycle) took it
   to 86k. We currently have carrot_fill OFF, so expect to need a filler.
2. NO LAND BEFORE DAY 4 -- put the opening $3,000 into cows. A cow placed day 2
   produces from day 10; land bought day 3 produces nothing until planted. Their
   measured swing: 11k deficit vs the strongest public agent became 2k. Our
   bootstrap_days 3 + min_days_for_animal 8 currently forbids exactly this.
3. PER-DAY PLANTING QUOTA. Ongoing crops decay one day after cumulative
   production hits max_yield, so 45 strawberries planted together all die
   together. Read the quota off the board (planted_day == today), stateless.
4. LIQUIDATION GLIDE PATH. Unsold stock scores zero at day 30; a reservation
   price alone held melons through a crash and dumped at the $1 floor, ~20k lost.
   Force a floor quantity once days_left <= 12.

**Where WE are ahead.** Their closing caveat: "They run cow-heavy herds -- 10 or
11 cows against my 1 cow : 2 sheep mix -- I tried a cow-heavy sequence and it
scored worse in my harness, which I do not yet understand." That is the problem
v6 solved: cow-heavy only works if animal buying is RATE-limited and sheep are
dropped entirely (sheep fill first and steal capital and pasture). v6 runs
12 cows / 0 sheep at 99% ALL / 96% worst matchup.

## Role freeze FAILED (2026-08-04) — drift is not the weed cause

The LB-950 notebook attributes its weeds to a role map that drifts with cash and
herd size, and fixes it by making the map a pure function of unlocked quadrants
plus a self-clearing wheat filler (their 77k -> 71k -> 86k progression).

Implemented behind `freeze_roles`. Measured, 6 seeds vs starter:

    v6 current              $79,475 mean / $71,035 min / 19.5 weeds at d24
    freeze + wheat filler   $50,272 / $43,173 / 24.5 weeds
    freeze, no filler       $48,729 / $39,966 / 19.5 weeds

Both variants lose ~$30k AND the weed count does not improve — it gets worse
with the filler. So our persistent 19-20 weeds are NOT caused by role drift, and
the diagnosis borrowed from that notebook does not transfer to this codebase.
Flag left in place, defaulting False, so this is not re-attempted blind.

Still unexplained: where the weeds actually come from. Worth instrumenting
directly (log every tile that becomes a WEED and what it was the day before)
rather than importing another agent's diagnosis.

Ladder status at time of writing: v6 (12cow/0sheep) 692.6 on 20 episodes, our
best ever; v5 596.6 on 27. Note v6 read 585.5 on 13 episodes a few hours
earlier, BELOW v5's then-657.5, and an apparent pattern of "every winner runs
sheep" in v6's losses did not survive more data. Do not act on <15 episodes.

## v7: mix found by search, not by hand (2026-08-04)

Hand-picked rounds had been sampling a five-dimensional space (cows, sheep,
melon, strawberry, wheat) five points at a time. tools/search.py screens random
constrained mixes cheaply, then runs the full gauntlet on the survivors.

Stage 2, 576 episodes, 6 archetypes, both seats:

    c10s2m10b28w12   100% ALL / 100% worst / $72,181   <- adopted (v7)
    c6s8m14b28w12    100% / 100% / $63,367
    current-v6        99% /  94% / $70,660             <- control
    c4s0m18b34w8      99% /  94% / $65,431

v7 = 10 cow / 2 sheep / 10 melon / 28 strawberry / 12 wheat.
vs starter: $88,762 (v6 was $80,634).

SHEEP ARE NON-MONOTONIC. 0 sheep -> 94% worst, 2 sheep -> 100%, 5 sheep -> 75%.
Do not read "some sheep good" as "more sheep better"; this axis has an interior
optimum and both neighbours are worse.

Also settled this round: the melon-heavy rebalance FAILS. Gauntlet worst-matchup
for m20-c10-s5 42%, m24-c10-s6 38%, m30-c10-s4 0% (against a stockrush). Melon
looks best per action but is the one product the field already floods.

## What the market data actually says (59 real replays, 2026-08-04)

Final market state averaged over 59 real ladder games:

    product      inv vs I0  final $  base  vs base  units sold
    MELON             +89      149    250     60%        229
    FERTILIZER       +161       68    100     68%        161
    CARROT           -399       42     35    120%         34
    WOOL             -279      247    200    124%         56
    EGG              -256       65     50    131%         84
    TOMATO           -337      100     60    167%          3
    WHEAT            -503       47     25    188%        136
    MILK             -327      312    160    195%        111
    STRAWBERRY       -412      289    120    241%        125

Only MELON and FERTILIZER end oversupplied. Melon is the most-produced product
in the game and closes at 60% of base -- that is where the whole field collides,
and it is why every melon-heavy variant fails the gauntlet.

Everything else closes ABOVE base because the town drains faster than two farms
supply. Strawberry at 241% and milk at 195% are exactly what this build sells,
which independently validates the direction.

Answers the "sell cheap goods in bulk" question with data: carrot moved only 34
units all season and still only reached 120% of base. Volume in cheap goods does
not convert, because actions are the constraint, not land.

TOMATO is unfarmed -- 3 units sold across 59 games at 167% of base. But it caps
at 4 lifetime productions for a $50 seed (~$400/tile against strawberry's
~$1,156), so it is uncontested rather than undervalued. Worth one test arm.

CAVEAT: these are our own games, so our production is in the numbers. We run 10
melon and 28 strawberry; strawberry still closes at 241%, so demand dwarfs even
our supply. The melon figure is partly self-inflicted.

## v8: weeds were a VALUATION bug, found by instrumenting (2026-08-04)

Three imported hypotheses had failed first: role drift (-$30k), stable wheat
capacity (-$57k), and "winners run sheep" (noise). Direct measurement settled it
in one run. Logging every tile that became a WEED and what it was the day before,
across 3 games (141 weeds, 47/game):

     57  40.4%  plant died (decay/lifespan)
     49  34.8%  random spawn on EMPTY tile
     33  23.4%  plant died UNWATERED

    top prior states:
     53  STRAWBERRY(unwatered=0, yield=0)   <- exhausted, fully harvested
     27  STRAWBERRY(unwatered=1, yield=0)
     49  EMPTY

**57% of all weeds are spent strawberry tiles.** Strawberry fires exactly 4
productions and then decays to a weed by design. We harvested it dry and left the
corpse all game, because clearing was priced at a flat $35 and lost every labour
auction to milk and egg harvests -- on a tile worth ~$1,156 replanted.

Not a planner defect. A valuation bug. Clearing is now priced as a fraction of
what REPLANTING that tile earns.

    weed_clear_frac   mean $    min $   weeds@d24
    0.15             82,612   75,405        18.8   <- adopted
    1.00             80,740   72,740         1.8
    0.60             80,040   73,078         2.0
    flat $35         77,404   70,350        27.5
    0.30             77,156   61,649         1.3

+$5,208 mean and +$5,055 worst case. Gauntlet: 100% ALL / 100% worst across all
six archetypes, against v7's 98% / 92%.

COUNTERINTUITIVE AND WORTH KEEPING: clearing ALL weeds is WORSE. frac 0.30-1.00
cuts the board to ~2 weeds and earns LESS than 0.15 leaving ~19 standing. A tidy
board is a farm that spent its actions tidying. The weed count was a byproduct
being mistaken for a scoreboard.

## v10 and the finding that matters more than v10 (2026-08-05)

Settled ladder ratings, finally clean:

    v6  678.1 (21 eps)   <- best
    v9  645.3 (21 eps)   <- v6 mix + weed fix; SAME episode count, directly comparable
    v8  583.8 (32 eps)   <- was 604.9 at 12 eps, FELL with more data
    v7  577.8 (30 eps)   <- was 656.2 at 14 eps, FELL with more data

Correction to an earlier claim in this file: v7/v8 reading low was NOT an
episode-count artifact. Both declined as episodes accumulated. Every change
since v6 has failed to beat it on the ladder.

**Why: the parameter space is largely inert.** Measured day-20 boards, 6 seeds:

    v6 exact (wht16 str28)   $74,119 / $64,291 min   10 wheat, 9 melon, 25 straw, 7 cow
    v10      (wht10 str34)   $74,952 / $67,188 min    0 wheat, 8 melon, 27 straw, 7 cow
    v10 + wheat_lead 1       $73,640 / $64,455 min    0 wheat, 8 melon, 27 straw, 7 cow

We ask for 12 cows and get 7. We ask for 34 strawberry and get 27. Moving the
wheat target 16 -> 10 changed the board by TWO tiles. The labour ceiling
(plan.workable) and the feed gate dominate; the tile targets are mostly
requests the clamp overrides.

That is the real explanation for five consecutive tuning attempts producing no
ladder movement -- not gauntlet overfitting, not episode counts. Further mix
search is measuring the clamp, not the strategy.

The next work worth doing is on the CLAMP itself: why 7 cows against a target of
12, and why ~27 tiles of ~91 workable. Not more parameter arms.

v10 = v6 exact + 6 wheat tiles reallocated to strawberry, weed fix reverted
(v9 suggests it costs ~33 points, inside noise but consistent with the trend).

## Two more mechanism fixes measured and REVERTED (2026-08-05)

From the public meta guide (cjlcjlcjl live-meta + Kaito v20). Both sounded right,
neither paid. 6 seeds vs starter:

    v10 baseline        $74,952 / $67,188 min   <- best, kept
    + wheat fertilise   $74,334 / $67,188
    + batch sell only   $74,300 / $66,444
    both                $71,374 / $60,107
    both, batch 5       $74,750 / $64,817

1. WHEAT FERTILISING. The guide is right that wheat cannot reach its 6-unit cap
   on watering alone. But the fertiliser is worth more sold than spent on +2
   wheat units. fertilize_min_gain stays 90, which excludes wheat by a hair.
2. BATCH-METERED SELLING. Second distinct metering mechanism to fail. The first
   withheld below a price floor; this one capped units per order so town demand
   could refill between batches. Both negative. Delay costs more than price
   impact saves -- shed caps at 100 and unsold stock scores zero at day 30.
   Do not propose a third metering scheme without a genuinely new reason.

## REAL-OPPONENT GAUNTLET: copying the top players makes us WORSE

Rebuilt the gauntlet's opponents from the actual day-20 boards of players who
beat us across 30 real losses, replacing archetypes that were all our own agent
with different parameters (that pool had saturated at 100% and stopped
discriminating). 720 episodes, both seats:

    config          starter  mikey  kazuta  somas  josh  yuelin   sam   ALL  worst   mean $
    v9-current         100%    96%     92%   100%  100%    100%  100%   98%    92%  73,368
    v9-lowwheat        100%    88%     79%   100%  100%    100%  100%   95%    79%  74,464
    v9+sheep4          100%    79%     58%   100%  100%    100%  100%   91%    58%  69,680
    mimic-soft         100%    79%     38%   100%  100%    100%  100%   88%    38%  70,363
    mimic-top          100%    54%     58%   100%  100%    100%  100%   88%    54%  68,218

The pool now discriminates (38-92% worst, vs a uniform 100% before).

**mimic-top -- our agent running Mikey/Kazuta's exact allocation (9 cow, 4 sheep,
9 melon, 36 straw, 4 wheat) -- is the WORST candidate tested.** Copying the
board of the strongest player on the ladder makes us measurably worse.

That kills the "just match the top allocation" thesis that drove v7-v10. Their
mix works with their execution; ours cannot run it. Combined with the earlier
finding that tile targets are largely inert under the labour clamp, the
remaining gap is EXECUTION -- actions per day and what they are spent on -- not
allocation.

WARNING: v10 (submitted 2026-08-05) reduced wheat 16 -> 10. v9-lowwheat is the
same direction and scores 79% worst against v9-current's 92%. v10 was shipped
before this run finished and is likely a small regression.

## v11: searching the CONSTRAINTS, not the mix (2026-08-05)

The decisive experiment. Asking for 20 cows instead of 12 produces a
BIT-IDENTICAL game -- same board, same money, to the cent. The tile targets are
requests the clamp overrides; the labour ceiling and the feed gate decide the
board. That is the whole explanation for v7-v10 producing no ladder movement:
five rounds of mix tuning were searching a space that does not exist.

    baseline                        $72,772   27 straw, 8 melon, 7 cow, 18 weed
    MIX: cows 12 -> 20              $72,772   IDENTICAL BOARD
    MIX: straw 34 -> 50             $66,194   board changes, cows collapse to 2
    CONSTRAINT: tiles/unit 7 -> 11  $68,678
    CONSTRAINT: animal cost -> 1.2  $67,883
    CONSTRAINT: feed gate 4 -> 1    $75,578   +$2,806, more straw AND more cows

Repointed tools/search.py at the eight constraint knobs and ran 40 configs
through the two-stage pipeline against REAL-derived opponents.

Winner: wheat_lead_tiles 2, wheat_buffer_per_animal 2.0, seed_buy_rate 2,
animal_buy_rate 2, ops_reserve_base 550, hire_bank_fraction 0.20
(tiles_per_unit and animal_labour_cost unchanged at 7.0 / 2.5).

    Stage 2, real opponents:   100% ALL / 100% worst  vs control 98% / 88%
    vs starter, 8 seeds:       $80,204 mean / $73,412 min  vs $74,464 / $65,011
    day-20 board:              30 straw, 10 melon, 9 cow, 13 weed
                       (was)   27 straw,  8 melon, 7 cow, 18 weed

First change in the project to improve EVERY axis at once -- more strawberry,
more melon, more cows and fewer weeds -- because it lifts the clamp rather than
re-asking for tiles the clamp was refusing.

Correction to the previous entry: v10 was called "likely a small regression" on
gauntlet evidence. The ladder disagreed -- v10 recovered from 582.9 to 635.0,
within 4 points of v9's 639.4. The gauntlet's 79%-vs-92% read did not transfer.

## v12: the labour ceiling (2026-08-06)

v11 relaxed the feed gate and pacing but left tiles_per_unit and
animal_labour_cost untouched -- and those two ARE the ceiling. Searched them
finely while holding v11's winning gate/pacing settings fixed, so the ceiling
was the only thing moving.

Winner: tiles_per_unit 7.0 -> 6.5, animal_labour_cost 2.5 -> 4.0,
hand_value_per_action 6.0 -> 20.0.

Note the DIRECTION: an animal tile costs MORE labour than assumed, not less.
Being honest about that frees the crew to finish crop work rather than spreading
thin across tiles it never returns to. I would have guessed the opposite, which
is exactly why this was searched rather than picked.

Real-opponent gauntlet, 420 episodes, head-to-head on identical seeds:

    config         starter  mikey  kazuta  somas  josh  yuelin   sam   ALL  worst   mean $
    ceiling-win       100%    90%     95%   100%  100%    100%  100%   98%    90%  78,813
    v11-control       100%    60%     85%   100%   65%    100%  100%   87%    60%  72,575
    ceiling-alt       100%    70%     70%   100%   65%    100%  100%   86%    65%  71,797

+30 points of worst matchup and +$6,238 mean.

CAUTION on reading earlier numbers: v11 scored 100%/100% in its own stage-2 run
at 8 seeds, and 87%/60% here at 10 seeds. More seeds pulled it down sharply. So
ceiling-win's 90% is probably optimistic too -- what is trustworthy is the
head-to-head gap on identical seeds, not the absolute figure.

Also: the search's stage 2 CRASHED with DeadlineExceeded (26,081s vs a 1,200s
per-episode limit). That was resource contention -- 12 workers plus leftover
processes from earlier runs -- not a code hang. Episodes run in ~10s. Verified
before submitting, because a hang on Kaggle is a submission ERROR, not a low
score. Use -j 8 when other work is running.

## SESSION HANDOFF � state as of 2026-08-06

If you are a fresh session, read this section and the ## Tuning lessons above
before touching anything.

**Where we are.** Rank ~720/1337 (54th pct). Top-10 needs ~2780.

    v12  just submitted   90% worst matchup vs real opponents (v11 got 60%)
    v11  659.4 (23 eps)   active
    v10  640.8 (22 eps)
    v6   678.1 (21 eps)   INACTIVE -- still the all-time high

**Setup.** venv at C:\kenv (short path deliberately: orbax blows past Windows
MAX_PATH elsewhere). Run everything with C:\kenv\Scripts\python.exe. Install
with --no-deps. GitHub auth works via Windows Credential Manager but pushes are
intermittently slow -- retry once, and push from bash rather than PowerShell
(PowerShell 5.1 wraps native stderr in error records and reports false failures).

**Tools.**
    tools/run.py       one episode + summary
    tools/trace.py     day-by-day economic trace -- finds economic bugs
    tools/gauntlet.py  6 REAL-derived opponent archetypes, both seats
    tools/search.py    two-stage constraint search
Use -j 8 not the default when other work is running; 12 workers plus leftovers
caused a DeadlineExceeded crash.

**The workflow that works.** Every genuine improvement came from either
(a) reading a losing replay and diffing their board against ours, or
(b) instrumenting a specific mechanism directly.
Nothing came from reasoning about the docs, and several imported diagnoses cost
-57k each. When stuck, MEASURE the thing rather than theorising about it.

**Open threads, in the order I would take them:**
1. Joint search over gate + ceiling parameters. v11 fixed the gate then v12
   searched the ceiling with the gate held fixed; their interaction is unsearched.
2. We plant ~30 tiles of ~91 nominally workable. A third of capacity is still
   unused and the reason is not yet known.
3. 35% of weeds are random spawns on EMPTY tiles, which implies significant
   unplanted land -- possibly the same root cause as (2).
4. Opponent modelling. Their farm tiles are public, so melon/strawberry maturity
   is computable and those goods are a race. Never attempted.

## Loss analysis across 72 real games (2026-08-06) � 34W 38L

Money curve, averaged over the 38 games we LOST:

    day    their $    our $      gap    their quads   our quads
      4        382      137     +246           1.3         2.0
      8        651      215     +436           1.6         2.0
     12      6,952    3,280   +3,672           2.6         4.0
     16     13,104    3,880   +9,224           2.7         4.0
     20     25,569   11,376  +14,193           2.8         4.0
     26     53,952   32,987  +20,965           2.8         4.0

The gap explodes between day 12 and 16: they nearly double, we gain 18%.

Board, day 8 (winners vs us):

            COW  SHEEP  STRAW  MELON  WHEAT
    them    2.3    1.1    3.6   10.3    8.1
    us      0.0    0.0    5.9   12.9   22.9

Confirmed on the CURRENT v12 build too: 0 animals until day 12, 29 wheat at
day 8, 4 quadrants by day 12 against their 2.6.

### Both obvious fixes FAILED

1. Let livestock dip into the reserve (nimal_reserve_frac). Animals at day 8
   stayed 0.0 even at frac 0.0 -- NO reserve gate at all. The bank is genuinely
   empty by day 8, not merely gated. frac 0.0 also cost $9k.
2. Delay land so the opening funds livestock (land_first_day), which is both
   the public advice and what the winner boards show. CATASTROPHIC: land>=4, >=6
   and >=8 all score $49,960 against $85,970. A 42% collapse.

**Why the winner profile does not transfer.** We run 12 hands against a ~84-tile
labour ceiling. One quadrant is 25 tiles, so delaying land leaves the crew with
nothing to do. The winners run FEWER tiles with much better per-action
efficiency -- their opening suits their architecture, not ours.

This is now the THIRD time copying the top players has made us worse:
  - mimic-top (their exact tile mix)      -> worst candidate in the gauntlet
  - their low-wheat allocation (v10)      -> 79% worst matchup vs 92%
  - their land timing                     -> -42%

The pattern is consistent enough to state as a rule: **their allocations and
their schedule are outputs of an execution model we do not share. Diff their
boards for WHAT IS POSSIBLE, never for parameters to copy.**

The real difference remains per-action efficiency, not allocation or timing.
