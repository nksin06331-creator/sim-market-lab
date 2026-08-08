"""Generate ASP Isotopes report HTML files and site data."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stocks" / "asp-isotopes-aspi"

DATE = "2026-08-09"
STOCK_ID = "asp-isotopes-aspi"
TICKER = "ASPI"
COMPANY = "ASPアイソトープス"
P0 = 3.775
PREVIOUS_CLOSE = 4.05
SHARES_M = 153.3
BEAR = 2.50
BASE = 6.00
BULL = 10.00
VALUATION = round((P0 - BEAR) / (BULL - BEAR) * 100, 1)
CATALYSTS = 72.0
BUSINESS_RISK = 82.0
POSITION = round(VALUATION * 0.60 + CATALYSTS * 0.25 + BUSINESS_RISK * 0.15, 1)

SOURCES = {
    "company": "https://ir.aspisotopes.com/company-information",
    "financials": "https://ir.aspisotopes.com/financial-information/financial-results",
    "q1": "https://www.sec.gov/Archives/edgar/data/1921865/000119312526232658/aspi-20260331.htm",
    "news": "https://ir.aspisotopes.com/news-events",
    "renergen": "https://ir.aspisotopes.com/news-events/press-releases/detail/116/asp-isotopes-inc-announces-that-renergen-limiteds",
    "presentation": "https://ir.aspisotopes.com/news-events/presentations",
    "price": "https://stockanalysis.com/stocks/aspi/history/",
}


def usd(value: float) -> str:
    return f"${value:,.2f}" if value < 100 else f"${value:,.0f}"


def link(label: str, key: str) -> str:
    return f'<a href="{SOURCES[key]}" target="_blank" rel="noopener noreferrer">{label}</a>'


def page(title: str, badge: str, lead: str, sections: list[tuple[str, str]], footer_note: str) -> str:
    body = "\n".join(f"<section><h2>{heading}</h2>{content}</section>" for heading, content in sections)
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{COMPANY}（{TICKER}）のSiM MARKET LABレポート">
<title>{title}</title>
<style>
:root {{ color-scheme: dark; --bg:#050806; --panel:#101711; --line:#28402c; --text:#f3f7f0; --muted:#aeb8ac; --green:#68e35f; --yellow:#ffd24f; --red:#ff7890; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:linear-gradient(180deg,#071008,#020402); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; line-height:1.75; }}
a {{ color:var(--green); }}
.wrap {{ width:min(1040px, calc(100% - 32px)); margin:0 auto; }}
header {{ padding:42px 0 24px; border-bottom:1px solid var(--line); }}
.badge {{ color:var(--green); font-weight:800; letter-spacing:.08em; font-size:13px; }}
h1 {{ font-size:clamp(34px,7vw,72px); line-height:1.05; margin:10px 0 14px; letter-spacing:0; }}
.lead {{ color:var(--muted); font-size:18px; max-width:780px; }}
.grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:24px 0 0; }}
.stat,.card,section {{ background:rgba(16,23,17,.9); border:1px solid var(--line); border-radius:8px; }}
.stat {{ padding:16px; }}
.stat b {{ display:block; color:var(--green); font-size:24px; }}
.stat span {{ color:var(--muted); font-size:13px; }}
main {{ padding:26px 0 48px; }}
section {{ margin:16px 0; padding:22px; }}
h2 {{ margin:0 0 10px; font-size:24px; }}
h3 {{ margin:18px 0 8px; color:var(--green); }}
ul {{ padding-left:1.2em; }}
table {{ width:100%; border-collapse:collapse; margin:12px 0; }}
th,td {{ border-bottom:1px solid var(--line); padding:10px; text-align:left; vertical-align:top; }}
th {{ color:var(--muted); }}
.cards {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }}
.card {{ padding:16px; }}
.pricebar {{ height:14px; background:linear-gradient(90deg,#9d2f46,#68e35f,#7bdcff); border-radius:999px; position:relative; margin:28px 0 8px; }}
.pin {{ position:absolute; top:50%; left:{VALUATION}%; width:18px; height:18px; border-radius:50%; background:var(--green); border:3px solid #071008; transform:translate(-50%,-50%); }}
.labels {{ display:flex; justify-content:space-between; color:var(--muted); font-size:13px; }}
.notice {{ border-left:4px solid var(--yellow); padding:10px 14px; background:#18160b; }}
footer {{ border-top:1px solid var(--line); color:var(--muted); padding:24px 0 36px; }}
@media (max-width:760px) {{ .grid,.cards {{ grid-template-columns:1fr; }} section {{ padding:18px; }} }}
</style>
</head>
<body data-stock-ticker="{TICKER}" data-price-source="../../data/prices.json">
<header><div class="wrap">
<div class="badge">{badge}</div>
<h1>{COMPANY}<br><span style="color:var(--green)">{TICKER}</span></h1>
<p class="lead">{lead}</p>
<div class="grid">
<div class="stat"><b>{usd(P0)}</b><span>評価基準株価</span></div>
<div class="stat"><b>${P0 * SHARES_M / 1000:.1f}B</b><span>時価総額の目安</span></div>
<div class="stat"><b>$290.5M</b><span>現金+短期投資</span></div>
<div class="stat"><b>Q3 2026</b><span>商業出荷・Renergen確認</span></div>
</div>
</div></header>
<main class="wrap">
<p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p>
{body}
</main>
<footer><div class="wrap">{footer_note}｜作成日 {DATE}</div></footer>
</body>
</html>
"""


def company_report() -> str:
    sections = [
        ("3秒まとめ", "<ul><li>ASPIは医療、半導体、核エネルギー向けの同位体濃縮技術を開発する先端材料企業です。</li><li>Q1 2026時点でC-14、Si-28、Yb-176の商業出荷が焦点です。</li><li>Renergen買収でヘリウム/LNG資産も加わり、材料は増えましたが実行リスクも高いです。</li></ul>"),
        ("事業の全体像", "<div class='cards'><div class='card'><h3>同位体</h3><p>C-14、Si-28、Yb-176などを医療、半導体、量子コンピューティング向けに供給する構想です。</p></div><div class='card'><h3>Quantum Leap Energy</h3><p>U-235、Li-6/7など核燃料・次世代原子力向けの濃縮技術を狙います。</p></div><div class='card'><h3>Renergen</h3><p>南アフリカのVirginia Gas ProjectでLNGと液体ヘリウムの商業化を目指します。</p></div></div>"),
        ("公式資料で確認したポイント", f"<ul><li>Q1 2026 10-Qでは、2026年3月31日時点で濃縮同位体販売による売上はまだ未計上と説明されています。</li><li>C-14は2026年Q3、Si-28は2026年半ば、Yb-176は2026年Q3の初期商業出荷が目標です。</li><li>2026年8月6日のRenergenニュースでは、Phase 1のLNG数量の約75%をtake-or-pay契約で支える状態と説明されています。</li></ul><p>出典：{link('会社情報', 'company')}、{link('Q1 2026 10-Q', 'q1')}、{link('Renergen契約ニュース', 'renergen')}</p>"),
        ("初心者向けに見る場所", "<table><thead><tr><th>確認点</th><th>意味</th></tr></thead><tbody><tr><td>初期商業出荷</td><td>技術が売上に変わる最初の関門です。</td></tr><tr><td>Renergen Phase 1</td><td>LNGとヘリウムのキャッシュフロー化が焦点です。</td></tr><tr><td>資金と希薄化</td><td>開発型企業なので、追加資金調達の条件が重要です。</td></tr><tr><td>規制</td><td>U-235/HALEU関連は許認可が最大級のリスクです。</td></tr></tbody></table>"),
    ]
    return page(f"{COMPANY}（{TICKER}）｜企業を知る", "企業を知る", "同位体濃縮、核燃料、ヘリウム/LNGという複数テーマを持つ、実行確認型の高リスク材料株です。", sections, f"SiM MARKET LAB｜{COMPANY}企業レポート")


def valuation_report() -> str:
    expected = BEAR * 0.35 + BASE * 0.40 + BULL * 0.25
    sections = [
        ("結論", f"<p>評価基準株価は悲観〜楽観レンジの <b>{VALUATION}%</b> 地点です。現在株価はかなり悲観寄りですが、商業出荷・Renergen・核燃料テーマが同時に進む場合は上値余地も残ります。</p><div class='notice'>ただし、ASPIはまだ実行確認前の要素が多い銘柄です。成功時の上値より、失敗時の希薄化・遅延・規制リスクを先に確認します。</div>"),
        ("現在株価の位置", f"<div class='pricebar'><i class='pin'></i></div><div class='labels'><span>Bear {usd(BEAR)}</span><span>Base {usd(BASE)}</span><span>Bull {usd(BULL)}</span></div><p>メインサイトと同じ位置表示は {VALUATION}% です。</p>"),
        ("3シナリオ", f"<table><thead><tr><th>ケース</th><th>株価</th><th>確率</th><th>前提</th></tr></thead><tbody><tr><td>悲観</td><td>{usd(BEAR)}</td><td>35%</td><td>商業出荷遅延、Renergen進捗遅れ、追加調達懸念。</td></tr><tr><td>標準</td><td>{usd(BASE)}</td><td>40%</td><td>C-14/Si-28/Yb-176の初期出荷とRenergen Phase 1が段階進行。</td></tr><tr><td>楽観</td><td>{usd(BULL)}</td><td>25%</td><td>同位体出荷、LNG/ヘリウム、QLE/HALEUテーマがそろって評価。</td></tr></tbody></table><p>確率加重の目安は <b>{usd(expected)}</b>、現在株価比で <b>{(expected / P0 - 1) * 100:+.1f}%</b> です。</p>"),
        ("なぜPERでは見ないか", "<p>Q1 2026の売上は$4.18M、継続事業の営業損失は$24.9Mで、通常の利益倍率では評価しにくい段階です。今回は商業化イベントごとのシナリオ法で見ます。</p>"),
        ("前提と出典", f"<ul><li>評価株価：2026年7月28日終値$3.775を採用。</li><li>Q1 2026：現金$207.3M、短期投資$83.2M、発行済株式約125.9Mを確認。</li><li>Renergen：2026年8月6日リリースでPhase 1契約進捗を確認。</li></ul><p>出典：{link('Q1 2026 10-Q', 'q1')}、{link('株価時系列', 'price')}、{link('Renergen契約ニュース', 'renergen')}</p>"),
    ]
    return page(f"{COMPANY}（{TICKER}）｜株価を考える", "株価を考える", "売上倍率やPERではなく、商業出荷、Renergen、核燃料テーマの成功確率で見るシナリオ型レポートです。", sections, f"SiM MARKET LAB｜{COMPANY}株価シナリオ")


def catalyst_report() -> str:
    sections = [
        ("重要材料まとめ", "<ul><li>2026年Q3：C-14とYb-176の初期商業出荷目標。</li><li>2026年半ば以降：Si-28の初期商業出荷確認。</li><li>2026年Q3：Renergen Phase 1のLNG/ヘリウム契約・商業生産確認。</li><li>中期：QLEのU-235/HALEU関連、規制、TerraPower関連の進展。</li></ul>"),
        ("カタリスト別の見方", "<table><thead><tr><th>材料</th><th>期待以上</th><th>期待外れ</th></tr></thead><tbody><tr><td>同位体出荷</td><td>実売上と顧客継続が見え、標準ケースへ近づく。</td><td>遅延なら技術・顧客・資金への疑念が強まる。</td></tr><tr><td>Renergen</td><td>LNG/ヘリウムの契約と生産が進み、キャッシュフロー材料になる。</td><td>建設、資金、契約、規制で遅れると重荷になる。</td></tr><tr><td>QLE/HALEU</td><td>許認可・資金・顧客が進めば大きなテーマ化。</td><td>規制が重く、未実証のままなら評価は剥落。</td></tr></tbody></table>"),
        ("織り込み具合", f"<p>現在株価の位置は悲観〜楽観レンジの <b>{VALUATION}%</b> です。市場は大型テーマを一部見つつも、実行遅延と希薄化リスクをかなり織り込んでいる状態と見ます。</p>"),
        ("直近ニュース", f"<p>2026年8月6日、Renergen子会社Tetra4がVirginia Gas ProjectのLNGについて5年take-or-pay契約を締結したと発表されました。会社はPhase 1のLNG想定量の約75%がtake-or-pay契約で支えられると説明しています。</p><p>出典：{link('Renergen契約ニュース', 'renergen')}</p>"),
        ("公開後に更新すべき点", f"<ul><li>Q2 2026決算が出たら、現金、短期投資、負債、発行済株式を更新。</li><li>商業出荷が確認されたら、レポート2の標準ケースを再計算。</li><li>Renergen Phase 1の契約率と年間売上見通しを更新。</li></ul><p>出典：{link('ニュース一覧', 'news')}、{link('決算資料', 'financials')}、{link('会社プレゼン', 'presentation')}</p>"),
    ]
    return page(f"{COMPANY}（{TICKER}）｜カタリスト", "カタリスト", "ASPIはニュースで動きやすい銘柄です。特に初期商業出荷、Renergen、QLE/HALEUの3本を分けて確認します。", sections, f"SiM MARKET LAB｜{COMPANY}カタリスト")


def write_reports() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "company.html").write_text(company_report(), encoding="utf-8")
    (OUT_DIR / "valuation.html").write_text(valuation_report(), encoding="utf-8")
    (OUT_DIR / "catalysts.html").write_text(catalyst_report(), encoding="utf-8")


def upsert_data() -> None:
    stocks_path = ROOT / "data" / "stocks.json"
    stocks = json.loads(stocks_path.read_text(encoding="utf-8"))
    stocks["stocks"] = [item for item in stocks["stocks"] if item["id"] != STOCK_ID]
    stocks["stocks"].append({
        "id": STOCK_ID,
        "order": 7,
        "ticker": TICKER,
        "quoteSymbol": TICKER,
        "name": COMPANY,
        "nameEn": "ASP Isotopes Inc.",
        "market": "US",
        "marketLabel": "米国株",
        "exchange": "Nasdaq",
        "currency": "USD",
        "sector": "同位体濃縮・先端材料・核燃料",
        "reports": {
            "company": {"path": f"./stocks/{STOCK_ID}/company.html", "available": True},
            "valuation": {"path": f"./stocks/{STOCK_ID}/valuation.html", "available": True},
            "catalysts": {"path": f"./stocks/{STOCK_ID}/catalysts.html", "available": True},
        },
    })
    stocks_path.write_text(json.dumps(stocks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    prices_path = ROOT / "data" / "prices.json"
    prices = json.loads(prices_path.read_text(encoding="utf-8"))
    prices.setdefault("prices", {})[STOCK_ID] = {
        "symbol": TICKER,
        "price": P0,
        "previousClose": PREVIOUS_CLOSE,
        "change": round(P0 - PREVIOUS_CLOSE, 3),
        "changePct": round((P0 - PREVIOUS_CLOSE) / PREVIOUS_CLOSE * 100, 4),
        "currency": "USD",
        "marketTime": "2026-07-28T20:00:00+00:00",
        "updatedAt": "2026-08-09T00:00:00+00:00",
        "status": "ok",
    }
    prices["quoteCount"] = len(prices["prices"])
    prices_path.write_text(json.dumps(prices, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    signals_path = ROOT / "data" / "signals.json"
    signals = json.loads(signals_path.read_text(encoding="utf-8"))
    signals["updatedAt"] = datetime.now(timezone.utc).isoformat()
    signals.setdefault("signals", {})[STOCK_ID] = {
        "position": POSITION,
        "zone": "中立",
        "asOf": DATE,
        "components": {
            "valuation": VALUATION,
            "catalysts": CATALYSTS,
            "businessRisk": BUSINESS_RISK,
        },
        "reportRevision": "asp-isotopes-aspi-2026-08-09",
        "summary": "同位体出荷、Renergen、QLE/HALEUが材料。株価は悲観寄りだが、商業化と規制の実行リスクが高いため中立。",
    }
    signals_path.write_text(json.dumps(signals, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_reports()
    upsert_data()


if __name__ == "__main__":
    main()
