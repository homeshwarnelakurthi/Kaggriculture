import json,statistics,collections
from pathlib import Path
root=Path(__file__).parent
summary={}
for f in root.glob('*-games.jsonl'):
 rows=[json.loads(x) for x in f.read_text().splitlines() if x.strip()]
 groups={}
 for candidate,opponent in sorted({(r['candidate'],r['opponent']) for r in rows}):
  group=[r for r in rows if (r['candidate'],r['opponent'])==(candidate,opponent)]
  good=[r for r in group if r['valid']]
  margins=[r['mine']-r['theirs'] for r in good]
  errors={k:sum(r.get('telemetry',{}).get(k,0) for r in good) for k in {k for r in good for k in r.get('telemetry',{}) if 'error' in k}}
  groups[f'{candidate}/{opponent}']={'episodes':len(group),'seeds':sorted({r['seed'] for r in group}),'valid':len(good),'wins':sum(m>0 for m in margins),'ties':sum(m==0 for m in margins),'losses':sum(m<0 for m in margins),'mean_margin':statistics.mean(margins) if margins else None,'minimum_margin':min(margins,default=None),'maximum_turn_ms':max((r['max_turn_ms'] for r in good),default=None),'nonzero_errors':{k:v for k,v in errors.items() if v},'loss_details':[{'seed':r['seed'],'seat':r['seat'],'margin':r['mine']-r['theirs']} for r in good if r['mine']<r['theirs']]}
 summary[f.name]=groups
(root/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
