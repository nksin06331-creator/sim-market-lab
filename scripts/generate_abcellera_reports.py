"""Generate AbCellera report HTML files from the bundled SiM templates."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from generate_rocket_lab_reports import dl, li, render_template, th, tr


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stocks" / "abcellera-abcl"

COMPANY = "アブセレラ"
TICKER = "ABCL"
DATE = "2026-08-09"
P0 = 5.19
PREVIOUS_CLOSE = 5.25
SHARES_M = 303.1
MARKET_CAP_B = P0 * SHARES_M / 1000

BEAR = 3.50
BASE = 7.00
BULL = 11.00
BAND_POSITION = (P0 - BEAR) / (BULL - BEAR) * 100
SIGNAL_POSITION = round(0.60 * round(BAND_POSITION, 1) + 0.25 * 74.0 + 0.15 * 78.0, 1)

SOURCES = {
    "overview": "https://investors.abcellera.com/overview/",
    "quarterly": "https://investors.abcellera.com/financials/quarterly-results/default.aspx",
    "q1": "https://investors.abcellera.com/news/news-releases/2026/AbCellera-Reports-Q1-2026-Business-Results--Announces-Positive-Interim-Phase-1-Clinical-Data-for-ABCL635/default.aspx",
    "q2_date": "https://investors.abcellera.com/news/news-releases/2026/AbCellera-to-Report-Second-Quarter-2026-Financial-Results-on-August-5-2026/default.aspx",
    "sec_q1": "https://www.sec.gov/Archives/edgar/data/1703057/000170305726000028/abcl-20260331.htm",
    "news": "https://investors.abcellera.com/news/default.aspx",
    "quote": "https://www.investing.com/equities/abcellera-biologics-historical-data",
}


def usd(value: int | float) -> str:
    return f"${value:,.2f}" if abs(value) < 100 else f"${value:,.0f}"


def details(title: str, body: str, open_: bool = False) -> str:
    return f"<details{' open' if open_ else ''}><summary>{title}</summary><p>{body}</p></details>"


def source_link(label: str, key: str) -> str:
    return f'<a href="{SOURCES[key]}" target="_blank" rel="noopener noreferrer">{label}</a>'


def guide_values() -> dict[str, str]:
    source_details = (
        '<details class="term-item" open><summary class="term-header"><span class="term-name">主要出典</span><span class="term-arrow">⌄</span></summary>'
        '<div class="term-body"><p>'
        f'{source_link("公式IR概要", "overview")}、'
        f'{source_link("四半期決算資料", "quarterly")}、'
        f'{source_link("2026年1Q決算リリース", "q1")}、'
        f'{source_link("2026年2Q発表日リリース", "q2_date")}、'
        f'{source_link("SEC 10-Q", "sec_q1")}、'
        f'{source_link("株価時系列", "quote")}を確認しました。'
        "本文の数値は2026年8月9日時点で取得できた公開情報に基づきます。"
        '</p><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p></div></details>'
    )
    terms = [
        ("抗体創薬", "抗体を使った医薬品候補を発見・開発する領域です。"),
        ("臨床段階バイオ", "製品売上よりも治験データ、資金残高、パートナー契約が評価材料になります。"),
        ("ABCL635", "更年期の血管運動症状を対象にしたNK3R抗体候補です。2026年Q3のPhase 2データが注目です。"),
        ("ABCL575", "炎症・免疫系を狙う臨床プログラムです。初期段階のため安全性と薬効シグナルが焦点です。"),
        ("ABCL688", "IND/CTA申請前の開発候補です。次の臨床入りが材料になります。"),
        ("ABCL386", "IND/CTA申請前の開発候補です。パイプライン厚みの確認材料です。"),
        ("下流権利", "提携先が開発を進めた場合、マイルストンやロイヤルティを受け取る権利です。"),
        ("流動性", "現金、現金同等物、有価証券、利用可能な政府資金を合わせた資金余力です。"),
        ("Phase 1", "主に安全性、忍容性、薬物動態を確認する初期試験です。"),
        ("Phase 2", "対象患者で有効性の初期確認を行う試験です。バイオ株では株価材料になりやすい段階です。"),
        ("Jazz提携", "2026年6月に発表された多重特異性抗体探索の提携です。"),
        ("キャッシュバーン", "研究開発と運営で現金が減る速度です。資金調達リスクを見る指標です。"),
    ]
    return {
        "TICKER": TICKER,
        "COMPANY_NAME": COMPANY,
        "INDUSTRY": "抗体創薬・臨床段階バイオ",
        "DATE": DATE,
        "TAGLINE": "AIと実験基盤を使って抗体医薬を発見し、自社パイプラインと提携プログラムの両方で価値化を狙う臨床段階バイオ企業です。",
        "HERO_TAGS": '<span class="hero-tag">米国株</span><span class="hero-tag">バイオ</span><span class="hero-tag">抗体創薬</span><span class="hero-tag">Nasdaq</span>',
        "HERO_STATS": (
            f'<div class="stat"><div class="stat-value">{usd(P0)}</div><div class="stat-label">評価基準株価</div><div class="stat-note">取得可能な直近株価</div></div>'
            f'<div class="stat"><div class="stat-value">${MARKET_CAP_B:.1f}B</div><div class="stat-label">時価総額の目安</div><div class="stat-note">約3.03億株で計算</div></div>'
            '<div class="stat"><div class="stat-value up">$655M</div><div class="stat-label">利用可能流動性</div><div class="stat-note">2026年1Q末</div></div>'
            '<div class="stat"><div class="stat-value">Q3 2026</div><div class="stat-label">重要読出し</div><div class="stat-note">ABCL635 Phase 2予定</div></div>'
        ),
        "SEC2_LABEL": "事業モデル",
        "SEC3_LABEL": "パイプライン",
        "SEC4_LABEL": "提携",
        "SEC5_LABEL": "競合比較",
        "SEC1_TLDR": li("AbCelleraは抗体創薬プラットフォームから、自社開発型の臨床段階バイオへ移行中です。", "*") + li("2026年1Q末の利用可能流動性は約$655Mで、資金余力は大きいです。", "*") + li("ABCL635のPhase 2データが2026年Q3の最大材料です。", "!"),
        "SEC1_FACTS": (
            "<div><dt>正式社名</dt><dd>AbCellera Biologics Inc.</dd></div><div><dt>本社</dt><dd>Vancouver, British Columbia</dd></div>"
            "<div><dt>上場</dt><dd>Nasdaq（ABCL）</dd></div><div><dt>業種</dt><dd>バイオテクノロジー</dd></div>"
            "<div><dt>主な領域</dt><dd>内分泌、女性ヘルス、免疫、がん</dd></div><div><dt>決算期</dt><dd>12月</dd></div>"
        ),
        "SEC1_CARDS": (
            '<div class="card-sm"><span class="card-emoji">🧬</span><div class="card-title">何をしている</div><div class="card-desc">抗体医薬候補を発見し、自社開発と提携で価値化します。</div></div>'
            '<div class="card-sm"><span class="card-emoji">💊</span><div class="card-title">主役</div><div class="card-desc">ABCL635は更年期症状向けのNK3R抗体候補です。</div></div>'
            '<div class="card-sm"><span class="card-emoji">💵</span><div class="card-title">資金力</div><div class="card-desc">Q1末で約$655Mの利用可能流動性を持ちます。</div></div>'
            '<div class="card-sm"><span class="card-emoji">⚠️</span><div class="card-title">リスク</div><div class="card-desc">臨床データ失敗、開発遅延、赤字継続が主なリスクです。</div></div>'
        ),
        "SEC1_BIZMODEL": (
            '<li><span class="kp-emoji">🧬</span><span class="kp-text"><b>創薬基盤</b>：抗体探索、実験、データ解析、製造基盤を統合しています。</span></li>'
            '<li><span class="kp-emoji">💊</span><span class="kp-text"><b>自社開発</b>：ABCL635、ABCL575など臨床プログラムを進めます。</span></li>'
            '<li><span class="kp-emoji">🤝</span><span class="kp-text"><b>提携</b>：製薬会社との提携でマイルストンや将来ロイヤルティを狙います。</span></li>'
        ),
        "SEC1_HIGHLIGHT": '<div class="highlight"><h3>ABCLを見る基本ルール</h3><p>短期売上よりも、臨床データ、資金残高、提携数、下流権利の質を見ます。特にABCL635のPhase 2データは、株価の評価レンジを大きく動かす可能性があります。</p></div>',
        "SEC2_ICON": "🧬",
        "SEC2_TITLE": "事業モデルの<span class=\"g\">基本</span>",
        "SEC2_SUB": "創薬基盤から自社パイプラインへ",
        "SEC2_TLDR": li("昔は提携型プラットフォーム色が強く、今は自社臨床パイプラインが評価の中心です。", "*") + li("Q1 2026売上は$8.3M、純損失は$43.2Mでした。", "*") + li("十分な資金は強みですが、臨床失敗時の下落リスクは大きいです。", "!"),
        "SEC2_CONTENT": (
            '<p class="lead">AbCelleraは、抗体を見つける技術基盤、前臨床・臨床開発、製造インフラを組み合わせて、抗体医薬の価値化を狙います。</p>'
            '<div class="sowhat"><p><b>つまり</b>、ABCLは「売上成長株」ではなく「臨床データで価値が変わるバイオ株」として見るのが自然です。</p></div>'
            '<div class="term-list">'
            + details("自社開発型への移行", "提携だけでなく、自社で臨床プログラムを持つことでアップサイドを大きくできます。", True)
            + details("利用可能流動性", "Q1 2026末の利用可能流動性は約$655Mです。開発継続の余裕を示します。")
            + details("赤字継続", "Q1 2026の純損失は$43.2Mでした。臨床段階では通常ですが、資金管理が重要です。")
            + details("下流権利", "提携先が開発を進めるほど、将来のマイルストンやロイヤルティ価値が出ます。")
            + "</div>"
        ),
        "SEC3_TITLE": "ABCL635と<span class=\"g\">臨床データ</span>",
        "SEC3_SUB": "2026年Q3の読出しが最大材料",
        "SEC3_TLDR": li("ABCL635は更年期の血管運動症状を狙う抗体候補です。", "*") + li("Phase 1では忍容性と標的関与の良好な中間データが示されました。", "*") + li("Phase 2の有効性データが弱いと、評価は大きく下がります。", "!"),
        "SEC3_CONTENT": (
            '<div class="product-grid"><div class="product-box"><div class="product-symbol">635</div><div class="product-name">ABCL635</div><div class="product-use">NK3R抗体、VMS対象。</div></div>'
            '<div class="product-box"><div class="product-symbol">575</div><div class="product-name">ABCL575</div><div class="product-use">臨床段階の自社候補。</div></div>'
            '<div class="product-box"><div class="product-symbol">688</div><div class="product-name">ABCL688</div><div class="product-use">IND/CTA準備段階。</div></div></div>'
            '<div class="term-list">'
            + details("ABCL635", "NK3Rを標的にした抗体候補です。Phase 1では肝毒性なし、良好な忍容性、標的関与の持続が示されました。", True)
            + details("Phase 2データ", "対象患者で症状改善を確認する段階です。2026年Q3の読出しが最重要です。")
            + details("ABCL575", "臨床中の別プログラムです。安全性と早期薬効シグナルの確認が焦点です。")
            + details("前臨床候補", "ABCL688とABCL386はIND/CTA準備段階です。臨床入りすればパイプラインの厚みが増します。")
            + "</div>"
        ),
        "SEC4_TITLE": "提携と<span class=\"g\">下流権利</span>",
        "SEC4_SUB": "自社開発以外の価値源",
        "SEC4_TLDR": li("製薬会社との提携は、研究収入と将来の下流権利につながります。", "*") + li("2026年6月にはJazz Pharmaceuticalsとの提携を発表しました。", "*") + li("ただし提携プログラムの進捗は外部要因に左右されます。", "!"),
        "SEC4_CONTENT": (
            '<ul class="keypoints"><li><span class="kp-emoji">🤝</span><span class="kp-text"><b>Jazz提携</b>：多重特異性抗体探索で新しい提携を追加しました。</span></li>'
            '<li><span class="kp-emoji">📄</span><span class="kp-text"><b>下流権利</b>：Q1末時点で進捗中と考える下流権利付きプログラムは40件です。</span></li>'
            '<li><span class="kp-emoji">🔬</span><span class="kp-text"><b>臨床分子</b>：下流権利を持つ臨床中分子は14件と説明されています。</span></li></ul>'
            '<div class="sowhat"><p><b>つまり</b>、自社データだけでなく、提携先の臨床進展も長期価値の材料になります。</p></div>'
        ),
        "SEC5_TITLE": "競合と<span class=\"g\">比べる</span>",
        "SEC5_SUB": "抗体創薬基盤と臨床バイオの中間",
        "SEC5_TLDR": li("比較対象はSchrodinger、Recursion、Generate、臨床段階バイオです。", "*") + li("ABCLはAI創薬だけでなく、抗体探索と実験基盤に強みがあります。", "*") + li("最終的には臨床データと資金効率で評価されます。", "!"),
        "SEC5_CONTENT": (
            '<div class="table-wrap"><table class="compare-table"><thead><tr><th>企業</th><th>強み</th><th>注意点</th></tr></thead><tbody>'
            '<tr><td class="me">AbCellera</td><td>抗体探索基盤、自社臨床、提携下流権利、資金力。</td><td>売上は小さく、臨床データ依存が大きい。</td></tr>'
            '<tr><td>AI創薬企業</td><td>計算・探索基盤の広がり。</td><td>臨床成功まで時間がかかる。</td></tr>'
            '<tr><td>臨床バイオ</td><td>単一プログラムの成功で大きく上がる。</td><td>失敗時の下落が大きい。</td></tr>'
            '<tr><td>大手製薬</td><td>資金力と販売網。</td><td>成長率は低めになりやすい。</td></tr>'
            '</tbody></table></div><div class="highlight"><h3>差別化の見方</h3><p>AbCelleraは創薬基盤と自社臨床を両方持つ点が特徴です。プラットフォームの夢だけでなく、ABCL635の実データで評価される段階に入っています。</p></div>'
        ),
        "SEC6_TLDR": li("ABCL635、Phase 2、下流権利、流動性を押さえると読みやすいです。", "*") + li("売上よりも臨床データと資金残高が重要です。", "*") + li("Q2詳細とQ3読出しは必ず更新確認が必要です。", "!"),
        "SEC6_CONTENT": '<div class="term-list">' + "".join(details(name, body) for name, body in terms) + "</div>",
        "SEC7_TLDR": li("最大材料はABCL635のPhase 2データです。", "*") + li("Jazz提携、Q2決算、追加候補の臨床入りも材料です。", "*") + li("データ失敗・赤字継続・資金調達懸念には注意です。", "!"),
        "SEC7_CONTENT": (
            '<div class="timeline"><div class="tl-row"><div class="tl-date">2026/05/11</div><div class="tl-title">Q1決算とABCL635 Phase 1中間データ <span class="signal bull">追い風</span></div><div class="tl-desc">忍容性、薬物動態、標的関与が良好と発表されました。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/06/17</div><div class="tl-title">Jazz Pharmaceuticals提携 <span class="signal bull">提携</span></div><div class="tl-desc">次世代T細胞誘導型多重特異性抗体探索で提携しました。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/08/05</div><div class="tl-title">Q2決算発表日の確認 <span class="signal neutral">確認</span></div><div class="tl-desc">公式リリースで発表日を確認。詳細資料は更新確認が必要です。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/Q3</div><div class="tl-title">ABCL635 Phase 2データ <span class="signal bull">最重要</span></div><div class="tl-desc">有効性が確認されるかが最大の株価材料です。</div></div></div>'
            '<div class="info-row"><div class="info-box info-box-green"><div class="info-title info-title-green">追い風</div><div class="info-text">Phase 1良好、資金力、Jazz提携、Q3読出し。</div></div>'
            '<div class="info-box info-box-amber"><div class="info-title info-title-amber">確認</div><div class="info-text">Q2詳細、Phase 2有効性、キャッシュバーン。</div></div>'
            '<div class="info-box info-box-red"><div class="info-title info-title-red">リスク</div><div class="info-text">臨床失敗、開発遅延、赤字継続、希薄化。</div></div></div>'
            + source_details
        ),
    }


def scenario_values() -> dict[str, str]:
    probs = {"bear": 0.30, "base": 0.45, "bull": 0.25}
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
        "VERDICT_STATUS": "データ待ちの高リスク中立",
        "VERDICT_LINE_1": f"評価基準株価は悲観〜楽観レンジの{BAND_POSITION:.1f}%地点です。Phase 2成功時の上値は残りますが、臨床失敗時の下値も大きい局面です。",
        "VERDICT_LINE_2": "この試算は2026年8月9日時点で取得できた公開情報に基づきます。Q2詳細とQ3データで更新が必要です。",
        "SCORE": str(score),
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "取得可能な直近株価",
        "BASE_PRICE": usd(BASE),
        "BASE_DELTA": "+34.9%",
        "EXPECTED_VALUE": usd(expected),
        "EXPECTED_DELTA": f"{(expected / P0 - 1) * 100:+.1f}%",
        "RISK_CLASS": "高",
        "RISK_NOTE": "臨床段階バイオ、データ依存が大きい",
        "WARN_BAND": '<div class="wrap"><div class="notice" style="margin-top:14px"><b>注意：</b>ABCLは臨床段階バイオです。治験データ、資金調達、規制イベントで株価が大きく変動します。</div></div>',
        "SNAPSHOT_LEAD": "今の株価は悲観ケース寄りです。ABCL635のPhase 2成功を十分には織り込んでいない一方、失敗時の下落リスクも残っています。",
        "BAND_POSITION": f"{BAND_POSITION:.1f}%",
        "ZONE_JUDGE": "悲観寄りの中立圏",
        "ZONE_NOTE": "Phase 2データが強ければ標準〜楽観側へ、弱ければ悲観側へ寄ります。",
        "BEAR_PRICE": usd(BEAR),
        "BULL_PRICE": usd(BULL),
        "ENDPOINT_RR": f"{endpoint_rr:.1f}倍",
        "MARKET_SCORE": str(round(BAND_POSITION)),
        "OWN_SCORE": str(round(own_score)),
        "MARKET_REVERSE_NOTE": "このモデルで逆算すると、市場はABCL635成功を一部だけ織り込み、臨床失敗と赤字継続リスクも強く見ています。",
        "SCENARIOS_LEAD": "現在株価から独立して、ABCL635、提携下流権利、資金余力、臨床失敗リスクを置きました。",
        "BEAR_PROB": "30%",
        "BASE_PROB": "45%",
        "BULL_PROB": "25%",
        "BEAR_DELTA": "-32.6%",
        "BULL_DELTA": "+112.0%",
        "BEAR_DL_ROWS": dl([("ABCL635", "Phase 2弱い"), ("提携価値", "限定的"), ("資金", "希薄化懸念"), ("株価", usd(BEAR))]),
        "BASE_DL_ROWS": dl([("ABCL635", "有効性シグナルあり"), ("提携価値", "一定評価"), ("資金", "十分"), ("株価", usd(BASE))]),
        "BULL_DL_ROWS": dl([("ABCL635", "強いデータ"), ("追加候補", "臨床入り進展"), ("提携", "大型化"), ("株価", usd(BULL))]),
        "PRICE_ZONE_ROWS": '<div class="zone"><div><b>$3.50未満</b><span>★★★</span></div><p>臨床失敗や希薄化懸念を強く織り込む価格帯です。</p></div><div class="zone"><div><b>$3.50〜$7.00</b><span>★★★</span></div><p>データ待ちの中立圏。今の株価はここです。</p></div><div class="zone"><div><b>$7.00〜$11.00</b><span>★★</span></div><p>ABCL635成功を評価し始める価格帯です。</p></div><div class="zone"><div><b>$11.00超</b><span>★</span></div><p>強いPhase 2と複数材料の成功が必要です。</p></div>',
        "SIGNAL_ROWS": '<div class="signal"><div><b>ABCL635 Phase 2</b><span class="up">最重要</span></div><p>Q3 2026予定の有効性データが最大材料です。</p></div><div class="signal"><div><b>資金余力</b><span class="up">追い風</span></div><p>Q1末で約$655Mの利用可能流動性があります。</p></div><div class="signal"><div><b>Q2詳細</b><span class="flat">確認</span></div><p>発表日後の詳細資料更新確認が必要です。</p></div><div class="signal"><div><b>赤字継続</b><span class="down">注意</span></div><p>臨床段階のためキャッシュバーンを確認します。</p></div>',
        "POSITIVES": "<li>ABCL635のPhase 1中間データは良好でした。</li><li>利用可能流動性が大きく、開発継続の余裕があります。</li><li>Jazz提携など外部提携の材料があります。</li><li>自社パイプラインと下流権利の両方を持ちます。</li>",
        "CONCERNS": "<li>臨床データ失敗時の下落が大きいです。</li><li>売上はまだ小さく、赤字が続いています。</li><li>Q2詳細とQ3読出しで前提が大きく変わります。</li><li>長期的には追加資金調達や希薄化に注意が必要です。</li>",
        "FORMULA": "臨床段階バイオのため、短期利益倍率ではなく、成功確率を反映した悲観・標準・楽観シナリオで見ました。",
        "CALC_TABLE_HEAD": th("ケース", "主な前提", "価値の見方", "計算株価", "確率", "確率加重"),
        "CALC_TABLE_ROWS": tr("悲観", "Phase 2弱い", "現金価値寄り", usd(BEAR), "30%", "$1.05") + tr("標準", "有効性シグナル", "自社候補を一部評価", usd(BASE), "45%", "$3.15") + tr("楽観", "強いデータ", "提携・追加候補も評価", usd(BULL), "25%", "$2.75"),
        "CALC_NOTICE": "現在株価に合わせた逆算ではありません。臨床データの成否で評価レンジが大きく変わる前提です。",
        "CONDITIONS": details("悲観ケース：$3.50 / 確率30%", "Phase 2データが弱く、現金価値と一部プラットフォーム価値だけが残るケースです。", True) + details("標準ケース：$7.00 / 確率45%", "Phase 2で有効性シグナルが出て、次試験への期待が残るケースです。") + details("楽観ケース：$11.00 / 確率25%", "ABCL635が強く、追加候補や提携価値も評価されるケースです。"),
        "SENSITIVITY_HEAD": th("前提", "弱い", "標準", "強い"),
        "SENSITIVITY_ROWS": tr("ABCL635成功確率", "低い → $3.50", "中程度 → $7.00", "高い → $11.00") + tr("資金評価", "希薄化懸念", "3年以上の余裕", "提携収入追加"),
        "SENSITIVITY_NOTE": "臨床バイオでは、1つの読出しで成功確率と倍率が同時に動きます。",
        "DIST_LEAD": "モンテカルロではなく、臨床イベント前の3点分布です。",
        "DIST_ROWS": '<div class="dist-row"><span>$3.50</span><div class="track"><i style="width:30%"></i></div><b>30%</b></div><div class="dist-row"><span>$7.00</span><div class="track"><i style="width:45%"></i></div><b>45%</b></div><div class="dist-row"><span>$11.00</span><div class="track"><i style="width:25%"></i></div><b>25%</b></div>',
        "DIST_SUMMARY": "期待値は標準ケース付近ですが、実際の株価はデータで上下に振れやすいです。",
        "WATCH_ROWS": '<div class="signal"><div><b>ABCL635 Phase 2</b></div><p>症状改善、有害事象、投与頻度を確認します。</p></div><div class="signal"><div><b>Q2決算詳細</b></div><p>キャッシュ、研究開発費、提携進捗を確認します。</p></div><div class="signal"><div><b>追加候補</b></div><p>ABCL688、ABCL386の臨床入り準備を確認します。</p></div>',
        "ASSUMPTIONS_ROWS": tr("評価基準株価", usd(P0), "市場データで確認", DATE, "取得可能な直近株価") + tr("利用可能流動性", "約$655M", "会社Q1リリース", "2026/03/31", "政府資金含む") + tr("Q2決算", "2026/08/05予定・詳細未確認", "会社リリース", "2026/07/07", "詳細更新確認が必要") + tr("ABCL635読出し", "2026年Q3予定", "会社Q1リリース", "Phase 2", "最大材料"),
        "DEEPDIVE_DETAILS": details("手法選定理由", "ABCLは赤字の臨床段階バイオです。PERではなく、臨床成功確率と資金価値を反映したシナリオ法を使います。", True) + details("Q2詳細について", "2026年8月5日に発表予定と公式リリースで確認していますが、この作成時点で取得できた詳細資料はQ1中心です。") + details("主要出典", f'{source_link("公式IR概要", "overview")}、{source_link("Q1決算リリース", "q1")}、{source_link("Q2発表日確認", "q2_date")}、{source_link("SEC 10-Q", "sec_q1")}。<br><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>'),
        "DISCLAIMER": "本資料は情報提供を目的とした試算です。投資助言ではありません。臨床段階バイオは治験結果、規制、資金調達で大きく変動します。",
        "FOOTER_NOTE": f"SiM MARKET LAB｜{COMPANY}（{TICKER}）株価シナリオ｜作成日 {DATE}",
    }


def catalyst_values() -> dict[str, str]:
    non_quant = '<div class="priced"><div class="priced-head"><span>主要材料の推定織り込み</span><b>38%</b></div><p>仮定：ABCL635 Phase 2成功期待を35%、Q2決算の資金余力維持を55%、Jazz提携価値を30%、追加候補の臨床入り期待を25%として置き、重複を控除しました。</p><p>読み方：株価はABCL635成功を一部織り込んでいますが、臨床データ前のため期待はまだ半分未満です。良いデータなら上振れ、失敗なら大きく下振れます。</p><p>次に見る数字：利用可能流動性、R&D費、下流権利付きプログラム数、臨床中分子数、Phase 2有効性です。</p><p>再計算方法：各材料の成功確率を更新し、レポート2のシナリオ株価を再計算します。</p></div>'
    outcome_common = "<ul><li>目安：下の％は、この結果が出た後に市場が材料を評価し直した場合の上昇・下落幅です。</li><li>実際の値動きは地合い、直前の株価上昇、同時ニュースで変わります。</li></ul>"
    impact_map = {
        "ABCL635 Phase 2データ": ("+45〜110%", "-15〜+35%", "-45〜-70%", "主力候補の成否で標準ケースと悲観ケースが直接入れ替わるため最大レンジにしています。"),
        "2026年Q2決算詳細": ("+8〜18%", "-6〜+6%", "-12〜-25%", "資金余力とバーン確認が中心で、臨床データほど企業価値を直接変えないため小さめです。"),
        "Jazz Pharmaceuticals提携": ("+10〜25%", "-4〜+8%", "-8〜-18%", "提携はプラットフォーム価値を支えますが、短期売上化まで距離があるため中程度です。"),
        "ABCL688・ABCL386の臨床入り準備": ("+12〜30%", "-6〜+10%", "-12〜-24%", "主力候補依存を下げる材料ですが、まだ初期段階なのでPhase 2より小さくしています。"),
    }
    description_map = {
        "ABCL635 Phase 2データ": "ABCL635は同社の自社開発パイプラインで最も株価への影響が大きい候補です。Phase 2で効き目と安全性が確認されるかにより、次の試験へ進める確度と開発価値の見方が大きく変わります。",
        "2026年Q2決算詳細": "決算詳細では、臨床試験を続けるための資金余力、研究開発費の増え方、提携収入の有無を確認します。良い臨床材料があっても、資金消費が大きいと希薄化懸念が株価を抑えます。",
        "Jazz Pharmaceuticals提携": "Jazzとの提携は、ABCLの抗体探索プラットフォームが外部企業に使われる価値を示す材料です。短期売上よりも、将来のマイルストーンや下流権利が増えるかを見ます。",
        "ABCL688・ABCL386の臨床入り準備": "追加候補の臨床入り準備は、ABCL635だけに期待が集中する状態を和らげる材料です。複数候補が進むほど、会社全体のパイプライン価値が厚くなります。",
    }

    def card(title: str, date: str, chips: str, mechanism: str, success: str, inline: str, failure: str, evidence: str) -> str:
        up, flat, down, reason = impact_map[title]
        description = description_map[title]
        return f'''<article class="catalyst-card">
<div class="catalyst-head"><div><span class="pill">重要材料</span><h3>{title}</h3><div class="chips">{chips}</div></div><div class="date-box"><b>{date}</b><span>会社公表または予定</span></div></div>
<p class="lead">{description}</p>
<div class="mechanism">{mechanism}</div>
<div class="outcomes">
<div class="outcome success"><b>期待以上</b><div class="impact up">{up}</div><p>{success}</p>{outcome_common}</div>
<div class="outcome inline"><b>ほぼ想定どおり</b><div class="impact flat">{flat}</div><p>{inline}</p>{outcome_common}</div>
<div class="outcome failure"><b>期待外れ・遅延</b><div class="impact down">{down}</div><p>{failure}</p>{outcome_common}</div>
</div>
<p class="notice"><b>この％にした理由：</b>{reason}</p>
<div class="evidence"><div><h4>根拠</h4><ul>{evidence}</ul></div><div><h4>反証・先行指標</h4><ul><li>有効性が弱い</li><li>安全性懸念</li><li>キャッシュバーン拡大</li></ul></div></div>
</article>'''

    cards = [
        card("ABCL635 Phase 2データ", "2026年Q3", '<span class="chip">重要度5</span><span class="chip">最重要</span>', '<span>有効性</span><i>→</i><span>成功確率</span><i>→</i><span>株価レンジ</span>', "症状改善が明確で、安全性も良好なら標準〜楽観ケースへ寄ります。", "改善傾向はあるが追加試験待ちなら、標準ケース中心です。", "有効性不足や安全性懸念があれば、悲観ケースへ寄ります。", "<li>会社はQ1リリースでPhase 2データを2026年Q3予定と説明。</li><li>Phase 1中間データでは忍容性と標的関与が良好でした。</li>"),
        card("2026年Q2決算詳細", "2026/08/05", '<span class="chip">重要度4</span><span class="chip blue">確認</span>', '<span>資金</span><i>→</i><span>開発余力</span><i>→</i><span>希薄化リスク</span>', "資金余力が維持され、開発費も管理されていれば安心材料です。", "資金は十分だが赤字継続なら、データ待ちです。", "キャッシュバーン拡大や見通し悪化なら下押しです。", "<li>公式リリースで2026年8月5日にQ2決算発表日の確認と確認。</li><li>Q1末の利用可能流動性は約$655Mでした。</li>"),
        card("Jazz Pharmaceuticals提携", "2026/06/17", '<span class="chip">重要度3</span><span class="chip blue">提携</span>', '<span>提携</span><i>→</i><span>研究収入</span><i>→</i><span>下流権利</span>', "追加提携や条件開示が強ければ、プラットフォーム価値が上がります。", "研究提携として長期材料にとどまる状態です。", "進捗が見えなければ短期株価影響は限定的です。", "<li>2026年6月にJazz Pharmaceuticalsとの提携を発表。</li><li>多重特異性抗体探索が対象です。</li>"),
        card("ABCL688・ABCL386の臨床入り準備", "2026年内", '<span class="chip">重要度3</span><span class="chip blue">パイプライン</span>', '<span>候補追加</span><i>→</i><span>分散</span><i>→</i><span>評価</span>', "複数候補が臨床入りすれば、ABCL635単独依存が下がります。", "準備進展だけなら中期材料です。", "遅延が続くとパイプライン厚みへの期待が下がります。", "<li>Q1リリースでABCL688とABCL386がIND-enabling活動中と説明。</li><li>2026年の重点項目として追加候補選定も挙げられています。</li>"),
    ]
    return {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "Nasdaq",
        "VALUATION_DATE": DATE,
        "LAST_UPDATED": DATE,
        "REPORT_STATUS": "データ待ち",
        "SUMMARY_LINE_1": "ABCL635 Phase 2、Q2決算詳細、Jazz提携、追加候補の臨床入りが主な材料です。",
        "SUMMARY_LINE_2": "足りない情報は仮定を置き、主要材料の織り込み度を38%と推定します。",
        "OVERALL_PRICED_IN": "38%",
        "OVERALL_PRICED_LABEL": "主要材料の推定織り込み",
        "PRICED_IN_CONFIDENCE": "低〜中",
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "取得可能な直近株価",
        "NEXT_CATALYST_TITLE": "ABCL635 Phase 2データ",
        "NEXT_CATALYST_WINDOW": "2026年Q3",
        "DATE_CONFIDENCE": "会社予定",
        "CATALYST_COUNT": "4件",
        "WARN_BAND": "",
        "NO_CATALYST_NOTICE": "",
        "OVERALL_PRICED_BLOCK": non_quant,
        "PRICED_IN_METHOD": "未確定情報に仮定確率を置き、ABCL635、Q2資金余力、Jazz提携、追加候補を標準ケース価値へ重み付けして推定。",
        "SURPRISE_UP": "ABCL635の有効性が明確で、安全性と月1回投与の魅力が保たれることです。",
        "SURPRISE_DOWN": "Phase 2の有効性不足、安全性懸念、キャッシュバーン拡大です。",
        "PRIMARY_RISK": "ABCL635に期待が集中しているため、読出し失敗時の株価下落が大きくなりやすいことです。",
        "TIMELINE_ROWS": '<div class="time-row"><div class="time-date">2026/05/11</div><div class="time-dot"></div><div class="time-body"><b>Q1決算とABCL635 Phase 1中間データ</b><p>良好な忍容性、標的関与、月1回投与可能性を確認。</p><div class="time-meta"><span class="chip">公表済み</span></div></div></div><div class="time-row"><div class="time-date">2026/06/17</div><div class="time-dot"></div><div class="time-body"><b>Jazz提携</b><p>多重特異性抗体探索の提携を発表。</p><div class="time-meta"><span class="chip blue">提携</span></div></div></div><div class="time-row"><div class="time-date">2026/08/05</div><div class="time-dot"></div><div class="time-body"><b>Q2決算発表日の確認</b><p>詳細資料は更新確認が必要。</p><div class="time-meta"><span class="chip">確認</span></div></div></div><div class="time-row"><div class="time-date">2026/Q3</div><div class="time-dot"></div><div class="time-body"><b>ABCL635 Phase 2データ</b><p>最大の価値変動イベント。</p><div class="time-meta"><span class="chip">最重要</span></div></div></div>',
        "CATALYST_CARDS": "".join(cards),
        "DEPENDENCY_ROWS": '<div class="signal"><div><b>ABCL635と資金余力</b><span class="up">連動</span></div><p>良いデータでも次試験に進む資金余力が重要です。</p></div><div class="signal"><div><b>提携と下流権利</b><span class="flat">長期</span></div><p>短期株価より長期価値の材料です。</p></div><div class="signal"><div><b>追加候補</b><span class="up">分散</span></div><p>ABCL635依存を下げる材料になります。</p></div>',
        "WATCH_ROWS": '<div class="signal"><div><b>Phase 2有効性</b><span class="up">最重要</span></div><p>頻度・重症度の改善幅を確認します。</p></div><div class="signal"><div><b>安全性</b><span class="flat">必須</span></div><p>肝毒性や重い有害事象を確認します。</p></div><div class="signal"><div><b>流動性</b><span class="up">重要</span></div><p>現金、有価証券、政府資金、バーンを確認します。</p></div><div class="signal"><div><b>提携進捗</b><span class="flat">長期</span></div><p>下流権利付きプログラムの質を確認します。</p></div>',
        "ASSUMPTION_ROWS": tr("評価基準株価", usd(P0), "市場データで確認", DATE, "取得可能な直近株価") + tr("利用可能流動性", "約$655M", "会社Q1リリース", "2026/03/31", "政府資金含む") + tr("Q2決算予定", "2026/08/05", "会社リリース", "2026/07/07", "詳細更新確認が必要") + tr("ABCL635", "Phase 2読出し", "会社Q1リリース", "2026年Q3", "最重要"),
        "SOURCE_DETAILS": f'<ul><li>{source_link("公式IR概要", "overview")}</li><li>{source_link("四半期決算資料", "quarterly")}</li><li>{source_link("Q1決算リリース", "q1")}</li><li>{source_link("Q2発表日確認", "q2_date")}</li><li>{source_link("SEC 10-Q", "sec_q1")}</li><li>{source_link("株価時系列", "quote")}</li></ul><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p>',
        "VALIDATION_DETAILS": "<p>PASS：公式IR、四半期決算ページ、Q1決算リリース、SEC 10-Q、Q2発表日確認、株価時系列を確認。WARN：Q2詳細は取得できた公式ページで未確認のため、公開後に更新確認が必要です。</p>",
        "UPDATE_HISTORY": f"<p>{DATE}：初版作成。Q1 2026、ABCL635 Phase 1中間データ、Jazz提携、Q2発表日確認、Q3 Phase 2読出し予定を反映。</p>",
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
        "id": "abcellera-abcl",
        "order": 6,
        "ticker": "ABCL",
        "quoteSymbol": "ABCL",
        "name": "アブセレラ",
        "nameEn": "AbCellera Biologics Inc.",
        "market": "US",
        "marketLabel": "米国株",
        "exchange": "Nasdaq",
        "currency": "USD",
        "sector": "抗体創薬・臨床段階バイオ",
        "reports": {
            "company": {"path": "./stocks/abcellera-abcl/company.html", "available": True},
            "valuation": {"path": "./stocks/abcellera-abcl/valuation.html", "available": True},
            "catalysts": {"path": "./stocks/abcellera-abcl/catalysts.html", "available": True},
        },
    }
    stocks_payload["stocks"] = [item for item in stocks_payload["stocks"] if item["id"] != "abcellera-abcl"]
    stocks_payload["stocks"].append(stock)
    stocks_path.write_text(json.dumps(stocks_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    prices_path = ROOT / "data" / "prices.json"
    prices_payload = json.loads(prices_path.read_text(encoding="utf-8"))
    prices_payload.setdefault("prices", {})["abcellera-abcl"] = {
        "symbol": "ABCL",
        "price": P0,
        "previousClose": PREVIOUS_CLOSE,
        "change": round(P0 - PREVIOUS_CLOSE, 2),
        "changePct": round((P0 - PREVIOUS_CLOSE) / PREVIOUS_CLOSE * 100, 4),
        "currency": "USD",
        "marketTime": "2026-07-28T20:00:00+00:00",
        "updatedAt": "2026-08-09T00:00:00+00:00",
        "status": "ok",
    }
    prices_payload["quoteCount"] = len(prices_payload["prices"])
    prices_path.write_text(json.dumps(prices_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    signals_path = ROOT / "data" / "signals.json"
    signals_payload = json.loads(signals_path.read_text(encoding="utf-8"))
    signals_payload["updatedAt"] = datetime.now(timezone.utc).isoformat()
    signals_payload.setdefault("signals", {})["abcellera-abcl"] = {
        "position": SIGNAL_POSITION,
        "zone": "中立",
        "asOf": DATE,
        "components": {
            "valuation": round(BAND_POSITION, 1),
            "catalysts": 74.0,
            "businessRisk": 78.0,
        },
        "reportRevision": "abcellera-abcl-2026-08-09",
        "summary": "ABCL635のPhase 2読出し待ち。資金力と提携は支えだが、臨床失敗時の下落が大きいため中立。",
    }
    signals_path.write_text(json.dumps(signals_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_reports()
    upsert_site_data()


if __name__ == "__main__":
    main()
