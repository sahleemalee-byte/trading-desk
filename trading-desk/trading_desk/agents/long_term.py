"""Long-term investment agent — the researcher.

No fixed list. It scans themes/sectors and names, ranks them, and hands you a
short reasoned suggestion. You pick; then it splits your monthly money evenly
across your picks. Runs monthly so it doesn't burn API calls or LLM credits
every day.
"""
from __future__ import annotations

from ..context import AgentResult, Cycle
from .base import Agent

# Deterministic fallback so the system runs with no key. With a key + LLM, the
# research() method below is where live ranking and synthesis slot in.
_FALLBACK_IDEAS = [
    {"theme": "Semiconductors", "verdict": "strong",
     "why": "AI demand plus a cyclical upturn; leaders keep compounding.",
     "names": ["NVDA", "TSM"]},
    {"theme": "AI infrastructure", "verdict": "watch",
     "why": "Datacenter and power buildout is real, but wait for a pullback.",
     "names": ["VRT"]},
    {"theme": "Broad tech", "verdict": "core",
     "why": "Low-cost anchor to hold the sleeve steady.",
     "names": ["QQQ"]},
]


class LongTermAgent(Agent):
    name = "long_term"
    substrate = "llm"   # ranking + synthesis is the LLM's job (monthly only)

    def research(self, ctx: Cycle) -> list[dict]:
        # TODO (runs monthly, not daily, to stay cheap):
        #   1. rank sectors by momentum using sector ETFs (a few quotes)
        #   2. screen names on fundamentals + analyst targets (Twelve Data)
        #   3. ONE LLM call to synthesize a ranked, reasoned shortlist
        # Cache the result to state.json so the app never re-triggers this.
        return list(_FALLBACK_IDEAS)

    def picks(self, ideas: list[dict]) -> list[str]:
        # Fund the names from 'strong' and 'core' themes.
        names: list[str] = []
        for i in ideas:
            if i["verdict"] in ("strong", "core"):
                names += i["names"]
        seen: set[str] = set()
        return [n for n in names if not (n in seen or seen.add(n))]

    def build_plan(self, ctx: Cycle, names: list[str]) -> list[dict]:
        amount = ctx.config["long_term"]["monthly_amount"]
        if not names:
            return []
        per = round(amount / len(names), 2)
        return [{"ticker": n, "amount": per} for n in names]

    def run(self, ctx: Cycle) -> AgentResult:
        lt = ctx.config["long_term"]
        ideas = self.research(ctx)
        names = self.picks(ideas)
        plan = self.build_plan(ctx, names)
        strong = [i["theme"] for i in ideas if i["verdict"] == "strong"]
        head = ", ".join(strong[:2]) if strong else "no standout themes"
        return self._result(
            f"Ideas this month: {head}. Funding {len(names)} name(s), "
            f"${lt['monthly_amount']:,.0f} split evenly.",
            data={
                "ideas": ideas,
                "buy_plan": plan,
                "monthly_amount": lt["monthly_amount"],
                "is_research_day": ctx.today.day == lt["buy_day_of_month"],
                "stubbed": True,
            },
        )
