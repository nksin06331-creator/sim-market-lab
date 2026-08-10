"""Generate Zeta Global report HTML files from the bundled SiM templates."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from generate_rocket_lab_reports import dl, li, render_template, th, tr


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stocks" / "zeta-global-zeta"

COMPANY = "ゼータ・グローバル・ホールディングス"
TICKER = "ZETA"
DATE = "2026-08-11"
P0 = 27.33
PREVIOUS_CLOSE = 26.64
SHARES_M = 251.01
MARKET_CAP_B = P0 * SHARES_M / 1000

BEAR = 20.00
BASE = 32.00
BULL = 42.00
BAND_POSITION = (P0 - BEAR) / (BULL - BEAR) * 100
SIGNAL_POSITION = round(0.60 * round(BAND_POSITION, 1) + 0.25 * 82.0 + 0.15 * 58.0, 1)

SOURCES = {
    "ir": "https://investors.zetaglobal.com/",
    "q2": "https://www.businesswire.com/news/home/20260804939577/en/Zeta-Global-Reports-20th-Consecutive-Beat-and-Raise-Quarter-Achieves-the-Rule-of-64-and-Generates-Positive-GAAP-Net-Income-in-2Q26",
    "q1": "https://investors.zetaglobal.com/news/news-details/2026/Zeta-Global-Revenue-Growth-Accelerates-to-50-and-Beats-and-Raises-for-Its-19th-Consecutive-Quarter-on-the-Heels-of-the-Athena-by-Zeta-Launch/default.aspx",
    "palantir": "https://zetaglobal.com/news/palantir-and-zeta-global-announce-strategic-partnership/",
    "credit": "https://www.businesswire.com/news/home/20260727428321/en/Zeta-Global-Closes-%241-Billion-Credit-Facility-for-Mergers-Acquisitions-Share-Repurchases-and-General-Corporate-Purposes",
    "presentations": "https://investors.zetaglobal.com/events-and-presentations/presentations/default.aspx",
    "quote": "https://stockanalysis.com/stocks/zeta/",
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
        f'{source_link("公式IR", "ir")}、'
        f'{source_link("2026年2Q決算リリース", "q2")}、'
        f'{source_link("2026年1Q決算リリース", "q1")}、'
        f'{source_link("Palantir提携リリース", "palantir")}、'
        f'{source_link("株価・統計", "quote")}を確認しました。'
        "本文の数値は2026年8月11日時点で取得できた公開情報に基づきます。"
        '</p><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p></div></details>'
    )
    terms = [
        ("Zeta Marketing Platform", "企業が顧客獲得、維持、成長を一つの基盤で行うマーケティングクラウドです。"),
        ("Zeta Data Cloud", "顧客データ、行動シグナル、企業内データをAI判断に使うためのデータ基盤です。"),
        ("Athena by Zeta", "ZetaのAIインテリジェンス層です。マーケティング判断や実行をAIで支援します。"),
        ("Super-Scaled Customer", "直近12カ月で100万ドル以上の売上を生む大型顧客です。"),
        ("ARPU", "顧客あたり平均売上です。大型顧客の深掘りが進むほど上がります。"),
        ("Rule of 64", "売上成長率と調整後EBITDAマージンの合計が64以上という高成長・収益性の目安です。"),
        ("Beat and Raise", "決算が会社予想を上回り、同時に今後の見通しも引き上げることです。"),
        ("FCF", "フリーキャッシュフローです。成長投資後に残る現金創出力を見ます。"),
        ("Palantir Foundry", "Palantirの企業データ統合・運用基盤です。Zeta Data Cloud再設計の材料です。"),
        ("Marigold", "Zetaが取得したエンタープライズソフトウェア事業です。成長率を見る際はM&A寄与を分けます。"),
    ]
    return {
        "TICKER": TICKER,
        "COMPANY_NAME": COMPANY,
        "INDUSTRY": "AIマーケティングクラウド・顧客データ基盤",
        "DATE": DATE,
        "TAGLINE": "Zeta Data CloudとAthena by Zetaを使い、企業の顧客データをAIでマーケティング判断・実行につなげるAIマーケティングクラウド企業です。",
        "HERO_TAGS": '<span class="hero-tag">米国株</span><span class="hero-tag">AI</span><span class="hero-tag">マーケティングクラウド</span><span class="hero-tag">NYSE</span>',
        "HERO_STATS": (
            f'<div class="stat"><div class="stat-value">{usd(P0)}</div><div class="stat-label">評価基準株価</div><div class="stat-note">2026/08/10場中確認</div></div>'
            f'<div class="stat"><div class="stat-value">${MARKET_CAP_B:.1f}B</div><div class="stat-label">時価総額の目安</div><div class="stat-note">約2.51億株で計算</div></div>'
            '<div class="stat"><div class="stat-value up">$443M</div><div class="stat-label">2026年2Q売上</div><div class="stat-note">前年比+44%</div></div>'
            '<div class="stat"><div class="stat-value">20</div><div class="stat-label">連続Beat & Raise</div><div class="stat-note">2Q 2026時点</div></div>'
        ),
        "SEC2_LABEL": "事業モデル",
        "SEC3_LABEL": "AI戦略",
        "SEC4_LABEL": "決算",
        "SEC5_LABEL": "競合比較",
        "SEC1_TLDR": li("ZetaはAIマーケティングクラウドと顧客データ基盤を提供するNYSE上場企業です。", "*") + li("2Q 2026は売上443百万ドル、前年比44%、20四半期連続のBeat and Raiseでした。", "*") + li("株価は52週高値圏に近く、AI期待の織り込みとバリュエーションには注意です。", "!"),
        "SEC1_FACTS": (
            "<div><dt>正式社名</dt><dd>Zeta Global Holdings Corp.</dd></div><div><dt>本社</dt><dd>New York, New York</dd></div>"
            "<div><dt>上場</dt><dd>NYSE（ZETA）</dd></div><div><dt>業種</dt><dd>ソフトウェア・AIマーケティング</dd></div>"
            "<div><dt>創業</dt><dd>2007年</dd></div><div><dt>従業員</dt><dd>約3,300人</dd></div>"
        ),
        "SEC1_CARDS": (
            '<div class="card-sm"><span class="card-emoji">🧠</span><div class="card-title">何をしている</div><div class="card-desc">企業の顧客データをAIでマーケティング判断へ変えます。</div></div>'
            '<div class="card-sm"><span class="card-emoji">📈</span><div class="card-title">成長</div><div class="card-desc">2Q売上は前年比44%、大型顧客も増加しています。</div></div>'
            '<div class="card-sm"><span class="card-emoji">🤝</span><div class="card-title">材料</div><div class="card-desc">OpenAI、Snowflake、Palantirとの連携がAI戦略を支えます。</div></div>'
            '<div class="card-sm"><span class="card-emoji">⚠️</span><div class="card-title">注意</div><div class="card-desc">高成長期待、M&A統合、競争、株価上昇後の反動に注意です。</div></div>'
        ),
        "SEC1_BIZMODEL": (
            '<li><span class="kp-emoji">🧠</span><span class="kp-text"><b>AI判断基盤</b>：Athenaがデータから顧客理解とマーケティング判断を支援します。</span></li>'
            '<li><span class="kp-emoji">📊</span><span class="kp-text"><b>データクラウド</b>：大規模な顧客・行動データを活用します。</span></li>'
            '<li><span class="kp-emoji">🎯</span><span class="kp-text"><b>実行まで一体</b>：メール、広告、モバイル、店頭など複数チャネルへつなげます。</span></li>'
        ),
        "SEC1_HIGHLIGHT": '<div class="highlight"><h3>ZETAを見る基本ルール</h3><p>ZETAは売上成長、調整後EBITDA、FCF、大型顧客数、Athena/Palantir連携の商業化を見ます。高成長株なので、決算が良くても株価が先に織り込んでいるかを確認します。</p></div>',
        "SEC2_ICON": "🧠",
        "SEC2_TITLE": "AIマーケティングの<span class=\"g\">基本</span>",
        "SEC2_SUB": "顧客データをAI判断と実行へ",
        "SEC2_TLDR": li("Zetaは顧客データ、AI、マーケティング実行を一つの基盤で提供します。", "*") + li("大型顧客の増加とARPU上昇が成長の中心です。", "*") + li("広告・マーケティング予算の景気感応度と競争には注意です。", "!"),
        "SEC2_CONTENT": (
            '<p class="lead">Zetaは、企業が持つ顧客データと外部シグナルをAIで分析し、誰に何をいつ届けるかを判断し、複数チャネルで実行する基盤です。</p>'
            '<div class="sowhat"><p><b>つまり</b>、ZETAは単なる広告会社ではなく、企業の顧客データを収益化するAIインフラ企業として評価され始めています。</p></div>'
            '<div class="term-list">'
            + details("Zeta Data Cloud", "企業の顧客理解を深めるデータ基盤です。データ量と精度がAI判断の質を左右します。", True)
            + details("Athena by Zeta", "AIエージェントのように、分析、判断、実行を支援するインテリジェンス層です。")
            + details("大型顧客戦略", "Super-Scaled Customer数とARPUが伸びるほど、既存顧客の深掘りが進んでいると見ます。")
            + details("収益性", "売上成長だけでなく、調整後EBITDAとFCFが同時に伸びている点が強みです。")
            + "</div>"
        ),
        "SEC3_TITLE": "Athenaと<span class=\"g\">提携</span>",
        "SEC3_SUB": "OpenAI、Snowflake、Palantirが材料",
        "SEC3_TLDR": li("AthenaはZetaのAI戦略の中心です。", "*") + li("Palantir Foundry上でData Cloudを再設計する提携は、企業AIインフラ化の材料です。", "*") + li("提携が売上にどれだけ変わるかは、今後の確認が必要です。", "!"),
        "SEC3_CONTENT": (
            '<div class="product-grid"><div class="product-box"><div class="product-symbol">AI</div><div class="product-name">Athena</div><div class="product-use">マーケティング判断のAI層。</div></div>'
            '<div class="product-box"><div class="product-symbol">PLTR</div><div class="product-name">Palantir</div><div class="product-use">Foundry上でData Cloudを再設計。</div></div>'
            '<div class="product-box"><div class="product-symbol">SNOW</div><div class="product-name">Snowflake</div><div class="product-use">AIマーケティング向け標準化。</div></div></div>'
            '<div class="term-list">'
            + details("Palantir提携", "Zeta Data CloudをPalantir Foundry上で再設計し、企業データとマーケティング実行を結ぶ狙いです。", True)
            + details("OpenAI連携", "Athenaの回答駆動型マーケティングを支える重要なAI材料として扱います。")
            + details("Snowflake連携", "AIマーケティング向けデータ標準化と企業データ接続の材料です。")
            + details("確認ポイント", "提携発表だけでなく、実際の顧客導入、契約金額、ARPU上昇に変わるかを見ます。")
            + "</div>"
        ),
        "SEC4_TITLE": "決算と<span class=\"g\">ガイダンス</span>",
        "SEC4_SUB": "20四半期連続のBeat and Raise",
        "SEC4_TLDR": li("2Q 2026売上は443百万ドル、前年比44%でした。", "*") + li("調整後EBITDAは92百万ドル、FCFは58百万ドルでした。", "*") + li("2026年売上ガイダンス中央値は18.18億ドルへ引き上げられました。", "!"),
        "SEC4_CONTENT": (
            '<ul class="keypoints"><li><span class="kp-emoji">📈</span><span class="kp-text"><b>売上</b>：2Qは$443M、前年比+44%。</span></li>'
            '<li><span class="kp-emoji">💵</span><span class="kp-text"><b>利益</b>：GAAP純利益$8M、調整後EBITDA$92M。</span></li>'
            '<li><span class="kp-emoji">🔁</span><span class="kp-text"><b>見通し</b>：2026年売上ガイダンス中央値は$1.818B。</span></li></ul>'
            '<div class="sowhat"><p><b>つまり</b>、ZETAは高成長だけでなくキャッシュ創出も伸びています。次はこの勢いが3Q、4Qでも続くかを確認します。</p></div>'
        ),
        "SEC5_TITLE": "競合と<span class=\"g\">比べる</span>",
        "SEC5_SUB": "CRM、ADBE、ORCL、TTDなどと競争",
        "SEC5_TLDR": li("競合はSalesforce、Adobe、Oracle、The Trade Desk、Braze、Klaviyoなどです。", "*") + li("ZetaはデータクラウドとAI判断、実行まで一体の点を差別化します。", "*") + li("大手競合は販売網と既存顧客基盤が強いため、勝率と解約率を確認します。", "!"),
        "SEC5_CONTENT": (
            '<div class="table-wrap"><table class="compare-table"><thead><tr><th>対象</th><th>強み</th><th>注意点</th></tr></thead><tbody>'
            '<tr><td class="me">Zeta</td><td>AI、データクラウド、顧客シグナル、成長率。</td><td>期待が高く、M&A統合と競争が課題。</td></tr>'
            '<tr><td>Salesforce / Adobe</td><td>既存顧客、製品網、販売力。</td><td>複雑化しやすく、Zetaの置換余地もある。</td></tr>'
            '<tr><td>Oracle</td><td>大企業基盤とデータ管理。</td><td>マーケティング特化の速度では差が出る。</td></tr>'
            '<tr><td>TTD / 広告系</td><td>広告配信とメディア接続。</td><td>Zetaは顧客データとCRM寄りで差別化。</td></tr>'
            '</tbody></table></div><div class="highlight"><h3>差別化の見方</h3><p>ZETAはAIの話題だけでなく、既存顧客の支出拡大、大型顧客数、FCF成長で実行力を確認します。</p></div>'
        ),
        "SEC6_TLDR": li("Athena、Data Cloud、Super-Scaled Customer、Rule of 64、FCFを押さえると読みやすいです。", "*") + li("AI提携が売上とARPUに変わるかが重要です。", "*") + li("株価が高値圏に近いため、ガイダンス未達には注意です。", "!"),
        "SEC6_CONTENT": '<div class="term-list">' + "".join(details(name, body) for name, body in terms) + "</div>",
        "SEC7_TLDR": li("最大材料は3Q決算、Athena導入、Palantir連携の商業化です。", "*") + li("Zeta Live 2026もAI戦略の追加材料になります。", "*") + li("高期待の反動、競争、広告予算減速には注意です。", "!"),
        "SEC7_CONTENT": (
            '<div class="timeline"><div class="tl-row"><div class="tl-date">2026/06/23</div><div class="tl-title">Palantir提携 <span class="signal bull">AI</span></div><div class="tl-desc">Data CloudをFoundry上で再設計する戦略提携。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/07/27</div><div class="tl-title">$1B信用枠 <span class="signal neutral">資金</span></div><div class="tl-desc">M&A、自社株買い、一般用途に使える資金枠。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/08/04</div><div class="tl-title">2Q決算 <span class="signal bull">好決算</span></div><div class="tl-desc">売上+44%、20四半期連続Beat and Raise。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/10/08</div><div class="tl-title">Zeta Live 2026 <span class="signal neutral">確認</span></div><div class="tl-desc">AIマーケティングと事業戦略の追加説明が期待されます。</div></div></div>'
            '<div class="info-row"><div class="info-box info-box-green"><div class="info-title info-title-green">追い風</div><div class="info-text">高成長、GAAP黒字、FCF、AI提携、大型顧客。</div></div>'
            '<div class="info-box info-box-amber"><div class="info-title info-title-amber">確認</div><div class="info-text">3Q、Athena導入、Palantir商業化、M&A。</div></div>'
            '<div class="info-box info-box-red"><div class="info-title info-title-red">リスク</div><div class="info-text">高期待、競争、広告予算、統合リスク。</div></div></div>'
            + source_details
        ),
    }


def scenario_values() -> dict[str, str]:
    probs = {"bear": 0.25, "base": 0.50, "bull": 0.25}
    expected = BEAR * probs["bear"] + BASE * probs["base"] + BULL * probs["bull"]
    own_score = (expected - BEAR) / (BULL - BEAR) * 100
    endpoint_rr = (BULL - P0) / max(P0 - BEAR, 0.01)
    expected_return = expected / P0 - 1
    bear_downside = (P0 - BEAR) / P0
    score = round(max(0, min(100, 50 + expected_return * 100 - probs["bear"] * bear_downside * 100)))
    return {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "NYSE",
        "VALUATION_DATE": DATE,
        "METHOD": "高成長SaaS・AIインフラ向けシナリオ評価",
        "VERDICT_STATUS": "好決算後の中立からやや強気",
        "VERDICT_LINE_1": f"評価基準株価は悲観〜楽観レンジの{BAND_POSITION:.1f}%地点です。成長とAI材料は強い一方、株価は高値圏に近づいています。",
        "VERDICT_LINE_2": "この試算は2026年8月11日時点で取得できた公開情報に基づきます。3Q決算、Athena導入、Palantir連携の進捗で更新が必要です。",
        "SCORE": str(score),
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "2026/08/10場中確認",
        "BASE_PRICE": usd(BASE),
        "BASE_DELTA": pct(BASE / P0 - 1),
        "EXPECTED_VALUE": usd(expected),
        "EXPECTED_DELTA": pct(expected / P0 - 1),
        "RISK_CLASS": "中〜高",
        "RISK_NOTE": "高成長AI株、期待織り込みと競争リスク",
        "WARN_BAND": "",
        "WARN_MESSAGE": "高成長株のため、決算が良くても株価が先に織り込む場合があります。",
        "SNAPSHOT_LEAD": "今の株価は標準ケース手前です。2Q好決算とAI提携を評価しつつ、さらなる上値には3Q継続成長とAI商業化の証拠が必要です。",
        "BAND_POSITION": f"{BAND_POSITION:.1f}%",
        "ZONE_JUDGE": "標準ケース手前",
        "ZONE_NOTE": "3QもBeat and Raiseなら標準〜楽観へ、成長鈍化なら悲観側へ寄ります。",
        "BEAR_PRICE": usd(BEAR),
        "BULL_PRICE": usd(BULL),
        "ENDPOINT_RR": f"{endpoint_rr:.1f}倍",
        "MARKET_SCORE": str(round(BAND_POSITION)),
        "OWN_SCORE": str(round(own_score)),
        "MARKET_REVERSE_NOTE": "市場はAIインフラ化と好決算をかなり評価していますが、まだ楽観ケース全体までは織り込んでいません。",
        "SCENARIOS_LEAD": "現在株価から独立して、売上成長、EBITDA、FCF、AI提携、競争リスクを置きました。",
        "BEAR_PROB": "25%",
        "BASE_PROB": "50%",
        "BULL_PROB": "25%",
        "BEAR_DELTA": pct(BEAR / P0 - 1),
        "BULL_DELTA": pct(BULL / P0 - 1),
        "BEAR_DL_ROWS": dl([("成長", "30%台前半へ鈍化"), ("AI", "売上寄与限定"), ("倍率", "圧縮"), ("株価", usd(BEAR))]),
        "BASE_DL_ROWS": dl([("成長", "40%前後維持"), ("利益", "EBITDA/FCF拡大"), ("AI", "ARPUに寄与"), ("株価", usd(BASE))]),
        "BULL_DL_ROWS": dl([("成長", "40%超継続"), ("提携", "商業化加速"), ("倍率", "AIインフラ株として拡大"), ("株価", usd(BULL))]),
        "PRICE_ZONE_ROWS": '<div class="zone"><div><b>$20未満</b><span>★★★</span></div><p>成長鈍化や倍率圧縮を強く織り込む価格帯です。</p></div><div class="zone"><div><b>$20〜$32</b><span>★★★</span></div><p>好決算後の中立圏。今の株価はここです。</p></div><div class="zone"><div><b>$32〜$42</b><span>★★</span></div><p>AI商業化と高成長継続を評価する価格帯です。</p></div><div class="zone"><div><b>$42超</b><span>★</span></div><p>複数四半期の上方修正とAI収益化が必要です。</p></div>',
        "SIGNAL_ROWS": '<div class="signal"><div><b>2Q決算</b><span class="up">強い</span></div><p>売上+44%、GAAP黒字、FCF増加。</p></div><div class="signal"><div><b>AI提携</b><span class="up">材料</span></div><p>OpenAI、Snowflake、Palantirが評価材料です。</p></div><div class="signal"><div><b>株価水準</b><span class="flat">確認</span></div><p>52週高値に近く、期待織り込みを確認します。</p></div><div class="signal"><div><b>競争</b><span class="down">注意</span></div><p>Salesforce、Adobe、Oracleなど大手と競争します。</p></div>',
        "POSITIVES": "<li>2Q売上は前年比44%で、20四半期連続Beat and Raiseです。</li><li>GAAP純利益とFCFが伸び、成長と収益性が両立しています。</li><li>Palantir、OpenAI、Snowflake連携でAIインフラ色が強まりました。</li><li>大型顧客数とARPUが伸びています。</li>",
        "CONCERNS": "<li>株価が好決算後に上昇し、期待が高まっています。</li><li>広告・マーケティング予算は景気影響を受けます。</li><li>M&A統合と大型提携の売上化には実行リスクがあります。</li><li>大手ソフトウェア企業との競争が続きます。</li>",
        "FORMULA": "高成長SaaS/AI株のため、売上倍率、成長率、EBITDA、FCF、提携商業化をまとめたシナリオ法で見ました。",
        "CALC_TABLE_HEAD": th("ケース", "主な前提", "価値の見方", "計算株価", "確率", "確率加重"),
        "CALC_TABLE_ROWS": tr("悲観", "成長鈍化", "倍率圧縮", usd(BEAR), "25%", "$5.00") + tr("標準", "高成長継続", "好決算を評価", usd(BASE), "50%", "$16.00") + tr("楽観", "AI商業化加速", "AIインフラ株として再評価", usd(BULL), "25%", "$10.50"),
        "CALC_NOTICE": "現在株価に合わせた逆算ではありません。高成長株のため、ガイダンスと倍率の変化で評価が大きく動きます。",
        "CONDITIONS": details("悲観ケース：$20 / 確率25%", "広告予算や競争で成長が鈍化し、AI提携の売上寄与が限定的なケースです。", True) + details("標準ケース：$32 / 確率50%", "2Qの勢いが続き、ガイダンス達成と大型顧客拡大が確認されるケースです。") + details("楽観ケース：$42 / 確率25%", "AI提携が商業化し、AthenaがARPUと新規顧客獲得を押し上げるケースです。"),
        "SENSITIVITY_HEAD": th("前提", "弱い", "標準", "強い"),
        "SENSITIVITY_ROWS": tr("売上成長", "30%台前半 → $20", "40%前後 → $32", "40%超継続 → $42") + tr("AI寄与", "話題先行", "ARPUに寄与", "大型契約化") + tr("倍率", "SaaS倍率圧縮", "高成長SaaS評価", "AIインフラ評価"),
        "SENSITIVITY_NOTE": "ZETAは利益も出始めていますが、株価はまだ成長率とAI期待への感応度が高いです。",
        "DIST_LEAD": "モンテカルロではなく、好決算後の3点シナリオです。",
        "DIST_ROWS": '<div class="dist-row"><span>$20</span><div class="track"><i style="width:25%"></i></div><b>25%</b></div><div class="dist-row"><span>$32</span><div class="track"><i style="width:50%"></i></div><b>50%</b></div><div class="dist-row"><span>$42</span><div class="track"><i style="width:25%"></i></div><b>25%</b></div>',
        "DIST_SUMMARY": "期待値は標準ケース付近ですが、AI提携の売上化次第で楽観側へ寄ります。",
        "WATCH_ROWS": '<div class="signal"><div><b>3Q決算</b></div><p>売上、EBITDA、FCF、ガイダンスを確認します。</p></div><div class="signal"><div><b>Athena導入</b></div><p>AI利用、商業化、ARPU寄与を確認します。</p></div><div class="signal"><div><b>Palantir提携</b></div><p>導入顧客、売上寄与、Foundry連携の進捗を確認します。</p></div>',
        "ASSUMPTIONS_ROWS": tr("評価基準株価", usd(P0), "市場データで確認", DATE, "2026/08/10場中確認") + tr("2Q売上", "$443M", "会社リリース", "2026/06/30", "前年比+44%") + tr("2026年売上見通し", "$1.818B midpoint", "会社リリース", "2026/08/04", "上方修正") + tr("時価総額", f"${MARKET_CAP_B:.1f}B", "株価・株式数から計算", DATE, "概算"),
        "DEEPDIVE_DETAILS": details("手法選定理由", "ZETAは利益が出始めた高成長AIソフト株です。PER単独ではなく、成長率、EBITDA、FCF、AI提携の商業化をシナリオ化します。", True) + details("株価水準について", "株価は好決算後に52週高値圏へ近づいています。良い会社でも期待が高い時は下振れに注意します。") + details("主要出典", f'{source_link("2Q決算リリース", "q2")}、{source_link("Palantir提携", "palantir")}、{source_link("公式IR", "ir")}、{source_link("株価・統計", "quote")}。<br><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>'),
        "DISCLAIMER": "本資料は情報提供を目的とした試算です。投資助言ではありません。高成長株は決算、金利、倍率、ガイダンスで大きく変動します。",
        "FOOTER_NOTE": f"SiM MARKET LAB｜{COMPANY}（{TICKER}）株価シナリオ｜作成日 {DATE}",
    }


def catalyst_values() -> dict[str, str]:
    non_quant = '<div class="priced"><div class="priced-head"><span>主要材料の推定織り込み</span><b>58%</b></div><p>仮定：2Q好決算を75%、2026年ガイダンス引き上げを70%、Palantir/OpenAI/Snowflake連携を45%、Zeta Liveと3Q継続成長を40%として置き、株価上昇後の期待織り込みを控除しました。</p><p>読み方：株価は好決算をかなり織り込んでいますが、AI提携の売上化と3Q継続成長はまだ一部だけです。</p><p>次に見る数字：3Q売上、調整後EBITDA、FCF、Super-Scaled Customer数、ARPU、Athena利用、Palantir連携の顧客導入です。</p><p>再計算方法：各材料の成功確率を更新し、レポート2のシナリオ株価を再計算します。</p></div>'
    impact_map = {
        "3Q決算と再上方修正": ("+18〜35%", "-7〜+10%", "-18〜-32%", "2Q後に株価が上がっているため、次の決算継続性が短期の最大材料です。"),
        "Athenaの商業化": ("+20〜45%", "-8〜+12%", "-15〜-28%", "AI利用がARPUや新規契約に変わると、AIインフラ株として倍率が上がるためです。"),
        "Palantir/OpenAI/Snowflake連携": ("+15〜38%", "-6〜+10%", "-12〜-24%", "提携は強い材料ですが、売上化までの距離があるため決算より小さめにしています。"),
        "Zeta Live 2026": ("+8〜20%", "-4〜+7%", "-8〜-16%", "戦略発表イベントですが、決算数字ほど直接価値を変えないため小さめです。"),
    }
    description_map = {
        "3Q決算と再上方修正": "2Qの強さが一過性ではなく続くかを確認する材料です。売上、EBITDA、FCF、ガイダンスの再上方修正が焦点です。",
        "Athenaの商業化": "AthenaがAIの話題から、顧客の利用増、ARPU上昇、新規契約へ変わるかを確認します。",
        "Palantir/OpenAI/Snowflake連携": "ZetaのAIインフラ化を支える外部連携です。発表だけでなく、導入顧客と収益化が重要です。",
        "Zeta Live 2026": "年次イベントでAI戦略、顧客事例、長期目標の追加説明が出る可能性があります。",
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
<div class="evidence"><div><h4>根拠</h4><ul>{evidence}</ul></div><div><h4>反証・先行指標</h4><ul><li>売上成長率の鈍化</li><li>ARPUや大型顧客の伸び鈍化</li><li>AI提携の売上寄与が見えない</li></ul></div></div>
</article>'''

    cards = [
        card("3Q決算と再上方修正", "2026年秋", '<span class="chip">重要度5</span><span class="chip">最重要</span>', '<span>売上</span><i>→</i><span>利益</span><i>→</i><span>ガイダンス</span>', "3Qも売上40%前後、EBITDA拡大、再上方修正なら楽観側です。", "会社見通しどおりなら標準ケースを維持します。", "成長率鈍化や見通し据え置きなら期待剥落です。", "<li>2Qは売上$443M、前年比+44%、20四半期連続Beat and Raise。</li><li>2026年売上ガイダンス中央値を$1.818Bへ引き上げ。</li>"),
        card("Athenaの商業化", "継続確認", '<span class="chip">重要度4</span><span class="chip blue">AI</span>', '<span>利用</span><i>→</i><span>ARPU</span><i>→</i><span>売上</span>', "Athena利用が顧客拡大やARPU上昇として明確に出る状態です。", "導入は進むが数字への寄与は確認待ちです。", "話題先行で、契約や利用指標への反映が弱い状態です。", "<li>会社は2QでAI採用と利用の測定フレームワークを導入。</li><li>AthenaはZetaのAI戦略の中心です。</li>"),
        card("Palantir/OpenAI/Snowflake連携", "2026年後半", '<span class="chip">重要度4</span><span class="chip blue">提携</span>', '<span>連携</span><i>→</i><span>導入</span><i>→</i><span>収益化</span>', "共同顧客や契約金額が見え、提携が売上に変わる状態です。", "戦略提携として期待が続く状態です。", "追加進捗がなく、材料が消化される状態です。", "<li>PalantirとData CloudをFoundry上で再設計する提携を発表。</li><li>2QリリースでOpenAI、Snowflake、Palantir連携の勢いに言及。</li>"),
        card("Zeta Live 2026", "2026/10/08", '<span class="chip">重要度3</span><span class="chip blue">イベント</span>', '<span>戦略</span><i>→</i><span>顧客事例</span><i>→</i><span>期待</span>', "新しいAI顧客事例や長期目標引き上げが出れば上振れです。", "既存戦略の説明中心なら中立です。", "新材料が乏しいと短期材料としては弱くなります。", "<li>会社はZeta Live 2026を10月8日に開催予定。</li><li>AIマーケティングとBusiness Intelligenceが主題です。</li>"),
    ]
    return {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "NYSE",
        "VALUATION_DATE": DATE,
        "LAST_UPDATED": DATE,
        "REPORT_STATUS": "好決算後",
        "SUMMARY_LINE_1": "3Q決算、Athena商業化、Palantir/OpenAI/Snowflake連携、Zeta Liveが主な材料です。",
        "SUMMARY_LINE_2": "足りない情報は仮定を置き、主要材料の織り込み度を58%と推定します。",
        "OVERALL_PRICED_IN": "58%",
        "OVERALL_PRICED_LABEL": "主要材料の推定織り込み",
        "PRICED_IN_CONFIDENCE": "中",
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "2026/08/10場中確認",
        "NEXT_CATALYST_TITLE": "3Q決算と再上方修正",
        "NEXT_CATALYST_WINDOW": "2026年秋",
        "DATE_CONFIDENCE": "通常決算サイクル",
        "CATALYST_COUNT": "4件",
        "WARN_BAND": "",
        "NO_CATALYST_NOTICE": "",
        "OVERALL_PRICED_BLOCK": non_quant,
        "PRICED_IN_METHOD": "2Q決算、2026年ガイダンス、AI提携、次回決算を標準ケース価値へ重み付けして推定。",
        "SURPRISE_UP": "3Qも再上方修正、AthenaのARPU寄与、Palantir連携の顧客導入が同時に確認されることです。",
        "SURPRISE_DOWN": "売上成長鈍化、AI提携の売上寄与不足、広告予算減速、M&A統合負担です。",
        "PRIMARY_RISK": "株価が好決算をかなり織り込み、次の決算で高い期待を超えられない場合に下落しやすいことです。",
        "TIMELINE_ROWS": '<div class="time-row"><div class="time-date">2026/06/23</div><div class="time-dot"></div><div class="time-body"><b>Palantir提携</b><p>Data CloudをFoundry上で再設計。</p><div class="time-meta"><span class="chip">AI</span></div></div></div><div class="time-row"><div class="time-date">2026/07/27</div><div class="time-dot"></div><div class="time-body"><b>$1B信用枠</b><p>M&A、自社株買い、一般用途の資金枠。</p><div class="time-meta"><span class="chip blue">資金</span></div></div></div><div class="time-row"><div class="time-date">2026/08/04</div><div class="time-dot"></div><div class="time-body"><b>2Q決算</b><p>売上+44%、GAAP黒字、ガイダンス上方修正。</p><div class="time-meta"><span class="chip">好決算</span></div></div></div><div class="time-row"><div class="time-date">2026/10/08</div><div class="time-dot"></div><div class="time-body"><b>Zeta Live 2026</b><p>AI戦略と顧客事例を確認。</p><div class="time-meta"><span class="chip">イベント</span></div></div></div>',
        "CATALYST_CARDS": "".join(cards) + '<p class="small">※下の％は、この結果が出た後に市場が材料を評価し直した場合の上昇・下落幅の目安です。実際の値動きは地合い、直前の株価上昇、同時ニュースで変わります。</p>',
        "DEPENDENCY_ROWS": '<div class="signal"><div><b>AI提携とARPU</b><span class="up">連動</span></div><p>提携が顧客支出拡大へ変わるかを確認します。</p></div><div class="signal"><div><b>成長と倍率</b><span class="flat">重要</span></div><p>高成長が続くほど高い倍率を維持しやすいです。</p></div><div class="signal"><div><b>FCFと自社株買い</b><span class="up">支え</span></div><p>現金創出が強いほど株主還元余地が出ます。</p></div>',
        "WATCH_ROWS": '<div class="signal"><div><b>3Q売上</b><span class="up">最重要</span></div><p>会社見通しを上回るかを確認します。</p></div><div class="signal"><div><b>Super-Scaled Customer</b><span class="up">重要</span></div><p>大型顧客数とARPUを確認します。</p></div><div class="signal"><div><b>Athena利用</b><span class="flat">AI</span></div><p>利用指標や売上寄与を確認します。</p></div><div class="signal"><div><b>倍率</b><span class="down">注意</span></div><p>好決算後の期待織り込みを確認します。</p></div>',
        "ASSUMPTION_ROWS": tr("評価基準株価", usd(P0), "市場データで確認", DATE, "2026/08/10場中確認") + tr("2Q売上", "$443M", "会社リリース", "2026/06/30", "前年比+44%") + tr("2026年売上見通し", "$1.818B midpoint", "会社リリース", "2026/08/04", "上方修正") + tr("Super-Scaled Customer", "197", "会社リリース", "2026/06/30", "前年比+17%"),
        "SOURCE_DETAILS": f'<ul><li>{source_link("公式IR", "ir")}</li><li>{source_link("2026年2Q決算リリース", "q2")}</li><li>{source_link("Palantir提携リリース", "palantir")}</li><li>{source_link("$1B信用枠リリース", "credit")}</li><li>{source_link("株価・統計", "quote")}</li></ul><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p>',
        "VALIDATION_DETAILS": "<p>PASS：公式IR、2Q決算リリース、1Q決算リリース、Palantir提携、信用枠リリース、株価・統計ページを確認。</p>",
        "UPDATE_HISTORY": f"<p>{DATE}：初版作成。2Q 2026、20四半期連続Beat and Raise、Palantir/OpenAI/Snowflake連携、$1B信用枠を反映。</p>",
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
        "id": "zeta-global-zeta",
        "order": 10,
        "ticker": "ZETA",
        "quoteSymbol": "ZETA",
        "name": "ゼータ・グローバル・ホールディングス",
        "nameEn": "Zeta Global Holdings Corp.",
        "market": "US",
        "marketLabel": "米国株",
        "exchange": "NYSE",
        "currency": "USD",
        "sector": "AIマーケティングクラウド・顧客データ基盤",
        "reports": {
            "company": {"path": "./stocks/zeta-global-zeta/company.html", "available": True},
            "valuation": {"path": "./stocks/zeta-global-zeta/valuation.html", "available": True},
            "catalysts": {"path": "./stocks/zeta-global-zeta/catalysts.html", "available": True},
        },
    }
    stocks_payload["stocks"] = [item for item in stocks_payload["stocks"] if item["id"] != "zeta-global-zeta"]
    stocks_payload["stocks"].append(stock)
    stocks_payload["stocks"].sort(key=lambda item: item["order"])
    stocks_path.write_text(json.dumps(stocks_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    prices_path = ROOT / "data" / "prices.json"
    prices_payload = json.loads(prices_path.read_text(encoding="utf-8"))
    prices_payload.setdefault("prices", {})["zeta-global-zeta"] = {
        "symbol": "ZETA",
        "price": P0,
        "previousClose": PREVIOUS_CLOSE,
        "change": round(P0 - PREVIOUS_CLOSE, 4),
        "changePct": round((P0 - PREVIOUS_CLOSE) / PREVIOUS_CLOSE * 100, 4),
        "currency": "USD",
        "marketTime": "2026-08-10T15:14:00+00:00",
        "updatedAt": "2026-08-11T00:00:00+00:00",
        "status": "ok",
    }
    prices_payload["quoteCount"] = len(prices_payload["prices"])
    prices_path.write_text(json.dumps(prices_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    signals_path = ROOT / "data" / "signals.json"
    signals_payload = json.loads(signals_path.read_text(encoding="utf-8"))
    signals_payload["updatedAt"] = datetime.now(timezone.utc).isoformat()
    signals_payload.setdefault("signals", {})["zeta-global-zeta"] = {
        "position": SIGNAL_POSITION,
        "zone": "中立",
        "asOf": DATE,
        "components": {
            "valuation": round(BAND_POSITION, 1),
            "catalysts": 82.0,
            "businessRisk": 58.0,
        },
        "reportRevision": "zeta-global-zeta-2026-08-11",
        "summary": "2Q好決算、20四半期連続Beat and Raise、AI提携は強い。株価は高値圏に近く、期待織り込み確認前のため中立。",
    }
    signals_path.write_text(json.dumps(signals_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_reports()
    upsert_site_data()


if __name__ == "__main__":
    main()
