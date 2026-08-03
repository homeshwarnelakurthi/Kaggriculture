"""Turn-level task generation.

Every actionable thing on the farm becomes a task with a dollar value, then
assignment is just "nearest capable unit takes the most valuable job". Values
are real marginal revenue from the market model, not spot price, so the agent
never over-rates a product whose price is about to collapse under its own sales.
"""

from .constants import ANIMALS, CROPS
from .market import marginal_value

# Losing a mature animal or a near-harvest melon is catastrophic; price these
# rescue jobs far above any ordinary revenue task so they always win.
RESCUE = 10_000.0


def _crop_unit_value(view, crop):
    return marginal_value(crop, view.minv.get(crop, 10000), 4)


def _product_unit_value(view, product):
    return marginal_value(product, view.minv.get(product, 10000), 4)


def _plant_replacement_value(view, tile):
    """Roughly what this plant is still worth if kept alive."""
    crop = tile["crop"]
    cd = CROPS[crop]
    remaining = max(1, cd["max_yield"] - tile.get("yield_units", 0))
    return _crop_unit_value(view, crop) * remaining


def generate(view, roles, p, plan):
    tasks = []

    def add(value, pos, op, args=(), needs=None):
        if value > 0:
            tasks.append({"value": value, "pos": pos, "op": op,
                          "args": list(args), "needs": needs})

    fert_value = _product_unit_value(view, "FERTILIZER")
    n_unfed = 0
    urgent_feed = False

    for y in range(view.board):
        for x in range(view.board):
            t = view.tile(x, y)
            pos = (x, y)

            if t == "LOCKED":
                continue

            if isinstance(t, dict) and t.get("kind") == "WEED":
                # A weed squats on a tile we planned to use. Worth roughly what
                # that tile earns before the season ends, not a flat token value.
                want = roles.get(pos)
                days_left = 30 - view.day
                add(p["weed_clear_value"] if want and days_left > 4 else 6.0,
                    pos, "DIG")
                continue

            # ---------------- animals ----------------
            if isinstance(t, dict) and "animal" in t:
                a = ANIMALS[t["animal"]]
                prod_val = _product_unit_value(view, a["product"])

                if not t.get("fed_today"):
                    n_unfed += 1
                    # consecutive_unfed 1 means it escapes tonight if unfed.
                    urgent = t.get("consecutive_unfed", 0) >= 1
                    urgent_feed = urgent_feed or urgent
                    add(RESCUE + a["cost"] if urgent else prod_val * 2.0,
                        pos, "FEED", needs=("WHEAT", 1))

                if t.get("yield_units", 0) > 0:
                    # Harvest hard when at max_held: further production is lost.
                    at_cap = t["yield_units"] >= a["max_held"]
                    add(prod_val * t["yield_units"] * (2.0 if at_cap else 1.0),
                        pos, "HARVEST")

                if t.get("fertilizer_available"):
                    add(fert_value, pos, "COLLECT_FERTILIZER")

                if not t.get("cared_today"):
                    # CARE banks +1 unit toward the next production tick.
                    add(prod_val * 0.9, pos, "CARE")
                continue

            # ------------- empty structures -------------
            if isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE"):
                for animal, a in ANIMALS.items():
                    if a["structure"] != t["kind"]:
                        continue
                    if view.inv_any(animal) or view.shed.get(animal, 0) > 0:
                        add(a["cost"] * 1.5, pos, "PLACE", [animal], needs=(animal, 1))
                        break
                continue

            # ---------------- plants ----------------
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                crop = t["crop"]
                cd = CROPS[crop]
                age = view.day - t["planted_day"]
                unit_val = _crop_unit_value(view, crop)

                if not t.get("watered_today"):
                    # consecutive_unwatered starts at 1 on the planting day, so
                    # a fresh plant MUST be watered today or it dies tonight.
                    if t.get("consecutive_unwatered", 0) >= 1:
                        add(RESCUE + _plant_replacement_value(view, t), pos, "WATER")
                    else:
                        ws = (cd["max_yield_day"] + 1) // 2
                        in_window = (not cd["ongoing"]) and ws <= age <= cd["max_yield_day"]
                        add(unit_val * 1.2 if in_window else unit_val * 0.3, pos, "WATER")

                ready = t.get("yield_units", 0) > 0 and age >= cd["first_yield_day"]
                if ready:
                    maxed = t["yield_units"] >= cd["max_yield"]
                    past = (not cd["ongoing"]) and age >= cd["max_yield_day"]
                    if cd["ongoing"] or maxed or past:
                        # Decay ticks every 2 steps once past lifespan — do not dawdle.
                        urgency = 2.5 if past else 1.0
                        add(unit_val * t["yield_units"] * urgency, pos, "HARVEST")
                continue

            # ---------------- empty land ----------------
            if t is None:
                role = roles.get(pos)
                if role == "ANIMAL":
                    want = _next_structure(view, plan)
                    if want:
                        add(90.0, pos, want)
                elif role in CROPS:
                    if view.seeds.get(role, 0) > 0 and _plantable(view, role, p):
                        cd = CROPS[role]
                        profit = _crop_unit_value(view, role) * cd["max_yield"] - cd["seed"]
                        span = max(1, cd["max_yield_day"] or cd["first_yield_day"])
                        add(max(5.0, profit / span), pos, "PLANT", [role])

    view.n_unfed = n_unfed
    _add_shed_tasks(view, p, add, n_unfed, urgent_feed)
    return tasks


def _add_shed_tasks(view, p, add, n_unfed, urgent_feed):
    """Fetching feed and ferrying livestock must compete on value like anything
    else. Left as an idle-unit fallback they never happen: with a full field
    there are no idle units, so the flock starves while everyone waters crops.
    """
    if not view.shed_tiles:
        return

    short = n_unfed - view.carried("WHEAT")
    stock = view.shed.get("WHEAT", 0)
    if short > 0 and stock > 0:
        # An unfed animal on its second day escapes tonight — price the fetch
        # that prevents it just under the rescue itself.
        value = RESCUE * 0.9 if urgent_feed else 60.0
        trips = min(len(view.shed_tiles), -(-short // p["wheat_carry"]))
        take = min(stock, short, p["wheat_carry"])
        for st in view.shed_tiles[:trips]:
            add(value, st, "PICKUP", ["WHEAT", int(take)])

    for animal, spec in ANIMALS.items():
        idle = min(view.shed.get(animal, 0) - view.carried(animal),
                   view.empty_structures(spec["structure"]))
        if idle <= 0:
            continue
        # Every bird sitting in the shed is $300 earning nothing.
        take = min(idle, p["animal_carry"])
        trips = min(len(view.shed_tiles), -(-idle // p["animal_carry"]))
        for st in view.shed_tiles[:trips]:
            add(spec["cost"] * 1.2, st, "PICKUP", [animal, int(take)])


def _plantable(view, crop, p):
    """Will this crop still reach a harvest before the season ends?"""
    cd = CROPS[crop]
    days_left = 30 - view.day
    if crop == "MELON":
        return view.day <= p["melon_last_plant_day"] and days_left >= cd["first_yield_day"]
    if crop == "STRAWBERRY":
        # Needs 10 days to first yield, then fires on days 10/12/14/16.
        return view.day <= p["straw_last_plant_day"] and days_left >= cd["first_yield_day"]
    return days_left > cd["first_yield_day"]


def _next_structure(view, plan):
    """Build only just ahead of the animals we can actually feed.

    An empty structure is a tile not growing wheat, and wheat is what limits the
    herd — so overbuilding actively shrinks the engine. Pastures come first:
    they hold sheep and cows, worth 2-3x a goose for identical work.
    """
    if view.count_structures("PASTURE") < plan.want_pastures:
        return "BUILD_PASTURE"
    if view.count_structures("COOP") < plan.want_coops:
        return "BUILD_COOP"
    return None
