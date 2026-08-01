# trading_desk

A multi-agent scaffold for a futures + investing workflow. Four top-level
agents, a ledger bridge, and an orchestrator with a human execution gate.
Everything is stubbed and **runs today** with placeholder data — you fill in the
real logic agent by agent.

## Run it

```bash
python -m trading_desk.run
```

One full cycle prints: the Trade agent's combined read, a surfaced setup, the
monthly long-term buy plan, the approval gate, the fill hitting the ledger, and
the debt/tax departments reading the result.

## The four agents

1. **Trade agent** — your whole trading brain. Runs five sub-agents and combines
   them into one read, then gates setups (Mon–Thu, daily stop, no MIXED days).
2. **Long-term agent** — splits your monthly contribution **equally** across your
   watchlist (NVDA, TSLA, SMH, TSM).
3. **Debt department** — counts down the $28,000, paced against market income.
4. **Tax department** — reserves for federal (1256 60/40 + prop 1099) **and
   Illinois** state.

## Structure

```
trading_desk/
  context.py        shared data objects (Verdict, TradeProposal, Fill, Cycle)
  ledger.py         records fills + payouts, computes R-multiples  <- the bridge
  config.py         your targets, watchlist, accounts, tax rates
  orchestrator.py   runs the pipeline in order + holds the execution gate
  run.py            demo cycle
  agents/
    base.py         Agent + SubAgent contracts
    trade/
      agent.py          Trade agent (umbrella)
      sentiment.py      sub: ETF-proxy risk read
      gamma.py          sub: dealer positioning
      news.py           sub: headlines & events
      trade_analysis.py sub: your setups (IB breakout / 20 EMA / 15m FVG)
      pnl_growth.py     sub: daily-stop tracking
    long_term.py    monthly equal-split buy plan
    debt.py         obligation payoff tracker
    tax.py          federal + IL reserve estimator
```

## The one rule baked in: agents advise, you execute

Trading agents return `TradeProposal`s. Nothing places an order or moves money.
`Orchestrator.execution_gate` takes a `confirm(proposal) -> bool` callback — your
prompt, UI click, or Slack reaction. Wire a broker only on your side of it. The
debt and tax departments are decision-support; the tax numbers are rough reserve
estimates for your CPA, not advice or a filing.

## Where to fill in (search for `TODO`)

| Piece | Replace the stub with |
|---|---|
| `trade/sentiment.fetch_signals` | your live dashboard output (Twelve Data / ETF proxies) |
| `trade/gamma.read` | your dealer-gamma read (positioning, flip level) |
| `trade/news.read` | headlines + economic calendar (LLM pass optional) |
| `trade/trade_analysis.read` | your R.R. 4H->30m->5m read + triggers |
| `long_term.scan_watchlist` | your "what's worth adding" scan (money still splits equally) |
| `debt` / `tax` | confirm targets + real brackets in `config.py` |

## Next steps you might reach for

- Persist the ledger (SQLite) so debt/tax survive between runs.
- Add per-account consistency-rule checks (Lucid vs Topstep) in trade_analysis.
- Score the news sub-agent so it contributes a number, not just a note.
- Add a copier adapter behind the execution gate (still human-approved).
