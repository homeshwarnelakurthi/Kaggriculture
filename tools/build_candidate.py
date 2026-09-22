"""Rebuild a submitted candidate from the recovered, hashed active submission.

Usage: python tools/build_candidate.py --horizon 6 [--queue] --name v43
"""
import argparse, hashlib, io, json, tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--horizon',type=int,default=6);ap.add_argument('--queue',action='store_true');ap.add_argument('--name',default='v43');a=ap.parse_args()
    if not a.name.replace('_','').isalnum() or not 1<=a.horizon<=24:raise ValueError('Invalid build parameters')
    provenance=json.loads((ROOT/'work/recovered/PROVENANCE.json').read_text())
    expected=next(s for s in provenance['sources'] if s['submission_id']=='56237315')
    src=(ROOT/'work/recovered/56237315/main.py').read_bytes()
    if hashlib.sha256(src).hexdigest()!=expected['sha256']:raise ValueError('Recovered baseline hash changed')
    source=src.decode('utf-8');target='if 288 <= step < 696:_R37_HORIZONS[player] = 4'
    if source.count(target)!=1:raise ValueError('Expected reservation setting not found exactly once')
    source=source.replace(target,f'if 288 <= step < 696:_R37_HORIZONS[player] = {a.horizon}')
    if a.queue:source+='\n'+(ROOT/'tools/sale_assignment_extension.py').read_text(encoding='utf-8-sig')
    source+=f'\n# Homii_N 2026-09-14: {a.horizon}-turn stock-backed sale reservation.\n'
    out=ROOT/'agents'/a.name;out.mkdir(parents=True,exist_ok=True)
    (out/'main.py').write_text(source,encoding='utf-8')
    notice='''Kaggriculture agent - Homii_N, 2026-09-14

Derived from this account's existing submission 56237315, downloaded from:
https://www.kaggle.com/code/homeshwarrao/farming-score-v4-a-better-shop?scriptVersionId=349859928

This is a derivative of a route-based agent, not a newly trained model or
wholly original source. All recovered source comments, attributions, embedded
route data and existing license headers have been preserved. The recovered
source credits Kaggle/kaggle-environments contributors, Ahmed Berat Ozer,
Dmitrii Gluzdov, fieldbook, tetsutani, lucifer19, prvsiyan and other public
capabilities named in the code. The archive originally contained only main.py;
it did not include a complete standalone upstream NOTICE or license file.
Full upstream provenance has not been independently verified.

Homii_N changes extend the existing stock-backed sale reservation horizon.
Any optional queue optimizer is new code that changes only all-sale ordering
under an explicit mirror scenario; no opponent private inventory is accessed.
Originality and licensing obligations mentioned in BRIEFING.md remain separate
from the local performance validation and have not been resolved with hosts.
'''
    (out/'NOTICE.txt').write_text(notice,encoding='utf-8')
    (out/'LICENSE-APACHE-2.0.txt').write_bytes((ROOT/'work/LICENSE-APACHE-2.0.txt').read_bytes())
    archive=out/f'{a.name}.tar.gz'
    with tarfile.open(archive,'w:gz') as t:
        for name in ('main.py','NOTICE.txt','LICENSE-APACHE-2.0.txt'):
            data=(out/name).read_bytes();info=tarfile.TarInfo(name);info.size=len(data);info.mtime=0;info.mode=0o644;t.addfile(info,io.BytesIO(data))
    manifest={'name':a.name,'parent_submission':'56237315','parent_sha256':expected['sha256'],'horizon':a.horizon,'queue_optimizer':a.queue,'main_sha256':hashlib.sha256((out/'main.py').read_bytes()).hexdigest(),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'runtime':'kaggle-environments==1.32.7'}
    (out/'build.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(manifest,indent=2));print(archive)
if __name__=='__main__':main()
