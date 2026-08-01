"""PnL growth sub-agent — lives under the Trade agent.

Watches how the day/week is going by reading the ledger. Its main job for the
Trade agent is the daily-stop rule: once realized P&L hits your daily target,
it flags that you're done, and the Trade agent stops surfacing setups.
"""
from __future__ import annotations

from ..base import SubAgent
from ...context import Cycle


class PnLGrowthSubAgent(SubAgent):
    name = "pnl_growth"

    def read(self, ctx: Cycle) -> dict:
        realized = ctx.ledger.realized_pnl()
        target = ctx.config["daily_target"]
        return {
            "realized": realized,
            "target": target,
            "target_hit": realized >= target,
            "r_stats": ctx.ledger.r_stats(),
        }
