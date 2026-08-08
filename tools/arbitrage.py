"""Is there money in trading the market rather than farming it?

Answer, from the engine source:

  1. NO SPREAD. `kaggriculture.py` quotes a buy at market_price(inv - 1) and a
     sell at market_price(inv), with the comment "so a buy/sell round-trip
     against an unchanged market nets zero". It is deliberate anti-arbitrage.
  2. ONLY TWO PRODUCTS ARE BUYABLE: WHEAT and FERTILIZER. Everything that
     actually earns -- milk, melon, wool, egg, strawberry -- is sell-only.

So the only trade available is a CARRY: buy a buyable product, wait for the town
to drain the market, sell higher. All the profit comes from the drain, none from
a margin. This prices that carry exactly, and prices the two structural facts
that fall out of the same reading:

  * WHEAT roughly DOUBLES over a season, and the drain is 4x after day 20.
    That is an argument about WHEN we buy feed and WHEN we sell wheat, worth
    more than the speculation itself.
  * FERTILIZER is excluded from TOWN_CENTER_PRODUCTS, so nothing ever drains
    it. Its price never recovers: the pot is finite and permanently spent.

Everything here is closed-form arithmetic against the engine's own price model.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kagri.constants import MARKET_I0
from kagri.market import buy_cost, price, sell_revenue

# Mirrored from kaggriculture.py.
TOWN_CENTER_SCHEDULE = [(20, 4), (10, 2), (0, 1)]
CENTER_INTERVAL = 12          # steps; 24 steps/day -> twice a day
SHOP_INTERVAL = 4             # steps; -> six times a day
SHOPS = {
    "BAKERY":         ["EGG", "WHEAT"],
    "PIZZA_SHOP":     ["MILK", "TOMATO", "WHEAT"],
    "BRUNCH_SPOT":    ["EGG", "WHEAT", "STRAWBERRY"],
    "YARN_STORE":     ["WOOL"],
    "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"],
    "PET_CAFE":       ["CARROT"],
    "SMOOTHIE_SHOP":  ["STRAWBERRY", "MILK"],
    "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
}
SHED_CAP = 100
DAYS = 30
TURNS = 24


def center_mult(day):
    return next(m for t, m in TOWN_CENTER_SCHEDULE if day >= t)


def drain_curve(item, shops=()):
    """Market inventory per day if NOBODY supplies -- pure town consumption."""
    inv = MARKET_I0
    out = [inv]
    for day in range(DAYS):
        for hour in range(TURNS):
            step = day * TURNS + hour
            if step % SHOP_INTERVAL == 0:
                for name in shops:
                    products = SHOPS[name]
                    if item in products:
                        inv -= 2 if len(products) == 1 else 1
            if step % CENTER_INTERVAL == 0 and item != "FERTILIZER":
                inv -= center_mult(day)
        out.append(inv)
    return out


def report_drain():
    print("=== What the town takes, per product, if we supply nothing ===")
    print("The town centre drains EVERY product but fertiliser, twice a day, at")
    print("1x before day 10, 2x from day 10 and 4x from day 20. Shops add more.\n")
    print(f"  {'product':<12}{'d10':>8}{'d20':>8}{'d30':>8}{'$ d0':>8}{'$ d20':>8}{'$ d30':>8}")
    all_shops = tuple(SHOPS)
    for item in ("WHEAT", "MELON", "MILK", "STRAWBERRY", "EGG", "WOOL", "FERTILIZER"):
        c = drain_curve(item, all_shops)
        print(f"  {item:<12}{MARKET_I0 - c[10]:>8,}{MARKET_I0 - c[20]:>8,}"
              f"{MARKET_I0 - c[30]:>8,}{price(item, c[0]):>8}"
              f"{price(item, c[20]):>8}{price(item, c[30]):>8}")


def report_roundtrip():
    print("\n=== Lock 1: the instant round trip, priced ===")
    print("Buy N units and sell them straight back into an unchanged market.\n")
    print(f"  {'product':<12}{'buy 20':>10}{'sell 20':>10}{'profit':>10}")
    for item in ("WHEAT", "FERTILIZER"):
        cost = buy_cost(item, MARKET_I0, 20)
        back = sell_revenue(item, MARKET_I0 - 20, 20)
        print(f"  {item:<12}{-cost:>10,}{back:>10,}{back - cost:>+10,}")
    print("\n  Exactly zero, as the engine comment promises. There is no spread to")
    print("  live in -- the 20-30%% middleman margin does not exist in this game.")


def report_carry():
    """The only real trade: hold WHEAT across the day-20 demand step-up."""
    print("\n=== Lock 2 bypass: the WHEAT carry trade, priced ===")
    print("Wheat is buyable AND town-drained, so its price genuinely rises.")
    print("Buy on day B, hold, sell on day S. Shed caps at 100 units TOTAL.\n")
    all_shops = tuple(SHOPS)
    curve = drain_curve("WHEAT", all_shops)
    print(f"  {'buy day':>8}{'sell day':>9}{'qty':>6}{'cost':>9}{'revenue':>9}"
          f"{'profit':>9}{'ROI':>7}")
    for buy_day, sell_day in ((8, 28), (16, 28), (20, 28), (24, 28), (26, 28)):
        for qty in (50, 100):
            inv_b = curve[buy_day]
            cost = buy_cost("WHEAT", inv_b, qty)
            # our purchase deepens the shortage; the town keeps draining on top
            inv_s = curve[sell_day] - qty
            rev = sell_revenue("WHEAT", inv_s, qty)
            print(f"  {buy_day:>8}{sell_day:>9}{qty:>6}{-cost:>9,}{rev:>9,}"
                  f"{rev - cost:>+9,}{100.0 * (rev - cost) / cost:>6.0f}%")


def report_fertilizer():
    print("\n=== FERTILIZER is a one-way door ===")
    print("It is excluded from TOWN_CENTER_PRODUCTS, so NOTHING ever drains it.")
    print("Every unit sold lowers the price permanently -- the pot is finite and")
    print("shared with the opponent, and it never recovers.\n")
    inv, total = MARKET_I0, 0
    marks = {}
    for k in range(1, 1200):
        p = price("FERTILIZER", inv)
        if p <= 1:
            break
        total += p
        inv += 1
        if k in (50, 100, 200, 400):
            marks[k] = (p, total)
    for k, (p, t) in marks.items():
        print(f"  after selling {k:>4} units: price ${p:>3}, cumulative ${t:>7,}")
    print(f"  ENTIRE lifetime pot, both players combined: ${total:,} over {k} units")
    print("\n  And the mirror of that: if the OPPONENT dumps fertiliser the price")
    print("  stays crashed. Fertiliser doubles a strawberry tile ($480 -> $960),")
    print("  so buying THEIR cheap fertiliser to use on our own crop is the one")
    print("  place where trading the market genuinely beats farming it.")
    print(f"  {'their dump':>11}{'our buy price':>15}{'cost to fert. 20 tiles':>24}")
    for dumped in (0, 100, 200, 300, 400):
        inv = MARKET_I0 + dumped
        print(f"  {dumped:>11}{price('FERTILIZER', inv - 1):>15}"
              f"{buy_cost('FERTILIZER', inv, 20):>24,}")


if __name__ == "__main__":
    report_drain()
    report_roundtrip()
    report_carry()
    report_fertilizer()
