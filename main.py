"""Kaggriculture submission entry point.

Kaggle unpacks the bundle into /kaggle_simulations/agent/, so make sure the
package directory next to this file is importable before touching it.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from kagri.agent import act  # noqa: E402

_SAFE = {"farmer": ["PASS"], "hands": [], "market": []}


def agent(obs, config=None):
    try:
        return act(obs)
    except Exception:
        # A crash forfeits the whole episode; a passed turn costs one turn.
        import traceback
        traceback.print_exc()
        farms = obs["farms"] if isinstance(obs, dict) else obs.farms
        player = obs["player"] if isinstance(obs, dict) else obs.player
        n_hands = len(farms[player].get("hands", []))
        return {"farmer": ["PASS"], "hands": [["PASS"]] * n_hands, "market": []}
