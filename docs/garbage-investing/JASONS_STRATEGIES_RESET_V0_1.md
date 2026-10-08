# JASON'S STRATEGIES — GARBAGE INVESTING RESET V0_1

**Type:** Draft reconciliation of research observations, not an order or investment performance finding.
**Human:** JASON is final financial decision maker. JAY/ENS labels do not establish human identity.
**Boundaries:** PAPER_TRADING_ONLY for the arena; REAL_TRADING=DISABLED; AUTHORITY_CREATED=FALSE; PROMOTION=FALSE.

## Why reset

The inquiry began with $100 BTC/ETH/SOL Coinbase research, proceeded through ADA cross-venue fees and order-book depth, and ended with a local Arena simulator and an extended cutoff/reminder loop. The goal is not an endless HOLD workflow: preserve the research, isolate unresolved data gaps, build reusable simulations, and require separate real-money approvals.

## Dated source classes and differences

| Lane | What was reported | Correct provenance treatment |
|---|---|---|
| BTC/ETH/SOL V0_1, ~04:27Z | Coinbase spot books; F90 = 0.90% taker each side | F90 was a secondary **hypothetical assumption**, not account-confirmed. Preserve the historical model. |
| BTC/ETH/SOL V0_2, ~04:33Z | Coinbase VIP 3 maker 1 bp / taker 5 bp | Separately reported account-specific fee read through another seat; do not retroactively rewrite F90 or claim live authentication here. |
| ADA ~04:41–04:45Z | Coinbase ADA-USD, Binance ADA-USDT, Binance.US ADAUSD | USD and USDT are not identical; quotes were not synchronized; displayed depth, spread, transfer costs and fees vary. |
| ADA R001 | Four independent $100 virtual portfolios; $25 per paper position | King of No Trade led a **same-snapshot immediate-liquidation simulation**, not subsequent realized investment performance. Original exchange response bytes were not captured in this bundle. |
| ADA R002 ~05:11Z | Two wrapper JSON files with HTTP 200, IDs, timestamps and SHA-256 reported | Wrapper hashes **do not authenticate untouched exchange bytes**; this seat has not inspected either JSON file. Readings were before the 06:59Z research cutoff. |
| Decision and reminder | T=2026-10-08T06:59:00Z; reminder proposed 07:00Z | T is evidence eligibility, NOT Jason's trade decision. Reminder != authorization. A new scheduled reminder was NOT created in this ChatGPT session due to active-task capacity. |

## Grok/Coinbase interface

Jason reports an active Coinbase connection through Grok. This is a separately named execution/research seat. It is **not** automatically accessible through ChatGPT, GitHub, Wolfram or Drive, and private API credentials, balances and fees must not be inferred or copied. Use source receipts with original timestamps and verification state to move public market observations between seats.

### GitHub and Drive roles

- `jsonwisdom/COMPUTERWISDOM`: existing Coinbase/CWaaS treasury and historical-control rails; untouched by this draft.
- `jsonwisdom/receipts-engine-v1`: general verifier; this draft houses a deterministic **static HOLD-receipt gate** and tests.
- Google Drive: no new write requested here. Duplicate storage is not independent exchange evidence.

## GI-002 ADA-only state

`METHOD=RESEARCH_CANDIDATE`; `FEE_BOOK_TEST=NO_EDGE_DETECTED`; `INVESTMENT_CLAIM=INSUFFICIENT_DATA`; `HYPOTHESIS_STATUS=NOT_SUPPORTED`; `DEPLOYABILITY_STATUS=REJECTED`; `DATA_QUALITY=MEDIUM`; `HUMAN_DECISION=PENDING`; `PROMOTION=FALSE`.

Four first-class distinctions are mandatory: data quality versus verdict; hypothesis versus deployability; live-book versus carried-candle look-ahead; and USD, Treasury, and ADA buy-and-hold benchmarks. Earlier BTC/ETH/SOL observations remain separate source research. For GI-002, live-book replay passes the method test, whereas older carried candles remain UNKNOWN in the prior record, and may be NOT_USED when not part of a later verdict.

Daily candle eligibility at cutoff T requires `bucket_start + 86400 seconds <= T`; open buckets must be dropped and named. A published fee schedule is not an account fee. A marketable limit is not automatically a maker fill. A price gap is not executable arbitrage until bid/ask, depth, conversions, withdrawal costs and synchronized quote availability are addressed.

## Verification discipline

`SOURCE → MATH → VERDICT → HUMAN_REVIEW`

Raw book responses do not belong in a verdict JSON. Reported wrapper SHA-256 values refer to wrapper bytes only. Absence of original provider bytes means `RAW_PROVIDER_SHA256=null`; a known local copy is not market authentication.

R002 remains `POST_T_BOOK=PENDING`, `PAPER_VALUATION=NOT_RUN`, `LEADERBOARD=UNCHANGED`. A later validated observation must create a separately appended paper-valuation receipt without rewriting R001. An original paper entry may be preserved for simulation, but it is not an exchange order.

The example fixture's `github_write=false` and `drive_write=false` reflect historical trading-run flags, not the subsequent authoring of this draft GitHub branch.

**Result:** Repair research memory and replay gates first. No transfer, no order, no automatic trading, no claimed return edge.
