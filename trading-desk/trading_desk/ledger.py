"""The ledger — the bridge between the trading side and the accounting side.

The debt and tax departments never watch trades; they read realized results
from here. Each fill snapshots the macro verdict at entry (so you can grade
setups by regime later) and computes its R-multiple.
"""
from __future__ import annotations

import json
import os
from datetime import date, datetime
from statistics import mean

from .context import Fill, Verdict


def _fill_to_dict(f: Fill) -> dict:
    return {
        "instrument": f.instrument, "direction": f.direction,
        "entry": f.entry, "exit": f.exit, "stop": f.stop, "size": f.size,
        "account": f.account, "point_value": f.point_value,
        "opened": f.opened.isoformat(),
        "closed": f.closed.isoformat() if f.closed else None,
        "macro_at_entry": f.macro_at_entry.value if f.macro_at_entry else None,
    }


def _fill_from_dict(d: dict) -> Fill:
    return Fill(
        instrument=d["instrument"], direction=d["direction"],
        entry=d["entry"], exit=d["exit"], stop=d["stop"], size=d["size"],
        account=d["account"], point_value=d.get("point_value", 20.0),
        opened=datetime.fromisoformat(d["opened"]),
        closed=datetime.fromisoformat(d["closed"]) if d["closed"] else None,
        macro_at_entry=Verdict(d["macro_at_entry"]) if d["macro_at_entry"] else None,
    )


class Ledger:
    def __init__(self) -> None:
        self.fills: list[Fill] = []
        self.payouts: list[tuple[date, str, float]] = []   # (when, account, amount)

    # --- writes -----------------------------------------------------------
    def record_fill(self, fill: Fill) -> None:
        self.fills.append(fill)

    def record_payout(self, account: str, amount: float, when: date | None = None) -> None:
        self.payouts.append((when or date.today(), account, amount))

    # --- reads (what the accounting agents consume) -----------------------
    def closed_fills(self) -> list[Fill]:
        return [f for f in self.fills if f.closed]

    def realized_pnl(self) -> float:
        return round(sum(f.pnl for f in self.closed_fills()), 2)

    def payouts_total(self) -> float:
        return round(sum(a for _, _, a in self.payouts), 2)

    def r_stats(self) -> dict:
        rs = [f.r_multiple for f in self.closed_fills() if f.r_multiple is not None]
        if not rs:
            return {"count": 0}
        wins = [r for r in rs if r > 0]
        return {
            "count": len(rs),
            "avg_r": round(mean(rs), 2),
            "win_rate": round(len(wins) / len(rs), 2),
            "expectancy_r": round(mean(rs), 2),
        }

    # --- persistence (so the cloud timer doesn't forget between runs) -----
    def save(self, path: str = "ledger.json") -> None:
        data = {
            "fills": [_fill_to_dict(f) for f in self.fills],
            "payouts": [[w.isoformat(), acct, amt] for w, acct, amt in self.payouts],
        }
        with open(path, "w") as fh:
            json.dump(data, fh, indent=2)

    @classmethod
    def load(cls, path: str = "ledger.json") -> "Ledger":
        led = cls()
        if not os.path.exists(path):
            return led
        with open(path) as fh:
            data = json.load(fh)
        led.fills = [_fill_from_dict(x) for x in data.get("fills", [])]
        led.payouts = [(date.fromisoformat(w), a, amt) for w, a, amt in data.get("payouts", [])]
        return led
