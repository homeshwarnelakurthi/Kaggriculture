**  
Kaggle · Featured Simulation Competition · 2 months to go**

**Kaggriculture**

Create an agent to play in this farming simulation and compete with others to maximize your income

**Kaggriculture**

**Play in Browser**

**Submit Agent**

**Overview**

In this competition, you will design, build, and deploy an autonomous AI agent to manage a virtual farm, navigate a dynamic economy, and compete head-to-head against other agents on a live leaderboard.

**Start**

3 days ago

**Close**

2 months to go

Merger & Entry

**Description**

This simulation competition is a turn-based farming game where two players compete on separate farms to see who can earn the most profit by the end of a 30-day season (720 turns).

Your agent acts as the main farmer and can strategically hire farm hands to scale up operations. To succeed, your agent must:

- Plant, water, fertilize, and harvest a variety of crops.
- Buy, feed, and care for animals to produce eggs, milk, and wool.
- Collect and utilize fertilizer to boost crop yields.
- Buy neighboring quadrants of land to expand your farm's footprint.
- Trade smart on a dynamic market where prices react to your sales and town demand.

Kaggriculture represents a highly complex environment that models the exact same dynamics found in real-world supply chains, dynamic market pricing, and industrial resource allocation under uncertainty. Underlying mechanics like scheduling resources, optimizing labor, adjusting to supply/demand price changes, and making long-horizon capital investments, serve as a high-fidelity sandbox for training AI to solve complex enterprise operations.

**Timeline**

- **July 29, 2026** - Start Date.
- **September 23, 2026** - Entry Deadline. You must accept the competition rules before this date in order to compete.
- **September 23, 2026** - Team Merger Deadline. This is the last day participants may join or merge teams.
- **September 30, 2026** - Final Submission Deadline.
- **October 1, 2026 to (approx) October 15, 2026** - We will continue to run games, or until the leaderboard has reached convergence. At the conclusion of this period, the leaderboard is final.

All deadlines are at 11:59 PM UTC on the corresponding day unless otherwise noted. _The competition organizers reserve the right to update the contest timeline if they deem it necessary._

**Evaluation**

Each day your team is able to submit up to 5 agents (bots) to the competition. Each submission will play Episodes (games) against other bots on the ladder that have a similar skill rating. Over time, skill ratings will go up with wins or down with losses, and even out with ties. To reduce the number of bots playing and ensure high-quality matching, only the latest 2 submissions are tracked. The latest 2 submissions are also used for final leaderboard evaluation.

Every bot submitted will continue to play episodes until the end of the competition, with newer bots playing a much more frequent number of episodes. On the leaderboard, only your best-scoring bot will be shown, but you can track the progress of all of your submissions on your Submissions page.

When you upload a submission, a **Validation Episode** is run where your agent plays against a copy of itself to ensure it runs without errors. If the episode fails, the submission is marked as Error, and you can download the agent logs to debug. Otherwise, the submission is initialized with a default rating and joins the matchmaking pool.

**Ranking System**

Each submission is assigned a skill rating. When your agent plays an episode against an opponent:

- Winning the match (having the most coins in the bank at the end of 720 turns) increases your skill rating, while losing decreases it.
- The amount your rating changes depends on the rating difference between you and your opponent. Beating a highly-rated agent will boost your rating more than beating a lower-rated one.
- Ties will generally pull ratings closer together.
- The actual coin difference in a match does not affect the rating change—only the win, loss, or tie outcome matters.

**Final Evaluation**

At the submission deadline, additional submissions will be locked. Games will continue to run for approximately two weeks to continue to reduce uncertainty, especially for new agents. A final Bradley-Terry tournament will be run on those episodes to produce the final leaderboard.

**Prizes**

- 1st Place - $5,000
- 2nd Place - $5,000
- 3rd Place - $5,000
- 4th Place - $5,000
- 5th Place - $5,000
- 6th Place - $5,000
- 7th Place - $5,000
- 8th Place - $5,000
- 9th Place - $5,000
- 10th Place - $5,000

**How to Play**

**Overview**

Each player starts with an empty farm and a small amount of income (seed money, if you will). Each turn, they can perform actions such as moving around the board, purchasing seeds or livestock, planting seeds, watering plants, harvesting produce or animal products, and selling that produce at the market. The game runs for a fixed amount of time representing one season, and the winner is determined by who has the most money in the bank at the end.

**Object Types**

| **Type** | **Yield Type** | **Seed Cost** | **Base Market Price** | **Time to First Yield** | **Time to Max Yield** | **Subsequent Yields** | **Max Yield** | **Action Cost** | **Max yield / tile / DAY** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Wheat** | One-time | 10  | 25  | 2 days | 4 days | none | 6   | 1   | 1.5 |
| **Carrot** | One-time | 20  | 35  | 2 days | 3 days | none | 4   | 1   | 1.333 |
| **Tomato** | Ongoing | 50  | 60  | 8 days | NA  | every day | 4   | 1   | 4   |
| **Strawberry** | Ongoing | 100 | 120 | 10 days | NA  | every other day | 4   | 1   | 2   |
| **Melon** | One-time | 80  | 250 | 10 days | 12 days | none | 6   | 1   | .5  |
| **Goose/Egg** | Ongoing | 300 | 50  | 4 days | NA  | every day | 4   | 1 + 1 (build coop) | 2   |
| **Cow/Milk** | Ongoing | 400 | 160 | 8 days | NA  | every two days | 6   | 1 + 1 (build pasture) | 1   |
| **Sheep/Wool** | Ongoing | 500 | 200 | 6 days | NA  | every three days | 6   | 1 + 1 (build pasture) | .67 |
| **Fertilizer** | NA  | 100 | X   |     | X   | X   |     | 1   |     |

All plants must be watered every day. They will turn into weeds if they are not watered for two successive days. All animals must be fed every day using wheat. They will escape and be unrecoverable if they are not fed for two successive days. Wheat is also available to buy at the market and can be purchased at the current market price.

**Actions**

Each turn, the player may take one action. There are 24 turns per day, and 30 days in the season - 720 total turns.

**Farmer / Farm Hand Action**

Each Farmer / Farm Hand can be given an action every turn. Farmer/Farm Hand CAN occupy the same space.

**Movement**

- NORTH, SOUTH, EAST, WEST — Move one cell in that direction

**Shed**

Picks up an item from the shed (must be orthogonally adjacent) into the inventory

- PICKUP &lt;item&gt; \[n\] — move up to n of &lt;item&gt; (default 1) from the shed into the active farmer/hand's inventory. Any item present in the shed is valid (animals, fertilizer, harvested produce, etc.). Seeds live in a separate slot and are never picked up — PLANT consumes them directly.
- DROP — orthogonally adjacent to the shed, dump the active farmer/hand's entire current inventory into the shed. Overflow past shedCapacity is discarded. No-op if not shed-adjacent.

**Plants**

- PLANT — Plant a seed purchased from the market  
    - Seeds are automatically available to all Farmers / Farm Hands
    - If you try to plant too many in a specific turn, none are planted
    - ie if you have 1 melon seed, but two units do the PLANT MELON command
- WATER — Water a plant. This only needs to be done once per day, and subsequent waterings on the same day are a no-op.
- HARVEST — Gather produce from a plant. If the plant does not have subsequent yields, it will be removed from the map. Each harvest action will yield at least one unit of the crop, with the potential of additional yield depending on watering and fertilizer (the formula differs by crop type — see harvest yields below). Harvested items are added to the inventory.
- FERTILIZE — Fertilize a plant to increase its potential yield (see harvest yields below).  
    - Doubles the per-day yield bonus for the next 3 days. The bonus only applies on days the plant is also watered (basic needs first).

**Animals**

- PLACE &lt;item&gt; \[n\] — Drop items from the active farmer/hand inventory into either a tile or the shed:  
    - **Animal placement**: standing on a matching unoccupied structure (GOOSE on a coop, SHEEP/COW on a pasture) places one animal from inventory onto the tile. The n argument is ignored.
    - **Shed drop**: standing orthogonally adjacent to the shed moves up to n (default 1) of &lt;item&gt; from inventory into the shed. Capped by shedCapacity; excess stays in inventory.
- FEED — Feed an animal using wheat (only needs to be done once per day)
- HARVEST — Collect the eggs/milk/wool produced by the animal.
- COLLECT_FERTILIZER — Collect 1 fertilizer from the animal. Each surviving animal makes 1 fertilizer available at the end of every day; collecting consumes that day's stock and the next becomes available after the next end-of-day refresh.
- CARE — Care for an animal (once per day, no-op if already cared for). See animal care below.

**Animal Care**

CARE banks a yield bonus that is paid out on the animal's next scheduled production:

- At end of day, if the animal was both fed AND cared for that day, pending_care_bonus increments by 2. Days where the animal was unfed do not bank a bonus (basic needs first).
- On a scheduled production day, if the animal is fed, the entire banked bonus is added to that production's yield (in addition to the base 1) and the bank resets to 0.
- If the animal is unfed on the production day, no yield is produced that day and the bank is also reset.
- pending_care_bonus is capped indirectly by the per-animal max_held cap on yield_units.

**Terrain**

- BUILD_COOP - adds a coop to an unoccupied tile
- BUILD_PASTURE - add pasture to an unoccupied tile
- DIG — Remove a plant from a square to free up space OR remove a weed from a square (does not yield any produce) OR remove a goose coop / pasture.

**Other**

- PASS — Default if there is nothing to do (optional)

**Market Action**

Each turn you can submit up to maxMarketOrdersPerTurn (default 10) market actions; any orders past that limit are silently dropped. This is an ordered list and market orders will be processed in order simultaneously (one from each player) while both players have orders.

- BUY_SEED — Purchase N units of a single item from the market.  
    - BUY_SEED WHEAT 1
- BUY_ANIMAL -  
    - BUY_ANIMAL GOOSE 1
- BUY_PRODUCT  
    - BUY_PRODUCT WHEAT 1
    - BUY_PRODUCT FERTILIZER 1
- SELL — Sell N units of a single item to the market.  
    - SELL WHEAT 1
- HIRE — Hire a farm hand for the day. Cost increases for each extra hand hired on the same day.
- BUY_LAND - unlock a new 5x5 segment of land to plant on. Increasing in cost.  
    - Costs are: $1k, $2k, $4k

**Watering / Animal Feed**

Plants (and animals) must be watered/fed a minimum of every other day. Watering only needs to be done once per day, and subsequent watering actions are a no-op. In the case of plants not watered for two consecutive days, at the end of the day they turn into a WEED. In the case of animals they escape (unrecoverable).

Note that watering one-time yield plants during their yield window results in a higher yield. This is NOT true for ongoing yield plants/animals. See below.

**Harvest Yields**

Plants will potentially have higher yields based on how well they have been cared for.

- **One-time crops** (wheat, carrot, melon): Starting at half the plant's max_yield_day (Time to Max Yield) rounded up, watering during the bonus window will add one unit per day to the total harvestable yield.  
    - Fertilized plants add 2 per day instead.
- **Ongoing crops** (tomato, strawberry): Scheduled production happens at fixed intervals. The base yield is 1 per scheduled production. If the plant is fertilized AND watered that day, yield is doubled to 2.
- Once a plant has hit its maximum lifespan, the total yield available on the plant will reduce by 1 every other turn until it hits 0, at which point the plant becomes a weed.
    - **One-time crops** reach max lifespan one day after max_yield_day.
    - **Ongoing crops** start decay one day after their cumulative production count reaches max_yield (i.e. they've fired enough scheduled productions to hit the cap, regardless of whether the produce has been harvested).

**Map Features**

Each player has their own farm with a set number of squares. Players are unable to see the state of the other’s shed, but can see the state of their opponent’s farm.

**Farm Space**

- The land near your farm is a boardSize × boardSize grid (default 10×10), divided into four 5×5 quadrants. At first, your farm covers one quadrant (25% of the squares). For an increasingly large fee, you can buy the neighboring quadrants and eventually cover 100% of the squares.
- Each plant or animal occupies one square on the farm.
- Players can allocate these squares however they choose between crops and livestock. There are no specific limits per type.
- Weeds have a chance of spawning on any empty cells on the farm, and must be cleared before the land can be used for other purposes.
- Squares on the farm can be either a plant, a coop/pasture, a weed, or empty.

**Shed (Inventory)**

- Functions as an inventory for items that are harvested but not yet sold, or for seeds that have not yet been planted
- Farmer and hired farm hands will spawn at the shed at the start of each day
- Farmer and hired farm hands drop their inventory at the end of the day in the shed (if there is room)
- Limited to 100 items, excluding seeds. Once the shed is full, any further items added (via PLACE mid-day or end-of-day inventory drop) are discarded — there is no overflow holding area, so stockpiling on farmer/hand inventories does not bypass the cap.

**Farmer/Farm Hand**

**Hiring**

- Hiring is a market order (HIRE). It costs more every time you want to hire an additional hand each day. At the end of the day all, hands drop inventory at the farm and disappear (need to be re-hired each day)
- Cost is farmHandCostMult \* fib(n) where n is the number of hires already made today (fib starts 1, 1, 2, 3, 5, 8, 13, …).  
    - With the default farmHandCostMult = 1: 1, 1, 2, 3, 5, 8, 13, 21, etc… (resets at the start of each day)
- A hired hand appears orthogonally adjacent to the shed in a free space following NWSE. If there are not open spaces, it looks for the one with the least occupants, breaking ties by NWSE preference

**Inventory**

- When harvesting or picking items up, they are added to inventory.
- Can drop items in the shed
- At the end of the day, all items in all inventory will be added to shed inventory (if there is room). Anything that doesn't fit is discarded — overflow is lost.

**Town Buildings**

As the season progresses, new shops unlock at regular intervals (every townShopUnlockInterval days, default 3). Each unlock is randomly selected from the shops that have not yet been added; once unlocked, a shop stays active for the rest of the game. Total demand grows monotonically as more shops unlock.

Each unlocked shop consumes one of every product it demands every townShopSellInterval turns (default 4). So with the default interval, a shop demanding wheat removes 6 wheat from the market per day. Single-product shops consume 2x.

In addition, the town center consumes one of every product (excluding fertilizer) every townCenterSellInterval turns (default 12). After day 10 this is increased to 2 of each, and after day 20 it is increased to 4 of each.

| **Shop Type** | **Increases Demand For** |
| --- | --- |
| Bakery | eggs, wheat |
| Pizza Shop | milk, tomatoes, wheat |
| Brunch Spot | eggs, wheat, strawberries |
| Yarn Store | wool (2x) |
| Ice Cream Shop | strawberries, milk, wheat |
| Pet Cafe | carrots (2x) |
| Smoothie Shop | strawberries, milk |
| Farmers Market | wheat, carrots, tomatoes, strawberries |

**Market Mechanics**

The market has an unlimited supply of seeds and animals at fixed prices. Sell prices, however, move dynamically per resource and persist across days.

Every product (and fertilizer) starts the game with a market inventory of I0 = 10,000 units, far above any single game's realistic production volume so that inventory is essentially guaranteed to stay positive. The sell price for a product is base at I0, rises as inventory falls (players buying or town consumption draining supply), and falls as inventory grows (players selling).

**Selling inventory to the market**

Players can queue any number of sell or buy orders (for any quantity) in the market action list. Orders are processed concurrently across players, one unit at a time. For example, when both players issue SELL CARROT 10 first, we take the current carrot price, give both players that price for their first carrot, then add 2 carrots to the market (1 from each player) — which may shift the price — and repeat until both orders complete.

If the sell price has been driven down to $1 (the price floor), the unit is still purchased but is _not_ added to market inventory, so the floor remains responsive to subsequent buys.

**Buying inventory from the market**

Only WHEAT and FERTILIZER can be bought from the market via BUY_PRODUCT (other products are sold at the market but not bought back). Two things drain market inventory: town buildings (town center and shops, which consume products for free) and player BUY_PRODUCT orders. Buy orders follow the same one-unit-at-a-time concurrent procedure as sell orders. If a player runs out of money mid-order, the order is stopped.

The buy price is quoted at the post-buy inventory and the sell price is quoted at the pre-sell inventory, so an immediate buy followed by a sell of the same item against an otherwise-unchanged market nets exactly zero.

**The Price Function**

For each resource the curve is defined by a base price, an anchor throughput T, and an independent **shape function** + **target move** for each side of the equilibrium:

price(inv) = base + sign · amp · f(|inv − I0|)

sign = +1 if inv < I0 (scarcity → price up)

sign = −1 if inv > I0 (glut → price down)

amp = target · base / f(T) (derived; not stored)

f ∈ { linear, sq, sqrt, log, log10 } (log uses ln(1+x), so f(0)=0)

Floored at $1 and rounded to the nearest dollar.

T is the production capacity of a single 5×5 field over a 24-day game at optimal watering with no fertilizer (animal totals are pre-discounted by 30% to account for wheat-feed overhead). target says "moving T units past I0 shifts the price by target × base." Picking different f and target on each side lets resources with similar production profiles play very differently strategically — wheat panics on scarcity but absorbs gluts, carrot is the opposite; melon barely reacts to scarcity but crashes hard on overproduction; wool mirrors melon at a smaller scale. Premium resources (base > $100: strawberry, melon, milk, wool) use above_target > 1, so even modest gluts drive them straight to the $1 floor — bundling and timing sales matters more for these than for staples.

| **Resource** | **Base** | **I0** | **T** | **Below func** | **Below target** | **Above func** | **Above target** | **P(I0−T)** | **P(I0+T)** | **P(I0+2T)** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Wheat** | 25  | 10,000 | 400 | sqrt | 0.80 | log | 0.20 | $45 | $20 | $19 |
| **Carrot** | 35  | 10,000 | 450 | log | 0.20 | sqrt | 0.70 | $42 | $10 | $1  |
| **Tomato** | 60  | 10,000 | 200 | linear | 0.40 | sqrt | 0.60 | $84 | $24 | $9  |
| **Strawberry** | 120 | 10,000 | 100 | sqrt | 0.70 | linear | 1.60 | $204 | $1  | $1  |
| **Melon** | 250 | 10,000 | 300 | log | 0.20 | sq  | 3.60 | $300 | $1  | $1  |
| **Egg** | 50  | 10,000 | 332 | linear | 0.40 | log | 0.20 | $70 | $40 | $39 |
| **Milk** | 160 | 10,000 | 122 | sqrt | 0.60 | linear | 1.60 | $256 | $1  | $1  |
| **Wool** | 200 | 10,000 | 105 | log | 0.20 | sq  | 3.20 | $240 | $1  | $1  |
| **Fertilizer** | 100 | 10,000 | 200 | linear | 0.40 | linear | 0.40 | $140 | $60 | $20 |

The defaults live in MARKET_PARAMS in kaggriculture.py. Per-resource overrides (sparse: any subset of base, I0, T, below_func, below_target, above_func, above_target) can be supplied at episode creation via env.configuration\["marketParams"\] without touching code, e.g. {"WOOL": {"above_target": 0.95}}.

**Turn Processing Order**

1.  **Action validation** — verify action legality
2.  **Player actions** — record the actions taken by each player (happening simultaneously)
3.  **Market actions** - process market queue in order by player (described above)
4.  **Town buy actions** - town center and shops reduce inventory
5.  **Update observations**  
    - **Day refresh** — if applicable, update the condition of plants and animals for a new day, and reset their fed/watered to condition to false
    - **Market refresh** — modify the price of items on the market based on sells from previous turn
    - **Income update** — update the player’s bank based on any buys or sells
    - **Farm update** — clear plants that have been harvested, items from the inventory that have been used or sold, add new plants/animals to the farm, etc

**Win Conditions**

The win condition is simple- whoever has the greatest number of coins at the end of the season is the winner. It is also possible that the two players will tie.

**Reward**

The player who has the most money in the bank at the end of the game wins. Unsold items in the inventory do not count towards that total.

**Observation Format**

The top-level observation passed to each agent:

{

"player": int, # 0 or 1

"day": int, # 0-indexed in-game day

"hour": int, # 0-indexed turn within the day

"farms": \[farm, farm\], # public per-player state, indexed by player id (shared)

"market": { # shared

"inventory": { "WHEAT": int, "CARROT": int, ... },

"prices": { "WHEAT": int, "CARROT": int, ... },

},

"town": { # shared

"unlocked_shops": \["BAKERY", ...\],

},

"private": { # this player only; opponent's private state is not visible

"shed": { "WHEAT": int, "GOOSE": int, "FERTILIZER": int, ... },

"seeds": { "WHEAT": int, "CARROT": int, ... },

"inventories": \[farmer_inv, hand_inv, ...\], # \[0\] is the main farmer

},

}

Each farm dict (public, visible to both players):

{

"money": float,

"tiles": \[\[tile, ...\], ...\], # tiles\[y\]\[x\]

"farmer": \[x, y\],

"hands": \[\[x, y\], ...\], # hired hands for the current day

"unlocked_quadrants": \["NW", ...\], # subset of {"NW","NE","SW","SE"}

"hires_today": int, # used to price the next HIRE

}

A tile is one of:

- None — empty unlocked tile
- "LOCKED" — tile in a quadrant the player has not yet bought
- a plant dict:

{

"kind": "PLANT",

"crop": "WHEAT" | "CARROT" | "TOMATO" | "STRAWBERRY" | "MELON",

"planted_day": int,

"watered_today": bool, # reset to False each end-of-day

"consecutive_unwatered": int, # 2+ → tile turns to a weed

"yield_units": int, # units currently harvestable

"max_lifespan_step": int, # step at which decay begins; -1 for ongoing crops

"fertilized_until_day": int, # last day fertilizer bonus applies; -1 if none

}

- a weed dict: {"kind": "WEED"}
- an animal structure dict (coop/pasture, optionally occupied):

{

"kind": "COOP" | "PASTURE",

"animal": "GOOSE" | "COW" | "SHEEP" | None, # None until PLACEd

"placed_day": int,

"yield_units": int,

"fed_today": bool,

"consecutive_unfed": int, # 2+ → animal escapes

"cared_today": bool,

"fertilizer_available": bool, # set after CARE; cleared by COLLECT_FERTILIZER

"pending_care_bonus": int, # banked CARE bonus, applied on the next yield tick

}

**Quick Start**

from kaggle_environments import make

def my_agent(obs):

\# Buy one wheat seed on the very first turn, then PASS forever after.

if obs.get("step", 0) == 0:

return {"farmer": \["PASS"\], "market": \[\["BUY_SEED", "WHEAT", 1\]\]}

return {"farmer": \["PASS"\], "market": \[\]}

env = make("kaggriculture", configuration={"episodeSteps": 200})

env.run(\[my_agent, "random"\])

env.render(mode="ipython", width=800, height=800)

**Configuration Defaults**

Per-crop seed costs and per-product base prices are not configurable; they are documented in the Object Types and Price Function tables above. The configurable knobs are:

| **Parameter** | **Default** | **Description** |
| --- | --- | --- |
| episodeSteps | 720 | Total turns in the season (24 turns × 30 days) |
| boardSize | 10  | Width and height (in tiles) of each player's square farm. Advanced uses 10 = four 5x5 quadrants |
| startingMoney | 3000 | Coins each player starts with |
| maxMarketOrdersPerTurn | 10  | Maximum number of market orders processed per player per turn; extras are silently dropped |
| turnsPerDay | 24  | Number of turns that make up one in-game day |
| shedCapacity | 100 | Max non-seed items the shed can hold; overflow at end-of-day drop is discarded |
| weedSpawnChance | 0.005 | Per-tile probability of a weed spawning on an empty unlocked tile during end-of-day refresh |
| townShopUnlockInterval | 3   | Days between successive town shop unlocks |
| townShopSellInterval | 4   | Turns between consumption ticks by every unlocked town shop |
| townCenterSellInterval | 12  | Turns between consumption ticks by the town center |
| seed | null | Optional input seed for deterministic episode generation; cleared from config after read so it stays out of agent observations |

**Getting Started: Test Locally & Submit**

This guide walks you through building an agent, testing it locally, and submitting it to this simulation competition.

**Test Locally**

Install the environment from PyPI (any recent release that includes Kaggriculture):

pip install -U kaggle-environments

Run a game from Python or a notebook — you can pass agent functions directly, or paths to .py files:

from kaggle_environments import make

env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)

env.run(\[agent, "random"\]) # or env.run(\["main.py", "random"\]) to load from a file

\# View result

final = env.steps\[-1\]

for i, s in enumerate(final):

print(f"Player {i}: reward={s.reward}, status={s.status}")

\# Render in a notebook

env.render(mode="ipython", width=1200, height=800)

\# Or dump a replay JSON for the visualizer / offline analysis

import json

with open("replay.json", "w") as f:

json.dump(env.toJSON(), f)

Three built-in agents are available by name: "pass", "random", and "starter" (a deterministic baseline).

**Set Up the Kaggle CLI**

Install the CLI:

pip install kaggle

You'll need a Kaggle account — sign up at [https://www.kaggle.com](https://www.kaggle.com/) if you don't have one. Then download your API credentials at https://www.kaggle.com/settings/api by clicking **"Generate New Token"** under the "API" section.

**Recommended: API token file.** Save the token string to ~/.kaggle/access_token:

mkdir -p ~/.kaggle

\# Paste the token from the Kaggle settings UI into this file

nano ~/.kaggle/access_token

chmod 600 ~/.kaggle/access_token

Alternative auth methods:

- **OAuth (browser flow):** kaggle auth login
- **Environment variable:** export KAGGLE_API_TOKEN=xxxxxxxxxxxxxx

Verify the CLI is wired up:

kaggle competitions list -s "kaggriculture"

**Find the Competition**

kaggle competitions list -s "kaggriculture"

kaggle competitions pages kaggriculture

kaggle competitions pages kaggriculture --content

**Accept the Competition Rules**

Before submitting, you **must** accept the rules on the Kaggle website. Navigate to https://www.kaggle.com/competitions/kaggriculture and click **"Join Competition"**.

Verify you've joined:

kaggle competitions list --group entered

**Download Competition Data**

kaggle competitions download kaggriculture -p kaggriculture-data

**Submit Your Agent**

Your submission must have a main.py at the root with an agent function.

**Single file agent:**

kaggle competitions submit kaggriculture -f main.py -m "Wheat loop v1"

**Multi-file agent** — bundle into a tar.gz with main.py at the root:

tar -czf submission.tar.gz main.py helper.py model_weights.pkl

kaggle competitions submit kaggriculture -f submission.tar.gz -m "Multi-file agent v1"

**Notebook submission:**

kaggle competitions submit kaggriculture -k YOUR_USERNAME/kaggriculture-agent -f submission.tar.gz -v 1 -m "Notebook agent v1"

**Monitor Your Submission**

Check submission status:

kaggle competitions submissions kaggriculture

Note the submission ID from the output — you'll need it for episodes.

**List Episodes**

Once your submission has played some games:

kaggle competitions episodes &lt;SUBMISSION_ID&gt;

CSV output for scripting:

kaggle competitions episodes &lt;SUBMISSION_ID&gt; -v

**Download Replays and Logs**

Download the replay JSON for an episode (for visualization or analysis):

kaggle competitions replay &lt;EPISODE_ID&gt;

kaggle competitions replay &lt;EPISODE_ID&gt; -p ./replays

Download agent logs to debug your agent's behavior:

\# Logs for the first agent (index 0)

kaggle competitions logs &lt;EPISODE_ID&gt; 0

\# Logs for the second agent (index 1)

kaggle competitions logs &lt;EPISODE_ID&gt; 1 -p ./logs

**Check the Leaderboard**

kaggle competitions leaderboard kaggriculture -s

**Typical Workflow**

\# Test locally

python -c "

from kaggle_environments import make

env = make('kaggriculture', debug=True)

env.run(\['main.py', 'random'\])

print(\[(i, s.reward) for i, s in enumerate(env.steps\[-1\])\])

"

\# Submit

kaggle competitions submit kaggriculture -f main.py -m "v1"

\# Check status

kaggle competitions submissions kaggriculture

\# Review episodes

kaggle competitions episodes &lt;SUBMISSION_ID&gt;

\# Download replay and logs

kaggle competitions replay &lt;EPISODE_ID&gt;

kaggle competitions logs &lt;EPISODE_ID&gt; 0

\# Check leaderboard

kaggle competitions leaderboard kaggriculture -s

**Quick Start Agent**

Below is a simple starter agent implementing a basic wheat loop:

def agent(obs):

player = obs\["player"\]

me = obs\["farms"\]\[player\]

private = obs\["private"\]

fx, fy = me\["farmer"\]

tile = me\["tiles"\]\[fy\]\[fx\]

market = \[\]

\# Buy a wheat seed if we have none and have enough money

if private\["seeds"\].get("WHEAT", 0) == 0 and me\["money"\] >= 10:

market.append(\["BUY_SEED", "WHEAT", 1\])

\# Sell any wheat sitting in the shed

wheat_in_shed = private\["shed"\].get("WHEAT", 0)

if wheat_in_shed > 0:

market.append(\["SELL", "WHEAT", wheat_in_shed\])

\# If standing on an empty tile, plant wheat

if tile is None and private\["seeds"\].get("WHEAT", 0) > 0:

return {"farmer": \["PLANT", "WHEAT"\], "hands": \[\], "market": market}

\# If standing on a plant, manage watering and harvesting

if isinstance(tile, dict) and tile.get("kind") == "PLANT":

crop_age = obs\["day"\] - tile\["planted_day"\]

if crop_age >= 2: # Wheat first_yield_day = 2

return {"farmer": \["HARVEST"\], "hands": \[\], "market": market}

if not tile\["watered_today"\]:

return {"farmer": \["WATER"\], "hands": \[\], "market": market}

return {"farmer": \["PASS"\], "hands": \[\], "market": market}

**Frequently Asked Questions**

**Submissions**

- Submissions must be at most **100 MiB**
- Daily submission limit **5**
- Only your most recent **2** are active
- Your files will be located in /kaggle_simulations/agent/. Ensure all your file imports are set appropriately

**Submission Resources**

- HDD Space: **8 GiB**
- RAM: **6.5 GiB**
- vCPUs: **1.6**
- Submission Size Limit: **100 MiB**

For questions about the environment OS or python env, please see:

- [Docker Image](https://github.com/Kaggle/kaggle-environments/blob/master/docker/Dockerfile)

**Citation**

Bovard Doerschuk-Tiberi, Domino Weir, and María Cruz. Kaggriculture. https://kaggle.com/competitions/kaggriculture, 2026. Kaggle.

**Cite**

**Competition Host**

Kaggle

**Prizes & Awards**

$50,000

Awards Points & Medals

**Participation**

1,581 Entrants

600 Participants

586 Teams

1,071 Submissions

**Tags**

[Simulations](https://www.kaggle.com/competitions?tagIds=16151-Simulations)

Custom Metric

**Table of Contents**

**  
Kaggle · Featured Simulation Competition · 2 months to go**

**Play in Browser**

**Submit Agent**

**Kaggriculture**

Create an agent to play in this farming simulation and compete with others to maximize your income

**Dataset Description**

This is the folder for the Python kit. Please make sure to read the instructions as they are important regarding how you will write a bot and submit it to the competition.

For kits in other languages please see this example from the [Lux AI Challenge Github repository](https://github.com/Lux-AI-Challenge/Lux-Design-S3)

**Files**

2 files

**Size**

34.97 kB

**Type**

md

**License**

[Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)

**README.md**(21.92 kB)

**Kaggriculture**

A farming sim where two players compete to maximize their income from farming by selling to a dynamic market.

**Overview**

Each player starts with an empty farm and a small amount of income (seed money, if you will). Each turn, they can perform actions such as moving around the board, purchasing seeds or livestock, planting seeds, watering plants, harvesting produce or animal products, and selling that produce at the market. The game runs for a fixed amount of time representing one season, and the winner is determined by who has the most money in the bank at the end.

**Object Types**

| **Type** | **Yield Type** | **Seed Cost** | **Base Market Price** | **Time to First Yield** | **Time to Max Yield** | **Subsequent Yields** | **Max Yield** | **Action Cost** | **Max yield / tile / DAY** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Wheat** | One-time | 10  | 25  | 2 days | 4 days | none | 6   | 1   | 1.5 |
| **Carrot** | One-time | 20  | 35  | 2 days | 3 days | none | 4   | 1   | 1.333 |
| **Tomato** | Ongoing | 50  | 60  | 8 days | NA  | every day | 4   | 1   | 4   |
| **Strawberry** | Ongoing | 100 | 120 | 10 days | NA  | every other day | 4   | 1   | 2   |
| **Melon** | One-time | 80  | 250 | 10 days | 12 days | none | 6   | 1   | .5  |
| **Goose/Egg** | Ongoing | 300 | 50  | 4 days | NA  | every day | 4   | 1 + 1 (build coop) | 2   |
| **Cow/Milk** | Ongoing | 400 | 160 | 8 days | NA  | every two days | 6   | 1 + 1 (build pasture) | 1   |
| **Sheep/Wool** | Ongoing | 500 | 200 | 6 days | NA  | every three days | 6   | 1 + 1 (build pasture) | .67 |
| **Fertilizer** | NA  | 100 | X   |     | X   | X   |     | 1   |     |

All plants must be watered every day. They will turn into weeds if they are not watered for two successive days. All animals must be fed every day using wheat. They will escape and be unrecoverable if they are not fed for two successive days. Wheat is also available to buy at the market and can be purchased at the current market price.

**Actions**

Each turn, the player may take one action. There are 24 turns per day, and 30 days in the season - 720 total turns.

**Farmer / Farm Hand Action**

Each Farmer / Farm Hand can be given an action every turn. Farmer/Farm Hand CAN occupy the same space.

**Movement**

- NORTH, SOUTH, EAST, WEST — Move one cell in that direction

**Shed**

Picks up an item from the shed (must be orthogonally adjacent) into the inventory

- PICKUP &lt;item&gt; \[n\] — move up to n of &lt;item&gt; (default 1) from the shed into the active farmer/hand's inventory. Any item present in the shed is valid (animals, fertilizer, harvested produce, etc.). Seeds live in a separate slot and are never picked up — PLANT consumes them directly.
- DROP — orthogonally adjacent to the shed, dump the active farmer/hand's entire current inventory into the shed. Overflow past shedCapacity is discarded. No-op if not shed-adjacent.

**Plants**

- PLANT — Plant a seed purchased from the market  
    - Seeds are automatically available to all Farmers / Farm Hands
    - If you try to plant too many in a specific turn, none are planted
    - ie if you have 1 melon seed, but two units do the PLANT MELON command
- WATER — Water a plant. This only needs to be done once per day, and subsequent waterings on the same day are a no-op.
- HARVEST — Gather produce from a plant. If the plant does not have subsequent yields, it will be removed from the map. Each harvest action will yield at least one unit of the crop, with the potential of additional yield depending on watering and fertilizer (the formula differs by crop type — see harvest yields below). Harvested items are added to the inventory.
- FERTILIZE — Fertilize a plant to increase its potential yield (see harvest yields below).  
    - Doubles the per-day yield bonus for the next 3 days. The bonus only applies on days the plant is also watered (basic needs first).

**Animals**

- PLACE &lt;item&gt; \[n\] — Drop items from the active farmer/hand inventory into either a tile or the shed:  
    - **Animal placement**: standing on a matching unoccupied structure (GOOSE on a coop, SHEEP/COW on a pasture) places one animal from inventory onto the tile. The n argument is ignored.
    - **Shed drop**: standing orthogonally adjacent to the shed moves up to n (default 1) of &lt;item&gt; from inventory into the shed. Capped by shedCapacity; excess stays in inventory.
- FEED — Feed an animal using wheat (only needs to be done once per day)
- HARVEST — Collect the eggs/milk/wool produced by the animal.
- COLLECT_FERTILIZER — Collect 1 fertilizer from the animal. Each surviving animal makes 1 fertilizer available at the end of every day; collecting consumes that day's stock and the next becomes available after the next end-of-day refresh.
- CARE — Care for an animal (once per day, no-op if already cared for). See animal care below.

**Animal Care**

CARE banks a yield bonus that is paid out on the animal's next scheduled production:

- At end of day, if the animal was both fed AND cared for that day, pending_care_bonus increments by 2. Days where the animal was unfed do not bank a bonus (basic needs first).
- On a scheduled production day, if the animal is fed, the entire banked bonus is added to that production's yield (in addition to the base 1) and the bank resets to 0.
- If the animal is unfed on the production day, no yield is produced that day and the bank is also reset.
- pending_care_bonus is capped indirectly by the per-animal max_held cap on yield_units.

**Terrain**

- BUILD_COOP - adds a coop to an unoccupied tile
- BUILD_PASTURE - add pasture to an unoccupied tile
- DIG — Remove a plant from a square to free up space OR remove a weed from a square (does not yield any produce) OR remove a goose coop / pasture.

**Other**

- PASS — Default if there is nothing to do (optional)

**Market Action**

Each turn you can submit up to maxMarketOrdersPerTurn (default 10) market actions; any orders past that limit are silently dropped. This is an ordered list and market orders will be processed in order simultaneously (one from each player) while both players have orders.

- BUY_SEED — Purchase N units of a single item from the market.  
    - BUY_SEED WHEAT 1
- BUY_ANIMAL -  
    - BUY_ANIMAL GOOSE 1
- BUY_PRODUCT  
    - BUY_PRODUCT WHEAT 1
    - BUY_PRODUCT FERTILIZER 1
- SELL — Sell N units of a single item to the market.  
    - SELL WHEAT 1
- HIRE — Hire a farm hand for the day. Cost increases for each extra hand hired on the same day.
- BUY_LAND - unlock a new 5x5 segment of land to plant on. Increasing in cost.  
    - Costs are: $1k, $2k, $4k

**Watering / Animal Feed**

Plants (and animals) must be watered/fed a minimum of every other day. Watering only needs to be done once per day, and subsequent watering actions are a no-op. In the case of plants not watered for two consecutive days, at the end of the day they turn into a WEED. In the case of animals they escape (unrecoverable).

Note that watering one-time yield plants during their yield window results in a higher yield. This is NOT true for ongoing yield plants/animals. See below.

**Harvest Yields**

Plants will potentially have higher yields based on how well they have been cared for.

- **One-time crops** (wheat, carrot, melon): Starting at half the plant's max_yield_day (Time to Max Yield) rounded up, watering during the bonus window will add one unit per day to the total harvestable yield.  
    - Fertilized plants add 2 per day instead.
- **Ongoing crops** (tomato, strawberry): Scheduled production happens at fixed intervals. The base yield is 1 per scheduled production. If the plant is fertilized AND watered that day, yield is doubled to 2.
- Once a plant has hit its maximum lifespan, the total yield available on the plant will reduce by 1 every other turn until it hits 0, at which point the plant becomes a weed.
    - **One-time crops** reach max lifespan one day after max_yield_day.
    - **Ongoing crops** start decay one day after their cumulative production count reaches max_yield (i.e. they've fired enough scheduled productions to hit the cap, regardless of whether the produce has been harvested).

**Map Features**

Each player has their own farm with a set number of squares. Players are unable to see the state of the other’s shed, but can see the state of their opponent’s farm.

**Farm Space**

- The land near your farm is a boardSize × boardSize grid (default 10×10), divided into four 5×5 quadrants. At first, your farm covers one quadrant (25% of the squares). For an increasingly large fee, you can buy the neighboring quadrants and eventually cover 100% of the squares.
- Each plant or animal occupies one square on the farm.
- Players can allocate these squares however they choose between crops and livestock. There are no specific limits per type.
- Weeds have a chance of spawning on any empty cells on the farm, and must be cleared before the land can be used for other purposes.
- Squares on the farm can be either a plant, a coop/pasture, a weed, or empty.

**Shed (Inventory)**

- Functions as an inventory for items that are harvested but not yet sold, or for seeds that have not yet been planted
- Farmer and hired farm hands will spawn at the shed at the start of each day
- Farmer and hired farm hands drop their inventory at the end of the day in the shed (if there is room)
- Limited to 100 items, excluding seeds. Once the shed is full, any further items added (via PLACE mid-day or end-of-day inventory drop) are discarded — there is no overflow holding area, so stockpiling on farmer/hand inventories does not bypass the cap.

**Farmer/Farm Hand**

**Hiring**

- Hiring is a market order (HIRE). It costs more every time you want to hire an additional hand each day. At the end of the day all, hands drop inventory at the farm and disappear (need to be re-hired each day)
- Cost is farmHandCostMult \* fib(n) where n is the number of hires already made today (fib starts 1, 1, 2, 3, 5, 8, 13, …).  
    - With the default farmHandCostMult = 1: 1, 1, 2, 3, 5, 8, 13, 21, etc… (resets at the start of each day)
- A hired hand appears orthogonally adjacent to the shed in a free space following NWSE. If there are not open spaces, it looks for the one with the least occupants, breaking ties by NWSE preference

**Inventory**

- When harvesting or picking items up, they are added to inventory.
- Can drop items in the shed
- At the end of the day, all items in all inventory will be added to shed inventory (if there is room). Anything that doesn't fit is discarded — overflow is lost.

**Town Buildings**

As the season progresses, new shops unlock at regular intervals (every townShopUnlockInterval days, default 3). Each unlock is randomly selected from the shops that have not yet been added; once unlocked, a shop stays active for the rest of the game. Total demand grows monotonically as more shops unlock.

Each unlocked shop consumes one of every product it demands every townShopSellInterval turns (default 4). So with the default interval, a shop demanding wheat removes 6 wheat from the market per day. Single-product shops consume 2x.

In addition, the town center consumes one of every product (excluding fertilizer) every townCenterSellInterval turns (default 12). After day 10 this is increased to 2 of each, and after day 20 it is increased to 4 of each.

| **Shop Type** | **Increases Demand For** |
| --- | --- |
| Bakery | eggs, wheat |
| Pizza Shop | milk, tomatoes, wheat |
| Brunch Spot | eggs, wheat, strawberries |
| Yarn Store | wool (2x) |
| Ice Cream Shop | strawberries, milk, wheat |
| Pet Cafe | carrots (2x) |
| Smoothie Shop | strawberries, milk |
| Farmers Market | wheat, carrots, tomatoes, strawberries |

**Market Mechanics**

The market has an unlimited supply of seeds and animals at fixed prices. Sell prices, however, move dynamically per resource and persist across days.

Every product (and fertilizer) starts the game with a market inventory of I0 = 10,000 units, far above any single game's realistic production volume so that inventory is essentially guaranteed to stay positive. The sell price for a product is base at I0, rises as inventory falls (players buying or town consumption draining supply), and falls as inventory grows (players selling).

**Selling inventory to the market**

Players can queue any number of sell or buy orders (for any quantity) in the market action list. Orders are processed concurrently across players, one unit at a time. For example, when both players issue SELL CARROT 10 first, we take the current carrot price, give both players that price for their first carrot, then add 2 carrots to the market (1 from each player) — which may shift the price — and repeat until both orders complete.

If the sell price has been driven down to $1 (the price floor), the unit is still purchased but is _not_ added to market inventory, so the floor remains responsive to subsequent buys.

**Buying inventory from the market**

Only WHEAT and FERTILIZER can be bought from the market via BUY_PRODUCT (other products are sold at the market but not bought back). Two things drain market inventory: town buildings (town center and shops, which consume products for free) and player BUY_PRODUCT orders. Buy orders follow the same one-unit-at-a-time concurrent procedure as sell orders. If a player runs out of money mid-order, the order is stopped.

The buy price is quoted at the post-buy inventory and the sell price is quoted at the pre-sell inventory, so an immediate buy followed by a sell of the same item against an otherwise-unchanged market nets exactly zero.

**The Price Function**

For each resource the curve is defined by a base price, an anchor throughput T, and an independent **shape function** + **target move** for each side of the equilibrium:

price(inv) = base + sign · amp · f(|inv − I0|)

sign = +1 if inv < I0 (scarcity → price up)

sign = −1 if inv > I0 (glut → price down)

amp = target · base / f(T) (derived; not stored)

f ∈ { linear, sq, sqrt, log, log10 } (log uses ln(1+x), so f(0)=0)

Floored at $1 and rounded to the nearest dollar.

T is the production capacity of a single 5×5 field over a 24-day game at optimal watering with no fertilizer (animal totals are pre-discounted by 30% to account for wheat-feed overhead). target says "moving T units past I0 shifts the price by target × base." Picking different f and target on each side lets resources with similar production profiles play very differently strategically — wheat panics on scarcity but absorbs gluts, carrot is the opposite; melon barely reacts to scarcity but crashes hard on overproduction; wool mirrors melon at a smaller scale. Premium resources (base > $100: strawberry, melon, milk, wool) use above_target > 1, so even modest gluts drive them straight to the $1 floor — bundling and timing sales matters more for these than for staples.

| **Resource** | **Base** | **I0** | **T** | **Below func** | **Below target** | **Above func** | **Above target** | **P(I0−T)** | **P(I0+T)** | **P(I0+2T)** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Wheat** | 25  | 10,000 | 400 | sqrt | 0.80 | log | 0.20 | $45 | $20 | $19 |
| **Carrot** | 35  | 10,000 | 450 | log | 0.20 | sqrt | 0.70 | $42 | $10 | $1  |
| **Tomato** | 60  | 10,000 | 200 | linear | 0.40 | sqrt | 0.60 | $84 | $24 | $9  |
| **Strawberry** | 120 | 10,000 | 100 | sqrt | 0.70 | linear | 1.60 | $204 | $1  | $1  |
| **Melon** | 250 | 10,000 | 300 | log | 0.20 | sq  | 3.60 | $300 | $1  | $1  |
| **Egg** | 50  | 10,000 | 332 | linear | 0.40 | log | 0.20 | $70 | $40 | $39 |
| **Milk** | 160 | 10,000 | 122 | sqrt | 0.60 | linear | 1.60 | $256 | $1  | $1  |
| **Wool** | 200 | 10,000 | 105 | log | 0.20 | sq  | 3.20 | $240 | $1  | $1  |
| **Fertilizer** | 100 | 10,000 | 200 | linear | 0.40 | linear | 0.40 | $140 | $60 | $20 |

The defaults live in MARKET_PARAMS in kaggriculture.py. Per-resource overrides (sparse: any subset of base, I0, T, below_func, below_target, above_func, above_target) can be supplied at episode creation via env.configuration\["marketParams"\] without touching code, e.g. {"WOOL": {"above_target": 0.95}}.

**Turn Processing Order**

1.  **Action validation** — verify action legality
2.  **Player actions** — record the actions taken by each player (happening simultaneously)
3.  **Market actions** - process market queue in order by player (described above)
4.  **Town buy actions** - town center and shops reduce inventory
5.  **Update observations**  
    - **Day refresh** — if applicable, update the condition of plants and animals for a new day, and reset their fed/watered to condition to false
    - **Market refresh** — modify the price of items on the market based on sells from previous turn
    - **Income update** — update the player’s bank based on any buys or sells
    - **Farm update** — clear plants that have been harvested, items from the inventory that have been used or sold, add new plants/animals to the farm, etc

**Win Conditions**

The win condition is simple- whoever has the greatest number of coins at the end of the season is the winner. It is also possible that the two players will tie.

**Reward**

The player who has the most money in the bank at the end of the game wins. Unsold items in the inventory do not count towards that total.

**Observation Format**

The top-level observation passed to each agent:

{

"player": int, # 0 or 1

"day": int, # 0-indexed in-game day

"hour": int, # 0-indexed turn within the day

"farms": \[farm, farm\], # public per-player state, indexed by player id (shared)

"market": { # shared

"inventory": { "WHEAT": int, "CARROT": int, ... },

"prices": { "WHEAT": int, "CARROT": int, ... },

},

"town": { # shared

"unlocked_shops": \["BAKERY", ...\],

},

"private": { # this player only; opponent's private state is not visible

"shed": { "WHEAT": int, "GOOSE": int, "FERTILIZER": int, ... },

"seeds": { "WHEAT": int, "CARROT": int, ... },

"inventories": \[farmer_inv, hand_inv, ...\], # \[0\] is the main farmer

},

}

Each farm dict (public, visible to both players):

{

"money": float,

"tiles": \[\[tile, ...\], ...\], # tiles\[y\]\[x\]

"farmer": \[x, y\],

"hands": \[\[x, y\], ...\], # hired hands for the current day

"unlocked_quadrants": \["NW", ...\], # subset of {"NW","NE","SW","SE"}

"hires_today": int, # used to price the next HIRE

}

A tile is one of:

- None — empty unlocked tile
- "LOCKED" — tile in a quadrant the player has not yet bought
- a plant dict:

{

"kind": "PLANT",

"crop": "WHEAT" | "CARROT" | "TOMATO" | "STRAWBERRY" | "MELON",

"planted_day": int,

"watered_today": bool, # reset to False each end-of-day

"consecutive_unwatered": int, # 2+ → tile turns to a weed

"yield_units": int, # units currently harvestable

"max_lifespan_step": int, # step at which decay begins; -1 for ongoing crops

"fertilized_until_day": int, # last day fertilizer bonus applies; -1 if none

}

- a weed dict: {"kind": "WEED"}
- an animal structure dict (coop/pasture, optionally occupied):

{

"kind": "COOP" | "PASTURE",

"animal": "GOOSE" | "COW" | "SHEEP" | None, # None until PLACEd

"placed_day": int,

"yield_units": int,

"fed_today": bool,

"consecutive_unfed": int, # 2+ → animal escapes

"cared_today": bool,

"fertilizer_available": bool, # set after CARE; cleared by COLLECT_FERTILIZER

"pending_care_bonus": int, # banked CARE bonus, applied on the next yield tick

}

**Quick Start**

from kaggle_environments import make

def my_agent(obs):

\# Buy one wheat seed on the very first turn, then PASS forever after.

if obs.get("step", 0) == 0:

return {"farmer": \["PASS"\], "market": \[\["BUY_SEED", "WHEAT", 1\]\]}

return {"farmer": \["PASS"\], "market": \[\]}

env = make("kaggriculture", configuration={"episodeSteps": 200})

env.run(\[my_agent, "random"\])

env.render(mode="ipython", width=800, height=800)

**Configuration Defaults**

Per-crop seed costs and per-product base prices are not configurable; they are documented in the Object Types and Price Function tables above. The configurable knobs are:

| **Parameter** | **Default** | **Description** |
| --- | --- | --- |
| episodeSteps | 720 | Total turns in the season (24 turns × 30 days) |
| boardSize | 10  | Width and height (in tiles) of each player's square farm. Advanced uses 10 = four 5x5 quadrants |
| startingMoney | 3000 | Coins each player starts with |
| maxMarketOrdersPerTurn | 10  | Maximum number of market orders processed per player per turn; extras are silently dropped |
| turnsPerDay | 24  | Number of turns that make up one in-game day |
| shedCapacity | 100 | Max non-seed items the shed can hold; overflow at end-of-day drop is discarded |
| weedSpawnChance | 0.005 | Per-tile probability of a weed spawning on an empty unlocked tile during end-of-day refresh |
| townShopUnlockInterval | 3   | Days between successive town shop unlocks |
| townShopSellInterval | 4   | Turns between consumption ticks by every unlocked town shop |
| townCenterSellInterval | 12  | Turns between consumption ticks by the town center |
| seed | null | Optional input seed for deterministic episode generation; cleared from config after read so it stays out of agent observations |

**Data Explorer**

34.97 kB

- AGENTS.md
- README.md

**Summary**

2 files

**Download All**

**Metadata**

**License**

[Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)

**  
Kaggle · Featured Simulation Competition · 2 months to go**

**Play in Browser**

**Submit Agent**

**Kaggriculture**

Create an agent to play in this farming simulation and compete with others to maximize your income

**Notebooks**

**New Notebook**

**Filters**

**Kaggle Frontier Lab | Strategy Improvement**

Updated 4h agoScore: 2351 · [0 comments](https://www.kaggle.com/code/prvsiyan/kaggle-frontier-lab-strategy-improvement/comments) · Kaggriculture

**44**

&nbsp;Silver

**🌾🚜Kaggriculture: Night Harvest**

Updated 3h agoScore: 979.4 · [2 comments](https://www.kaggle.com/code/lucifer19/kaggriculture-night-harvest/comments) · Kaggriculture

**30**

&nbsp;Bronze

**Kaggriculture | Hamburger 🍔**

Updated 3h agoScore: 2515.1 · [0 comments](https://www.kaggle.com/code/romantamrazov/kaggriculture-hamburger/comments) · Kaggriculture

**51**

&nbsp;Silver

**kaggriculture-agent-builder**

Updated 16h agoScore: 1771.3 · [0 comments](https://www.kaggle.com/code/degnonguidi/kaggriculture-agent-builder/comments) · Kaggriculture

**42**

&nbsp;Bronze

**Kaggriculture: Scenario-Aware Economic Policy**

Updated 2h agoScore: 1279.6 · [1 comment](https://www.kaggle.com/code/pilkwang/kaggriculture-scenario-aware-economic-policy/comments) · Kaggriculture

**69**

&nbsp;Silver

**Kaggriculture v1**

Updated 8h ago[0 comments](https://www.kaggle.com/code/blacklions/kaggriculture-v1/comments) · Kaggriculture

**3**

**Kaggriculture v14 Public Experiment**

Updated 4h ago[0 comments](https://www.kaggle.com/code/blacklions/kaggriculture-v14-public-experiment/comments) · Kaggriculture

**1**

**Kaggriculture v12 Public Experiment**

Updated 4h ago[0 comments](https://www.kaggle.com/code/blacklions/kaggriculture-v12-public-experiment/comments) · Kaggriculture

**1**

**Kaggriculture Agent**

Updated 8h agoScore: 1443.7 · [0 comments](https://www.kaggle.com/code/emanuellcs/kaggriculture-agent/comments) · Kaggriculture

**5**

**Kaggriculture | Adaptive Replay Agent**

Updated 8h agoScore: 1485.1 · [0 comments](https://www.kaggle.com/code/flexonafft/kaggriculture-adaptive-replay-agent/comments) · Kaggriculture

**2**

**🌾Adaptive Farming Strategy for Kaggriculture**

Updated 15h agoScore: 1536.4 · [0 comments](https://www.kaggle.com/code/tetsutani/adaptive-farming-strategy-for-kaggriculture/comments) · Kaggriculture

**7**

&nbsp;Bronze

**Wide-Sigma CMA Tuned Scenario-Aware (submitted)**

Updated 17h agoScore: 1314.4 · [0 comments](https://www.kaggle.com/code/pengwang91/wide-sigma-cma-tuned-scenario-aware-submitted/comments) · Kaggriculture

**6**

&nbsp;Bronze

**🌾 Kaggriculture Baseline**

Updated 11h agoScore: 321.1 · [0 comments](https://www.kaggle.com/code/pavloivanin/kaggriculture-baseline/comments) · Kaggriculture

**14**

&nbsp;Bronze

**Kaggriculture v15 Public Experiment**

Updated 2h ago[0 comments](https://www.kaggle.com/code/blacklions/kaggriculture-v15-public-experiment/comments) · Kaggriculture

**0**

**Kaggriculture Frontier | The Moon Counts Melons**

Updated 3h ago[0 comments](https://www.kaggle.com/code/prvsiyan/kaggriculture-frontier-the-moon-counts-melons/comments) · Kaggriculture

**1**

**Kaggriculture Frontier | The Soil Remembers Rain**

Updated 3h ago[0 comments](https://www.kaggle.com/code/prvsiyan/kaggriculture-frontier-the-soil-remembers-rain/comments) · Kaggriculture

**1**

**Kaggriculture v11 Public Experiment**

Updated 4h ago[0 comments](https://www.kaggle.com/code/blacklions/kaggriculture-v11-public-experiment/comments) · Kaggriculture

**1**

**Kaggriculture v9 Public Experiment**

Updated 4h ago[0 comments](https://www.kaggle.com/code/blacklions/kaggriculture-v9-public-experiment/comments) · Kaggriculture

**1**

**KAGGRICULTURE- BEST-SCORE**

Notebook copied with edits from [renji_starfall](https://www.kaggle.com/code/degnonguidi/kaggriculture-agent-builder) · Updated 14h agoScore: 1583.5 · [0 comments](https://www.kaggle.com/code/navazshfathi/kaggriculture-best-score/comments) · Kaggriculture

**2**

**Kaggriculture: Findings from Zero to Top Meta**

Updated 1d agoScore: 1323.8 · [0 comments](https://www.kaggle.com/code/raykkretzschmar/kaggriculture-findings-from-zero-to-top-meta/comments) · Kaggriculture

**5**

**  
Kaggle · Featured Simulation Competition · 2 months to go**

**Play in Browser**

**Submit Agent**

**Kaggriculture**

Create an agent to play in this farming simulation and compete with others to maximize your income

**Discussion**

**FollowNew Topic**

**Filters**

Pinned topics

**Comment on the final evaluation for this competition**

[María Cruz](https://www.kaggle.com/macruzbar) · Posted 2d ago

**7**

**How to get started + Competition's Official Discord**

[María Cruz](https://www.kaggle.com/macruzbar) · Last [comment](https://www.kaggle.com/competitions/kaggriculture/discussion/730708#3506572) 2d ago by Ahmed Jendoubi, Ph.D.

**3**

3 comments

**Daily Top Episodes Dataset**

[Bovard Doerschuk-Tiberi](https://www.kaggle.com/bovard) · Posted 3d ago

**6**

All other topics

**Hard to rl**

[hwe owe](https://www.kaggle.com/hweowe) · Posted 10h ago

**1**

**\[Problem\] Too many requests to ListEpisodes**

[Ali](https://www.kaggle.com/asalhi) · Last [comment](https://www.kaggle.com/competitions/kaggriculture/discussion/732114#3507687) 11h ago by SeshuRaju 🧘‍♂️

**1**

4 comments

**Did anyone else think of board games?**

[Kaito Fukami](https://www.kaggle.com/kaitofukami) · Last [comment](https://www.kaggle.com/competitions/kaggriculture/discussion/732129#3507553) 14h ago by robga

**2**

1 comment

**Why Opponents Matter: Shared-Market Dynamics (English Diagram)**

[MakiMakiAi](https://www.kaggle.com/makimakiai) · Posted 1d ago

**0**

**A few rule questions for the organizers**

[Triston Morgan](https://www.kaggle.com/yanzhou06) · Posted 1d ago

**4**

**Query on Submission Resources**

[harshraj22](https://www.kaggle.com/harshraj22) · Last [comment](https://www.kaggle.com/competitions/kaggriculture/discussion/731810#3507013) 2d ago by mikelou1

**0**

1 comment

**Bug: Hired hands can spawn on locked land and get stuck**

[Victor Mercklé](https://www.kaggle.com/vmerckle) · Last [comment](https://www.kaggle.com/competitions/kaggriculture/discussion/731635#3506710) 2d ago by Bovard Doerschuk-Tiberi

**3**

1 comment

**Seat swap did not move my bot's bank (6 seeds, both seats)**

[Georgy Mamarin](https://www.kaggle.com/georgymamarin) · Last [comment](https://www.kaggle.com/competitions/kaggriculture/discussion/731152#3506697) 2d ago by Sakhawat Hossen

**\-9**

4 comments

**\[Guide\] A Reproducible Evaluation Checklist for Kaggriculture Agents**

[yw8837](https://www.kaggle.com/yw8837) · Posted 2d ago

**0**

**  
Kaggle · Featured Simulation Competition · 2 months to go**

**Play in Browser**

**Submit Agent**

**Kaggriculture**

Create an agent to play in this farming simulation and compete with others to maximize your income

You have accepted the rules for this competition. Good luck!

**Competition Rules**

**ENTRY IN THIS COMPETITION CONSTITUTES YOUR ACCEPTANCE OF THESE OFFICIAL COMPETITION RULES.**

[**See Section 3.18 for defined terms**](https://www.kaggle.com/competitions/kaggriculture/rules#18.-terms)

_The Competition named below is a skills-based competition to promote and further the field of data science. You must register via the Competition Website to enter. To enter the Competition, you must agree to these Official Competition Rules, which incorporate by reference the provisions and content of the Competition Website and any Specific Competition Rules herein (collectively, the "Rules"). Please read these Rules carefully before entry to ensure you understand and agree. You further agree that Submission in the Competition constitutes agreement to these Rules. You may not submit to the Competition and are not eligible to receive the prizes associated with this Competition unless you agree to these Rules. These Rules form a binding legal agreement between you and the Competition Sponsor with respect to the Competition. Your competition Submissions must conform to the requirements stated on the Competition Website. Your Submissions will be scored based on the evaluation metric described on the Competition Website. Subject to compliance with the Competition Rules, Prizes, if any, will be awarded to Participants with the best scores, based on the merits of the data science models submitted. See below for the complete Competition Rules. For Competitions designated as hackathons by the Competition Sponsor (“Hackathons”), your Submissions will be judged by the Competition Sponsor based on the evaluation rubric set forth on the Competition Website (“Evaluation Rubric”). The Prizes, if any, will be awarded to Participants with the highest ranking(s) as determined by the Competition Sponsor based on such rubric._

**You cannot sign up to Kaggle from multiple accounts and therefore you cannot enter or submit from multiple accounts.**

**1\. COMPETITION-SPECIFIC TERMS**

**1\. COMPETITION TITLE**

Kaggriculture

**2\. COMPETITION SPONSOR**

Google LLC

**3\. COMPETITION SPONSOR ADDRESS**

1600 Amphitheatre Parkway, Mountain View, CA 94043

**4\. COMPETITION WEBSITE**

https://www.kaggle.com/competitions/kaggriculture

**5\. TOTAL PRIZES AVAILABLE: $50,000**

First Prize: $5,000  
Second Prize: $5,000  
Third Prize: $5,000  
Fourth Prize: $5,000  
Fifth Prize: $5,000  
Sixth Prize: $5,000  
Seventh Prize: $5,000  
Eight Prize: $5,000  
Ninth Prize: $5,000  
Tenth Prize: $5,000

**6\. WINNER LICENSE TYPE**

CC-BY 4.0

**7\. DATA ACCESS AND USE**

Apache 2.0

**2\. COMPETITION-SPECIFIC RULES**

In addition to the provisions of the General Competition Rules below, you understand and agree to these Competition-Specific Rules required by the Competition Sponsor:

**1\. TEAM LIMITS**

a. The maximum Team size is five (5). b. Team mergers are allowed and can be performed by the Team leader. In order to merge, the combined Team must have a total Submission count less than or equal to the maximum allowed as of the Team Merger Deadline. The maximum allowed is the number of Submissions per day multiplied by the number of days the competition has been running. For Hackathons, each team is allowed one (1) Submission; any Submissions submitted by Participants before merging into a Team will be unsubmitted.

**2\. SUBMISSION LIMITS**

a. You may submit a maximum of five (5) Submissions per day. b. You may select up to two (2) Final Submissions for judging. c. For Hackathons, each Team may submit one (1) Submission only.

**3\. COMPETITION TIMELINE**

a. Competition Timeline dates (including Entry Deadline, Final Submission Deadline, Start Date, and Team Merger Deadline, as applicable) are reflected on the competition’s Overview > Timeline page.

**4\. COMPETITION DATA**

a. Data Access and Use.

1.  You may access and use the Competition Data for any purpose, whether commercial or non-commercial, including for participating in the Competition and on Kaggle.com forums, and for academic research and education. The Competition Sponsor reserves the right to disqualify any Participant who uses the Competition Data other than as permitted by the Competition Website and these Rules.

b. Data Security.

1.  You agree to use reasonable and suitable measures to prevent persons who have not formally agreed to these Rules from gaining access to the Competition Data. You agree not to transmit, duplicate, publish, redistribute or otherwise provide or make available the Competition Data to any party not participating in the Competition. You agree to notify Kaggle immediately upon learning of any possible unauthorized transmission of or unauthorized access to the Competition Data and agree to work with Kaggle to rectify any unauthorized transmission or access.

**5\. WINNER LICENSE**

a. Under Section 2.8 (Winners Obligations) of the General Rules below, you hereby grant and will grant the Competition Sponsor the following license(s) with respect to your Submission if you are a Competition winner:

1.  **Open Source:** You hereby license and will license your winning Submission and the source code used to generate the Submission under CC-BY 4.0 an Open Source Initiative-approved license (see [www.opensource.org](http://www.opensource.org/)) that in no event limits commercial use of such code or model containing or depending on such code.
2.  For generally commercially available software that you used to generate your Submission that is not owned by you, but that can be procured by the Competition Sponsor without undue expense, you do not need to grant the license in the preceding Section for that software.
3.  In the event that input data or pretrained models with an incompatible license are used to generate your winning solution, you do not need to grant an open source license in the preceding Section for that data and/or model(s).

b. You may be required by the Sponsor to provide a detailed description of how the winning Submission was generated, to the Competition Sponsor’s specifications, as outlined in Section 2.8, Winner’s Obligations. This may include a detailed description of methodology, where one must be able to reproduce the approach by reading the description, and includes a detailed explanation of the architecture, preprocessing, loss function, training details, hyper-parameters, etc. The description should also include a link to a code repository with complete and detailed instructions so that the results obtained can be reproduced. After your solution has been validated, you may be asked to discuss your results via a recorded call or panel call with the competition sponsors, which call may take the form of a panel with the attendance of other winners.

**6\. EXTERNAL DATA AND TOOLS**

a. You may use data other than the Competition Data (“External Data”) to develop and test your Submissions. However, you will ensure the External Data is either publicly available and equally accessible to use by all Participants of the Competition for purposes of the competition at no cost to the other Participants, or satisfies the Reasonableness criteria as outlined in Section 2.6.b below. The ability to use External Data under this Section does not limit your other obligations under these Competition Rules, including but not limited to Section 2.8 (Winners Obligations).

b. The use of external data and models is acceptable unless specifically prohibited by the Host. Because of the potential costs or restrictions (e.g., “geo restrictions”) associated with obtaining rights to use external data or certain software and associated tools, their use must be “reasonably accessible to all” and of “minimal cost”. Also, regardless of the cost challenges as they might affect all Participants during the course of the competition, the costs of potentially procuring a license for software used to generate a Submission, must also be considered. The Host will employ an assessment of whether or not the following criteria can exclude the use of the particular LLM, data set(s), or tool(s):

1.  Are Participants being excluded from a competition because of the "excessive" costs for access to certain LLMs, external data, or tools that might be used by other Participants. The Host will assess the excessive cost concern by applying a “Reasonableness” standard (the “Reasonableness Standard”). The Reasonableness Standard will be determined and applied by the Host in light of things like cost thresholds and accessibility.
2.  By way of example only, a small subscription charge to use additional elements of a large language model such as Gemini Advanced are acceptable if meeting the Reasonableness Standard of Sec. 8.2. Purchasing a license to use a proprietary dataset that exceeds the cost of a prize in the competition would not be considered reasonable.

c. Automated Machine Learning Tools (“AMLT”)

1.  Individual Participants and Teams may use automated machine learning tool(s) (“AMLT”) (e.g., Google toML, H2O Driverless AI, etc.) to create a Submission, provided that the Participant or Team ensures that they have an appropriate license to the AMLT such that they are able to comply with the Competition Rules.

**7\. ELIGIBILITY**

a. Unless otherwise stated in the Competition-Specific Rules above or prohibited by internal policies of the Competition Entities, employees, interns, contractors, officers and directors of Competition Entities may enter and participate in the Competition, but are not eligible to win any Prizes. "Competition Entities" means the Competition Sponsor, Kaggle Inc., and their respective parent companies, subsidiaries and affiliates. If you are such a Participant from a Competition Entity, you are subject to all applicable internal policies of your employer with respect to your participation.

**8\. WINNER’S OBLIGATIONS**

a. As a condition to being awarded a Prize, a Prize winner must fulfill the following obligations:

1.  Provide a detailed description of how the winning Submission was generated in the Competition forums, to the Competition Sponsor’s specifications. This may include a detailed description of methodology, where one must be able to reproduce the approach by reading the description, and includes a detailed explanation of the architecture, preprocessing, loss function, training details, hyper-parameters, etc. The description should also include a link to a code repository with complete and detailed instructions so that the results obtained can be reproduced.

a. To the extent that the final model’s software code includes generally commercially available software that is not owned by you, but that can be procured by the Competition Sponsor without undue expense, then instead of delivering the code for that software to the Competition Sponsor, you must identify that software, method for procuring it, and any parameters or other information necessary to replicate the winning Submission; Individual Participants and Teams who create a Submission using an AMLT may win a Prize. However, for clarity, the potential winner’s Submission must still meet the requirements of these Rules, including but not limited to Section 2.5 (Winners License), Section 2.8 (Winners Obligations), and Section 3.14 (Warranty, Indemnity, and Release).”

b. Individual Participants and Teams who create a Submission using an AMLT may win a Prize. However, for clarity, the potential winner’s Submission must still meet the requirements of these Rules,

1.  Grant to the Competition Sponsor the license to the winning Submission stated in the Competition Specific Rules above, and represent that you have the unrestricted right to grant that license;
2.  Sign and return all Prize acceptance documents as may be required by Competition Sponsor or Kaggle, including without limitation: (a) eligibility certifications; (b) licenses, releases and other agreements required under the Rules; and (c) U.S. tax forms (such as IRS Form W-9 if U.S. resident, IRS Form W-8BEN if foreign resident, or future equivalents).

**9\. GOVERNING LAW**

a. Unless otherwise provided in the Competition Specific Rules above, all claims arising out of or relating to these Rules will be governed by California law, excluding its conflict of laws rules, and will be litigated exclusively in the Federal or State courts of Santa Clara County, California, USA. The parties consent to personal jurisdiction in those courts. If any provision of these Rules is held to be invalid or unenforceable, all remaining provisions of the Rules will remain in full force and effect.

**10\. SCORING AND LEADERBOARD**

Your Submissions will be scored based on their performance in an episode, and your performances in episodes will be aggregated to determine your position on the Leaderboard, in each case as described in the evaluation documentation on the Competition Website. There is no Private Leaderboard in Simulation competitions.

**11\. ENVIRONMENTS & PUBLIC AVAILABILITY**

This Competition makes use of Kaggle Environments. Additional rules related to the Environment(s) used in this Competition are available on the Competition Website. A replay of each episode of the competition, which includes the actions taken by your Submission in the episode, may be publicly available and downloadable.

**12\. NO INGRESS OR EGRESS**

During the evaluation of an episode your Submission may not pull in or use any information external to the Submission and Environment and may not send any information out.

**3\. GENERAL COMPETITION RULES - BINDING AGREEMENT**

**1\. ELIGIBILITY**

a. To be eligible to enter the Competition, you must be:

1.  a registered account holder at Kaggle.com;
2.  the older of 18 years old or the age of majority in your jurisdiction of residence (unless otherwise agreed to by Competition Sponsor and appropriate parental/guardian consents have been obtained by Competition Sponsor);
3.  not a resident of Crimea, so-called Donetsk People's Republic (DNR) or Luhansk People's Republic (LNR), Cuba, Iran, or North Korea; and
4.  not a person or representative of an entity under U.S. export controls or sanctions (see: [https://www.treasury.gov/resourcecenter/sanctions/Programs/Pages/Programs.aspx](https://www.treasury.gov/resource-center/sanctions/Programs/Pages/Programs.aspx)).

b. Competitions are open to residents of the United States and worldwide, except that if you are a resident of Crimea, so-called Donetsk People's Republic (DNR) or Luhansk People's Republic (LNR), Cuba, Iran, North Korea, or are subject to U.S. export controls or sanctions, you may not enter the Competition. Other local rules and regulations may apply to you, so please check your local laws to ensure that you are eligible to participate in skills-based competitions. The Competition Host reserves the right to forego or award alternative Prizes where needed to comply with local laws. If a winner is located in a country where prizes cannot be awarded, then they are not eligible to receive a prize.

c. If you are entering as a representative of a company, educational institution or other legal entity, or on behalf of your employer, these rules are binding on you, individually, and the entity you represent or where you are an employee. If you are acting within the scope of your employment, or as an agent of another party, you warrant that such party or your employer has full knowledge of your actions and has consented thereto, including your potential receipt of a Prize. You further warrant that your actions do not violate your employer's or entity's policies and procedures.

d. The Competition Sponsor reserves the right to verify eligibility and to adjudicate on any dispute at any time. If you provide any false information relating to the Competition concerning your identity, residency, mailing address, telephone number, email address, ownership of right, or information required for entering the Competition, you may be immediately disqualified from the Competition.

**2\. SPONSOR AND HOSTING PLATFORM**

a. The Competition is sponsored by Competition Sponsor named above. The Competition is hosted on behalf of Competition Sponsor by Kaggle Inc. ("Kaggle"). Kaggle is an independent contractor of Competition Sponsor, and is not a party to this or any agreement between you and Competition Sponsor. You understand that Kaggle has no responsibility with respect to selecting the potential Competition winner(s) or awarding any Prizes. Kaggle will perform certain administrative functions relating to hosting the Competition, and you agree to abide by the provisions relating to Kaggle under these Rules. As a Kaggle.com account holder and user of the Kaggle competition platform, remember you have accepted and are subject to the Kaggle Terms of Service at [www.kaggle.com/terms](http://www.kaggle.com/terms) in addition to these Rules.

**3\. COMPETITION PERIOD**

a. For the purposes of Prizes, the Competition will run from the Start Date and time to the Final Submission Deadline (such duration the “Competition Period”). The Competition Timeline is subject to change, and Competition Sponsor may introduce additional hurdle deadlines during the Competition Period. Any updated or additional deadlines will be publicized on the Competition Website. It is your responsibility to check the Competition Website regularly to stay informed of any deadline changes. YOU ARE RESPONSIBLE FOR DETERMINING THE CORRESPONDING TIME ZONE IN YOUR LOCATION.

**4\. COMPETITION ENTRY**

a. NO PURCHASE NECESSARY TO ENTER OR WIN. To enter the Competition, you must register on the Competition Website prior to the Entry Deadline, and follow the instructions for developing and entering your Submission through the Competition Website. Your Submissions must be made in the manner and format, and in compliance with all other requirements, stated on the Competition Website (the "Requirements"). Submissions must be received before any Submission deadlines stated on the Competition Website. Submissions not received by the stated deadlines will not be eligible to receive a Prize. b. Except as expressly allowed in Hackathons as set forth on the Competition Website, submissions may not use or incorporate information from hand labeling or human prediction of the validation dataset or test data records. c. If the Competition is a multi-stage competition with temporally separate training and/or test data, one or more valid Submissions may be required during each Competition stage in the manner described on the Competition Website in order for the Submissions to be Prize eligible. d. Submissions are void if they are in whole or part illegible, incomplete, damaged, altered, counterfeit, obtained through fraud, or late. Competition Sponsor reserves the right to disqualify any entrant who does not follow these Rules, including making a Submission that does not meet the Requirements.

**5\. INDIVIDUALS AND TEAMS**

a. Individual Account. You may make Submissions only under one, unique Kaggle.com account. You will be disqualified if you make Submissions through more than one Kaggle account, or attempt to falsify an account to act as your proxy. You may submit up to the maximum number of Submissions per day as specified on the Competition Website. b. Teams. If permitted under the Competition Website guidelines, multiple individuals may collaborate as a Team; however, you may join or form only one Team. Each Team member must be a single individual with a separate Kaggle account. You must register individually for the Competition before joining a Team. You must confirm your Team membership to make it official by responding to the Team notification message sent to your Kaggle account. Team membership may not exceed the Maximum Team Size stated on the Competition Website. c. Team Merger. Teams (or individual Participants) may request to merge via the Competition Website. Team mergers may be allowed provided that: (i) the combined Team does not exceed the Maximum Team Size; (ii) the number of Submissions made by the merging Teams does not exceed the number of Submissions permissible for one Team at the date of the merger request; (iii) the merger is completed before the earlier of: any merger deadline or the Competition deadline; and (iv) the proposed combined Team otherwise meets all the requirements of these Rules. d. Private Sharing. No private sharing outside of Teams. Privately sharing code or data outside of Teams is not permitted. It's okay to share code if made available to all Participants on the forums.

**6\. SUBMISSION CODE REQUIREMENTS**

a. Private Code Sharing. Unless otherwise specifically permitted under the Competition Website or Competition Specific Rules above, during the Competition Period, you are not allowed to privately share source or executable code developed in connection with or based upon the Competition Data or other source or executable code relevant to the Competition (“Competition Code”). This prohibition includes sharing Competition Code between separate Teams, unless a Team merger occurs. Any such sharing of Competition Code is a breach of these Competition Rules and may result in disqualification. b. Public Code Sharing. You are permitted to publicly share Competition Code, provided that such public sharing does not violate the intellectual property rights of any third party. If you do choose to share Competition Code or other such code, you are required to share it on Kaggle.com on the discussion forum or notebooks associated specifically with the Competition for the benefit of all competitors. By so sharing, you are deemed to have licensed the shared code under an Open Source Initiative-approved license (see [www.opensource.org](http://www.opensource.org/)) that in no event limits commercial use of such Competition Code or model containing or depending on such Competition Code. c. Use of Open Source. Unless otherwise stated in the Specific Competition Rules above, if open source code is used in the model to generate the Submission, then you must only use open source code licensed under an Open Source Initiative-approved license (see [www.opensource.org](http://www.opensource.org/)) that in no event limits commercial use of such code or model containing or depending on such code.

**7\. DETERMINING WINNERS**

a. Each Submission will be scored and/or ranked by the evaluation metric, or Evaluation Rubric (in the case of Hackathon Competitions),stated on the Competition Website. During the Competition Period, the current ranking will be visible on the Competition Website's Public Leaderboard. The potential winner(s) are determined solely by the leaderboard ranking on the Private Leaderboard, subject to compliance with these Rules. The Public Leaderboard will be based on the public test set and the Private Leaderboard will be based on the private test set. There will be no leaderboards for Hackathon Competitions. b. In the event of a tie, the Submission that was entered first to the Competition will be the winner. In the event a potential winner is disqualified for any reason, the Submission that received the next highest score rank will be chosen as the potential winner. For Hackathon Competitions, each of the top Submissions will get a unique ranking and there will be no tiebreakers.

**8\. NOTIFICATION OF WINNERS & DISQUALIFICATION**

a. The potential winner(s) will be notified by email. b. If a potential winner (i) does not respond to the notification attempt within one (1) week from the first notification attempt or (ii) notifies Kaggle within one week after the Final Submission Deadline that the potential winner does not want to be nominated as a winner or does not want to receive a Prize, then, in each case (i) and (ii) such potential winner will not receive any Prize, and an alternate potential winner will be selected from among all eligible entries received based on the Competition’s judging criteria. c. In case (i) and (ii) above Kaggle may disqualify the Participant. However, in case (ii) above, if requested by Kaggle, such potential winner may provide code and documentation to verify the Participant’s compliance with these Rules. If the potential winner provides code and documentation to the satisfaction of Kaggle, the Participant will not be disqualified pursuant to this paragraph. d. Competition Sponsor reserves the right to disqualify any Participant from the Competition if the Competition Sponsor reasonably believes that the Participant has attempted to undermine the legitimate operation of the Competition by cheating, deception, or other unfair playing practices or abuses, threatens or harasses any other Participants, Competition Sponsor or Kaggle. e. A disqualified Participant may be removed from the Competition leaderboard, at Kaggle's sole discretion. If a Participant is removed from the Competition Leaderboard, additional winning features associated with the Kaggle competition platform, for example Kaggle points or medals, may also not be awarded. f. The final leaderboard list will be publicly displayed at Kaggle.com. Determinations of Competition Sponsor are final and binding.

**9\. PRIZES**

a. Prize(s) are as described on the Competition Website and are only available for winning during the time period described on the Competition Website. The odds of winning any Prize depends on the number of eligible Submissions received during the Competition Period and the skill of the Participants. b. All Prizes are subject to Competition Sponsor's review and verification of the Participant’s eligibility and compliance with these Rules, and the compliance of the winning Submissions with the Submissions Requirements. In the event that the Submission demonstrates non-compliance with these Competition Rules, Competition Sponsor may at its discretion take either of the following actions: (i) disqualify the Submission(s); or (ii) require the potential winner to remediate within one week after notice all issues identified in the Submission(s) (including, without limitation, the resolution of license conflicts, the fulfillment of all obligations required by software licenses, and the removal of any software that violates the software restrictions). c. A potential winner may decline to be nominated as a Competition winner in accordance with Section 3.8. d. Potential winners must return all required Prize acceptance documents within two (2) weeks following notification of such required documents, or such potential winner will be deemed to have forfeited the prize and another potential winner will be selected. Prize(s) will be awarded within approximately thirty (30) days after receipt by Competition Sponsor or Kaggle of the required Prize acceptance documents. Transfer or assignment of a Prize is not allowed. e. You are not eligible to receive any Prize if you do not meet the Eligibility requirements in Section 2.7 and Section 3.1 above. f. If a Team wins a monetary Prize, the Prize money will be allocated in even shares between the eligible Team members, unless the Team unanimously opts for a different Prize split and notifies Kaggle before Prizes are issued.

**10\. TAXES**

a. ALL TAXES IMPOSED ON PRIZES ARE THE SOLE RESPONSIBILITY OF THE WINNERS. Payments to potential winners are subject to the express requirement that they submit all documentation requested by Competition Sponsor or Kaggle for compliance with applicable state, federal, local and foreign (including provincial) tax reporting and withholding requirements. Prizes will be net of any taxes that Competition Sponsor is required by law to withhold. If a potential winner fails to provide any required documentation or comply with applicable laws, the Prize may be forfeited and Competition Sponsor may select an alternative potential winner. Any winners who are U.S. residents will receive an IRS Form-1099 in the amount of their Prize.

**11\. GENERAL CONDITIONS**

a. All federal, state, provincial and local laws and regulations apply.

**12\. PUBLICITY**

a. You agree that Competition Sponsor, Kaggle and its affiliates may use your name and likeness for advertising and promotional purposes without additional compensation, unless prohibited by law.

**13\. PRIVACY**

a. You acknowledge and agree that Competition Sponsor and Kaggle may collect, store, share and otherwise use personally identifiable information provided by you during the Kaggle account registration process and the Competition, including but not limited to, name, mailing address, phone number, and email address (“Personal Information”). Kaggle acts as an independent controller with regard to its collection, storage, sharing, and other use of this Personal Information, and will use this Personal Information in accordance with its Privacy Policy <[www.kaggle.com/privacy](http://www.kaggle.com/privacy)\>, including for administering the Competition. As a Kaggle.com account holder, you have the right to request access to, review, rectification, portability or deletion of any personal data held by Kaggle about you by logging into your account and/or contacting Kaggle Support at <[www.kaggle.com/contact](http://www.kaggle.com/contact)\>. b. As part of Competition Sponsor performing this contract between you and the Competition Sponsor, Kaggle will transfer your Personal Information to Competition Sponsor, which acts as an independent controller with regard to this Personal Information. As a controller of such Personal Information, Competition Sponsor agrees to comply with all U.S. and foreign data protection obligations with regard to your Personal Information. Kaggle will transfer your Personal Information to Competition Sponsor in the country specified in the Competition Sponsor Address listed above, which may be a country outside the country of your residence. Such country may not have privacy laws and regulations similar to those of the country of your residence.

**14\. WARRANTY, INDEMNITY AND RELEASE**

a. You warrant that your Submission is your own original work and, as such, you are the sole and exclusive owner and rights holder of the Submission, and you have the right to make the Submission and grant all required licenses. You agree not to make any Submission that: (i) infringes any third party proprietary rights, intellectual property rights, industrial property rights, personal or moral rights or any other rights, including without limitation, copyright, trademark, patent, trade secret, privacy, publicity or confidentiality obligations, or defames any person; or (ii) otherwise violates any applicable U.S. or foreign state or federal law. b. To the maximum extent permitted by law, you indemnify and agree to keep indemnified Competition Entities at all times from and against any liability, claims, demands, losses, damages, costs and expenses resulting from any of your acts, defaults or omissions and/or a breach of any warranty set forth herein. To the maximum extent permitted by law, you agree to defend, indemnify and hold harmless the Competition Entities from and against any and all claims, actions, suits or proceedings, as well as any and all losses, liabilities, damages, costs and expenses (including reasonable attorneys fees) arising out of or accruing from: (a) your Submission or other material uploaded or otherwise provided by you that infringes any third party proprietary rights, intellectual property rights, industrial property rights, personal or moral rights or any other rights, including without limitation, copyright, trademark, patent, trade secret, privacy, publicity or confidentiality obligations, or defames any person; (b) any misrepresentation made by you in connection with the Competition; (c) any non-compliance by you with these Rules or any applicable U.S. or foreign state or federal law; (d) claims brought by persons or entities other than the parties to these Rules arising from or related to your involvement with the Competition; and (e) your acceptance, possession, misuse or use of any Prize, or your participation in the Competition and any Competition-related activity. c. You hereby release Competition Entities from any liability associated with: (a) any malfunction or other problem with the Competition Website; (b) any error in the collection, processing, or retention of any Submission; or (c) any typographical or other error in the printing, offering or announcement of any Prize or winners.

**15\. INTERNET**

a. Competition Entities are not responsible for any malfunction of the Competition Website or any late, lost, damaged, misdirected, incomplete, illegible, undeliverable, or destroyed Submissions or entry materials due to system errors, failed, incomplete or garbled computer or other telecommunication transmission malfunctions, hardware or software failures of any kind, lost or unavailable network connections, typographical or system/human errors and failures, technical malfunction(s) of any telephone network or lines, cable connections, satellite transmissions, servers or providers, or computer equipment, traffic congestion on the Internet or at the Competition Website, or any combination thereof, which may limit a Participant’s ability to participate.

**16\. RIGHT TO CANCEL, MODIFY OR DISQUALIFY**

a. If for any reason the Competition is not capable of running as planned, including infection by computer virus, bugs, tampering, unauthorized intervention, fraud, technical failures, or any other causes which corrupt or affect the administration, security, fairness, integrity, or proper conduct of the Competition, Competition Sponsor reserves the right to cancel, terminate, modify or suspend the Competition. Competition Sponsor further reserves the right to disqualify any Participant who tampers with the submission process or any other part of the Competition or Competition Website. Any attempt by a Participant to deliberately damage any website, including the Competition Website, or undermine the legitimate operation of the Competition is a violation of criminal and civil laws. Should such an attempt be made, Competition Sponsor and Kaggle each reserves the right to seek damages from any such Participant to the fullest extent of the applicable law.

**17\. NOT AN OFFER OR CONTRACT OF EMPLOYMENT**

a. Under no circumstances will the entry of a Submission, the awarding of a Prize, or anything in these Rules be construed as an offer or contract of employment with Competition Sponsor or any of the Competition Entities. You acknowledge that you have submitted your Submission voluntarily and not in confidence or in trust. You acknowledge that no confidential, fiduciary, agency, employment or other similar relationship is created between you and Competition Sponsor or any of the Competition Entities by your acceptance of these Rules or your entry of your Submission.

**18\. DEFINITIONS**

a. "Competition Data" are the data or datasets available from the Competition Website for the purpose of use in the Competition, including any prototype or executable code provided on the Competition Website. The Competition Data will contain private and public test sets. Which data belongs to which set will not be made available to Participants. b. An “Entry” is when a Participant has joined, signed up, or accepted the rules of a competition. Entry is required to make a Submission to a competition. c. A “Final Submission” is the Submission selected by the user, or automatically selected by Kaggle in the event not selected by the user, that is/are used for final placement on the competition leaderboard. d. A “Participant” or “Participant User” is an individual who participates in a competition by entering the competition and making a Submission. e. The “Private Leaderboard” is a ranked display of Participants’ Submission scores against the private test set. The Private Leaderboard determines the final standing in the competition. f. The “Public Leaderboard” is a ranked display of Participants’ Submission scores against a representative sample of the test data. This leaderboard is visible throughout the competition. g. A “Sponsor” is responsible for hosting the competition, which includes but is not limited to providing the data for the competition, determining winners, and enforcing competition rules. h. A “Submission” is anything provided by the Participant to the Sponsor to be evaluated for competition purposes and determine leaderboard position. A Submission may be made as a model, notebook, prediction file, or other format as determined by the Sponsor. i. A “Team” is one or more Participants participating together in a Kaggle competition, by officially merging together as a Team within the competition platform.

**Kaggle Competition Foundational Rules**

**(Non-editable)**

Competition participants must also agree to Kaggle's Foundational Competition Rules. These rules will supersede the competition-specific rules in the event of any conflict.

The following Kaggle Competition Foundational Rules (“ Foundational Rules ”) apply to every competition regardless of whether the Sponsor creates competition-specific rules. Any competition-specific rules provided by the Sponsor are in addition to these rules, and in the case of any conflict or inconsistency, these Foundational Rules control and nullify contrary competition-specific rules.

**GENERAL COMPETITION RULES - BINDING AGREEMENT**

**1\. ELIGIBILITY**

a. To be eligible to enter the Competition, you must be:

1.  a registered account holder at Kaggle.com;
2.  the older of 18 years old or the age of majority in your jurisdiction of residence (unless otherwise agreed to by Competition Sponsor and appropriate parental/guardian consents have been obtained by Competition Sponsor);
3.  not a resident of Crimea, so-called Donetsk People's Republic (DNR) or Luhansk People's Republic (LNR), Cuba, Iran, or North Korea; and
4.  not a person or representative of an entity under U.S. export controls or sanctions (see: [https://www.treasury.gov/resourcecenter/sanctions/Programs/Pages/Programs.aspx](https://www.treasury.gov/resource-center/sanctions/Programs/Pages/Programs.aspx)).

b. Competitions are open to residents of the United States and worldwide, except that if you are a resident of Crimea, so-called Donetsk People's Republic (DNR) or Luhansk People's Republic (LNR), Cuba, Iran, North Korea, or are subject to U.S. export controls or sanctions, you may not enter the Competition. Other local rules and regulations may apply to you, so please check your local laws to ensure that you are eligible to participate in skills-based competitions. The Competition Host reserves the right to forego or award alternative Prizes where needed to comply with local laws. If a winner is located in a country where prizes cannot be awarded, then they are not eligible to receive a prize.

c. If you are entering as a representative of a company, educational institution or other legal entity, or on behalf of your employer, these rules are binding on you, individually, and the entity you represent or where you are an employee. If you are acting within the scope of your employment, or as an agent of another party, you warrant that such party or your employer has full knowledge of your actions and has consented thereto, including your potential receipt of a Prize. You further warrant that your actions do not violate your employer's or entity's policies and procedures.

d. The Competition Sponsor reserves the right to verify eligibility and to adjudicate on any dispute at any time. If you provide any false information relating to the Competition concerning your identity, residency, mailing address, telephone number, email address, ownership of right, or information required for entering the Competition, you may be immediately disqualified from the Competition.

**2\. SPONSOR AND HOSTING PLATFORM**

a. The Competition is sponsored by Competition Sponsor named above. The Competition is hosted on behalf of Competition Sponsor by Kaggle Inc. ("Kaggle"). Kaggle is an independent contractor of Competition Sponsor, and is not a party to this or any agreement between you and Competition Sponsor. You understand that Kaggle has no responsibility with respect to selecting the potential Competition winner(s) or awarding any Prizes. Kaggle will perform certain administrative functions relating to hosting the Competition, and you agree to abide by the provisions relating to Kaggle under these Rules. As a Kaggle.com account holder and user of the Kaggle competition platform, remember you have accepted and are subject to the Kaggle Terms of Service at [www.kaggle.com/terms](http://www.kaggle.com/terms) in addition to these Rules.

**3\. COMPETITION PERIOD**

a. For the purposes of Prizes, the Competition will run from the Start Date and time to the Final Submission Deadline (such duration the “Competition Period”). The Competition Timeline is subject to change, and Competition Sponsor may introduce additional hurdle deadlines during the Competition Period. Any updated or additional deadlines will be publicized on the Competition Website. It is your responsibility to check the Competition Website regularly to stay informed of any deadline changes. YOU ARE RESPONSIBLE FOR DETERMINING THE CORRESPONDING TIME ZONE IN YOUR LOCATION.

**4\. COMPETITION ENTRY**

a. NO PURCHASE NECESSARY TO ENTER OR WIN. To enter the Competition, you must register on the Competition Website prior to the Entry Deadline, and follow the instructions for developing and entering your Submission through the Competition Website. Your Submissions must be made in the manner and format, and in compliance with all other requirements, stated on the Competition Website (the "Requirements"). Submissions must be received before any Submission deadlines stated on the Competition Website. Submissions not received by the stated deadlines will not be eligible to receive a Prize. b. Submissions may not use or incorporate information from hand labeling or human prediction of the validation dataset or test data records. c. If the Competition is a multi-stage competition with temporally separate training and/or test data, one or more valid Submissions may be required during each Competition stage in the manner described on the Competition Website in order for the Submissions to be Prize eligible. d. Submissions are void if they are in whole or part illegible, incomplete, damaged, altered, counterfeit, obtained through fraud, or late. Competition Sponsor reserves the right to disqualify any entrant who does not follow these Rules, including making a Submission that does not meet the Requirements.

**5\. INDIVIDUALS AND TEAMS**

a. Individual Account. You may make Submissions only under one, unique Kaggle.com account. You will be disqualified if you make Submissions through more than one Kaggle account, or attempt to falsify an account to act as your proxy. You may submit up to the maximum number of Submissions per day as specified on the Competition Website. b. Teams. If permitted under the Competition Website guidelines, multiple individuals may collaborate as a Team; however, you may join or form only one Team. Each Team member must be a single individual with a separate Kaggle account. You must register individually for the Competition before joining a Team. You must confirm your Team membership to make it official by responding to the Team notification message sent to your Kaggle account. Team membership may not exceed the Maximum Team Size stated on the Competition Website. c. Team Merger. Teams may request to merge via the Competition Website. Team mergers may be allowed provided that: (i) the combined Team does not exceed the Maximum Team Size; (ii) the number of Submissions made by the merging Teams does not exceed the number of Submissions permissible for one Team at the date of the merger request; (iii) the merger is completed before the earlier of: any merger deadline or the Competition deadline; and (iv) the proposed combined Team otherwise meets all the requirements of these Rules. d. Private Sharing. No private sharing outside of Teams. Privately sharing code or data outside of Teams is not permitted. It's okay to share code if made available to all Participants on the forums.

**6\. SUBMISSION CODE REQUIREMENTS**

a. Private Code Sharing. Unless otherwise specifically permitted under the Competition Website or Competition Specific Rules above, during the Competition Period, you are not allowed to privately share source or executable code developed in connection with or based upon the Competition Data or other source or executable code relevant to the Competition (“Competition Code”). This prohibition includes sharing Competition Code between separate Teams, unless a Team merger occurs. Any such sharing of Competition Code is a breach of these Competition Rules and may result in disqualification. b. Public Code Sharing. You are permitted to publicly share Competition Code, provided that such public sharing does not violate the intellectual property rights of any third party. If you do choose to share Competition Code or other such code, you are required to share it on Kaggle.com on the discussion forum or notebooks associated specifically with the Competition for the benefit of all competitors. By so sharing, you are deemed to have licensed the shared code under an Open Source Initiative-approved license (see [www.opensource.org](http://www.opensource.org/)) that in no event limits commercial use of such Competition Code or model containing or depending on such Competition Code. c. Use of Open Source. Unless otherwise stated in the Specific Competition Rules above, if open source code is used in the model to generate the Submission, then you must only use open source code licensed under an Open Source Initiative-approved license (see [www.opensource.org](http://www.opensource.org/)) that in no event limits commercial use of such code or model containing or depending on such code.

**7\. DETERMINING WINNERS**

a. Each Submission will be scored and ranked by the evaluation metric stated on the Competition Website. During the Competition Period, the current ranking will be visible on the Competition Website's Public Leaderboard. The potential winner(s) are determined solely by the leaderboard ranking on the Private Leaderboard, subject to compliance with these Rules. The Public Leaderboard will be based on the public test set and the Private Leaderboard will be based on the private test set. b. In the event of a tie, the Submission that was entered first to the Competition will be the winner. In the event a potential winner is disqualified for any reason, the Submission that received the next highest score rank will be chosen as the potential winner.

**8\. NOTIFICATION OF WINNERS & DISQUALIFICATION**

a. The potential winner(s) will be notified by email. b. If a potential winner (i) does not respond to the notification attempt within one (1) week from the first notification attempt or (ii) notifies Kaggle within one week after the Final Submission Deadline that the potential winner does not want to be nominated as a winner or does not want to receive a Prize, then, in each case (i) and (ii) such potential winner will not receive any Prize, and an alternate potential winner will be selected from among all eligible entries received based on the Competition’s judging criteria. c. In case (i) and (ii) above Kaggle may disqualify the Participant. However, in case (ii) above, if requested by Kaggle, such potential winner may provide code and documentation to verify the Participant’s compliance with these Rules. If the potential winner provides code and documentation to the satisfaction of Kaggle, the Participant will not be disqualified pursuant to this paragraph. d. Competition Sponsor reserves the right to disqualify any Participant from the Competition if the Competition Sponsor reasonably believes that the Participant has attempted to undermine the legitimate operation of the Competition by cheating, deception, or other unfair playing practices or abuses, threatens or harasses any other Participants, Competition Sponsor or Kaggle. e. A disqualified Participant may be removed from the Competition leaderboard, at Kaggle's sole discretion. If a Participant is removed from the Competition Leaderboard, additional winning features associated with the Kaggle competition platform, for example Kaggle points or medals, may also not be awarded. f. The final leaderboard list will be publicly displayed at Kaggle.com. Determinations of Competition Sponsor are final and binding.

**9\. PRIZES**

a. Prize(s) are as described on the Competition Website and are only available for winning during the time period described on the Competition Website. The odds of winning any Prize depends on the number of eligible Submissions received during the Competition Period and the skill of the Participants. b. All Prizes are subject to Competition Sponsor's review and verification of the Participant’s eligibility and compliance with these Rules, and the compliance of the winning Submissions with the Submissions Requirements. In the event that the Submission demonstrates non-compliance with these Competition Rules, Competition Sponsor may at its discretion take either of the following actions: (i) disqualify the Submission(s); or (ii) require the potential winner to remediate within one week after notice all issues identified in the Submission(s) (including, without limitation, the resolution of license conflicts, the fulfillment of all obligations required by software licenses, and the removal of any software that violates the software restrictions). c. A potential winner may decline to be nominated as a Competition winner in accordance with Section 3.8. d. Potential winners must return all required Prize acceptance documents within two (2) weeks following notification of such required documents, or such potential winner will be deemed to have forfeited the prize and another potential winner will be selected. Prize(s) will be awarded within approximately thirty (30) days after receipt by Competition Sponsor or Kaggle of the required Prize acceptance documents. Transfer or assignment of a Prize is not allowed. e. You are not eligible to receive any Prize if you do not meet the Eligibility requirements in Section 2.7 and Section 3.1 above. f. If a Team wins a monetary Prize, the Prize money will be allocated in even shares between the eligible Team members, unless the Team unanimously opts for a different Prize split and notifies Kaggle before Prizes are issued.

**10\. TAXES**

a. ALL TAXES IMPOSED ON PRIZES ARE THE SOLE RESPONSIBILITY OF THE WINNERS. Payments to potential winners are subject to the express requirement that they submit all documentation requested by Competition Sponsor or Kaggle for compliance with applicable state, federal, local and foreign (including provincial) tax reporting and withholding requirements. Prizes will be net of any taxes that Competition Sponsor is required by law to withhold. If a potential winner fails to provide any required documentation or comply with applicable laws, the Prize may be forfeited and Competition Sponsor may select an alternative potential winner. Any winners who are U.S. residents will receive an IRS Form-1099 in the amount of their Prize.

**11\. GENERAL CONDITIONS**

a. All federal, state, provincial and local laws and regulations apply.

**12\. PUBLICITY**

a. You agree that Competition Sponsor, Kaggle and its affiliates may use your name and likeness for advertising and promotional purposes without additional compensation, unless prohibited by law.

**13\. PRIVACY**

a. You acknowledge and agree that Competition Sponsor and Kaggle may collect, store, share and otherwise use personally identifiable information provided by you during the Kaggle account registration process and the Competition, including but not limited to, name, mailing address, phone number, and email address (“Personal Information”). Kaggle acts as an independent controller with regard to its collection, storage, sharing, and other use of this Personal Information, and will use this Personal Information in accordance with its Privacy Policy <[www.kaggle.com/privacy](http://www.kaggle.com/privacy)\>, including for administering the Competition. As a Kaggle.com account holder, you have the right to request access to, review, rectification, portability or deletion of any personal data held by Kaggle about you by logging into your account and/or contacting Kaggle Support at <[www.kaggle.com/contact](http://www.kaggle.com/contact)\>. b. As part of Competition Sponsor performing this contract between you and the Competition Sponsor, Kaggle will transfer your Personal Information to Competition Sponsor, which acts as an independent controller with regard to this Personal Information. As a controller of such Personal Information, Competition Sponsor agrees to comply with all U.S. and foreign data protection obligations with regard to your Personal Information. Kaggle will transfer your Personal Information to Competition Sponsor in the country specified in the Competition Sponsor Address listed above, which may be a country outside the country of your residence. Such country may not have privacy laws and regulations similar to those of the country of your residence.

**14\. WARRANTY, INDEMNITY AND RELEASE**

a. You warrant that your Submission is your own original work and, as such, you are the sole and exclusive owner and rights holder of the Submission, and you have the right to make the Submission and grant all required licenses. You agree not to make any Submission that: (i) infringes any third party proprietary rights, intellectual property rights, industrial property rights, personal or moral rights or any other rights, including without limitation, copyright, trademark, patent, trade secret, privacy, publicity or confidentiality obligations, or defames any person; or (ii) otherwise violates any applicable U.S. or foreign state or federal law. b. To the maximum extent permitted by law, you indemnify and agree to keep indemnified Competition Entities at all times from and against any liability, claims, demands, losses, damages, costs and expenses resulting from any of your acts, defaults or omissions and/or a breach of any warranty set forth herein. To the maximum extent permitted by law, you agree to defend, indemnify and hold harmless the Competition Entities from and against any and all claims, actions, suits or proceedings, as well as any and all losses, liabilities, damages, costs and expenses (including reasonable attorneys fees) arising out of or accruing from: (a) your Submission or other material uploaded or otherwise provided by you that infringes any third party proprietary rights, intellectual property rights, industrial property rights, personal or moral rights or any other rights, including without limitation, copyright, trademark, patent, trade secret, privacy, publicity or confidentiality obligations, or defames any person; (b) any misrepresentation made by you in connection with the Competition; (c) any non-compliance by you with these Rules or any applicable U.S. or foreign state or federal law; (d) claims brought by persons or entities other than the parties to these Rules arising from or related to your involvement with the Competition; and (e) your acceptance, possession, misuse or use of any Prize, or your participation in the Competition and any Competition-related activity. c. You hereby release Competition Entities from any liability associated with: (a) any malfunction or other problem with the Competition Website; (b) any error in the collection, processing, or retention of any Submission; or (c) any typographical or other error in the printing, offering or announcement of any Prize or winners.

**15\. INTERNET**

a. Competition Entities are not responsible for any malfunction of the Competition Website or any late, lost, damaged, misdirected, incomplete, illegible, undeliverable, or destroyed Submissions or entry materials due to system errors, failed, incomplete or garbled computer or other telecommunication transmission malfunctions, hardware or software failures of any kind, lost or unavailable network connections, typographical or system/human errors and failures, technical malfunction(s) of any telephone network or lines, cable connections, satellite transmissions, servers or providers, or computer equipment, traffic congestion on the Internet or at the Competition Website, or any combination thereof, which may limit a Participant’s ability to participate.

**16\. RIGHT TO CANCEL, MODIFY OR DISQUALIFY**

a. If for any reason the Competition is not capable of running as planned, including infection by computer virus, bugs, tampering, unauthorized intervention, fraud, technical failures, or any other causes which corrupt or affect the administration, security, fairness, integrity, or proper conduct of the Competition, Competition Sponsor reserves the right to cancel, terminate, modify or suspend the Competition. Competition Sponsor further reserves the right to disqualify any Participant who tampers with the submission process or any other part of the Competition or Competition Website. Any attempt by a Participant to deliberately damage any website, including the Competition Website, or undermine the legitimate operation of the Competition is a violation of criminal and civil laws. Should such an attempt be made, Competition Sponsor and Kaggle each reserves the right to seek damages from any such Participant to the fullest extent of the applicable law.

**17\. NOT AN OFFER OR CONTRACT OF EMPLOYMENT**

a. Under no circumstances will the entry of a Submission, the awarding of a Prize, or anything in these Rules be construed as an offer or contract of employment with Competition Sponsor or any of the Competition Entities. You acknowledge that you have submitted your Submission voluntarily and not in confidence or in trust. You acknowledge that no confidential, fiduciary, agency, employment or other similar relationship is created between you and Competition Sponsor or any of the Competition Entities by your acceptance of these Rules or your entry of your Submission.

**18\. DEFINITIONS**

a. "Competition Data" are the data or datasets available from the Competition Website for the purpose of use in the Competition, including any prototype or executable code provided on the Competition Website. The Competition Data will contain private and public test sets. Which data belongs to which set will not be made available to Participants. b. An “Entry” is when a Participant has joined, signed up, or accepted the rules of a competition. Entry is required to make a Submission to a competition. c. A “Final Submission” is the Submission selected by the user, or automatically selected by Kaggle in the event not selected by the user, that is/are used for final placement on the competition leaderboard. d. A “Participant” or “Participant User” is an individual who participates in a competition by entering the competition and making a Submission. e. The “Private Leaderboard” is a ranked display of Participants’ Submission scores against the private test set. The Private Leaderboard determines the final standing in the competition. f. The “Public Leaderboard” is a ranked display of Participants’ Submission scores against a representative sample of the test data. This leaderboard is visible throughout the competition. g. A “Sponsor” is responsible for hosting the competition, which includes but is not limited to providing the data for the competition, determining winners, and enforcing competition rules. h. A “Submission” is anything provided by the Participant to the Sponsor to be evaluated for competition purposes and determine leaderboard position. A Submission may be made as a model, notebook, prediction file, or other format as determined by the Sponsor. i. A “Team” is one or more Participants participating together in a Kaggle competition, by officially merging together as a Team within the competition platform.

**Rules**

**  
Kaggle · Featured Simulation Competition · 2 months to go**

**Play in Browser**

**Submit Agent**

**Kaggriculture**

Create an agent to play in this farming simulation and compete with others to maximize your income

**Submissions**

**All**SuccessfulErrors

Submission and Description

Episodes

**No submissions found**

Need help making a submission? Check out the Code and Discussion tabs for this competition.