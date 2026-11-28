"""A catalogue registration alone must not pass the production publication gate."""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_site import Validation,validate_stocks


class PublicationCompletenessTests(unittest.TestCase):
    def test_finished_report_set_can_be_published(self):
        stock=json.loads((ROOT/'data/stocks.json').read_text())['stocks'][0]
        validation=Validation();validate_stocks({'stocks':[stock]},validation)
        self.assertEqual(validation.errors,[])

    def test_one_or_all_pending_reports_block_publication(self):
        stock=json.loads((ROOT/'data/stocks.json').read_text())['stocks'][0]
        for keys in [('company',),('company','valuation','catalysts')]:
            with self.subTest(keys=keys):
                draft=copy.deepcopy(stock)
                for key in keys:draft['reports'][key]['available']=False
                validation=Validation();validate_stocks({'stocks':[draft]},validation)
                self.assertTrue(any('3レポート完成' in e for e in validation.errors))


if __name__=='__main__':unittest.main()
