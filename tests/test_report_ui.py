"""Regression checks for layout corruption introduced by report generation."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from apply_report_ui import apply, normalize_layout


class ReportLayoutTests(unittest.TestCase):
    def test_redundant_grid_does_not_confine_facts_to_one_column(self):
        source = '<body><div class="facts"><div class="info-row"><div class="info-box">売上100</div><div class="info-box">利益20</div></div></div></body>'
        result = normalize_layout(source)
        self.assertIn('<div class="facts"><div class="info-box">売上100</div><div class="info-box">利益20</div></div>', result)
        self.assertNotIn('class="info-row"', result)

    def test_block_details_content_keeps_values_without_invalid_paragraph(self):
        source = '<body><details><summary>根拠</summary><p><p>価格$42.57</p><ul><li>出典S1</li></ul></p></details></body>'
        result = normalize_layout(source)
        self.assertIn('<summary>根拠</summary><p>価格$42.57</p><ul><li>出典S1</li></ul></details>', result)

    def test_valid_paragraph_and_script_and_comments_are_preserved(self):
        content = '<p>利益 <b>100</b> 円</p><!-- <div class="card-grid"> --><script>const s="<p>";</script>'
        self.assertIn(content, normalize_layout('<body>' + content + '</body>'))

    def test_regeneration_is_idempotent_and_tables_are_focusable(self):
        source = '<html><head></head><body><div class="table-wrap"><table><tr><td>100</td></tr></table></div><div class="card-grid"><div class="card-grid"><div>説明</div></div></div></body></html>'
        result = apply(source)
        self.assertEqual(apply(result), result)
        self.assertEqual(result.count('class="card-grid"'), 1)
        self.assertIn('tabindex="0"', result)
        self.assertEqual(result.count('report-ui.css'), 1)


if __name__ == '__main__':
    unittest.main()
