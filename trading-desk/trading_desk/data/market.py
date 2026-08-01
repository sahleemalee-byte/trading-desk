"""Market data department. Agents ask THIS for data — never the API directly.

It fetches your ETF proxies, cleans them, and turns each into a plain
risk-on / neutral / risk-off label. If there's no API key or a fetch fails, it
falls back to placeholder data and flips `stubbed = True`, so the whole system
keeps running (and you can see it's running on stubbed data, not silently wrong).
"""
from __future__ import annotations

from .client import TwelveDataClient, NoAPIKey, TwelveDataError
from .clean import clean_quote, DataQualityError

# proxy symbol, direction (does 'up' mean risk-ON or risk-OFF?), signal name
PROXIES = [
    ("VIXY", "inverse", "vix"),        # VIX up  -> risk-off
    ("SMH", "direct", "smh"),          # semis up -> risk-on
    ("EWY", "direct", "ewy_kospi"),    # KOSPI proxy up -> risk-on (leads semis/NQ)
    ("IEF", "inverse", "ief"),         # bonds bid -> risk-off lean
    ("SHY", "inverse", "shy"),
    ("USD/JPY", "direct", "usdjpy"),   # yen weak -> risk-on
]

NEUTRAL_BAND = 0.15   # a move smaller than +/-0.15% counts as neutral


def _label(percent_change: float | None, direction: str) -> str:
    if percent_change is None or abs(percent_change) < NEUTRAL_BAND:
        return "neutral"
    up = percent_change > 0
    risk_on = up if direction == "direct" else (not up)
    return "risk-on" if risk_on else "risk-off"


class MarketData:
    def __init__(self, client: TwelveDataClient | None = None) -> None:
        self.client = client or TwelveDataClient()
        self.stubbed = False
        self.error: str | None = None

    def get_risk_signals(self) -> dict[str, str]:
        if not self.client.has_key:
            self.stubbed = True
            return self._placeholder()
        try:
            signals = {}
            for symbol, direction, name in PROXIES:
                q = clean_quote(self.client.quote(symbol), symbol)
                signals[name] = _label(q["percent_change"], direction)
            return signals
        except (TwelveDataError, DataQualityError, NoAPIKey) as e:
            # Fail safe: never let a bad fetch crash the run.
            self.stubbed = True
            self.error = str(e)
            return self._placeholder()

    @staticmethod
    def _placeholder() -> dict[str, str]:
        return {
            "vix": "risk-off", "smh": "risk-on", "ewy_kospi": "risk-on",
            "ief": "neutral", "shy": "neutral", "usdjpy": "risk-on",
        }
