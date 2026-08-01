"""Base class every agent/department inherits from.

An agent does exactly one thing: read the cycle context, do its work, and
return an AgentResult. It never places orders, moves money, or mutates another
agent's state. Keeping this contract narrow is what lets you develop, test, and
swap each agent in isolation.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..context import AgentResult, Cycle


class Agent(ABC):
    name: str = "agent"

    #: SUBSTRATE hint for you, not enforced:
    #:   "rules" -> deterministic code (risk, consistency, tax math)
    #:   "llm"   -> reasons over fuzzy inputs (news, gamma context, screening)
    substrate: str = "rules"

    @abstractmethod
    def run(self, ctx: Cycle) -> AgentResult:
        """Do the work and return a result. Must not have side effects beyond
        appending to the ledger via ctx.ledger (accounting agents read only)."""
        raise NotImplementedError

    def _result(self, summary: str, **kw) -> AgentResult:
        return AgentResult(agent=self.name, summary=summary, **kw)


class SubAgent(ABC):
    """A worker that lives *under* the Trade agent (sentiment, gamma, news,
    trade analysis, PnL growth). It doesn't produce a final result — it produces
    a small piece of the read that the Trade agent combines."""
    name: str = "sub"

    @abstractmethod
    def read(self, ctx: Cycle) -> dict:
        raise NotImplementedError
