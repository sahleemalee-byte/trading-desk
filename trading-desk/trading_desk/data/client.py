"""Twelve Data client. Reads your key from the environment — never hardcoded.

Set TWELVEDATA_API_KEY in a .env file (local) or a repo secret (GitHub Actions).
Uses only the Python standard library, so there's nothing to pip-install.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.twelvedata.com"


class NoAPIKey(Exception):
    """No TWELVEDATA_API_KEY was found in the environment."""


class TwelveDataError(Exception):
    """The API returned an error, or the request failed after retries."""


class TwelveDataClient:
    def __init__(self, api_key: str | None = None, timeout: int = 10, retries: int = 3) -> None:
        self.api_key = api_key or os.environ.get("TWELVEDATA_API_KEY")
        self.timeout = timeout
        self.retries = retries

    @property
    def has_key(self) -> bool:
        return bool(self.api_key)

    def _get(self, endpoint: str, **params) -> dict:
        if not self.api_key:
            raise NoAPIKey("Set TWELVEDATA_API_KEY in your .env or repo secrets.")
        params["apikey"] = self.api_key
        url = f"{BASE}/{endpoint}?{urllib.parse.urlencode(params)}"

        last_err = None
        for _ in range(self.retries):
            try:
                with urllib.request.urlopen(url, timeout=self.timeout) as resp:
                    data = json.loads(resp.read().decode())
                if isinstance(data, dict) and data.get("status") == "error":
                    raise TwelveDataError(data.get("message", "unknown API error"))
                return data
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
                last_err = e
        raise TwelveDataError(f"request failed after {self.retries} tries: {last_err}")

    # --- thin wrappers over the endpoints we use --------------------------
    def quote(self, symbol: str) -> dict:
        return self._get("quote", symbol=symbol)

    def price(self, symbol: str) -> dict:
        return self._get("price", symbol=symbol)

    def time_series(self, symbol: str, interval: str = "1day", outputsize: int = 30) -> dict:
        return self._get("time_series", symbol=symbol, interval=interval, outputsize=outputsize)
