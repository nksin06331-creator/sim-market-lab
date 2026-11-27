"""Regression checks for errors that the old site-only validator missed."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from validate_report_bundles import check_bundle


class ReportValidationTests(unittest.TestCase):
    def setUp(self):
        self.bundle = json.loads((ROOT/'data/reports/coreweave-crwv.json').read_text())
        stocks = json.loads((ROOT/'data/stocks.json').read_text())['stocks']
        self.stock = next(stock for stock in stocks if stock['id'] == 'coreweave-crwv')
        self.signal = {'asOf': self.bundle['meta']['valuation_date'],
                       'reportRevision': self.stock.get('reportRevision')}

    def check(self, bundle=None, signal=None, paths=None):
        return check_bundle(bundle or self.bundle, self.stock,
                            self.signal if signal is None else signal, paths or [])[0]

    def test_current_bundle_has_no_errors(self):
        self.assertEqual(self.check(), [])

    def test_wrong_per_share_value_blocks_publication(self):
        bundle = copy.deepcopy(self.bundle)
        bundle['scenario']['cases'][0]['price'] += 1
        self.assertTrue(any('X07' in error for error in self.check(bundle)))

    def test_nonexistent_source_blocks_publication(self):
        bundle = copy.deepcopy(self.bundle)
        bundle['claims'][0]['source_ids'].append('SOURCE_DOES_NOT_EXIST')
        self.assertTrue(any('X06' in error for error in self.check(bundle)))

    def test_signal_revision_must_match_registered_reports(self):
        self.assertTrue(any('revisions differ' in error for error in self.check(signal={
            'asOf': self.bundle['meta']['valuation_date'], 'reportRevision': 'obsolete'})))

    def test_old_signal_date_cannot_accompany_new_reports(self):
        self.assertTrue(any('analysis date' in error for error in self.check(signal={'asOf':'2000-01-01'})))

    def test_price_cannot_postdate_information_cutoff(self):
        bundle = copy.deepcopy(self.bundle)
        bundle['meta']['price_as_of'] = '2099-01-01T00:00:00Z'
        self.assertTrue(any('timestamp' in error for error in self.check(bundle)))

    def test_unfinished_html_blocks_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'report.html'
            path.write_text('<html><body>{{COMPANY_NAME}}</body></html>')
            self.assertTrue(any('X25' in error for error in self.check(paths=[path])))

    def test_negative_common_equity_endpoint_blocks_publication(self):
        bundle = copy.deepcopy(self.bundle)
        bundle['catalyst_report']['overall_priced_in']['all_events_excluded_equity_value'] = -1
        self.assertTrue(any('negative common-equity' in error for error in self.check(bundle)))

    def test_missing_event_outcome_blocks_publication(self):
        bundle = copy.deepcopy(self.bundle)
        bundle['catalyst_report']['catalysts'][0]['outcomes'].pop()
        self.assertTrue(any('X12' in error for error in self.check(bundle)))


if __name__ == '__main__':
    unittest.main()
