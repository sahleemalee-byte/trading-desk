"""Shared data structures passed between agents.

Everything the agents read or produce flows through these objects, so the
pipeline stays decoupled: an agent depends only on the *shape* of the context,
never on another agent's internals. Swap any agent's implementation and the
rest of the system keeps working.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


class Verdict(str, Enum):
    RISK_ON = "RISK-ON"
    RISK_OFF = "RISK-OFF"
    MIXED = "MIXED"


@dataclass
class SentimentVerdict:
    """Output of the market sentiment agent — the gate for everything else."""
    verdict: Verdict
    score: float                                     # composite, -1.0 .. +1.0
    signals: dict[str, str] = field(default_factory=dict)   # signal -> state
    as_of: datetime = field(default_factory=datetime.now)

    @property
    def tradeable(self) -> bool:
        # You stand down on MIXED days.
        return self.verdict is not Verdict.MIXED


@dataclass
class TradeProposal:
    """A setup an agent wants to take.

    IMPORTANT: this is a *proposal*, never an executed order. It goes to the
    execution gate, where you (the human) approve and place it yourself.
    """
    instrument: str
    direction: str                # "long" / "short"
    setup: str                    # "IB breakout", "20 EMA", "15m FVG", ...
    entry: float
    stop: float
    target: float
    size: int
    account: str
    point_value: float = 20.0     # NQ = $20/pt, MNQ = $2/pt
    rationale: str = ""

    @property
    def risk_points(self) -> float:
        return abs(self.entry - self.stop)

    @property
    def risk_dollars(self) -> float:
        return self.risk_points * self.size * self.point_value

    @property
    def reward_risk(self) -> float:
        r = self.risk_points
        return round(abs(self.target - self.entry) / r, 2) if r else 0.0


@dataclass
class Fill:
    """A trade that actually happened, recorded to the ledger."""
    instrument: str
    direction: str
    entry: float
    exit: float
    stop: float
    size: int
    account: str
    opened: datetime
    closed: Optional[datetime] = None
    point_value: float = 20.0
    macro_at_entry: Optional[Verdict] = None   # snapshot of the gate at entry

    @property
    def _move(self) -> float:
        return (self.exit - self.entry) if self.direction == "long" else (self.entry - self.exit)

    @property
    def pnl(self) -> float:
        return round(self._move * self.size * self.point_value, 2)

    @property
    def r_multiple(self) -> Optional[float]:
        risk = abs(self.entry - self.stop)
        return round(self._move / risk, 2) if risk else None


@dataclass
class AgentResult:
    """What every agent hands back to the orchestrator."""
    agent: str
    summary: str
    proposals: list[TradeProposal] = field(default_factory=list)
    data: dict = field(default_factory=dict)


@dataclass
class Cycle:
    """The context object threaded through one run of the pipeline."""
    today: date
    ledger: "object"              # trading_desk.ledger.Ledger (avoid circular import)
    config: dict
    sentiment: Optional[SentimentVerdict] = None
    results: list[AgentResult] = field(default_factory=list)

    @property
    def is_trading_day(self) -> bool:
        # You trade Monday–Thursday only; skip Fridays.
        return self.today.weekday() <= 3  # Mon=0 .. Thu=3
