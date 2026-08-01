"""Gamma sub-agent — lives under the Trade agent.

Dealer gamma positioning as its own signal layer (you asked for this to be
separate from sentiment). Returns a score in [-1, +1] and a plain-language
state. Long-gamma / supportive tape -> positive; short-gamma / unstable -> negative.
"""
from __future__ import annotations

from ..base import SubAgent
from ...context import Cycle


class GammaSubAgent(SubAgent):
    name = "gamma"

    def read(self, ctx: Cycle) -> dict:
        # TODO: input your gamma read here (dealer positioning, flip level,
        # distance to it). Placeholder: supportive / long-gamma.
        score = 1.0
        state = "long gamma (supportive)"
        return {"score": score, "state": state}
