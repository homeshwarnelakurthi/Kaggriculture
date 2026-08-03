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
