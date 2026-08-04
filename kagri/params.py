"""Tunable strategy parameters.

Everything the self-play tuner is allowed to search over lives here, as a flat
dict of scalars so CMA-ES / random search can drive it without touching logic.
"""

DEFAULTS = {
    # --- Labour -------------------------------------------------------------
    # 10 hands cost $143 for a whole day and buy 240 actions. Labour is the
    # cheapest thing in the game; being short of it is what kills runs.
    "hand_value_per_action": 6.0,
    "max_hands": 12,
    # Eight hands cost $54 total; twelve cost $376. Almost never worth skipping,
    # so the floor is deliberately tiny — the fib curve is the real cap.
    "hire_money_floor": 30.0,
    "hire_bank_fraction": 0.30,     # never spend more than this share of the bank on a crew
    "tiles_per_unit": 7.0,          # tiles one unit can meaningfully tend/day
    "animal_labour_cost": 2.5,      # an animal tile costs ~2.5 crop tiles of work

    # --- Cash discipline ----------------------------------------------------
    # Never spend below this. A full day of hands is added on top automatically.
    "ops_reserve_base": 350.0,
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
    "target_sheep": 0,
    "target_cows": 12,
    "target_geese": 0,
    "feed_per_animal_day": 1.0,
    "wheat_buffer_per_animal": 3.0,  # shed wheat per animal before expanding
    "wheat_lead_tiles": 4,           # wheat tiles must lead animal count by this
    "coop_lead": 2,                  # empty coops allowed ahead of the birds
    # Buy one animal per turn, not four. Measured +$1,474 mean and +$4,470 on the
    # WORST case (6 seeds). Note this is a per-TURN cap and there are 24 turns a
    # day, so it is a gentle brake on lump spending rather than a real daily
    # limit — it does not fix the cow shortfall (see DEV.md on milk).
    "animal_buy_rate": 1,
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
    "fertilize_min_gain": 90.0,
    "drop_threshold": 5,             # carried produce that triggers a shed run

    # --- Crops --------------------------------------------------------------
    "wheat_units_per_tile_day": 0.9,
    "wheat_tiles_per_animal": 1.15,
    "wheat_tile_share": 0.6,         # hard cap: fraction of land given to wheat
    "min_wheat_tiles": 8,
    # Absolute wheat target, independent of flock size. Wheat sells for ~$35 per
    # action (same as an egg) with none of the capital, build or starvation risk,
    # and town demand of ~639 units/season keeps its price climbing all game.
    "wheat_tiles_target": 16,
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
    "strawberry_tiles": 28,
    "straw_last_plant_day": 17,
    "melon_first_day": 0,            # melon pays nothing for 10 days
    "melon_last_plant_day": 16,
    # MUST stay False. Carrot filler occupies tiles strawberry cannot yet afford
    # and never yields them back — the mechanism behind strawberry previously
    # "destabilising" the allocator (3 planted of 35, 24 tiles of carrot).
    "carrot_fill": False,
    "max_seed_stock": 10,
    "seed_reserve_frac": 0.5,        # share of the reserve seed buying must respect
    "seed_buy_rate": 3,              # max premium seeds bought per turn (rate, not level)
    "premium_seed_cost": 80,         # seeds at/above this are rate-limited
    "weed_clear_value": 35.0,

    # --- Land ---------------------------------------------------------------
    "land_reserve": 600.0,
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
    # MELON is the exception: town takes only ~140/season and no shop demands it,
    # so its pot really is a fixed race against the opponent. Dump on sight.
    "race_products": ("MELON",),
}


def merge(overrides=None):
    p = dict(DEFAULTS)
    if overrides:
        p.update(overrides)
    return p
