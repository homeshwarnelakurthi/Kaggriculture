"""Top-level policy: market orders + unit assignment."""

from .constants import ANIMALS, CROPS, MARKET_PARAMS
from .farm import View, bfs_field, plan_layout, step_toward
from .market import marginal_value, price
from .params import merge
from .plan import economics
from .tasks import generate

MAX_ORDERS = 10


def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# --------------------------------------------------------------------------
# Market
# --------------------------------------------------------------------------

def plan_market(view, p, plan):
    """Orders commit in list order and money updates as they commit, so sells
    go first — today's harvest funds today's expansion in the same turn.

    Every purchase below must leave `plan.reserve` in the bank. That single
    rule is what prevents the day-0 over-investment spiral: broke means no
    hands, no hands means no watering, and the whole farm rots.
    """
    orders = []
    # Count birds we OWN, not just the ones already standing in a coop. Sizing
    # feed off placed animals alone sells the wheat out from under a flock
    # still waiting in the shed, and they starve the day they are placed.
    animals = view.count_animals() + sum(view.shed.get(k, 0) + view.carried(k)
                                         for k in ANIMALS)
    # Keep feed back unless the season is over and wheat is just inventory.
    feed_reserve = 0 if plan.endgame else int(round(animals * p["wheat_feed_reserve_days"]))

    # --- sell -------------------------------------------------------------
    shed_total = sum(view.shed.values())
    under_pressure = shed_total >= p["shed_pressure_cap"] or plan.endgame
    sellable = []
    for item, n in view.shed.items():
        if n <= 0 or item in ANIMALS:
            continue
        qty = n - feed_reserve if item == "WHEAT" else n
        if item == "FERTILIZER":
            # Do not sell the input that doubles strawberry yield ($480 -> $960
            # per tile). Animals produce it free, so keep enough on hand to
            # cover every plant currently worth fertilising.
            qty = n - min(n, getattr(view, "n_fertilize_targets", 0) + p["fert_reserve"])
        if qty <= 0:
            continue
        qty = _meterable(item, view.minv.get(item, 10000), qty, p, under_pressure)
        # Batch cap. Price impact is permanent, but the town drains continuously,
        # so splitting a big sale across turns lets the price recover between
        # batches and raises the average. Distinct from withholding, which was
        # measured worthless: same volume, just paced.
        if not under_pressure and item in p["metered_products"]:
            qty = min(qty, int(p["sell_batch"]))
        if qty <= 0:
            continue
        unit = marginal_value(item, view.minv.get(item, 10000), min(qty, 8))
        if unit < p["min_sell_price"]:
            continue
        rush = 2.0 if item in p["race_products"] else 1.0
        sellable.append((unit * qty * rush, item, qty))
    sellable.sort(reverse=True)
    for _, item, qty in sellable[:5]:
        orders.append(["SELL", item, qty])

    # --- emergency feed ---------------------------------------------------
    # Losing a $300 goose to one missed feed dwarfs any wheat price.
    held = view.shed.get("WHEAT", 0) + view.carried("WHEAT")
    short = animals * 2 - held
    if animals and short > 0 and view.money > plan.reserve * 0.5:
        orders.append(["BUY_PRODUCT", "WHEAT", int(short)])

    if plan.endgame:
        return orders[:MAX_ORDERS]

    # --- labour -----------------------------------------------------------
    # Cheapest lever in the game; hire before anything else discretionary.
    if view.hour <= 2 and view.money > p["hire_money_floor"]:
        for _ in range(max(0, plan.target_hands - view.hires_today)):
            if len(orders) >= MAX_ORDERS:
                break
            orders.append(["HIRE"])

    # --- land -------------------------------------------------------------
    if plan.allow_land:
        orders.append(["BUY_LAND"])

    # --- animals ----------------------------------------------------------
    # Highest value per action first: sheep ($254/day), cow ($208), goose ($94).
    for kind in ("SHEEP", "COW", "GOOSE"):
        have = (view.count_animals(kind) + view.shed.get(kind, 0)
                + view.carried(kind))
        want = plan.want_by_animal.get(kind, 0) - have
        # Animals may dip into the reserve, like premium seed. The reserve is
        # ~$926 and a cow is $400, so a full gate forbids any livestock until
        # ~day 12 -- while the winners sit at $131-651 for ten days buying cows
        # continuously and are 3.4 animals ahead by day 8. The earlier attempt at
        # this caused death spirals, but that was seeds with an UNBOUNDED rate;
        # animal_buy_rate now paces purchases, which is what made seeds safe.
        budget = view.money - plan.reserve * p["animal_reserve_frac"]
        # Rate-limited, like premium seed. Buying four cows at once ($1,600) in
        # one turn starves the strawberry pipeline; the same money spread over
        # several days does not. Level gates keep failing here — pace instead.
        n = min(want, int(budget // ANIMALS[kind]["cost"]) if budget > 0 else 0,
                int(p["animal_buy_rate"]))
        if n > 0:
            orders.append(["BUY_ANIMAL", kind, n])
            break  # one species per turn; re-evaluate against the new balance

    # --- seeds ------------------------------------------------------------
    for crop, need in sorted(_seed_needs(view, p).items()):
        if need <= 0:
            continue
        cost = CROPS[crop]["seed"]
        # Seed may dip into the reserve, but only at a bounded RATE. The failure
        # mode is not the level, it is the lump: allowing the full bank bought
        # 24 strawberry seeds ($2,400 of $3,000) on day 0 and killed the farm.
        # The top players spend the same money trickled over ten days while
        # sitting at $131-689, so cap purchases per turn instead.
        budget = view.money - plan.reserve * p["seed_reserve_frac"]
        # Cap the seed stockpile: unplanted seed is dead money, and low-value
        # crops legitimately lose the labour auction to the animal engine.
        room = max(0, p["max_seed_stock"] - view.seeds.get(crop, 0))
        rate = p["seed_buy_rate"] if cost >= p["premium_seed_cost"] else 99
        n = min(need, room, rate, int(budget // cost) if budget > 0 else 0)
        if n > 0:
            orders.append(["BUY_SEED", crop, n])

    return orders[:MAX_ORDERS]


def _meterable(item, inv, have, p, under_pressure):
    """How many units to sell now without tanking our own price.

    The town drains every product continuously (438 milk, 335 wool, 537
    strawberry per season), so supplying at roughly that rate holds price at or
    above base — milk was observed at $365 against a $160 base. Dumping the same
    goods in one order walks them straight down their own curve instead.

    Staples on log curves barely move, so this returns everything for them; it
    only bites on the premium goods where it matters.
    """
    if under_pressure:
        return have  # shed overflow is discarded at end of day: a cheap sale beats losing it
    floor = MARKET_PARAMS[item]["base"] * p["sell_min_price_frac"]
    sold, sim = 0, inv
    while sold < have:
        pr = price(item, sim)
        if pr < floor:
            break
        sold += 1
        if pr > 1:
            sim += 1
    return sold


def _seed_needs(view, p):
    """Seeds required to plant every empty tile currently assigned to a crop."""
    roles = view.roles
    need = {}
    for pos, role in roles.items():
        if role in CROPS and view.tile(*pos) is None:
            need[role] = need.get(role, 0) + 1
    for crop in list(need):
        need[crop] = max(0, need[crop] - view.seeds.get(crop, 0))
    return need


# --------------------------------------------------------------------------
# Unit assignment
# --------------------------------------------------------------------------

def assign(view, tasks, p):
    """Match units to jobs on `value - travel * distance`, using BFS distances.

    Previously this walked tasks in value order and gave each to the NEAREST
    capable unit, with distance never entering the job's worth. A unit would
    cross the board for a $12 weed clear while a $95 cow harvest three tiles away
    went unserved. Distance is also measured by BFS now: once NE and SW are
    owned the farm is an L-shape, so Manhattan under-counts exactly the trips
    that waste the most actions.
    """
    n = view.n_units
    actions = [["PASS"] for _ in range(n)]
    free = set(range(n))
    claimed = set()
    planted = {}

    use_bfs = p["assign_bfs"]
    fields = ({u: bfs_field(view, view.positions[u]) for u in range(n)}
              if use_bfs else None)
    # TERRITORIES. 66% of every action we take is walking and only 23% is work.
    # With all units competing globally for every job they criss-cross the farm.
    # Anchor each unit to a home tile and charge a penalty for leaving its patch,
    # so a unit prefers the jobs beside it. Urgent work (RESCUE-priced: a
    # starving animal, a plant that dies tonight) is exempt -- those must always
    # be servable from anywhere.
    homes = _territories(view, p) if p["territory_pull"] > 0 else None
    tasks.sort(key=lambda t: (-t["value"], t["pos"]))

    # Two passes. Tasks needing a carried item (FEED needs wheat, PLACE needs
    # the animal) go first, restricted to units already holding it — otherwise
    # the one unit carrying a $300 goose gets grabbed for the nearest watering
    # job and the bird never reaches its coop.
    ordered = [t for t in tasks if t["needs"]] + [t for t in tasks if not t["needs"]]

    for task in ordered:
        if not free:
            break
        key = (task["pos"], task["op"], tuple(task["args"]))
        if key in claimed:
            continue
        # Atomic PLANT rule: exceeding seed count drops EVERY plant order for
        # that crop this turn, so never queue more than we hold.
        if task["op"] == "PLANT":
            crop = task["args"][0]
            if planted.get(crop, 0) >= view.seeds.get(crop, 0):
                continue
        needs = task["needs"]
        best, bestscore = None, None
        for u in sorted(free):
            if needs and view.inv(u).get(needs[0], 0) < needs[1]:
                continue
            if use_bfs:
                d = fields[u][0].get(task["pos"])
                if d is None:
                    continue  # unreachable: locked quadrant, or trapped hand
            else:
                d = _dist(view.positions[u], task["pos"])
            score = task["value"] - d * p["travel_cost"]
            if homes is not None and task["value"] < RESCUE_FLOOR:
                # distance from this unit's HOME, not its current position:
                # penalises drifting off-patch rather than the current step
                hx, hy = homes[u]
                score -= (abs(hx - task["pos"][0]) + abs(hy - task["pos"][1])) * p["territory_pull"]
            if score <= 0 and d > 0:
                continue  # the walk costs more than the job is worth
            # Tie-break on distance, else a zero travel_cost makes every unit
            # score identically and the lowest INDEX always wins rather than the
            # nearest -- which collapsed results to $29k when first measured.
            key = (score, -d)
            if bestscore is None or key > bestscore:
                best, bestscore = u, key
        if best is None:
            continue
        act = _act_for(view, best, task, fields[best] if use_bfs else None)
        if act is None:
            continue
        actions[best] = act
        free.discard(best)
        claimed.add(key)
        if task["op"] == "PLANT" and act[0] == "PLANT":
            planted[task["args"][0]] = planted.get(task["args"][0], 0) + 1

    _assign_logistics(view, actions, free, p)
    return actions



RESCUE_FLOOR = 9_000.0   # tasks at or above this are emergencies; ignore territory


def _territories(view, p):
    """Give every unit a home tile, spreading them over the worked area.

    Sort candidate tiles by distance from the shed (the same ordering the layout
    uses, so homes land where the work is) and deal them round-robin. Cheap,
    stateless, and recomputed each turn -- units drift toward their patch rather
    than being fenced into it.
    """
    live = []
    for (x, y) in view.unlocked_tiles():
        t = view.tile(x, y)
        if isinstance(t, dict) and t.get("kind") in ("PLANT", "COOP", "PASTURE"):
            live.append((x, y))
    if not live:
        return {u: view.positions[u] for u in range(view.n_units)}
    live.sort(key=lambda c: (view.shed_dist(*c), c[1], c[0]))
    step = max(1, len(live) // max(1, view.n_units))
    return {u: live[min(u * step, len(live) - 1)] for u in range(view.n_units)}

def _act_for(view, u, task, field=None):
    pos = view.positions[u]
    if pos == task["pos"]:
        return [task["op"]] + task["args"]
    if field is not None:
        mv = field[1].get(task["pos"])
        if mv:
            return [mv]
    mv = step_toward(view, pos, task["pos"])
    return [mv] if mv else None


def _assign_logistics(view, actions, free, p):
    """Idle units fetch feed, fetch animals, or run harvest back to the shed."""
    if not free or not view.shed_tiles:
        return

    for u in sorted(free):
        pos = view.positions[u]
        inv = view.inv(u)
        target = min(view.shed_tiles, key=lambda t: _dist(pos, t))
        at_shed = pos in view.shed_tiles

        # Shed cap is 100 and end-of-day overflow is discarded, so run produce
        # in during the day rather than hoarding it on unit inventories.
        carried = sum(v for k, v in inv.items() if k not in ANIMALS)
        if carried >= p["drop_threshold"]:
            actions[u] = ["DROP"] if at_shed else [step_toward(view, pos, target) or "PASS"]
            continue

        # Idle: wait at the shed, where tomorrow's fetch and drop jobs start.
        if not at_shed:
            actions[u] = [step_toward(view, pos, target) or "PASS"]


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def act(obs, overrides=None):
    p = merge(overrides)
    view = View(obs)
    view.plan = economics(view, p)
    view.roles = plan_layout(view, p, view.plan)
    tasks = generate(view, view.roles, p, view.plan)
    market = plan_market(view, p, view.plan)
    actions = assign(view, tasks, p)
    return {"farmer": actions[0], "hands": actions[1:], "market": market}
