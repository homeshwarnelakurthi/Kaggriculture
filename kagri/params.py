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
    # Livestock ranked by revenue per identical action+feed cost, at base price:
    #   SHEEP $254/day   COW $208/day   GOOSE $94/day
    # A sheep is 2.7x a goose for the same work. Geese were only ever preferred
    # because EGG is an unbounded sink — but town demand (438 milk, 335 wool per
    # season) keeps milk and wool near or above base too, and they are worth
    # 3-4x per unit. Buy sheep first, then cows, then geese.
    "target_sheep": 6,
    "target_cows": 10,
    "target_geese": 4,
    "feed_per_animal_day": 1.0,
    "wheat_buffer_per_animal": 3.0,  # shed wheat per animal before expanding
    "wheat_lead_tiles": 4,           # wheat tiles must lead animal count by this
    "coop_lead": 2,                  # empty coops allowed ahead of the birds
    "animal_carry": 3,               # animals one unit ferries per shed trip
    "wheat_carry": 8,                # wheat one unit ferries per feeding round
    "drop_threshold": 5,             # carried produce that triggers a shed run

    # --- Crops --------------------------------------------------------------
    "wheat_units_per_tile_day": 0.9,
    "wheat_tiles_per_animal": 1.15,
    "wheat_tile_share": 0.6,         # hard cap: fraction of land given to wheat
    "min_wheat_tiles": 8,
    # Absolute wheat target, independent of flock size. Wheat sells for ~$35 per
    # action (same as an egg) with none of the capital, build or starvation risk,
    # and town demand of ~639 units/season keeps its price climbing all game.
    "wheat_tiles_target": 38,
    # Melon is a FIXED, SHARED pot (~$26.5k, floors near 200 units), so taking
    # it faster both earns and denies. Self-play is monotonic in melon acreage:
    # 16 tiles 65%, 20 tiles 73%, 24 tiles 90% against the 10-tile baseline.
    "melon_tiles": 16,
    # OFF by default. At 14 tiles this cost ~$28k vs starter: seed is $100/tile
    # and the livestock had already spent the capital, so the tiles were reserved,
    # never planted, and weeded over — while squeezing melon out entirely.
    # Reserving land for a crop we cannot afford is worse than not reserving it.
    "strawberry_tiles": 0,
    "straw_last_plant_day": 17,
    "melon_first_day": 0,            # melon pays nothing for 10 days
    "melon_last_plant_day": 16,
    "carrot_fill": True,
    "max_seed_stock": 10,
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
