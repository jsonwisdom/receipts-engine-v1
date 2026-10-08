import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from garbage_investing_gate_v0_1 import check_gi002, eligible_closed_candles


class GIGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads((ROOT / 'fixtures/garbage-investing/GI_002_R002_HOLD_V0_1.json').read_text())

    def test_hold_receipt_valid(self):
        self.assertEqual(check_gi002(self.record), [])

    def test_scope_cannot_include_earlier_coins(self):
        r = deepcopy(self.record); r['asset_scope'] += ['BTC-USD']
        self.assertTrue(check_gi002(r))

    def test_investment_claim_not_promoted_by_fee_result(self):
        r = deepcopy(self.record); r['investment_claim'] = 'SUPPORTED'
        self.assertTrue(check_gi002(r))

    def test_reminder_not_authorization(self):
        r = deepcopy(self.record); r['human_decision_at_utc'] = r['reminder_at_utc']
        self.assertTrue(check_gi002(r))

    def test_wrapper_hash_not_source_hash(self):
        r = deepcopy(self.record); r['sources'][0]['raw_provider_sha256'] = r['sources'][0]['wrapper_sha256_reported']
        self.assertTrue(check_gi002(r))

    def test_no_premark_or_leaderboard(self):
        r = deepcopy(self.record); r['r002']['paper_valuation'] = 'RAN'; r['r002']['leaderboard'] = 'UPDATED'
        self.assertTrue(check_gi002(r))

    def test_keep_only_closed_daily_candles(self):
        candles = [{'start_utc': '2026-10-07T00:00:00Z'}, {'start_utc': '2026-10-08T00:00:00Z'}]
        keep, drop = eligible_closed_candles(candles, self.record['research_cutoff_at_utc'])
        self.assertEqual(len(keep), 1); self.assertEqual(len(drop), 1)
        self.assertEqual(keep[0]['start_utc'], '2026-10-07T00:00:00Z')

    def test_requires_source_classification(self):
        r = deepcopy(self.record); r['sources'][1]['class'] = 'AUTHENTICATED_EXCHANGE_BYTES'
        self.assertTrue(check_gi002(r))


if __name__ == '__main__':
    unittest.main()
