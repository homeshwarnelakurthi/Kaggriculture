"""Live ladder status: our submissions, their episodes, and where we stand.

Kept in the repo rather than a scratchpad because this gets re-run every session
and the scratchpad does not survive between them.

  python tools/ladder.py            # submissions + leaderboard + episode stats
  python tools/ladder.py --no-eps   # skip the episode calls (they throttle)

Notes on the Kaggle episode API, learned the hard way:
  * GetEpisodeReplay was removed -- 404s even on episodes already downloaded.
  * ListEpisodes needs {"submissionId": N}; a bare teamId is rejected with
    "You must specify at least one ID filter".
  * It throttles hard (HTTP 429). Pace requests and do not retry in a tight loop.
"""

import argparse
import csv
import glob
import json
import os
import time
import zipfile

import requests
from kaggle.api.kaggle_api_extended import KaggleApi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LB_DIR = os.path.join(ROOT, "replays")
COMP = "kaggriculture"
OUR_KEYS = ("homii", "homesh", "nelakurthi")
EPISODE_URL = "https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes"


def leaderboard(api):
    os.makedirs(LB_DIR, exist_ok=True)
    api.competition_leaderboard_download(COMP, LB_DIR)
    for z in glob.glob(os.path.join(LB_DIR, "*.zip")):
        with zipfile.ZipFile(z) as zf:
            zf.extractall(LB_DIR)
        os.remove(z)
    path = max(glob.glob(os.path.join(LB_DIR, "*publicleaderboard*.csv")),
               key=os.path.getmtime)
    # utf-8-sig: the export carries a BOM, so plain utf-8 hides the "Rank" key.
    return path, list(csv.DictReader(open(path, encoding="utf-8-sig")))


def episode_stats(sess, sub_id):
    r = sess.post(EPISODE_URL, json={"submissionId": int(sub_id)}, timeout=60)
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}"
    rows = []
    for e in r.json().get("episodes", []):
        if e.get("state") != "COMPLETED":
            continue
        ag = e.get("agents", [])
        me = [a for a in ag if int(a.get("submissionId", 0)) == int(sub_id)]
        op = [a for a in ag if int(a.get("submissionId", 0)) != int(sub_id)]
        if not me or not op:
            continue
        a, b = me[0].get("reward"), op[0].get("reward")
        if a is None or b is None:
            continue
        rows.append((float(a), float(b), op[0].get("updatedScore") or 0.0,
                     me[0].get("updatedScore") or 0.0))
    return rows, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-eps", action="store_true")
    ap.add_argument("--eps-for", type=int, default=4,
                    help="how many of the newest submissions to pull episodes for")
    ap.add_argument("--pace", type=float, default=4.0)
    args = ap.parse_args()

    api = KaggleApi()
    api.authenticate()

    subs = list(api.competition_submissions(COMP))
    print("=== SUBMISSIONS (newest first) ===")
    print(f"{'date':<20}{'ref':<11}{'status':<10}{'score':>9}  description")
    for s in subs[:10]:
        print(f"{str(s.date)[:19]:<20}{str(s.ref):<11}"
              f"{str(s.status).split('.')[-1]:<10}{str(s.public_score):>9}  "
              f"{(str(s.description) or '(none)')[:60]}")

    path, rows = leaderboard(api)
    scores = sorted((float(r["Score"]) for r in rows), reverse=True)
    n = len(rows)
    print(f"\n=== LEADERBOARD === ({n:,} teams, {os.path.basename(path)[-24:-4]})")
    for r in rows[:10]:
        print(f"  {r['Rank']:>4}  {r['TeamName'][:34]:<36}{r['Score']:>9}")
    print("  ---")
    for label, idx in (("rank 10", 9), ("rank 50", 49), ("rank 100", 99)):
        if n > idx:
            print(f"  {label:<9}{scores[idx]:>9.1f}")
    for p in (1, 5, 10, 25, 50):
        print(f"  top {p:>2}%   {scores[min(n - 1, int(n * p / 100))]:>9.1f}")

    ours = [r for r in rows
            if any(k in r["TeamName"].lower() for k in OUR_KEYS)
            or any(k in (r.get("TeamMemberUserNames") or "").lower() for k in OUR_KEYS)]
    for r in ours:
        rank = int(r["Rank"])
        gap = scores[9] - float(r["Score"]) if n > 9 else 0.0
        print(f"\n  OURS: rank {rank:,} of {n:,} (top {100.0 * rank / n:.1f}%)  "
              f"score {r['Score']}  last sub {r['LastSubmissionDate'][:19]}")
        print(f"        gap to rank 10: {gap:+,.1f}")

    if args.no_eps:
        return
    cfg = json.load(open(os.path.join(os.path.expanduser("~"), ".kaggle", "kaggle.json")))
    sess = requests.Session()
    sess.auth = (cfg["username"], cfg["key"])
    print(f"\n=== EPISODES (newest {args.eps_for} submissions) ===")
    print(f"{'ref':<11}{'eps':>6}{'win%':>7}{'our $':>11}{'opp $':>11}"
          f"{'opp rating':>12}{'our rating':>12}")
    for s in subs[:args.eps_for]:
        rows_e, err = episode_stats(sess, s.ref)
        if err:
            print(f"{str(s.ref):<11}  {err}")
            continue
        if not rows_e:
            print(f"{str(s.ref):<11}{0:>6}")
            continue
        k = len(rows_e)
        wins = sum(1 for a, b, _, _ in rows_e if a > b) + 0.5 * sum(
            1 for a, b, _, _ in rows_e if a == b)
        print(f"{str(s.ref):<11}{k:>6}{100.0 * wins / k:>6.0f}%"
              f"{sum(a for a, _, _, _ in rows_e) / k:>11,.0f}"
              f"{sum(b for _, b, _, _ in rows_e) / k:>11,.0f}"
              f"{sum(c for _, _, c, _ in rows_e) / k:>12,.0f}"
              f"{sum(d for _, _, _, d in rows_e) / k:>12,.0f}")
        time.sleep(args.pace)


if __name__ == "__main__":
    main()
