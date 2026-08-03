"""Market price model — an exact mirror of the engine's pricing and order commit.

Lets the agent answer "what will N more units actually earn me?" instead of
trusting the quoted spot price, which is what makes premium goods look far more
valuable than they are.
"""

import math

from .constants import MARKET_I0, MARKET_PARAMS, PRICE_FLOOR


def _shape(func, x):
    x = max(0.0, x)
    if func == "linear":
        return x
    if func == "sq":
        return x * x
    if func == "sqrt":
        return math.sqrt(x)
    if func == "log":
        return math.log(1.0 + x)
    if func == "log10":
        return math.log10(1.0 + x)
    return x


def price(item, inventory, params=None):
    """Spot price at a given market inventory. Mirrors engine market_price()."""
    p = (params or MARKET_PARAMS)[item]
    base, T = p["base"], p["T"]
    I0 = p.get("I0", MARKET_I0)
    if inventory < I0:
        f = p["below_func"]
        amp = p["below_target"] * base / _shape(f, T)
        v = base + amp * _shape(f, I0 - inventory)
    else:
        f = p["above_func"]
        amp = p["above_target"] * base / _shape(f, T)
        v = base - amp * _shape(f, inventory - I0)
    return max(PRICE_FLOOR, int(round(v)))


def sell_revenue(item, inventory, n, params=None):
    """Exact proceeds from selling n units one at a time (mirrors _commit_unit).

    Sales at the $1 floor pay out but do NOT raise market inventory.
    """
    inv, total = inventory, 0
    for _ in range(n):
        p = price(item, inv, params)
        total += p
        if p > PRICE_FLOOR:
            inv += 1
    return total


def buy_cost(item, inventory, n, params=None):
    """Exact cost of buying n units. Quoted at post-buy inventory, per engine."""
    inv, total = inventory, 0
    for _ in range(n):
        total += price(item, inv - 1, params)
        inv -= 1
    return total


def marginal_value(item, inventory, n=1, params=None):
    """Average $/unit for the next n units sold — the number worth optimising."""
    if n <= 0:
        return 0.0
    return sell_revenue(item, inventory, n, params) / n


def revenue_to_floor(item, inventory=MARKET_I0, params=None, cap=4000):
    """Total remaining money in this product before it hits the $1 floor.

    The headline result: EGG and WHEAT never floor (log curve), so they are the
    only unbounded sinks. Everything else has a fixed pot shared with the
    opponent — which makes selling those a race, not a schedule.
    """
    inv, total = inventory, 0
    for i in range(cap):
        p = price(item, inv, params)
        if p <= PRICE_FLOOR:
            return total, i
        total += p
        inv += 1
    return total, cap
