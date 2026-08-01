"""Sentiment sub-agent — lives under the Trade agent.

Your ETF-proxy composite (VIX/SMH/KOSPI/IEF/SHY/USDJPY). It no longer hardcodes
signals — it asks the data department (MarketData) for clean, checked data. If
there's no API key or a fetch fails, MarketData returns placeholders and marks
itself stubbed, so this keeps running either way.
"""
from __future__ import annotations

from ..base import SubAgent
from ...context import Cycle
from ...data import MarketData

_STATE_SCORE = {"risk-on": 1.0, "neutral": 0.0, "risk-off": -1.0}


class SentimentSubAgent(SubAgent):
    name = "sentiment"

    def __init__(self, market: MarketData | None = None) -> None:
        self.market = market or MarketData()

    def read(self, ctx: Cycle) -> dict:
        signals = self.market.get_risk_signals()
        score = sum(_STATE_SCORE.get(v, 0.0) for v in signals.values()) / len(signals)
        return {
            "score": round(score, 2),
            "signals": signals,
            "stubbed": self.market.stubbed,   # True = ran on placeholder data
        }
