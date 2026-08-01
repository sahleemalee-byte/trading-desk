"""Tax department — reads the ledger, estimates reserves.

The sharpest-edged department. Two income streams, two treatments:
  - Futures P&L  -> IRC section 1256: marked-to-market, 60% long-term /
                    40% short-term regardless of holding period.
  - Prop payouts -> 1099 income, taxed as ordinary income.

Everything here is a ROUGH RESERVE ESTIMATE to keep cash set aside and to hand
your CPA clean numbers. It is NOT tax advice and it is not a filing. Rates are
placeholders in config — confirm your real brackets with your CPA.
"""
from __future__ import annotations

from ..context import AgentResult, Cycle
from .base import Agent


class TaxDepartment(Agent):
    name = "tax"
    substrate = "rules"

    def run(self, ctx: Cycle) -> AgentResult:
        cfg = ctx.config
        lt_rate = cfg["tax"]["long_term_rate"]     # e.g. 0.15
        st_rate = cfg["tax"]["short_term_rate"]    # ordinary bracket, e.g. 0.24

        futures_pnl = ctx.ledger.realized_pnl()
        prop_income = ctx.ledger.payouts_total()

        # 1256 60/40 blend on futures gains (only tax positive P&L here).
        futures_gain = max(futures_pnl, 0.0)
        sec1256 = futures_gain * (0.60 * lt_rate + 0.40 * st_rate)

        # Prop payouts as ordinary income.
        prop_tax = prop_income * st_rate

        # State tax (Illinois flat rate) on futures gains + prop income.
        state_rate = cfg["tax"].get("state_rate", 0.0)
        state_tax = (futures_gain + prop_income) * state_rate

        federal = sec1256 + prop_tax
        reserve = round(federal + state_tax, 2)
        return self._result(
            f"Set aside ~${reserve:,.0f} "
            f"(federal ${federal:,.0f} + IL state ${state_tax:,.0f}). "
            "Estimate only — confirm with your CPA.",
            data={
                "futures_pnl": futures_pnl,
                "prop_income": prop_income,
                "federal": round(federal, 2),
                "state": round(state_tax, 2),
                "estimated_reserve": reserve,
            },
        )
