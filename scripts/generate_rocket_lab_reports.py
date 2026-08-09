"""Generate Rocket Lab report HTML files from the bundled SiM templates."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATERIALS = ROOT.parent / "report-generation-materials"
OUT_DIR = ROOT / "stocks" / "rocket-lab-rklb"

COMPANY = "ロケット・ラボ"
TICKER = "RKLB"
DATE = "2026-08-08"
P0 = 82.83
SHARES_M = 629.0
MARKET_CAP_B = P0 * SHARES_M / 1000

SOURCES = {
    "q1": "https://investors.rocketlabcorp.com/news-releases/news-release-details/rocket-lab-announces-first-quarter-2026-financial-results",
    "annual": "https://www.sec.gov/Archives/edgar/data/1819994/000181999426000013/rklb-20251231.htm",
    "ir": "https://investors.rocketlabcorp.com/",
    "presentations": "https://investors.rocketlabcorp.com/events-presentations/presentations",
    "iridium": "https://investors.rocketlabcorp.com/news-releases/news-release-details/rocket-lab-acquire-iridium-historic-deal-creating-fully",
    "space_force": "https://investors.rocketlabcorp.com/news",
    "sda": "https://investors.rocketlabcorp.com/news-releases/news-release-details/rocket-lab-achieves-milestone-missile-defense-constellation",
    "q2_date": "https://investors.rocketlabcorp.com/news-releases/news-release-details/rocket-lab-announces-date-second-quarter-2026-financial-results",
}


def usd(value: int | float) -> str:
    return f"${value:,.2f}" if value < 100 else f"${value:,.0f}"


def tr(*cells: str) -> str:
    return "<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>"


def th(*cells: str) -> str:
    return "".join(f"<th>{cell}</th>" for cell in cells)


def dl(rows: list[tuple[str, str]]) -> str:
    return "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in rows)


def li(text: str, emoji: str = "*") -> str:
    return f'<li data-emoji="{emoji}">{text}</li>'


def details(title: str, body: str, open_: bool = False) -> str:
    return f"<details{' open' if open_ else ''}><summary>{title}</summary><p>{body}</p></details>"


def source_link(label: str, key: str) -> str:
    return f'<a href="{SOURCES[key]}" target="_blank" rel="noopener noreferrer">{label}</a>'


def strip_comments(html: str) -> str:
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    html = re.sub(r"/\*.*?\*/", "", html, flags=re.S)
    return html.replace("{{ }}", "プレースホルダー")


def render_template(name: str, values: dict[str, str]) -> str:
    template = (MATERIALS / name).read_text(encoding="utf-8")
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    template = strip_comments(template)
    template = template.replace("ドパガキ株価シナリオ", "株価シナリオ")
    leftovers = sorted(set(re.findall(r"{{[A-Z0-9_]+}}", template)))
    if leftovers:
        raise RuntimeError(f"{name}: unresolved placeholders: {leftovers}")
    return template


def guide_values() -> dict[str, str]:
    source_details = (
        '<details class="term-item" open><summary class="term-header"><span class="term-name">主要出典</span><span class="term-arrow">⌄</span></summary>'
        '<div class="term-body"><p>'
        f'{source_link("2026年1Q決算リリース", "q1")}、'
        f'{source_link("2025年Form 10-K", "annual")}、'
        f'{source_link("Rocket Lab投資家向けサイト", "ir")}、'
        f'{source_link("Iridium買収発表", "iridium")}、'
        f'{source_link("SDA Tranche 3進捗", "sda")}を確認しました。'
        "本文の数値は2026年8月8日時点の公開情報に基づきます。"
        '</p><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p></div></details>'
    )
    terms = [
        ("Electron", "Rocket Labの小型軌道ロケットです。小型衛星を専用打ち上げしやすいことが強みです。"),
        ("HASTE", "Electronをベースにしたサブオービタル試験用ロケットです。極超音速・ミサイル防衛関連の試験で使われます。"),
        ("Neutron", "開発中の中型ロケットです。大型コンステレーションや国家安全保障向けの打ち上げ市場を狙います。"),
        ("Space Systems", "衛星本体、部品、ソフトウェア、オンオービット管理などの宇宙システム事業です。"),
        ("Backlog", "受注残です。将来売上に変わる可能性がある契約残高を示します。"),
        ("Gross Margin", "売上総利益率です。打ち上げと宇宙システムの採算改善を見る指標です。"),
        ("Adjusted EBITDA", "一時費用や株式報酬などを調整した利益指標です。GAAP損益とは分けて見ます。"),
        ("SDA", "米国宇宙開発庁です。ミサイル警戒・追跡などの宇宙インフラ案件で重要顧客です。"),
        ("TRKT3", "SDA Tracking Layer Tranche 3の略です。Rocket Labは約8.16億ドル規模の受注を得ています。"),
        ("Iridium", "衛星通信会社です。Rocket Labは2026年6月、買収合意を発表しました。"),
        ("Liquidity", "現金などの手元流動性です。Rocket Labは1Q後に20億ドル超へのアクセスを示しました。"),
        ("Dilution", "増資や転換証券により1株あたり価値が薄まることです。成長投資企業では重要です。"),
    ]
    return {
        "TICKER": TICKER,
        "COMPANY_NAME": COMPANY,
        "INDUSTRY": "宇宙輸送・宇宙システム",
        "DATE": DATE,
        "TAGLINE": "小型ロケットElectron、開発中の中型ロケットNeutron、衛星・部品・ソフトウェアをまとめて提供する宇宙インフラ企業です。",
        "HERO_TAGS": '<span class="hero-tag">宇宙輸送</span><span class="hero-tag">衛星製造</span><span class="hero-tag">防衛宇宙</span><span class="hero-tag">Nasdaq</span>',
        "HERO_STATS": (
            f'<div class="stat"><div class="stat-value">{usd(P0)}</div><div class="stat-label">評価基準株価</div><div class="stat-note">2026/08/07終値</div></div>'
            f'<div class="stat"><div class="stat-value">${MARKET_CAP_B:.1f}B</div><div class="stat-label">時価総額の目安</div><div class="stat-note">Q2会社見通し株式数で計算</div></div>'
            '<div class="stat"><div class="stat-value up">$200.3M</div><div class="stat-label">2026年1Q売上</div><div class="stat-note">前年比+63.5%</div></div>'
            '<div class="stat"><div class="stat-value">$2.2B</div><div class="stat-label">受注残</div><div class="stat-note">2026年1Q末</div></div>'
        ),
        "SEC2_LABEL": "事業モデル",
        "SEC3_LABEL": "ロケット",
        "SEC4_LABEL": "宇宙システム",
        "SEC5_LABEL": "競合比較",
        "SEC1_TLDR": li("Rocket Labは打ち上げと衛星システムを両方持つ宇宙インフラ企業です。", "*") + li("2026年1Qは売上$200.3M、受注残$2.2Bと成長が続きました。", "*") + li("まだ赤字で、Neutron、買収、希薄化、政府契約の実行が株価を大きく動かします。", "!"),
        "SEC1_FACTS": (
            "<div><dt>正式社名</dt><dd>Rocket Lab Corporation</dd></div><div><dt>本社</dt><dd>Long Beach, California</dd></div>"
            "<div><dt>上場</dt><dd>Nasdaq（RKLB）</dd></div><div><dt>創業</dt><dd>2006年</dd></div>"
            "<div><dt>CEO</dt><dd>Sir Peter Beck</dd></div><div><dt>事業</dt><dd>Launch Services / Space Systems</dd></div>"
        ),
        "SEC1_CARDS": (
            '<div class="card-sm"><span class="card-emoji">🚀</span><div class="card-title">何をしている</div><div class="card-desc">ElectronやHASTEで打ち上げサービスを提供します。</div></div>'
            '<div class="card-sm"><span class="card-emoji">🛰️</span><div class="card-title">もう一つの柱</div><div class="card-desc">衛星、部品、ソフトウェア、オンオービット管理も提供します。</div></div>'
            '<div class="card-sm"><span class="card-emoji">📈</span><div class="card-title">直近業績</div><div class="card-desc">2026年1Q売上は$200.3M、GAAP粗利率は38.2%です。</div></div>'
            '<div class="card-sm"><span class="card-emoji">🛡️</span><div class="card-title">注目点</div><div class="card-desc">SDA、HASTE、Space Force案件など国家安全保障向けが拡大しています。</div></div>'
        ),
        "SEC1_BIZMODEL": (
            '<li><span class="kp-emoji">🚀</span><span class="kp-text"><b>打ち上げ</b>：Electron、HASTE、将来のNeutronで顧客衛星や試験ペイロードを運びます。</span></li>'
            '<li><span class="kp-emoji">🛰️</span><span class="kp-text"><b>宇宙システム</b>：衛星、部品、太陽電池、ソフトウェア、運用まで広く提供します。</span></li>'
            '<li><span class="kp-emoji">📄</span><span class="kp-text"><b>受注残</b>：政府・商業契約が将来売上の見通しを作ります。</span></li>'
        ),
        "SEC1_HIGHLIGHT": '<div class="highlight"><h3>RKLBを見る基本ルール</h3><p>売上成長だけでなく、粗利率、受注残の消化、Neutronの開発、買収による希薄化と統合リスクを同時に見ます。宇宙テーマ株として期待が先行しやすい点も重要です。</p></div>',
        "SEC2_ICON": "🛰️",
        "SEC2_TITLE": "事業モデルの<span class=\"g\">基本</span>",
        "SEC2_SUB": "LaunchだけでなくSpace Systemsが大きい",
        "SEC2_TLDR": li("Rocket Labはロケット会社であり、衛星システム会社でもあります。", "*") + li("2026年1Qは製品売上$127.5M、サービス売上$72.9Mでした。", "*") + li("利益化には売上規模拡大と固定費吸収が必要です。", "!"),
        "SEC2_CONTENT": (
            '<p class="lead">Rocket Labは、ロケット打ち上げだけでなく、衛星製造、部品、地上ソフトウェア、運用まで提供します。宇宙へ行く手段と宇宙で使うハードの両方を持つ点が特徴です。</p>'
            '<div class="sowhat"><p><b>つまり</b>、RKLBは「打ち上げ回数」だけでなく「宇宙システムの大型契約」と「粗利率改善」を見る銘柄です。</p></div>'
            '<div class="term-list">'
            + details("Launch Services", "Electron、HASTE、将来のNeutronによる打ち上げサービスです。顧客は商業、政府、国家安全保障分野です。", True)
            + details("Space Systems", "衛星本体、太陽電池、センサー、ソフトウェア、通信部品などを提供する事業です。大型政府契約で存在感が増しています。")
            + details("Backlog", "受注残は将来売上の候補です。ただし納期、原価、契約変更により利益への変わり方は変動します。")
            + details("赤字の意味", "成長投資、研究開発、買収統合、Neutron開発で費用が先行しています。売上成長が粗利とEBITDAに変わるかが焦点です。")
            + "</div>"
        ),
        "SEC3_TITLE": "ロケットと<span class=\"g\">打ち上げ</span>",
        "SEC3_SUB": "Electron、HASTE、Neutronを分けて見る",
        "SEC3_TLDR": li("Electronは小型衛星打ち上げで実績があります。", "*") + li("HASTEはミサイル防衛・極超音速試験の需要に結びつきます。", "*") + li("Neutronは中型ロケット市場へ入るための大きな賭けです。", "!"),
        "SEC3_CONTENT": (
            '<div class="product-grid"><div class="product-box"><div class="product-symbol">EL</div><div class="product-name">Electron</div><div class="product-use">小型衛星向けの主力ロケット。</div></div>'
            '<div class="product-box"><div class="product-symbol">HS</div><div class="product-name">HASTE</div><div class="product-use">サブオービタル試験・防衛用途。</div></div>'
            '<div class="product-box"><div class="product-symbol">NT</div><div class="product-name">Neutron</div><div class="product-use">中型打ち上げ市場向けに開発中。</div></div></div>'
            '<div class="term-list">'
            + details("Electron", "小型衛星を専用軌道へ運ぶロケットです。2026年8月時点で多数のミッション実績があります。", True)
            + details("HASTE", "Electron派生のサブオービタルロケットです。2026年7月にSpace Force向け$266M契約が公表されました。")
            + details("Neutron", "中型ロケットです。開発成功なら市場規模は広がりますが、遅延やコスト超過は株価リスクです。")
            + details("打ち上げの収益性", "打ち上げ回数、再使用性、固定費、失敗リスク、保険・顧客信頼が収益性に影響します。")
            + "</div>"
        ),
        "SEC4_TITLE": "宇宙システムと<span class=\"g\">防衛案件</span>",
        "SEC4_SUB": "大型政府契約が成長の柱",
        "SEC4_TLDR": li("SDA案件はRocket Labを宇宙システムの主契約企業へ近づけます。", "*") + li("Mynaric買収やIridium買収合意で垂直統合を進めています。", "*") + li("買収は成長加速と同時に統合・資金調達リスクもあります。", "!"),
        "SEC4_CONTENT": (
            '<ul class="keypoints"><li><span class="kp-emoji">🛡️</span><span class="kp-text"><b>SDA</b>：TRKT3で約$816M、Transport Layer Betaで約$515Mの受注実績があります。</span></li>'
            '<li><span class="kp-emoji">🔦</span><span class="kp-text"><b>Mynaric</b>：レーザー光通信端末の買収で衛星部品の幅を広げました。</span></li>'
            '<li><span class="kp-emoji">📡</span><span class="kp-text"><b>Iridium</b>：2026年6月、$54/株の現金・株式取引で買収合意を発表しました。</span></li></ul>'
            '<div class="sowhat"><p><b>つまり</b>、Rocket Labは「ロケットを飛ばす会社」から「宇宙インフラをまとめて作る会社」へ広げようとしています。</p></div>'
        ),
        "SEC5_TITLE": "競合と<span class=\"g\">比べる</span>",
        "SEC5_SUB": "大型企業とスタートアップの間にいる",
        "SEC5_TLDR": li("競合はSpaceX、Northrop、Lockheed、Firefly、Astraなどです。", "*") + li("Rocket Labは実績ある小型打ち上げと宇宙システムの垂直統合が強みです。", "*") + li("規模では大手に劣り、Neutronでは実績づくりがこれからです。", "!"),
        "SEC5_CONTENT": (
            '<div class="table-wrap"><table class="compare-table"><thead><tr><th>企業</th><th>主な強み</th><th>注意点</th></tr></thead><tbody>'
            '<tr><td class="me">Rocket Lab</td><td>Electron実績、Space Systems、政府案件、垂直統合。</td><td>赤字、Neutron未実証、希薄化。</td></tr>'
            '<tr><td>SpaceX</td><td>大型打ち上げ、再使用、Starlink規模。</td><td>非上場または別評価軸で直接比較しづらい。</td></tr>'
            '<tr><td>Lockheed / Northrop</td><td>防衛契約、資本力、政府関係。</td><td>成長率は大型成熟企業として見られやすい。</td></tr>'
            '<tr><td>Fireflyなど</td><td>新興打ち上げ・防衛宇宙分野。</td><td>実績、資金力、契約消化力の確認が必要。</td></tr>'
            '</tbody></table></div><div class="highlight"><h3>差別化の見方</h3><p>Rocket Labは、小型打ち上げで実績を作りながら、衛星システムと防衛宇宙へ広げています。Neutronが成功すれば評価軸は大きく変わります。</p></div>'
        ),
        "SEC6_TLDR": li("Electron、HASTE、Neutron、Backlogの意味を押さえると読みやすいです。", "*") + li("宇宙システム案件は売上規模を作る一方、実行リスクもあります。", "*") + li("Adjusted EBITDAはGAAP赤字と分けて見ます。", "!"),
        "SEC6_CONTENT": '<div class="term-list">' + "".join(details(name, body) for name, body in terms) + "</div>",
        "SEC7_TLDR": li("Q2決算、Neutron進捗、Iridium買収の承認・統合が大きな材料です。", "*") + li("HASTEとSDA案件は防衛宇宙テーマを支えます。", "*") + li("高い評価倍率、赤字、希薄化が下落リスクです。", "!"),
        "SEC7_CONTENT": (
            '<div class="timeline"><div class="tl-row"><div class="tl-date">2026/08/10</div><div class="tl-title">Q2決算予定 <span class="signal bull">重要</span></div><div class="tl-desc">会社はQ2売上$225M〜$240Mを見込んでいます。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026後半</div><div class="tl-title">HASTE / Space Force契約 <span class="signal bull">追い風</span></div><div class="tl-desc">$266M契約。最初の打ち上げは2026年末以降予定です。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026-2027</div><div class="tl-title">Iridium買収とNeutron <span class="signal neutral">確認</span></div><div class="tl-desc">成長加速の可能性と、統合・資金調達・開発遅延リスクを同時に見ます。</div></div></div>'
            '<div class="info-row"><div class="info-box info-box-green"><div class="info-title info-title-green">追い風</div><div class="info-text">受注残$2.2B、Q2売上見通し、SDA・HASTE契約。</div></div>'
            '<div class="info-box info-box-amber"><div class="info-title info-title-amber">確認</div><div class="info-text">Neutron開発、Iridium買収条件、粗利率とEBITDA改善。</div></div>'
            '<div class="info-box info-box-red"><div class="info-title info-title-red">リスク</div><div class="info-text">高い評価倍率、赤字継続、希薄化、打ち上げ失敗。</div></div></div>'
            + source_details
        ),
    }


def scenario_values() -> dict[str, str]:
    bear, base, bull = 48.0, 88.0, 130.0
    probs = {"bear": 0.25, "base": 0.50, "bull": 0.25}
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
        "EXCHANGE": "Nasdaq",
        "VALUATION_DATE": DATE,
        "METHOD": "高成長宇宙インフラ向け売上倍率シナリオ",
        "VERDICT_STATUS": "期待先行の中立圏",
        "VERDICT_LINE_1": "評価基準株価は悲観〜楽観レンジの42.5%地点です。Q1成長と受注残は強い一方、現在株価はすでに高い成長を織り込んでいます。",
        "VERDICT_LINE_2": "この試算は2026年8月8日時点の公開情報で固定しています。Q2決算は2026年8月10日発表予定のため、未反映です。",
        "SCORE": str(score),
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "2026/08/07 16:00 ET",
        "BASE_PRICE": usd(base),
        "BASE_DELTA": "+6.2%",
        "EXPECTED_VALUE": usd(expected),
        "EXPECTED_DELTA": "+6.8%",
        "RISK_CLASS": "高い",
        "RISK_NOTE": "成長期待と赤字・希薄化が同居",
        "WARN_BAND": '<div class="wrap"><div class="notice" style="margin-top:14px"><b>注意：</b>Q2決算は2026年8月10日予定です。このページは直前時点の会社見通しと公開資料に基づく暫定版です。</div></div>',
        "SNAPSHOT_LEAD": "今の株価は、強い受注残、防衛宇宙需要、NeutronとIridiumの期待をかなり評価しています。ただし、楽観ケースを完全に織り込む水準ではありません。",
        "BAND_POSITION": f"{band:.1f}%",
        "ZONE_JUDGE": "標準ケースの少し下",
        "ZONE_NOTE": "Q2実績とNeutron進捗が良ければ標準〜楽観側へ寄ります。",
        "BEAR_PRICE": usd(bear),
        "BULL_PRICE": usd(bull),
        "ENDPOINT_RR": f"{endpoint_rr:.1f}倍",
        "MARKET_SCORE": str(round(band)),
        "OWN_SCORE": str(round(own_score)),
        "MARKET_REVERSE_NOTE": "このモデルで逆算すると、今の株価は2028年売上約$1.7B、EV/Sales約30倍前後、またはそれに近い成長期待を織り込む水準です。市場全体の予想ではなく、このモデル上の逆算です。",
        "SCENARIOS_LEAD": "現在株価から独立して、2028年ごろの売上規模、粗利率、Neutron/Space Systemsの進捗、評価倍率を置きました。赤字企業のためPERではなく売上倍率を主に使います。",
        "BEAR_PROB": "25%",
        "BASE_PROB": "50%",
        "BULL_PROB": "25%",
        "BEAR_DELTA": "-42.1%",
        "BULL_DELTA": "+57.0%",
        "BEAR_DL_ROWS": dl([("2028年売上", "$1.2B"), ("EV/Sales", "22倍"), ("前提", "Neutron遅延・倍率低下"), ("株式数", "約6.29億株")]),
        "BASE_DL_ROWS": dl([("2028年売上", "$1.7B"), ("EV/Sales", "30倍"), ("前提", "Q2達成・防衛宇宙堅調"), ("株式数", "約6.29億株")]),
        "BULL_DL_ROWS": dl([("2028年売上", "$2.2B"), ("EV/Sales", "36倍"), ("前提", "Neutron成功・Iridium統合進展"), ("株式数", "約6.29億株")]),
        "PRICE_ZONE_ROWS": (
            '<div class="zone"><div><b>$48未満</b><span>★★★★</span></div><p>悲観ケース以下。成長鈍化や市場倍率低下をかなり織り込む価格帯です。</p></div>'
            '<div class="zone"><div><b>$48〜$88</b><span>★★★</span></div><p>標準ケース手前。今の株価はこの範囲です。</p></div>'
            '<div class="zone"><div><b>$88〜$130</b><span>★★</span></div><p>Q2達成、Neutron、買収統合の成功をかなり評価する価格帯です。</p></div>'
            '<div class="zone"><div><b>$130超</b><span>★</span></div><p>楽観ケース超。さらに強い売上加速と倍率維持が必要です。</p></div>'
        ),
        "SIGNAL_ROWS": (
            '<div class="signal"><div><b>Q2売上見通し</b><span class="up">追い風</span></div><p>会社は$225M〜$240Mを見込んでいます。</p></div>'
            '<div class="signal"><div><b>受注残$2.2B</b><span class="up">追い風</span></div><p>将来売上の見通しを支えます。</p></div>'
            '<div class="signal"><div><b>Iridium買収</b><span class="flat">確認</span></div><p>規模拡大と統合・資金調達リスクが同時にあります。</p></div>'
            '<div class="signal"><div><b>Neutron</b><span class="down">注意</span></div><p>成功なら大きい一方、遅延やコスト超過は下落要因です。</p></div>'
        ),
        "POSITIVES": "<li>2026年1Q売上は$200.3M、前年比+63.5%でした。</li><li>受注残は$2.2Bで、Q2売上見通しは$225M〜$240Mです。</li><li>SDA、HASTE、Space Force契約で防衛宇宙の実績が増えています。</li><li>Iridium買収が成立すれば、通信ネットワークと宇宙インフラの統合が進みます。</li>",
        "CONCERNS": "<li>GAAPではまだ赤字です。2026年1Q純損失は$45.0Mでした。</li><li>現在株価は売上倍率が高く、少しの失望で大きく下がり得ます。</li><li>Iridium買収は承認、資金調達、統合リスクがあります。</li><li>Neutron開発、打ち上げ失敗、政府予算変更、希薄化がリスクです。</li>",
        "FORMULA": "主計算は売上倍率です。赤字成長企業のため、短期PERよりも将来売上とEV/Salesを使いました。",
        "CALC_TABLE_HEAD": th("ケース", "2028年売上", "EV/Sales", "計算株価", "確率", "確率加重"),
        "CALC_TABLE_ROWS": tr("悲観", "$1.2B", "22倍", usd(bear), "25%", "$12.00") + tr("標準", "$1.7B", "30倍", usd(base), "50%", "$44.00") + tr("楽観", "$2.2B", "36倍", usd(bull), "25%", "$32.50"),
        "CALC_NOTICE": "市場の正確な予想ではなく、公開情報から置いた条件付きシナリオです。買収、希薄化、ネットキャッシュ、Neutron進捗で大きく変わります。",
        "CONDITIONS": details("悲観ケース：$48 / 確率25%", "Q2は達成するが、Neutron遅延、Iridium統合不安、成長株倍率低下が重なるケースです。", True) + details("標準ケース：$88 / 確率50%", "Q2会社見通しをおおむね達成し、SDA・HASTE・Space Systemsが順調に伸びるケースです。") + details("楽観ケース：$130 / 確率25%", "Neutron進捗、Iridium統合、防衛宇宙の大型契約が重なり、倍率が高く保たれるケースです。"),
        "SENSITIVITY_HEAD": th("前提", "弱い", "標準", "強い"),
        "SENSITIVITY_ROWS": tr("2028年売上", "$1.4B → $69", "$1.7B → $88", "$2.0B → $106") + tr("EV/Sales", "24倍 → $63", "30倍 → $88", "36倍 → $113"),
        "SENSITIVITY_NOTE": "1変数だけを動かした簡易感応度です。実際には売上成長と倍率が同時に動きます。",
        "DIST_LEAD": "モンテカルロではなく、悲観・標準・楽観の3点分布です。",
        "DIST_ROWS": '<div class="dist-row"><span>$48</span><div class="track"><i style="width:25%"></i></div><b>25%</b></div><div class="dist-row"><span>$88</span><div class="track"><i style="width:50%"></i></div><b>50%</b></div><div class="dist-row"><span>$130</span><div class="track"><i style="width:25%"></i></div><b>25%</b></div>',
        "DIST_SUMMARY": "中心は標準ケースです。ただし宇宙テーマ株として、ニュースと倍率で両端へ大きく振れやすい銘柄です。",
        "WATCH_ROWS": '<div class="signal"><div><b>2026年Q2決算</b></div><p>売上$225M〜$240M、粗利率、Adjusted EBITDA損失幅を確認します。</p></div><div class="signal"><div><b>Neutron開発</b></div><p>試験、初号機、顧客契約、コスト超過の有無を見ます。</p></div><div class="signal"><div><b>Iridium買収</b></div><p>承認、資金調達、統合計画、希薄化を確認します。</p></div>',
        "ASSUMPTIONS_ROWS": tr("評価基準株価", usd(P0), "市場データで確認済み", "2026/08/07終値") + tr("Q2売上見通し", "$225M〜$240M", "会社の目標・予定", "2026/05/07") + tr("Q1売上", "$200.3M", "公式情報で確認済み", "2026年1〜3月") + tr("Q2株式数目安", "629M", "会社見通し", "Series A preferred含む"),
        "DEEPDIVE_DETAILS": details("手法選定理由", "Rocket Labは高成長ですがGAAP赤字です。短期PERではなく、将来売上とEV/Salesを主に使いました。", True) + details("希薄化について", "Q2会社見通しでは基本加重平均株式数629Mが示されています。買収や資金調達で将来株式数は変わり得ます。") + details("主要出典", f'{source_link("Q1決算", "q1")}、{source_link("2025年10-K", "annual")}、{source_link("Iridium買収", "iridium")}、{source_link("SDA進捗", "sda")}、{source_link("投資家向けサイト", "ir")}。<br><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>'),
        "DISCLAIMER": "本資料は情報提供を目的とした試算です。投資助言ではありません。宇宙・防衛関連の成長株は、契約、開発、資金調達、市場倍率により大きく変動します。",
        "FOOTER_NOTE": f"SiM MARKET LAB｜{COMPANY}（{TICKER}）株価シナリオ｜作成日 {DATE}",
    }


def catalyst_values() -> dict[str, str]:
    non_quant = (
        '<div class="priced"><div class="priced-head"><span>主要材料の推定織り込み</span><b>72%</b></div>'
        '<p>仮定：Q2決算の達成を70%、Neutron進捗を65%、Iridium買収成立を60%、防衛契約の継続拡大を75%として置き、材料の重複を控除しました。</p>'
        '<p>読み方：株価はすでに強い成長期待をかなり含みます。好材料でも内容が想定内なら上値は限定されやすく、Neutron遅延や買収条件悪化には敏感です。</p>'
        '<p>次に見る数字：Q2売上、粗利率、Adjusted EBITDA、受注残、Neutron進捗、買収条件です。</p>'
        '<p>再計算方法：材料ごとの成功確率を更新し、売上倍率モデルの標準ケースに対する織り込み度として再計算します。</p></div>'
    )
    outcome_common = "<ul><li>数値化手法A〜Eを検討。</li><li>このページでは条件付き売上倍率再計算を主に使用。</li></ul>"

    def card(title: str, date: str, chips: str, mechanism: str, success: str, inline: str, failure: str, evidence: str) -> str:
        return f'''<article class="catalyst-card">
<div class="catalyst-head"><div><span class="pill">重要材料</span><h3>{title}</h3><div class="chips">{chips}</div></div><div class="date-box"><b>{date}</b><span>会社公表またはイベント期間</span></div></div>
<div class="mechanism">{mechanism}</div>
<div class="outcomes">
<div class="outcome success"><b>期待以上</b><div class="impact up">+15〜30%</div><p>{success}</p>{outcome_common}</div>
<div class="outcome inline"><b>ほぼ想定どおり</b><div class="impact flat">-7〜+8%</div><p>{inline}</p>{outcome_common}</div>
<div class="outcome failure"><b>期待外れ・遅延</b><div class="impact down">-20〜-40%</div><p>{failure}</p>{outcome_common}</div>
</div>
<div class="evidence"><div><h4>根拠</h4><ul>{evidence}</ul></div><div><h4>反証・先行指標</h4><ul><li>粗利率低下</li><li>受注残の伸び鈍化</li><li>開発日程の後ろ倒し</li></ul></div></div>
</article>'''

    cards = [
        card(
            "2026年Q2決算",
            "2026/08/10",
            '<span class="chip">重要度5</span><span class="chip">日程確定</span>',
            '<span>売上・粗利率</span><i>→</i><span>倍率維持</span><i>→</i><span>株価</span>',
            "売上がガイダンス上限を超え、粗利率とAdjusted EBITDAも改善する状態です。",
            "売上$225M〜$240Mの範囲で、利益改善はまだ段階的な状態です。",
            "売上未達、粗利率悪化、費用増が見える状態です。",
            "<li>Q1決算でQ2売上$225M〜$240Mの会社見通しを開示。</li><li>Q2決算日は2026年8月10日と公表。</li>",
        ),
        card(
            "Iridium買収の承認・統合",
            "2026-2027",
            '<span class="chip">重要度5</span><span class="chip blue">条件付き</span>',
            '<span>買収成立</span><i>→</i><span>売上規模</span><i>→</i><span>CF改善</span>',
            "承認が進み、資金調達と統合計画が明確になり、キャッシュフロー改善期待が高まる状態です。",
            "買収合意は維持されるが、承認・統合の詳細確認待ちの状態です。",
            "承認遅延、条件変更、希薄化懸念、統合コスト増が見える状態です。",
            "<li>2026年6月29日、Iridiumを$54/株の現金・株式取引で買収する合意を発表。</li><li>会社は売上規模とキャッシュフローへの寄与を説明。</li>",
        ),
        card(
            "Neutron開発と初回打ち上げへの道筋",
            "2026-2027",
            '<span class="chip">重要度5</span><span class="chip blue">期間のみ</span>',
            '<span>開発進捗</span><i>→</i><span>大型市場</span><i>→</i><span>倍率</span>',
            "主要試験が順調に進み、初号機日程と顧客契約がより明確になる状態です。",
            "進捗は出るが、商業化までは追加確認が必要な状態です。",
            "大幅遅延、コスト増、顧客契約の後ろ倒しが見える状態です。",
            "<li>会社はNeutronを中型打ち上げ市場向けの重要開発として位置づけています。</li><li>Q1では専用Neutron打ち上げ契約5件の追加を説明。</li>",
        ),
        card(
            "HASTE / Space Force $266M契約",
            "2026年末以降",
            '<span class="chip">重要度4</span><span class="chip">契約公表済み</span>',
            '<span>防衛契約</span><i>→</i><span>受注残</span><i>→</i><span>信頼性</span>',
            "初回ミッションが順調に始まり、追加オプションや類似契約につながる状態です。",
            "契約通りに進むが、売上認識と利益貢献は段階的な状態です。",
            "打ち上げ遅延、技術問題、採算懸念が出る状態です。",
            "<li>2026年7月、Space Force向け$266Mの複数打ち上げ契約が公表されました。</li><li>12回、追加最大6回のサブオービタル打ち上げが対象です。</li>",
        ),
    ]
    return {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "Nasdaq",
        "VALUATION_DATE": DATE,
        "LAST_UPDATED": DATE,
        "REPORT_STATUS": "重要材料が集中",
        "SUMMARY_LINE_1": "Q2決算、Iridium買収、Neutron、HASTE/Space Force契約が今後の主な材料です。",
        "SUMMARY_LINE_2": "足りない情報は仮定を置き、主要材料の織り込み度を72%と推定します。",
        "OVERALL_PRICED_IN": "72%",
        "OVERALL_PRICED_LABEL": "主要材料の推定織り込み",
        "PRICED_IN_CONFIDENCE": "中〜高",
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "2026/08/07 16:00 ET",
        "NEXT_CATALYST_TITLE": "2026年Q2決算",
        "NEXT_CATALYST_WINDOW": "2026/08/10",
        "DATE_CONFIDENCE": "日程確定",
        "CATALYST_COUNT": "4件",
        "WARN_BAND": "",
        "NO_CATALYST_NOTICE": "",
        "OVERALL_PRICED_BLOCK": non_quant,
        "PRICED_IN_METHOD": "未確定情報に仮定確率を置き、Q2決算、Neutron、Iridium、防衛契約を標準ケース価値へ重み付けして推定。",
        "SURPRISE_UP": "Q2上振れ、Neutron進捗、Iridium承認、HASTE追加契約が重なることです。",
        "SURPRISE_DOWN": "Q2未達、粗利率悪化、Neutron遅延、買収条件への懸念です。",
        "PRIMARY_RISK": "期待が高く、好材料が出ても織り込み済みと判断される可能性です。",
        "TIMELINE_ROWS": (
            '<div class="time-row"><div class="time-date">2026/08/10</div><div class="time-dot"></div><div class="time-body"><b>Q2決算</b><p>売上、粗利率、Adjusted EBITDA、受注残を確認します。</p><div class="time-meta"><span class="chip">日程確定</span></div></div></div>'
            '<div class="time-row"><div class="time-date">2026年末以降</div><div class="time-dot"></div><div class="time-body"><b>HASTE契約の初回打ち上げ</b><p>Space Force契約の実行開始を確認します。</p><div class="time-meta"><span class="chip blue">予定</span></div></div></div>'
            '<div class="time-row"><div class="time-date">2026-2027</div><div class="time-dot"></div><div class="time-body"><b>Iridium買収</b><p>承認、資金調達、統合計画を確認します。</p><div class="time-meta"><span class="chip blue">条件付き</span></div></div></div>'
            '<div class="time-row"><div class="time-date">2026-2027</div><div class="time-dot"></div><div class="time-body"><b>Neutron進捗</b><p>試験、初回打ち上げ、顧客契約を確認します。</p><div class="time-meta"><span class="chip blue">期間のみ</span></div></div></div>'
        ),
        "CATALYST_CARDS": "".join(cards),
        "DEPENDENCY_ROWS": '<div class="signal"><div><b>Q2決算と倍率</b><span class="up">直結</span></div><p>売上と粗利率が期待を上回るほど高い倍率を支えやすくなります。</p></div><div class="signal"><div><b>Iridiumと希薄化</b><span class="flat">同時確認</span></div><p>規模拡大と資金調達の影響を分けて見る必要があります。</p></div><div class="signal"><div><b>Neutronと契約</b><span class="up">連動</span></div><p>開発進捗が大型打ち上げ契約の信頼性に影響します。</p></div>',
        "WATCH_ROWS": '<div class="signal"><div><b>売上成長率</b><span class="up">最重要</span></div><p>Q2会社見通しの上限を超えるか見ます。</p></div><div class="signal"><div><b>GAAP粗利率</b><span class="up">重要</span></div><p>売上成長が利益へ変わっているかを確認します。</p></div><div class="signal"><div><b>受注残</b><span class="flat">確認</span></div><p>大型契約が将来売上へ積み上がっているかを見ます。</p></div><div class="signal"><div><b>株式数</b><span class="down">注意</span></div><p>買収や資金調達による希薄化を確認します。</p></div>',
        "ASSUMPTION_ROWS": tr("評価基準株価", usd(P0), "市場データで確認済み", DATE, "2026/08/07終値") + tr("Q2売上見通し", "$225M〜$240M", "会社の目標・予定", "2026/05/07", "2026年4〜6月") + tr("Iridium買収", "$54/株", "会社発表", "2026/06/29", "承認・完了は未反映") + tr("Space Force契約", "$266M", "会社発表", "2026/07/27", "初回は2026年末以降予定"),
        "SOURCE_DETAILS": f'<ul><li>{source_link("Q1決算", "q1")}</li><li>{source_link("2025年10-K", "annual")}</li><li>{source_link("Iridium買収", "iridium")}</li><li>{source_link("Space Force契約", "space_force")}</li><li>{source_link("SDA進捗", "sda")}</li><li>{source_link("Q2決算日程", "q2_date")}</li></ul><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p>',
        "VALIDATION_DETAILS": "<p>PASS：Q1決算、Q2日程、Iridium買収、SDA進捗、HASTE契約を確認。WARN：Q2決算は2026年8月10日予定のため、実績は未反映です。</p>",
        "UPDATE_HISTORY": f"<p>{DATE}：初版作成。Q1決算、Q2日程、Iridium買収、SDA進捗、Space Force契約を反映。</p>",
        "DISCLAIMER": "本資料は情報提供を目的とした整理です。投資助言ではありません。カタリストの影響率は条件付き試算であり、短期株価を予測するものではありません。",
        "FOOTER_NOTE": f"SiM MARKET LAB｜{COMPANY}（{TICKER}）カタリスト｜作成日 {DATE}",
    }


def write_reports() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "company.html").write_text(render_template("template_stock_guide_v4_unified.html", guide_values()), encoding="utf-8")
    (OUT_DIR / "valuation.html").write_text(render_template("template_scenario_v4_unified.html", scenario_values()), encoding="utf-8")
    (OUT_DIR / "catalysts.html").write_text(render_template("template_catalyst_v1_unified.html", catalyst_values()), encoding="utf-8")


def update_site_data() -> None:
    stocks_path = ROOT / "data" / "stocks.json"
    stocks = json.loads(stocks_path.read_text(encoding="utf-8"))
    for stock in stocks["stocks"]:
        if stock["id"] == "rocket-lab-rklb":
            for report in stock["reports"].values():
                report["available"] = True
    stocks_path.write_text(json.dumps(stocks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    signals_path = ROOT / "data" / "signals.json"
    signals = json.loads(signals_path.read_text(encoding="utf-8"))
    signals["updatedAt"] = datetime.now(timezone.utc).isoformat()
    signals["signals"]["rocket-lab-rklb"] = {
        "position": 54.8,
        "zone": "中立",
        "asOf": DATE,
        "components": {
            "valuation": 42.5,
            "catalysts": 74.0,
            "businessRisk": 72.0,
        },
        "reportRevision": "rocket-lab-rklb-2026-08-08",
        "summary": "Q1成長、受注残、防衛宇宙材料は強い一方、現在株価は高い成長期待と買収・Neutronリスクを織り込むため中立。",
    }
    signals_path.write_text(json.dumps(signals, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_reports()
    update_site_data()


if __name__ == "__main__":
    main()
