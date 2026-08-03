"""Kaggriculture submission entry point.

Kaggle loads this file by exec-ing its source, NOT by importing it as a module,
so `__file__` is undefined at runtime. Anything that assumes otherwise fails the
validation episode immediately with:

    InvalidArgument: Invalid raw Python: NameError("name '__file__' is not defined")

Submissions are unpacked into /kaggle_simulations/agent/, so probe that first
and fall back to whatever locations exist locally.
"""

import os
import sys


def _add_package_dir():
    candidates = ["/kaggle_simulations/agent"]
    try:
        candidates.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass  # exec'd source: no __file__, which is the normal Kaggle path
    candidates.append(os.getcwd())
    for d in candidates:
        if d and os.path.isdir(os.path.join(d, "kagri")) and d not in sys.path:
            sys.path.insert(0, d)
            return d
    return None


_add_package_dir()

from kagri.agent import act  # noqa: E402


def agent(obs, config=None):
    try:
        return act(obs)
    except Exception:
        # A crash forfeits the episode; a passed turn costs one turn. Always
        # return a well-formed action with one op per hand the farm actually has.
        import traceback
        traceback.print_exc()
        try:
            farms = obs["farms"] if isinstance(obs, dict) else obs.farms
            player = obs["player"] if isinstance(obs, dict) else obs.player
            n_hands = len(farms[player].get("hands", []))
        except Exception:
            n_hands = 0
        return {"farmer": ["PASS"], "hands": [["PASS"]] * n_hands, "market": []}
