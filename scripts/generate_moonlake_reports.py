"""Generate MoonLake Immunotherapeutics report HTML files from the bundled SiM templates."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from generate_rocket_lab_reports import dl, li, render_template, th, tr


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stocks" / "moonlake-mltx"

COMPANY = "ムーンレイク・イミュノセラピューティクス"
TICKER = "MLTX"
DATE = "2026-08-10"
P0 = 18.26
PREVIOUS_CLOSE = 18.03
SHARES_M = 85.1
MARKET_CAP_B = P0 * SHARES_M / 1000

BEAR = 11.00
BASE = 25.00
BULL = 42.00
BAND_POSITION = (P0 - BEAR) / (BULL - BEAR) * 100
SIGNAL_POSITION = round(0.60 * round(BAND_POSITION, 1) + 0.25 * 78.0 + 0.15 * 82.0, 1)

SOURCES = {
    "overview": "https://ir.moonlaketx.com/",
    "events": "https://ir.moonlaketx.com/events-presentations",
    "q1": "https://ir.moonlaketx.com/news-releases/news-release-details/moonlake-immunotherapeutics-announces-positive-outcome-its-final",
    "week52": "https://ir.moonlaketx.com/news-releases/news-release-details/moonlake-announces-week-52-results-sonelokimab-its-phase-3-vela",
    "offering": "https://www.globenewswire.com/news-release/2026/06/24/3316568/0/en/moonlake-immunotherapeutics-announces-pricing-of-upsized-200-million-public-offering.html",
    "quote": "https://stockanalysis.com/stocks/mltx/",
    "history": "https://uk.investing.com/equities/helix-acquisition-corp-historical-data",
}


def usd(value: int | float) -> str:
    return f"${value:,.2f}" if abs(value) < 100 else f"${value:,.0f}"


def pct(value: float) -> str:
    return f"{value * 100:+.1f}%"


def details(title: str, body: str, open_: bool = False) -> str:
    return f"<details{' open' if open_ else ''}><summary>{title}</summary><p>{body}</p></details>"


def source_link(label: str, key: str) -> str:
    return f'<a href="{SOURCES[key]}" target="_blank" rel="noopener noreferrer">{label}</a>'


def guide_values() -> dict[str, str]:
    source_details = (
        '<details class="term-item" open><summary class="term-header"><span class="term-name">主要出典</span><span class="term-arrow">⌄</span></summary>'
        '<div class="term-body"><p>'
        f'{source_link("公式IR概要", "overview")}、'
        f'{source_link("2026年1Q・Pre-BLAリリース", "q1")}、'
        f'{source_link("VELA Week 52リリース", "week52")}、'
        f'{source_link("2026年6月増資リリース", "offering")}、'
        f'{source_link("株価・統計", "quote")}を確認しました。'
        "本文の数値は2026年8月10日時点で取得できた公開情報に基づきます。"
        '</p><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p></div></details>'
    )
    terms = [
        ("Sonelokimab", "IL-17AとIL-17Fを抑えるNanobody候補です。炎症性皮膚・関節疾患が対象です。"),
        ("HS", "化膿性汗腺炎です。痛み、炎症、生活の質低下が大きい慢性皮膚疾患です。"),
        ("BLA", "米国でバイオ医薬品の承認を申請する手続きです。"),
        ("PDUFA", "FDAが審査期限を割り当てる日程です。承認時期の目安になります。"),
        ("Priority Review", "優先審査です。認められると通常より審査期間が短くなる可能性があります。"),
        ("VELA", "HS向けのPhase 3プログラムです。成人のVELA-1/2と青年向けVELA-TEENがあります。"),
        ("HiSCR75", "膿瘍・炎症性結節数の75%以上改善を測るHSの臨床評価指標です。"),
        ("IZAR", "乾癬性関節炎向けのPhase 3プログラムです。"),
        ("P-OLARIS", "PsAとaxSpAを対象に、炎症や組織ダメージを画像で見るPhase 2試験です。"),
        ("キャッシュランウェイ", "手元資金で開発を続けられる期間です。"),
        ("希薄化", "増資により1株あたり価値が薄まることです。臨床段階バイオでは重要です。"),
    ]
    return {
        "TICKER": TICKER,
        "COMPANY_NAME": COMPANY,
        "INDUSTRY": "臨床段階バイオ・免疫疾患",
        "DATE": DATE,
        "TAGLINE": "Sonelokimabを軸に、化膿性汗腺炎、乾癬性関節炎、軸性脊椎関節炎など炎症性疾患で承認と商業化を狙う臨床段階バイオ企業です。",
        "HERO_TAGS": '<span class="hero-tag">米国株</span><span class="hero-tag">バイオ</span><span class="hero-tag">免疫疾患</span><span class="hero-tag">Nasdaq</span>',
        "HERO_STATS": (
            f'<div class="stat"><div class="stat-value">{usd(P0)}</div><div class="stat-label">評価基準株価</div><div class="stat-note">2026/08/07終値</div></div>'
            f'<div class="stat"><div class="stat-value">${MARKET_CAP_B:.1f}B</div><div class="stat-label">時価総額の目安</div><div class="stat-note">約8,506万株で計算</div></div>'
            '<div class="stat"><div class="stat-value up">$357.9M</div><div class="stat-label">現金等</div><div class="stat-note">2026年1Q末</div></div>'
            '<div class="stat"><div class="stat-value">Sep 2026</div><div class="stat-label">HS BLA提出予定</div><div class="stat-note">会社予定</div></div>'
        ),
        "SEC2_LABEL": "事業モデル",
        "SEC3_LABEL": "臨床",
        "SEC4_LABEL": "資金",
        "SEC5_LABEL": "競合比較",
        "SEC1_TLDR": li("MoonLakeはSonelokimab単一資産への依存が大きい臨床段階バイオです。", "*") + li("HSではWeek 52データとPre-BLA完了により、承認申請へ進む視界が強まりました。", "*") + li("一方で商業化前の赤字企業で、承認・優先審査・販売準備・追加試験の成否で株価が大きく動きます。", "!"),
        "SEC1_FACTS": (
            "<div><dt>正式社名</dt><dd>MoonLake Immunotherapeutics AG</dd></div><div><dt>本社</dt><dd>Zug, Switzerland</dd></div>"
            "<div><dt>上場</dt><dd>Nasdaq（MLTX）</dd></div><div><dt>業種</dt><dd>バイオテクノロジー</dd></div>"
            "<div><dt>主な領域</dt><dd>HS、PsA、axSpA、PPP</dd></div><div><dt>決算期</dt><dd>12月</dd></div>"
        ),
        "SEC1_CARDS": (
            '<div class="card-sm"><span class="card-emoji">🧬</span><div class="card-title">何をしている</div><div class="card-desc">IL-17A/Fを狙うSonelokimabで免疫疾患を治療します。</div></div>'
            '<div class="card-sm"><span class="card-emoji">📄</span><div class="card-title">主役</div><div class="card-desc">HS向けBLAを2026年9月末に提出予定です。</div></div>'
            '<div class="card-sm"><span class="card-emoji">💵</span><div class="card-title">資金</div><div class="card-desc">Q1末現金等に加え、6月に約2億ドルの公募増資を発表しました。</div></div>'
            '<div class="card-sm"><span class="card-emoji">⚠️</span><div class="card-title">リスク</div><div class="card-desc">承認審査、商業化、追加適応データの失敗が主な下落要因です。</div></div>'
        ),
        "SEC1_BIZMODEL": (
            '<li><span class="kp-emoji">💊</span><span class="kp-text"><b>単一主力資産</b>：Sonelokimabを複数疾患へ展開します。</span></li>'
            '<li><span class="kp-emoji">📄</span><span class="kp-text"><b>承認申請</b>：HSで2026年9月末のBLA提出が最大イベントです。</span></li>'
            '<li><span class="kp-emoji">🏥</span><span class="kp-text"><b>商業化準備</b>：承認後の販売体制と市場浸透が価値を決めます。</span></li>'
        ),
        "SEC1_HIGHLIGHT": '<div class="highlight"><h3>MLTXを見る基本ルール</h3><p>MLTXは売上倍率より、Sonelokimabの承認確率、優先審査の有無、PsAデータ、資金余力を追う銘柄です。HSのBLA提出とFDA受理が短期の中心です。</p></div>',
        "SEC2_ICON": "🧬",
        "SEC2_TITLE": "Sonelokimabの<span class=\"g\">価値</span>",
        "SEC2_SUB": "HSから複数疾患へ広げるモデル",
        "SEC2_TLDR": li("SonelokimabはIL-17A/Fを抑えるNanobodyで、HSを最初の商業化候補にしています。", "*") + li("HSのWeek 52データでは持続性と安全性が確認されました。", "*") + li("単一資産依存が強いため、1つの規制・臨床イベントで評価が大きく変わります。", "!"),
        "SEC2_CONTENT": (
            '<p class="lead">MoonLakeはSonelokimabを複数の炎症性疾患へ横展開する企業です。最初の価値化ポイントはHSの承認申請で、その後にPsA、axSpA、PPPへ期待が広がります。</p>'
            '<div class="sowhat"><p><b>つまり</b>、MLTXは「申請・審査・適応拡大」の順に評価が進むイベントドリブン銘柄です。</p></div>'
            '<div class="term-list">'
            + details("Sonelokimab", "IL-17A/A、IL-17A/F、IL-17F/Fを阻害するNanobodyです。炎症が強い皮膚・関節疾患で使う候補です。", True)
            + details("HSでの位置づけ", "成人と青年患者データを含めたラベル提案を目指しています。承認されれば最初の商業化ドライバーになります。")
            + details("PsAへの展開", "IZAR-1/2のPhase 3読出しが、HS以外の価値を確認する材料になります。")
            + details("単一資産リスク", "Sonelokimabに依存しているため、安全性や審査で問題が出ると会社全体の評価に直撃します。")
            + "</div>"
        ),
        "SEC3_TITLE": "HS申請と<span class=\"g\">追加試験</span>",
        "SEC3_SUB": "9月末BLAと11月末PDUFA日程が焦点",
        "SEC3_TLDR": li("Pre-BLAは完了し、会社は2026年9月末のBLA提出を予定しています。", "*") + li("VELA Week 52ではHiSCR75が約67%、新たな安全性シグナルなしと説明されています。", "*") + li("優先審査が取れない場合、商業化タイミングは2027年後半想定です。", "!"),
        "SEC3_CONTENT": (
            '<div class="product-grid"><div class="product-box"><div class="product-symbol">HS</div><div class="product-name">BLA提出</div><div class="product-use">2026年9月末予定。</div></div>'
            '<div class="product-box"><div class="product-symbol">PsA</div><div class="product-name">IZAR</div><div class="product-use">Phase 3読出し。</div></div>'
            '<div class="product-box"><div class="product-symbol">P-OL</div><div class="product-name">P-OLARIS</div><div class="product-use">画像評価のPhase 2。</div></div></div>'
            '<div class="term-list">'
            + details("VELA Week 52", "成人HSの長期データで、持続的な反応と新たな安全性シグナルなしが示されました。", True)
            + details("VELA-TEEN", "青年HS患者データをBLAに含める方針で、優先審査の材料にもなります。")
            + details("PDUFA日程", "BLA受理時に審査期限と優先審査の可否が見えます。会社は2026年11月末を目安にしています。")
            + details("IZAR-1/2", "PsAで有効性が出れば、Sonelokimabの価値がHS単独から広がります。")
            + "</div>"
        ),
        "SEC4_TITLE": "資金と<span class=\"g\">希薄化</span>",
        "SEC4_SUB": "承認前バイオでは資金余力も材料",
        "SEC4_TLDR": li("Q1末の現金等は$357.9Mで、会社は2027年末までのランウェイを見込んでいます。", "*") + li("6月に約$200Mの公募増資を発表し、商業化準備資金を厚くしました。", "*") + li("増資は資金面では追い風ですが、1株価値の希薄化は短期の重しになります。", "!"),
        "SEC4_CONTENT": (
            '<ul class="keypoints"><li><span class="kp-emoji">💵</span><span class="kp-text"><b>現金等</b>：Q1末で$357.9M。</span></li>'
            '<li><span class="kp-emoji">🏦</span><span class="kp-text"><b>追加資金</b>：Hercules Capitalの非希薄化資金枠は最大$400M。</span></li>'
            '<li><span class="kp-emoji">📈</span><span class="kp-text"><b>公募増資</b>：6月に約$200Mの資金調達を発表。</span></li></ul>'
            '<div class="sowhat"><p><b>つまり</b>、承認・販売準備に必要な資金は厚くなりましたが、増資後は「資金があるか」より「承認と販売準備が前に進むか」が問われます。</p></div>'
        ),
        "SEC5_TITLE": "競合と<span class=\"g\">比べる</span>",
        "SEC5_SUB": "HS市場で差別化できるか",
        "SEC5_TLDR": li("競合は既存IL-17系薬剤、TNF阻害薬、他の皮膚・免疫疾患薬です。", "*") + li("MoonLakeはHiSCR75、HiSCR100、生活の質、痛み、安全性、投与利便性で差別化を狙います。", "*") + li("承認されても、販売立ち上げと保険償還で期待に届くかは別問題です。", "!"),
        "SEC5_CONTENT": (
            '<div class="table-wrap"><table class="compare-table"><thead><tr><th>対象</th><th>強み</th><th>注意点</th></tr></thead><tbody>'
            '<tr><td class="me">MoonLake</td><td>HSの長期データ、青年データ、Q4W投与、複数適応。</td><td>商業化前でSonelokimab依存が大きい。</td></tr>'
            '<tr><td>既存IL-17薬</td><td>承認済み実績、販売体制。</td><td>差別化余地があればMLTXの追い風。</td></tr>'
            '<tr><td>大手製薬</td><td>販売力、償還交渉力、複数製品。</td><td>成長率は限定的になりやすい。</td></tr>'
            '<tr><td>臨床段階バイオ</td><td>データ成功時の上値が大きい。</td><td>失敗時の下落と増資リスクが大きい。</td></tr>'
            '</tbody></table></div><div class="highlight"><h3>差別化の見方</h3><p>MLTXは「承認できるか」だけでなく、HSでどれだけ強いラベルを取れるか、PsAで次の柱を作れるかが評価の分かれ目です。</p></div>'
        ),
        "SEC6_TLDR": li("Sonelokimab、HS、BLA、PDUFA、IZAR、希薄化を押さえると読みやすいです。", "*") + li("売上よりも規制イベントと臨床データが重要です。", "*") + li("9月末BLAと11月末の審査日程確認が短期の山場です。", "!"),
        "SEC6_CONTENT": '<div class="term-list">' + "".join(details(name, body) for name, body in terms) + "</div>",
        "SEC7_TLDR": li("最大材料はHSのBLA提出とFDA受理・優先審査判断です。", "*") + li("PsAのIZARデータは、HS以外の上値を作る材料です。", "*") + li("審査遅延、安全性、商業化準備不足、追加増資には注意です。", "!"),
        "SEC7_CONTENT": (
            '<div class="timeline"><div class="tl-row"><div class="tl-date">2026/05/10</div><div class="tl-title">Pre-BLA完了とQ1決算 <span class="signal bull">追い風</span></div><div class="tl-desc">FDAとの申請方針が整理され、Q1末現金等は$357.9M。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/06/21</div><div class="tl-title">VELA Week 52 <span class="signal bull">データ</span></div><div class="tl-desc">HiSCR75約67%、新たな安全性シグナルなしと説明。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/06/23</div><div class="tl-title">約$200M公募増資 <span class="signal neutral">資金</span></div><div class="tl-desc">商業化準備資金は厚くなる一方、希薄化は短期の重し。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/09末</div><div class="tl-title">HS BLA提出予定 <span class="signal bull">最重要</span></div><div class="tl-desc">提出完了と受理が次の株価材料。</div></div></div>'
            '<div class="info-row"><div class="info-box info-box-green"><div class="info-title info-title-green">追い風</div><div class="info-text">Week 52データ、Pre-BLA完了、資金調達、適応拡大。</div></div>'
            '<div class="info-box info-box-amber"><div class="info-title info-title-amber">確認</div><div class="info-text">BLA提出、優先審査、PsA読出し、販売準備。</div></div>'
            '<div class="info-box info-box-red"><div class="info-title info-title-red">リスク</div><div class="info-text">審査遅延、安全性、商業化失敗、希薄化。</div></div></div>'
            + source_details
        ),
    }


def scenario_values() -> dict[str, str]:
    probs = {"bear": 0.28, "base": 0.47, "bull": 0.25}
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
        "METHOD": "臨床段階バイオ向けリスク調整シナリオ",
        "VERDICT_STATUS": "申請前の高リスク中立",
        "VERDICT_LINE_1": f"評価基準株価は悲観〜楽観レンジの{BAND_POSITION:.1f}%地点です。HS承認申請の進展は上値材料ですが、審査・商業化・単一資産依存のリスクも大きい局面です。",
        "VERDICT_LINE_2": "この試算は2026年8月10日時点で取得できた公開情報に基づきます。BLA提出、PDUFA日程、PsAデータで更新が必要です。",
        "SCORE": str(score),
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "2026/08/07終値",
        "BASE_PRICE": usd(BASE),
        "BASE_DELTA": pct(BASE / P0 - 1),
        "EXPECTED_VALUE": usd(expected),
        "EXPECTED_DELTA": pct(expected / P0 - 1),
        "RISK_CLASS": "高",
        "RISK_NOTE": "承認申請前の臨床段階バイオ",
        "WARN_BAND": '<div class="wrap"><div class="notice" style="margin-top:14px"><b>注意：</b>MLTXは臨床段階バイオです。FDA審査、治験結果、資金調達、商業化計画で株価が大きく変動します。</div></div>',
        "WARN_MESSAGE": "承認申請前の臨床段階バイオのため、通常のPER評価ではなくイベント確率で見ます。",
        "SNAPSHOT_LEAD": "今の株価は悲観寄りです。HSのBLA提出・受理を一部織り込む一方、承認審査と販売立ち上げの不確実性も残っています。",
        "BAND_POSITION": f"{BAND_POSITION:.1f}%",
        "ZONE_JUDGE": "悲観寄りの中立圏",
        "ZONE_NOTE": "BLAが予定通り進めば標準側へ、遅延や審査懸念が出れば悲観側へ寄ります。",
        "BEAR_PRICE": usd(BEAR),
        "BULL_PRICE": usd(BULL),
        "ENDPOINT_RR": f"{endpoint_rr:.1f}倍",
        "MARKET_SCORE": str(round(BAND_POSITION)),
        "OWN_SCORE": str(round(own_score)),
        "MARKET_REVERSE_NOTE": "このモデルで逆算すると、市場はHS承認申請の進展を評価しつつも、商業化前・単一資産依存・希薄化を強く割り引いています。",
        "SCENARIOS_LEAD": "現在株価から独立して、HS承認確率、PsA拡大余地、資金余力、商業化前リスクを置きました。",
        "BEAR_PROB": "28%",
        "BASE_PROB": "47%",
        "BULL_PROB": "25%",
        "BEAR_DELTA": pct(BEAR / P0 - 1),
        "BULL_DELTA": pct(BULL / P0 - 1),
        "BEAR_DL_ROWS": dl([("HS BLA", "遅延・受理懸念"), ("PsA", "弱いデータ"), ("資金", "追加希薄化懸念"), ("株価", usd(BEAR))]),
        "BASE_DL_ROWS": dl([("HS BLA", "予定通り提出・受理"), ("PsA", "一定の有効性"), ("資金", "商業化準備に十分"), ("株価", usd(BASE))]),
        "BULL_DL_ROWS": dl([("HS BLA", "優先審査期待"), ("PsA", "強いデータ"), ("販売準備", "高評価"), ("株価", usd(BULL))]),
        "PRICE_ZONE_ROWS": '<div class="zone"><div><b>$11未満</b><span>★★★</span></div><p>申請遅延や安全性懸念を強く織り込む価格帯です。</p></div><div class="zone"><div><b>$11〜$25</b><span>★★★</span></div><p>申請前の中立圏。今の株価はここです。</p></div><div class="zone"><div><b>$25〜$42</b><span>★★</span></div><p>BLA進展とPsA成功を評価し始める価格帯です。</p></div><div class="zone"><div><b>$42超</b><span>★</span></div><p>優先審査、強いPsA、商業化期待が同時に必要です。</p></div>',
        "SIGNAL_ROWS": '<div class="signal"><div><b>HS BLA提出</b><span class="up">最重要</span></div><p>2026年9月末予定の提出完了が最大材料です。</p></div><div class="signal"><div><b>PDUFA日程</b><span class="up">確認</span></div><p>11月末見込みの受理・優先審査判断を確認します。</p></div><div class="signal"><div><b>PsAデータ</b><span class="up">上値</span></div><p>IZARの読出しがHS以外の価値を左右します。</p></div><div class="signal"><div><b>希薄化</b><span class="down">注意</span></div><p>公募増資後も追加資金調達リスクは監視します。</p></div>',
        "POSITIVES": "<li>HSのWeek 52データで持続性と安全性が示されました。</li><li>Pre-BLA完了により、申請方針が具体化しています。</li><li>6月の増資で商業化準備資金が厚くなりました。</li><li>PsA、axSpA、PPPへ適応拡大余地があります。</li>",
        "CONCERNS": "<li>商業化前で売上はまだありません。</li><li>Sonelokimabへの依存が大きいです。</li><li>FDA審査や優先審査の結果で評価が大きく変わります。</li><li>増資による希薄化が株価の重しになります。</li>",
        "FORMULA": "臨床段階バイオのため、短期利益倍率ではなく、承認申請と適応拡大の成功確率を反映した悲観・標準・楽観シナリオで見ました。",
        "CALC_TABLE_HEAD": th("ケース", "主な前提", "価値の見方", "計算株価", "確率", "確率加重"),
        "CALC_TABLE_ROWS": tr("悲観", "BLA遅延・PsA弱い", "現金価値と限定的パイプライン", usd(BEAR), "28%", "$3.08") + tr("標準", "BLA提出・受理", "HS承認期待を中心に評価", usd(BASE), "47%", "$11.75") + tr("楽観", "優先審査・PsA強い", "複数適応と商業化を評価", usd(BULL), "25%", "$10.50"),
        "CALC_NOTICE": "現在株価に合わせた逆算ではありません。申請・審査・追加データの成否で評価レンジが大きく変わる前提です。",
        "CONDITIONS": details("悲観ケース：$11.00 / 確率28%", "BLA提出や受理に遅れが出る、またはPsAデータが弱く、承認後の市場浸透にも疑問が残るケースです。", True) + details("標準ケース：$25.00 / 確率47%", "HS BLAが予定通り提出・受理され、優先審査は不確定ながら承認期待が保たれるケースです。") + details("楽観ケース：$42.00 / 確率25%", "優先審査期待が高まり、PsAデータも強く、HS以外の価値も上乗せされるケースです。"),
        "SENSITIVITY_HEAD": th("前提", "弱い", "標準", "強い"),
        "SENSITIVITY_ROWS": tr("HS承認確率", "遅延・追加照会 → $11", "予定通り受理 → $25", "優先審査期待 → $42") + tr("PsA価値", "失敗・遅延", "一部評価", "複数適応の柱") + tr("資金評価", "追加希薄化懸念", "2027年末まで余力", "商業化準備を評価"),
        "SENSITIVITY_NOTE": "臨床バイオでは、1つの規制イベントで成功確率と倍率が同時に動きます。",
        "DIST_LEAD": "モンテカルロではなく、申請前イベントの3点分布です。",
        "DIST_ROWS": '<div class="dist-row"><span>$11</span><div class="track"><i style="width:28%"></i></div><b>28%</b></div><div class="dist-row"><span>$25</span><div class="track"><i style="width:47%"></i></div><b>47%</b></div><div class="dist-row"><span>$42</span><div class="track"><i style="width:25%"></i></div><b>25%</b></div>',
        "DIST_SUMMARY": "期待値は標準ケース寄りですが、実際の株価はBLA受理とPsAデータで上下に振れやすいです。",
        "WATCH_ROWS": '<div class="signal"><div><b>HS BLA提出</b></div><p>予定通り2026年9月末に提出されるかを確認します。</p></div><div class="signal"><div><b>FDA受理・優先審査</b></div><p>11月末見込みのPDUFA日程とPriority Reviewの可否を確認します。</p></div><div class="signal"><div><b>IZAR-1/2</b></div><p>PsAの有効性、安全性、競合比較を確認します。</p></div>',
        "ASSUMPTIONS_ROWS": tr("評価基準株価", usd(P0), "市場データで確認", DATE, "2026/08/07終値") + tr("現金等", "$357.9M", "会社Q1リリース", "2026/03/31", "短期市場性債券含む") + tr("公募増資", "約$200M", "会社リリース", "2026/06/23", "商業化準備資金") + tr("HS BLA", "2026年9月末予定", "会社リリース", "2026/06/21", "最大材料"),
        "DEEPDIVE_DETAILS": details("手法選定理由", "MLTXは商業化前の臨床段階バイオです。PERではなく、申請・審査・適応拡大の確率を反映したシナリオ法を使います。", True) + details("優先審査について", "Priority Reviewは上振れ材料ですが、FDA判断次第です。取れない場合でも会社は2027年後半の米国ローンチを想定しています。") + details("主要出典", f'{source_link("Q1・Pre-BLAリリース", "q1")}、{source_link("VELA Week 52", "week52")}、{source_link("増資リリース", "offering")}、{source_link("株価・統計", "quote")}。<br><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>'),
        "DISCLAIMER": "本資料は情報提供を目的とした試算です。投資助言ではありません。臨床段階バイオは治験結果、規制、資金調達で大きく変動します。",
        "FOOTER_NOTE": f"SiM MARKET LAB｜{COMPANY}（{TICKER}）株価シナリオ｜作成日 {DATE}",
    }


def catalyst_values() -> dict[str, str]:
    non_quant = '<div class="priced"><div class="priced-head"><span>主要材料の推定織り込み</span><b>42%</b></div><p>仮定：HS BLA提出期待を55%、PDUFA日程・優先審査期待を35%、PsA読出し期待を30%、商業化準備と資金余力を45%として置き、単一資産依存と希薄化を控除しました。</p><p>読み方：株価はHS承認申請の進展をある程度織り込んでいますが、申請前・商業化前のため期待はまだ半分未満です。提出と受理が進めば上振れ、遅延や審査懸念なら下振れです。</p><p>次に見る数字：BLA提出日、PDUFA日程、Priority Reviewの可否、IZARデータ、現金残高、営業費用です。</p><p>再計算方法：各材料の成功確率を更新し、レポート2のシナリオ株価を再計算します。</p></div>'
    impact_map = {
        "HS BLA提出": ("+18〜35%", "-6〜+10%", "-20〜-40%", "承認申請へ進むかどうかで標準ケースへの確度が直接変わるため、大きめにしています。"),
        "FDA受理・Priority Review判断": ("+25〜55%", "-10〜+15%", "-25〜-45%", "審査期間と初回ローンチ時期の見方が変わるため、BLA提出後の最大材料です。"),
        "IZAR-1/2 PsAデータ": ("+30〜75%", "-12〜+18%", "-30〜-55%", "HS単独企業から複数適応企業へ評価が広がるかを決めるため、上振れも下振れも大きいです。"),
        "資金余力・商業化準備": ("+10〜22%", "-5〜+8%", "-12〜-28%", "承認されても販売体制と資金が弱いと価値化が遅れるため、中程度の影響にしています。"),
    }
    description_map = {
        "HS BLA提出": "HS向けBLA提出は、Sonelokimabが臨床データの段階から承認審査の段階へ進むイベントです。提出が予定通り行われるほど、承認期待の確度が上がります。",
        "FDA受理・Priority Review判断": "BLA受理とPDUFA日程の割当は、審査の時計が正式に動き出す確認です。Priority Reviewが認められれば、ローンチ時期の前倒し期待が出ます。",
        "IZAR-1/2 PsAデータ": "PsAデータはSonelokimabがHS以外でも価値を持つかを確認する材料です。良い結果なら市場規模とパイプライン価値の見方が広がります。",
        "資金余力・商業化準備": "6月の公募増資で資金は厚くなりましたが、販売体制、医師への浸透、保険償還の準備が進むかで承認後の価値化スピードが変わります。",
    }

    def card(title: str, date: str, chips: str, mechanism: str, success: str, inline: str, failure: str, evidence: str) -> str:
        up, flat, down, reason = impact_map[title]
        description = description_map[title]
        return f'''<article class="catalyst-card">
<div class="catalyst-head"><div><span class="pill">重要材料</span><h3>{title}</h3><div class="chips">{chips}</div></div><div class="date-box"><b>{date}</b><span>会社公表または予定</span></div></div>
<p class="lead">{description}</p>
<div class="mechanism">{mechanism}</div>
<div class="outcomes">
<div class="outcome success"><b>期待以上</b><div class="impact up">{up}</div><p>{success}</p></div>
<div class="outcome inline"><b>ほぼ想定どおり</b><div class="impact flat">{flat}</div><p>{inline}</p></div>
<div class="outcome failure"><b>期待外れ・遅延</b><div class="impact down">{down}</div><p>{failure}</p></div>
</div>
<p class="notice"><b>この％にした理由：</b>{reason}</p>
<div class="evidence"><div><h4>根拠</h4><ul>{evidence}</ul></div><div><h4>反証・先行指標</h4><ul><li>予定日の後ろ倒し</li><li>安全性やCMCへの追加照会</li><li>商業化費用の急増</li></ul></div></div>
</article>'''

    cards = [
        card("HS BLA提出", "2026年9月末", '<span class="chip">重要度5</span><span class="chip">最重要</span>', '<span>提出</span><i>→</i><span>審査入り</span><i>→</i><span>承認確率</span>', "予定通り提出され、青年データも含む強いラベル案が示される状態です。", "予定どおり提出だが、追加確認待ちが残る状態です。", "提出遅延や資料不足が出ると、承認時期の見方が後ろ倒しになります。", "<li>会社はHS BLAを2026年9月末に提出予定と説明。</li><li>Pre-BLAで申請方針とラベル戦略が整理されました。</li>"),
        card("FDA受理・Priority Review判断", "2026年11月末見込み", '<span class="chip">重要度5</span><span class="chip blue">規制</span>', '<span>受理</span><i>→</i><span>PDUFA</span><i>→</i><span>ローンチ時期</span>', "受理に加えて優先審査が認められれば、承認・販売開始の前倒し期待が出ます。", "受理されるが通常審査なら、2027年後半ローンチ期待が中心です。", "受理遅延や追加資料要求が出れば、株価は審査リスクを織り込みます。", "<li>会社はBLA受理とPDUFA日程の割当を2026年11月末見込みと説明。</li><li>Priority ReviewはFDA判断次第の上振れ材料です。</li>"),
        card("IZAR-1/2 PsAデータ", "2026年中", '<span class="chip">重要度4</span><span class="chip blue">適応拡大</span>', '<span>PsA有効性</span><i>→</i><span>市場拡大</span><i>→</i><span>評価レンジ</span>', "ACR50などで強い有効性と安全性が出れば、複数適応の価値が上乗せされます。", "一定の有効性なら、HS承認待ちの補助材料です。", "弱いデータなら、HS単独依存が強まり評価レンジが下がります。", "<li>会社はIZAR-1とIZAR-2のPhase 3読出しを2026年の重要予定に挙げています。</li><li>PsAはSonelokimabの横展開を確認する材料です。</li>"),
        card("資金余力・商業化準備", "2026年後半", '<span class="chip">重要度3</span><span class="chip blue">資金</span>', '<span>資金</span><i>→</i><span>販売準備</span><i>→</i><span>希薄化リスク</span>', "増資後の資金で販売準備が進み、追加希薄化懸念が薄れる状態です。", "資金は十分だが費用増も続き、承認待ちになる状態です。", "商業化費用が想定以上に膨らむと、追加資金調達懸念が出ます。", "<li>Q1末現金等は$357.9M、会社は2027年末までのランウェイを見込み。</li><li>6月に約$200Mの公募増資を発表しました。</li>"),
    ]
    return {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "Nasdaq",
        "VALUATION_DATE": DATE,
        "LAST_UPDATED": DATE,
        "REPORT_STATUS": "申請前",
        "SUMMARY_LINE_1": "HS BLA提出、FDA受理・Priority Review判断、PsAデータ、商業化準備が主な材料です。",
        "SUMMARY_LINE_2": "足りない情報は仮定を置き、主要材料の織り込み度を42%と推定します。",
        "OVERALL_PRICED_IN": "42%",
        "OVERALL_PRICED_LABEL": "主要材料の推定織り込み",
        "PRICED_IN_CONFIDENCE": "低〜中",
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "2026/08/07終値",
        "NEXT_CATALYST_TITLE": "HS BLA提出",
        "NEXT_CATALYST_WINDOW": "2026年9月末",
        "DATE_CONFIDENCE": "会社予定",
        "CATALYST_COUNT": "4件",
        "WARN_BAND": "",
        "NO_CATALYST_NOTICE": "",
        "OVERALL_PRICED_BLOCK": non_quant,
        "PRICED_IN_METHOD": "未確定情報に仮定確率を置き、HS BLA、FDA受理、PsAデータ、資金・商業化準備を標準ケース価値へ重み付けして推定。",
        "SURPRISE_UP": "BLAが予定通り提出・受理され、Priority Reviewが認められ、PsAデータも強いことです。",
        "SURPRISE_DOWN": "BLA提出遅延、FDA追加照会、PsAデータ失敗、商業化費用の急増です。",
        "PRIMARY_RISK": "Sonelokimab単一資産への依存が大きく、規制・安全性・商業化のどこかでつまずくと株価下落が大きくなりやすいことです。",
        "TIMELINE_ROWS": '<div class="time-row"><div class="time-date">2026/05/10</div><div class="time-dot"></div><div class="time-body"><b>Pre-BLA完了・Q1決算</b><p>FDAとの申請方針を整理。Q1末現金等は$357.9M。</p><div class="time-meta"><span class="chip">公表済み</span></div></div></div><div class="time-row"><div class="time-date">2026/06/21</div><div class="time-dot"></div><div class="time-body"><b>VELA Week 52</b><p>HiSCR75約67%、新たな安全性シグナルなし。</p><div class="time-meta"><span class="chip blue">データ</span></div></div></div><div class="time-row"><div class="time-date">2026/09末</div><div class="time-dot"></div><div class="time-body"><b>HS BLA提出予定</b><p>申請段階へ進む最大材料。</p><div class="time-meta"><span class="chip">最重要</span></div></div></div><div class="time-row"><div class="time-date">2026/11末</div><div class="time-dot"></div><div class="time-body"><b>PDUFA日程・優先審査判断見込み</b><p>承認時期の見方が具体化します。</p><div class="time-meta"><span class="chip">規制</span></div></div></div>',
        "CATALYST_CARDS": "".join(cards) + '<p class="small">※下の％は、この結果が出た後に市場が材料を評価し直した場合の上昇・下落幅の目安です。実際の値動きは地合い、直前の株価上昇、同時ニュースで変わります。</p>',
        "DEPENDENCY_ROWS": '<div class="signal"><div><b>BLA提出とFDA受理</b><span class="up">連動</span></div><p>提出後に受理されて初めて審査スケジュールが見えます。</p></div><div class="signal"><div><b>Priority Reviewとローンチ</b><span class="flat">時期</span></div><p>優先審査の有無で販売開始期待が前後します。</p></div><div class="signal"><div><b>PsAと評価レンジ</b><span class="up">拡大</span></div><p>HS以外の価値が見えると標準ケースが上がります。</p></div>',
        "WATCH_ROWS": '<div class="signal"><div><b>BLA提出日</b><span class="up">最重要</span></div><p>9月末までに提出できるかを確認します。</p></div><div class="signal"><div><b>PDUFA日程</b><span class="flat">必須</span></div><p>受理・審査期限・優先審査の可否を確認します。</p></div><div class="signal"><div><b>PsA読出し</b><span class="up">重要</span></div><p>IZAR-1/2の有効性、安全性、競合比較を確認します。</p></div><div class="signal"><div><b>資金消費</b><span class="flat">注意</span></div><p>販売準備費用と追加資金調達リスクを確認します。</p></div>',
        "ASSUMPTION_ROWS": tr("評価基準株価", usd(P0), "市場データで確認", DATE, "2026/08/07終値") + tr("現金等", "$357.9M", "会社Q1リリース", "2026/03/31", "短期市場性債券含む") + tr("公募増資", "約$200M", "会社リリース", "2026/06/23", "希薄化も考慮") + tr("HS BLA", "2026年9月末予定", "会社リリース", "2026/06/21", "最大材料"),
        "SOURCE_DETAILS": f'<ul><li>{source_link("公式IR概要", "overview")}</li><li>{source_link("2026年1Q・Pre-BLAリリース", "q1")}</li><li>{source_link("VELA Week 52リリース", "week52")}</li><li>{source_link("2026年6月増資リリース", "offering")}</li><li>{source_link("株価・統計", "quote")}</li></ul><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p>',
        "VALIDATION_DETAILS": "<p>PASS：公式IR、Q1・Pre-BLAリリース、VELA Week 52、増資リリース、株価・統計ページを確認。WARN：Yahoo Finance APIは429応答だったため、株価初期値は複数の株価ページで確認した2026/08/07終値を使用し、更新スクリプトで再取得対象にします。</p>",
        "UPDATE_HISTORY": f"<p>{DATE}：初版作成。Q1 2026、Pre-BLA完了、VELA Week 52、6月増資、9月末BLA提出予定、11月末PDUFA日程見込みを反映。</p>",
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
        "id": "moonlake-mltx",
        "order": 8,
        "ticker": "MLTX",
        "quoteSymbol": "MLTX",
        "name": "ムーンレイク・イミュノセラピューティクス",
        "nameEn": "MoonLake Immunotherapeutics AG",
        "market": "US",
        "marketLabel": "米国株",
        "exchange": "Nasdaq",
        "currency": "USD",
        "sector": "臨床段階バイオ・免疫疾患",
        "reports": {
            "company": {"path": "./stocks/moonlake-mltx/company.html", "available": True},
            "valuation": {"path": "./stocks/moonlake-mltx/valuation.html", "available": True},
            "catalysts": {"path": "./stocks/moonlake-mltx/catalysts.html", "available": True},
        },
    }
    stocks_payload["stocks"] = [item for item in stocks_payload["stocks"] if item["id"] != "moonlake-mltx"]
    stocks_payload["stocks"].append(stock)
    stocks_payload["stocks"].sort(key=lambda item: item["order"])
    stocks_path.write_text(json.dumps(stocks_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    prices_path = ROOT / "data" / "prices.json"
    prices_payload = json.loads(prices_path.read_text(encoding="utf-8"))
    prices_payload.setdefault("prices", {})["moonlake-mltx"] = {
        "symbol": "MLTX",
        "price": P0,
        "previousClose": PREVIOUS_CLOSE,
        "change": round(P0 - PREVIOUS_CLOSE, 2),
        "changePct": round((P0 - PREVIOUS_CLOSE) / PREVIOUS_CLOSE * 100, 4),
        "currency": "USD",
        "marketTime": "2026-08-07T20:00:00+00:00",
        "updatedAt": "2026-08-10T00:00:00+00:00",
        "status": "ok",
    }
    prices_payload["quoteCount"] = len(prices_payload["prices"])
    prices_path.write_text(json.dumps(prices_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    signals_path = ROOT / "data" / "signals.json"
    signals_payload = json.loads(signals_path.read_text(encoding="utf-8"))
    signals_payload["updatedAt"] = datetime.now(timezone.utc).isoformat()
    signals_payload.setdefault("signals", {})["moonlake-mltx"] = {
        "position": SIGNAL_POSITION,
        "zone": "中立",
        "asOf": DATE,
        "components": {
            "valuation": round(BAND_POSITION, 1),
            "catalysts": 78.0,
            "businessRisk": 82.0,
        },
        "reportRevision": "moonlake-mltx-2026-08-10",
        "summary": "HS BLA提出とFDA受理が最大材料。Week 52と資金調達は支えだが、商業化前・単一資産依存のため中立。",
    }
    signals_path.write_text(json.dumps(signals_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_reports()
    upsert_site_data()


if __name__ == "__main__":
    main()
