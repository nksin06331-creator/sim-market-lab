"""Generate Furukawa Electric report HTML files from the bundled SiM templates."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from generate_rocket_lab_reports import dl, li, render_template, th, tr


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stocks" / "furukawa-electric-5801"

COMPANY = "古河電気工業"
TICKER = "5801"
DATE = "2026-08-19"
P0 = 3919.0
PREVIOUS_CLOSE = 3566.0
SHARES_M = 706.67
MARKET_CAP_TN = P0 * SHARES_M / 1_000_000

BEAR = 3000
BASE = 4300
BULL = 5600
CATALYST_SCORE = 82.0
BUSINESS_RISK_SCORE = 56.0
BAND_POSITION = (P0 - BEAR) / (BULL - BEAR) * 100
SIGNAL_POSITION = round(0.60 * round(BAND_POSITION, 1) + 0.25 * CATALYST_SCORE + 0.15 * BUSINESS_RISK_SCORE, 1)

SOURCES = {
    "ir": "https://www.furukawaelectric.com/ir/",
    "library": "https://www.furukawaelectric.com/ir/library/",
    "highlight": "https://www.furukawaelectric.com/ir/achievements/highlight.html",
    "mid": "https://www.furukawaelectric.com/ir/library/mid_briefing/",
    "management": "https://www.furukawaelectric.com/ir/management/feature.html",
    "energy": "https://www.furukawaelectric.com/ir/achievements/segment/energy.html",
    "yahoo": "https://finance.yahoo.co.jp/quote/5801.T/history",
    "kabutan": "https://s.kabutan.jp/stocks/5801/historical_prices/monthly/",
}


def yen(value: int | float) -> str:
    if value < 1000 and value != int(value):
        return f"{value:,.1f}円"
    return f"{value:,.0f}円"


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
        f'{source_link("古河電工公式IR", "ir")}、'
        f'{source_link("IR資料室", "library")}、'
        f'{source_link("業績概要・予想", "highlight")}、'
        f'{source_link("経営方針説明会", "mid")}、'
        f'{source_link("株価時系列", "yahoo")}を確認しました。'
        "本文の数値は2026年8月19日時点で取得できた公開情報に基づきます。"
        '</p><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p></div></details>'
    )
    terms = [
        ("情報通信ソリューション", "光ファイバ、光ファイバケーブル、光部品などです。AIデータセンタ需要が焦点です。"),
        ("エネルギーインフラ", "電力ケーブル、接続部品、地中線、海底線などです。送電網・再エネ投資が追い風です。"),
        ("電装エレクトロニクス", "ワイヤハーネス、自動車部品、電子材料などの領域です。車両生産と採算が重要です。"),
        ("機能製品", "放熱・冷却、AT、銅箔などを含む高付加価値製品群です。"),
        ("光ファイバケーブル", "データセンタや通信網を支える光通信ケーブルです。需要増と価格・採算が評価材料です。"),
        ("データセンタ関連", "AIサーバーやクラウド投資に連動する光通信・放熱関連需要です。"),
        ("ROIC", "投下資本利益率です。中計では資本効率改善が重要な目標です。"),
        ("25中計", "2025年度を目標年度とする中期経営計画です。営業利益580億円以上などの目標が示されました。"),
        ("上方修正", "会社が従来予想を引き上げることです。2027年3月期1Qで通期予想を大きく引き上げました。"),
        ("銅価格", "電線・ケーブル材料として重要です。価格転嫁と在庫評価が業績に影響します。"),
        ("為替", "海外売上・調達・持分法損益に影響します。円安・円高の方向を確認します。"),
        ("株式分割", "2026年に株式分割があり、過去株価との単純比較では単位に注意が必要です。"),
    ]
    return {
        "TICKER": TICKER,
        "COMPANY_NAME": COMPANY,
        "INDUSTRY": "光通信・電力ケーブル・自動車部品・機能製品",
        "DATE": DATE,
        "TAGLINE": "光ファイバ、電力ケーブル、自動車部品、電子・機能製品を持つ総合電線メーカーです。AIデータセンタ需要と電力インフラ投資が主な成長テーマです。",
        "HERO_TAGS": '<span class="hero-tag">日本株</span><span class="hero-tag">光通信</span><span class="hero-tag">データセンタ</span><span class="hero-tag">電力ケーブル</span>',
        "HERO_STATS": (
            f'<div class="stat"><div class="stat-value">{yen(P0)}</div><div class="stat-label">評価基準株価</div><div class="stat-note">2026/08/05終値</div></div>'
            f'<div class="stat"><div class="stat-value">{MARKET_CAP_TN:.1f}兆円</div><div class="stat-label">時価総額の目安</div><div class="stat-note">概算株式数で計算</div></div>'
            '<div class="stat"><div class="stat-value up">1.53兆円</div><div class="stat-label">2027年3月期売上予想</div><div class="stat-note">1Q発表後の会社予想</div></div>'
            '<div class="stat"><div class="stat-value">1,230億円</div><div class="stat-label">2027年3月期営業利益予想</div><div class="stat-note">従来950億円から上方修正</div></div>'
        ),
        "SEC2_LABEL": "事業モデル",
        "SEC3_LABEL": "光通信",
        "SEC4_LABEL": "決算",
        "SEC5_LABEL": "競合比較",
        "SEC1_TLDR": li("古河電工は光通信、電力ケーブル、自動車部品、機能製品を持つ総合電線メーカーです。", "*") + li("2027年3月期1Qは経常利益が前年同期比で大幅増となり、通期予想も上方修正されました。", "*") + li("株価は急騰後の水準で、光ファイバ・データセンタ期待の織り込み度を確認する局面です。", "!"),
        "SEC1_FACTS": (
            "<div><dt>正式社名</dt><dd>古河電気工業株式会社</dd></div><div><dt>本社</dt><dd>東京都千代田区</dd></div>"
            "<div><dt>上場</dt><dd>東証プライム（5801）</dd></div><div><dt>決算期</dt><dd>3月</dd></div>"
            "<div><dt>主な領域</dt><dd>情報通信、エネルギーインフラ、自動車部品、機能製品</dd></div><div><dt>業種</dt><dd>非鉄金属</dd></div>"
        ),
        "SEC1_CARDS": (
            '<div class="card-sm"><span class="card-emoji">🌐</span><div class="card-title">光通信</div><div class="card-desc">AIデータセンタ需要で光ファイバ・光部品が注目されています。</div></div>'
            '<div class="card-sm"><span class="card-emoji">⚡</span><div class="card-title">電力</div><div class="card-desc">再エネ、送電網、地中線・海底線の投資が材料です。</div></div>'
            '<div class="card-sm"><span class="card-emoji">🚗</span><div class="card-title">自動車</div><div class="card-desc">ワイヤハーネスや電装部品が収益基盤です。</div></div>'
            '<div class="card-sm"><span class="card-emoji">📈</span><div class="card-title">決算</div><div class="card-desc">1Qで通期業績予想を大きく上方修正しました。</div></div>'
        ),
        "SEC1_BIZMODEL": (
            '<li><span class="kp-emoji">🌐</span><span class="kp-text"><b>情報通信</b>：光ファイバ・光ケーブル・光部品でデータセンタ需要を取り込みます。</span></li>'
            '<li><span class="kp-emoji">⚡</span><span class="kp-text"><b>エネルギー</b>：電力ケーブルや接続部品で送電網・再エネ投資に関わります。</span></li>'
            '<li><span class="kp-emoji">🚗</span><span class="kp-text"><b>電装</b>：自動車部品・電池・電子材料で景気と車生産に連動します。</span></li>'
        ),
        "SEC1_HIGHLIGHT": '<div class="highlight"><h3>古河電工を見る基本ルール</h3><p>光通信の収益改善、電力ケーブルの採算、自動車部品の安定性、上方修正後の利益進捗を分けて見ます。株価はテーマ性で動きやすいため、決算の数字と倍率を同時に確認します。</p></div>',
        "SEC2_ICON": "🏭",
        "SEC2_TITLE": "光・電力・車を持つ<span class=\"g\">総合電線</span>",
        "SEC2_SUB": "景気敏感と成長テーマが同居",
        "SEC2_TLDR": li("事業は情報通信、エネルギーインフラ、電装エレクトロニクス、機能製品に分かれます。", "*") + li("光ファイバとデータセンタ関連が評価拡大の中心です。", "*") + li("銅価格、為替、自動車生産、投資負担で利益が動きます。", "!"),
        "SEC2_CONTENT": (
            '<p class="lead">古河電工は、電線から始まった技術を光通信、電力インフラ、自動車、機能製品へ広げてきた会社です。</p>'
            '<div class="sowhat"><p><b>つまり</b>、5801は「AIデータセンタ関連株」と「電力インフラ株」と「自動車部品株」の3つの顔を持つ銘柄です。</p></div>'
            '<div class="term-list">'
            + details("情報通信ソリューション", "光ファイバ・ケーブル、光部品などです。データセンタ市場の需要が収益を押し上げています。", True)
            + details("エネルギーインフラ", "電力ケーブル、接続部品、地中線・海底線などです。受注と採算が重要です。")
            + details("電装エレクトロニクス", "ワイヤハーネス、自動車部品、電子材料などです。車両生産とコスト管理を見ます。")
            + details("機能製品", "放熱・冷却や高機能材料などです。データセンタ向けの広がりも確認します。")
            + "</div>"
        ),
        "SEC3_TITLE": "光ファイバと<span class=\"g\">データセンタ</span>",
        "SEC3_SUB": "上方修正の中心テーマ",
        "SEC3_TLDR": li("光ファイバケーブル等のデータセンタ関連製品が収益伸長に貢献しています。", "*") + li("2026年8月には光ファイバ・光ケーブル生産に係る固定資産取得も開示されています。", "*") + li("需要が強くても、増産投資の回収と価格競争には注意です。", "!"),
        "SEC3_CONTENT": (
            '<div class="product-grid"><div class="product-box"><div class="product-symbol">OF</div><div class="product-name">光ファイバ</div><div class="product-use">AI・クラウドの通信容量増に対応。</div></div>'
            '<div class="product-box"><div class="product-symbol">DC</div><div class="product-name">データセンタ</div><div class="product-use">光接続・放熱関連需要。</div></div>'
            '<div class="product-box"><div class="product-symbol">EN</div><div class="product-name">電力ケーブル</div><div class="product-use">再エネ・送電網投資に対応。</div></div></div>'
            '<div class="term-list">'
            + details("データセンタ関連", "AIサーバーやクラウド投資により、光通信部品・ケーブル・放熱関連の需要が増える領域です。", True)
            + details("固定資産取得", "光ファイバ・光ケーブルの生産能力増強は、需要が強い局面では追い風ですが、投資回収を確認する必要があります。")
            + details("光ソリューション", "古河電工はノキアとのAI活用ネットワーク運用ソリューションなども発表しています。")
            + details("競争", "フジクラ、住友電工、海外光部品企業との競争があり、価格と採算が焦点です。")
            + "</div>"
        ),
        "SEC4_TITLE": "1Qで<span class=\"g\">上方修正</span>",
        "SEC4_SUB": "通期営業利益予想は1,230億円へ",
        "SEC4_TLDR": li("2027年3月期1Q売上は3,652億円、営業利益は255億円でした。", "*") + li("通期予想は売上1兆5,300億円、営業利益1,230億円、経常利益1,430億円へ上方修正されました。", "*") + li("上方修正後は、2Q以降に勢いが続くかを確認します。", "!"),
        "SEC4_CONTENT": (
            '<ul class="keypoints"><li><span class="kp-emoji">📈</span><span class="kp-text"><b>1Q</b>：売上3,652億円、営業利益255億円、経常利益310億円。</span></li>'
            '<li><span class="kp-emoji">🔁</span><span class="kp-text"><b>通期修正</b>：営業利益は950億円から1,230億円へ、経常利益は1,000億円から1,430億円へ。</span></li>'
            '<li><span class="kp-emoji">🌐</span><span class="kp-text"><b>背景</b>：データセンタ関連製品と収益性改善が主な評価材料です。</span></li></ul>'
            '<div class="sowhat"><p><b>つまり</b>、いまの焦点は「上方修正が一過性か、構造的な利益改善か」です。2Qと下期見通しで確認します。</p></div>'
        ),
        "SEC5_TITLE": "競合と<span class=\"g\">比べる</span>",
        "SEC5_SUB": "光通信ではフジクラ、総合電線では住友電工",
        "SEC5_TLDR": li("比較対象はフジクラ、住友電工、SWCC、海外光通信部品企業です。", "*") + li("古河電工は光通信と電力インフラの改善が評価材料です。", "*") + li("株価は光通信テーマで上がりやすい一方、倍率の調整にも注意です。", "!"),
        "SEC5_CONTENT": (
            '<div class="table-wrap"><table class="compare-table"><thead><tr><th>企業</th><th>主な強み</th><th>注意点</th></tr></thead><tbody>'
            '<tr><td class="me">古河電工</td><td>光通信、電力インフラ、自動車、機能製品。上方修正で利益成長が明確。</td><td>急騰後の倍率、銅価格、投資負担、景気敏感。</td></tr>'
            '<tr><td>フジクラ</td><td>データセンタ・光通信テーマで評価されやすい。</td><td>期待が高い局面では倍率調整に注意。</td></tr>'
            '<tr><td>住友電工</td><td>自動車、電力、通信を広く持つ分散型。</td><td>成長テーマの寄与が分散されやすい。</td></tr>'
            '<tr><td>SWCC</td><td>電線・インフラ関連の収益改善。</td><td>規模とテーマ性は相対的に限定的。</td></tr>'
            '</tbody></table></div><div class="highlight"><h3>差別化の見方</h3><p>古河電工は、光通信と電力インフラの収益改善が同時に見えると評価が広がります。いまは上方修正後なので、次は利益率の持続性が重要です。</p></div>'
        ),
        "SEC6_TLDR": li("情報通信、電力ケーブル、上方修正、ROIC、銅価格を押さえると読みやすいです。", "*") + li("株式分割後の価格比較には注意が必要です。", "*") + li("光通信テーマは強いですが、期待先行になりやすいです。", "!"),
        "SEC6_CONTENT": '<div class="term-list">' + "".join(details(name, body) for name, body in terms) + "</div>",
        "SEC7_TLDR": li("最大材料は8月6日の1Q決算と通期上方修正です。", "*") + li("光ファイバ増産投資、データセンタ需要、2Q進捗が次の確認点です。", "*") + li("株価急騰後の倍率調整と、投資負担には注意です。", "!"),
        "SEC7_CONTENT": (
            '<div class="timeline"><div class="tl-row"><div class="tl-date">2026/05/12</div><div class="tl-title">2026年3月期決算 <span class="signal bull">改善</span></div><div class="tl-desc">売上1兆3,076億円、営業利益639億円。データセンタ関連製品が増収に貢献。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/08/04</div><div class="tl-title">光ファイバ・光ケーブル投資 <span class="signal bull">成長投資</span></div><div class="tl-desc">生産に係る固定資産取得を開示。データセンタ需要への対応を確認。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/08/06</div><div class="tl-title">2027年3月期1Q決算 <span class="signal bull">最重要</span></div><div class="tl-desc">1Q好調と通期上方修正を発表。株価反応も大きい材料です。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/11ごろ</div><div class="tl-title">2Q・中間決算 <span class="signal neutral">確認</span></div><div class="tl-desc">上方修正後の進捗、情報通信と電力の利益率を確認します。</div></div></div>'
            '<div class="info-row"><div class="info-box info-box-green"><div class="info-title info-title-green">追い風</div><div class="info-text">1Q上方修正、データセンタ需要、光ファイバ投資、電力インフラ。</div></div>'
            '<div class="info-box info-box-amber"><div class="info-title info-title-amber">確認</div><div class="info-text">2Q進捗、利益率、増産投資の回収、株価倍率。</div></div>'
            '<div class="info-box info-box-red"><div class="info-title info-title-red">リスク</div><div class="info-text">急騰後の反動、銅価格、為替、投資負担、競争激化。</div></div></div>'
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
        "EXCHANGE": "東京証券取引所プライム市場",
        "VALUATION_DATE": DATE,
        "METHOD": "上方修正後のPER・利益成長シナリオ",
        "VERDICT_STATUS": "強い決算後の中立上限寄り",
        "VERDICT_LINE_1": f"評価基準株価は悲観〜楽観レンジの{BAND_POSITION:.1f}%地点です。1Q上方修正は強い一方、株価はかなり材料を織り込み始めています。",
        "VERDICT_LINE_2": "この試算は2026年8月19日時点で取得できた公開情報に基づきます。2Q進捗と利益率で更新が必要です。",
        "SCORE": str(score),
        "CURRENT_PRICE": yen(P0),
        "CURRENT_PRICE_NOTE": "2026/08/05終値",
        "BASE_PRICE": yen(BASE),
        "BASE_DELTA": pct(BASE / P0 - 1),
        "EXPECTED_VALUE": yen(expected),
        "EXPECTED_DELTA": pct(expected / P0 - 1),
        "RISK_CLASS": "中〜高",
        "RISK_NOTE": "光通信テーマ、急騰後、景気・銅価格連動",
        "WARN_BAND": '<div class="wrap"><div class="notice" style="margin-top:14px"><b>注意：</b>株式分割後の価格を基準にしています。過去株価との比較では単位変更に注意してください。</div></div>',
        "WARN_MESSAGE": "株式分割後の価格を基準にしています。",
        "SNAPSHOT_LEAD": "今の株価は標準ケースに近づいた位置です。1Q上方修正は強いですが、さらに上を見るには2Q以降も情報通信と電力の利益率が続く必要があります。",
        "BAND_POSITION": f"{BAND_POSITION:.1f}%",
        "ZONE_JUDGE": "標準ケース手前",
        "ZONE_NOTE": "2Qで上方修正の持続性が確認できれば標準〜楽観側へ、利益率低下や材料出尽くしなら悲観側へ戻ります。",
        "BEAR_PRICE": yen(BEAR),
        "BULL_PRICE": yen(BULL),
        "ENDPOINT_RR": f"{endpoint_rr:.1f}倍",
        "MARKET_SCORE": str(round(BAND_POSITION)),
        "OWN_SCORE": str(round(own_score)),
        "MARKET_REVERSE_NOTE": "市場は1Q上方修正とデータセンタ関連の成長をかなり評価しています。ただし、増産投資の回収と2Q以降の利益率はまだ確認余地があります。",
        "SCENARIOS_LEAD": "現在株価から独立して、上方修正後の営業利益、EPS、PER、光通信需要、電力ケーブル採算を置きました。",
        "BEAR_PROB": "25%",
        "BASE_PROB": "50%",
        "BULL_PROB": "25%",
        "BEAR_DELTA": pct(BEAR / P0 - 1),
        "BULL_DELTA": pct(BULL / P0 - 1),
        "BEAR_DL_ROWS": dl([("利益", "上方修正後に失速"), ("PER", "テーマ剥落"), ("光通信", "採算伸び悩み"), ("株価", yen(BEAR))]),
        "BASE_DL_ROWS": dl([("営業利益", "1,230億円前後"), ("EPS", "会社修正予想を概ね達成"), ("PER", "光通信評価を維持"), ("株価", yen(BASE))]),
        "BULL_DL_ROWS": dl([("営業利益", "さらに上振れ"), ("光通信", "DC需要が継続"), ("倍率", "成長株寄りに再評価"), ("株価", yen(BULL))]),
        "PRICE_ZONE_ROWS": '<div class="zone"><div><b>3,000円未満</b><span>★★★</span></div><p>上方修正後の期待が剥落し、景気・採算リスクを強く織り込む価格帯です。</p></div><div class="zone"><div><b>3,000〜4,300円</b><span>★★★</span></div><p>強い決算を評価しつつ、2Q確認待ちの価格帯です。</p></div><div class="zone"><div><b>4,300〜5,600円</b><span>★★</span></div><p>光通信と電力インフラの利益成長が続くことを評価する価格帯です。</p></div><div class="zone"><div><b>5,600円超</b><span>★</span></div><p>さらなる上方修正と倍率拡大が必要です。</p></div>',
        "SIGNAL_ROWS": '<div class="signal"><div><b>1Q決算</b><span class="up">強い</span></div><p>経常利益が大幅増、通期予想も上方修正。</p></div><div class="signal"><div><b>光通信</b><span class="up">追い風</span></div><p>データセンタ関連製品が収益伸長に貢献。</p></div><div class="signal"><div><b>株価水準</b><span class="flat">確認</span></div><p>急騰後で材料織り込みを確認。</p></div><div class="signal"><div><b>投資負担</b><span class="down">注意</span></div><p>増産投資の回収と採算を確認。</p></div>',
        "POSITIVES": "<li>2027年3月期1Qは営業利益・経常利益が大きく伸びました。</li><li>通期営業利益予想は950億円から1,230億円へ上方修正されました。</li><li>データセンタ関連製品と光通信需要が収益成長に貢献しています。</li><li>電力インフラや機能製品にも中期成長テーマがあります。</li>",
        "CONCERNS": "<li>株価は短期間で大きく上昇しており、材料出尽くしリスクがあります。</li><li>銅価格、為替、自動車生産、設備投資負担で利益が変動します。</li><li>光通信テーマは競争と価格変動に敏感です。</li><li>上方修正後の2Q進捗が弱いと倍率が下がりやすいです。</li>",
        "FORMULA": "主計算は上方修正後のEPSとPERです。補助的に営業利益成長、光通信の利益率、電力ケーブル採算を見ます。",
        "CALC_TABLE_HEAD": th("ケース", "主な前提", "価値の見方", "計算株価", "確率", "確率加重"),
        "CALC_TABLE_ROWS": tr("悲観", "上方修正後に失速", "PER圧縮", yen(BEAR), "25%", "750円") + tr("標準", "修正予想を概ね達成", "PERを維持", yen(BASE), "50%", "2,150円") + tr("楽観", "再上方修正余地", "光通信株として再評価", yen(BULL), "25%", "1,400円"),
        "CALC_NOTICE": "現在株価に合わせた逆算ではありません。1Q上方修正後の利益水準と倍率を分けて置いた条件付き試算です。",
        "CONDITIONS": details("悲観ケース：3,000円 / 確率25%", "上方修正後に利益率が鈍化し、株価急騰の反動でPERが下がるケースです。", True) + details("標準ケース：4,300円 / 確率50%", "修正後の通期予想を概ね達成し、光通信と電力の利益率が維持されるケースです。") + details("楽観ケース：5,600円 / 確率25%", "2Q以降も上振れ、データセンタ関連と電力ケーブルが再評価されるケースです。"),
        "SENSITIVITY_HEAD": th("前提", "弱い", "標準", "強い"),
        "SENSITIVITY_ROWS": tr("営業利益", "1,050億円 → 3,000円", "1,230億円 → 4,300円", "1,400億円超 → 5,600円") + tr("光通信", "採算鈍化", "需要継続", "増産投資が高採算で寄与") + tr("PER", "テーマ剥落", "上方修正評価を維持", "成長株寄りに再評価"),
        "SENSITIVITY_NOTE": "1変数だけを動かした簡易感応度です。実際には利益とPERが同時に動きます。",
        "DIST_LEAD": "モンテカルロではなく、1Q上方修正後の3点シナリオです。",
        "DIST_ROWS": '<div class="dist-row"><span>3,000円</span><div class="track"><i style="width:25%"></i></div><b>25%</b></div><div class="dist-row"><span>4,300円</span><div class="track"><i style="width:50%"></i></div><b>50%</b></div><div class="dist-row"><span>5,600円</span><div class="track"><i style="width:25%"></i></div><b>25%</b></div>',
        "DIST_SUMMARY": "中心は標準ケースです。強い決算後なので、上値は2Qでの再確認が必要です。",
        "WATCH_ROWS": '<div class="signal"><div><b>2Q・中間決算</b></div><p>上方修正後の進捗、情報通信、電力、機能製品の利益率を確認します。</p></div><div class="signal"><div><b>光ファイバ投資</b></div><p>固定資産取得の規模、稼働時期、採算を確認します。</p></div><div class="signal"><div><b>株価倍率</b></div><p>上方修正後のPERが維持されるかを確認します。</p></div>',
        "ASSUMPTIONS_ROWS": tr("評価基準株価", yen(P0), "市場データで確認", DATE, "2026/08/05終値") + tr("2027年3月期1Q売上", "3,652億円", "決算速報・会社開示", "2026/08/06", "前年比+24.3%") + tr("通期営業利益予想", "1,230億円", "会社上方修正", "2026/08/06", "従来950億円") + tr("通期経常利益予想", "1,430億円", "会社上方修正", "2026/08/06", "従来1,000億円"),
        "DEEPDIVE_DETAILS": details("手法選定理由", "古河電工は黒字の大型製造業ですが、足元は光通信テーマで倍率が動いています。上方修正後の利益水準とPERを分けて見ます。", True) + details("株価水準について", "株価は1Q前後で大きく動いています。現在地バーはprices.jsonの現在株価とBear/Bullから表示時に再計算されます。") + details("主要出典", f'{source_link("公式IR", "ir")}、{source_link("IR資料室", "library")}、{source_link("業績概要・予想", "highlight")}、{source_link("株価時系列", "yahoo")}。<br><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>'),
        "DISCLAIMER": "本資料は情報提供を目的とした試算です。投資助言ではありません。製造業株は景気、為替、銅価格、投資計画、需給で大きく変動します。",
        "FOOTER_NOTE": f"SiM MARKET LAB｜{COMPANY}（{TICKER}）株価シナリオ｜作成日 {DATE}",
    }


def catalyst_values() -> dict[str, str]:
    non_quant = '<div class="priced"><div class="priced-head"><span>主要材料の推定織り込み</span><b>66%</b></div><p>仮定：1Q上方修正を80%、光通信・データセンタ需要を70%、光ファイバ増産投資を55%、2Qでの再上方期待を50%として置き、急騰後の材料織り込みを控除しました。</p><p>読み方：1Qの好材料はかなり織り込まれていますが、2Q以降の利益率持続と増産投資の回収はまだ確認余地があります。</p><p>次に見る数字：情報通信ソリューション利益、エネルギーインフラ利益、通期予想再修正、営業利益率、設備投資額です。</p><p>再計算方法：各材料の成功確率を更新し、レポート2のBear/Base/Bullを見直します。</p></div>'
    impact_map = {
        "2027年3月期1Q決算と上方修正": ("+10〜24%", "-5〜+8%", "-12〜-24%", "大型株としては大きな上方修正ですが、発表済み材料のため追加反応は2Qへの期待次第です。"),
        "光通信・データセンタ需要の継続": ("+14〜32%", "-6〜+10%", "-14〜-28%", "いまの評価の中心で、需要継続と採算改善が確認されるとPERを支えるためです。"),
        "光ファイバ・光ケーブル増産投資": ("+8〜20%", "-4〜+7%", "-10〜-20%", "成長投資は将来売上を押し上げますが、投資回収まで時間差があるためです。"),
        "2Q・中間決算での進捗確認": ("+12〜28%", "-5〜+9%", "-15〜-30%", "上方修正後の最初の確認点で、利益率の持続性を市場が評価し直すためです。"),
    }
    description_map = {
        "2027年3月期1Q決算と上方修正": "2026年8月6日の1Q決算で、営業利益・経常利益が大きく伸び、通期予想も引き上げられました。発表済みですが、株価の基準を変えた最大材料です。",
        "光通信・データセンタ需要の継続": "AI・クラウド投資に伴う光ファイバ、光ケーブル、光部品需要が続くかを確認します。古河電工の再評価の中心です。",
        "光ファイバ・光ケーブル増産投資": "2026年8月4日に開示された固定資産取得は、強い需要に対応する成長投資です。設備投資が高採算売上に変わるかを見ます。",
        "2Q・中間決算での進捗確認": "上方修正後の進捗確認です。情報通信、エネルギー、電装、機能製品のどこが利益を伸ばすかで評価が変わります。",
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
<div class="evidence"><div><h4>根拠</h4><ul>{evidence}</ul></div><div><h4>反証・先行指標</h4><ul><li>営業利益率の低下</li><li>光通信製品の価格下落</li><li>銅価格・為替の逆風</li></ul></div></div>
</article>'''

    cards = [
        card("2027年3月期1Q決算と上方修正", "2026/08/06", '<span class="chip">重要度5</span><span class="chip">発表済み</span>', '<span>1Q実績</span><i>→</i><span>通期修正</span><i>→</i><span>PER</span>', "上方修正後も保守的と見られ、再上方期待が高まる状態です。", "発表内容はおおむね織り込まれ、2Q待ちの状態です。", "材料出尽くしや一過性要因が意識される状態です。", "<li>1Q経常利益は前年同期比で大幅増。</li><li>通期経常利益予想は1,000億円から1,430億円へ上方修正。</li>"),
        card("光通信・データセンタ需要の継続", "2026-2027", '<span class="chip">重要度5</span><span class="chip blue">DC需要</span>', '<span>AI投資</span><i>→</i><span>光需要</span><i>→</i><span>利益率</span>', "光ファイバ・光部品の需要と採算が続けば楽観側です。", "需要は強いが、株価も織り込んでいる状態です。", "需要減速や価格競争が見えると下押しです。", "<li>会社はデータセンタ関連製品が収益伸長に貢献すると説明。</li><li>情報通信ソリューションの収益改善が注目点。</li>"),
        card("光ファイバ・光ケーブル増産投資", "2026/08/04", '<span class="chip">重要度4</span><span class="chip blue">成長投資</span>', '<span>投資</span><i>→</i><span>能力増強</span><i>→</i><span>売上</span>', "高稼働・高採算で投資回収が見えれば上振れです。", "投資発表だけなら中立です。", "需要変化や稼働遅れが出ると負担になります。", "<li>光ファイバおよび光ファイバケーブル生産に係る固定資産取得を開示。</li><li>AIデータセンタ市場向け需要が背景。</li>"),
        card("2Q・中間決算での進捗確認", "2026/11ごろ", '<span class="chip">重要度5</span><span class="chip">次の確認</span>', '<span>2Q</span><i>→</i><span>利益率</span><i>→</i><span>再評価</span>', "情報通信と電力がそろって強く、再上方修正余地が見えれば上振れです。", "修正後計画どおりなら標準ケース維持です。", "1Q偏重や利益率低下が見えると下落要因です。", "<li>上方修正後の最初の大型確認点。</li><li>セグメント別利益の持続性が重要。</li>"),
    ]
    return {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "東京証券取引所プライム市場",
        "VALUATION_DATE": DATE,
        "LAST_UPDATED": DATE,
        "REPORT_STATUS": "上方修正後の確認局面",
        "SUMMARY_LINE_1": "1Q上方修正、光通信・データセンタ需要、増産投資、2Q進捗が主な材料です。",
        "SUMMARY_LINE_2": "足りない情報は仮定を置き、主要材料の織り込み度を66%と推定します。",
        "OVERALL_PRICED_IN": "66%",
        "OVERALL_PRICED_LABEL": "主要材料の推定織り込み",
        "PRICED_IN_CONFIDENCE": "中",
        "CURRENT_PRICE": yen(P0),
        "CURRENT_PRICE_NOTE": "2026/08/05終値",
        "NEXT_CATALYST_TITLE": "2Q・中間決算での進捗確認",
        "NEXT_CATALYST_WINDOW": "2026年11月ごろ",
        "DATE_CONFIDENCE": "例年スケジュールからの推定",
        "CATALYST_COUNT": "4件",
        "WARN_BAND": "",
        "NO_CATALYST_NOTICE": "",
        "OVERALL_PRICED_BLOCK": non_quant,
        "PRICED_IN_METHOD": "1Q上方修正、光通信需要、増産投資、2Q再確認、株価急騰後の材料消化を重み付けして推定。",
        "SURPRISE_UP": "2Qでも利益率が高く、通期再上方修正余地と光通信の高採算成長が同時に見えることです。",
        "SURPRISE_DOWN": "1Q偏重、光通信の価格下落、投資負担、材料出尽くしです。",
        "PRIMARY_RISK": "上方修正後に株価が先に織り込み、2Qで期待を超えられない場合に倍率が下がることです。",
        "TIMELINE_ROWS": '<div class="time-row"><div class="time-date">2026/05/12</div><div class="time-dot"></div><div class="time-body"><b>2026年3月期決算</b><p>データセンタ関連製品の増収と収益改善を確認。</p><div class="time-meta"><span class="chip">決算</span></div></div></div><div class="time-row"><div class="time-date">2026/08/04</div><div class="time-dot"></div><div class="time-body"><b>光ファイバ・光ケーブル投資</b><p>需要増への生産能力対応を確認。</p><div class="time-meta"><span class="chip blue">成長投資</span></div></div></div><div class="time-row"><div class="time-date">2026/08/06</div><div class="time-dot"></div><div class="time-body"><b>2027年3月期1Q決算</b><p>通期業績予想を大きく上方修正。</p><div class="time-meta"><span class="chip">最重要</span></div></div></div><div class="time-row"><div class="time-date">2026/11ごろ</div><div class="time-dot"></div><div class="time-body"><b>2Q・中間決算</b><p>上方修正後の進捗を確認。</p><div class="time-meta"><span class="chip">確認</span></div></div></div>',
        "CATALYST_CARDS": "".join(cards) + '<p class="small">※下の％は、この結果が出た後に市場が材料を評価し直した場合の上昇・下落幅の目安です。実際の値動きは地合い、直前の株価上昇、同時ニュースで変わります。</p>',
        "DEPENDENCY_ROWS": '<div class="signal"><div><b>1Qと2Q</b><span class="up">連動</span></div><p>1Qが強くても、2Qで持続性が確認される必要があります。</p></div><div class="signal"><div><b>光通信と投資</b><span class="flat">重要</span></div><p>増産投資が高採算売上に変わるかを確認します。</p></div><div class="signal"><div><b>株価倍率</b><span class="down">注意</span></div><p>好材料の織り込みが進むほど決算ハードルは上がります。</p></div>',
        "WATCH_ROWS": '<div class="signal"><div><b>情報通信利益</b><span class="up">最重要</span></div><p>データセンタ関連の利益率が続くか。</p></div><div class="signal"><div><b>通期再修正</b><span class="up">重要</span></div><p>2Qでさらに上方修正余地があるか。</p></div><div class="signal"><div><b>設備投資</b><span class="flat">確認</span></div><p>光ファイバ投資の回収時期と採算。</p></div><div class="signal"><div><b>銅価格・為替</b><span class="down">注意</span></div><p>電線事業の採算影響を確認。</p></div>',
        "ASSUMPTION_ROWS": tr("評価基準株価", yen(P0), "市場データで確認", DATE, "2026/08/05終値") + tr("1Q経常利益", "310億円", "決算速報・会社開示", "2026/08/06", "前年同期比で大幅増") + tr("通期営業利益予想", "1,230億円", "会社上方修正", "2026/08/06", "従来950億円") + tr("通期経常利益予想", "1,430億円", "会社上方修正", "2026/08/06", "従来1,000億円"),
        "SOURCE_DETAILS": f'<ul><li>{source_link("公式IR", "ir")}</li><li>{source_link("IR資料室", "library")}</li><li>{source_link("業績概要・予想", "highlight")}</li><li>{source_link("経営方針説明会", "mid")}</li><li>{source_link("株価時系列", "yahoo")}</li></ul><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p>',
        "VALIDATION_DETAILS": "<p>PASS：公式IR、IR資料室、業績概要・予想、経営方針説明会、株価時系列を確認。1Q決算は2026年8月6日発表情報を反映。</p>",
        "UPDATE_HISTORY": f"<p>{DATE}：初版作成。2027年3月期1Q決算、通期上方修正、光ファイバ投資、データセンタ関連需要を反映。</p>",
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
        "id": "furukawa-electric-5801",
        "order": 12,
        "ticker": "5801",
        "quoteSymbol": "5801.T",
        "name": "古河電気工業",
        "nameEn": "Furukawa Electric Co., Ltd.",
        "market": "JP",
        "marketLabel": "日本株",
        "exchange": "東京証券取引所プライム市場",
        "currency": "JPY",
        "sector": "光通信・電力ケーブル・自動車部品・機能製品",
        "themes": ["データセンタ", "光通信", "電力インフラ"],
        "reports": {
            "company": {"path": "./stocks/furukawa-electric-5801/company.html", "available": True},
            "valuation": {"path": "./stocks/furukawa-electric-5801/valuation.html", "available": True},
            "catalysts": {"path": "./stocks/furukawa-electric-5801/catalysts.html", "available": True},
        },
    }
    stocks_payload["stocks"] = [item for item in stocks_payload["stocks"] if item["id"] != "furukawa-electric-5801"]
    stocks_payload["stocks"].append(stock)
    stocks_payload["stocks"].sort(key=lambda item: item["order"])
    stocks_path.write_text(json.dumps(stocks_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    prices_path = ROOT / "data" / "prices.json"
    prices_payload = json.loads(prices_path.read_text(encoding="utf-8"))
    prices_payload.setdefault("prices", {})["furukawa-electric-5801"] = {
        "symbol": "5801.T",
        "price": P0,
        "previousClose": PREVIOUS_CLOSE,
        "change": round(P0 - PREVIOUS_CLOSE, 1),
        "changePct": round((P0 - PREVIOUS_CLOSE) / PREVIOUS_CLOSE * 100, 4),
        "currency": "JPY",
        "marketTime": "2026-08-05T06:30:00+00:00",
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "ok",
    }
    prices_payload["quoteCount"] = len(prices_payload["prices"])
    prices_path.write_text(json.dumps(prices_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    signals_path = ROOT / "data" / "signals.json"
    signals_payload = json.loads(signals_path.read_text(encoding="utf-8"))
    signals_payload["updatedAt"] = datetime.now(timezone.utc).isoformat()
    signals_payload.setdefault("signals", {})["furukawa-electric-5801"] = {
        "position": SIGNAL_POSITION,
        "zone": "中立",
        "asOf": DATE,
        "components": {
            "valuation": round(BAND_POSITION, 1),
            "catalysts": CATALYST_SCORE,
            "businessRisk": BUSINESS_RISK_SCORE,
        },
        "reportRevision": "furukawa-electric-5801-2026-08-19",
        "summary": "1Q決算と通期上方修正は強い。光通信・データセンタ需要と増産投資は追い風だが、株価急騰後の材料織り込みと2Q進捗確認が必要。",
    }
    signals_path.write_text(json.dumps(signals_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_reports()
    upsert_site_data()


if __name__ == "__main__":
    main()
