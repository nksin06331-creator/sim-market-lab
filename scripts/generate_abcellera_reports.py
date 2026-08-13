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
DATE = "2026-08-13"
P0 = 10.355
PREVIOUS_CLOSE = 9.76
SHARES_M = 305.38
MARKET_CAP_B = P0 * SHARES_M / 1000

BEAR = 6.00
BASE = 12.00
BULL = 18.00
BAND_POSITION = (P0 - BEAR) / (BULL - BEAR) * 100
SIGNAL_POSITION = round(0.60 * round(BAND_POSITION, 1) + 0.25 * 88.0 + 0.15 * 70.0, 1)

SOURCES = {
    "overview": "https://investors.abcellera.com/overview/",
    "quarterly": "https://investors.abcellera.com/financials/quarterly-results/default.aspx",
    "q1": "https://investors.abcellera.com/news/news-releases/2026/AbCellera-Reports-Q1-2026-Business-Results--Announces-Positive-Interim-Phase-1-Clinical-Data-for-ABCL635/default.aspx",
    "q2_date": "https://investors.abcellera.com/news/news-releases/2026/AbCellera-to-Report-Second-Quarter-2026-Financial-Results-on-August-5-2026/default.aspx",
    "phase2_news": "https://www.barrons.com/articles/abcellera-stock-menopause-drug-f6dfa1ca",
    "sec_q1": "https://www.sec.gov/Archives/edgar/data/1703057/000170305726000028/abcl-20260331.htm",
    "news": "https://investors.abcellera.com/news/default.aspx",
    "quote": "https://stockanalysis.com/stocks/abcl/",
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
        f'{source_link("四半期決算資料", "quarterly")}、'
        f'{source_link("2026年1Q決算リリース", "q1")}、'
        f'{source_link("2026年2Q発表日リリース", "q2_date")}、'
        f'{source_link("ABCL635 Phase 2報道", "phase2_news")}、'
        f'{source_link("SEC 10-Q", "sec_q1")}、'
        f'{source_link("株価・統計", "quote")}を確認しました。'
        "本文の数値は2026年8月13日時点で取得できた公開情報に基づきます。"
        '</p><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p></div></details>'
    )
    terms = [
        ("抗体創薬", "抗体を使った医薬品候補を発見・開発する領域です。"),
        ("臨床段階バイオ", "製品売上よりも治験データ、資金残高、パートナー契約が評価材料になります。"),
        ("ABCL635", "更年期の血管運動症状を対象にしたNK3R抗体候補です。Phase 2で頻度・重症度低下と良好な忍容性が報じられました。"),
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
            f'<div class="stat"><div class="stat-value">{usd(P0)}</div><div class="stat-label">評価基準株価</div><div class="stat-note">Phase 2好結果後の更新基準</div></div>'
            f'<div class="stat"><div class="stat-value">${MARKET_CAP_B:.1f}B</div><div class="stat-label">時価総額の目安</div><div class="stat-note">約3.05億株で計算</div></div>'
            '<div class="stat"><div class="stat-value up">$655M</div><div class="stat-label">利用可能流動性</div><div class="stat-note">2026年1Q末</div></div>'
            '<div class="stat"><div class="stat-value up">Positive</div><div class="stat-label">重要読出し</div><div class="stat-note">ABCL635 Phase 2</div></div>'
        ),
        "SEC2_LABEL": "事業モデル",
        "SEC3_LABEL": "パイプライン",
        "SEC4_LABEL": "提携",
        "SEC5_LABEL": "競合比較",
        "SEC1_TLDR": li("AbCelleraは抗体創薬プラットフォームから、自社開発型の臨床段階バイオへ移行中です。", "*") + li("ABCL635のPhase 2で頻度・重症度低下と良好な忍容性が報じられ、株価は大きく反応しました。", "*") + li("次は後期試験計画、資金消費、Q2以降の決算詳細を確認します。", "!"),
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
        "SEC3_SUB": "Phase 2好結果後は後期試験設計が焦点",
        "SEC3_TLDR": li("ABCL635は更年期の血管運動症状を狙う抗体候補です。", "*") + li("Phase 2では症状の頻度・重症度低下、睡眠・全体的な状態の改善、良好な忍容性が報じられました。", "*") + li("次は効果量の詳細、後期試験設計、競合薬との差別化を確認します。", "!"),
        "SEC3_CONTENT": (
            '<div class="product-grid"><div class="product-box"><div class="product-symbol">635</div><div class="product-name">ABCL635</div><div class="product-use">NK3R抗体、VMS対象。</div></div>'
            '<div class="product-box"><div class="product-symbol">575</div><div class="product-name">ABCL575</div><div class="product-use">臨床段階の自社候補。</div></div>'
            '<div class="product-box"><div class="product-symbol">688</div><div class="product-name">ABCL688</div><div class="product-use">IND/CTA準備段階。</div></div></div>'
            '<div class="term-list">'
            + details("ABCL635", "NK3Rを標的にした抗体候補です。Phase 1では肝毒性なし、良好な忍容性、標的関与の持続が示されました。", True)
            + details("Phase 2データ", "対象患者で症状改善を確認する段階です。好結果が報じられたため、次は後期試験へ進める質かを確認します。")
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
        "SEC6_TLDR": li("ABCL635、Phase 2、下流権利、流動性を押さえると読みやすいです。", "*") + li("売上よりも臨床データと資金残高が重要です。", "*") + li("Phase 2好結果後は、後期試験の設計と資金余力が確認点です。", "!"),
        "SEC6_CONTENT": '<div class="term-list">' + "".join(details(name, body) for name, body in terms) + "</div>",
        "SEC7_TLDR": li("最大材料だったABCL635のPhase 2は好結果として株価に反映されました。", "*") + li("次は後期試験計画、Q2以降の決算詳細、追加候補の臨床入りが材料です。", "*") + li("データ詳細の解釈、赤字継続、資金調達懸念には注意です。", "!"),
        "SEC7_CONTENT": (
            '<div class="timeline"><div class="tl-row"><div class="tl-date">2026/05/11</div><div class="tl-title">Q1決算とABCL635 Phase 1中間データ <span class="signal bull">追い風</span></div><div class="tl-desc">忍容性、薬物動態、標的関与が良好と発表されました。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/06/17</div><div class="tl-title">Jazz Pharmaceuticals提携 <span class="signal bull">提携</span></div><div class="tl-desc">次世代T細胞誘導型多重特異性抗体探索で提携しました。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/08</div><div class="tl-title">ABCL635 Phase 2好結果 <span class="signal bull">公表済み</span></div><div class="tl-desc">頻度・重症度低下、睡眠改善、良好な忍容性が報じられました。</div></div>'
            '<div class="tl-row"><div class="tl-date">次回</div><div class="tl-title">後期試験計画 <span class="signal bull">最重要</span></div><div class="tl-desc">用量、対象患者、試験規模、規制当局との協議を確認します。</div></div></div>'
            '<div class="info-row"><div class="info-box info-box-green"><div class="info-title info-title-green">追い風</div><div class="info-text">Phase 1良好、資金力、Jazz提携、Q3読出し。</div></div>'
            '<div class="info-box info-box-amber"><div class="info-title info-title-amber">確認</div><div class="info-text">Phase 2詳細、後期試験設計、キャッシュバーン。</div></div>'
            '<div class="info-box info-box-red"><div class="info-title info-title-red">リスク</div><div class="info-text">臨床失敗、開発遅延、赤字継続、希薄化。</div></div></div>'
            + source_details
        ),
    }


def scenario_values() -> dict[str, str]:
    probs = {"bear": 0.20, "base": 0.50, "bull": 0.30}
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
        "VERDICT_STATUS": "Phase 2好結果後の中立からやや強気",
        "VERDICT_LINE_1": f"評価基準株価は悲観〜楽観レンジの{BAND_POSITION:.1f}%地点です。Phase 2好結果で標準ケースに近づきましたが、後期試験前のバイオ株としてリスクは残ります。",
        "VERDICT_LINE_2": "この試算は2026年8月13日時点で取得できた公開情報に基づきます。Phase 2詳細、後期試験設計、Q2以降の資金消費で更新が必要です。",
        "SCORE": str(score),
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "取得可能な直近株価",
        "BASE_PRICE": usd(BASE),
        "BASE_DELTA": pct(BASE / P0 - 1),
        "EXPECTED_VALUE": usd(expected),
        "EXPECTED_DELTA": f"{(expected / P0 - 1) * 100:+.1f}%",
        "RISK_CLASS": "高",
        "RISK_NOTE": "臨床段階バイオ、データ依存が大きい",
        "WARN_BAND": '<div class="wrap"><div class="notice" style="margin-top:14px"><b>注意：</b>ABCLは臨床段階バイオです。治験データ、資金調達、規制イベントで株価が大きく変動します。</div></div>',
        "SNAPSHOT_LEAD": "今の株価はPhase 2好結果を一部織り込みました。標準ケースまではまだ上値がありますが、次は後期試験へ進めるデータの質と資金計画を確認します。",
        "BAND_POSITION": f"{BAND_POSITION:.1f}%",
        "ZONE_JUDGE": "標準ケース手前",
        "ZONE_NOTE": "後期試験計画が明確なら標準〜楽観側へ、データ詳細が弱い・資金消費が重いなら悲観側へ寄ります。",
        "BEAR_PRICE": usd(BEAR),
        "BULL_PRICE": usd(BULL),
        "ENDPOINT_RR": f"{endpoint_rr:.1f}倍",
        "MARKET_SCORE": str(round(BAND_POSITION)),
        "OWN_SCORE": str(round(own_score)),
        "MARKET_REVERSE_NOTE": "このモデルで逆算すると、市場はPhase 2好結果を相当評価しましたが、後期試験成功まではまだ割り引いています。",
        "SCENARIOS_LEAD": "現在株価から独立して、ABCL635のPhase 2好結果、後期試験移行、提携下流権利、資金余力、臨床リスクを置きました。",
        "BEAR_PROB": "20%",
        "BASE_PROB": "50%",
        "BULL_PROB": "30%",
        "BEAR_DELTA": pct(BEAR / P0 - 1),
        "BULL_DELTA": pct(BULL / P0 - 1),
        "BEAR_DL_ROWS": dl([("ABCL635", "詳細が弱い"), ("後期試験", "遅延"), ("資金", "希薄化懸念"), ("株価", usd(BEAR))]),
        "BASE_DL_ROWS": dl([("ABCL635", "後期試験へ前進"), ("提携価値", "一定評価"), ("資金", "十分"), ("株価", usd(BASE))]),
        "BULL_DL_ROWS": dl([("ABCL635", "ベストインクラス期待"), ("追加候補", "臨床入り進展"), ("提携", "大型化"), ("株価", usd(BULL))]),
        "PRICE_ZONE_ROWS": '<div class="zone"><div><b>$6未満</b><span>★★★</span></div><p>好材料の反動や資金懸念を強く織り込む価格帯です。</p></div><div class="zone"><div><b>$6〜$12</b><span>★★★</span></div><p>Phase 2好結果を評価しつつ、後期試験前のリスクも残す価格帯です。</p></div><div class="zone"><div><b>$12〜$18</b><span>★★</span></div><p>後期試験移行と競合優位を評価し始める価格帯です。</p></div><div class="zone"><div><b>$18超</b><span>★</span></div><p>強いデータ詳細、後期試験計画、複数材料の成功が必要です。</p></div>',
        "SIGNAL_ROWS": '<div class="signal"><div><b>ABCL635 Phase 2</b><span class="up">好材料</span></div><p>頻度・重症度低下と良好な忍容性が報じられました。</p></div><div class="signal"><div><b>資金余力</b><span class="up">追い風</span></div><p>Q1末で約$655Mの利用可能流動性があります。</p></div><div class="signal"><div><b>後期試験設計</b><span class="flat">確認</span></div><p>用量、試験規模、規制当局との協議を確認します。</p></div><div class="signal"><div><b>赤字継続</b><span class="down">注意</span></div><p>臨床段階のためキャッシュバーンを確認します。</p></div>',
        "POSITIVES": "<li>ABCL635のPhase 2で症状の頻度・重症度低下と良好な忍容性が報じられました。</li><li>利用可能流動性が大きく、開発継続の余裕があります。</li><li>Jazz提携など外部提携の材料があります。</li><li>自社パイプラインと下流権利の両方を持ちます。</li>",
        "CONCERNS": "<li>Phase 2好結果後も、後期試験で再現できるかは未確定です。</li><li>売上はまだ小さく、赤字が続いています。</li><li>データ詳細、後期試験設計、Q2以降の資金消費で前提が変わります。</li><li>長期的には追加資金調達や希薄化に注意が必要です。</li>",
        "FORMULA": "臨床段階バイオのため、短期利益倍率ではなく、成功確率を反映した悲観・標準・楽観シナリオで見ました。",
        "CALC_TABLE_HEAD": th("ケース", "主な前提", "価値の見方", "計算株価", "確率", "確率加重"),
        "CALC_TABLE_ROWS": tr("悲観", "詳細弱い・遅延", "現金価値寄り", usd(BEAR), "20%", "$1.20") + tr("標準", "後期試験へ前進", "自社候補を評価", usd(BASE), "50%", "$6.00") + tr("楽観", "ベストインクラス期待", "提携・追加候補も評価", usd(BULL), "30%", "$5.40"),
        "CALC_NOTICE": "現在株価に合わせた逆算ではありません。Phase 2好結果後も、後期試験の再現性と資金計画で評価レンジが変わる前提です。",
        "CONDITIONS": details("悲観ケース：$6 / 確率20%", "Phase 2詳細が期待ほど強くない、後期試験設計が遅れる、資金消費が重くなるケースです。", True) + details("標準ケース：$12 / 確率50%", "Phase 2好結果を土台に後期試験へ前進し、資金余力も維持されるケースです。") + details("楽観ケース：$18 / 確率30%", "ABCL635が競合薬に対して明確な差別化を示し、追加候補や提携価値も評価されるケースです。"),
        "SENSITIVITY_HEAD": th("前提", "弱い", "標準", "強い"),
        "SENSITIVITY_ROWS": tr("ABCL635成功確率", "詳細弱い → $6", "後期試験へ前進 → $12", "強い差別化 → $18") + tr("資金評価", "希薄化懸念", "3年以上の余裕", "提携収入追加"),
        "SENSITIVITY_NOTE": "臨床バイオでは、1つの読出しで成功確率と倍率が同時に動きます。",
        "DIST_LEAD": "モンテカルロではなく、Phase 2好結果後の3点分布です。",
        "DIST_ROWS": '<div class="dist-row"><span>$6</span><div class="track"><i style="width:20%"></i></div><b>20%</b></div><div class="dist-row"><span>$12</span><div class="track"><i style="width:50%"></i></div><b>50%</b></div><div class="dist-row"><span>$18</span><div class="track"><i style="width:30%"></i></div><b>30%</b></div>',
        "DIST_SUMMARY": "期待値は標準ケースを少し上回りますが、実際の株価は後期試験設計と資金計画で上下に振れやすいです。",
        "WATCH_ROWS": '<div class="signal"><div><b>Phase 2詳細</b></div><p>症状改善幅、安全性、投与頻度、競合薬との差を確認します。</p></div><div class="signal"><div><b>後期試験設計</b></div><p>用量、試験規模、規制協議、開始時期を確認します。</p></div><div class="signal"><div><b>Q2以降の決算</b></div><p>キャッシュ、研究開発費、提携進捗を確認します。</p></div>',
        "ASSUMPTIONS_ROWS": tr("評価基準株価", usd(P0), "市場データで確認", DATE, "Phase 2好結果後の更新基準") + tr("利用可能流動性", "約$655M", "会社Q1リリース", "2026/03/31", "政府資金含む") + tr("Phase 2結果", "好結果報道", "報道・公式情報確認", "2026/08", "詳細確認を継続") + tr("ABCL635次段階", "後期試験計画", "会社Q1方針と報道から推定", "今後", "最大材料"),
        "DEEPDIVE_DETAILS": details("手法選定理由", "ABCLは赤字の臨床段階バイオです。PERではなく、臨床成功確率と資金価値を反映したシナリオ法を使います。", True) + details("Phase 2好結果後について", "好結果は株価に大きく反映されました。ここからは効果量の詳細、後期試験設計、競合薬との差別化が評価の中心です。") + details("主要出典", f'{source_link("公式IR概要", "overview")}、{source_link("Q1決算リリース", "q1")}、{source_link("ABCL635 Phase 2報道", "phase2_news")}、{source_link("SEC 10-Q", "sec_q1")}。<br><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>'),
        "DISCLAIMER": "本資料は情報提供を目的とした試算です。投資助言ではありません。臨床段階バイオは治験結果、規制、資金調達で大きく変動します。",
        "FOOTER_NOTE": f"SiM MARKET LAB｜{COMPANY}（{TICKER}）株価シナリオ｜作成日 {DATE}",
    }


def catalyst_values() -> dict[str, str]:
    non_quant = '<div class="priced"><div class="priced-head"><span>主要材料の推定織り込み</span><b>64%</b></div><p>仮定：ABCL635 Phase 2好結果を80%、後期試験移行期待を55%、資金余力維持を60%、Jazz提携価値を30%、追加候補の臨床入り期待を25%として置き、株価急騰後の期待織り込みを控除しました。</p><p>読み方：Phase 2好結果はかなり織り込まれましたが、後期試験の設計、規制協議、資金計画はまだ一部織り込みです。</p><p>次に見る数字：Phase 2の効果量、安全性、投与間隔、後期試験開始時期、利用可能流動性、R&D費、下流権利付きプログラム数です。</p><p>再計算方法：各材料の成功確率を更新し、レポート2のシナリオ株価を再計算します。</p></div>'
    impact_map = {
        "ABCL635 Phase 2詳細と後期試験計画": ("+25〜60%", "-10〜+18%", "-25〜-45%", "好結果後の次の評価軸は、後期試験に進めるデータの質と試験設計なので最大材料にしています。"),
        "2026年Q2以降の決算詳細": ("+8〜18%", "-6〜+6%", "-12〜-25%", "資金余力とバーン確認が中心で、臨床データほど企業価値を直接変えないため小さめです。"),
        "Jazz Pharmaceuticals提携": ("+10〜25%", "-4〜+8%", "-8〜-18%", "提携はプラットフォーム価値を支えますが、短期売上化まで距離があるため中程度です。"),
        "ABCL688・ABCL386の臨床入り準備": ("+12〜30%", "-6〜+10%", "-12〜-24%", "主力候補依存を下げる材料ですが、まだ初期段階なのでPhase 2より小さくしています。"),
    }
    description_map = {
        "ABCL635 Phase 2詳細と後期試験計画": "ABCL635は同社の自社開発パイプラインで最も株価への影響が大きい候補です。Phase 2好結果後は、効果量の詳細、安全性、投与間隔、後期試験へ進む計画が評価の中心です。",
        "2026年Q2以降の決算詳細": "決算詳細では、臨床試験を続けるための資金余力、研究開発費の増え方、提携収入の有無を確認します。良い臨床材料があっても、資金消費が大きいと希薄化懸念が株価を抑えます。",
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
<div class="outcome success"><b>期待以上</b><div class="impact up">{up}</div><p>{success}</p></div>
<div class="outcome inline"><b>ほぼ想定どおり</b><div class="impact flat">{flat}</div><p>{inline}</p></div>
<div class="outcome failure"><b>期待外れ・遅延</b><div class="impact down">{down}</div><p>{failure}</p></div>
</div>
<p class="notice"><b>この％にした理由：</b>{reason}</p>
<div class="evidence"><div><h4>根拠</h4><ul>{evidence}</ul></div><div><h4>反証・先行指標</h4><ul><li>有効性が弱い</li><li>安全性懸念</li><li>キャッシュバーン拡大</li></ul></div></div>
</article>'''

    cards = [
        card("ABCL635 Phase 2詳細と後期試験計画", "今後", '<span class="chip">重要度5</span><span class="chip">最重要</span>', '<span>効果量</span><i>→</i><span>後期試験</span><i>→</i><span>株価レンジ</span>', "効果量が強く、安全性も良好で、後期試験開始時期が明確なら楽観側です。", "好結果を維持しつつ詳細確認待ちなら、標準ケース中心です。", "詳細データが期待ほど強くない、または後期試験が遅れると下押しです。", "<li>Phase 2で頻度・重症度低下と良好な忍容性が報じられました。</li><li>Phase 1中間データでは忍容性と標的関与が良好でした。</li>"),
        card("2026年Q2以降の決算詳細", "継続確認", '<span class="chip">重要度4</span><span class="chip blue">確認</span>', '<span>資金</span><i>→</i><span>開発余力</span><i>→</i><span>希薄化リスク</span>', "資金余力が維持され、開発費も管理されていれば安心材料です。", "資金は十分だが赤字継続なら、臨床進捗待ちです。", "キャッシュバーン拡大や見通し悪化なら下押しです。", "<li>Q1末の利用可能流動性は約$655Mでした。</li><li>後期試験に進む場合、R&D費と資金計画の確認が重要です。</li>"),
        card("Jazz Pharmaceuticals提携", "2026/06/17", '<span class="chip">重要度3</span><span class="chip blue">提携</span>', '<span>提携</span><i>→</i><span>研究収入</span><i>→</i><span>下流権利</span>', "追加提携や条件開示が強ければ、プラットフォーム価値が上がります。", "研究提携として長期材料にとどまる状態です。", "進捗が見えなければ短期株価影響は限定的です。", "<li>2026年6月にJazz Pharmaceuticalsとの提携を発表。</li><li>多重特異性抗体探索が対象です。</li>"),
        card("ABCL688・ABCL386の臨床入り準備", "2026年内", '<span class="chip">重要度3</span><span class="chip blue">パイプライン</span>', '<span>候補追加</span><i>→</i><span>分散</span><i>→</i><span>評価</span>', "複数候補が臨床入りすれば、ABCL635単独依存が下がります。", "準備進展だけなら中期材料です。", "遅延が続くとパイプライン厚みへの期待が下がります。", "<li>Q1リリースでABCL688とABCL386がIND-enabling活動中と説明。</li><li>2026年の重点項目として追加候補選定も挙げられています。</li>"),
    ]
    return {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "Nasdaq",
        "VALUATION_DATE": DATE,
        "LAST_UPDATED": DATE,
        "REPORT_STATUS": "Phase 2好結果後",
        "SUMMARY_LINE_1": "ABCL635 Phase 2好結果、後期試験計画、Q2以降の資金消費、Jazz提携、追加候補の臨床入りが主な材料です。",
        "SUMMARY_LINE_2": "足りない情報は仮定を置き、主要材料の織り込み度を64%と推定します。",
        "OVERALL_PRICED_IN": "64%",
        "OVERALL_PRICED_LABEL": "主要材料の推定織り込み",
        "PRICED_IN_CONFIDENCE": "低〜中",
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "Phase 2好結果後の更新基準",
        "NEXT_CATALYST_TITLE": "ABCL635 Phase 2詳細と後期試験計画",
        "NEXT_CATALYST_WINDOW": "今後",
        "DATE_CONFIDENCE": "時期未定",
        "CATALYST_COUNT": "4件",
        "WARN_BAND": "",
        "NO_CATALYST_NOTICE": "",
        "OVERALL_PRICED_BLOCK": non_quant,
        "PRICED_IN_METHOD": "Phase 2好結果、後期試験移行期待、資金余力、Jazz提携、追加候補を標準ケース価値へ重み付けして推定。",
        "SURPRISE_UP": "ABCL635の効果量が強く、安全性と月1回投与の魅力が保たれ、後期試験計画が明確になることです。",
        "SURPRISE_DOWN": "Phase 2詳細が期待ほど強くないこと、安全性懸念、後期試験遅延、キャッシュバーン拡大です。",
        "PRIMARY_RISK": "Phase 2好結果で株価が大きく反応したため、詳細データや後期試験計画が期待を下回ると下落しやすいことです。",
        "TIMELINE_ROWS": '<div class="time-row"><div class="time-date">2026/05/11</div><div class="time-dot"></div><div class="time-body"><b>Q1決算とABCL635 Phase 1中間データ</b><p>良好な忍容性、標的関与、月1回投与可能性を確認。</p><div class="time-meta"><span class="chip">公表済み</span></div></div></div><div class="time-row"><div class="time-date">2026/06/17</div><div class="time-dot"></div><div class="time-body"><b>Jazz提携</b><p>多重特異性抗体探索の提携を発表。</p><div class="time-meta"><span class="chip blue">提携</span></div></div></div><div class="time-row"><div class="time-date">2026/08</div><div class="time-dot"></div><div class="time-body"><b>ABCL635 Phase 2好結果</b><p>頻度・重症度低下、睡眠改善、良好な忍容性が報じられました。</p><div class="time-meta"><span class="chip">好材料</span></div></div></div><div class="time-row"><div class="time-date">今後</div><div class="time-dot"></div><div class="time-body"><b>後期試験計画</b><p>試験設計、開始時期、規制協議を確認。</p><div class="time-meta"><span class="chip">最重要</span></div></div></div>',
        "CATALYST_CARDS": "".join(cards) + '<p class="small">※下の％は、この結果が出た後に市場が材料を評価し直した場合の上昇・下落幅の目安です。実際の値動きは地合い、直前の株価上昇、同時ニュースで変わります。</p>',
        "DEPENDENCY_ROWS": '<div class="signal"><div><b>ABCL635と資金余力</b><span class="up">連動</span></div><p>良いデータでも次試験に進む資金余力が重要です。</p></div><div class="signal"><div><b>提携と下流権利</b><span class="flat">長期</span></div><p>短期株価より長期価値の材料です。</p></div><div class="signal"><div><b>追加候補</b><span class="up">分散</span></div><p>ABCL635依存を下げる材料になります。</p></div>',
        "WATCH_ROWS": '<div class="signal"><div><b>Phase 2詳細</b><span class="up">最重要</span></div><p>頻度・重症度の改善幅、睡眠、全体的状態、安全性を確認します。</p></div><div class="signal"><div><b>後期試験設計</b><span class="flat">必須</span></div><p>用量、試験規模、主要評価項目、開始時期を確認します。</p></div><div class="signal"><div><b>流動性</b><span class="up">重要</span></div><p>現金、有価証券、政府資金、バーンを確認します。</p></div><div class="signal"><div><b>提携進捗</b><span class="flat">長期</span></div><p>下流権利付きプログラムの質を確認します。</p></div>',
        "ASSUMPTION_ROWS": tr("評価基準株価", usd(P0), "市場データで確認", DATE, "Phase 2好結果後の更新基準") + tr("利用可能流動性", "約$655M", "会社Q1リリース", "2026/03/31", "政府資金含む") + tr("ABCL635 Phase 2", "好結果報道", "報道・公式情報確認", "2026/08", "詳細確認を継続") + tr("次の材料", "後期試験計画", "会社方針と報道から推定", "今後", "最重要"),
        "SOURCE_DETAILS": f'<ul><li>{source_link("公式IR概要", "overview")}</li><li>{source_link("四半期決算資料", "quarterly")}</li><li>{source_link("Q1決算リリース", "q1")}</li><li>{source_link("ABCL635 Phase 2報道", "phase2_news")}</li><li>{source_link("SEC 10-Q", "sec_q1")}</li><li>{source_link("株価・統計", "quote")}</li></ul><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p>',
        "VALIDATION_DETAILS": "<p>PASS：公式IR、四半期決算ページ、Q1決算リリース、SEC 10-Q、ABCL635 Phase 2報道、株価・統計ページを確認。WARN：Q2詳細本文は取得できた公式ページで未確認のため、公開後も更新確認が必要です。</p>",
        "UPDATE_HISTORY": f"<p>{DATE}：更新。ABCL635 Phase 2好結果報道、株価反応、後期試験計画への確認軸を反映。</p>",
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
    stocks_payload["stocks"].sort(key=lambda item: item["order"])
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
        "updatedAt": "2026-08-13T00:00:00+00:00",
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
            "catalysts": 88.0,
            "businessRisk": 70.0,
        },
        "reportRevision": "abcellera-abcl-2026-08-13",
        "summary": "ABCL635のPhase 2好結果で株価は再評価。次は後期試験設計、資金消費、データ詳細を確認するため中立からやや強気。",
    }
    signals_path.write_text(json.dumps(signals_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_reports()
    upsert_site_data()


if __name__ == "__main__":
    main()
