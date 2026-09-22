"""New Homii_N sale queue optimizer, 2026-09-14.

Use a public-board similarity gate and an explicit equal-stock mirror scenario.
Solve the <=10-slot ordering problem exactly; never alter quantities or buys.
"""
_HOMII_PARENT = agent
_HOMII_STATS = {}

def _homii_sale_assignment(obs, action):
    step = int(obs['step'])
    orders = action.get('market') or []
    if not 288 <= step < 712 or len(orders) < 2 or len(orders) > 10:
        return action
    if _r37_similarity(obs) < 0.9:
        return action
    if any(len(o) != 3 or o[0] != 'SELL' or o[1] not in PRODUCTS or type(o[2]) is not int or o[2] < 0 for o in orders):
        return action
    if len({o[1] for o in orders}) != len(orders):
        return action
    stock = projected_shed(action, FarmView(obs))
    params = _r132_price_params(obs)
    n = len(orders)
    exposed = []
    for order in orders:
        item = order[1]
        q = min(order[2], max(0, int(stock.get(item, 0))))
        inv = int(obs['market']['inventory'][item])
        # Each pair is a scenario with equal saleable stock. Prices at the
        # floor remain flat, so the prefix expression is valid there too.
        first = sum(_r37_market_price(item, inv+j, params) for j in range(q))
        second = sum(_r37_market_price(item, inv+q+j, params) for j in range(q))
        exposed.append(first-second)
    costs = [[gain if slot < i else -gain if slot > i else 0 for slot in range(n)] for i,gain in enumerate(exposed)]
    scores = [float('-inf')] * (1 << n)
    paths = [None] * (1 << n)
    scores[0] = 0
    paths[0] = ()
    for mask in range(1 << n):
        slot = mask.bit_count()
        if slot == n:
            continue
        for i in range(n):
            if mask & (1 << i):
                continue
            new = mask | (1 << i)
            score = scores[mask] + costs[i][slot]
            if score > scores[new]:
                scores[new] = score
                paths[new] = paths[mask] + (i,)
    if scores[-1] < 25:
        return action
    chosen = [list(orders[i]) for i in paths[-1]]
    if chosen == orders:
        return action
    _HOMII_STATS['queue_reorders'] += 1
    _HOMII_STATS['modeled_margin_gain'] += scores[-1]
    return dict(action, market=chosen)

def agent(observation, configuration=None):
    if int(observation.get('step',0)) == 0:
        _HOMII_STATS.update(queue_reorders=0,modeled_margin_gain=0,queue_errors=0)
    result = _HOMII_PARENT(observation,configuration)
    try:
        if _r132_standard(configuration):
            result = _homii_sale_assignment(observation,result)
    except Exception:
        _HOMII_STATS['queue_errors'] += 1
    _HOMII_STATS.update(getattr(_HOMII_PARENT,'telemetry',{}))
    return result

agent.telemetry = _HOMII_STATS
agent = globals().pop('agent')
