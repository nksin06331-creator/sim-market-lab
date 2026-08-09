"""Generate Redwire report HTML files from the bundled SiM templates."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from generate_rocket_lab_reports import dl, li, render_template, th, tr


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stocks" / "redwire-rdw"

COMPANY = "レッドワイヤー"
TICKER = "RDW"
DATE = "2026-08-08"
P0 = 12.16
PREVIOUS_CLOSE = 10.76
SHARES_M = 198.9
MARKET_CAP_B = P0 * SHARES_M / 1000

SOURCES = {
    "q2_article": "https://www.investors.com/news/howmet-aerospace-hwm-stock-breakout-ati-stock-redwire-rdw-caci-international-earnings-rally-defense-stocks/",
    "q1": "https://ir.rdw.com/sec-filings/all-sec-filings/content/0001819810-26-000060/exhibit991redwire03312026e.htm",
    "annual": "https://www.sec.gov/Archives/edgar/data/1819810/000181981026000029/rdw-20251231.htm",
    "ir": "https://ir.rdw.com/",
    "financials": "https://ir.rdw.com/financial-information/financial-results",
    "presentations": "https://ir.rdw.com/company-information/presentations",
    "edge": "https://rdw.com/newsroom/redwire-announces-sunsetting-of-edge-autonomy-brand-and-new-organizational-structure-to-align-with-market-opportunities-for-accelerated-growth/",
    "stalker": "https://rdw.com/newsroom/redwire-awarded-20-million-in-follow-on-orders-from-portfolio-acquisition-executive-robotic-autonomous-systems-pae-ras-to-deliver-stalker-uas-advanced-navigation-and-standard-systems/",
    "space_md": "https://rdw.com/newsroom/redwire-opens-state-of-the-art-facility-in-indiana-to-accelerate-space-enabled-rd-and-manufacturing-with-a-focus-on-next-gen-drug-development-and-human-health-breakthroughs/",
    "q2_date": "https://www.businesswire.com/news/home/20260730660026/en/",
}


def usd(value: int | float) -> str:
    return f"${value:,.2f}" if value < 100 else f"${value:,.0f}"


def details(title: str, body: str, open_: bool = False) -> str:
    return f"<details{' open' if open_ else ''}><summary>{title}</summary><p>{body}</p></details>"


def source_link(label: str, key: str) -> str:
    return f'<a href="{SOURCES[key]}" target="_blank" rel="noopener noreferrer">{label}</a>'


def guide_values() -> dict[str, str]:
    source_details = (
        '<details class="term-item" open><summary class="term-header"><span class="term-name">主要出典</span><span class="term-arrow">⌄</span></summary>'
        '<div class="term-body"><p>'
        f'{source_link("2026年1Q決算リリース", "q1")}、'
        f'{source_link("2025年Form 10-K", "annual")}、'
        f'{source_link("Redwire投資家向けサイト", "ir")}、'
        f'{source_link("Edge Autonomy統合発表", "edge")}、'
        f'{source_link("Q2決算関連記事", "q2_article")}を確認しました。'
        "本文の数値は2026年8月8日時点の公開情報に基づきます。"
        '</p><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p></div></details>'
    )
    terms = [
        ("Space", "宇宙機、センサー、電源、構造、軌道上製造、微小重力ペイロードなどの宇宙向け事業です。"),
        ("Defense", "Edge Autonomy由来のUAS、ISR、マルチドメイン運用など防衛向け事業です。"),
        ("Stalker UAS", "長時間飛行の無人航空機システムです。米軍・同盟国向けの防衛需要が注目点です。"),
        ("Edge Autonomy", "2025年に取得した無人航空機・防衛技術の事業です。2026年からRedwireブランドへ統合しています。"),
        ("Backlog", "受注残です。RedwireはQ1 2026で$498.1Mの記録的バックログを公表しました。"),
        ("Book-to-Bill", "受注額を売上で割る指標です。1倍超なら受注残が積み上がりやすい状態です。"),
        ("Andromeda IDIQ", "最大$1.8B規模の先進宇宙機関連IDIQです。受注機会の枠であり、全額売上確定ではありません。"),
        ("ELSA", "高性能・低質量ソーラーアレイです。国家安全保障向けプログラムで初回注文が出ています。"),
        ("SpaceMD", "宇宙での医薬品研究・製造を商業化するRedwireの取り組みです。"),
        ("Gross Margin", "売上総利益率です。Q1 2026は26.6%へ改善しました。"),
        ("Adjusted EBITDA", "一時費用等を調整した利益指標です。GAAP損益とは分けて見ます。"),
        ("Material Weakness", "内部統制の重要な不備です。2025年10-Kで継続的な是正計画が説明されています。"),
    ]
    return {
        "TICKER": TICKER,
        "COMPANY_NAME": COMPANY,
        "INDUSTRY": "宇宙インフラ・防衛テクノロジー",
        "DATE": DATE,
        "TAGLINE": "宇宙インフラ、センサー、電源、軌道上製造、無人航空機、防衛向け自律システムを組み合わせる宇宙・防衛テクノロジー企業です。",
        "HERO_TAGS": '<span class="hero-tag">宇宙インフラ</span><span class="hero-tag">UAS</span><span class="hero-tag">防衛宇宙</span><span class="hero-tag">NYSE</span>',
        "HERO_STATS": (
            f'<div class="stat"><div class="stat-value">{usd(P0)}</div><div class="stat-label">評価基準株価</div><div class="stat-note">2026/08/07終値</div></div>'
            f'<div class="stat"><div class="stat-value">${MARKET_CAP_B:.1f}B</div><div class="stat-label">時価総額の目安</div><div class="stat-note">約1.99億株で計算</div></div>'
            '<div class="stat"><div class="stat-value up">$117.1M</div><div class="stat-label">2026年2Q売上</div><div class="stat-note">市場記事ベース、過去最高</div></div>'
            '<div class="stat"><div class="stat-value">$498.1M</div><div class="stat-label">2026年1Q受注残</div><div class="stat-note">会社公表</div></div>'
        ),
        "SEC2_LABEL": "事業モデル",
        "SEC3_LABEL": "防衛UAS",
        "SEC4_LABEL": "宇宙技術",
        "SEC5_LABEL": "競合比較",
        "SEC1_TLDR": li("Redwireは宇宙インフラと防衛UASを組み合わせる会社です。", "*") + li("Q1は売上$97.0M、粗利率26.6%、受注残$498.1Mでした。", "*") + li("Q2は売上急伸が報じられましたが、赤字・買収統合・内部統制はリスクです。", "!"),
        "SEC1_FACTS": (
            "<div><dt>正式社名</dt><dd>Redwire Corporation</dd></div><div><dt>本社</dt><dd>Jacksonville, Florida</dd></div>"
            "<div><dt>上場</dt><dd>NYSE（RDW）</dd></div><div><dt>CEO</dt><dd>Peter Cannito</dd></div>"
            "<div><dt>従業員</dt><dd>約1,400人</dd></div><div><dt>事業</dt><dd>Space / Defense</dd></div>"
        ),
        "SEC1_CARDS": (
            '<div class="card-sm"><span class="card-emoji">🛰️</span><div class="card-title">何をしている</div><div class="card-desc">宇宙機部品、センサー、電源、構造、軌道上製造を提供します。</div></div>'
            '<div class="card-sm"><span class="card-emoji">🛩️</span><div class="card-title">防衛の柱</div><div class="card-desc">Edge Autonomy由来のStalker UASなどを防衛顧客へ展開します。</div></div>'
            '<div class="card-sm"><span class="card-emoji">📈</span><div class="card-title">直近業績</div><div class="card-desc">Q1 2026売上は$97.0M、Q2は過去最高売上が報じられています。</div></div>'
            '<div class="card-sm"><span class="card-emoji">🧪</span><div class="card-title">注目点</div><div class="card-desc">宇宙医薬品、UAS、国家安全保障、月面・深宇宙関連が材料です。</div></div>'
        ),
        "SEC1_BIZMODEL": (
            '<li><span class="kp-emoji">🛰️</span><span class="kp-text"><b>宇宙</b>：アビオニクス、センサー、電源、構造、微小重力ペイロードを提供します。</span></li>'
            '<li><span class="kp-emoji">🛡️</span><span class="kp-text"><b>防衛</b>：StalkerなどUAS、ISR、自律システムを提供します。</span></li>'
            '<li><span class="kp-emoji">📄</span><span class="kp-text"><b>受注残</b>：政府・防衛・商業案件が将来売上の土台になります。</span></li>'
        ),
        "SEC1_HIGHLIGHT": '<div class="highlight"><h3>RDWを見る基本ルール</h3><p>Redwireはテーマ性が強い一方、買収統合で事業構造が変わっています。売上成長、粗利率、受注残、UASの継続受注、内部統制の改善をセットで見ます。</p></div>',
        "SEC2_ICON": "🛰️",
        "SEC2_TITLE": "事業モデルの<span class=\"g\">基本</span>",
        "SEC2_SUB": "SpaceとDefenseの2本柱で見る",
        "SEC2_TLDR": li("2026年からSpaceとDefenseの2セグメントが見やすくなりました。", "*") + li("Edge Autonomy統合で防衛UASの比重が増えています。", "*") + li("買収成長は売上を押し上げる一方、統合と内部統制のリスクもあります。", "!"),
        "SEC2_CONTENT": (
            '<p class="lead">Redwireは、宇宙向け部品・システムと、防衛向けUAS・自律システムを持つ企業です。Edge Autonomy買収後、宇宙と防衛を一体で売る形へ移っています。</p>'
            '<div class="sowhat"><p><b>つまり</b>、RDWは「宇宙テーマ」だけでなく「防衛UASの受注企業」として見る必要があります。</p></div>'
            '<div class="term-list">'
            + details("Space", "宇宙船の電源、センサー、構造、通信、軌道上製造、微小重力実験などを扱います。", True)
            + details("Defense", "Stalker UAS、ISR、自律システム、マルチドメイン運用などを扱います。")
            + details("Backlog", "Q1 2026の受注残は$498.1Mでした。売上成長の見通しを支える一方、実行と利益率が重要です。")
            + details("内部統制", "2025年10-Kでは一部事業の内部統制上の重要な不備と是正計画が説明されています。投資家はここも確認します。")
            + "</div>"
        ),
        "SEC3_TITLE": "防衛UASと<span class=\"g\">Edge Autonomy</span>",
        "SEC3_SUB": "Stalkerが防衛テーマの中心",
        "SEC3_TLDR": li("Stalker UASは防衛・ISR需要の中心製品です。", "*") + li("PAE RASから追加注文が出ており、継続受注が焦点です。", "*") + li("防衛予算、納入能力、採算が株価材料になります。", "!"),
        "SEC3_CONTENT": (
            '<div class="product-grid"><div class="product-box"><div class="product-symbol">UAS</div><div class="product-name">Stalker</div><div class="product-use">長時間飛行・ISR向け無人機。</div></div>'
            '<div class="product-box"><div class="product-symbol">ISR</div><div class="product-name">Sensors</div><div class="product-use">監視・偵察・通信支援。</div></div>'
            '<div class="product-box"><div class="product-symbol">AI</div><div class="product-name">Autonomy</div><div class="product-use">自律運用・マルチドメイン対応。</div></div></div>'
            '<div class="term-list">'
            + details("Stalker UAS", "長時間飛行の無人航空機システムです。米軍・同盟国のISR需要と結びつきます。", True)
            + details("PAE RAS注文", "2026年4月、Stalker UAS向けの$20Mフォローオン注文を発表しました。")
            + details("Edge Autonomy統合", "RedwireはEdge AutonomyブランドをRedwireへ統合し、防衛市場での見え方を整理しました。")
            + details("防衛の注意点", "予算、調達時期、納入能力、輸出規制、顧客集中で売上時期が変わることがあります。")
            + "</div>"
        ),
        "SEC4_TITLE": "宇宙技術と<span class=\"g\">SpaceMD</span>",
        "SEC4_SUB": "宇宙インフラから宇宙医薬品へ",
        "SEC4_TLDR": li("宇宙機部品とミッション機器が基盤です。", "*") + li("SpaceMDは微小重力を使う医薬品開発テーマです。", "*") + li("テーマ性は強いが、商業化時期と収益貢献は確認が必要です。", "!"),
        "SEC4_CONTENT": (
            '<ul class="keypoints"><li><span class="kp-emoji">🔋</span><span class="kp-text"><b>電源・センサー</b>：宇宙機の電源、姿勢制御、構造などの部品を提供します。</span></li>'
            '<li><span class="kp-emoji">🧪</span><span class="kp-text"><b>SpaceMD</b>：宇宙での医薬品研究・製造を商業化する取り組みです。</span></li>'
            '<li><span class="kp-emoji">🏭</span><span class="kp-text"><b>施設拡張</b>：IndianaやHuntsvilleなどで製造・R&D体制の拡大が進んでいます。</span></li></ul>'
            '<div class="sowhat"><p><b>つまり</b>、Redwireは既存の宇宙部品に、防衛UASと宇宙医薬品という成長テーマを重ねています。</p></div>'
        ),
        "SEC5_TITLE": "競合と<span class=\"g\">比べる</span>",
        "SEC5_SUB": "宇宙・防衛の小型成長株",
        "SEC5_TLDR": li("競合はRocket Lab、AeroVironment、Kratos、防衛大手などです。", "*") + li("Redwireは宇宙部品とUASを組み合わせる独自性があります。", "*") + li("規模、利益率、内部統制ではまだ確認事項があります。", "!"),
        "SEC5_CONTENT": (
            '<div class="table-wrap"><table class="compare-table"><thead><tr><th>企業</th><th>主な強み</th><th>注意点</th></tr></thead><tbody>'
            '<tr><td class="me">Redwire</td><td>宇宙インフラ、防衛UAS、微小重力商業化。</td><td>赤字、買収統合、内部統制。</td></tr>'
            '<tr><td>Rocket Lab</td><td>打ち上げと宇宙システムの垂直統合。</td><td>評価倍率が高くNeutron開発リスク。</td></tr>'
            '<tr><td>AeroVironment</td><td>UASと徘徊型弾薬で防衛実績。</td><td>Redwireより成熟企業として見られやすい。</td></tr>'
            '<tr><td>防衛大手</td><td>資本力、政府契約、規模。</td><td>成長率は大型成熟企業として評価されやすい。</td></tr>'
            '</tbody></table></div><div class="highlight"><h3>差別化の見方</h3><p>Redwireは宇宙インフラ企業でありつつ、防衛UASと宇宙医薬品テーマも持ちます。複数テーマが評価される一方、実行リスクも分散して存在します。</p></div>'
        ),
        "SEC6_TLDR": li("Space、Defense、Backlog、Book-to-Billを押さえると読みやすいです。", "*") + li("UASは防衛需要、SpaceMDは長期テーマです。", "*") + li("Adjusted EBITDAとGAAP損失は分けて見ます。", "!"),
        "SEC6_CONTENT": '<div class="term-list">' + "".join(details(name, body) for name, body in terms) + "</div>",
        "SEC7_TLDR": li("Q2決算、UAS追加受注、施設拡張、SpaceMDが主な材料です。", "*") + li("Q1の受注残と粗利率改善は支えです。", "*") + li("赤字、希薄化、内部統制、買収統合はリスクです。", "!"),
        "SEC7_CONTENT": (
            '<div class="timeline"><div class="tl-row"><div class="tl-date">2026/08/05</div><div class="tl-title">Q2決算 <span class="signal bull">重要</span></div><div class="tl-desc">売上$117.07M、過去最高売上が報じられました。公式10-Qで詳細確認が必要です。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/07</div><div class="tl-title">施設拡張・SpaceMD <span class="signal neutral">確認</span></div><div class="tl-desc">宇宙医薬品・防衛UASの製造/R&D体制を拡大しています。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026年後半</div><div class="tl-title">UAS受注と納入 <span class="signal bull">追い風</span></div><div class="tl-desc">Stalker関連の追加注文と納入進捗を確認します。</div></div></div>'
            '<div class="info-row"><div class="info-box info-box-green"><div class="info-title info-title-green">追い風</div><div class="info-text">Q2売上急伸、Q1受注残$498.1M、防衛UAS需要。</div></div>'
            '<div class="info-box info-box-amber"><div class="info-title info-title-amber">確認</div><div class="info-text">Q2公式10-Q、粗利率、Adjusted EBITDA、受注残更新。</div></div>'
            '<div class="info-box info-box-red"><div class="info-title info-title-red">リスク</div><div class="info-text">赤字、内部統制、買収統合、希薄化、政府予算。</div></div></div>'
            + source_details
        ),
    }


def scenario_values() -> dict[str, str]:
    bear, base, bull = 8.0, 15.0, 24.0
    probs = {"bear": 0.30, "base": 0.50, "bull": 0.20}
    expected = bear * probs["bear"] + base * probs["base"] + bull * probs["bull"]
    band = (P0 - bear) / (bull - bear) * 100
    own_score = (expected - bear) / (bull - bear) * 100
    endpoint_rr = (bull - P0) / (P0 - bear)
    expected_return = expected / P0 - 1
    bear_downside = (P0 - bear) / P0
    score = round(max(0, min(100, 50 + expected_return * 100 - probs["bear"] * bear_downside * 100)))
    return {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "NYSE",
        "VALUATION_DATE": DATE,
        "METHOD": "高成長宇宙・防衛向け売上倍率シナリオ",
        "VERDICT_STATUS": "標準ケース手前の中立圏",
        "VERDICT_LINE_1": "評価基準株価は悲観〜楽観レンジの26.0%地点です。Q2売上急伸と防衛UAS需要は追い風ですが、赤字・統合・内部統制リスクも残ります。",
        "VERDICT_LINE_2": "この試算は2026年8月8日時点の公開情報で固定しています。Q2の詳細は公式10-Q確認前の暫定扱いです。",
        "SCORE": str(score),
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "2026/08/07 16:00 ET",
        "BASE_PRICE": usd(base),
        "BASE_DELTA": "+23.4%",
        "EXPECTED_VALUE": usd(expected),
        "EXPECTED_DELTA": "+20.9%",
        "RISK_CLASS": "高い",
        "RISK_NOTE": "小型成長株、赤字、買収統合",
        "WARN_BAND": '<div class="wrap"><div class="notice" style="margin-top:14px"><b>注意：</b>Q2売上は市場記事で確認した速報値を使っています。公式10-Q公開後に、粗利率・受注残・希薄化を再確認してください。</div></div>',
        "SNAPSHOT_LEAD": "今の株価は、Q2売上急伸と防衛UASテーマを評価し始めています。ただし、過去高値圏ほど楽観ケースを強く織り込んでいるわけではありません。",
        "BAND_POSITION": f"{band:.1f}%",
        "ZONE_JUDGE": "標準ケースの手前",
        "ZONE_NOTE": "Q2の粗利率と受注残が強ければ標準ケースへ寄ります。",
        "BEAR_PRICE": usd(bear),
        "BULL_PRICE": usd(bull),
        "ENDPOINT_RR": f"{endpoint_rr:.1f}倍",
        "MARKET_SCORE": str(round(band)),
        "OWN_SCORE": str(round(own_score)),
        "MARKET_REVERSE_NOTE": "このモデルで逆算すると、今の株価は2027年売上約$600M、EV/Sales 4倍台後半に近い成長期待を織り込む水準です。市場全体の予想ではなく、このモデル上の逆算です。",
        "SCENARIOS_LEAD": "赤字成長企業のためPERではなく売上倍率を使います。SpaceとDefenseの成長、粗利率、内部統制、株式数を主要前提にしました。",
        "BEAR_PROB": "30%",
        "BASE_PROB": "50%",
        "BULL_PROB": "20%",
        "BEAR_DELTA": "-34.2%",
        "BULL_DELTA": "+97.4%",
        "BEAR_DL_ROWS": dl([("2027年売上", "$500M"), ("EV/Sales", "3.5倍"), ("前提", "統合遅延・倍率低下"), ("株式数", "約1.99億株")]),
        "BASE_DL_ROWS": dl([("2027年売上", "$650M"), ("EV/Sales", "4.5倍"), ("前提", "UASと宇宙が堅調"), ("株式数", "約1.99億株")]),
        "BULL_DL_ROWS": dl([("2027年売上", "$800M"), ("EV/Sales", "6.0倍"), ("前提", "防衛UASとSpaceMDが評価拡大"), ("株式数", "約1.99億株")]),
        "PRICE_ZONE_ROWS": '<div class="zone"><div><b>$8未満</b><span>★★★★</span></div><p>悲観ケース以下。赤字や統合不安をかなり織り込む価格帯です。</p></div><div class="zone"><div><b>$8〜$15</b><span>★★★</span></div><p>標準ケース手前。今の株価はこの範囲です。</p></div><div class="zone"><div><b>$15〜$24</b><span>★★</span></div><p>UASと宇宙テーマの両方が評価される価格帯です。</p></div><div class="zone"><div><b>$24超</b><span>★</span></div><p>楽観ケース超。高成長と黒字化の道筋が必要です。</p></div>',
        "SIGNAL_ROWS": '<div class="signal"><div><b>Q2売上急伸</b><span class="up">追い風</span></div><p>売上$117.07M、過去最高が報じられました。</p></div><div class="signal"><div><b>Q1受注残$498.1M</b><span class="up">追い風</span></div><p>将来売上の見通しを支えます。</p></div><div class="signal"><div><b>買収統合</b><span class="flat">確認</span></div><p>Edge Autonomy統合が売上と利益にどう出るか確認します。</p></div><div class="signal"><div><b>内部統制</b><span class="down">注意</span></div><p>10-Kで重要な不備と是正計画が説明されています。</p></div>',
        "POSITIVES": "<li>Q2売上は$117.07M、過去最高売上が報じられました。</li><li>Q1 2026の受注残は$498.1M、Book-to-Billは1.92でした。</li><li>Stalker UASや防衛向け注文が継続しています。</li><li>SpaceMDや施設拡張で長期テーマもあります。</li>",
        "CONCERNS": "<li>GAAPでは赤字です。Q1純損失は$76.5Mでした。</li><li>Q2詳細は公式10-Qで粗利率・損失・株式数の確認が必要です。</li><li>買収統合と内部統制の是正が残ります。</li><li>小型株で値動きが大きく、希薄化や政府予算変更もリスクです。</li>",
        "FORMULA": "主計算は売上倍率です。赤字成長企業のため、短期PERよりも将来売上とEV/Salesを使いました。",
        "CALC_TABLE_HEAD": th("ケース", "2027年売上", "EV/Sales", "計算株価", "確率", "確率加重"),
        "CALC_TABLE_ROWS": tr("悲観", "$500M", "3.5倍", usd(bear), "30%", "$2.40") + tr("標準", "$650M", "4.5倍", usd(base), "50%", "$7.50") + tr("楽観", "$800M", "6.0倍", usd(bull), "20%", "$4.80"),
        "CALC_NOTICE": "現在株価に合わせて標準ケースを置いていません。Q2速報、Q1受注残、UAS需要、統合リスクを踏まえた条件付き試算です。",
        "CONDITIONS": details("悲観ケース：$8 / 確率30%", "Q2後に利益率や統合不安が重く見られ、評価倍率が下がるケースです。", True) + details("標準ケース：$15 / 確率50%", "防衛UASと宇宙インフラが堅調に伸び、売上倍率が適度に維持されるケースです。") + details("楽観ケース：$24 / 確率20%", "UAS大型受注、SpaceMD、粗利率改善、内部統制改善が重なるケースです。"),
        "SENSITIVITY_HEAD": th("前提", "弱い", "標準", "強い"),
        "SENSITIVITY_ROWS": tr("2027年売上", "$550M → $11", "$650M → $15", "$750M → $19") + tr("EV/Sales", "3.5倍 → $9", "4.5倍 → $15", "5.5倍 → $21"),
        "SENSITIVITY_NOTE": "1変数だけを動かした簡易感応度です。実際には売上成長と倍率が同時に動きます。",
        "DIST_LEAD": "モンテカルロではなく、悲観・標準・楽観の3点分布です。",
        "DIST_ROWS": '<div class="dist-row"><span>$8</span><div class="track"><i style="width:30%"></i></div><b>30%</b></div><div class="dist-row"><span>$15</span><div class="track"><i style="width:50%"></i></div><b>50%</b></div><div class="dist-row"><span>$24</span><div class="track"><i style="width:20%"></i></div><b>20%</b></div>',
        "DIST_SUMMARY": "中心は標準ケースです。ただし小型宇宙・防衛株として、材料と市場倍率で大きく振れやすい銘柄です。",
        "WATCH_ROWS": '<div class="signal"><div><b>Q2 10-Q</b></div><p>売上、粗利率、純損失、受注残、株式数を確認します。</p></div><div class="signal"><div><b>Stalker UAS注文</b></div><p>追加注文と納入能力を確認します。</p></div><div class="signal"><div><b>内部統制の是正</b></div><p>監査・開示上のリスク低下を確認します。</p></div>',
        "ASSUMPTIONS_ROWS": tr("評価基準株価", usd(P0), "市場データで確認済み", "2026/08/07終値") + tr("Q2売上", "$117.07M", "市場記事で確認", "2026/08/06") + tr("Q1売上", "$97.0M", "公式情報で確認済み", "2026年1〜3月") + tr("Q1受注残", "$498.1M", "公式情報で確認済み", "2026/03/31"),
        "DEEPDIVE_DETAILS": details("手法選定理由", "Redwireは高成長ですがGAAP赤字です。短期PERではなく、将来売上とEV/Salesを主に使いました。", True) + details("株式数について", "2025年10-Kの発行済株式数と市場データを参考に約1.99億株で概算しています。買収や資金調達で変わり得ます。") + details("主要出典", f'{source_link("Q1決算", "q1")}、{source_link("2025年10-K", "annual")}、{source_link("Q2関連記事", "q2_article")}、{source_link("Edge Autonomy統合", "edge")}。<br><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>'),
        "DISCLAIMER": "本資料は情報提供を目的とした試算です。投資助言ではありません。宇宙・防衛関連の小型成長株は、契約、統合、資金調達、市場倍率により大きく変動します。",
        "FOOTER_NOTE": f"SiM MARKET LAB｜{COMPANY}（{TICKER}）株価シナリオ｜作成日 {DATE}",
    }


def catalyst_values() -> dict[str, str]:
    non_quant = '<div class="priced"><div class="priced-head"><span>主要材料の推定織り込み</span><b>54%</b></div><p>仮定：Q2売上急伸の持続を60%、UAS注文拡大を55%、SpaceMDの中期価値を35%、内部統制改善を45%として置き、重複を控除しました。</p><p>読み方：防衛UASと売上成長はかなり評価されていますが、赤字、統合、内部統制の不安も残るため、織り込みは中程度です。</p><p>次に見る数字：売上、粗利率、Adjusted EBITDA、受注残、Stalker注文です。</p><p>再計算方法：売上、倍率、株式数、ネットデットを分け、株価シナリオと同じ売上倍率モデルで更新します。</p></div>'
    outcome_common = "<ul><li>目安：下の％は、この結果が出た後に市場が材料を評価し直した場合の上昇・下落幅です。</li><li>実際の値動きは地合い、直前の株価上昇、同時ニュースで変わります。</li></ul>"
    impact_map = {
        "Q2決算詳細と10-Q確認": ("+18〜40%", "-8〜+12%", "-22〜-42%", "直近の売上急伸が本物かを確認する材料で、売上倍率と赤字見通しを直接動かすため最大級です。"),
        "Stalker UASと防衛注文": ("+15〜35%", "-6〜+12%", "-18〜-35%", "防衛UASは成長期待の中心ですが、受注から売上・利益まで時間差があるため決算より少し小さめです。"),
        "SpaceMDと宇宙医薬品施設": ("+6〜18%", "-4〜+6%", "-8〜-18%", "長期テーマで短期業績への寄与が限定的なため、影響レンジは小さくしています。"),
        "内部統制と買収統合の改善": ("+8〜22%", "-6〜+8%", "-15〜-30%", "評価倍率の信頼性に効く材料ですが、売上を直接増やすものではないため中程度です。"),
    }
    description_map = {
        "Q2決算詳細と10-Q確認": "Q2決算詳細と10-Q確認は、報じられた売上急伸が利益や受注残まで伴っているかを見る材料です。赤字や希薄化の不安が残るため、売上だけでなく粗利率、Adjusted EBITDA、現金も重要です。",
        "Stalker UASと防衛注文": "Stalker UASと防衛注文は、Redwireの防衛ドローン事業が継続的な受注基盤になるかを見る材料です。追加注文、納入能力、採算がそろうと成長期待が強まります。",
        "SpaceMDと宇宙医薬品施設": "SpaceMDは宇宙環境を使った医薬品研究・製造の長期テーマです。話題性はありますが、短期売上への寄与はまだ限定的なので、顧客や商業化の具体化を確認します。",
        "内部統制と買収統合の改善": "内部統制と買収統合は、会社の数字を信頼して評価できるかに関わる材料です。売上を直接増やすものではありませんが、改善すれば評価倍率の重しが軽くなります。",
    }

    def card(title: str, date: str, chips: str, mechanism: str, success: str, inline: str, failure: str, evidence: str) -> str:
        up, flat, down, reason = impact_map[title]
        description = description_map[title]
        return f'''<article class="catalyst-card">
<div class="catalyst-head"><div><span class="pill">重要材料</span><h3>{title}</h3><div class="chips">{chips}</div></div><div class="date-box"><b>{date}</b><span>会社公表またはイベント期間</span></div></div>
<p class="lead">{description}</p>
<div class="mechanism">{mechanism}</div>
<div class="outcomes">
<div class="outcome success"><b>期待以上</b><div class="impact up">{up}</div><p>{success}</p>{outcome_common}</div>
<div class="outcome inline"><b>ほぼ想定どおり</b><div class="impact flat">{flat}</div><p>{inline}</p>{outcome_common}</div>
<div class="outcome failure"><b>期待外れ・遅延</b><div class="impact down">{down}</div><p>{failure}</p>{outcome_common}</div>
</div>
<p class="notice"><b>この％にした理由：</b>{reason}</p>
<div class="evidence"><div><h4>根拠</h4><ul>{evidence}</ul></div><div><h4>反証・先行指標</h4><ul><li>粗利率低下</li><li>受注残の伸び鈍化</li><li>内部統制の是正遅延</li></ul></div></div>
</article>'''

    cards = [
        card("Q2決算詳細と10-Q確認", "2026/08以降", '<span class="chip">重要度5</span><span class="chip blue">詳細確認待ち</span>', '<span>売上・粗利率</span><i>→</i><span>倍率</span><i>→</i><span>株価</span>', "売上だけでなく粗利率、受注残、Adjusted EBITDAも改善する状態です。", "売上は強いが、利益率と損失の改善は段階的な状態です。", "売上以外の指標が弱く、赤字や希薄化が嫌気される状態です。", "<li>Q2売上$117.07M、過去最高売上が報じられました。</li><li>公式10-Qで詳細確認が必要です。</li>"),
        card("Stalker UASと防衛注文", "2026年後半", '<span class="chip">重要度5</span><span class="chip">継続確認</span>', '<span>追加注文</span><i>→</i><span>受注残</span><i>→</i><span>売上成長</span>', "PAE RASや軍向け注文が継続し、納入能力も確認される状態です。", "追加注文は続くが、売上認識と利益貢献は段階的な状態です。", "注文減速、納入遅延、採算悪化が見える状態です。", "<li>2026年4月、Stalker UAS向け$20Mフォローオン注文を発表。</li><li>Edge Autonomy統合で防衛事業がRedwireブランドへ移行。</li>"),
        card("SpaceMDと宇宙医薬品施設", "2026-2028", '<span class="chip amber">重要度3</span><span class="chip blue">長期テーマ</span>', '<span>施設</span><i>→</i><span>実験</span><i>→</i><span>商業化</span>', "顧客・提携・収益化の道筋が具体化し、宇宙医薬品テーマが再評価される状態です。", "施設拡張と実験は進むが、売上寄与はまだ限定的な状態です。", "商業化が遅れ、テーマだけが先行したと見られる状態です。", "<li>Indiana施設の開設で宇宙医薬品R&D・製造を強化。</li><li>SpaceMDを商業化テーマとして展開。</li>"),
        card("内部統制と買収統合の改善", "2026-2027", '<span class="chip">重要度4</span><span class="chip blue">継続確認</span>', '<span>統合改善</span><i>→</i><span>信頼性</span><i>→</i><span>倍率</span>', "重要な不備の是正が進み、買収事業の管理と開示信頼性が改善する状態です。", "是正計画は進むが、完全解消には時間がかかる状態です。", "是正遅延や追加問題が出て、評価倍率が下がる状態です。", "<li>2025年10-Kで内部統制の重要な不備と是正計画を説明。</li><li>Edge Autonomy統合が事業構造の中心課題です。</li>"),
    ]
    return {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "NYSE",
        "VALUATION_DATE": DATE,
        "LAST_UPDATED": DATE,
        "REPORT_STATUS": "重要材料が集中",
        "SUMMARY_LINE_1": "Q2決算詳細、Stalker UAS、SpaceMD、内部統制改善が今後の主な材料です。",
        "SUMMARY_LINE_2": "足りない情報は仮定を置き、主要材料の織り込み度を54%と推定します。",
        "OVERALL_PRICED_IN": "54%",
        "OVERALL_PRICED_LABEL": "主要材料の推定織り込み",
        "PRICED_IN_CONFIDENCE": "ふつう",
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "2026/08/07 16:00 ET",
        "NEXT_CATALYST_TITLE": "Q2 10-Q詳細確認",
        "NEXT_CATALYST_WINDOW": "2026年8月以降",
        "DATE_CONFIDENCE": "一部確定",
        "CATALYST_COUNT": "4件",
        "WARN_BAND": "",
        "NO_CATALYST_NOTICE": "",
        "OVERALL_PRICED_BLOCK": non_quant,
        "PRICED_IN_METHOD": "未確定情報に仮定確率を置き、Q2決算、UAS注文、SpaceMD、内部統制を標準ケース価値へ重み付けして推定。",
        "SURPRISE_UP": "Q2詳細で粗利率と受注残も強く、UAS追加注文やSpaceMD提携が続くことです。",
        "SURPRISE_DOWN": "Q2詳細で損失拡大、粗利率悪化、統合遅延、希薄化が見えることです。",
        "PRIMARY_RISK": "売上急伸だけが先に評価され、利益率や統合リスクが後から嫌気される可能性です。",
        "TIMELINE_ROWS": '<div class="time-row"><div class="time-date">2026/08</div><div class="time-dot"></div><div class="time-body"><b>Q2詳細確認</b><p>10-Qで粗利率、損失、受注残、株式数を確認します。</p><div class="time-meta"><span class="chip blue">確認待ち</span></div></div></div><div class="time-row"><div class="time-date">2026後半</div><div class="time-dot"></div><div class="time-body"><b>UAS追加注文</b><p>Stalker関連の追加受注と納入進捗を確認します。</p><div class="time-meta"><span class="chip">継続材料</span></div></div></div><div class="time-row"><div class="time-date">2026-2028</div><div class="time-dot"></div><div class="time-body"><b>SpaceMD商業化</b><p>提携、施設稼働、収益化の道筋を確認します。</p><div class="time-meta"><span class="chip blue">長期</span></div></div></div>',
        "CATALYST_CARDS": "".join(cards),
        "DEPENDENCY_ROWS": '<div class="signal"><div><b>Q2詳細と倍率</b><span class="up">直結</span></div><p>売上だけでなく利益率が強いほど倍率を支えます。</p></div><div class="signal"><div><b>UAS受注とDefense</b><span class="up">連動</span></div><p>追加注文が受注残と将来売上へつながります。</p></div><div class="signal"><div><b>内部統制と信頼性</b><span class="down">注意</span></div><p>是正が遅れると評価倍率の重しになります。</p></div>',
        "WATCH_ROWS": '<div class="signal"><div><b>Q2粗利率</b><span class="up">最重要</span></div><p>売上成長が利益へ変わっているかを見ます。</p></div><div class="signal"><div><b>受注残</b><span class="up">重要</span></div><p>Q1の$498.1Mから増えたか確認します。</p></div><div class="signal"><div><b>株式数</b><span class="down">注意</span></div><p>買収や資金調達による希薄化を確認します。</p></div>',
        "ASSUMPTION_ROWS": tr("評価基準株価", usd(P0), "市場データで確認済み", DATE, "2026/08/07終値") + tr("Q2売上", "$117.07M", "市場記事で確認", "2026/08/06", "公式10-Q詳細待ち") + tr("Q1受注残", "$498.1M", "会社発表", "2026/05/06", "2026/03/31時点") + tr("Stalker注文", "$20M", "会社発表", "2026/04/14", "フォローオン注文"),
        "SOURCE_DETAILS": f'<ul><li>{source_link("Q2関連記事", "q2_article")}</li><li>{source_link("Q1決算", "q1")}</li><li>{source_link("2025年10-K", "annual")}</li><li>{source_link("Edge Autonomy統合", "edge")}</li><li>{source_link("Stalker注文", "stalker")}</li><li>{source_link("SpaceMD施設", "space_md")}</li></ul><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p>',
        "VALIDATION_DETAILS": "<p>PASS：Q1決算、10-K、Edge Autonomy統合、Stalker注文、SpaceMD施設を確認。WARN：Q2詳細は公式10-Q確認前のため、速報値として扱っています。</p>",
        "UPDATE_HISTORY": f"<p>{DATE}：初版作成。Q1決算、Q2速報、Edge Autonomy統合、Stalker注文、SpaceMD施設を反映。</p>",
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
    rdw_stock = {
        "id": "redwire-rdw",
        "order": 3,
        "ticker": "RDW",
        "quoteSymbol": "RDW",
        "name": "レッドワイヤー",
        "nameEn": "Redwire Corporation",
        "market": "US",
        "marketLabel": "米国株",
        "exchange": "NYSE",
        "currency": "USD",
        "sector": "宇宙インフラ・防衛テクノロジー",
        "reports": {
            "company": {"path": "./stocks/redwire-rdw/company.html", "available": True},
            "valuation": {"path": "./stocks/redwire-rdw/valuation.html", "available": True},
            "catalysts": {"path": "./stocks/redwire-rdw/catalysts.html", "available": True},
        },
    }
    stocks_payload["stocks"] = [stock for stock in stocks_payload["stocks"] if stock["id"] != "redwire-rdw"]
    stocks_payload["stocks"].append(rdw_stock)
    stocks_path.write_text(json.dumps(stocks_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    prices_path = ROOT / "data" / "prices.json"
    prices_payload = json.loads(prices_path.read_text(encoding="utf-8"))
    prices_payload["quoteCount"] = len(prices_payload.get("prices", {})) + (0 if "redwire-rdw" in prices_payload.get("prices", {}) else 1)
    prices_payload.setdefault("prices", {})["redwire-rdw"] = {
        "symbol": "RDW",
        "price": P0,
        "previousClose": PREVIOUS_CLOSE,
        "change": round(P0 - PREVIOUS_CLOSE, 2),
        "changePct": round((P0 - PREVIOUS_CLOSE) / PREVIOUS_CLOSE * 100, 4),
        "currency": "USD",
        "marketTime": "2026-08-07T20:00:00+00:00",
        "updatedAt": "2026-08-08T10:00:00+00:00",
        "status": "ok",
    }
    prices_path.write_text(json.dumps(prices_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    signals_path = ROOT / "data" / "signals.json"
    signals_payload = json.loads(signals_path.read_text(encoding="utf-8"))
    signals_payload["updatedAt"] = datetime.now(timezone.utc).isoformat()
    signals_payload.setdefault("signals", {})["redwire-rdw"] = {
        "position": 43.1,
        "zone": "中立",
        "asOf": DATE,
        "components": {
            "valuation": 26.0,
            "catalysts": 72.0,
            "businessRisk": 63.0,
        },
        "reportRevision": "redwire-rdw-2026-08-08",
        "summary": "Q2売上急伸、受注残、防衛UAS材料は強い一方、赤字、買収統合、内部統制、希薄化リスクが残るため中立。",
    }
    signals_path.write_text(json.dumps(signals_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_reports()
    upsert_site_data()


if __name__ == "__main__":
    main()
