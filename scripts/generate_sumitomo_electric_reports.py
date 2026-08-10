"""Generate Sumitomo Electric report HTML files from the bundled SiM templates."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from generate_rocket_lab_reports import dl, li, render_template, th, tr


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stocks" / "sumitomo-electric-5802"

COMPANY = "住友電気工業"
TICKER = "5802"
DATE = "2026-08-09"
P0 = 2336.5
PREVIOUS_CLOSE = 2109.5
SHARES_M = 3165.0
MARKET_CAP_TN = P0 * SHARES_M / 1_000_000

SOURCES = {
    "ir": "https://sumitomoelectric.com/jp/ir",
    "library": "https://sumitomoelectric.com/jp/ir/library",
    "library_en": "https://sumitomoelectric.com/ir/library",
    "calendar": "https://sumitomoelectric.com/jp/ir/calendar",
    "faq": "https://sumitomoelectric.com/jp/ir/faq",
    "price": "https://jp.investing.com/equities/sumitomo-electric-industries-ltd.-historical-data",
    "kabutan": "https://s.kabutan.jp/stocks/5802/historical_prices/monthly/",
}


def yen(value: int | float) -> str:
    if value < 1000 and value != int(value):
        return f"{value:,.1f}円"
    return f"{value:,.0f}円"


def details(title: str, body: str, open_: bool = False) -> str:
    return f"<details{' open' if open_ else ''}><summary>{title}</summary><p>{body}</p></details>"


def source_link(label: str, key: str) -> str:
    return f'<a href="{SOURCES[key]}" target="_blank" rel="noopener noreferrer">{label}</a>'


def guide_values() -> dict[str, str]:
    source_details = (
        '<details class="term-item" open><summary class="term-header"><span class="term-name">主要出典</span><span class="term-arrow">⌄</span></summary>'
        '<div class="term-body"><p>'
        f'{source_link("住友電工公式IR", "ir")}、'
        f'{source_link("IR資料室", "library")}、'
        f'{source_link("英文IR Library", "library_en")}、'
        f'{source_link("IRカレンダー", "calendar")}、'
        f'{source_link("株価時系列", "price")}を確認しました。'
        "本文の数値は2026年8月9日時点の公開情報に基づきます。"
        '</p><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p></div></details>'
    )
    terms = [
        ("ワイヤーハーネス", "自動車内の電線束です。車の電動化・高機能化で重要度が高い部品です。"),
        ("電力ケーブル", "発電所、送電網、海底送電などに使う大型ケーブルです。再エネと電力インフラ投資が追い風です。"),
        ("情報通信", "光ファイバ、光部品、データセンター関連の通信インフラ事業です。"),
        ("エレクトロニクス", "FPC、電子線材、半導体関連などの部材事業です。"),
        ("産業素材", "超硬工具、焼結部品、特殊線など産業向け素材・部品です。"),
        ("自動車関連", "住友電工最大級の事業領域です。為替、車生産、銅価格、人件費が利益に影響します。"),
        ("データセンター関連", "光通信や高速接続部材の需要です。AI投資拡大で注目されています。"),
        ("中期経営計画2028", "会社が2026年5月に公表した中期計画です。事業ポートフォリオと成長投資の方向を示します。"),
        ("株式分割", "2026年5月に株式分割を発表しました。投資単位を下げ、流動性改善を狙う施策です。"),
        ("配当", "2026年3月期の配当と次期配当方針は、株主還元を見る材料です。"),
        ("銅価格", "電線・ケーブル材料として重要です。販売価格へ転嫁できるかが収益に影響します。"),
        ("為替感応度", "海外売上や海外生産が大きいため、円安・円高が業績に影響します。"),
    ]
    return {
        "TICKER": TICKER,
        "COMPANY_NAME": COMPANY,
        "INDUSTRY": "自動車部品・電線・光通信・電力インフラ",
        "DATE": DATE,
        "TAGLINE": "自動車用ワイヤーハーネス、電力ケーブル、光通信、エレクトロニクス、産業素材を展開する総合電線・部材メーカーです。",
        "HERO_TAGS": '<span class="hero-tag">日本株</span><span class="hero-tag">自動車部品</span><span class="hero-tag">電力ケーブル</span><span class="hero-tag">データセンター関連</span>',
        "HERO_STATS": (
            f'<div class="stat"><div class="stat-value">{yen(P0)}</div><div class="stat-label">評価基準株価</div><div class="stat-note">2026/07/31終値</div></div>'
            f'<div class="stat"><div class="stat-value">{MARKET_CAP_TN:.1f}兆円</div><div class="stat-label">時価総額の目安</div><div class="stat-note">分割後概算株式数で計算</div></div>'
            '<div class="stat"><div class="stat-value up">4.9兆円</div><div class="stat-label">2026年3月期売上</div><div class="stat-note">会社決算資料ベース</div></div>'
            '<div class="stat"><div class="stat-value">中計2028</div><div class="stat-label">注目計画</div><div class="stat-note">2026年5月公表</div></div>'
        ),
        "SEC2_LABEL": "事業モデル",
        "SEC3_LABEL": "自動車",
        "SEC4_LABEL": "電力・通信",
        "SEC5_LABEL": "競合比較",
        "SEC1_TLDR": li("住友電工は自動車、電力、通信、電子部材を持つ総合部材メーカーです。", "*") + li("2026年5月に中期経営計画2028と株式分割を公表しました。", "*") + li("株価は大きく上昇後に調整しており、1Q決算後の評価を慎重に見る局面です。", "!"),
        "SEC1_FACTS": (
            "<div><dt>正式社名</dt><dd>住友電気工業株式会社</dd></div><div><dt>本社</dt><dd>大阪市中央区</dd></div>"
            "<div><dt>上場</dt><dd>東証プライム（5802）</dd></div><div><dt>決算期</dt><dd>3月</dd></div>"
            "<div><dt>主な領域</dt><dd>自動車、電力、通信、電子、産業素材</dd></div><div><dt>業種</dt><dd>非鉄金属</dd></div>"
        ),
        "SEC1_CARDS": (
            '<div class="card-sm"><span class="card-emoji">🚗</span><div class="card-title">自動車</div><div class="card-desc">ワイヤーハーネスが主力。車の電動化で重要部品です。</div></div>'
            '<div class="card-sm"><span class="card-emoji">⚡</span><div class="card-title">電力</div><div class="card-desc">電力ケーブルやインフラ投資関連が成長テーマです。</div></div>'
            '<div class="card-sm"><span class="card-emoji">🌐</span><div class="card-title">通信</div><div class="card-desc">光ファイバやデータセンター関連需要が注目です。</div></div>'
            '<div class="card-sm"><span class="card-emoji">🧱</span><div class="card-title">素材</div><div class="card-desc">電子部材、産業素材、超硬工具も事業ポートフォリオを支えます。</div></div>'
        ),
        "SEC1_BIZMODEL": (
            '<li><span class="kp-emoji">🚗</span><span class="kp-text"><b>自動車</b>：ワイヤーハーネスを中心に世界の車両生産と電動化需要を取り込みます。</span></li>'
            '<li><span class="kp-emoji">⚡</span><span class="kp-text"><b>電力</b>：再エネ、送電網、海底ケーブルなど電力インフラ需要が支えます。</span></li>'
            '<li><span class="kp-emoji">🌐</span><span class="kp-text"><b>通信</b>：AI・データセンター投資で高速光通信関連の需要を狙います。</span></li>'
        ),
        "SEC1_HIGHLIGHT": '<div class="highlight"><h3>住友電工を見る基本ルール</h3><p>自動車の安定性、電力ケーブルの大型案件、データセンター関連の成長期待を分けて見ます。株式分割後の株価は過去データと単位が変わるため、比較時は注意が必要です。</p></div>',
        "SEC2_ICON": "🏭",
        "SEC2_TITLE": "事業モデルの<span class=\"g\">基本</span>",
        "SEC2_SUB": "複数事業の組み合わせで景気変動をならす",
        "SEC2_TLDR": li("自動車関連が大きく、電力・通信が成長テーマです。", "*") + li("為替、銅価格、車両生産、設備投資が業績を動かします。", "*") + li("中計2028で成長投資と収益力改善を確認します。", "!"),
        "SEC2_CONTENT": (
            '<p class="lead">住友電工は、ワイヤーハーネス、電力ケーブル、光通信、電子部材、産業素材を持つ総合部材メーカーです。景気敏感な面もありますが、複数事業で収益源が分散しています。</p>'
            '<div class="sowhat"><p><b>つまり</b>、5802は「自動車部品株」と「電力・データセンター関連株」の両方として見る銘柄です。</p></div>'
            '<div class="term-list">'
            + details("自動車関連", "ワイヤーハーネスを中心とする主力事業です。車両生産、電動化、海外人件費、為替で利益が動きます。", True)
            + details("電力インフラ", "電力ケーブルは再エネ・送電網投資と関係します。大型案件の進捗と採算が重要です。")
            + details("情報通信", "光通信、データセンター関連需要が注目です。AI投資の継続が追い風になります。")
            + details("株式分割", "2026年に株式分割を発表しました。投資単位低下と流動性改善が狙いです。")
            + "</div>"
        ),
        "SEC3_TITLE": "自動車関連と<span class=\"g\">ワイヤーハーネス</span>",
        "SEC3_SUB": "安定収益とコスト管理が焦点",
        "SEC3_TLDR": li("ワイヤーハーネスは車の神経網のような部品です。", "*") + li("電動化・高機能化で重要性は高まります。", "*") + li("労務費、物流費、銅価格、為替が利益を左右します。", "!"),
        "SEC3_CONTENT": (
            '<div class="product-grid"><div class="product-box"><div class="product-symbol">WH</div><div class="product-name">ワイヤーハーネス</div><div class="product-use">車内の電力・信号をつなぐ主力部品。</div></div>'
            '<div class="product-box"><div class="product-symbol">EV</div><div class="product-name">電動化部材</div><div class="product-use">高電圧・高機能化に対応。</div></div>'
            '<div class="product-box"><div class="product-symbol">ADAS</div><div class="product-name">高機能車</div><div class="product-use">センサー・制御の配線需要。</div></div></div>'
            '<div class="term-list">'
            + details("ワイヤーハーネス", "車内の電線束です。EVや高機能車ほど配線と接続の重要性が上がります。", True)
            + details("利益率の注意", "部材価格、人件費、物流費、顧客との価格改定で利益が変わります。")
            + details("車両生産", "自動車メーカーの生産台数が需要に直結します。地域別の生産動向も重要です。")
            + details("電動化", "EV、HEV、ADASで高電圧・高速通信・軽量化ニーズが増えます。")
            + "</div>"
        ),
        "SEC4_TITLE": "電力ケーブルと<span class=\"g\">データセンター</span>",
        "SEC4_SUB": "インフラ投資とAI需要を確認",
        "SEC4_TLDR": li("電力ケーブルは再エネ・送電網投資が追い風です。", "*") + li("データセンター関連は光通信需要として注目です。", "*") + li("大型案件は受注・納期・採算を分けて確認します。", "!"),
        "SEC4_CONTENT": (
            '<ul class="keypoints"><li><span class="kp-emoji">⚡</span><span class="kp-text"><b>電力ケーブル</b>：再エネ、送電網、海底ケーブルなどインフラ投資が追い風です。</span></li>'
            '<li><span class="kp-emoji">🌐</span><span class="kp-text"><b>光通信</b>：AI・クラウド投資でデータセンター関連需要が増えています。</span></li>'
            '<li><span class="kp-emoji">📄</span><span class="kp-text"><b>中計2028</b>：電力・通信関連の成長戦略と投資回収を確認します。</span></li></ul>'
            '<div class="sowhat"><p><b>つまり</b>、自動車以外の評価拡大には、電力とデータセンター関連の利益成長が必要です。</p></div>'
        ),
        "SEC5_TITLE": "競合と<span class=\"g\">比べる</span>",
        "SEC5_SUB": "電線・非鉄・自動車部品の横断企業",
        "SEC5_TLDR": li("比較対象は古河電工、フジクラ、SWCC、自動車部品大手です。", "*") + li("住友電工は自動車と電力・通信を広く持つ分散型です。", "*") + li("テーマ性だけでなく、各事業の利益率を確認します。", "!"),
        "SEC5_CONTENT": (
            '<div class="table-wrap"><table class="compare-table"><thead><tr><th>企業</th><th>主な強み</th><th>注意点</th></tr></thead><tbody>'
            '<tr><td class="me">住友電工</td><td>自動車、電力、通信、電子、素材の分散。</td><td>事業が広く、全体成長率は複数要因で決まる。</td></tr>'
            '<tr><td>古河電工</td><td>電線、光通信、インフラ関連。</td><td>採算改善と事業選別が焦点。</td></tr>'
            '<tr><td>フジクラ</td><td>データセンター・光通信テーマで評価されやすい。</td><td>期待が高い局面では倍率に注意。</td></tr>'
            '<tr><td>自動車部品大手</td><td>車両生産と電動化の恩恵。</td><td>顧客構成と価格転嫁で利益が変わる。</td></tr>'
            '</tbody></table></div><div class="highlight"><h3>差別化の見方</h3><p>住友電工は、電線・光通信テーマだけでなく、自動車ハーネスという大きな基盤を持ちます。派手さよりも、複数事業の利益改善を積み上げる銘柄です。</p></div>'
        ),
        "SEC6_TLDR": li("ワイヤーハーネス、電力ケーブル、データセンター、中計2028を押さえると読みやすいです。", "*") + li("株式分割後の価格比較には注意が必要です。", "*") + li("銅価格と為替は業績を動かします。", "!"),
        "SEC6_CONTENT": '<div class="term-list">' + "".join(details(name, body) for name, body in terms) + "</div>",
        "SEC7_TLDR": li("1Q決算、株式分割、中計2028、データセンター関連が主な材料です。", "*") + li("7月31日の1Q決算発表後、株価は大きく動いています。", "*") + li("期待先行の反動、為替、車両生産、銅価格には注意です。", "!"),
        "SEC7_CONTENT": (
            '<div class="timeline"><div class="tl-row"><div class="tl-date">2026/05/12</div><div class="tl-title">2026年3月期決算・株式分割 <span class="signal bull">追い風</span></div><div class="tl-desc">通期決算、中計2028、株式分割が公表されました。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/07/31</div><div class="tl-title">2026年度1Q決算 <span class="signal neutral">重要</span></div><div class="tl-desc">IRカレンダー上の決算発表日。発表後の株価変動が大きくなっています。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/10-11</div><div class="tl-title">2Q・中間決算 <span class="signal bull">確認</span></div><div class="tl-desc">自動車、電力、通信の利益進捗を確認します。</div></div></div>'
            '<div class="info-row"><div class="info-box info-box-green"><div class="info-title info-title-green">追い風</div><div class="info-text">中計2028、電力ケーブル、データセンター関連、株式分割。</div></div>'
            '<div class="info-box info-box-amber"><div class="info-title info-title-amber">確認</div><div class="info-text">1Q後の株価反応、2Q進捗、自動車関連の採算。</div></div>'
            '<div class="info-box info-box-red"><div class="info-title info-title-red">リスク</div><div class="info-text">高値からの調整、為替、銅価格、車両生産、期待先行。</div></div></div>'
            + source_details
        ),
    }


def scenario_values() -> dict[str, str]:
    bear, base, bull = 1900, 2450, 3200
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
        "EXCHANGE": "東京証券取引所プライム市場",
        "VALUATION_DATE": DATE,
        "METHOD": "分散型製造業向けPER・EV/EBITDAシナリオ",
        "VERDICT_STATUS": "標準ケース手前の中立圏",
        "VERDICT_LINE_1": "評価基準株価は悲観〜楽観レンジの33.6%地点です。高値から調整しており、標準ケースまでは余地がありますが、1Q後の業績確認が必要です。",
        "VERDICT_LINE_2": "この試算は2026年8月9日時点の公開情報で固定しています。株価は2026年7月31日終値2,336.5円を基準にしています。",
        "SCORE": str(score),
        "CURRENT_PRICE": yen(P0),
        "CURRENT_PRICE_NOTE": "2026/07/31 15:30",
        "BASE_PRICE": yen(base),
        "BASE_DELTA": "+4.9%",
        "EXPECTED_VALUE": yen(expected),
        "EXPECTED_DELTA": "+7.0%",
        "RISK_CLASS": "中",
        "RISK_NOTE": "大型製造業、為替・銅価格・景気に連動",
        "WARN_BAND": '<div class="wrap"><div class="notice" style="margin-top:14px"><b>注意：</b>株式分割後の価格を基準にしています。過去株価との比較では単位変更に注意してください。</div></div>',
        "SNAPSHOT_LEAD": "今の株価は、悲観ケースより上、標準ケースより少し下です。中計や電力・通信テーマは支えですが、1Q後の進捗確認が必要です。",
        "BAND_POSITION": f"{band:.1f}%",
        "ZONE_JUDGE": "標準ケースの手前",
        "ZONE_NOTE": "2Qで自動車、電力、通信の進捗が強ければ標準〜楽観側へ寄ります。",
        "BEAR_PRICE": yen(bear),
        "BULL_PRICE": yen(bull),
        "ENDPOINT_RR": f"{endpoint_rr:.1f}倍",
        "MARKET_SCORE": str(round(band)),
        "OWN_SCORE": str(round(own_score)),
        "MARKET_REVERSE_NOTE": "このモデルで逆算すると、今の株価は分割後EPSに対してPER13〜14倍程度、または中計成長を一部織り込む水準です。市場全体の予想ではなく、このモデル上の逆算です。",
        "SCENARIOS_LEAD": "現在株価から独立して、営業利益、EPS、PER、電力・通信の成長期待を置きました。分散型製造業なのでPERとEV/EBITDAを併用します。",
        "BEAR_PROB": "25%",
        "BASE_PROB": "50%",
        "BULL_PROB": "25%",
        "BEAR_DELTA": "-18.7%",
        "BULL_DELTA": "+36.9%",
        "BEAR_DL_ROWS": dl([("EPS", "150円"), ("PER", "12.7倍"), ("前提", "自動車採算弱含み"), ("営業利益", "4,000億円台")]),
        "BASE_DL_ROWS": dl([("EPS", "175円"), ("PER", "14.0倍"), ("前提", "中計どおり改善"), ("営業利益", "5,000億円前後")]),
        "BULL_DL_ROWS": dl([("EPS", "210円"), ("PER", "15.2倍"), ("前提", "電力・通信が上振れ"), ("営業利益", "5,500億円超")]),
        "PRICE_ZONE_ROWS": '<div class="zone"><div><b>1,900円未満</b><span>★★★★</span></div><p>悲観ケース以下。景気悪化や採算低下をかなり織り込む価格帯です。</p></div><div class="zone"><div><b>1,900〜2,450円</b><span>★★★</span></div><p>標準ケース手前。今の株価はこの範囲です。</p></div><div class="zone"><div><b>2,450〜3,200円</b><span>★★</span></div><p>中計達成と電力・通信成長を評価する価格帯です。</p></div><div class="zone"><div><b>3,200円超</b><span>★</span></div><p>楽観ケース超。さらに強い利益成長と倍率拡大が必要です。</p></div>',
        "SIGNAL_ROWS": '<div class="signal"><div><b>中計2028</b><span class="up">追い風</span></div><p>成長投資と事業ポートフォリオの方向性を示します。</p></div><div class="signal"><div><b>電力・通信需要</b><span class="up">追い風</span></div><p>電力ケーブルとデータセンター関連が注目です。</p></div><div class="signal"><div><b>自動車採算</b><span class="flat">確認</span></div><p>人件費、物流費、価格転嫁を確認します。</p></div><div class="signal"><div><b>株価変動</b><span class="down">注意</span></div><p>分割後に値動きが大きくなっています。</p></div>',
        "POSITIVES": "<li>自動車、電力、通信、電子、素材と事業が分散しています。</li><li>電力ケーブルとデータセンター関連は中期成長テーマです。</li><li>中期経営計画2028で成長戦略が明確化されています。</li><li>株式分割により投資単位低下と流動性改善が期待されます。</li>",
        "CONCERNS": "<li>株価は2026年に大きく上昇した後、調整も大きくなっています。</li><li>為替、銅価格、車両生産、人件費で利益が変動します。</li><li>事業が広いため、成長テーマだけで全社利益が決まるわけではありません。</li><li>1Q後の詳しい進捗確認が必要です。</li>",
        "FORMULA": "主計算はPERです。補助的にEV/EBITDAを見ます。大型製造業なので、短期テーマだけでなく利益水準と倍率を分けて見ました。",
        "CALC_TABLE_HEAD": th("ケース", "EPS", "PER", "計算株価", "確率", "確率加重"),
        "CALC_TABLE_ROWS": tr("悲観", "150円", "12.7倍", yen(bear), "25%", "475円") + tr("標準", "175円", "14.0倍", yen(base), "50%", "1,225円") + tr("楽観", "210円", "15.2倍", yen(bull), "25%", "800円"),
        "CALC_NOTICE": "現在株価に合わせて標準ケースを置いていません。中計、電力・通信、自動車採算、株式分割後の需給を踏まえた条件付き試算です。",
        "CONDITIONS": details("悲観ケース：1,900円 / 確率25%", "自動車採算や景気が弱く、電力・通信の成長期待も縮むケースです。", True) + details("標準ケース：2,450円 / 確率50%", "中計に沿って利益改善が進み、PERが適度に維持されるケースです。") + details("楽観ケース：3,200円 / 確率25%", "電力ケーブル、データセンター関連、自動車採算改善が重なるケースです。"),
        "SENSITIVITY_HEAD": th("前提", "弱い", "標準", "強い"),
        "SENSITIVITY_ROWS": tr("EPS", "160円 → 2,240円", "175円 → 2,450円", "190円 → 2,660円") + tr("PER", "12倍 → 2,100円", "14倍 → 2,450円", "16倍 → 2,800円"),
        "SENSITIVITY_NOTE": "1変数だけを動かした簡易感応度です。実際にはEPSとPERが同時に動きます。",
        "DIST_LEAD": "モンテカルロではなく、悲観・標準・楽観の3点分布です。",
        "DIST_ROWS": '<div class="dist-row"><span>1,900円</span><div class="track"><i style="width:25%"></i></div><b>25%</b></div><div class="dist-row"><span>2,450円</span><div class="track"><i style="width:50%"></i></div><b>50%</b></div><div class="dist-row"><span>3,200円</span><div class="track"><i style="width:25%"></i></div><b>25%</b></div>',
        "DIST_SUMMARY": "中心は標準ケースです。大型株ですが、分割後の需給とテーマ性で値動きは大きめです。",
        "WATCH_ROWS": '<div class="signal"><div><b>2Q・中間決算</b></div><p>自動車、電力、通信の利益進捗を確認します。</p></div><div class="signal"><div><b>電力ケーブル受注</b></div><p>大型案件の採算と納期を確認します。</p></div><div class="signal"><div><b>データセンター関連</b></div><p>光通信関連の需要継続を確認します。</p></div>',
        "ASSUMPTIONS_ROWS": tr("評価基準株価", yen(P0), "市場データで確認済み", "2026/07/31終値") + tr("株式分割", "公表済み", "会社発表", "2026/05/12", "比較時は単位に注意") + tr("中期経営計画", "中計2028", "会社発表", "2026/05", "成長戦略の前提") + tr("1Q決算発表日", "2026/07/31", "IRカレンダーで確認", "2026年度1Q", "詳細資料確認が必要"),
        "DEEPDIVE_DETAILS": details("手法選定理由", "住友電工は黒字の大型製造業です。PERを主に使い、電力・通信テーマの倍率変化を補助的に見ます。", True) + details("株式分割について", "2026年5月に株式分割を公表しています。このレポートでは分割後株価水準で表示しています。") + details("主要出典", f'{source_link("公式IR", "ir")}、{source_link("IR資料室", "library")}、{source_link("IRカレンダー", "calendar")}、{source_link("株価時系列", "price")}。<br><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>'),
        "DISCLAIMER": "本資料は情報提供を目的とした試算です。投資助言ではありません。製造業株は景気、為替、原材料、顧客生産、投資計画により大きく変動します。",
        "FOOTER_NOTE": f"SiM MARKET LAB｜{COMPANY}（{TICKER}）株価シナリオ｜作成日 {DATE}",
    }


def catalyst_values() -> dict[str, str]:
    non_quant = '<div class="priced"><div class="priced-head"><span>主要材料の推定織り込み</span><b>49%</b></div><p>仮定：1Q決算の好材料消化を55%、中計2028達成期待を50%、電力・データセンター需要を55%、株式分割後の需給改善を35%として置き、重複を控除しました。</p><p>読み方：電力・通信テーマは一定評価されていますが、2Q進捗とセグメント利益確認前のため、織り込みは中程度です。</p><p>次に見る数字：自動車関連利益、電力・通信売上、営業利益率、受注残です。</p><p>再計算方法：EPS、PER、セグメント利益、株式数を分け、株価シナリオと同じモデルで更新します。</p></div>'
    impact_map = {
        "2026年度1Q決算の消化": ("+5〜13%", "-3〜+5%", "-8〜-16%", "大型株の実績確認材料なので、短期影響は中程度。ただし通期進捗が崩れると下押しします。"),
        "中期経営計画2028": ("+7〜16%", "-4〜+6%", "-8〜-18%", "中計はPERの土台に効くため重要ですが、実績化まで時間があるためレンジを中程度にしています。"),
        "電力ケーブル・インフラ需要": ("+8〜20%", "-4〜+7%", "-10〜-22%", "電力インフラは利益成長の中核候補で、受注と採算が見えると全社評価を押し上げます。"),
        "データセンター関連需要": ("+6〜15%", "-3〜+6%", "-8〜-16%", "光通信・DCテーマは追い風ですが、住友電工全社に占める寄与は段階的なので中程度です。"),
    }
    description_map = {
        "2026年度1Q決算の消化": "1Q決算の消化は、発表された内容を市場がどう評価し直すかを見る材料です。自動車、電力、通信のどこが伸びたか、利益率が保てたかで次の中間決算への期待が変わります。",
        "中期経営計画2028": "中計2028は、住友電工がどの事業に投資し、どの程度の利益成長を目指すかを示す中期材料です。計画そのものより、四半期実績で進捗が確認できるかが重要です。",
        "電力ケーブル・インフラ需要": "電力ケーブル・インフラ需要は、送電網投資や再エネ関連投資を背景にした成長材料です。受注が増えるだけでなく、採算が良い案件として利益に変わるかを見ます。",
        "データセンター関連需要": "データセンター関連需要は、AI・クラウド投資に伴う光通信部品や関連製品の伸びを見る材料です。全社規模では段階的な寄与ですが、成長テーマとして倍率を支えます。",
    }

    def card(title: str, date: str, chips: str, mechanism: str, success: str, inline: str, failure: str, evidence: str) -> str:
        up, flat, down, reason = impact_map[title]
        description = description_map[title]
        return f'''<article class="catalyst-card">
<div class="catalyst-head"><div><span class="pill">重要材料</span><h3>{title}</h3><div class="chips">{chips}</div></div><div class="date-box"><b>{date}</b><span>会社公表またはイベント期間</span></div></div>
<p class="lead">{description}</p>
<div class="mechanism">{mechanism}</div>
<div class="outcomes">
<div class="outcome success"><b>期待以上</b><div class="impact up">{up}</div><p>{success}</p></div>
<div class="outcome inline"><b>ほぼ想定どおり</b><div class="impact flat">{flat}</div><p>{inline}</p></div>
<div class="outcome failure"><b>期待外れ・遅延</b><div class="impact down">{down}</div><p>{failure}</p></div>
</div>
<p class="notice"><b>この％にした理由：</b>{reason}</p>
<div class="evidence"><div><h4>根拠</h4><ul>{evidence}</ul></div><div><h4>反証・先行指標</h4><ul><li>セグメント利益率低下</li><li>為替・銅価格の逆風</li><li>自動車生産の減速</li></ul></div></div>
</article>'''

    cards = [
        card("2026年度1Q決算の消化", "2026/07/31", '<span class="chip">重要度5</span><span class="chip">発表済み</span>', '<span>1Q実績</span><i>→</i><span>通期進捗</span><i>→</i><span>倍率</span>', "自動車、電力、通信の利益進捗が強く、通期上振れ期待が高まる状態です。", "進捗はおおむね想定どおりで、2Q確認待ちの状態です。", "採算悪化や一過性要因が嫌気される状態です。", "<li>IRカレンダーで2026年7月31日15:00に1Q決算発表と確認。</li><li>発表後の株価変動が大きく、内容消化が重要です。</li>"),
        card("中期経営計画2028", "2026/05以降", '<span class="chip">重要度5</span><span class="chip">公表済み</span>', '<span>中計</span><i>→</i><span>利益成長</span><i>→</i><span>PER</span>', "電力・通信・自動車の成長投資が利益成長として見え、倍率が維持される状態です。", "中計は評価されるが、実績確認まで様子見の状態です。", "投資負担や採算悪化が先に見え、期待が後退する状態です。", "<li>2026年5月に中期経営計画2028を公表。</li><li>IR資料室に全体版が掲載されています。</li>"),
        card("電力ケーブル・インフラ需要", "2026-2028", '<span class="chip">重要度4</span><span class="chip blue">中期材料</span>', '<span>受注</span><i>→</i><span>採算</span><i>→</i><span>利益</span>', "大型案件の受注と採算改善が見え、電力事業の評価が上がる状態です。", "受注は堅調だが、利益寄与は段階的な状態です。", "納期遅延、コスト増、採算悪化が見える状態です。", "<li>会社は電力ケーブル事業を成長テーマとして継続説明。</li><li>再エネ・送電網投資が背景にあります。</li>"),
        card("データセンター関連需要", "2026-2028", '<span class="chip">重要度4</span><span class="chip blue">中期材料</span>', '<span>AI投資</span><i>→</i><span>光通信</span><i>→</i><span>成長期待</span>', "データセンター投資が続き、光通信関連の成長が全社評価を押し上げる状態です。", "需要は堅調だが、全社インパクトは段階的な状態です。", "顧客投資の減速や競争激化で期待が下がる状態です。", "<li>IR資料室にデータセンター関連事業の成長戦略資料が掲載されています。</li><li>AI・クラウド投資が背景にあります。</li>"),
    ]
    return {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "東京証券取引所プライム市場",
        "VALUATION_DATE": DATE,
        "LAST_UPDATED": DATE,
        "REPORT_STATUS": "重要材料が複数",
        "SUMMARY_LINE_1": "1Q決算、中計2028、電力ケーブル、データセンター関連が今後の主な材料です。",
        "SUMMARY_LINE_2": "足りない情報は仮定を置き、主要材料の織り込み度を49%と推定します。",
        "OVERALL_PRICED_IN": "49%",
        "OVERALL_PRICED_LABEL": "主要材料の推定織り込み",
        "PRICED_IN_CONFIDENCE": "ふつう",
        "CURRENT_PRICE": yen(P0),
        "CURRENT_PRICE_NOTE": "2026/07/31 15:30",
        "NEXT_CATALYST_TITLE": "2Q・中間決算",
        "NEXT_CATALYST_WINDOW": "2026年10〜11月ごろ",
        "DATE_CONFIDENCE": "当方推定",
        "CATALYST_COUNT": "4件",
        "WARN_BAND": "",
        "NO_CATALYST_NOTICE": "",
        "OVERALL_PRICED_BLOCK": non_quant,
        "PRICED_IN_METHOD": "未確定情報に仮定確率を置き、1Q決算、中計2028、電力・データセンター需要、株式分割後の需給を標準ケース価値へ重み付けして推定。",
        "SURPRISE_UP": "2Qで自動車採算、電力ケーブル、光通信がそろって強いことです。",
        "SURPRISE_DOWN": "1Q後の期待が剥落し、為替・銅価格・自動車生産の逆風が見えることです。",
        "PRIMARY_RISK": "株式分割後にテーマ性で上がった後、業績確認で倍率が下がる可能性です。",
        "TIMELINE_ROWS": '<div class="time-row"><div class="time-date">2026/05/12</div><div class="time-dot"></div><div class="time-body"><b>通期決算・株式分割・中計2028</b><p>成長戦略と資本政策を確認します。</p><div class="time-meta"><span class="chip">公表済み</span></div></div></div><div class="time-row"><div class="time-date">2026/07/31</div><div class="time-dot"></div><div class="time-body"><b>2026年度1Q決算</b><p>発表後の株価変動が大きく、内容消化が焦点です。</p><div class="time-meta"><span class="chip">発表済み</span></div></div></div><div class="time-row"><div class="time-date">2026/10-11</div><div class="time-dot"></div><div class="time-body"><b>2Q・中間決算</b><p>自動車、電力、通信の進捗を確認します。</p><div class="time-meta"><span class="chip blue">時期推定</span></div></div></div>',
        "CATALYST_CARDS": "".join(cards) + '<p class="small">※下の％は、この結果が出た後に市場が材料を評価し直した場合の上昇・下落幅の目安です。実際の値動きは地合い、直前の株価上昇、同時ニュースで変わります。</p>',
        "DEPENDENCY_ROWS": '<div class="signal"><div><b>中計と2Q進捗</b><span class="up">連動</span></div><p>中計が評価されるには、四半期実績で利益改善が必要です。</p></div><div class="signal"><div><b>電力と通信</b><span class="up">成長経路</span></div><p>電力ケーブルとデータセンター関連は評価拡大の材料です。</p></div><div class="signal"><div><b>自動車と為替</b><span class="flat">確認</span></div><p>主力事業の採算と為替影響を確認します。</p></div>',
        "WATCH_ROWS": '<div class="signal"><div><b>セグメント利益</b><span class="up">最重要</span></div><p>自動車、電力、通信のどこが伸びたかを確認します。</p></div><div class="signal"><div><b>通期予想修正</b><span class="up">重要</span></div><p>上方修正や配当方針の変化を確認します。</p></div><div class="signal"><div><b>株式分割後の需給</b><span class="flat">確認</span></div><p>流動性改善と値動きの荒さを確認します。</p></div><div class="signal"><div><b>銅価格・為替</b><span class="down">注意</span></div><p>原材料と為替の利益影響を確認します。</p></div>',
        "ASSUMPTION_ROWS": tr("評価基準株価", yen(P0), "市場データで確認済み", DATE, "2026/07/31終値") + tr("1Q決算発表", "2026/07/31", "IRカレンダーで確認", "2026年度1Q", "発表済み") + tr("中計2028", "公表済み", "会社発表", "2026/05", "成長戦略") + tr("株式分割", "公表済み", "会社発表", "2026/05/12", "単位比較に注意"),
        "SOURCE_DETAILS": f'<ul><li>{source_link("公式IR", "ir")}</li><li>{source_link("IR資料室", "library")}</li><li>{source_link("IRカレンダー", "calendar")}</li><li>{source_link("株価時系列", "price")}</li><li>{source_link("株探時系列", "kabutan")}</li></ul><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p>',
        "VALIDATION_DETAILS": "<p>PASS：公式IR、IR資料室、IRカレンダー、株価時系列を確認。WARN：1Qの詳細数値は公式ライブラリ更新反映待ちのため、2Qで再確認します。</p>",
        "UPDATE_HISTORY": f"<p>{DATE}：初版作成。2026年3月期決算、中計2028、株式分割、2026年度1Q決算予定・株価反応を反映。</p>",
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
        "id": "sumitomo-electric-5802",
        "order": 5,
        "ticker": "5802",
        "quoteSymbol": "5802.T",
        "name": "住友電気工業",
        "nameEn": "Sumitomo Electric Industries, Ltd.",
        "market": "JP",
        "marketLabel": "日本株",
        "exchange": "東京証券取引所プライム市場",
        "currency": "JPY",
        "sector": "自動車部品・電線・光通信・電力インフラ",
        "reports": {
            "company": {"path": "./stocks/sumitomo-electric-5802/company.html", "available": True},
            "valuation": {"path": "./stocks/sumitomo-electric-5802/valuation.html", "available": True},
            "catalysts": {"path": "./stocks/sumitomo-electric-5802/catalysts.html", "available": True},
        },
    }
    stocks_payload["stocks"] = [item for item in stocks_payload["stocks"] if item["id"] != "sumitomo-electric-5802"]
    stocks_payload["stocks"].append(stock)
    stocks_path.write_text(json.dumps(stocks_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    prices_path = ROOT / "data" / "prices.json"
    prices_payload = json.loads(prices_path.read_text(encoding="utf-8"))
    prices_payload.setdefault("prices", {})["sumitomo-electric-5802"] = {
        "symbol": "5802.T",
        "price": P0,
        "previousClose": PREVIOUS_CLOSE,
        "change": round(P0 - PREVIOUS_CLOSE, 1),
        "changePct": round((P0 - PREVIOUS_CLOSE) / PREVIOUS_CLOSE * 100, 4),
        "currency": "JPY",
        "marketTime": "2026-07-31T06:30:00+00:00",
        "updatedAt": "2026-08-09T00:00:00+00:00",
        "status": "ok",
    }
    prices_payload["quoteCount"] = len(prices_payload["prices"])
    prices_path.write_text(json.dumps(prices_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    signals_path = ROOT / "data" / "signals.json"
    signals_payload = json.loads(signals_path.read_text(encoding="utf-8"))
    signals_payload["updatedAt"] = datetime.now(timezone.utc).isoformat()
    signals_payload.setdefault("signals", {})["sumitomo-electric-5802"] = {
        "position": 45.9,
        "zone": "中立",
        "asOf": DATE,
        "components": {
            "valuation": 33.6,
            "catalysts": 68.0,
            "businessRisk": 58.0,
        },
        "reportRevision": "sumitomo-electric-5802-2026-08-09",
        "summary": "株価は標準ケース手前まで調整。中計2028、電力・通信テーマは支えだが、1Q後の進捗と需給確認前のため中立。",
    }
    signals_path.write_text(json.dumps(signals_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_reports()
    upsert_site_data()


if __name__ == "__main__":
    main()
