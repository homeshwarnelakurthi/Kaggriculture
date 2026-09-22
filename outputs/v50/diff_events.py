import json,collections
from pathlib import Path
W=Path(__file__).parent
for eid in [110991298,110986214,110984757]:
    a=json.loads((W/f'v48-{eid}.json').read_text());b=json.loads((W/f'v50-{eid}.json').read_text())
    print(eid,'margin',a['margin'],b['margin'])
    for item in ['STRAWBERRY','WOOL','MILK','WHEAT','EGG']:
        x={(e['step'],tuple(e.get('xy',[]))):e['units'] for e in a['events'] if e['seat']==0 and e['kind']=='harvest' and e['item']==item}
        y={(e['step'],tuple(e.get('xy',[]))):e['units'] for e in b['events'] if e['seat']==0 and e['kind']=='harvest' and e['item']==item}
        d=[(k,x.get(k,0),y.get(k,0)) for k in x.keys()|y.keys() if x.get(k,0)!=y.get(k,0)]
        if d:print(item,sorted(d))
    print('unit totals', {k:(a['totals'][0].get(k,0),v) for k,v in b['totals'][0].items() if k.startswith('SELL units') and a['totals'][0].get(k,0)!=v})
