"""Configuration — placeholders. Replace with your real numbers.

Nothing here is advice; the tax rates especially are stand-ins to confirm with
your CPA. Kept as a plain dict so it's trivial to load from JSON/env later.
"""
from datetime import date

CONFIG = {
    "accounts": {
        "prop_primary": "Lucid-01",
        "prop_secondary": "Topstep-01",
        "live": "personal-live",
    },
    "default_size": 2,               # contracts per proposal (placeholder)
    "risk_per_trade": 300.0,         # target $ risk per trade
    "daily_target": 900.0,           # stop trading once realized P&L >= this

    "long_term": {
        # Equal split across these every month.
        "watchlist": ["NVDA", "TSLA", "SMH", "TSM"],
        "monthly_amount": 650.0,     # your $500-$800 monthly contribution
        "buy_day_of_month": 1,
    },

    "obligation_target": 28000.0,    # the debt you're clearing
    "obligation_deadline": date(date.today().year, 12, 31),

    "tax": {
        # Placeholders — confirm with your CPA.
        "long_term_rate": 0.15,      # applied to 60% of 1256 gains
        "short_term_rate": 0.24,     # ordinary bracket; 40% of 1256 + prop 1099
        "state_rate": 0.0495,        # Illinois flat income tax
    },
}
