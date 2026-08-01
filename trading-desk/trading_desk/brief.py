"""Daily brief — the REAL scheduled entry point (this is what the timer runs).

Unlike run.py (a demo that fabricates a trade to show the flow), this is
read-only: it loads your saved ledger, fetches live data, runs the agents, and
prints the brief. It does NOT invent trades — real fills only get recorded when
you approve them. It saves the ledger back so nothing is forgotten between runs.

Run:  python -m trading_desk.brief
"""
from __future__ import annotations

from datetime import date

from .config import CONFIG
from .ledger import Ledger
from .orchestrator import Orchestrator

LEDGER_PATH = "ledger.json"


def main() -> None:
    ledger = Ledger.load(LEDGER_PATH)          # remembers previous runs
    orch = Orchestrator(CONFIG, ledger=ledger)
    ctx = orch.run_cycle(date.today())

    print(f"=== daily brief {date.today()} ({date.today().strftime('%A')}) ===")
    for r in ctx.results:
        print(f"[{r.agent}] {r.summary}")
        for p in r.proposals:
            print(f"    -> {p.instrument} {p.direction} {p.setup} @ {p.entry} "
                  f"(stop {p.stop}, target {p.target})")
        for row in r.data.get("buy_plan", []):
            print(f"    -> buy ${row['amount']:,.2f} of {row['ticker']}")

    # Warn loudly if we ran on placeholder data (no key / fetch failed).
    trade = next((r for r in ctx.results if r.agent == "trade"), None)
    if trade and trade.data.get("stubbed"):
        print("\n[!] running on PLACEHOLDER data — set TWELVEDATA_API_KEY for live signals")

    ledger.save(LEDGER_PATH)


if __name__ == "__main__":
    main()
