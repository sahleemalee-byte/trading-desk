"""Demo entry point. Run:  python -m trading_desk.run

Simulates one cycle with placeholder data so you can see the whole pipeline
flow — the Trade agent's combined read, a surfaced setup, the human execution
gate, the ledger, the monthly long-term buy plan, and the accounting readouts —
before you fill in any real logic.
"""
from __future__ import annotations

from datetime import date, datetime

from .config import CONFIG
from .context import Fill
from .orchestrator import Orchestrator


def _auto_approve(proposal) -> bool:
    """Stand-in for YOUR decision. In real use this is a prompt / UI / Slack
    reaction. Here it auto-approves so the demo can show a full round-trip."""
    print(f"    [gate] approve {proposal.instrument} {proposal.direction} "
          f"{proposal.setup} @ {proposal.entry}? -> yes (demo)")
    return True


def main() -> None:
    orch = Orchestrator(CONFIG)

    # Force a Wednesday so the trade agent is active in the demo.
    today = date.today()
    while today.weekday() != 2:
        today = today.fromordinal(today.toordinal() + 1)

    print(f"=== cycle {today} ({today.strftime('%A')}) ===\n")
    ctx = orch.run_cycle(today)

    for r in ctx.results:
        print(f"[{r.agent}] {r.summary}")
        for p in r.proposals:
            print(f"    -> {p.instrument} {p.direction} {p.setup} "
                  f"@ {p.entry} (stop {p.stop}, target {p.target})")
        if r.agent == "long_term":
            for row in r.data.get("buy_plan", []):
                print(f"    -> buy ${row['amount']:,.2f} of {row['ticker']}")

    # Execution gate — you approve; then a fill lands on the ledger.
    proposals = [p for r in ctx.results for p in r.proposals]
    if proposals:
        print("\n=== execution gate (human) ===")
        approved = orch.execution_gate(proposals, _auto_approve)

        p = approved[0]
        orch.ledger.record_fill(Fill(
            instrument=p.instrument, direction=p.direction,
            entry=p.entry, exit=p.target, stop=p.stop, size=p.size,
            account=p.account, point_value=p.point_value,
            opened=datetime.now(), closed=datetime.now(),
            macro_at_entry=ctx.sentiment.verdict if ctx.sentiment else None,
        ))
        orch.ledger.record_payout(p.account, 1500.0, today)

    # Re-read the accounting side now that the ledger has data.
    print("\n=== accounting (post-fill) ===")
    print(f"    realized P&L : ${orch.ledger.realized_pnl():,.2f}")
    print(f"    R stats      : {orch.ledger.r_stats()}")
    ctx2 = orch.run_cycle(today)
    for r in ctx2.results:
        if r.agent in ("debt", "tax"):
            print(f"    [{r.agent}] {r.summary}")


if __name__ == "__main__":
    main()
