"""Publish — run the pipeline once and write one state.json the app reads.

This is the efficient core: a single run produces everything, and the web app is
static (it just reads this file), so viewing the desk costs nothing. Run:

    python -m trading_desk.publish
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict
from datetime import date, datetime

from .config import CONFIG
from .ledger import Ledger
from .orchestrator import Orchestrator

STATE_PATH = os.environ.get("DESK_STATE_PATH", "docs/state.json")
LEDGER_PATH = "ledger.json"


def build_state(ctx, ledger: Ledger) -> dict:
    by = {r.agent: r for r in ctx.results}

    def data(name):
        r = by.get(name)
        return dict(r.data) if r and r.data else {}

    def summary(name):
        r = by.get(name)
        return r.summary if r else ""

    trade = by.get("trade")
    proposals = [asdict(p) for p in (trade.proposals if trade else [])]

    highlights = []
    if proposals:
        highlights.append(f"{len(proposals)} trade setup(s) pending your ok")
    if data("trade").get("stubbed"):
        highlights.append("running on placeholder data — add your API key")
    debt_left = data("debt").get("remaining")
    if debt_left == 0:
        highlights.append("debt cleared — route surplus to savings")

    return {
        "as_of": datetime.now().isoformat(timespec="minutes"),
        "day": ctx.today.isoformat(),
        "weekday": ctx.today.strftime("%A"),
        "highlights": highlights,
        "trade": {"summary": summary("trade"), "proposals": proposals, **data("trade")},
        "long_term": {"summary": summary("long_term"), **data("long_term")},
        "debt": {"summary": summary("debt"), **data("debt")},
        "tax": {"summary": summary("tax"), **data("tax")},
        "ledger": {
            "realized_pnl": ledger.realized_pnl(),
            "payouts_total": ledger.payouts_total(),
            "r_stats": ledger.r_stats(),
        },
    }


def main() -> None:
    ledger = Ledger.load(LEDGER_PATH)
    orch = Orchestrator(CONFIG, ledger=ledger)
    ctx = orch.run_cycle(date.today())

    state = build_state(ctx, ledger)
    os.makedirs(os.path.dirname(STATE_PATH) or ".", exist_ok=True)
    with open(STATE_PATH, "w") as fh:
        json.dump(state, fh, indent=2)
    ledger.save(LEDGER_PATH)
    print(f"wrote {STATE_PATH} with {len(state['highlights'])} highlight(s)")


if __name__ == "__main__":
    main()
