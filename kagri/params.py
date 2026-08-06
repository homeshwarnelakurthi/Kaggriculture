"""Tunable strategy parameters.

Everything the self-play tuner is allowed to search over lives here, as a flat
dict of scalars so CMA-ES / random search can drive it without touching logic.
"""

DEFAULTS = {
    # --- Labour -------------------------------------------------------------
    # 10 hands cost $143 for a whole day and buy 240 actions. Labour is the
    # cheapest thing in the game; being short of it is what kills runs.
    "hand_value_per_action": 20.0,
    "max_hands": 12,
    # Eight hands cost $54 total; twelve cost $376. Almost never worth skipping,
    # so the floor is deliberately tiny — the fib curve is the real cap.
    "hire_money_floor": 30.0,
    "hire_bank_fraction": 0.20,     # never spend more than this share of the bank on a crew
    # v12 (search over the LABOUR CEILING, holding v11's gate/pacing fixed):
    # tiles_per_unit 7.0 -> 6.5 and animal_labour_cost 2.5 -> 4.0. Note the
    # direction: an animal tile costs MORE labour than assumed, not less. Being
    # honest about that frees the crew to actually finish the crop work instead
    # of spreading thin over tiles it never gets back to.
    # Real-opponent gauntlet, head-to-head on identical seeds:
    #   ceiling-win  98% ALL / 90% worst / $78,813
    #   v11 control  87% / 60% / $72,575
    "tiles_per_unit": 6.5,
    "animal_labour_cost": 4.0,      # measured, not assumed — see above

    # v11: the CONSTRAINT parameters below were found by tools/search.py over 40
    # random configs. They are the knobs that actually bind. Tile targets are
    # inert -- asking for 20 cows instead of 12 produces a bit-identical game,
    # because the labour ceiling and feed gate decide the board, not the targets.
    # That is why five rounds of mix tuning (v7-v10) produced no ladder movement.
    # Real-opponent gauntlet 100% worst matchup vs the control's 88%; vs starter
    # +$5,740 mean and +$8,401 worst case, with MORE strawberry, MORE melon,
    # MORE cows and FEWER weeds simultaneously -- the first change to improve
    # every axis at once, because it lifts the clamp instead of re-asking for
    # tiles the clamp was refusing.
    # --- Cash discipline ----------------------------------------------------
    # Never spend below this. A full day of hands is added on top automatically.
    "ops_reserve_base": 550.0,
    "ops_reserve_per_animal": 15.0,

    # --- Bootstrap ----------------------------------------------------------
    "bootstrap_days": 3,            # crops only; no livestock before this
    "min_days_for_animal": 8,       # 4 days to first egg, then payback

    # --- Animal engine (the core of the strategy) ---------------------------
    # Flock size trades directly against melon acreage for hands. Raising melon
    # alone turns over (28 tiles at 22 geese scores 38%), but the same 28 tiles
    # with the flock cut to 18 scores 67% — the constraint is labour, not land.
    # Geese are off entirely: strawberry now competes for the same capital and
    # a goose returns $94/day against a sheep's $254 for identical work.
    # Livestock ranked by revenue per identical action+feed cost, at base price:
    #   SHEEP $254/day   COW $208/day   GOOSE $94/day
    # A sheep is 2.7x a goose for the same work. Geese were only ever preferred
    # because EGG is an unbounded sink — but town demand (438 milk, 335 wool per
    # season) keeps milk and wool near or above base too, and they are worth
    # 3-4x per unit. Buy sheep first, then cows, then geese.
    # Cows over sheep. Wool floors fast (335 town units/season on a `sq` curve)
    # while milk absorbs 438 at a $160 base — the biggest pot in the game. Real
    # ladder losses were to opponents running 7+ cows against our 1. Sheep are
    # dropped ENTIRELY: they were filled first and stole capital and pasture from
    # cows, and wool floors fast where milk does not. Gauntlet worst-matchup:
    # 12cow/0sheep 96%, 12cow/4sheep 88%, 14cow/6sheep 79%.
    # Note 16 cows measures IDENTICAL to 12 — the feed/labour clamp caps the herd
    # at 12, so raising the target above that is a no-op.
    # Found by tools/search.py over 28 random mixes, not by hand-picking: the
    # winner is 10 cow / 2 sheep / 10 melon / 28 strawberry / 12 wheat at
    # 100% ALL and 100% worst matchup ($72,181 mean) against v6's 99% / 94%.
    # Sheep are non-monotonic: 2 helps, 5 hurts badly (75% worst). Do not read
    # "some sheep good" as "more sheep better".
    # v9 reverts the MIX to v6's (12 cow / 0 sheep / 16 wheat), the only build with
    # a settled above-600 ladder rating (678.1 on 21 episodes, vs v7 656 on 14 and
    # v8 605 on 12). The v7 search-tuned mix won a gauntlet that had saturated at
    # 100% and therefore stopped discriminating. Keeps v8's weed valuation fix,
    # which came from direct instrumentation rather than that gauntlet.
    "target_sheep": 0,
    "target_cows": 12,
    "target_geese": 0,
    "feed_per_animal_day": 1.0,
    "wheat_buffer_per_animal": 2.0,  # shed wheat per animal before expanding
    "wheat_lead_tiles": 2,           # wheat tiles must lead animal count by this
    "coop_lead": 2,                  # empty coops allowed ahead of the birds
    # Buy one animal per turn, not four. Measured +$1,474 mean and +$4,470 on the
    # WORST case (6 seeds). Note this is a per-TURN cap and there are 24 turns a
    # day, so it is a gentle brake on lump spending rather than a real daily
    # limit — it does not fix the cow shortfall (see DEV.md on milk).
    "animal_buy_rate": 2,
    # Kept at 1.0. Letting livestock dip into the reserve does NOT produce early
    # animals -- 0.0 (no gate at all) still gives 0 animals at day 8, because the
    # bank is genuinely empty by then, not merely gated. And 0.0 costs $9k.
    "animal_reserve_frac": 1.0,
    # MUST stay False. Sizing feed capacity off allocated tiles (rather than the
    # oscillating planted count) correctly stabilises the animal target and then
    # collapses the run to ~$14.7k, with or without a rate limit. The oscillation
    # is load-bearing: it paces livestock spend. Kept as a flag to stop this
    # being re-attempted without re-measuring.
    "stable_wheat_capacity": False,
    "animal_carry": 3,               # animals one unit ferries per shed trip
    "wheat_carry": 8,                # wheat one unit ferries per feeding round
    "fert_carry": 6,                 # fertiliser one unit ferries per round
    "fert_reserve": 4,               # keep this much fertiliser back from sale
    # Only fertilise where the gain beats what the fertiliser would sell for.
    # Wheat is the ONE crop that needs fertiliser: it cannot reach its 6-unit cap on
    # watering alone, while melon reaches 6 unaided by day 10 (fertilising melon is
    # pure waste). Wheat's computed gain is ~$90, so a threshold of exactly 90 made
    # `gain > 90` fail by a hair and we fertilised nothing at all.
    # MEASURED AND REVERTED. The public meta guide says wheat cannot reach its 6-unit
    # cap on watering alone and therefore needs fertiliser. True of the mechanic,
    # but not worth it here: lowering this to 40 so wheat qualifies scored
    # $74,334 mean against the baseline's $74,952. The fertiliser is worth more
    # sold than spent on +2 wheat units. Left at 90, which excludes wheat by a hair.
    "fertilize_min_gain": 90.0,
    "drop_threshold": 5,             # carried produce that triggers a shed run

    # --- Crops --------------------------------------------------------------
    "wheat_units_per_tile_day": 0.9,
    "wheat_tiles_per_animal": 1.15,
    "wheat_tile_share": 0.6,         # hard cap: fraction of land given to wheat
    "min_wheat_tiles": 6,
    # Absolute wheat target, independent of flock size. Wheat sells for ~$35 per
    # action (same as an egg) with none of the capital, build or starvation risk,
    # and town demand of ~639 units/season keeps its price climbing all game.
    "wheat_tiles_target": 10,
    # Melon is a FIXED, SHARED pot (~$26.5k, floors near 200 units). Held small
    # now: with strawberry in the build, raising melon to 16 collapsed the run
    # ($38k mean, $9k worst) by crowding out the crop that actually compounds.
    "melon_tiles": 10,
    # Strawberry is now the CORE crop, not an experiment. Two fixes unlocked it:
    # carrot_fill off (it squatted on tiles strawberry could not yet afford and
    # never returned them) and rate-limited seed buying. The earlier failure was
    # never the reserve LEVEL — it was the lump: an unbounded gate bought 24
    # seeds ($2,400 of $3,000) on day 0 and killed the farm. Top players spend
    # the same money trickled over ten days while sitting at $131-689.
    # Sized 28 (not 34/40) on WORST-MATCHUP, not average: 34 and 40 score 85-86%
    # overall but only 33% against a strawberry rusher, while 28 scores 82%
    # overall and 67% there. On a win/loss ladder the soft archetype is what
    # bleeds rating, and strawrush is the top-of-ladder build we now resemble.
    "strawberry_tiles": 34,
    "straw_last_plant_day": 17,
    "melon_first_day": 0,            # melon pays nothing for 10 days
    "melon_last_plant_day": 16,
    # MUST stay False. Carrot filler occupies tiles strawberry cannot yet afford
    # and never yields them back — the mechanism behind strawberry previously
    # "destabilising" the allocator (3 planted of 35, 24 tiles of carrot).
    "carrot_fill": False,
    # Freeze the tile role map: make it a pure function of the unlocked quadrants
    # rather than of cash and herd size, so a tile cannot change crop mid-life and
    # strand a growing plant. Needs a self-clearing filler (see role_filler).
    "freeze_roles": False,
    "role_filler": "WHEAT",
    # MEASURED AND DISABLED. Per-day planting quota (stateless, read off
    # planted_day). Scored +$2,268 mean / +$5,187 floor against `starter` -- and
    # 80% worst matchup against REAL opponents, against the control's 90%.
    # Classic v7-v10 trap: a gain against the weak baseline that does not survive
    # real builds. Note also it did NOT reduce weeds (14.8 either way), so the
    # mechanism I proposed for it was wrong regardless.
    # Mechanism kept, quota empty = unlimited.
    "plant_quota": {},
    "max_seed_stock": 10,
    "seed_reserve_frac": 0.5,        # share of the reserve seed buying must respect
    "seed_buy_rate": 2,              # max premium seeds bought per turn (rate, not level)
    "premium_seed_cost": 80,         # seeds at/above this are rate-limited
    # Clearing a weed is priced as a FRACTION of what replanting that tile earns,
    # because 57% of weeds are spent strawberry and the tile is worth ~$1,156
    # replanted. A flat value loses every labour auction to milk/egg harvests.
    # 0.15 measured best on BOTH mean and worst case (+$5.2k / +$5.1k over a flat
    # value). Non-monotonic: 0.30 dips hard. And note clearing ALL weeds is NOT
    # optimal — frac 0.30-1.00 cuts weeds to ~2 tiles and earns LESS than 0.15
    # leaving ~19 standing. Those actions are worth more on milk and strawberry.
    "weed_clear_frac": 0.0,
    "weed_clear_value": 35.0,     # fallback for non-crop roles

    # --- Land ---------------------------------------------------------------
    "land_reserve": 600.0,
    # MEASURED AND KEPT AT 0 (i.e. no delay). The public advice and the winner
    # boards both say hold land until day 4+ so the opening funds livestock.
    # For US it is catastrophic: land>=4/6/8 all score $49,960 against $85,970.
    # We run 12 hands with a ~84-tile labour ceiling, so one quadrant (25 tiles)
    # leaves the crew with nothing to do. Winners run fewer tiles with far better
    # per-action efficiency; their land timing starves our build.
    "land_first_day": 0,
    "buy_land_last_day": 20,
    "land_saturation": 0.9,          # only buy land once labour outgrows what we own

    # --- Selling ------------------------------------------------------------
    "wheat_feed_reserve_days": 3.0,
    "min_sell_price": 2,
    "endgame_days": 2,               # stop investing, liquidate
    # METERED SELLING: MEASURED AS NOT WORTH IT, left at 0 (disabled).
    # The theory was sound — dumping premium goods walks them down their own
    # curve — but withholding costs more than it saves: the shed caps at 100 and
    # discards overflow, and delayed sales lose their compounding. Gauntlet:
    # disabled 92% ALL / 58% worst / $56.0k vs enabled 91% / 54% / $55.3k.
    # Kept as a tunable rather than deleted, in case a future build holds less.
    "sell_min_price_frac": 0.0,
    # ...unless the shed is close to its 100 cap, where overflow is discarded at
    # end of day and a cheap sale beats losing the goods outright.
    "shed_pressure_cap": 80,
    # MEASURED AND DISABLED (second failed attempt at metering).
    # Theory: price impact is permanent but the town drains continuously, so
    # splitting a sale across turns should let the price recover between batches.
    # It does not pay. batch 8 scored $74,300 / $66,444 min, batch 5 $74,750 /
    # $64,817, against an unbatched $74,952 / $67,188. Combined with wheat
    # fertilising it was worse still ($71,374 / $60,107).
    # The earlier withhold-below-a-floor variant also failed. Two different
    # metering mechanisms, both negative -- stop proposing a third without a new
    # reason. Delay costs more than price impact saves, most likely because the
    # shed caps at 100 and unsold stock scores zero at day 30.
    "sell_batch": 99999,
    "metered_products": (),
    # MELON is the exception: town takes only ~140/season and no shop demands it,
    # so its pot really is a fixed race against the opponent. Dump on sight.
    "race_products": ("MELON",),
}


def merge(overrides=None):
    p = dict(DEFAULTS)
    if overrides:
        p.update(overrides)
    return p
