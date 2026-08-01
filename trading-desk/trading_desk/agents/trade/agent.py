"""Trade agent — the umbrella. Your whole trading brain.

It runs its sub-agents (sentiment, gamma, news, trade analysis, PnL growth) and
combines them into ONE read, then applies your gates in order:
  1. Calendar   — Mon–Thu only.
  2. PnL stop   — done once the daily target is hit.
  3. Tape gate  — no setups on a MIXED read.
Only if all three pass does it surface trade proposals — which still go to you.

Combining rule (tune the weights): sentiment 60%, gamma 40%. News is carried as
context for now, not a number.
"""
from __future__ import annotations

from ..base import Agent
from ...context import AgentResult, Cycle, SentimentVerdict, Verdict
from .sentiment import SentimentSubAgent
from .gamma import GammaSubAgent
from .news import NewsSubAgent
from .trade_analysis import TradeAnalysisSubAgent
from .pnl_growth import PnLGrowthSubAgent

_W_SENTIMENT = 0.60
_W_GAMMA = 0.40


class TradeAgent(Agent):
    name = "trade"
    substrate = "llm"   # the news/context read is LLM-assisted; the rest is rules

    def __init__(self) -> None:
        self.sentiment = SentimentSubAgent()
        self.gamma = GammaSubAgent()
        self.news = NewsSubAgent()
        self.analysis = TradeAnalysisSubAgent()
        self.pnl = PnLGrowthSubAgent()

    def _combine(self, ctx: Cycle) -> SentimentVerdict:
        s = self.sentiment.read(ctx)
        g = self.gamma.read(ctx)
        n = self.news.read(ctx)
        self.last_stubbed = s.get("stubbed", False)   # True = placeholder data
        score = _W_SENTIMENT * s["score"] + _W_GAMMA * g["score"]

        if score >= 0.33:
            verdict = Verdict.RISK_ON
        elif score <= -0.33:
            verdict = Verdict.RISK_OFF
        else:
            verdict = Verdict.MIXED

        signals = dict(s["signals"])
        signals["dealer_gamma"] = g["state"]
        signals["news"] = n["note"]
        return SentimentVerdict(verdict=verdict, score=round(score, 2), signals=signals)

    def run(self, ctx: Cycle) -> AgentResult:
        ctx.sentiment = self._combine(ctx)                 # the combined read
        read = ctx.sentiment
        flag = {"stubbed": self.last_stubbed}

        if not ctx.is_trading_day:
            return self._result(
                f"{read.verdict.value} — skipped (Friday/non-trading day).", data=flag)

        pnl = self.pnl.read(ctx)
        if pnl["target_hit"]:
            return self._result(
                f"{read.verdict.value} — target hit (${pnl['realized']:,.0f}), done for the day.",
                data=flag)

        if not read.tradeable:
            return self._result(f"{read.verdict.value} — standing down, no setups.", data=flag)

        proposals = self.analysis.read(ctx)["proposals"]
        for p in proposals:
            p.rationale += f"  [risk ${p.risk_dollars:,.0f}, {p.reward_risk}R]"
        return self._result(
            f"{read.verdict.value} (score {read.score:+.2f}) — "
            f"{len(proposals)} setup(s), pending your approval.",
            proposals=proposals,
            data={"verdict": read.verdict.value, "score": read.score,
                  "signals": read.signals, "stubbed": self.last_stubbed},
        )
