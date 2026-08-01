"""Debt department — reads the ledger, tracks the year-end obligation.

Consumes payouts (not trades) and answers: how much is left, and are you on
pace. Once the obligation is cleared, its recommendation flips to routing
surplus toward savings/investing — your stated pivot.

This is decision-support, not financial advice.
"""
from __future__ import annotations

from datetime import date

from ..context import AgentResult, Cycle
from .base import Agent


class DebtDepartment(Agent):
    name = "debt"
    substrate = "rules"

    def run(self, ctx: Cycle) -> AgentResult:
        target = ctx.config["obligation_target"]
        deadline = ctx.config["obligation_deadline"]     # a date
        paid = ctx.ledger.payouts_total()
        remaining = round(max(target - paid, 0.0), 2)

        if remaining <= 0:
            return self._result(
                f"Obligation cleared (${paid:,.0f} paid). "
                "Recommendation: route surplus to savings/investing.",
                data={"remaining": 0.0, "status": "cleared"},
            )

        weeks_left = max((deadline - ctx.today).days / 7, 0.01)
        pace = round(remaining / weeks_left, 2)
        return self._result(
            f"${remaining:,.0f} left; need ~${pace:,.0f}/week for "
            f"{weeks_left:.0f} weeks.",
            data={"remaining": remaining, "weekly_pace_needed": pace},
        )
