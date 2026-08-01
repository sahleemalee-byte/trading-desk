"""Long-term investment agent — your personal live account.

Once a month it takes your contribution and splits it EQUALLY across your
watchlist (NVDA, TSLA, SMH/SOX, TSM, ...). It also scans for names worth adding,
but the money it already has gets divided evenly — same dollar amount into each
name, every month. It builds a buy plan; it does not place orders.
"""
from __future__ import annotations

from ..context import AgentResult, Cycle
from .base import Agent


class LongTermAgent(Agent):
    name = "long_term"
    substrate = "llm"   # the "what's worth adding" scan is LLM-assisted

    def scan_watchlist(self, ctx: Cycle) -> list[str]:
        # TODO: scan for good long-term candidates and suggest add/drop.
        # For now the watchlist comes straight from config.
        return list(ctx.config["long_term"]["watchlist"])

    def build_buy_plan(self, ctx: Cycle) -> list[dict]:
        lt = ctx.config["long_term"]
        names = self.scan_watchlist(ctx)
        amount = lt["monthly_amount"]
        if not names:
            return []
        per = round(amount / len(names), 2)
        return [{"ticker": t, "amount": per} for t in names]

    def run(self, ctx: Cycle) -> AgentResult:
        plan = self.build_buy_plan(ctx)
        lt = ctx.config["long_term"]
        is_buy_day = ctx.today.day == lt["buy_day_of_month"]
        per = plan[0]["amount"] if plan else 0.0

        when = "today" if is_buy_day else f"on day {lt['buy_day_of_month']}"
        return self._result(
            f"Equal split: ${lt['monthly_amount']:,.0f} / {len(plan)} names = "
            f"${per:,.2f} each, buy {when}.",
            data={"buy_plan": plan, "is_buy_day": is_buy_day},
        )
