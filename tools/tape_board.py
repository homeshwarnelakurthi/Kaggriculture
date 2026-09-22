"""Replay the strong agent's action tape locally and measure the board it builds.

The top-of-ladder replay endpoint is gone from Kaggle's API, so we cannot see a
3000-rated game directly. But we HOLD one strong agent's full action tape: the
`main.py` submission is a replay clone of a public notebook that peaked at 1358
(top 27% of 2,976), and its 719 recorded turns are embedded in
public_kernels/adaptive_agent.py.

Replaying it against our own environment gives a direct, API-free measurement of
how a strong agent EXECUTES, on exactly the axes we measure ourselves:

    tiles carrying anything   (ours: ~30 of ~91 workable)
    action split              (ours: 66% move / 23% work / 10% idle)
    herd, crop mix, land timing, weeds

Caveat worth stating plainly: a tape is a fixed action sequence recorded against
some other opponent. Replayed here it will desync from the board it expects, so
treat the LATE game as unreliable and the opening as solid. That is also exactly
why the tape decays on the ladder -- it cannot respond.

  python tools/tape_board.py
"""

import contextlib
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    from kaggle_environments import make

from kagri.farm import View

KERNEL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "public_kernels", "adaptive_agent.py")

MOVES = {"NORTH", "SOUTH", "EAST", "WEST"}
PROBE_DAYS = (2, 4, 8, 12, 16, 20, 26)


def load_tape():
    """Pull the base85 blob out of the notebook export and decode it."""
    import base64
    import json
    import zlib

    src = open(KERNEL, encoding="utf-8", errors="replace").read()
    # This is a NOTEBOOK EXPORT, so the agent source appears several times at
    # different nesting depths (once raw, once backslash-escaped inside another
    # string). Collect every candidate blob and take the first that decodes --
    # guessing one shape gave "bad base85 character at position 10470".
    cands = []
    for m in re.finditer(r"SASH_ACTIONS_B85\s*=\s*\\?'([^']{500,})\\?'", src):
        cands.append(m.group(1))
    for m in re.finditer(
            r"_ACTIONS\s*=\s*json\.loads\(zlib\.decompress\(base64\.b85decode\(\s*\((.*?)\)\s*\)\s*\.decode\(\)\)",
            src, re.S):
        cands.append("".join(re.findall(r"'([^']*)'", m.group(1))))

    for blob in cands:
        blob = blob.strip().replace("\\n", "").replace("\n", "")
        try:
            tape = json.loads(zlib.decompress(base64.b85decode(blob)).decode())
        except Exception:
            continue
        if isinstance(tape, list) and tape:
            return tape
    raise SystemExit(f"no decodable tape found ({len(cands)} candidates tried)")


def main():
    tape = load_tape()
    print(f"tape: {len(tape)} recorded turns\n")

    stat = {"move": 0, "work": 0, "pass": 0}
    log = {}

    def taped(obs):
        v = View(obs)
        trace = tape[min(max(int(v.step), 0), len(tape) - 1)] or {}
        farmer = list(trace.get("farmer") or ["PASS"])
        hands = [list(h) for h in (trace.get("hands") or [])]
        # The farm may have a different number of hands than the recording.
        hands = (hands + [["PASS"]] * v.n_units)[:max(0, v.n_units - 1)]
        for a in [farmer] + hands:
            op = a[0] if a else "PASS"
            if op in MOVES:
                stat["move"] += 1
            elif op == "PASS":
                stat["pass"] += 1
            else:
                stat["work"] += 1
        if v.hour == 23 and v.day in PROBE_DAYS:
            counts = {}
            for row in v.tiles:
                for t in row:
                    if isinstance(t, dict):
                        k = (t.get("animal") or
                             (t["crop"] if t.get("kind") == "PLANT" else t.get("kind")))
                        counts[k] = counts.get(k, 0) + 1
            carrying = sum(n for k, n in counts.items() if k != "WEED")
            log[v.day] = (carrying, counts.get("WEED", 0), len(v.unlocked),
                          int(v.money), v.n_units - 1, dict(counts))
        return {"farmer": farmer, "hands": hands,
                "market": list(trace.get("market") or [])}

    with contextlib.redirect_stderr(io.StringIO()):
        env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 42},
                   debug=False)
        env.run([taped, "starter"])

    total = max(1, sum(stat.values()))
    print(f"{'day':>4}{'tiles used':>12}{'weeds':>7}{'quads':>7}"
          f"{'money':>10}{'hands':>7}  board")
    for d in PROBE_DAYS:
        if d not in log:
            continue
        used, weeds, quads, money, hands, counts = log[d]
        board = " ".join(f"{k}:{n}" for k, n in sorted(counts.items())
                         if k and k != "WEED")
        print(f"{d:>4}{used:>12}{weeds:>7}{quads:>7}{money:>10,}{hands:>7}  {board}")

    print(f"\nACTION SPLIT over {total:,} unit-actions:")
    print(f"  move {100.0 * stat['move'] / total:5.1f}%   "
          f"work {100.0 * stat['work'] / total:5.1f}%   "
          f"idle {100.0 * stat['pass'] / total:5.1f}%")
    print(f"  OURS, measured earlier:  move 66%   work 23%   idle 10%")
    print(f"\nfinal: {[s.reward for s in env.steps[-1]]}")


if __name__ == "__main__":
    main()
