"""Generate Credo Technology report HTML files from the bundled SiM templates."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from generate_rocket_lab_reports import dl, li, render_template, th, tr


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stocks" / "credo-crdo"

COMPANY = "クレド・テクノロジー・グループ"
TICKER = "CRDO"
DATE = "2026-08-11"
P0 = 248.00
PREVIOUS_CLOSE = 249.89
SHARES_M = 186.48
MARKET_CAP_B = P0 * SHARES_M / 1000

BEAR = 180.00
BASE = 280.00
BULL = 360.00
BAND_POSITION = (P0 - BEAR) / (BULL - BEAR) * 100
SIGNAL_POSITION = round(0.60 * round(BAND_POSITION, 1) + 0.25 * 80.0 + 0.15 * 62.0, 1)

SOURCES = {
    "ir": "https://investors.credosemi.com/overview/default.aspx",
    "q4": "https://investors.credosemi.com/news-events/news/news-details/2026/Credo-Technology-Group-Holding-Ltd-Reports-Fourth-Quarter-and-Fiscal-Year-2026-Financial-Results/default.aspx",
    "q3": "https://investors.credosemi.com/news-events/news/news-details/2026/Credo-Technology-Group-Holding-Ltd-Reports-Third-Quarter-of-Fiscal-Year-2026-Financial-Results/default.aspx",
    "dust": "https://investors.credosemi.com/news-events/news/news-details/2026/Credo-Completes-Acquisition-of-DustPhotonics/default.aspx",
    "quote": "https://stockanalysis.com/stocks/crdo/",
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
        f'{source_link("FY2026 Q4決算リリース", "q4")}、'
        f'{source_link("FY2026 Q3決算リリース", "q3")}、'
        f'{source_link("DustPhotonics買収リリース", "dust")}、'
        f'{source_link("株価・統計", "quote")}を確認しました。'
        "本文の数値は2026年8月11日時点で取得できた公開情報に基づきます。"
        '</p><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p></div></details>'
    )
    terms = [
        ("AEC", "Active Electrical Cableです。AIサーバーやスイッチを低消費電力で接続する高速ケーブルです。"),
        ("SerDes", "高速データを送受信する半導体IPです。AIデータセンターの接続速度と消費電力に効きます。"),
        ("DSP", "信号を補正・処理する半導体です。光・銅接続の品質を支える部品です。"),
        ("ZeroFlap", "リンク切断や再接続を抑えることを狙うCredoの光トランシーバー製品群です。"),
        ("OmniConnect", "AIメモリー接続向けの製品群です。GPUクラスタのメモリー壁問題が背景です。"),
        ("DustPhotonics", "2026年5月に買収完了したシリコンフォトニクス企業です。光接続の垂直統合を強めます。"),
        ("NPO/CPO", "近接パッケージ光学/共同パッケージ光学です。次世代AIインフラの高速・省電力接続で注目されます。"),
        ("ハイパースケーラー", "大規模クラウド事業者です。AIインフラ投資の主要顧客です。"),
        ("非GAAP粗利率", "株式報酬などを除いた粗利率です。CRDOは高い粗利率を維持している点が評価材料です。"),
        ("ガイダンス", "会社が示す次四半期見通しです。高成長株では株価反応が大きくなります。"),
    ]
    return {
        "TICKER": TICKER,
        "COMPANY_NAME": COMPANY,
        "INDUSTRY": "AIデータセンター接続・高速インターコネクト",
        "DATE": DATE,
        "TAGLINE": "AIデータセンター向けに、高速・省電力の銅接続、光接続、SerDes、DSPを提供する接続半導体企業です。",
        "HERO_TAGS": '<span class="hero-tag">米国株</span><span class="hero-tag">AI</span><span class="hero-tag">半導体</span><span class="hero-tag">Nasdaq</span>',
        "HERO_STATS": (
            f'<div class="stat"><div class="stat-value">{usd(P0)}</div><div class="stat-label">評価基準株価</div><div class="stat-note">2026/08/10場中確認</div></div>'
            f'<div class="stat"><div class="stat-value">${MARKET_CAP_B:.1f}B</div><div class="stat-label">時価総額の目安</div><div class="stat-note">約1.86億株で計算</div></div>'
            '<div class="stat"><div class="stat-value up">$437M</div><div class="stat-label">FY2026 Q4売上</div><div class="stat-note">前年比+157%</div></div>'
            '<div class="stat"><div class="stat-value">$1.4B</div><div class="stat-label">現金・短期投資</div><div class="stat-note">FY2026末</div></div>'
        ),
        "SEC2_LABEL": "事業モデル",
        "SEC3_LABEL": "製品",
        "SEC4_LABEL": "決算",
        "SEC5_LABEL": "競合比較",
        "SEC1_TLDR": li("CredoはAIデータセンターの高速接続を支える半導体・ケーブル企業です。", "*") + li("FY2026 Q4売上は437百万ドル、前年比157%増、非GAAP EPSは1.16ドルでした。", "*") + li("株価はAI接続期待を大きく織り込み、決算や顧客集中への反応が大きい点に注意です。", "!"),
        "SEC1_FACTS": (
            "<div><dt>正式社名</dt><dd>Credo Technology Group Holding Ltd.</dd></div><div><dt>本社</dt><dd>San Jose, California</dd></div>"
            "<div><dt>上場</dt><dd>Nasdaq（CRDO）</dd></div><div><dt>業種</dt><dd>半導体・高速接続</dd></div>"
            "<div><dt>主な製品</dt><dd>AEC、光トランシーバー、DSP、SerDes、リタイマー</dd></div><div><dt>決算期</dt><dd>5月期</dd></div>"
        ),
        "SEC1_CARDS": (
            '<div class="card-sm"><span class="card-emoji">🔌</span><div class="card-title">何をしている</div><div class="card-desc">AIサーバー間の高速・省電力接続を提供します。</div></div>'
            '<div class="card-sm"><span class="card-emoji">🚀</span><div class="card-title">成長</div><div class="card-desc">FY2026売上は約13.35億ドルで前年比約3倍です。</div></div>'
            '<div class="card-sm"><span class="card-emoji">💡</span><div class="card-title">材料</div><div class="card-desc">DustPhotonics買収で光接続の垂直統合を強化しました。</div></div>'
            '<div class="card-sm"><span class="card-emoji">⚠️</span><div class="card-title">注意</div><div class="card-desc">AI期待、顧客集中、競争、半導体サイクルに敏感です。</div></div>'
        ),
        "SEC1_BIZMODEL": (
            '<li><span class="kp-emoji">🔌</span><span class="kp-text"><b>AEC</b>：GPUクラスタ内の高速銅接続で成長しています。</span></li>'
            '<li><span class="kp-emoji">💡</span><span class="kp-text"><b>光接続</b>：ZeroFlap光トランシーバー、光DSP、シリコンフォトニクスを広げます。</span></li>'
            '<li><span class="kp-emoji">🧠</span><span class="kp-text"><b>AIインフラ</b>：GPU利用率、ネットワーク安定性、消費電力低減が価値になります。</span></li>'
        ),
        "SEC1_HIGHLIGHT": '<div class="highlight"><h3>CRDOを見る基本ルール</h3><p>売上成長率、非GAAP粗利率、次四半期ガイダンス、AECから光接続への広がり、主要顧客依存を確認します。良い会社でも期待が高い時は、ガイダンスの少しの弱さで株価が動きます。</p></div>',
        "SEC2_ICON": "🔌",
        "SEC2_TITLE": "AI接続の<span class=\"g\">基本</span>",
        "SEC2_SUB": "GPUクラスタをつなぐ会社",
        "SEC2_TLDR": li("AIデータセンターでは、GPUだけでなくGPU同士をつなぐ接続が重要です。", "*") + li("Credoは銅接続、光接続、DSP、SerDesを組み合わせて提供します。", "*") + li("顧客のAI投資が減速すると、成長期待も下がります。", "!"),
        "SEC2_CONTENT": (
            '<p class="lead">Credoは、AIデータセンター内で大量のデータを速く、安定して、省電力で動かすための接続部品を提供します。</p>'
            '<div class="sowhat"><p><b>つまり</b>、CRDOはGPUそのものではなく、GPUクラスタの性能を引き出す「接続インフラ」の成長株として見ます。</p></div>'
            '<div class="term-list">'
            + details("AEC", "AIクラスタ内の短距離高速接続で使われる銅ケーブルです。消費電力と安定性が評価されます。", True)
            + details("光接続", "データ量が増えるほど光接続の重要性が高まります。DustPhotonics買収でシリコンフォトニクスを加えました。")
            + details("PILOT", "診断・分析ソフトウェア基盤です。接続の安定性や運用改善に関わります。")
            + details("顧客集中", "大口AI顧客の投資計画に売上が左右される可能性があります。")
            + "</div>"
        ),
        "SEC3_TITLE": "AECから<span class=\"g\">光接続</span>へ",
        "SEC3_SUB": "800G、1.6T、3.2Tが焦点",
        "SEC3_TLDR": li("主力はAECと高速接続半導体です。", "*") + li("DustPhotonics買収で、シリコンフォトニクス、NPO、CPO領域を強化しました。", "*") + li("光接続の売上寄与がFY2027にどれだけ伸びるかが確認点です。", "!"),
        "SEC3_CONTENT": (
            '<div class="product-grid"><div class="product-box"><div class="product-symbol">AEC</div><div class="product-name">ZeroFlap AEC</div><div class="product-use">AIクラスタ内の高速銅接続。</div></div>'
            '<div class="product-box"><div class="product-symbol">DSP</div><div class="product-name">Optical DSP</div><div class="product-use">光接続の信号処理。</div></div>'
            '<div class="product-box"><div class="product-symbol">SiPh</div><div class="product-name">DustPhotonics</div><div class="product-use">シリコンフォトニクスを追加。</div></div></div>'
            '<div class="term-list">'
            + details("ZeroFlap", "リンク切断や不安定さを減らし、AIクラスタの稼働効率を高める製品群です。", True)
            + details("OmniConnect", "AIメモリー接続を狙う製品群です。GPUとメモリーのボトルネックが背景です。")
            + details("1.6T", "AIネットワークの高速化に対応する速度帯です。Credoは最大1.6T製品を説明しています。")
            + details("DustPhotonics買収", "SerDes、DSP、シリコンフォトニクス、システム統合までの接続スタックを広げる狙いです。")
            + "</div>"
        ),
        "SEC4_TITLE": "決算と<span class=\"g\">ガイダンス</span>",
        "SEC4_SUB": "売上3倍、Q1も増収見通し",
        "SEC4_TLDR": li("FY2026 Q4売上は437百万ドル、前年比157%増でした。", "*") + li("FY2026通期売上は13.35億ドル、通期非GAAP純利益は6.62億ドルでした。", "*") + li("FY2027 Q1売上見通しは465〜475百万ドルです。", "!"),
        "SEC4_CONTENT": (
            '<ul class="keypoints"><li><span class="kp-emoji">📈</span><span class="kp-text"><b>売上</b>：FY2026 Q4は$437M、前年比+157%。</span></li>'
            '<li><span class="kp-emoji">💵</span><span class="kp-text"><b>利益</b>：Q4非GAAP EPSは$1.16、現金・短期投資は$1.4B。</span></li>'
            '<li><span class="kp-emoji">🔁</span><span class="kp-text"><b>見通し</b>：FY2027 Q1売上は$465M〜$475M。</span></li></ul>'
            '<div class="sowhat"><p><b>つまり</b>、CRDOは売上成長と利益率が同時に強い状態です。次はこの勢いがFY2027も続くかを確認します。</p></div>'
        ),
        "SEC5_TITLE": "競合と<span class=\"g\">比べる</span>",
        "SEC5_SUB": "光・銅接続のAIインフラ銘柄",
        "SEC5_TLDR": li("比較対象はBroadcom、Marvell、Astera Labs、Coherent、Lumentumなどです。", "*") + li("CRDOはAECと接続半導体の専門性、低消費電力、顧客採用で差別化します。", "*") + li("大手半導体企業との競争と顧客集中は継続リスクです。", "!"),
        "SEC5_CONTENT": (
            '<div class="table-wrap"><table class="compare-table"><thead><tr><th>対象</th><th>強み</th><th>注意点</th></tr></thead><tbody>'
            '<tr><td class="me">Credo</td><td>AEC、DSP、SerDes、光接続、AI顧客で高成長。</td><td>期待が高く、顧客集中と競争が課題。</td></tr>'
            '<tr><td>Broadcom / Marvell</td><td>ASIC、ネットワーク、規模、顧客基盤。</td><td>大型で成長率は分散されやすい。</td></tr>'
            '<tr><td>Astera Labs</td><td>AI接続半導体の高成長。</td><td>バリュエーションと競争が焦点。</td></tr>'
            '<tr><td>Coherent / Lumentum</td><td>光部品とレーザー技術。</td><td>サイクルと価格競争に敏感。</td></tr>'
            '</tbody></table></div><div class="highlight"><h3>差別化の見方</h3><p>CRDOは銅接続から光接続へ広がる実行力を見ます。FY2027に光製品が売上成長ドライバーになるかが重要です。</p></div>'
        ),
        "SEC6_TLDR": li("AEC、SerDes、DSP、ZeroFlap、DustPhotonics、ガイダンスを押さえると読みやすいです。", "*") + li("AI接続需要が続くほど評価されます。", "*") + li("株価が高いため、良い決算でも期待との差が重要です。", "!"),
        "SEC6_CONTENT": '<div class="term-list">' + "".join(details(name, body) for name, body in terms) + "</div>",
        "SEC7_TLDR": li("最大材料はFY2027 Q1決算とガイダンスです。", "*") + li("DustPhotonics統合、光接続の採用、OCP/FMS関連発表も確認します。", "*") + li("顧客集中、粗利率低下、AI投資減速には注意です。", "!"),
        "SEC7_CONTENT": (
            '<div class="timeline"><div class="tl-row"><div class="tl-date">2026/05/28</div><div class="tl-title">DustPhotonics買収完了 <span class="signal bull">光接続</span></div><div class="tl-desc">シリコンフォトニクスを加え、光接続ポートフォリオを拡大。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/06/01</div><div class="tl-title">FY2026 Q4決算 <span class="signal bull">好決算</span></div><div class="tl-desc">Q4売上$437M、通期売上$1.335B。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/08/10</div><div class="tl-title">AI接続関連ニュース <span class="signal neutral">確認</span></div><div class="tl-desc">OCP、FMS、AIメモリー接続の発表を確認。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/09/02</div><div class="tl-title">FY2027 Q1決算予定 <span class="signal bull">最重要</span></div><div class="tl-desc">売上$465M〜$475M見通しの達成と次回ガイダンスを確認。</div></div></div>'
            '<div class="info-row"><div class="info-box info-box-green"><div class="info-title info-title-green">追い風</div><div class="info-text">AI接続需要、売上急成長、高粗利率、光接続拡大。</div></div>'
            '<div class="info-box info-box-amber"><div class="info-title info-title-amber">確認</div><div class="info-text">Q1決算、光製品採用、主要顧客の発注。</div></div>'
            '<div class="info-box info-box-red"><div class="info-title info-title-red">リスク</div><div class="info-text">高期待、顧客集中、競争、粗利率低下。</div></div></div>'
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
        "EXCHANGE": "Nasdaq",
        "VALUATION_DATE": DATE,
        "METHOD": "AI半導体・高成長接続インフラ向けシナリオ評価",
        "VERDICT_STATUS": "高成長だが期待織り込み確認",
        "VERDICT_LINE_1": f"評価基準株価は悲観〜楽観レンジの{BAND_POSITION:.1f}%地点です。AI接続需要は強い一方、株価は高期待を織り込んでいます。",
        "VERDICT_LINE_2": "この試算は2026年8月11日時点で取得できた公開情報に基づきます。FY2027 Q1決算と次回ガイダンスで更新が必要です。",
        "SCORE": str(score),
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "2026/08/10場中確認",
        "BASE_PRICE": usd(BASE),
        "BASE_DELTA": pct(BASE / P0 - 1),
        "EXPECTED_VALUE": usd(expected),
        "EXPECTED_DELTA": pct(expected / P0 - 1),
        "RISK_CLASS": "中〜高",
        "RISK_NOTE": "AI半導体高成長株、顧客集中と倍率変動",
        "WARN_BAND": "",
        "WARN_MESSAGE": "AI関連の高成長株のため、決算が良くてもガイダンスや粗利率で大きく動きます。",
        "SNAPSHOT_LEAD": "今の株価は標準ケース手前です。Q4決算は強いですが、さらなる上値にはFY2027 Q1以降の成長継続と光接続の売上化が必要です。",
        "BAND_POSITION": f"{BAND_POSITION:.1f}%",
        "ZONE_JUDGE": "標準ケース手前",
        "ZONE_NOTE": "Q1決算とガイダンスが強ければ標準〜楽観へ、粗利率低下や顧客発注鈍化なら悲観側へ寄ります。",
        "BEAR_PRICE": usd(BEAR),
        "BULL_PRICE": usd(BULL),
        "ENDPOINT_RR": f"{endpoint_rr:.1f}倍",
        "MARKET_SCORE": str(round(BAND_POSITION)),
        "OWN_SCORE": str(round(own_score)),
        "MARKET_REVERSE_NOTE": "市場はAI接続需要をかなり評価していますが、光接続のFY2027成長までは一部織り込みに見ます。",
        "SCENARIOS_LEAD": "現在株価から独立して、売上成長、粗利率、光接続、顧客集中、倍率を置きました。",
        "BEAR_PROB": "25%",
        "BASE_PROB": "50%",
        "BULL_PROB": "25%",
        "BEAR_DELTA": pct(BEAR / P0 - 1),
        "BULL_DELTA": pct(BULL / P0 - 1),
        "BEAR_DL_ROWS": dl([("成長", "AI投資鈍化"), ("粗利率", "低下"), ("倍率", "圧縮"), ("株価", usd(BEAR))]),
        "BASE_DL_ROWS": dl([("成長", "Q1見通し達成"), ("利益", "高粗利率維持"), ("光接続", "徐々に寄与"), ("株価", usd(BASE))]),
        "BULL_DL_ROWS": dl([("成長", "上方修正継続"), ("光接続", "FY2027成長ドライバー"), ("倍率", "AI接続株として拡大"), ("株価", usd(BULL))]),
        "PRICE_ZONE_ROWS": '<div class="zone"><div><b>$180未満</b><span>★★★</span></div><p>成長鈍化や倍率圧縮を強く織り込む価格帯です。</p></div><div class="zone"><div><b>$180〜$280</b><span>★★★</span></div><p>強い成長を評価しつつ、期待織り込みを確認する価格帯です。</p></div><div class="zone"><div><b>$280〜$360</b><span>★★</span></div><p>FY2027も高成長が続くことを評価する価格帯です。</p></div><div class="zone"><div><b>$360超</b><span>★</span></div><p>複数四半期の上方修正と光接続の急拡大が必要です。</p></div>',
        "SIGNAL_ROWS": '<div class="signal"><div><b>FY2026 Q4</b><span class="up">強い</span></div><p>売上+157%、非GAAP EPS $1.16。</p></div><div class="signal"><div><b>Q1見通し</b><span class="up">追い風</span></div><p>売上$465M〜$475Mを会社が提示。</p></div><div class="signal"><div><b>株価水準</b><span class="flat">確認</span></div><p>52週高値からは下にあるが高倍率です。</p></div><div class="signal"><div><b>顧客集中</b><span class="down">注意</span></div><p>大口AI顧客の投資計画に左右されます。</p></div>',
        "POSITIVES": "<li>FY2026売上は前年比約3倍の$1.335Bでした。</li><li>Q4非GAAP粗利率は68.3%で高水準です。</li><li>現金・短期投資は$1.4Bあり、財務余力があります。</li><li>DustPhotonics買収で光接続の成長領域を強化しました。</li>",
        "CONCERNS": "<li>AI関連株として期待が高く、倍率変動が大きいです。</li><li>主要顧客の発注やAI投資サイクルに左右されます。</li><li>光接続の統合と売上化には実行リスクがあります。</li><li>大手半導体・光部品企業との競争が続きます。</li>",
        "FORMULA": "AI半導体高成長株のため、PER単独ではなく、売上成長、粗利率、光接続の寄与、倍率をまとめたシナリオ法で見ました。",
        "CALC_TABLE_HEAD": th("ケース", "主な前提", "価値の見方", "計算株価", "確率", "確率加重"),
        "CALC_TABLE_ROWS": tr("悲観", "成長鈍化", "倍率圧縮", usd(BEAR), "25%", "$45.00") + tr("標準", "高成長継続", "Q1見通し達成", usd(BASE), "50%", "$140.00") + tr("楽観", "光接続加速", "AI接続株として再評価", usd(BULL), "25%", "$90.00"),
        "CALC_NOTICE": "現在株価に合わせた逆算ではありません。高成長株のため、ガイダンスと倍率の変化で評価が大きく動きます。",
        "CONDITIONS": details("悲観ケース：$180 / 確率25%", "AI投資や主要顧客発注が鈍化し、倍率が圧縮されるケースです。", True) + details("標準ケース：$280 / 確率50%", "FY2027 Q1見通しを達成し、高粗利率と売上成長が続くケースです。") + details("楽観ケース：$360 / 確率25%", "光接続とAECが同時に伸び、上方修正が続くケースです。"),
        "SENSITIVITY_HEAD": th("前提", "弱い", "標準", "強い"),
        "SENSITIVITY_ROWS": tr("売上成長", "鈍化 → $180", "Q1見通し達成 → $280", "上方修正継続 → $360") + tr("光接続", "統合遅れ", "徐々に寄与", "大きな成長ドライバー") + tr("倍率", "半導体倍率圧縮", "AI接続評価", "希少高成長評価"),
        "SENSITIVITY_NOTE": "CRDOは利益が出ていますが、株価は成長率とAI接続テーマへの感応度が高いです。",
        "DIST_LEAD": "モンテカルロではなく、FY2027 Q1決算前の3点シナリオです。",
        "DIST_ROWS": '<div class="dist-row"><span>$180</span><div class="track"><i style="width:25%"></i></div><b>25%</b></div><div class="dist-row"><span>$280</span><div class="track"><i style="width:50%"></i></div><b>50%</b></div><div class="dist-row"><span>$360</span><div class="track"><i style="width:25%"></i></div><b>25%</b></div>',
        "DIST_SUMMARY": "期待値は標準ケース付近ですが、光接続の採用と次回ガイダンス次第で楽観側へ寄ります。",
        "WATCH_ROWS": '<div class="signal"><div><b>FY2027 Q1決算</b></div><p>売上、非GAAP粗利率、次回ガイダンスを確認します。</p></div><div class="signal"><div><b>光接続</b></div><p>DustPhotonics統合、ZeroFlap、DSPの売上寄与を確認します。</p></div><div class="signal"><div><b>顧客集中</b></div><p>大口顧客の発注継続と新規顧客拡大を確認します。</p></div>',
        "ASSUMPTIONS_ROWS": tr("評価基準株価", usd(P0), "市場データで確認", DATE, "2026/08/10場中確認") + tr("FY2026 Q4売上", "$437M", "会社リリース", "2026/05/02", "前年比+157%") + tr("FY2027 Q1売上見通し", "$465M〜$475M", "会社リリース", "2026/08/01期", "会社ガイダンス") + tr("時価総額", f"${MARKET_CAP_B:.1f}B", "株価・株式数から計算", DATE, "概算"),
        "DEEPDIVE_DETAILS": details("手法選定理由", "CRDOは利益が出ているAI接続高成長株です。PERだけでなく、売上成長、粗利率、光接続の広がり、顧客集中をシナリオ化します。", True) + details("株価水準について", "株価は52週高値からは下にありますが、AI接続需要を高く評価しています。良い決算でも期待を超えるかが重要です。") + details("主要出典", f'{source_link("FY2026 Q4決算リリース", "q4")}、{source_link("DustPhotonics買収リリース", "dust")}、{source_link("公式IR", "ir")}、{source_link("株価・統計", "quote")}。<br><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>'),
        "DISCLAIMER": "本資料は情報提供を目的とした試算です。投資助言ではありません。高成長AI半導体株は決算、金利、倍率、ガイダンスで大きく変動します。",
        "FOOTER_NOTE": f"SiM MARKET LAB｜{COMPANY}（{TICKER}）株価シナリオ｜作成日 {DATE}",
    }


def catalyst_values() -> dict[str, str]:
    non_quant = '<div class="priced"><div class="priced-head"><span>主要材料の推定織り込み</span><b>60%</b></div><p>仮定：FY2026 Q4好決算を80%、FY2027 Q1ガイダンスを65%、DustPhotonics/光接続の成長期待を45%、OCP/FMSなど追加製品発表を35%として置き、株価がすでに高成長を評価している点を控除しました。</p><p>読み方：好決算はかなり織り込み済みですが、光接続がFY2027の大きな成長ドライバーになるかはまだ一部織り込みです。</p><p>次に見る数字：FY2027 Q1売上、次回ガイダンス、非GAAP粗利率、現金、光接続の売上寄与、主要顧客の発注です。</p><p>再計算方法：各材料の成功確率を更新し、レポート2のシナリオ株価を再計算します。</p></div>'
    impact_map = {
        "FY2027 Q1決算と次回ガイダンス": ("+18〜40%", "-8〜+12%", "-20〜-35%", "高成長株では次四半期の売上とガイダンスが評価レンジを直接動かすため最大材料です。"),
        "DustPhotonics統合と光接続の売上化": ("+16〜35%", "-6〜+10%", "-12〜-25%", "光接続がFY2027の成長ドライバーになると、銅接続中心から評価が広がるためです。"),
        "AECと大口AI顧客の需要継続": ("+14〜32%", "-7〜+9%", "-18〜-30%", "現在の売上成長を支える主因なので、需要継続は標準ケース維持に直結します。"),
        "OCP/FMSなど製品発表": ("+6〜16%", "-3〜+6%", "-6〜-14%", "製品発表は期待材料ですが、決算数字ほど直接価値を変えないため小さめです。"),
    }
    description_map = {
        "FY2027 Q1決算と次回ガイダンス": "FY2026 Q4の強さが続くかを確認する最重要イベントです。売上、非GAAP粗利率、営業費用、次回ガイダンスが焦点です。",
        "DustPhotonics統合と光接続の売上化": "買収したシリコンフォトニクス技術が、ZeroFlap光トランシーバーや光DSPの採用拡大に変わるかを確認します。",
        "AECと大口AI顧客の需要継続": "AIクラスタ向けAECの需要が続くか、大口顧客以外にも採用が広がるかを見ます。",
        "OCP/FMSなど製品発表": "AIメモリー、ストレージ、標準化関連の発表が、実際の採用や売上見通しに結びつくかを確認します。",
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
<div class="evidence"><div><h4>根拠</h4><ul>{evidence}</ul></div><div><h4>反証・先行指標</h4><ul><li>売上成長率の鈍化</li><li>非GAAP粗利率の低下</li><li>主要顧客の発注減少</li></ul></div></div>
</article>'''

    cards = [
        card("FY2027 Q1決算と次回ガイダンス", "2026/09/02", '<span class="chip">重要度5</span><span class="chip">最重要</span>', '<span>売上</span><i>→</i><span>粗利率</span><i>→</i><span>ガイダンス</span>', "売上が見通し上限を超え、次回も上方感があれば楽観側です。", "見通しどおりなら標準ケースを維持します。", "売上や粗利率が弱い、または次回見通しが保守的なら期待剥落です。", "<li>会社はFY2027 Q1売上を$465M〜$475Mと見通しました。</li><li>FY2026 Q4は売上$437M、前年比+157%でした。</li>"),
        card("DustPhotonics統合と光接続の売上化", "FY2027", '<span class="chip">重要度4</span><span class="chip blue">光接続</span>', '<span>買収</span><i>→</i><span>製品</span><i>→</i><span>採用</span>', "光製品がFY2027の明確な成長ドライバーになれば上振れです。", "統合は進むが売上寄与は段階的なら中立です。", "統合遅延や顧客採用不足なら下押しです。", "<li>DustPhotonics買収でシリコンフォトニクスを追加。</li><li>会社は光製品がFY2027の成長ドライバーになると説明。</li>"),
        card("AECと大口AI顧客の需要継続", "継続確認", '<span class="chip">重要度4</span><span class="chip blue">AI需要</span>', '<span>AI投資</span><i>→</i><span>AEC需要</span><i>→</i><span>売上</span>', "大口顧客の追加発注と顧客分散が確認できれば上振れです。", "需要継続なら標準ケース維持です。", "AI投資鈍化や在庫調整が出ると下落要因です。", "<li>FY2026は売上が$1.335Bへ急拡大。</li><li>AECとICの成長がQ3時点でも強いと説明されました。</li>"),
        card("OCP/FMSなど製品発表", "2026年夏", '<span class="chip">重要度3</span><span class="chip blue">製品</span>', '<span>発表</span><i>→</i><span>標準化</span><i>→</i><span>採用</span>', "標準化や顧客採用が具体化すれば上振れです。", "発表中心なら短期は中立です。", "採用や売上化が見えない場合は材料消化です。", "<li>AIメモリー、ストレージ、OCP関連の発表が報じられています。</li><li>OmniConnectなど製品群の広がりを確認します。</li>"),
    ]
    return {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "Nasdaq",
        "VALUATION_DATE": DATE,
        "LAST_UPDATED": DATE,
        "REPORT_STATUS": "Q1決算待ち",
        "SUMMARY_LINE_1": "FY2027 Q1決算、DustPhotonics統合、AEC需要、OCP/FMS関連発表が主な材料です。",
        "SUMMARY_LINE_2": "足りない情報は仮定を置き、主要材料の織り込み度を60%と推定します。",
        "OVERALL_PRICED_IN": "60%",
        "OVERALL_PRICED_LABEL": "主要材料の推定織り込み",
        "PRICED_IN_CONFIDENCE": "中",
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "2026/08/10場中確認",
        "NEXT_CATALYST_TITLE": "FY2027 Q1決算と次回ガイダンス",
        "NEXT_CATALYST_WINDOW": "2026/09/02",
        "DATE_CONFIDENCE": "株価情報ページの決算予定",
        "CATALYST_COUNT": "4件",
        "WARN_BAND": "",
        "NO_CATALYST_NOTICE": "",
        "OVERALL_PRICED_BLOCK": non_quant,
        "PRICED_IN_METHOD": "FY2026 Q4決算、Q1ガイダンス、光接続、AEC需要、製品発表を標準ケース価値へ重み付けして推定。",
        "SURPRISE_UP": "Q1売上が見通し上限を超え、光接続の売上寄与と次回上方修正が同時に確認されることです。",
        "SURPRISE_DOWN": "売上成長鈍化、粗利率低下、主要顧客発注減、DustPhotonics統合遅れです。",
        "PRIMARY_RISK": "株価がAI接続の高成長をかなり織り込んでおり、良い決算でも期待を超えられない場合に下落しやすいことです。",
        "TIMELINE_ROWS": '<div class="time-row"><div class="time-date">2026/05/28</div><div class="time-dot"></div><div class="time-body"><b>DustPhotonics買収完了</b><p>シリコンフォトニクスを追加。</p><div class="time-meta"><span class="chip blue">光接続</span></div></div></div><div class="time-row"><div class="time-date">2026/06/01</div><div class="time-dot"></div><div class="time-body"><b>FY2026 Q4決算</b><p>売上$437M、非GAAP EPS $1.16。</p><div class="time-meta"><span class="chip">好決算</span></div></div></div><div class="time-row"><div class="time-date">2026/08</div><div class="time-dot"></div><div class="time-body"><b>OCP/FMS関連発表</b><p>AIメモリー・ストレージ接続の広がりを確認。</p><div class="time-meta"><span class="chip">製品</span></div></div></div><div class="time-row"><div class="time-date">2026/09/02</div><div class="time-dot"></div><div class="time-body"><b>FY2027 Q1決算予定</b><p>売上見通し達成と次回ガイダンスを確認。</p><div class="time-meta"><span class="chip">最重要</span></div></div></div>',
        "CATALYST_CARDS": "".join(cards) + '<p class="small">※下の％は、この結果が出た後に市場が材料を評価し直した場合の上昇・下落幅の目安です。実際の値動きは地合い、直前の株価上昇、同時ニュースで変わります。</p>',
        "DEPENDENCY_ROWS": '<div class="signal"><div><b>Q1決算と倍率</b><span class="up">連動</span></div><p>高成長が続くほど高い倍率を維持しやすいです。</p></div><div class="signal"><div><b>光接続と粗利率</b><span class="flat">重要</span></div><p>新製品が粗利率を崩さず伸びるかを確認します。</p></div><div class="signal"><div><b>顧客集中</b><span class="down">注意</span></div><p>顧客分散が進むほどリスクは下がります。</p></div>',
        "WATCH_ROWS": '<div class="signal"><div><b>Q1売上</b><span class="up">最重要</span></div><p>$465M〜$475M見通しを上回るか。</p></div><div class="signal"><div><b>非GAAP粗利率</b><span class="up">重要</span></div><p>67〜69%近辺を維持できるか。</p></div><div class="signal"><div><b>光接続</b><span class="flat">AI</span></div><p>DustPhotonics統合と顧客採用。</p></div><div class="signal"><div><b>顧客発注</b><span class="down">注意</span></div><p>大口顧客の需要継続と分散。</p></div>',
        "ASSUMPTION_ROWS": tr("評価基準株価", usd(P0), "市場データで確認", DATE, "2026/08/10場中確認") + tr("FY2026 Q4売上", "$437M", "会社リリース", "2026/05/02", "前年比+157%") + tr("FY2027 Q1売上見通し", "$465M〜$475M", "会社リリース", "2026/08/01期", "会社ガイダンス") + tr("現金・短期投資", "$1.4B", "会社リリース", "2026/05/02", "FY2026末"),
        "SOURCE_DETAILS": f'<ul><li>{source_link("公式IR", "ir")}</li><li>{source_link("FY2026 Q4決算リリース", "q4")}</li><li>{source_link("FY2026 Q3決算リリース", "q3")}</li><li>{source_link("DustPhotonics買収リリース", "dust")}</li><li>{source_link("株価・統計", "quote")}</li></ul><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p>',
        "VALIDATION_DETAILS": "<p>PASS：公式IR、FY2026 Q4決算、FY2026 Q3決算、DustPhotonics買収リリース、株価・統計ページを確認。</p>",
        "UPDATE_HISTORY": f"<p>{DATE}：初版作成。FY2026 Q4決算、FY2027 Q1ガイダンス、DustPhotonics買収、AI接続製品を反映。</p>",
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
        "id": "credo-crdo",
        "order": 10,
        "ticker": "CRDO",
        "quoteSymbol": "CRDO",
        "name": "クレド・テクノロジー・グループ",
        "nameEn": "Credo Technology Group Holding Ltd.",
        "market": "US",
        "marketLabel": "米国株",
        "exchange": "Nasdaq",
        "currency": "USD",
        "sector": "AIデータセンター接続・高速インターコネクト",
        "reports": {
            "company": {"path": "./stocks/credo-crdo/company.html", "available": True},
            "valuation": {"path": "./stocks/credo-crdo/valuation.html", "available": True},
            "catalysts": {"path": "./stocks/credo-crdo/catalysts.html", "available": True},
        },
    }
    stocks_payload["stocks"] = [item for item in stocks_payload["stocks"] if item["id"] != "credo-crdo"]
    stocks_payload["stocks"].append(stock)
    stocks_payload["stocks"].sort(key=lambda item: item["order"])
    stocks_path.write_text(json.dumps(stocks_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    prices_path = ROOT / "data" / "prices.json"
    prices_payload = json.loads(prices_path.read_text(encoding="utf-8"))
    prices_payload.setdefault("prices", {})["credo-crdo"] = {
        "symbol": "CRDO",
        "price": P0,
        "previousClose": PREVIOUS_CLOSE,
        "change": round(P0 - PREVIOUS_CLOSE, 4),
        "changePct": round((P0 - PREVIOUS_CLOSE) / PREVIOUS_CLOSE * 100, 4),
        "currency": "USD",
        "marketTime": "2026-08-10T14:57:00+00:00",
        "updatedAt": "2026-08-11T00:00:00+00:00",
        "status": "ok",
    }
    prices_payload["quoteCount"] = len(prices_payload["prices"])
    prices_path.write_text(json.dumps(prices_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    signals_path = ROOT / "data" / "signals.json"
    signals_payload = json.loads(signals_path.read_text(encoding="utf-8"))
    signals_payload["updatedAt"] = datetime.now(timezone.utc).isoformat()
    signals_payload.setdefault("signals", {})["credo-crdo"] = {
        "position": SIGNAL_POSITION,
        "zone": "中立",
        "asOf": DATE,
        "components": {
            "valuation": round(BAND_POSITION, 1),
            "catalysts": 80.0,
            "businessRisk": 62.0,
        },
        "reportRevision": "credo-crdo-2026-08-11",
        "summary": "FY2026 Q4決算とQ1ガイダンスは強い。AI接続需要と光接続拡大は追い風だが、株価は高期待を織り込むため中立。",
    }
    signals_path.write_text(json.dumps(signals_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_reports()
    upsert_site_data()


if __name__ == "__main__":
    main()
