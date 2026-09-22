import json,statistics,collections
from pathlib import Path
out=Path(__file__).parent
rows=[json.loads(x) for x in (out/'coverage.jsonl').read_text().splitlines()]
groups={}
for c in ('v43','v42'):
 for o in ('barnyard','legacy_head'):
  r=[x for x in rows if x['candidate']==c and x['opponent']==o and x['valid']]
  groups[c+'/'+o]={'games':len(r),'wins':sum(x['win']==1 for x in r),'mean_margin':statistics.mean(x['mine']-x['theirs'] for x in r),'max_turn_ms':max(x['max_turn_ms'] for x in r)}
paired=[]
for r in rows:
 if r['candidate']!='v43':continue
 b=next(x for x in rows if x['candidate']=='v42' and all(x[k]==r[k] for k in ('opponent','seed','seat')))
 paired.append(dict(opponent=r['opponent'],seed=r['seed'],seat=r['seat'],same_shops=r['shops']==b['shops'],own_money_delta=r['mine']-b['mine'],margin_delta=(r['mine']-r['theirs'])-(b['mine']-b['theirs']),queue_reorders=r['telemetry'].get('queue_reorders',0)))
result={'groups':groups,'pairs':paired,'games':len(rows),'unique_shop_sequences':len({tuple(x['shops']) for x in rows})}
(out/'coverage-summary.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
