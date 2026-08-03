"""Economic phase planning.

The single most dangerous mistake in this game is buying the engine before you
can run it. Animals cost $300-500 and eat 1 wheat/day *each*; if the bank runs
dry you cannot hire hands, without hands you cannot water, the field rots to
weeds, and the livestock starves. Every purchase here is gated on demonstrated
capacity to feed and work what we already own.
"""

from .constants import ANIMALS, LAND_PRICES, LAND_ORDER, cumulative_hire_cost, fib

SEASON_DAYS = 30


def target_hands(view, p):
    """Hire while the marginal hand's fib cost is worth a day of its actions.

    Two separate guards, and both are needed. The flat floor stops us hiring
    with an empty bank; the bank-fraction cap stops the opposite failure, where
    a $609 crew looks affordable against $640 and eats the money that was meant
    to buy seed and feed. Without it the fib curve happily bankrupts the farm.
    """
    budget = min(view.money - p["hire_money_floor"],
                 view.money * p["hire_bank_fraction"])
    best = 0
    for k in range(1, int(p["max_hands"]) + 1):
        if fib(k - 1) > p["hand_value_per_action"] * 24:
            break
        if cumulative_hire_cost(k) > budget:
            break
        best = k
    return best


class Plan:
    __slots__ = ("days_left", "reserve", "want_animals", "want_coops",
                 "allow_land", "want_wheat_tiles", "want_melon_tiles",
                 "wheat_flow", "endgame", "target_hands", "workable")

    def __repr__(self):
        return (f"Plan(animals={self.want_animals} coops={self.want_coops} "
                f"wheat={self.want_wheat_tiles} melon={self.want_melon_tiles} "
                f"land={self.allow_land} reserve={self.reserve:.0f})")


def economics(view, p):
    """Decide what we are allowed to buy this turn."""
    pl = Plan()
    pl.days_left = SEASON_DAYS - view.day
    animals_now = view.count_animals()
    pl.endgame = pl.days_left <= p["endgame_days"]

    # Hiring is funded FIRST and gated only by a small floor. It must not be
    # gated on `reserve`, because `reserve` exists in order to pay for hiring —
    # making it a precondition deadlocks the farm at zero hands.
    pl.target_hands = target_hands(view, p)

    # Cash discretionary spending must never dip below: tomorrow's crew plus a
    # feed buffer. Going below this is what triggers the death spiral.
    pl.reserve = (p["ops_reserve_base"]
                  + cumulative_hire_cost(pl.target_hands)
                  + p["ops_reserve_per_animal"] * animals_now)

    # Labour ceiling. Planting more land than the crew can water is strictly
    # worse than leaving it fallow: the seed money is spent, the tile still
    # rots to a weed, and clearing the weed costs another action later.
    expected_units = 1 + max(pl.target_hands, view.n_units - 1)
    pl.workable = max(6, int(expected_units * p["tiles_per_unit"]))

    # --- how much wheat can we actually put on the table? -----------------
    wheat_plants = view.count_plants("WHEAT")
    wheat_stock = view.shed.get("WHEAT", 0) + view.carried("WHEAT")
    pl.wheat_flow = wheat_plants * p["wheat_units_per_tile_day"]

    # --- animals ----------------------------------------------------------
    # Only expand the flock when wheat is comfortably ahead of demand and the
    # bird still has time to pay back its $300 (4 days to first egg).
    can_feed = (wheat_stock >= animals_now * p["wheat_buffer_per_animal"]
                and wheat_plants >= animals_now + p["wheat_lead_tiles"])
    if pl.days_left < p["min_days_for_animal"] or view.day < p["bootstrap_days"]:
        pl.want_animals = animals_now
    elif can_feed:
        by_feed = int(pl.wheat_flow / max(0.1, p["feed_per_animal_day"]))
        pl.want_animals = min(p["target_geese"], max(animals_now, by_feed))
    else:
        pl.want_animals = animals_now

    # Build coops just ahead of the birds, never far ahead — an empty coop is
    # a tile that could have been growing their feed.
    pl.want_coops = min(p["target_geese"],
                        animals_now + view.shed.get("GOOSE", 0) + p["coop_lead"])

    # --- land -------------------------------------------------------------
    # Also quietly fixes the (h,h) hand-spawn trap, which costs us a hand a day.
    n_extra = len(view.unlocked) - 1
    pl.allow_land = False
    if n_extra < len(LAND_ORDER) and view.day <= p["buy_land_last_day"]:
        cost = LAND_PRICES[n_extra]
        # Do not buy land we have no labour to farm — extra tiles we cannot
        # tend just grow weeds and cost actions to clear.
        saturated = pl.workable > p["land_saturation"] * len(view.unlocked_tiles())
        if view.money >= cost + pl.reserve + p["land_reserve"] and saturated:
            pl.allow_land = True

    # --- tile budget ------------------------------------------------------
    tiles = len(view.unlocked_tiles())
    pl.want_wheat_tiles = min(int(tiles * p["wheat_tile_share"]),
                              max(p["min_wheat_tiles"],
                                  int(round(p["target_geese"] * p["wheat_tiles_per_animal"]))))
    # Melon pays nothing for 10 days. Planting it during the cash-starved
    # opening starves the flock of capital exactly when birds compound hardest.
    if p["melon_first_day"] <= view.day <= p["melon_last_plant_day"] and pl.days_left >= 11:
        pl.want_melon_tiles = p["melon_tiles"]
    else:
        pl.want_melon_tiles = 0

    # Clamp the whole tile budget to what the crew can actually service.
    # Animals are the most action-hungry role, so they claim their share first.
    budget = pl.workable
    animal_slots = min(pl.want_coops, int(budget / p["animal_labour_cost"]))
    budget -= int(animal_slots * p["animal_labour_cost"])
    pl.want_coops = animal_slots
    pl.want_wheat_tiles = max(0, min(pl.want_wheat_tiles, budget))
    budget -= pl.want_wheat_tiles
    pl.want_melon_tiles = max(0, min(pl.want_melon_tiles, budget))
    return pl
