# Homii_N integrated flow controller, 2026-09-15. Standard-library only.
# Forecasts are scenarios, never access to the opponent's private inventory.
_FLOW_PARENT = agent
_FLOW_NATIVE_RESERVE = _r36_reserve
_FLOW_STATE = {}
_FLOW_STATS = {}
_FLOW_ADAPTIVE = True
_FLOW_LEAD = 10
_FLOW_SHOPS = {'BAKERY':['EGG','WHEAT'],'PIZZA_SHOP':['MILK','TOMATO','WHEAT'],
 'BRUNCH_SPOT':['EGG','WHEAT','STRAWBERRY'],'YARN_STORE':['WOOL'],
 'ICE_CREAM_SHOP':['STRAWBERRY','MILK','WHEAT'],'PET_CAFE':['CARROT'],
 'SMOOTHIE_SHOP':['STRAWBERRY','MILK'],'FARMERS_MARKET':['WHEAT','CARROT','TOMATO','STRAWBERRY']}

def _flow_forecast(obs, config):
    step=int(obs['step']); p=int(obs['player']); horizon=min(12,718-step)
    own=obs['farms'][p]; rival=obs['farms'][1-p]
    ready={i:0 for i in PRODUCTS}; own_ready={i:0 for i in PRODUCTS}
    animals=0
    for side,dest in [(own,own_ready),(rival,ready)]:
        for row in side['tiles']:
            for t in row:
                if not isinstance(t,dict):continue
                animal=t.get('animal')
                if side is own and animal:animals+=1
                item=t.get('crop') or {'GOOSE':'EGG','COW':'MILK','SHEEP':'WOOL'}.get(animal)
                if item:dest[item]+=max(0,int(t.get('yield_units',0)))
    cfg=config or {}; si=max(1,int(cfg.get('townShopSellInterval',4))); ci=max(1,int(cfg.get('townCenterSellInterval',24)))
    demand={i:0 for i in PRODUCTS}
    for t in range(step,step+horizon):
        if t%si==0:
            for shop in obs['town']['unlocked_shops']:
                goods=_FLOW_SHOPS.get(shop,[])
                for i in goods:demand[i]+=2 if len(goods)==1 else 1
        if t%ci==0:
            for i in PRODUCTS:
                if i!='FERTILIZER':demand[i]+=1
    model={'step':step,'standard':_r132_standard(config),'similarity':_r37_similarity(obs),'ready':ready,'own_ready':own_ready,
           'demand':demand,'animals':animals,'horizon':horizon,'decisions':{}}
    _FLOW_STATE[p]=model
    return model

def _flow_quote(obs,item,offset,quantity=0):
    model=_FLOW_STATE[int(obs['player'])]
    horizon=max(1,model['horizon']); fraction=min(1,offset/horizon)
    drain=model['demand'][item]*fraction
    # Only part of visible harvestable output may reach the market in this window.
    supply=model['ready'][item]*fraction*0.5
    stock=max(0,int(obs['private']['shed'].get(item,0)))
    if model['similarity']>=0.9:supply=max(supply,min(stock,quantity))
    inv=int(obs['market']['inventory'][item])
    params=_r132_price_params(obs)
    return {'now':_r37_market_price(item,inv,params),
            'expected':_r37_market_price(item,int(inv+supply-drain),params),
            'optimistic':_r37_market_price(item,int(inv-drain),params),
            'rival_supply':supply,'demand':drain}

def _flow_reservations(obs,action):
    step=int(obs['step'])
    # The final planner forecasts its own parent, so keep its full window native.
    if not 288<=step<696:return action
    native=_IMPL.chassis.players[int(obs['player'])]
    tape=_IMPL.chassis.routes[native['route']]
    end=min(695,step+10,(step//72+1)*72-1)
    if end<=step:return action
    commands=[action.get('farmer') or ['PASS'],*(action.get('hands') or [])]
    view=FarmView(obs)
    # This projection intentionally abstains on ambiguous animal depot returns.
    if any(len(c)>1 and c[0]=='PLACE' and c[1] in ANIMAL_STRUCTURE
           and view.inv(i).get(c[1],0)>0 for i,c in enumerate(commands[:len(view.positions)])):
        return action
    stock=projected_shed(action,view)
    market=action.get('market',[])
    blocked={o[1] for o in market if len(o)>1 and o[0] in ('SELL','BUY_PRODUCT')}
    blocked.update(c[1] for c in commands if len(c)>1 and c[0]=='PICKUP')
    blocked.update(c[1] for queue in native['pending'].values() for pos,c in queue
                   if len(c)>1 and c[0]=='PICKUP')
    debts=native['sell_state'].setdefault('r36_debts',{})
    for item in PRODUCTS:
        if item in ('WHEAT','FERTILIZER') or item in blocked or view.prices.get(item,0)<2:continue
        available=max(0,int(stock.get(item,0)))
        if not available or len(market)>=10:continue
        reservations=[]
        for due_step in range(step+1,end+1):
            future=tape[due_step]
            work=[future.get('farmer') or ['PASS'],*(future.get('hands') or [])]
            if any(len(c)>1 and c[:2]==['PICKUP',item] for c in work):break
            if any(len(o)>1 and o[:2]==['BUY_PRODUCT',item] for o in future.get('market',[])):break
            planned=sum(max(0,int(o[2])) for o in future.get('market',[]) if len(o)>=3 and o[:2]==['SELL',item])
            amount=min(available,max(0,planned-debts.get(due_step,{}).get(item,0)))
            if amount:
                model=_FLOW_STATE[int(obs['player'])]
                quote=_flow_quote(obs,item,due_step-step,amount)
                pressure=sum(stock.values())+sum(sum(inv.values()) for inv in obs['private']['inventories'])>90
                similar=model['similarity']>=.9 and _R44_PROBES.get(int(obs['player']),{}).get('matched',False)
                if due_step-step>8 and not (similar and (quote['expected']<quote['now'] or pressure)):continue
                if not similar and not pressure and quote['expected']>quote['now']+2 and due_step-step>4:
                    model['decisions'][item]={'action':'hold_for_demand','quantity':amount,**quote}
                    _FLOW_STATS['held_reservations']+=1
                    continue
                reservations.append((due_step,amount));available-=amount
            if not available:break
        qty=sum(q for _,q in reservations)
        if qty:
            market.append(['SELL',item,qty])
            for due,q in reservations:
                debt=debts.setdefault(due,{})
                debt[item]=debt.get(item,0)+q
            _R36_SALE_REPORT['sale_reserved_units']+=qty
            _R36_SALE_REPORT['sale_reservations']+=1
    return action

def _r36_reserve(obs,action):
    if not _FLOW_ADAPTIVE or not _FLOW_STATE.get(int(obs['player']),{}).get('standard',False):return _FLOW_NATIVE_RESERVE(obs,action)
    result=_flow_reservations(obs,action)
    _FLOW_STATS['forecast_extended_calls']+=1
    return result

def _flow_reserve(obs,item):
    # Preserve all planned pickups until the next replenishment, plus one day of feed.
    step=int(obs['step']); native=_IMPL.chassis.players[int(obs['player'])];need=0
    for t in range(step+1,min(719,step+49)):
        future=_IMPL.chassis.routes[2 if t>=648 else native['route']][t]
        for c in _r128_commands(future):
            if len(c)>1 and c[:2]==['PICKUP',item]:need+=max(0,int(c[2]) if len(c)>2 else 1)
        if any(len(o)>1 and o[:2]==['BUY_PRODUCT',item] for o in future.get('market',[])):break
    if item=='WHEAT':need=max(need,_FLOW_STATE[int(obs['player'])]['animals'])
    return min(100,need)

def _flow_allocate(obs,action):
    step=int(obs['step']); model=_FLOW_STATE[int(obs['player'])]
    if not 288<=step<712:return action
    orders=action.get('market') or []
    # Affordability and purchase-side capacity must be modeled before changing those turns.
    if any(o and o[0]!='SELL' for o in orders):return action
    farm,private=_r127_fields(obs,action)
    stock,_,_=_r97_market_stock(private['shed'],orders)
    incoming={i:sum(max(0,int(inv.get(i,0))) for inv in private['inventories']) for i in PRODUCTS}
    for item in PRODUCTS:
        model['decisions'].setdefault(item,{'action':'consume_or_reserve' if item in ('WHEAT','FERTILIZER') else 'hold',
            'shed':stock.get(item,0),'incoming':incoming[item],'visible_production':model['own_ready'][item]})
    if step%24!=23:return action
    baseline,oldloss=_r97_delivery(stock,private,True)
    needed=sum(oldloss.values())
    if needed<=0:return action
    result=copy.deepcopy(action)
    reserve={i:_flow_reserve(obs,i) for i in ('WHEAT','FERTILIZER')}
    # Rank surplus by the opportunity cost of selling now rather than after demand recovery.
    candidates=[]
    for item in PRODUCTS:
        if stock.get(item,0)<=0:continue
        quote=_flow_quote(obs,item,8,stock[item])
        candidates.append((quote['expected']-quote['now'], -quote['now'],item))
    for _,_,item in sorted(candidates):
        existing=next((o for o in result['market'] if o[:2]==['SELL',item]),None)
        if existing is None and len(result['market'])>=10:continue
        cap=min(needed,max(0,int(stock.get(item,0))))
        # Test quantities with exact ordered overnight deposits; reserves must survive.
        accepted=0
        for q in range(cap,0,-1):
            trial=dict(stock);trial[item]-=q
            final,loss=_r97_delivery(trial,private,True)
            if any(final.get(i,0)<min(reserve[i],baseline.get(i,0)) for i in reserve):continue
            if sum(loss.values())>=needed:continue
            accepted=q;break
        if not accepted:continue
        if existing is None:result['market'].append(['SELL',item,accepted])
        else:existing[2]+=accepted
        stock[item]-=accepted
        _,loss=_r97_delivery(stock,private,True);needed=sum(loss.values())
        model['decisions'][item]={'action':'sell_for_incoming','quantity':accepted,'feed_reserve':reserve.get(item,0),**_flow_quote(obs,item,8,accepted)}
        _FLOW_STATS['storage_sale_units']+=accepted
        if needed<=0:break
    if result!=action:_FLOW_STATS['storage_turns']+=1
    _FLOW_STATS['unresolved_overflow']+=needed
    return result

def _flow_production(obs,action):
    step=int(obs['step']);day=step//24
    if not 288<=step<712:return action
    commands=_r128_commands(action);positions=[obs['farms'][obs['player']]['farmer'],*obs['farms'][obs['player']]['hands']]
    result=copy.deepcopy(action); changed=False
    first={'WHEAT':2,'CARROT':2,'TOMATO':8,'STRAWBERRY':10,'MELON':10}
    for actor,c in enumerate(commands):
        if len(c)>1 and c[0]=='PLANT' and day+first.get(c[1],100)>29:
            commands[actor]=['PASS'];changed=True;_FLOW_STATS['unmaturing_plants_avoided']+=1
    if changed:result['farmer'],result['hands']=commands[0],commands[1:]
    if step%24!=23 or any(o and o[0]!='SELL' for o in result.get('market',[])):return result
    _,private=_r127_fields(obs,result)
    post,_,_=_r97_market_stock(private['shed'],result.get('market',[]))
    _,loss=_r97_delivery(post,private,True)
    if not sum(loss.values()):return result
    for actor,c in enumerate(commands):
        if c!=['PASS'] or actor>=len(positions) or not _shed_adjacent(positions[actor],10):continue
        inv=obs['private']['inventories'][actor]
        for item in sorted((i for i,q in inv.items() if q>0 and i in PRODUCTS and i not in ('WHEAT','FERTILIZER')),key=lambda i:-obs['market']['prices'].get(i,0)):
            room=max(0,100-sum(private['shed'].values()))
            q=min(int(inv[item]),room)
            if q<=0:continue
            trial=_r132_set_command(result,actor,['PLACE',item,q])
            _,newprivate=_r127_fields(obs,trial)
            before=sum(private['shed'].values())+sum(sum(v.values()) for v in private['inventories'])
            after=sum(newprivate['shed'].values())+sum(sum(v.values()) for v in newprivate['inventories'])
            if after<before:continue
            oldstock,_,_=_r97_market_stock(private['shed'],result.get('market',[]))
            newstock,_,_=_r97_market_stock(newprivate['shed'],trial.get('market',[]))
            oldfinal,_=_r97_delivery(oldstock,private,True)
            newfinal,_=_r97_delivery(newstock,newprivate,True)
            if any(newfinal.get(i,0)<min(_flow_reserve(obs,i),oldfinal.get(i,0)) for i in ('WHEAT','FERTILIZER')):continue
            result=trial;private=newprivate;_FLOW_STATS['early_deposit_units']+=q;break
    return result

def agent(observation,configuration=None):
    step=int(observation.get('step',0))
    if step==0:
        _FLOW_STATS.clear();_FLOW_STATS.update(forecast_extended_calls=0,storage_sale_units=0,storage_turns=0,unresolved_overflow=0,flow_errors=0,held_reservations=0,unmaturing_plants_avoided=0,early_deposit_units=0)
    try:_flow_forecast(observation,configuration)
    except Exception:
        _FLOW_STATS['flow_errors']+=1
        _FLOW_STATE.pop(int(observation['player']),None)
    result=_FLOW_PARENT(observation,configuration)
    try:
        if _r132_standard(configuration) and int(observation['player']) in _FLOW_STATE:
            result=_flow_production(observation,result)
            result=_flow_allocate(observation,result)
    except Exception:_FLOW_STATS['flow_errors']+=1
    _FLOW_STATS.update(getattr(_FLOW_PARENT,'telemetry',{}))
    return result
agent.telemetry=_FLOW_STATS
agent=globals().pop('agent')
