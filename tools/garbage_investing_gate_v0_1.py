"""Research-only receipt gate; never imports a broker SDK or places orders."""
from datetime import datetime, timezone, timedelta


def utc(iso):
    dt = datetime.fromisoformat(iso.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('UTC offset required')
    return dt.astimezone(timezone.utc)


def eligible_closed_candles(buckets, cutoff_utc):
    """Return admitted UTC daily buckets and exclusions, without price interpolation."""
    t = utc(cutoff_utc)
    kept, dropped = [], []
    for b in buckets:
        start = utc(b['start_utc'])
        end = start + timedelta(days=1)
        (kept if end <= t else dropped).append(b)
    return kept, dropped


def check_gi002(record):
    """Static and state-transition checks; a PASS never authenticates exchange bytes."""
    failures = []
    def require(ok, msg):
        if not ok:
            failures.append(msg)
    require(record.get('episode_id') == 'GI-002', 'episode must be GI-002')
    require(record.get('asset_scope') == ['ADA-USD'], 'GI-002 is ADA-only; BTC/ETH/SOL stay separate')
    require(record.get('operating_mode') == 'PAPER_TRADING_ONLY', 'paper mode required')
    require(record.get('real_money_trading') == 'DISABLED', 'real trading must remain disabled')
    require(record.get('authority_created') is False, 'cannot create authority')
    require(record.get('promotion') is False, 'unpromoted draft only')
    require(record.get('human_decision') == 'PENDING', 'human decision remains pending')
    require(record.get('human_decision_at_utc') is None, 'no invented human decision timestamp')
    require(record.get('fee_book_test') == 'NO_EDGE_DETECTED', 'fee/book result must be separate')
    require(record.get('investment_claim') == 'INSUFFICIENT_DATA', 'investment claim not established')
    require(record.get('hypothesis_status') == 'NOT_SUPPORTED', 'no historical return edge shown')
    require(record.get('deployability_status') == 'REJECTED', 'deployability remains rejected')
    require(record.get('data_quality') == 'MEDIUM', 'data quality must be separately recorded')
    require(record.get('source_authentication') == 'NOT_VERIFIED_THIS_SEAT', 'do not self-authenticate sources')
    require(record.get('look_ahead', {}).get('live_book_walks') == 'PASS', 'live-book test separate')
    require(record.get('look_ahead', {}).get('carried_historical_candles') in ('UNKNOWN', 'NOT_USED'),
            'carried-candle check must be explicitly scoped')
    benchmarks = record.get('benchmarks', {})
    require(benchmarks.get('A_USD') == 'NOT_BEATEN', 'USD benchmark not beaten')
    require(benchmarks.get('B_TREASURY') == 'NOT_RUN', 'Treasury benchmark not run')
    require(benchmarks.get('C_BUY_AND_HOLD_ADA') == 'NOT_RUN', 'ADA buy/hold benchmark not run')
    require(record.get('bns') == 'UNRESOLVED_LABEL', 'BNS meaning unresolved')
    require(record.get('ens_role') == 'NAME_REFERENCE_ONLY', 'ENS is not account identity')
    require(record.get('github_write') is False and record.get('drive_write') is False,
            'research receipt does not authorize external writes')
    # The path under review can be committed to GitHub; these are historical session-event flags.
    sources = record.get('sources', [])
    require(len(sources) >= 2, 'record source classification per venue')
    for src in sources:
        require(src.get('class') in ('CONNECTOR_READ_REPORTED', 'PUBLIC_FEED_READ_REPORTED', 'USER_SUMMARY'),
                'unsupported source class')
        require(src.get('raw_provider_bytes_captured') is False, 'no original exchange bytes in this record')
        require(src.get('raw_provider_sha256') is None, 'wrapper hash is not exchange-byte hash')
        require(src.get('verification') == 'REPORTED_NOT_REPLAYED', 'no source authentication by declaration')
    try:
        t = utc(record['research_cutoff_at_utc'])
        r = record.get('reminder_at_utc')
        if r:
            require(utc(r) > t, 'reminder should be after cutoff')
    except (KeyError, TypeError, ValueError) as ex:
        failures.append('invalid cutoff/reminder timestamp: '+str(ex))
    require(record.get('r002', {}).get('post_t_source') == 'PENDING', 'post-T data pending')
    require(record.get('r002', {}).get('paper_valuation') == 'NOT_RUN', 'no paper valuation before verified source')
    require(record.get('r002', {}).get('leaderboard') == 'UNCHANGED', 'do not advance leaderboard')
    return failures
