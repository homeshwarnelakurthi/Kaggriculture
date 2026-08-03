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
    "target_geese": 22,
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
    "wheat_tile_share": 0.5,         # hard cap: fraction of land given to wheat
    "min_wheat_tiles": 8,
    "melon_tiles": 10,               # melon floors at ~200 units — cap it
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
    # Floor-crashing goods are a race against the opponent: dump on sight.
    "race_products": ("MELON", "STRAWBERRY", "MILK", "WOOL"),
}


def merge(overrides=None):
    p = dict(DEFAULTS)
    if overrides:
        p.update(overrides)
    return p
