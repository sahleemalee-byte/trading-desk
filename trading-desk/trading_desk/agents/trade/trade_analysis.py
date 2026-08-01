"""Trade analysis sub-agent — lives under the Trade agent.

Your actual setups: the R.R. multi-timeframe read (4H -> 30m -> 5m) and the
triggers (IB breakout / 20 EMA rejection / 15m FVG). It only *finds* trades and
sizes risk; the Trade agent decides whether the tape allows taking them, and you
place them. This never sends an order.
"""
from __future__ import annotations

from ..base import SubAgent
from ...context import Cycle, TradeProposal


class TradeAnalysisSubAgent(SubAgent):
    name = "trade_analysis"

    def read(self, ctx: Cycle) -> dict:
        cfg = ctx.config
        # TODO: your real 4H/30m/5m read + triggers.
        proposals = [
            TradeProposal(
                instrument="NQ",
                direction="long",
                setup="IB breakout",
                entry=28226.0,
                stop=28196.0,
                target=28316.0,
                size=cfg["default_size"],
                account=cfg["accounts"]["prop_primary"],
                rationale="Reclaim of 28,226 pivot with KOSPI-led semis bid.",
            )
        ]
        return {"proposals": proposals}
