"""News sub-agent — lives under the Trade agent.

Headlines and scheduled events (CPI, FOMC, earnings). For now it contributes a
plain-language note rather than a hard score, since news is the fuzziest input —
this is the natural place for an LLM pass (summarize overnight tape, flag event
risk). The Trade agent treats it as context, not a number, until you score it.
"""
from __future__ import annotations

from ..base import SubAgent
from ...context import Cycle


class NewsSubAgent(SubAgent):
    name = "news"

    def read(self, ctx: Cycle) -> dict:
        # TODO: pull headlines + the economic calendar. Optionally run an LLM
        # pass to summarize and flag event risk for the day.
        return {"note": "no major scheduled events", "event_risk": False}
