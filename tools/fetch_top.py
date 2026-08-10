"""Fetch replays of games between TOP-OF-LADDER agents.

Why this exists: we hold 203 cached replays and every one is from our own
~650-rated matches, so every "real opponent" archetype in tools/gauntlet.py was
reconstructed from mid-ladder players who happened to beat us. We have never
observed a game between two strong agents, and we have been tuning against a
field we never measured.

The episode endpoint refuses a bare teamId ("You must specify at least one ID
filter"), but ListEpisodes{submissionId} works AND returns a `teams` array in
which every entry carries `publicLeaderboardSubmissionId`. So we snowball: seed
with one known submission, harvest team -> submission ids, then pull the top
teams' episodes directly.

  python tools/fetch_top.py --teams 10 --per-team 6 --min-opp 2500

Writes replays/top/episode-<id>-replay.json plus a manifest.
"""

import argparse
import csv
import glob
import json
import os
import time

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "replays", "top")
BASE = "https://www.kaggle.com/api/i/competitions.EpisodeService"
SEED_SUBMISSION = 55134735          # one of ours; any completed submission works


def session():
    path = os.path.join(os.path.expanduser("~"), ".kaggle", "kaggle.json")
    d = json.load(open(path))
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
    raise RuntimeError(f"{endpoint} failed after {tries} tries")


def leaderboard(limit):
    files = glob.glob(os.path.join(ROOT, "replays", "*publicleaderboard*.csv"))
    if not files:
        raise SystemExit("no leaderboard CSV in replays/; download one first")
    path = max(files, key=os.path.getmtime)
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    print(f"leaderboard: {os.path.basename(path)} ({len(rows)} teams)")
    return [(int(r["TeamId"]), r["TeamName"], float(r["Score"])) for r in rows[:limit]]


def harvest_team_submissions(s, seed_subs):
    """teamId -> publicLeaderboardSubmissionId, snowballed from seed queries."""
    known = {}
    for sub in seed_subs:
        try:
            data = post(s, "ListEpisodes", {"submissionId": sub})
        except Exception as exc:
            print(f"  ! seed {sub}: {exc}")
            continue
        for t in data.get("teams", []):
            plsid = t.get("publicLeaderboardSubmissionId")
            if plsid:
                known[int(t["id"])] = int(plsid)
    return known


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--teams", type=int, default=10)
    ap.add_argument("--per-team", type=int, default=6)
    ap.add_argument("--max-hops", type=int, default=8,
                    help="ladder-climbing rounds; each queries the strongest "
                         "known-but-unqueried teams to discover stronger ones")
    ap.add_argument("--hop-width", type=int, default=6)
    ap.add_argument("--min-opp", type=float, default=2500.0,
                    help="only keep games where the OPPONENT is at least this "
                         "strong -- we want strong-vs-strong, not a top agent "
                         "farming a weak one")
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    s = session()

    top = leaderboard(args.teams)
    known = harvest_team_submissions(s, [SEED_SUBMISSION])
    print(f"harvested {len(known)} team->submission ids from the seed")

    # CLIMB. The seed only ever yields teams WE have played, which by
    # matchmaking are all near our own rating -- none of the top 10 appear.
    # So walk up: repeatedly query the strongest team we know but have not
    # queried, harvesting its opponents. Each hop moves us up the ladder.
    rating = {tid: sc for tid, _, sc in leaderboard(10_000)}
    wanted = {t[0] for t in top}
    queried = set()
    for hop in range(args.max_hops):
        if wanted <= set(known):
            break
        pool = [(rating.get(tid, 0.0), tid) for tid in known if tid not in queried]
        pool.sort(reverse=True)
        batch = [tid for _, tid in pool[:args.hop_width]]
        if not batch:
            break
        before = len(known)
        for tid in batch:
            queried.add(tid)
        known.update(harvest_team_submissions(s, [known[tid] for tid in batch]))
        best = max((rating.get(t, 0.0) for t in known), default=0.0)
        print(f"  hop {hop + 1}: {before} -> {len(known)} teams, "
              f"best rating seen {best:.1f}, "
              f"{len(wanted & set(known))}/{len(wanted)} targets resolved")

    missing = [t for t in top if t[0] not in known]
    if missing:
        print(f"unresolved teams (skipped): {[m[1] for m in missing]}")

    manifest, seen = [], set()
    for team_id, name, score in top:
        sub = known.get(team_id)
        if not sub:
            continue
        try:
            data = post(s, "ListEpisodes", {"submissionId": sub})
        except Exception as exc:
            print(f"  ! {name}: {exc}")
            continue

        rated = []
        for e in data.get("episodes", []):
            if e.get("state") != "COMPLETED":
                continue
            agents = e.get("agents", [])
            if len(agents) != 2:
                continue
            others = [a for a in agents if int(a.get("teamId", 0)) != team_id]
            if not others:
                continue
            opp = others[0].get("updatedScore") or 0
            if opp >= args.min_opp:
                rated.append((opp, e))
        rated.sort(key=lambda t: -t[0])
        best = f"{rated[0][0]:.0f}" if rated else "-"
        print(f"{name:<30}{score:>8.1f}  {len(data.get('episodes', [])):>4} eps, "
              f"{len(rated):>3} vs >={args.min_opp:.0f}, best opp {best}")

        for opp_rating, e in rated[:args.per_team]:
            eid = e["id"]
            if eid in seen:
                continue
            seen.add(eid)
            path = os.path.join(OUT, f"episode-{eid}-replay.json")
            if not os.path.exists(path):
                try:
                    rep = post(s, "GetEpisodeReplay", {"episodeId": eid})
                except Exception as exc:
                    print(f"    ! replay {eid}: {exc}")
                    continue
                open(path, "w", encoding="utf-8").write(json.dumps(rep))
                time.sleep(1.0)
            manifest.append({"episode": eid, "team": name, "team_rating": score,
                             "opp_rating": opp_rating})

    open(os.path.join(OUT, "manifest.json"), "w").write(json.dumps(manifest, indent=1))
    print(f"\n{len(manifest)} strong-vs-strong replays in {OUT}")


if __name__ == "__main__":
    main()
