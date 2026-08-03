"""Run one episode and print a short diagnostic. Usage: python tools/run.py [opp] [steps]"""

import contextlib
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    from kaggle_environments import make  # noqa: E402

from kagri.agent import act  # noqa: E402


def my_agent(obs):
    return act(obs)


def main():
    opp = sys.argv[1] if len(sys.argv) > 1 else "starter"
    steps = int(sys.argv[2]) if len(sys.argv) > 2 else 720
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 42

    env = make("kaggriculture",
               configuration={"episodeSteps": steps, "seed": seed},
               debug=True)
    env.run([my_agent, opp])

    final = env.steps[-1]
    obs = final[0].observation
    print(f"--- vs {opp}, {steps} steps, seed {seed} ---")
    for i, s in enumerate(final):
        print(f"player {i}: reward={s.reward} status={s.status}")

    farm = obs["farms"][0]
    priv = final[0].observation["private"]
    counts = {}
    for row in farm["tiles"]:
        for t in row:
            if isinstance(t, dict):
                k = t.get("animal") or ("PLANT:" + t["crop"] if t.get("kind") == "PLANT" else t.get("kind"))
                counts[k] = counts.get(k, 0) + 1
    print("my tiles :", counts)
    print("quadrants:", farm["unlocked_quadrants"])
    print("shed     :", {k: v for k, v in priv["shed"].items() if v})
    print("prices   :", obs["market"]["prices"])
    print("mkt inv  :", {k: v - 10000 for k, v in obs["market"]["inventory"].items()})


if __name__ == "__main__":
    main()
