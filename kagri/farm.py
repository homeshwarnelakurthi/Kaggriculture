"""Observation parsing, farm layout planning, and movement."""

from .constants import (
    ANIMALS, CROPS, DELTA_TO_MOVE, MOVES, quadrant_of, shed_access_tiles,
)


def g(obs, key, default=None):
    """Observations arrive as dicts or Struct-likes depending on the caller."""
    if isinstance(obs, dict):
        return obs.get(key, default)
    return getattr(obs, key, default)


class View:
    """Flattened, convenient read of one turn's observation."""

    def __init__(self, obs):
        self.obs = obs
        self.player = g(obs, "player", 0)
        self.day = g(obs, "day", 0)
        self.hour = g(obs, "hour", 0)
        self.step = g(obs, "step", self.day * 24 + self.hour)

        farms = g(obs, "farms", []) or []
        self.farm = farms[self.player]
        self.opp = farms[1 - self.player] if len(farms) > 1 else None

        self.tiles = self.farm["tiles"]
        self.board = len(self.tiles)
        self.money = self.farm["money"]
        self.unlocked = list(self.farm.get("unlocked_quadrants", ["NW"]))
        self.hires_today = self.farm.get("hires_today", 0)

        private = g(obs, "private", {}) or {}
        self.shed = dict(private.get("shed", {}) or {})
        self.seeds = dict(private.get("seeds", {}) or {})
        self.invs = [dict(i or {}) for i in (private.get("inventories", [{}]) or [{}])]

        market = g(obs, "market", {}) or {}
        self.prices = dict(market.get("prices", {}) or {})
        self.minv = dict(market.get("inventory", {}) or {})

        town = g(obs, "town", {}) or {}
        self.shops = list(town.get("unlocked_shops", []) or [])

        # unit 0 is the main farmer; 1..n are the hands hired today
        self.positions = [tuple(self.farm["farmer"])]
        self.positions += [tuple(p) for p in self.farm.get("hands", [])]
        self.n_units = len(self.positions)

        self.shed_tiles = [t for t in shed_access_tiles(self.board) if self.is_open(*t)]

    # -- tile helpers ------------------------------------------------------
    def tile(self, x, y):
        return self.tiles[y][x]

    def is_open(self, x, y):
        """Unlocked (walkable). LOCKED tiles block movement and all tile ops."""
        return self.tiles[y][x] != "LOCKED"

    def inv(self, idx):
        return self.invs[idx] if idx < len(self.invs) else {}

    def unlocked_tiles(self):
        return [(x, y) for y in range(self.board) for x in range(self.board)
                if self.is_open(x, y)]

    def shed_dist(self, x, y):
        if not self.shed_tiles:
            return 999
        return min(abs(x - sx) + abs(y - sy) for sx, sy in self.shed_tiles)

    def animals(self):
        """(x, y, tile) for every tile holding a live animal."""
        out = []
        for y in range(self.board):
            for x in range(self.board):
                t = self.tiles[y][x]
                if isinstance(t, dict) and "animal" in t:
                    out.append((x, y, t))
        return out

    def count_animals(self, kind=None):
        return sum(1 for _, _, t in self.animals()
                   if kind is None or t["animal"] == kind)

    def count_plants(self, crop=None):
        n = 0
        for row in self.tiles:
            for t in row:
                if isinstance(t, dict) and t.get("kind") == "PLANT":
                    if crop is None or t["crop"] == crop:
                        n += 1
        return n

    def count_structures(self, kind):
        """Coops/pastures, occupied or not — an animal tile keeps its structure kind."""
        n = 0
        for row in self.tiles:
            for t in row:
                if isinstance(t, dict) and t.get("kind") == kind:
                    n += 1
        return n

    def inv_any(self, item):
        return any(i.get(item, 0) > 0 for i in self.invs)

    def empty_structures(self, kind):
        """Built but unoccupied coops/pastures waiting for an animal."""
        n = 0
        for row in self.tiles:
            for t in row:
                if isinstance(t, dict) and t.get("kind") == kind and "animal" not in t:
                    n += 1
        return n

    def carried(self, item):
        return sum(i.get(item, 0) for i in self.invs)

    def opp_tile_counts(self):
        """What the opponent is growing — their farm is public.

        Used to predict when their floor-crashing crops mature so we can sell
        into the high price before they do.
        """
        counts = {}
        if not self.opp:
            return counts
        for row in self.opp["tiles"]:
            for t in row:
                if isinstance(t, dict):
                    if t.get("kind") == "PLANT":
                        counts[t["crop"]] = counts.get(t["crop"], 0) + 1
                    elif "animal" in t:
                        counts[t["animal"]] = counts.get(t["animal"], 0) + 1
        return counts


def step_toward(view, pos, target):
    """One legal move reducing Manhattan distance, or None if already there.

    Unlocked quadrants are always a connected prefix of NW/NE/SW/SE, so greedy
    axis-preferring descent never gets stuck in a concave trap — except on
    (h, h), which is fully enclosed while SE is locked. Returns "PASS" there.
    """
    x, y = pos
    tx, ty = target
    if (x, y) == (tx, ty):
        return None
    dx, dy = tx - x, ty - y
    cands = []
    if abs(dx) >= abs(dy):
        if dx: cands.append((1 if dx > 0 else -1, 0))
        if dy: cands.append((0, 1 if dy > 0 else -1))
    else:
        if dy: cands.append((0, 1 if dy > 0 else -1))
        if dx: cands.append((1 if dx > 0 else -1, 0))
    # Sideways fallbacks let us walk around a locked quadrant.
    cands += [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for ddx, ddy in cands:
        nx, ny = x + ddx, y + ddy
        if 0 <= nx < view.board and 0 <= ny < view.board and view.is_open(nx, ny):
            return DELTA_TO_MOVE[(ddx, ddy)]
    return "PASS"


# Actions each role costs per day — drives how close to the shed it should sit.
# Strawberry: plant + daily water over ~17 days + 4 harvests ≈ 1.3 actions/day.
ROLE_ACTION_LOAD = {"ANIMAL": 4.0, "WHEAT": 1.75, "CARROT": 2.0,
                    "STRAWBERRY": 1.3, "MELON": 1.15}


def plan_layout(view, p, plan):
    """Assign a role to every unlocked tile.

    Existing structures keep their role; free tiles are filled by descending
    daily action cost, so the busiest roles sit closest to the shed. That
    routing saving is worth more than it looks — movement is pure overhead.

    Wheat is allocated FIRST, ahead of coops: the flock can only grow as fast
    as its feed supply, so feed capacity is what we build out first.
    """
    roles = {}
    free = []
    for (x, y) in view.unlocked_tiles():
        t = view.tile(x, y)
        if isinstance(t, dict):
            kind = t.get("kind")
            if kind in ("COOP", "PASTURE"):
                roles[(x, y)] = "ANIMAL"
                continue
            if kind == "PLANT":
                crop = t["crop"]
                roles[(x, y)] = crop if crop in ("MELON", "WHEAT", "CARROT", "STRAWBERRY") else "CARROT"
                continue
            if kind == "WEED":
                free.append((x, y))
                continue
        if t is None:
            free.append((x, y))

    free.sort(key=lambda c: (view.shed_dist(*c), c[1], c[0]))

    have_animals = sum(1 for r in roles.values() if r == "ANIMAL")
    have_melon = sum(1 for r in roles.values() if r == "MELON")
    have_wheat = sum(1 for r in roles.values() if r == "WHEAT")
    have_straw = sum(1 for r in roles.values() if r == "STRAWBERRY")

    # How many tiles each role still wants. Wheat is sized first because feed
    # capacity is the hard gate on the whole animal engine.
    want = {
        "WHEAT": max(0, plan.want_wheat_tiles - have_wheat),
        "ANIMAL": max(0, plan.want_coops + plan.want_pastures - have_animals),
        "STRAWBERRY": max(0, plan.want_straw_tiles - have_straw),
        "MELON": max(0, plan.want_melon_tiles - have_melon),
    }
    budget = len(free)
    for role in ("WHEAT", "ANIMAL", "STRAWBERRY", "MELON"):
        want[role] = min(want[role], budget)
        budget -= want[role]

    # Placement order is by daily action load, so the busiest roles get the
    # tiles nearest the shed and we pay less movement tax all season.
    def load(role):
        return p["animal_labour_cost"] if role == "ANIMAL" else 1.0

    used = sum(load(r) for r in roles.values())
    i = 0
    for role in sorted(want, key=lambda r: -ROLE_ACTION_LOAD.get(r, 0)):
        for _ in range(want[role]):
            if i >= len(free) or used + load(role) > plan.workable:
                break
            roles[free[i]] = role
            used += load(role)
            i += 1

    # Anything past the labour ceiling stays deliberately fallow. An untended
    # tile costs nothing; a planted one we cannot water costs seed money and
    # then a DIG to clear the weed it becomes.
    fill = "CARROT" if p["carrot_fill"] else "WHEAT"
    while i < len(free) and used + 1.0 <= plan.workable:
        roles[free[i]] = fill
        used += 1.0
        i += 1
    return roles
