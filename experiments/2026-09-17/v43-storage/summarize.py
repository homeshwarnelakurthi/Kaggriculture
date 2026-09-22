from pathlib import Path
import json,statistics,hashlib
r=Path.cwd();w=r/'work/v43-storage'
def read(n):return [json.loads(x) for x in (w/n).read_text().splitlines()]
hold=read('holdout-valid.jsonl');ext=read('external-valid.jsonl');control=[x for x in read('external-games.jsonl') if x['candidate']=='v43']
assert len(hold)==16 and len(ext)==16 and len(control)==16
rows=hold+ext+control;assert all(x['valid'] for x in rows)
groups={}
for c,o in sorted({(x['candidate'],x['opponent']) for x in rows}):
 a=[x for x in rows if (x['candidate'],x['opponent'])==(c,o)];margin=[x['mine']-x['theirs'] for x in a]
 groups[c+'/'+o]={'games':len(a),'wins':sum(v>0 for v in margin),'ties':sum(v==0 for v in margin),'losses':sum(v<0 for v in margin),'mean_margin':statistics.mean(margin),'minimum_margin':min(margin),'maximum_turn_ms':max(x['max_turn_ms'] for x in a),'error_counts':{k:sum(x.get('telemetry',{}).get(k,0) for x in a) for k in {k for x in a for k in x.get('telemetry',{}) if 'error' in k or 'fallback' in k}},'storage_sale_units':sum(x.get('telemetry',{}).get('storage_sale_units',0) for x in a)}
pairs=[]
for x in ext:
 b=next(y for y in control if all(x[k]==y[k] for k in ['opponent','seed','seat']))
 pairs.append({'opponent':x['opponent'],'seed':x['seed'],'seat':x['seat'],'same_shops':x['shops']==b['shops'],'margin_delta':x['mine']-x['theirs']-b['mine']+b['theirs']})
report={'groups':groups,'pairs':pairs,'source_sha256':hashlib.sha256((w/'main.py').read_bytes()).hexdigest(),'invalid_initial_candidate_runs':32,'note':'Initial candidate had a line-ending packaging error before playing any turns. Corrected candidate runs are separate; failed games are never counted as wins.'}
(w/'summary.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'groups':groups,'pairs':pairs},indent=2))
