"""Audit benchmark JSONL without treating seat swaps as independent seed draws.

Usage: python tools/report_benchmarks.py result1.jsonl ... --output report.json
No Kaggle calls. A completed game is counted only once per candidate/opponent/seed/seat.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
from statistics import mean


def summarize(paths):
    records = {}
    sources = []
    for source in paths:
        path = Path(source).resolve()
        raw = path.read_bytes()
        sources.append({'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest()})
        for number, line in enumerate(raw.decode('utf-8-sig').splitlines(), 1):
            if not line.strip():
                continue
            row = json.loads(line)
            key = tuple(row[k] for k in ('candidate', 'opponent', 'seed', 'seat'))
            if key in records:
                raise ValueError(f'Duplicate episode {key} at {path}:{number}; provide disjoint runs.')
            if row['seat'] not in (0, 1):
                raise ValueError(f'Invalid seat at {path}:{number}')
            records[key] = row
    groups = defaultdict(list)
    for key, row in records.items():
        groups[key[:2]].append(row)
    matchups = []
    for (candidate, opponent), rows in sorted(groups.items()):
        valid = [r for r in rows if r.get('valid') and r.get('status') == ['DONE', 'DONE']
                 and r.get('steps') == 720 and isinstance(r.get('mine'), (int, float))
                 and isinstance(r.get('theirs'), (int, float))]
        seeds = sorted({r['seed'] for r in rows})
        by_seed = defaultdict(dict)
        for row in valid:
            by_seed[row['seed']][row['seat']] = row
        paired = []
        missing = []
        for seed in seeds:
            if set(by_seed[seed]) != {0, 1}:
                missing.append(seed)
                continue
            pair = [by_seed[seed][seat] for seat in (0, 1)]
            scores = [float(r['mine'] > r['theirs']) + 0.5 * float(r['mine'] == r['theirs']) for r in pair]
            paired.append({'seed': seed, 'mean_game_points': mean(scores),
                           'mean_coin_margin': mean(r['mine'] - r['theirs'] for r in pair),
                           'wins_both_seats': all(r['mine'] > r['theirs'] for r in pair),
                           'loses_either_seat': any(r['mine'] < r['theirs'] for r in pair)})
        problems = defaultdict(int)
        for row in valid:
            for key, value in row.get('telemetry', {}).items():
                if any(word in key.lower() for word in ('error', 'fallback', 'shortfall')) and isinstance(value, (int, float)) and value:
                    problems[key] += value
        matchups.append({
            'candidate': candidate, 'opponent': opponent, 'episodes': len(rows),
            'valid_episodes': len(valid), 'invalid_episodes': len(rows) - len(valid),
            'wins': sum(r['mine'] > r['theirs'] for r in valid),
            'ties': sum(r['mine'] == r['theirs'] for r in valid),
            'losses': sum(r['mine'] < r['theirs'] for r in valid),
            'unique_seeds': len(seeds), 'complete_seat_pairs': len(paired), 'unpaired_or_invalid_seeds': missing,
            'mean_paired_game_points': mean(p['mean_game_points'] for p in paired) if paired else None,
            'mean_coin_margin': mean(r['mine'] - r['theirs'] for r in valid) if valid else None,
            'min_coin_margin': min((r['mine'] - r['theirs'] for r in valid), default=None),
            'max_turn_ms': max((r['max_turn_ms'] for r in valid), default=None),
            'telemetry_nonzero_problem_counts': dict(problems),
            'seed_pairs': paired,
        })
    return {'sources': sources, 'matchups': matchups,
            'interpretation': 'Coins diagnose changes; game wins/ties/losses measure success. Both seats share a seed. Related opponents do not establish leaderboard strength. Missing planned seeds cannot be detected without a planned-run manifest.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('results', nargs='+')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    report = summarize(args.results)
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    for row in report['matchups']:
        print(f"{row['candidate']} vs {row['opponent']}: {row['wins']}W/{row['ties']}T/{row['losses']}L; "
              f"{row['invalid_episodes']} invalid; {row['complete_seat_pairs']} complete seed pairs; "
              f"mean margin {row['mean_coin_margin']}; max {row['max_turn_ms']} ms")


if __name__ == '__main__':
    main()
