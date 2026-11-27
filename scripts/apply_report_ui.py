"""Apply shared reading UI after report generation, without changing analysis values.

Idempotent: python scripts/apply_report_ui.py
"""
import json
from html.parser import HTMLParser
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLE = '<link rel="stylesheet" href="../../lab/assets/css/report-ui.css">'
BACK = '<nav class="report-backbar" aria-label="サイトナビゲーション"><div class="wrap"><a href="../../index.html">← 銘柄一覧へ戻る</a></div></nav>'


class LayoutNormalizer(HTMLParser):
    """Remove redundant layout wrappers and invalid block-in-paragraph markup.

    Keep original source text, attributes and comments using source offsets.
    """
    BLOCKS = {"p", "div", "ul", "ol", "table", "details", "section", "h2", "h3"}
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.offsets = [0]
        for line in source.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.stack = []
        self.removals = []

    def source_offset(self):
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            return
        classes = set(dict(attrs).get("class", "").split())
        parent = self.stack[-1] if self.stack else None
        redundant = parent and (("facts" in parent["classes"] and "info-row" in classes) or
                                ("card-grid" in parent["classes"] and "card-grid" in classes))
        if tag in self.BLOCKS:
            for node in self.stack:
                if node["tag"] == "p":
                    node["remove"] = True
        start = self.source_offset()
        self.stack.append(dict(tag=tag, classes=classes, start=start,
                               end=start + len(self.get_starttag_text()), remove=bool(redundant)))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] == tag:
                node = self.stack[index]
                if node["remove"]:
                    self.removals.extend([(node["start"], node["end"]),
                                          (self.source_offset(), self.source_offset() + len(tag) + 3)])
                self.stack = self.stack[:index]
                break

    def normalized(self):
        self.feed(self.source)
        result = self.source
        for start, end in sorted(set(self.removals), reverse=True):
            result = result[:start] + result[end:]
        return result


def normalize_layout(html):
    html = LayoutNormalizer(html).normalized()
    html = html.replace("ドパガキ株価シナリオ", "株価シナリオ")
    html = html.replace('<div class="table-wrap">', '<div class="table-wrap" tabindex="0" role="region" aria-label="横にスクロールできる表">')
    kind = "company" if 'class="tldr-hero"' in html else (
        "catalysts" if 'class="priced-score"' in html else "valuation")
    if 'data-report-kind=' not in html:
        html = re.sub(r'<body\b', '<body data-report-kind="' + kind + '"', html, count=1)
    if kind == "company":
        html = re.sub(r'<h1>(.*?)を<br><span class="g">まるっと</span>解説</h1>',
                      r'<h1>\1<span class="report-title-kind">企業概要</span></h1>', html, count=1)
    return html


def apply(html):
    html = normalize_layout(html)
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
