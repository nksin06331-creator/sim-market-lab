"""Apply shared reading UI after report generation, without changing analysis values.

Idempotent: python scripts/apply_report_ui.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLE = '<link rel="stylesheet" href="../../lab/assets/css/report-ui.css">'
BACK = '<nav class="report-backbar" aria-label="サイトナビゲーション"><div class="wrap"><a href="../../index.html">← 銘柄一覧へ戻る</a></div></nav>'


def apply(html):
    if STYLE not in html:
        html = html.replace('</head>', STYLE + '\n</head>', 1)
    if 'class="report-backbar"' not in html:
        html = re.sub(r'(<body\b[^>]*>)', lambda m: m[0] + '\n' + BACK, html, count=1)
    if 'class="score-detail"' not in html:
        html = re.sub(r'(<div class="score">.*?</div>)', r'<details class="score-detail"><summary>シナリオの参考スコア（総合判定とは別）</summary>\1</details>', html, count=1, flags=re.S)
    if 'class="analysis-basis"' not in html and 'data-live-price' in html:
        price = re.search(r'<b data-live-price[^>]*>(.*?)</b>', html, re.S)
        date = re.search(r'<small data-live-price-date[^>]*>(.*?)</small>', html, re.S)
        if price and date:
            note = ('<div class="analysis-basis"><p><strong>計算に使った基準株価：' + price[1] + '</strong> ／ ' + date[1] + '</p><p>シナリオ・騰落率・参考スコアはこの基準で固定。現在株価の更新では再計算しません。</p></div>')
            # Place it before the KPIs, alongside the current quote and scenario prices.
            html = html.replace('<div class="kpis">', note + '\n<div class="kpis">', 1)
    return html


if __name__ == '__main__':
    count = 0
    for stock in json.loads((ROOT / 'data/stocks.json').read_text())['stocks']:
        for report in stock['reports'].values():
            path = ROOT / report['path']
            if report['available'] and path.is_file():
                original = path.read_text()
                updated = apply(original)
                if updated != original:
                    path.write_text(updated)
                    count += 1
    print(f'Updated {count} reports')
