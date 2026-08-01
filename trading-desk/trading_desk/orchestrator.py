"""Orchestrator — runs one cycle in the right order and holds the execution gate.

Order matters: sentiment first (it gates the trading agents), then the two
trading agents, then the accounting departments read the ledger. The execution
gate sits between "agent proposed a trade" and "trade exists" — and it requires
you. Nothing here places an order or moves money.
"""
from __future__ import annotations

from datetime import date

from .context import Cycle, TradeProposal
from .ledger import Ledger
from .agents import (
    TradeAgent,
    LongTermAgent,
    DebtDepartment,
    TaxDepartment,
)


class Orchestrator:
    def __init__(self, config: dict, ledger: Ledger | None = None) -> None:
        self.config = config
        self.ledger = ledger or Ledger()
        # Trade agent runs first (it sets the read); accounting runs last.
        self.pipeline = [
            TradeAgent(),
            LongTermAgent(),
            DebtDepartment(),
            TaxDepartment(),
        ]

    def run_cycle(self, today: date | None = None) -> Cycle:
        ctx = Cycle(today=today or date.today(), ledger=self.ledger, config=self.config)
        for agent in self.pipeline:
            ctx.results.append(agent.run(ctx))
        return ctx

    # --- the human-in-the-loop boundary ----------------------------------
    def execution_gate(self, proposals: list[TradeProposal], confirm) -> list[TradeProposal]:
        """Present proposals for approval. `confirm(proposal) -> bool` is YOUR
        decision (a prompt, a UI click, a Slack reaction). This method returns
        the approved list; it deliberately does NOT connect to any broker.

        Placing the order, and any transfer of funds, stays with you.
        """
        approved = []
        for p in proposals:
            if confirm(p):
                approved.append(p)
        return approved
