"""Generate ASP Isotopes report HTML files from the bundled SiM templates."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from generate_rocket_lab_reports import dl, li, render_template, th, tr


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stocks" / "asp-isotopes-aspi"

COMPANY = "ASPアイソトープス"
TICKER = "ASPI"
DATE = "2026-08-09"
P0 = 4.43
PREVIOUS_CLOSE = 4.10
SHARES_M = 153.3
MARKET_CAP_B = P0 * SHARES_M / 1000
BEAR = 2.50
BASE = 6.00
BULL = 10.00
BAND_POSITION = (P0 - BEAR) / (BULL - BEAR) * 100
SIGNAL_POSITION = round(BAND_POSITION * 0.60 + 72.0 * 0.25 + 82.0 * 0.15, 1)

SOURCES = {
    "company": "https://ir.aspisotopes.com/company-information",
    "financials": "https://ir.aspisotopes.com/financial-information/financial-results",
    "q1": "https://www.sec.gov/Archives/edgar/data/1921865/000119312526232658/aspi-20260331.htm",
    "news": "https://ir.aspisotopes.com/news-events",
    "renergen": "https://ir.aspisotopes.com/news-events/press-releases/detail/116/asp-isotopes-inc-announces-that-renergen-limiteds",
    "presentation": "https://ir.aspisotopes.com/news-events/presentations",
    "price": "https://stockanalysis.com/stocks/aspi/history/",
}


def usd(value: int | float) -> str:
    return f"${value:,.2f}" if abs(value) < 100 else f"${value:,.0f}"


def details(title: str, body: str, open_: bool = False) -> str:
    return f"<details{' open' if open_ else ''}><summary>{title}</summary><p>{body}</p></details>"


def source_link(label: str, key: str) -> str:
    return f'<a href="{SOURCES[key]}" target="_blank" rel="noopener noreferrer">{label}</a>'


def source_details() -> str:
    return (
        '<details class="term-item" open><summary class="term-header"><span class="term-name">主要出典</span><span class="term-arrow">⌄</span></summary>'
        '<div class="term-body"><p>'
        f'{source_link("会社情報", "company")}、'
        f'{source_link("決算資料", "financials")}、'
        f'{source_link("2026年1Q 10-Q", "q1")}、'
        f'{source_link("Renergen契約ニュース", "renergen")}、'
        f'{source_link("会社プレゼン", "presentation")}、'
        f'{source_link("株価時系列", "price")}を確認しました。'
        "本文の数値は2026年8月9日時点で取得できた公開情報に基づきます。"
        '</p><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p></div></details>'
    )


def guide_values() -> dict[str, str]:
    terms = [
        ("同位体", "同じ元素でも中性子数が違う原子です。医療、半導体、量子、原子力などで特定同位体の需要があります。"),
        ("C-14", "炭素14です。医薬品開発や診断・トレーサー用途で使われます。ASPIは2026年Q3の初期商業出荷を目標にしています。"),
        ("Si-28", "シリコン28です。量子コンピューティングや高機能半導体材料のテーマです。"),
        ("Yb-176", "イッテルビウム176です。医療用放射性同位体の原料用途が注目されています。"),
        ("Quantum Leap Energy", "ASPIの核燃料・先進原子力関連子会社です。U-235やLi-6/7などを対象にしています。"),
        ("HALEU", "高アッセイ低濃縮ウランです。次世代原子炉向け燃料として注目されますが、規制・資金・許認可が重い領域です。"),
        ("Renergen", "南アフリカのLNG・液体ヘリウム事業を持つ会社です。ASPIは買収によりVirginia Gas Projectへの関与を強めました。"),
        ("take-or-pay契約", "買い手が一定量を引き取る、または代金を支払う契約です。プロジェクトの売上見通しを支えます。"),
        ("Virginia Gas Project", "Renergen傘下Tetra4が進める南アフリカの天然ガス・ヘリウムプロジェクトです。"),
        ("希薄化", "増資や株式発行で1株あたり価値が薄まることです。開発型企業では重要リスクです。"),
        ("商業出荷", "試験段階ではなく、顧客に製品として出荷し売上化する段階です。ASPIの最重要確認点です。"),
        ("規制リスク", "核燃料・濃縮関連は許認可、輸出管理、安全保障上の制約を受けます。"),
    ]
    return {
        "TICKER": TICKER,
        "COMPANY_NAME": COMPANY,
        "INDUSTRY": "同位体濃縮・先端材料・核燃料",
        "DATE": DATE,
        "TAGLINE": "医療、半導体、量子、原子力向けの濃縮同位体と、Renergen由来のヘリウム/LNG資産を持つ高リスク材料株です。",
        "HERO_TAGS": '<span class="hero-tag">米国株</span><span class="hero-tag">同位体</span><span class="hero-tag">核燃料</span><span class="hero-tag">ヘリウム</span>',
        "HERO_STATS": (
            f'<div class="stat"><div class="stat-value">{usd(P0)}</div><div class="stat-label">評価基準株価</div><div class="stat-note">2026/08/07終値</div></div>'
            f'<div class="stat"><div class="stat-value">${MARKET_CAP_B:.1f}B</div><div class="stat-label">時価総額の目安</div><div class="stat-note">約1.53億株で計算</div></div>'
            '<div class="stat"><div class="stat-value up">$290.5M</div><div class="stat-label">現金+短期投資</div><div class="stat-note">2026年1Q 10-Q</div></div>'
            '<div class="stat"><div class="stat-value">Q3 2026</div><div class="stat-label">重要時期</div><div class="stat-note">商業出荷・Renergen確認</div></div>'
        ),
        "SEC2_LABEL": "事業モデル",
        "SEC3_LABEL": "同位体",
        "SEC4_LABEL": "Renergen",
        "SEC5_LABEL": "競合比較",
        "SEC1_TLDR": li("ASPIは同位体濃縮、核燃料、ヘリウム/LNGの複数テーマを持つ会社です。", "*") + li("Q1 2026時点では濃縮同位体販売の売上はまだ本格化前です。", "*") + li("商業出荷、Renergen Phase 1、QLE/HALEUの進展が株価材料です。", "!"),
        "SEC1_FACTS": (
            "<div><dt>正式社名</dt><dd>ASP Isotopes Inc.</dd></div><div><dt>本社</dt><dd>Washington, D.C.</dd></div>"
            "<div><dt>上場</dt><dd>Nasdaq（ASPI）</dd></div><div><dt>業種</dt><dd>先端材料・同位体</dd></div>"
            "<div><dt>主な領域</dt><dd>C-14、Si-28、Yb-176、U-235、Li-6/7、ヘリウム</dd></div><div><dt>決算期</dt><dd>12月</dd></div>"
        ),
        "SEC1_CARDS": (
            '<div class="card-sm"><span class="card-emoji">⚛️</span><div class="card-title">同位体</div><div class="card-desc">C-14、Si-28、Yb-176などの商業化を狙います。</div></div>'
            '<div class="card-sm"><span class="card-emoji">☢️</span><div class="card-title">核燃料</div><div class="card-desc">QLEでU-235やHALEU関連テーマを狙います。</div></div>'
            '<div class="card-sm"><span class="card-emoji">⛽</span><div class="card-title">Renergen</div><div class="card-desc">LNGと液体ヘリウムのVirginia Gas Projectが焦点です。</div></div>'
            '<div class="card-sm"><span class="card-emoji">⚠️</span><div class="card-title">リスク</div><div class="card-desc">商業化遅延、規制、資金調達、希薄化に注意です。</div></div>'
        ),
        "SEC1_BIZMODEL": (
            '<li><span class="kp-emoji">⚛️</span><span class="kp-text"><b>同位体</b>：医療、半導体、量子向けに高付加価値材料を供給する構想です。</span></li>'
            '<li><span class="kp-emoji">☢️</span><span class="kp-text"><b>QLE</b>：先進原子力・核燃料向けの濃縮技術を狙います。</span></li>'
            '<li><span class="kp-emoji">⛽</span><span class="kp-text"><b>Renergen</b>：LNGと液体ヘリウムの商業化でキャッシュフロー化を狙います。</span></li>'
        ),
        "SEC1_HIGHLIGHT": '<div class="highlight"><h3>ASPIを見る基本ルール</h3><p>テーマは大きいですが、評価の中心は「本当に売上化できるか」です。初期商業出荷、Renergenの契約と生産、QLEの許認可・資金を分けて確認します。</p></div>',
        "SEC2_ICON": "⚛️",
        "SEC2_TITLE": "事業モデルの<span class=\"g\">基本</span>",
        "SEC2_SUB": "テーマ株から商業化確認へ",
        "SEC2_TLDR": li("同位体濃縮は高付加価値ですが、量産・品質・顧客確認が必要です。", "*") + li("Renergen買収でヘリウム/LNG材料が加わりました。", "*") + li("複数テーマがある分、実行遅延と資金調達リスクも大きいです。", "!"),
        "SEC2_CONTENT": (
            '<p class="lead">ASPIは、医療・半導体・量子・原子力向けの同位体濃縮技術を商業化しようとしている企業です。RenergenによりLNGと液体ヘリウムの資産も加わりました。</p>'
            '<div class="sowhat"><p><b>つまり</b>、ASPIは「テーマの大きさ」ではなく「出荷、契約、生産、許認可」が確認されるたびに評価が変わる銘柄です。</p></div>'
            '<div class="term-list">'
            + details("濃縮同位体", "特定同位体の割合を高めた材料です。医療、半導体、量子、原子力で用途があります。", True)
            + details("本格売上前", "Q1 2026 10-Qでは、濃縮同位体販売による売上はまだ本格化前と読める状態です。")
            + details("Renergen", "LNGとヘリウムの実物資産です。契約と生産が見えればテーマ株から一歩進みます。")
            + details("資金管理", "開発・設備・買収を進めるため、現金、短期投資、借入、株式発行を継続確認します。")
            + "</div>"
        ),
        "SEC3_TITLE": "同位体と<span class=\"g\">商業出荷</span>",
        "SEC3_SUB": "最初の売上化が最大の確認点",
        "SEC3_TLDR": li("C-14、Si-28、Yb-176の初期商業出荷が焦点です。", "*") + li("出荷だけでなく、顧客継続、品質、粗利も重要です。", "*") + li("遅延すると、技術・顧客・資金の信頼が下がります。", "!"),
        "SEC3_CONTENT": (
            '<div class="product-grid"><div class="product-box"><div class="product-symbol">C14</div><div class="product-name">C-14</div><div class="product-use">医薬品開発・診断向け。</div></div>'
            '<div class="product-box"><div class="product-symbol">Si28</div><div class="product-name">Si-28</div><div class="product-use">量子・半導体材料。</div></div>'
            '<div class="product-box"><div class="product-symbol">Yb</div><div class="product-name">Yb-176</div><div class="product-use">医療用同位体原料。</div></div></div>'
            '<div class="term-list">'
            + details("C-14", "2026年Q3の初期商業出荷が目標です。売上化できるかが最初の関門です。", True)
            + details("Si-28", "量子コンピューティングや半導体材料として期待があります。初期出荷と顧客確認が必要です。")
            + details("Yb-176", "医療用放射性同位体の供給網に関わる材料です。需要は強い一方、供給品質が重要です。")
            + details("見る数字", "出荷量、販売価格、粗利率、顧客数、再注文、設備稼働率を確認します。")
            + "</div>"
        ),
        "SEC4_TITLE": "Renergenと<span class=\"g\">ヘリウム/LNG</span>",
        "SEC4_SUB": "契約から生産・キャッシュフローへ",
        "SEC4_TLDR": li("RenergenによりLNGと液体ヘリウムの材料が加わりました。", "*") + li("2026年8月6日にLNGのtake-or-pay契約ニュースが出ています。", "*") + li("建設、稼働、資金、契約の実行確認が必要です。", "!"),
        "SEC4_CONTENT": (
            '<ul class="keypoints"><li><span class="kp-emoji">⛽</span><span class="kp-text"><b>LNG</b>：Renergen子会社Tetra4のVirginia Gas Projectで商業生産を狙います。</span></li>'
            '<li><span class="kp-emoji">🎈</span><span class="kp-text"><b>液体ヘリウム</b>：供給制約のある高付加価値ガスとして注目されます。</span></li>'
            '<li><span class="kp-emoji">📄</span><span class="kp-text"><b>take-or-pay</b>：Phase 1のLNG想定量の約75%を支える契約と会社は説明しています。</span></li></ul>'
            '<div class="sowhat"><p><b>つまり</b>、RenergenはASPIの評価を広げる材料ですが、契約が実際の生産と現金収入へつながるかを確認する必要があります。</p></div>'
        ),
        "SEC5_TITLE": "競合と<span class=\"g\">比べる</span>",
        "SEC5_SUB": "同位体・核燃料・ヘリウムの横断企業",
        "SEC5_TLDR": li("比較対象は同位体供給会社、核燃料企業、ヘリウム資源会社です。", "*") + li("ASPIは複数テーマを持つ一方、商業実績はまだ確認途上です。", "*") + li("大きなテーマほど規制・資金・実行リスクも高くなります。", "!"),
        "SEC5_CONTENT": (
            '<div class="table-wrap"><table class="compare-table"><thead><tr><th>分類</th><th>強み</th><th>注意点</th></tr></thead><tbody>'
            '<tr><td class="me">ASPI</td><td>同位体、QLE、Renergenを横断。</td><td>商業化確認前の要素が多い。</td></tr>'
            '<tr><td>同位体供給企業</td><td>医療・産業向け需要が安定しやすい。</td><td>品質、供給量、契約が重要。</td></tr>'
            '<tr><td>核燃料企業</td><td>先進原子炉テーマで評価されやすい。</td><td>規制・許認可・安全保障が重い。</td></tr>'
            '<tr><td>ヘリウム資源会社</td><td>供給制約と高付加価値が魅力。</td><td>生産設備と販売契約の実行が重要。</td></tr>'
            '</tbody></table></div><div class="highlight"><h3>差別化の見方</h3><p>ASPIはテーマの幅が広い反面、各テーマの実行段階は違います。同位体、Renergen、QLEを混ぜず、別々に成功確率を見ます。</p></div>'
        ),
        "SEC6_TLDR": li("C-14、Si-28、Yb-176、Renergen、HALEUを押さえると読みやすいです。", "*") + li("商業出荷と契約が売上に変わるかを確認します。", "*") + li("規制と希薄化は常に注意です。", "!"),
        "SEC6_CONTENT": '<div class="term-list">' + "".join(details(name, body) for name, body in terms) + "</div>",
        "SEC7_TLDR": li("最大材料は初期商業出荷とRenergen Phase 1の実行です。", "*") + li("QLE/HALEUは大きいが、規制と時間軸が重い材料です。", "*") + li("遅延・資金調達・希薄化で大きく下がる可能性があります。", "!"),
        "SEC7_CONTENT": (
            '<div class="timeline"><div class="tl-row"><div class="tl-date">2026/Q3</div><div class="tl-title">C-14・Yb-176初期商業出荷 <span class="signal bull">最重要</span></div><div class="tl-desc">売上化、品質、顧客継続を確認します。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/08/06</div><div class="tl-title">Renergen LNG契約 <span class="signal bull">追い風</span></div><div class="tl-desc">Tetra4の5年take-or-pay契約を会社が発表しました。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026後半</div><div class="tl-title">Renergen Phase 1確認 <span class="signal neutral">確認</span></div><div class="tl-desc">契約、生産、ヘリウム、資金の進捗を確認します。</div></div>'
            '<div class="tl-row"><div class="tl-date">中期</div><div class="tl-title">QLE/HALEU関連 <span class="signal neutral">大型材料</span></div><div class="tl-desc">許認可、資金、顧客、規制が焦点です。</div></div></div>'
            '<div class="info-row"><div class="info-box info-box-green"><div class="info-title info-title-green">追い風</div><div class="info-text">商業出荷、Renergen契約、ヘリウム、核燃料テーマ。</div></div>'
            '<div class="info-box info-box-amber"><div class="info-title info-title-amber">確認</div><div class="info-text">出荷実績、生産稼働、現金残高、発行株式数。</div></div>'
            '<div class="info-box info-box-red"><div class="info-title info-title-red">リスク</div><div class="info-text">遅延、規制、資金調達、希薄化、買収統合。</div></div></div>'
            + source_details()
        ),
    }


def scenario_values() -> dict[str, str]:
    probs = {"bear": 0.35, "base": 0.40, "bull": 0.25}
    expected = BEAR * probs["bear"] + BASE * probs["base"] + BULL * probs["bull"]
    own_score = (expected - BEAR) / (BULL - BEAR) * 100
    endpoint_rr = (BULL - P0) / (P0 - BEAR)
    expected_return = expected / P0 - 1
    bear_downside = (P0 - BEAR) / P0
    score = round(max(0, min(100, 50 + expected_return * 100 - probs["bear"] * bear_downside * 100)))
    return {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "Nasdaq",
        "VALUATION_DATE": DATE,
        "METHOD": "商業化前テーマ株向けリスク調整シナリオ",
        "VERDICT_STATUS": "悲観寄りの高リスク中立",
        "VERDICT_LINE_1": f"評価基準株価は悲観〜楽観レンジの{BAND_POSITION:.1f}%地点です。上値材料は大きい一方、商業出荷・Renergen・規制の確認前です。",
        "VERDICT_LINE_2": "この試算は2026年8月9日時点の公開情報と2026年8月7日終値を基準にしています。",
        "SCORE": str(score),
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "2026/08/07終値",
        "BASE_PRICE": usd(BASE),
        "BASE_DELTA": f"{(BASE / P0 - 1) * 100:+.1f}%",
        "EXPECTED_VALUE": usd(expected),
        "EXPECTED_DELTA": f"{(expected / P0 - 1) * 100:+.1f}%",
        "RISK_CLASS": "高",
        "RISK_NOTE": "商業化前、規制、資金調達、希薄化リスクが大きい",
        "WARN_BAND": '<div class="wrap"><div class="notice" style="margin-top:14px"><b>注意：</b>ASPIは商業化前の要素が多い高リスク銘柄です。テーマ性だけでなく、実際の出荷・契約・生産・資金を確認してください。</div></div>',
        "WARN_MESSAGE": "投資判断ではなく、公開情報に基づくシナリオ整理です。",
        "SNAPSHOT_LEAD": "今の株価は悲観ケースに近い位置です。商業出荷とRenergenが進めば標準ケースへ寄りますが、遅延や希薄化では悲観側へ戻りやすいです。",
        "BAND_POSITION": f"{BAND_POSITION:.1f}%",
        "ZONE_JUDGE": "悲観寄りの中立圏",
        "ZONE_NOTE": "C-14、Yb-176、Renergen Phase 1が進めば標準側へ、遅れれば悲観側へ寄ります。",
        "BEAR_PRICE": usd(BEAR),
        "BULL_PRICE": usd(BULL),
        "ENDPOINT_RR": f"{endpoint_rr:.1f}倍",
        "MARKET_SCORE": str(round(BAND_POSITION)),
        "OWN_SCORE": str(round(own_score)),
        "MARKET_REVERSE_NOTE": "このモデルで逆算すると、市場は大型テーマを一部見ながらも、商業化遅延・規制・希薄化リスクを強く見ています。",
        "SCENARIOS_LEAD": "現在株価から独立して、同位体出荷、Renergen、QLE/HALEU、資金調達リスクを置きました。",
        "BEAR_PROB": "35%",
        "BASE_PROB": "40%",
        "BULL_PROB": "25%",
        "BEAR_DELTA": f"{(BEAR / P0 - 1) * 100:+.1f}%",
        "BULL_DELTA": f"{(BULL / P0 - 1) * 100:+.1f}%",
        "BEAR_DL_ROWS": dl([("同位体", "出荷遅延"), ("Renergen", "生産・資金遅れ"), ("QLE", "規制進展なし"), ("株価", usd(BEAR))]),
        "BASE_DL_ROWS": dl([("同位体", "初期出荷確認"), ("Renergen", "Phase 1段階進行"), ("QLE", "テーマ維持"), ("株価", usd(BASE))]),
        "BULL_DL_ROWS": dl([("同位体", "複数品目で売上化"), ("Renergen", "LNG/ヘリウム前進"), ("QLE", "許認可・顧客進展"), ("株価", usd(BULL))]),
        "PRICE_ZONE_ROWS": '<div class="zone"><div><b>$2.50未満</b><span>★★★</span></div><p>商業化遅延や希薄化を強く織り込む価格帯です。</p></div><div class="zone"><div><b>$2.50〜$6.00</b><span>★★★</span></div><p>データと出荷待ちの中立圏。今の株価はここです。</p></div><div class="zone"><div><b>$6.00〜$10.00</b><span>★★</span></div><p>初期商業出荷とRenergen進捗を評価する価格帯です。</p></div><div class="zone"><div><b>$10.00超</b><span>★</span></div><p>複数テーマの成功と希薄化懸念後退が必要です。</p></div>',
        "SIGNAL_ROWS": '<div class="signal"><div><b>商業出荷</b><span class="up">最重要</span></div><p>C-14、Si-28、Yb-176の初期出荷を確認します。</p></div><div class="signal"><div><b>Renergen</b><span class="up">材料</span></div><p>LNG契約と液体ヘリウム生産が焦点です。</p></div><div class="signal"><div><b>QLE/HALEU</b><span class="flat">長期</span></div><p>規制・許認可・顧客確認が必要です。</p></div><div class="signal"><div><b>希薄化</b><span class="down">注意</span></div><p>開発型企業のため資金調達条件に注意します。</p></div>',
        "POSITIVES": "<li>同位体、ヘリウム、核燃料という大きなテーマを持ちます。</li><li>Q1 2026時点で現金と短期投資が大きく、開発余力があります。</li><li>RenergenのLNG契約ニュースは実行確認の材料です。</li><li>商業出荷が始まれば、テーマから売上化へ評価が変わります。</li>",
        "CONCERNS": "<li>本格売上はまだ確認途上です。</li><li>規制、許認可、設備、品質、顧客継続のリスクがあります。</li><li>買収統合とRenergenの資金・生産進捗に注意です。</li><li>追加資金調達や希薄化で1株価値が下がる可能性があります。</li>",
        "FORMULA": "PERではなく、商業出荷とRenergen進捗の3シナリオで評価しました。利益が安定していないため、短期倍率評価は使いません。",
        "CALC_TABLE_HEAD": th("ケース", "同位体", "Renergen", "計算株価", "確率", "確率加重"),
        "CALC_TABLE_ROWS": tr("悲観", "出荷遅延", "進捗遅れ", usd(BEAR), "35%", "$0.88") + tr("標準", "初期出荷", "段階進行", usd(BASE), "40%", "$2.40") + tr("楽観", "複数品目売上化", "LNG/ヘリウム前進", usd(BULL), "25%", "$2.50"),
        "CALC_NOTICE": "現在株価に合わせた逆算ではありません。商業化イベントの成否で大きく変わる条件付き試算です。",
        "CONDITIONS": details("悲観ケース：$2.50 / 確率35%", "商業出荷が遅れ、Renergenも資金・生産面で不透明なケースです。", True) + details("標準ケース：$6.00 / 確率40%", "同位体の初期出荷とRenergen Phase 1が段階的に進むケースです。") + details("楽観ケース：$10.00 / 確率25%", "同位体、Renergen、QLE/HALEUの複数材料が同時に評価されるケースです。"),
        "SENSITIVITY_HEAD": th("前提", "弱い", "標準", "強い"),
        "SENSITIVITY_ROWS": tr("商業出荷", "遅延 → $2.50", "初期出荷 → $6.00", "複数品目 → $10.00") + tr("資金調達", "希薄化大", "資金余力維持", "提携・契約で改善"),
        "SENSITIVITY_NOTE": "ASPIは1つの材料ではなく、複数イベントが連動して倍率が動きます。",
        "DIST_LEAD": "モンテカルロではなく、商業化前の3点分布です。",
        "DIST_ROWS": '<div class="dist-row"><span>$2.50</span><div class="track"><i style="width:35%"></i></div><b>35%</b></div><div class="dist-row"><span>$6.00</span><div class="track"><i style="width:40%"></i></div><b>40%</b></div><div class="dist-row"><span>$10.00</span><div class="track"><i style="width:25%"></i></div><b>25%</b></div>',
        "DIST_SUMMARY": "期待値は標準ケース近辺ですが、実際の株価はニュースで大きく振れやすいです。",
        "WATCH_ROWS": '<div class="signal"><div><b>C-14・Yb-176出荷</b></div><p>売上化、顧客継続、品質を確認します。</p></div><div class="signal"><div><b>Renergen Phase 1</b></div><p>LNG契約、液体ヘリウム、生産稼働を確認します。</p></div><div class="signal"><div><b>資金と株式数</b></div><p>現金、短期投資、借入、希薄化を確認します。</p></div>',
        "ASSUMPTIONS_ROWS": tr("評価基準株価", usd(P0), "市場データで確認", "2026/08/07", "自動更新後の終値") + tr("現金+短期投資", "$290.5M", "Q1 2026 10-Q", "2026/03/31", "現金$207.3M+短期投資$83.2M") + tr("Renergen契約", "Phase 1 LNGの約75%", "会社発表", "2026/08/06", "take-or-pay契約") + tr("同位体出荷", "2026年Q3中心", "会社資料", DATE, "初期商業出荷確認が必要"),
        "DEEPDIVE_DETAILS": details("手法選定理由", "ASPIは本格商業化前のテーマ株です。PERではなく、商業出荷とRenergenの成功確率でレンジを置きます。", True) + details("株価基準について", "2026年8月7日終値$4.43を使っています。自動株価更新後の価格です。") + details("主要出典", f'{source_link("会社情報", "company")}、{source_link("Q1 2026 10-Q", "q1")}、{source_link("Renergen契約ニュース", "renergen")}、{source_link("株価時系列", "price")}。<br><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>'),
        "DISCLAIMER": "本資料は情報提供を目的とした試算です。投資助言ではありません。ASPIは商業化前要素、規制、資金調達、希薄化で大きく変動します。",
        "FOOTER_NOTE": f"SiM MARKET LAB｜{COMPANY}（{TICKER}）株価シナリオ｜作成日 {DATE}",
    }


def catalyst_values() -> dict[str, str]:
    non_quant = '<div class="priced unknown"><div class="priced-head"><span>全体割合は出していません</span><b>算出不能</b></div><p>商業出荷、Renergen、QLE/HALEU、資金調達は価値経路が重なります。単純平均は使いません。</p><p>足りない情報：実出荷量、販売価格、粗利、Renergen生産、液体ヘリウム販売、追加資金調達条件です。</p><p>次に見る数字：売上、現金、短期投資、発行済株式、契約量、設備稼働率です。</p><p>再計算方法：材料ごとの成功確率を更新し、レポート2のシナリオ株価を再計算します。</p></div>'
    outcome_common = "<ul><li>数値化手法A〜Eを検討。</li><li>このページでは条件付きシナリオ再計算を主に使用。</li></ul>"

    def card(title: str, date: str, chips: str, mechanism: str, success: str, inline: str, failure: str, evidence: str) -> str:
        return f'''<article class="catalyst-card">
<div class="catalyst-head"><div><span class="pill">重要材料</span><h3>{title}</h3><div class="chips">{chips}</div></div><div class="date-box"><b>{date}</b><span>会社公表または予定</span></div></div>
<div class="mechanism">{mechanism}</div>
<div class="outcomes">
<div class="outcome success"><b>期待以上</b><div class="impact up">+25〜80%</div><p>{success}</p>{outcome_common}</div>
<div class="outcome inline"><b>ほぼ想定どおり</b><div class="impact flat">-10〜+25%</div><p>{inline}</p>{outcome_common}</div>
<div class="outcome failure"><b>期待外れ・遅延</b><div class="impact down">-25〜-55%</div><p>{failure}</p>{outcome_common}</div>
</div>
<div class="evidence"><div><h4>根拠</h4><ul>{evidence}</ul></div><div><h4>反証・先行指標</h4><ul><li>出荷遅延</li><li>契約量不足</li><li>資金調達条件の悪化</li></ul></div></div>
</article>'''

    cards = [
        card("C-14・Yb-176初期商業出荷", "2026年Q3", '<span class="chip">重要度5</span><span class="chip">最重要</span>', '<span>出荷</span><i>→</i><span>売上化</span><i>→</i><span>信頼</span>', "実出荷、顧客継続、品質、粗利が確認されれば標準ケースへ近づきます。", "少量出荷にとどまり、売上規模確認待ちなら中立です。", "出荷遅延や品質・顧客不透明なら悲観ケースへ寄ります。", "<li>会社資料でC-14とYb-176の初期商業出荷が2026年Q3目標と説明されています。</li><li>Q1 2026時点では本格売上化前です。</li>"),
        card("Renergen Phase 1", "2026年後半", '<span class="chip">重要度5</span><span class="chip blue">ヘリウム</span>', '<span>契約</span><i>→</i><span>生産</span><i>→</i><span>現金収入</span>', "LNGと液体ヘリウムの契約・生産・販売がそろえば評価拡大です。", "契約は進むが生産と現金収入の確認待ちなら中立です。", "建設・生産・資金で遅れると買収が重荷になります。", "<li>2026年8月6日にTetra4の5年take-or-pay契約を会社が発表。</li><li>会社はPhase 1 LNG想定量の約75%が契約で支えられると説明しています。</li>"),
        card("Si-28初期出荷", "2026年半ば以降", '<span class="chip">重要度4</span><span class="chip blue">量子</span>', '<span>材料</span><i>→</i><span>顧客</span><i>→</i><span>テーマ継続</span>', "量子・半導体向け顧客との継続需要が見えれば上振れです。", "初期出荷のみなら中期材料です。", "遅延や顧客不明ならテーマ剥落です。", "<li>会社資料でSi-28の初期商業出荷が目標として示されています。</li><li>量子・半導体材料として注目されます。</li>"),
        card("QLE/HALEU関連", "中期", '<span class="chip">重要度4</span><span class="chip blue">核燃料</span>', '<span>許認可</span><i>→</i><span>資金</span><i>→</i><span>顧客</span>', "許認可、顧客、資金が同時に進めば楽観ケース材料です。", "テーマ維持にとどまるなら短期影響は限定的です。", "規制・資金で進まなければ評価は下がります。", "<li>QLEはU-235やLi-6/7など先進原子力向けテーマを持ちます。</li><li>核燃料関連は規制と許認可が重要です。</li>"),
    ]
    return {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "Nasdaq",
        "VALUATION_DATE": DATE,
        "LAST_UPDATED": DATE,
        "REPORT_STATUS": "商業化確認待ち",
        "SUMMARY_LINE_1": "C-14・Yb-176出荷、Renergen Phase 1、Si-28、QLE/HALEUが主な材料です。",
        "SUMMARY_LINE_2": "全体の織り込み割合は、各材料の価値経路が重なるため単純計算していません。",
        "OVERALL_PRICED_IN": "算出不能",
        "OVERALL_PRICED_LABEL": "全体割合は出していません",
        "PRICED_IN_CONFIDENCE": "低〜中",
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "2026/08/07終値",
        "NEXT_CATALYST_TITLE": "C-14・Yb-176初期商業出荷",
        "NEXT_CATALYST_WINDOW": "2026年Q3",
        "DATE_CONFIDENCE": "会社予定",
        "CATALYST_COUNT": "4件",
        "WARN_BAND": "",
        "NO_CATALYST_NOTICE": "",
        "OVERALL_PRICED_BLOCK": non_quant,
        "PRICED_IN_METHOD": "価値経路の分離条件を満たさないため、全体割合は非算出。個別材料は条件付きシナリオ再計算でレンジ表示。",
        "SURPRISE_UP": "同位体の実出荷、Renergenの生産、ヘリウム販売、QLEの許認可進展が同時に見えることです。",
        "SURPRISE_DOWN": "商業出荷遅延、Renergenの資金・生産遅れ、希薄化、規制停滞です。",
        "PRIMARY_RISK": "テーマが大きい一方、実売上確認前の要素が多く、資金調達と希薄化で株価が大きく下がる可能性です。",
        "TIMELINE_ROWS": '<div class="time-row"><div class="time-date">2026/Q3</div><div class="time-dot"></div><div class="time-body"><b>C-14・Yb-176初期商業出荷</b><p>最初の売上化確認が焦点。</p><div class="time-meta"><span class="chip">最重要</span></div></div></div><div class="time-row"><div class="time-date">2026/08/06</div><div class="time-dot"></div><div class="time-body"><b>Renergen LNG契約</b><p>Tetra4の5年take-or-pay契約を会社が発表。</p><div class="time-meta"><span class="chip blue">発表済み</span></div></div></div><div class="time-row"><div class="time-date">2026後半</div><div class="time-dot"></div><div class="time-body"><b>Renergen Phase 1確認</b><p>LNGと液体ヘリウムの生産・販売を確認。</p><div class="time-meta"><span class="chip">確認</span></div></div></div><div class="time-row"><div class="time-date">中期</div><div class="time-dot"></div><div class="time-body"><b>QLE/HALEU関連</b><p>規制、許認可、資金、顧客を確認。</p><div class="time-meta"><span class="chip blue">大型材料</span></div></div></div>',
        "CATALYST_CARDS": "".join(cards),
        "DEPENDENCY_ROWS": '<div class="signal"><div><b>出荷と資金</b><span class="up">連動</span></div><p>良い出荷でも、資金調達条件が悪いと評価は伸びにくいです。</p></div><div class="signal"><div><b>Renergenと契約</b><span class="flat">確認</span></div><p>契約が生産と現金収入に変わるかを見ます。</p></div><div class="signal"><div><b>QLEと規制</b><span class="flat">長期</span></div><p>許認可が進まないと大型テーマは評価されにくいです。</p></div>',
        "WATCH_ROWS": '<div class="signal"><div><b>初期商業出荷</b><span class="up">最重要</span></div><p>出荷日、数量、顧客、粗利を確認します。</p></div><div class="signal"><div><b>Renergen生産</b><span class="up">重要</span></div><p>LNGと液体ヘリウムの稼働を確認します。</p></div><div class="signal"><div><b>現金と株式数</b><span class="down">注意</span></div><p>資金調達と希薄化を確認します。</p></div><div class="signal"><div><b>規制</b><span class="flat">長期</span></div><p>QLE/HALEUの許認可を確認します。</p></div>',
        "ASSUMPTION_ROWS": tr("評価基準株価", usd(P0), "市場データで確認", "2026/08/07", "自動更新後の終値") + tr("現金+短期投資", "$290.5M", "Q1 2026 10-Q", "2026/03/31", "現金$207.3M+短期投資$83.2M") + tr("Renergen契約", "Phase 1 LNGの約75%", "会社発表", "2026/08/06", "take-or-pay契約") + tr("同位体出荷", "2026年Q3中心", "会社資料", DATE, "初期商業出荷確認が必要"),
        "SOURCE_DETAILS": f'<ul><li>{source_link("会社情報", "company")}</li><li>{source_link("決算資料", "financials")}</li><li>{source_link("Q1 2026 10-Q", "q1")}</li><li>{source_link("Renergen契約ニュース", "renergen")}</li><li>{source_link("会社プレゼン", "presentation")}</li><li>{source_link("株価時系列", "price")}</li></ul><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p>',
        "VALIDATION_DETAILS": "<p>PASS：会社情報、決算資料、Q1 2026 10-Q、Renergen契約ニュース、株価時系列を確認。WARN：商業出荷、Renergen生産、QLE/HALEUは今後の実行確認が必要です。</p>",
        "UPDATE_HISTORY": f"<p>{DATE}：統一テンプレート版へ修正。Q1 2026 10-Q、Renergen契約、2026年8月7日終値を反映。</p>",
        "DISCLAIMER": "本資料は情報提供を目的とした整理です。投資助言ではありません。カタリストの影響率は条件付き試算であり、短期株価を予測するものではありません。",
        "FOOTER_NOTE": f"SiM MARKET LAB｜{COMPANY}（{TICKER}）カタリスト｜作成日 {DATE}",
    }


def write_reports() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "company.html").write_text(render_template("template_stock_guide_v4_unified.html", guide_values()), encoding="utf-8")
    (OUT_DIR / "valuation.html").write_text(render_template("template_scenario_v4_unified.html", scenario_values()), encoding="utf-8")
    (OUT_DIR / "catalysts.html").write_text(render_template("template_catalyst_v1_unified.html", catalyst_values()), encoding="utf-8")


def upsert_site_data() -> None:
    stocks_path = ROOT / "data" / "stocks.json"
    stocks_payload = json.loads(stocks_path.read_text(encoding="utf-8"))
    stock = {
        "id": "asp-isotopes-aspi",
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
            "company": {"path": "./stocks/asp-isotopes-aspi/company.html", "available": True},
            "valuation": {"path": "./stocks/asp-isotopes-aspi/valuation.html", "available": True},
            "catalysts": {"path": "./stocks/asp-isotopes-aspi/catalysts.html", "available": True},
        },
    }
    stocks_payload["stocks"] = [item for item in stocks_payload["stocks"] if item["id"] != "asp-isotopes-aspi"]
    stocks_payload["stocks"].append(stock)
    stocks_path.write_text(json.dumps(stocks_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    prices_path = ROOT / "data" / "prices.json"
    prices_payload = json.loads(prices_path.read_text(encoding="utf-8"))
    prices_payload.setdefault("prices", {})["asp-isotopes-aspi"] = {
        "symbol": TICKER,
        "price": P0,
        "previousClose": PREVIOUS_CLOSE,
        "change": round(P0 - PREVIOUS_CLOSE, 4),
        "changePct": round((P0 - PREVIOUS_CLOSE) / PREVIOUS_CLOSE * 100, 4),
        "currency": "USD",
        "marketTime": "2026-08-07T20:00:01+00:00",
        "updatedAt": "2026-08-08T15:55:15.571113+00:00",
        "status": "ok",
    }
    prices_payload["quoteCount"] = len(prices_payload["prices"])
    prices_path.write_text(json.dumps(prices_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    signals_path = ROOT / "data" / "signals.json"
    signals_payload = json.loads(signals_path.read_text(encoding="utf-8"))
    signals_payload["updatedAt"] = datetime.now(timezone.utc).isoformat()
    signals_payload.setdefault("signals", {})["asp-isotopes-aspi"] = {
        "position": SIGNAL_POSITION,
        "zone": "中立",
        "asOf": DATE,
        "components": {
            "valuation": round(BAND_POSITION, 1),
            "catalysts": 72.0,
            "businessRisk": 82.0,
        },
        "reportRevision": "asp-isotopes-aspi-2026-08-09-unified",
        "summary": "同位体出荷、Renergen、QLE/HALEUが材料。株価は悲観寄りだが、商業化と規制の実行リスクが高いため中立。",
    }
    signals_path.write_text(json.dumps(signals_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_reports()
    upsert_site_data()


if __name__ == "__main__":
    main()
