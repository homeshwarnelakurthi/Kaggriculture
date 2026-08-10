"""What do top-of-ladder agents actually SCORE, and how does that compare to us?

We have never observed the top of this ladder. Every "real opponent" archetype
in tools/gauntlet.py was reconstructed from mid-ladder players who beat us, and
every one of our 203 cached replays is from our own ~650-rated matches. So we
have been tuning against a field we never measured.

Kaggle's GetEpisodeReplay route is gone (404s even on episodes we already hold),
so full turn-by-turn replays are no longer downloadable. But ListEpisodes still
returns REWARDS and RATINGS for every episode, which settles the question that
actually decides our next move:

    Do top agents earn far more money than us, or similar money more reliably?

If they earn far more, our ECONOMICS are weak and the fix is production --
tile utilisation, the labour model. If they earn about what we do but win more
often, the fix is DECISION QUALITY and the answer is search, not tuning.

  python tools/top_stats.py --teams 12

Caches the team -> submission map so the ladder climb happens only once.
"""

import argparse
import csv
import glob
import json
import os
import statistics
import time

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "replays", "top", "teams.json")
# Per-team results accumulate here. The endpoint rate-limits hard after a ladder
# climb, so a single run reliably collects only a few teams -- without this the
# partial sample is thrown away every time and the measurement never completes.
RESULTS = os.path.join(ROOT, "replays", "top", "top_money.json")
BASE = "https://www.kaggle.com/api/i/competitions.EpisodeService"
SEED_SUBMISSION = 55134735
OUR_TEAM_NAMES = ("homii_n", "homeshwar", "nelakurthi")


def session():
    d = json.load(open(os.path.join(os.path.expanduser("~"), ".kaggle", "kaggle.json")))
    s = requests.Session()
    s.auth = (d["username"], d["key"])
    return s


def post(s, endpoint, payload, tries=3):
    for i in range(tries):
        r = s.post(f"{BASE}/{endpoint}", json=payload,
                   headers={"Content-Type": "application/json"}, timeout=90)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 500, 502, 503):
            time.sleep(3 * (i + 1))
            continue
        r.raise_for_status()
    raise RuntimeError(f"{endpoint} failed")


def leaderboard():
    files = glob.glob(os.path.join(ROOT, "replays", "*publicleaderboard*.csv"))
    if not files:
        raise SystemExit("no leaderboard CSV in replays/")
    path = max(files, key=os.path.getmtime)
    return list(csv.DictReader(open(path, encoding="utf-8")))


def harvest(s, subs):
    known = {}
    for sub in subs:
        try:
            data = post(s, "ListEpisodes", {"submissionId": sub})
        except Exception:
            continue
        for t in data.get("teams", []):
            plsid = t.get("publicLeaderboardSubmissionId")
            if plsid:
                known[int(t["id"])] = int(plsid)
    return known


def climb(s, rating, wanted, max_hops=8, width=6):
    """Walk UP the ladder. Matchmaking means our own opponents are all near our
    rating, so the top never appears in a seed query -- each hop queries the
    strongest team we know but have not queried, discovering stronger ones."""
    if os.path.exists(CACHE):
        known = {int(k): int(v) for k, v in json.load(open(CACHE)).items()}
        print(f"cached team map: {len(known)} teams")
        if wanted <= set(known):
            return known
    else:
        known = {}
    known.update(harvest(s, [SEED_SUBMISSION]))
    queried = set()
    for hop in range(max_hops):
        if wanted <= set(known):
            break
        pool = sorted(((rating.get(t, 0.0), t) for t in known if t not in queried),
                      reverse=True)
        batch = [t for _, t in pool[:width]]
        if not batch:
            break
        queried.update(batch)
        known.update(harvest(s, [known[t] for t in batch]))
        print(f"  hop {hop + 1}: {len(known)} teams, "
              f"{len(wanted & set(known))}/{len(wanted)} targets")
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump({str(k): v for k, v in known.items()}, open(CACHE, "w"))
    return known


def episodes_for(s, sub, label=""):
    """Never swallow the error: a silent [] reads as "this team has no games",
    which is exactly the mistake that made the first run look like the whole
    top of the ladder was empty."""
    for attempt in range(4):
        try:
            return post(s, "ListEpisodes", {"submissionId": sub}).get("episodes", [])
        except Exception as exc:
            wait = 5 * (attempt + 1)
            print(f"    ! {label} attempt {attempt + 1}: {str(exc)[:70]} "
                  f"-- retrying in {wait}s")
            time.sleep(wait)
    print(f"    ! {label}: GIVING UP, this team is MISSING from the sample")
    return []


def summarise(eps, team_id, min_opp=0.0):
    """(our rewards, their rewards, wins, games) from this team's viewpoint."""
    mine, theirs, wins, n = [], [], 0, 0
    for e in eps:
        if e.get("state") != "COMPLETED":
            continue
        agents = e.get("agents", [])
        if len(agents) != 2:
            continue
        us = [a for a in agents if int(a.get("teamId", 0)) == team_id]
        op = [a for a in agents if int(a.get("teamId", 0)) != team_id]
        if not us or not op:
            continue
        if (op[0].get("updatedScore") or 0) < min_opp:
            continue
        a, b = us[0].get("reward"), op[0].get("reward")
        if a is None or b is None:
            continue
        mine.append(float(a))
        theirs.append(float(b))
        n += 1
        if a > b:
            wins += 1
        elif a == b:
            wins += 0.5
    return mine, theirs, wins, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--teams", type=int, default=12)
    ap.add_argument("--min-opp", type=float, default=2500.0)
    ap.add_argument("--pace", type=float, default=20.0,
                    help="seconds between team queries; the endpoint throttles "
                         "hard after a ladder climb and 2s was far too fast")
    args = ap.parse_args()

    rows = leaderboard()
    rating = {int(r["TeamId"]): float(r["Score"]) for r in rows}
    top = [(int(r["TeamId"]), r["TeamName"], float(r["Score"])) for r in rows[:args.teams]]
    ours = [(int(r["TeamId"]), r["TeamName"], float(r["Score"])) for r in rows
            if any(k in r["TeamName"].lower() for k in OUR_TEAM_NAMES)
            or any(k in (r.get("TeamMemberUserNames") or "").lower()
                   for k in OUR_TEAM_NAMES)]

    s = session()
    known = climb(s, rating, {t[0] for t in top} | {o[0] for o in ours})

    done = json.load(open(RESULTS)) if os.path.exists(RESULTS) else {}
    print(f"\n=== TOP {args.teams}: money in games vs opponents rated "
          f">= {args.min_opp:.0f} ===")
    if done:
        print(f"(resuming: {len(done)} teams already collected)")

    for team_id, name, score in top:
        if str(team_id) in done:
            continue
        sub = known.get(team_id)
        if not sub:
            continue
        eps = episodes_for(s, sub, name[:25])
        time.sleep(args.pace)
        mine, theirs, wins, n = summarise(eps, team_id, args.min_opp)
        if not n:
            continue
        done[str(team_id)] = {"name": name, "rating": score, "games": n,
                              "winrate": 100.0 * wins / n, "mine": mine,
                              "theirs": theirs}
        json.dump(done, open(RESULTS, "w"))
        print(f"  collected {name[:25]} ({n} games)")

    print(f"\n{'team':<26}{'rating':>8}{'games':>7}{'win%':>7}"
          f"{'their $':>11}{'opp $':>11}{'median $':>11}")
    allmine = []
    for rec in sorted(done.values(), key=lambda r: -r["rating"]):
        allmine += rec["mine"]
        print(f"{rec['name'][:25]:<26}{rec['rating']:>8.1f}{rec['games']:>7}"
              f"{rec['winrate']:>6.0f}%{statistics.mean(rec['mine']):>11,.0f}"
              f"{statistics.mean(rec['theirs']):>11,.0f}"
              f"{statistics.median(rec['mine']):>11,.0f}")
    missing = [n for _, n, _ in top if not any(r["name"] == n for r in done.values())]
    if missing:
        print(f"\nSTILL MISSING ({len(missing)}): {', '.join(m[:18] for m in missing)}"
              f"\nRe-run later -- results accumulate; the endpoint throttles hard.")

    print(f"\n=== US ===")
    for team_id, name, score in ours:
        sub = known.get(team_id)
        if not sub:
            continue
        mine, theirs, wins, n = summarise(episodes_for(s, sub, name[:25]), team_id, 0.0)
        if not n:
            continue
        print(f"{name[:25]:<26}{score:>8.1f}{n:>7}{100.0 * wins / n:>6.0f}%"
              f"{statistics.mean(mine):>11,.0f}{statistics.mean(theirs):>11,.0f}"
              f"{statistics.median(mine):>11,.0f}")

    if allmine:
        print(f"\nTOP-OF-LADDER money, pooled over {len(allmine)} strong-vs-strong "
              f"games:\n  mean ${statistics.mean(allmine):,.0f}   "
              f"median ${statistics.median(allmine):,.0f}   "
              f"p10 ${sorted(allmine)[len(allmine) // 10]:,.0f}   "
              f"max ${max(allmine):,.0f}")


if __name__ == "__main__":
    main()
