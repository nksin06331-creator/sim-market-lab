"""Generate Murata Manufacturing report HTML files from the SiM templates."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from generate_rocket_lab_reports import dl, li, render_template


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stocks" / "murata-6981"
COMPANY = "村田製作所"
TICKER = "6981"
DATE = "2026-08-24"
P0 = 7091.0
PREVIOUS_CLOSE = 7205.0
SHARES_M = 1819.637
MARKET_CAP_TN = P0 * SHARES_M / 1_000_000

SOURCES = {
    "ir": "https://corporate.murata.com/ja-jp/ir",
    "q1": "https://corporate.murata.com/-/media/corporate/about/newsroom/news/irnews/irnews/2026/0731/26q1-j-fls.ashx?cvid=20260731015630000000&la=ja-jp",
    "forecast": "https://corporate.murata.com/ja-jp/ir/financial/forecast",
    "calendar": "https://corporate.murata.com/ir/calendar?sc_lang=ja-JP",
    "strategy": "https://corporate.murata.com/ja-jp/company/business-strategy/mid-term-policy",
    "company": "https://corporate.murata.com/ja-jp/company/factsandfigures",
    "price": "https://finance.yahoo.co.jp/quote/6981.T/history",
}


def yen(value: int | float) -> str:
    return f"{value:,.0f}円"


def details(title: str, body: str, open_: bool = False) -> str:
    return f"<details{' open' if open_ else ''}><summary>{title}</summary><p>{body}</p></details>"


def source_link(label: str, key: str) -> str:
    return f'<a href="{SOURCES[key]}" target="_blank" rel="noopener noreferrer">{label}</a>'


def tr(rows: list[tuple[str, ...]]) -> str:
    return "".join("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows)


def th(cells: list[str]) -> str:
    return "".join(f"<th>{cell}</th>" for cell in cells)


def guide_values() -> dict[str, str]:
    terms = [
        ("MLCC", "積層セラミックコンデンサ。電気を安定させる小型部品で、スマートフォン、車、AIサーバーに多数使われます。"),
        ("コンデンサ", "電気を一時的に蓄え、電圧を安定させる部品です。村田製作所の最大事業です。"),
        ("インダクタ", "電流の変化を抑え、電源や信号を安定させる電子部品です。"),
        ("EMIフィルタ", "電子機器のノイズを減らし、誤動作を防ぐ部品です。"),
        ("高周波モジュール", "スマートフォンなどの無線通信を支える複数部品をまとめた製品です。"),
        ("樹脂多層基板", "薄い樹脂層を重ねた高密度配線部品です。小型端末で使われます。"),
        ("電源モジュール", "機器が必要とする電圧へ効率よく変換する部品です。AIサーバー需要が注目されています。"),
        ("操業度益", "工場の稼働率が上がり、固定費を多くの製品へ配分できることで生じる利益改善です。"),
        ("BBレシオ", "受注額を出荷額で割った指標です。1を上回ると受注が出荷を上回ります。"),
        ("製品ミックス", "利益率の異なる製品の売上構成です。高信頼・大容量品が増えると採算が改善しやすくなります。"),
        ("中期方針2027", "2026年3月期から2028年3月期までの会社方針です。AIが生む電子部品需要を重点機会としています。"),
        ("為替感応度", "円相場が業績へ与える影響です。会社資料では対ドル1円の変動で年間営業利益約45億円が目安です。"),
    ]
    source_details = (
        '<details class="term-item" open><summary class="term-header"><span class="term-name">主要出典</span><span class="term-arrow">⌄</span></summary>'
        '<div class="term-body"><p>' + source_link("2027年3月期1Q決算短信", "q1") + "、" +
        source_link("会社業績予想", "forecast") + "、" + source_link("IRカレンダー", "calendar") + "、" +
        source_link("中期方針2027", "strategy") + "、" + source_link("会社概要", "company") +
        "を確認しました。株価は2026年8月21日終値です。</p><p><a href=\"../../index.html\">SiM MARKET LABの銘柄一覧へ戻る</a></p></div></details>"
    )
    return {
        "TICKER": TICKER, "COMPANY_NAME": COMPANY,
        "INDUSTRY": "電子部品・MLCC・通信モジュール",
        "DATE": DATE,
        "TAGLINE": "MLCCを中心に、通信、モビリティ、AIサーバー向けの電子部品を世界へ供給する総合電子部品メーカーです。",
        "HERO_TAGS": '<span class="hero-tag">日本株</span><span class="hero-tag">MLCC</span><span class="hero-tag">AIサーバー</span><span class="hero-tag">モビリティ</span>',
        "HERO_STATS": (
            f'<div class="stat"><div class="stat-value">{yen(P0)}</div><div class="stat-label">評価基準株価</div><div class="stat-note">2026/08/21終値</div></div>'
            f'<div class="stat"><div class="stat-value">{MARKET_CAP_TN:.1f}兆円</div><div class="stat-label">時価総額の目安</div><div class="stat-note">自己株式控除後で概算</div></div>'
            '<div class="stat"><div class="stat-value up">5,023億円</div><div class="stat-label">2027年3月期1Q売上</div><div class="stat-note">前年同期比20.7%増</div></div>'
            '<div class="stat"><div class="stat-value">985億円</div><div class="stat-label">同1Q営業利益</div><div class="stat-note">前年同期比59.8%増</div></div>'
        ),
        "SEC1_TLDR": li("MLCCを核に、スマートフォン、車、AIサーバーへ電子部品を供給します。", "*") + li("2027年3月期1Qは過去最高の四半期売上でした。", "*") + li("為替と電子部品需給で利益が大きく動きます。", "!"),
        "SEC1_FACTS": '<div><dt>正式社名</dt><dd>株式会社村田製作所</dd></div><div><dt>本社</dt><dd>京都府長岡京市</dd></div><div><dt>設立</dt><dd>1950年12月23日</dd></div><div><dt>上場</dt><dd>東証プライム（6981）</dd></div><div><dt>決算期</dt><dd>3月</dd></div><div><dt>会計基準</dt><dd>IFRS</dd></div>',
        "SEC1_CARDS": '<div class="card-sm"><span class="card-emoji">🔋</span><div class="card-title">コンデンサ</div><div class="card-desc">2027年3月期会社予想で売上の54.9%。MLCCが中心です。</div></div><div class="card-sm"><span class="card-emoji">📶</span><div class="card-title">通信部品</div><div class="card-desc">高周波モジュールや樹脂多層基板をスマートフォンへ供給します。</div></div><div class="card-sm"><span class="card-emoji">🚗</span><div class="card-title">モビリティ</div><div class="card-desc">電装化とADASで搭載される部品数が増えます。</div></div><div class="card-sm"><span class="card-emoji">🖥️</span><div class="card-title">AIサーバー</div><div class="card-desc">MLCC、電源モジュール、電池の需要拡大が成長を牽引します。</div></div>',
        "SEC1_BIZMODEL": '<li><span class="kp-emoji">🏭</span><span class="kp-text"><b>材料から量産まで</b>：セラミック材料、製品設計、生産技術を社内で磨きます。</span></li><li><span class="kp-emoji">🌍</span><span class="kp-text"><b>世界の機器メーカーへ販売</b>：通信、車、コンピュータ、産業機器へ供給します。</span></li><li><span class="kp-emoji">📈</span><span class="kp-text"><b>高機能化で数量増</b>：機器1台当たりの電子部品数と高付加価値品の比率が利益を動かします。</span></li>',
        "SEC1_HIGHLIGHT": '<div class="highlight"><h3>村田製作所を見る基本</h3><p>MLCCの数量だけでなく、AIサーバー・車向け高信頼品の構成、工場稼働率、値下げ、為替を分けて確認します。</p></div>',
        "SEC2_LABEL": "事業モデル", "SEC2_ICON": "🏭", "SEC2_TITLE": "電子部品で<span class=\"g\">どう稼ぐか</span>", "SEC2_SUB": "数量・製品構成・工場稼働率が利益を決める",
        "SEC2_TLDR": li("コンデンサは2027年3月期会社予想売上の約55%です。", "*") + li("AIサーバーと車向けは高信頼・高機能品が増えます。", "*") + li("市況悪化時は値下げと稼働率低下が重なります。", "!"),
        "SEC2_CONTENT": '<p class="lead">電子部品は大量生産で固定費を回収する事業です。需要増で稼働率が上がると利益が伸びやすい一方、在庫調整では逆回転します。</p><div class="term-list">' + details("数量", "スマートフォン台数、車両生産、サーバー投資が部品需要を動かします。", True) + details("製品構成", "大容量・高信頼・小型品の比率が採算を左右します。") + details("価格", "一般品の競争と毎期の値下げを、高付加価値化と合理化で吸収できるかが重要です。") + details("為替", "海外売上が大きく、円安は円換算売上と利益の押し上げ要因です。") + '</div>',
        "SEC3_LABEL": "主力製品", "SEC3_TITLE": "MLCCと<span class=\"g\">コンポーネント</span>", "SEC3_SUB": "AIサーバーとモビリティが数量・容量を押し上げる",
        "SEC3_TLDR": li("1Qコンデンサ売上は2,825億円で前年同期比30.0%増でした。", "*") + li("データセンターとモビリティ向けが中心に増えました。", "*") + li("供給能力と顧客在庫の変化を確認します。", "!"),
        "SEC3_CONTENT": '<div class="product-grid"><div class="product-box"><div class="product-symbol">MLCC</div><div class="product-name">積層セラミックコンデンサ</div><div class="product-use">電圧安定・ノイズ除去。機器1台に多数搭載。</div></div><div class="product-box"><div class="product-symbol">EMI</div><div class="product-name">ノイズ対策部品</div><div class="product-use">通信・車・サーバーの安定動作を支える。</div></div><div class="product-box"><div class="product-symbol">L</div><div class="product-name">インダクタ</div><div class="product-use">電源と信号を安定させる。</div></div></div><div class="sowhat"><p><b>つまり</b>、AI計算能力や車の電子制御が増えるほど、電源を安定させる部品の数量と性能要求が上がります。</p></div>',
        "SEC4_LABEL": "需要先", "SEC4_TITLE": "通信・車・<span class=\"g\">AIサーバー</span>", "SEC4_SUB": "用途ごとの成長速度と循環を分ける",
        "SEC4_TLDR": li("1Qのコンピュータ用途は前年同期比47.0%増でした。", "*") + li("通信は13.7%増、モビリティは16.1%増でした。", "*") + li("スマートフォンと家電は市況・顧客構成の影響が大きいです。", "!"),
        "SEC4_CONTENT": '<ul class="keypoints"><li><span class="kp-emoji">🖥️</span><span class="kp-text"><b>コンピュータ</b>：AIサーバー向けMLCC、電源モジュール、電池が伸びています。</span></li><li><span class="kp-emoji">🚗</span><span class="kp-text"><b>モビリティ</b>：電動化とADASでコンデンサ、フィルタ、センサが増えます。</span></li><li><span class="kp-emoji">📱</span><span class="kp-text"><b>通信</b>：スマートフォン台数と高機能化、主要顧客の製品構成が影響します。</span></li></ul>',
        "SEC5_LABEL": "競合比較", "SEC5_TITLE": "競合と<span class=\"g\">比べる</span>", "SEC5_SUB": "製品構成と量産力の違いを見る",
        "SEC5_TLDR": li("MLCCでは太陽誘電、TDK、Samsung Electro-Mechanicsなどが比較対象です。", "*") + li("村田は材料・設計・量産の総合力と幅広い用途を持ちます。", "*") + li("競合の増産と価格競争は継続的なリスクです。", "!"),
        "SEC5_CONTENT": '<div class="table-wrap"><table class="compare-table"><thead><tr><th>企業</th><th>主な特徴</th><th>確認点</th></tr></thead><tbody><tr><td class="me">村田製作所</td><td>MLCC、通信モジュール、電源、センサを幅広く展開。</td><td>AIサーバー向け構成と高い評価倍率。</td></tr><tr><td>TDK</td><td>受動部品、センサ、電池などの複合事業。</td><td>電池を含む事業構成が異なる。</td></tr><tr><td>太陽誘電</td><td>コンデンサを中心とする電子部品メーカー。</td><td>MLCC市況への感応度が高い。</td></tr><tr><td>Samsung Electro-Mechanics</td><td>MLCC、基板、カメラモジュールを展開。</td><td>供給能力と価格競争。</td></tr></tbody></table></div>',
        "SEC6_TLDR": li("MLCC、操業度益、製品ミックスを押さえると読みやすくなります。", "*") + li("BBレシオは需給の先行指標です。", "*") + li("為替効果と実需成長を分けて見ます。", "!"),
        "SEC6_CONTENT": '<div class="term-list">' + ''.join(details(a, b) for a, b in terms) + '</div>',
        "SEC7_TLDR": li("10月30日の2Q決算、11月30日のIR Dayが次の確認点です。", "*") + li("AIサーバー向け需要と通期上方修正の進捗が中心です。", "*") + li("期待先行、為替反転、供給増による価格下落に注意します。", "!"),
        "SEC7_CONTENT": '<div class="timeline"><div class="tl-row"><div class="tl-date">2026/10/30</div><div class="tl-title">2027年3月期2Q決算 <span class="signal bull">重要</span></div><div class="tl-desc">売上1兆400億円、営業利益2,020億円の会社上期予想に対する進捗を確認します。</div></div><div class="tl-row"><div class="tl-date">2026/11/30</div><div class="tl-title">2026年度IR Day <span class="signal neutral">確認</span></div><div class="tl-desc">AIサーバー、MLCC能力増強、中期方針2027の進捗を確認します。</div></div><div class="tl-row"><div class="tl-date">2027/02/02</div><div class="tl-title">2027年3月期3Q決算 <span class="signal neutral">確認</span></div><div class="tl-desc">需要継続と通期予想の確度を確認します。</div></div></div><div class="info-row"><div class="info-box info-box-green"><div class="info-title info-title-green">追い風</div><div class="info-text">AIサーバー、モビリティ、操業度益、自己株式取得。</div></div><div class="info-box info-box-amber"><div class="info-title info-title-amber">確認</div><div class="info-text">MLCC受注、能力増強、製品ミックス、上期進捗。</div></div><div class="info-box info-box-red"><div class="info-title info-title-red">リスク</div><div class="info-text">高い評価倍率、円高、値下げ、顧客在庫、競合増産。</div></div></div>' + source_details,
    }


def scenario_values() -> dict[str, str]:
    bear, base, bull = 4200, 6200, 8500
    probs = {"bear": .25, "base": .50, "bull": .25}
    expected = sum((bear * probs["bear"], base * probs["base"], bull * probs["bull"]))
    band = (P0 - bear) / (bull - bear) * 100
    own = (expected - bear) / (bull - bear) * 100
    rr = (bull - P0) / (P0 - bear)
    score = round(max(0, min(100, 50 + (expected / P0 - 1) * 100 - probs["bear"] * ((P0 - bear) / P0) * 100)))
    common_sources = source_link("1Q決算短信", "q1") + "、" + source_link("会社業績予想", "forecast") + "、" + source_link("株価時系列", "price")
    return {
        "COMPANY_NAME": COMPANY, "TICKER": TICKER, "EXCHANGE": "東京証券取引所プライム市場", "VALUATION_DATE": DATE,
        "METHOD": "景気循環電子部品向けPERシナリオ", "VERDICT_STATUS": "期待がかなり入った価格帯",
        "VERDICT_LINE_1": f"評価基準株価は悲観〜楽観レンジの{band:.1f}%地点です。1Q上振れとAIサーバー成長を強く反映しています。",
        "VERDICT_LINE_2": "分析値は2026年8月24日に固定し、株価は8月21日終値7,091円を使用しています。",
        "SCORE": str(score), "CURRENT_PRICE": yen(P0), "CURRENT_PRICE_NOTE": "2026/08/21 15:30", "BASE_PRICE": yen(base), "BASE_DELTA": "-12.6%", "EXPECTED_VALUE": yen(expected), "EXPECTED_DELTA": "-11.5%",
        "RISK_CLASS": "中", "RISK_NOTE": "電子部品循環、為替、高い評価倍率", "WARN_BAND": '<div class="wrap"><div class="notice" style="margin-top:14px"><b>注意：</b>会社予想EPS185.68円に対して評価基準株価は約38倍です。好材料が強く入った局面として前提の下振れを確認してください。</div></div>',
        "SNAPSHOT_LEAD": "会社は通期予想を上方修正しました。一方、株価は標準ケースを上回り、AIサーバー成長と利益率改善の継続をかなり先取りしています。",
        "BAND_POSITION": f"{band:.1f}%", "ZONE_JUDGE": "標準ケースより上", "ZONE_NOTE": "楽観ケースにはAIサーバー需要の継続、利益率維持、円安が必要です。",
        "BEAR_PRICE": yen(bear), "BULL_PRICE": yen(bull), "ENDPOINT_RR": f"{rr:.1f}倍", "MARKET_SCORE": str(round(band)), "OWN_SCORE": str(round(own)),
        "MARKET_REVERSE_NOTE": "会社予想EPS185.68円に対する現値PERは約38倍です。このモデルでは、2028年3月期EPSが約220円へ伸び、32倍前後の倍率が続く前提に近い水準です。市場全体の予想ではなくモデル上の逆算です。",
        "SCENARIOS_LEAD": "現在株価から独立して、2028年3月期の正常化EPSと電子部品企業としてのPERを組み合わせました。",
        "BEAR_PROB": "25%", "BASE_PROB": "50%", "BULL_PROB": "25%", "BEAR_DELTA": "-40.8%", "BULL_DELTA": "+19.9%",
        "BEAR_DL_ROWS": dl([("2028年3月期EPS", "175円"), ("PER", "24.0倍"), ("条件", "AI投資鈍化、円高、値下げ、稼働率低下")]),
        "BASE_DL_ROWS": dl([("2028年3月期EPS", "200円"), ("PER", "31.0倍"), ("条件", "会社予想達成後、AI・車向けが巡航成長")]),
        "BULL_DL_ROWS": dl([("2028年3月期EPS", "225円"), ("PER", "37.8倍"), ("条件", "AIサーバー高成長、製品構成改善、円安継続")]),
        "PRICE_ZONE_ROWS": tr([("4,200円未満", "悲観ケース未満", "需要・為替・稼働率の悪化を強く反映"), ("4,200～5,600円", "悲観寄り", "循環減速を一部反映"), ("5,600～6,700円", "標準周辺", "成長と循環リスクが均衡"), ("6,700～8,500円", "楽観寄り", "AI成長と高収益を強く反映"), ("8,500円超", "楽観ケース超", "追加の上方修正が必要")]),
        "SIGNAL_ROWS": tr([("2026/10/30", "2Q決算", "上期会社予想とコンピュータ用途の進捗"), ("2026/11/30", "IR Day", "AIサーバー、能力増強、中期方針"), ("四半期", "MLCC受注・稼働", "受注出荷比率、値下げ、製品構成"), ("随時", "為替", "会社前提155円/USDとの差")]),
        "POSITIVES": li("1Q売上は前年同期比20.7%増、営業利益は59.8%増でした。", "+") + li("会社は通期売上と営業利益を上方修正しました。", "+") + li("コンピュータ用途は1Qに47.0%増加しました。", "+"),
        "CONCERNS": li("株価は会社予想EPSの約38倍で、期待が高い水準です。", "-") + li("会社予想には第2四半期以降155円/USDを使用しています。", "-") + li("電子部品の値下げ、在庫調整、競合増産で利益率が変動します。", "-"),
        "ASSUMPTIONS_ROWS": tr([("評価時点", "2026/08/24", "公式情報で確認済み"), ("評価基準株価", "7,091円", "2026/08/21終値"), ("希薄化後株式数", "約18.20億株", "1Q期中平均株式数"), ("通期会社予想EPS", "185.68円", "2027年3月期"), ("純現金の目安", "約5,480億円", "現金等－借入金－リース負債")]),
        "CONDITIONS": li("悲観：AI投資減速、円高、一般品の値下げと稼働率低下。", "-") + li("標準：会社予想達成後、AI・車向けが巡航成長。", "*") + li("楽観：AIサーバー向け高成長と製品構成改善が継続。", "+"),
        "CALC_TABLE_HEAD": th(["ケース", "EPS", "PER", "1株価値"]), "CALC_TABLE_ROWS": tr([("悲観", "175円", "24.0倍", yen(bear)), ("標準", "200円", "31.0倍", yen(base)), ("楽観", "225円", "37.8倍", yen(bull))]),
        "FORMULA": "1株価値 ＝ 2028年3月期の条件付きEPS × 条件付きPER", "CALC_NOTICE": "PERは電子部品循環、成長率、財務余力、現在の市場評価を踏まえたこのレポートの推定です。",
        "SENSITIVITY_HEAD": th(["2028年EPS＼PER", "26倍", "31倍", "36倍"]), "SENSITIVITY_ROWS": tr([("180円", "4,680円", "5,580円", "6,480円"), ("200円", "5,200円", "6,200円", "7,200円"), ("220円", "5,720円", "6,820円", "7,920円")]), "SENSITIVITY_NOTE": "EPSとPERを別々に動かした単純感応度です。",
        "DIST_LEAD": "連続分布ではなく、3ケースだけの離散分布です。", "DIST_ROWS": tr([("悲観", yen(bear), "25%"), ("標準", yen(base), "50%"), ("楽観", yen(bull), "25%")]), "DIST_SUMMARY": f"3ケースを確率でならした値は{yen(expected)}です。",
        "DEEPDIVE_DETAILS": details("評価手法と逆算", "景気循環企業として2028年3月期の正常化EPSにPERを掛けました。現値はEPS220円・PER約32倍に相当します。", True) + details("株式数と財務", "1Q期中平均株式数約18.20億株を使用。2026年6月末の現金等5,575億円に対し、借入金とリース負債は約554億円です。自己株取得は将来EPSの上振れ要因ですが、価格と取得時期が未確定のため株式数へ先取りしていません。") + details("主要出典", common_sources + '<br><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>'),
        "WATCH_ROWS": tr([("2Q決算", "2026/10/30", "上期売上・利益、用途別売上、通期予想"), ("IR Day", "2026/11/30", "AIサーバー需要、能力増強、中期目標"), ("為替", "随時", "155円/USD前提との差")]),
        "WARN_MESSAGE": "評価倍率が高いため、業績が伸びても期待未達で下落する可能性があります。", "DISCLAIMER": "本レポートは情報提供を目的とした条件付き試算であり、売買を推奨するものではありません。", "FOOTER_NOTE": "分析値は2026年8月24日時点で固定しています。",
    }


def catalyst_values() -> dict[str, str]:
    def outcomes(rows: list[tuple[str, str, str]]) -> str:
        return '<div class="outcome-grid">' + ''.join(f'<div class="outcome"><b>{a}</b><span>{b}</span><small>{c}</small></div>' for a, b, c in rows) + '</div>'
    cards = (
        '<article class="catalyst-card"><h3>2027年3月期 第2四半期決算</h3><p class="lead">上方修正後の上期計画に対し、AIサーバー向け部品と利益率が計画どおり伸びているかを確認します。</p><div class="notice"><b>この％にした理由：</b>直近材料であり、通期EPSと高い評価倍率の両方を直接動かすため影響を大きめにしました。</div>' + outcomes([("期待以上", "+8～+18%", "上期計画超過、コンピュータ用途高成長、追加上方修正"), ("ほぼ想定どおり", "-5～+6%", "会社計画線、通期予想据え置き"), ("期待外れ・遅延", "-18～-8%", "AI需要鈍化、利益率低下、通期下方修正")]) + '</article>'
        '<article class="catalyst-card"><h3>2026年度 IR Day</h3><p class="lead">AIサーバー向けMLCC・電源部品の需要、供給能力、中期方針2027の進捗を会社が説明する予定です。</p><div class="notice"><b>この％にした理由：</b>中長期EPSと適用PERへ効きますが、決算ほど即時の数値更新を伴わないため幅を抑えました。</div>' + outcomes([("期待以上", "+5～+12%", "AI向け成長見通し・能力増強・収益性が期待以上"), ("ほぼ想定どおり", "-3～+4%", "既存方針の確認にとどまる"), ("期待外れ・遅延", "-12～-5%", "需要や能力増強の慎重化、収益目標の確度低下")]) + '</article>'
        '<article class="catalyst-card"><h3>MLCC受注・稼働率と製品構成</h3><p class="lead">AIサーバー、モビリティ、一般品の受注と工場稼働が高水準を保てるかを四半期ごとに確認します。</p><div class="notice"><b>この％にした理由：</b>全社売上の過半を占めるコンデンサの数量、価格、利益率を動かす継続材料です。</div>' + outcomes([("期待以上", "+6～+15%", "受注が出荷を上回り、高付加価値品比率も上昇"), ("ほぼ想定どおり", "-4～+5%", "能力増強と需要が均衡"), ("期待外れ・遅延", "-16～-7%", "在庫調整、値下げ、稼働率低下")]) + '</article>'
        '<p class="small">※上の％は、この結果が出た後に市場が材料を評価し直した場合の上昇・下落幅の目安です。実際の値動きは地合い、直前の株価上昇、同時ニュースで変わります。</p>'
    )
    sources = details("主要出典", source_link("1Q決算短信", "q1") + "、" + source_link("1Q決算説明資料", "ir") + "、" + source_link("IRカレンダー", "calendar") + "、" + source_link("中期方針2027", "strategy") + '<br><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>', True)
    return {
        "COMPANY_NAME": COMPANY, "TICKER": TICKER, "EXCHANGE": "東京証券取引所プライム市場", "VALUATION_DATE": DATE, "LAST_UPDATED": "2026/08/24",
        "REPORT_STATUS": "期待が先に高まっている", "CATALYST_COUNT": "3", "NEXT_CATALYST_WINDOW": "2026/10/30", "NEXT_CATALYST_TITLE": "2027年3月期 第2四半期決算",
        "SUMMARY_LINE_1": "AIサーバー向け需要と通期上方修正は強い一方、現在株価には大幅な利益成長がかなり入っています。",
        "SUMMARY_LINE_2": "2Q決算、IR Day、MLCC受注・稼働率を一つの連続した期待経路として確認します。",
        "CURRENT_PRICE": yen(P0), "CURRENT_PRICE_NOTE": "2026/08/21 15:30", "OVERALL_PRICED_IN": "算出していません", "OVERALL_PRICED_LABEL": "全体割合は出していません", "PRICED_IN_CONFIDENCE": "ふつう", "DATE_CONFIDENCE": "高い",
        "OVERALL_PRICED_BLOCK": '<div class="priced unknown"><h3>全体割合は出していません</h3><p><b>出していない理由：</b>2Q決算、IR Day、MLCC需給は同じAI需要と利益率前提に重なり、価値を独立に足せません。</p><p><b>足りない情報：</b>AI向け売上、製品別利益率、能力増強量の会社開示。</p><p><b>次に見る数字：</b>コンピュータ用途売上、コンデンサ受注、営業利益率、通期予想。</p><p><b>再計算方法：</b>開示された用途別成長率と利益率をEPSへ反映し、同一PERで条件付き価値を再計算します。</p></div>',
        "PRICED_IN_METHOD": "材料が同じ利益成長経路を共有するため、個別割合の平均は行いません。", "SURPRISE_UP": "追加上方修正とAI向け能力・採算の強い見通し", "SURPRISE_DOWN": "AI需要鈍化、値下げ、円高、通期予想の未達", "PRIMARY_RISK": "高い期待倍率の反動",
        "TIMELINE_ROWS": tr([("2026/10/30", "2Q決算", "日程確定", "上期計画と通期予想"), ("2026/11/30", "IR Day", "日程確定", "AIサーバー・能力増強・中期方針"), ("2027/02/02", "3Q決算", "日程確定", "通期達成確度")]),
        "CATALYST_CARDS": cards,
        "DEPENDENCY_ROWS": tr([("AI需要・利益率", "一連の材料", "2Q決算→IR Day→四半期需給", "同じ価値を重複加算しない"), ("為替", "共通前提", "会社予想155円/USD", "業績影響として一度だけ反映")]),
        "WATCH_ROWS": tr([("2Q決算", "2026/10/30", "売上、営業利益、用途別売上、通期予想"), ("IR Day", "2026/11/30", "AI向け需要、供給能力、中期目標"), ("MLCC需給", "四半期", "受注出荷比率、稼働率、値下げ"), ("為替", "随時", "155円/USD前提との差")]),
        "ASSUMPTION_ROWS": tr([("株価", "7,091円", "2026/08/21終値"), ("会社予想", "売上2兆1,100億円・営業利益4,300億円", "2027年3月期"), ("会社予想EPS", "185.68円", "2027年3月期"), ("為替", "155円/USD", "第2四半期以降の会社前提")]),
        "SOURCE_DETAILS": sources, "VALIDATION_DETAILS": details("検証結果", "日程は公式IRカレンダーの粒度を維持。3結果の影響幅は同一のEPS・PERモデルで再計算し、重複する材料は合算していません。", True),
        "UPDATE_HISTORY": "2026/08/24 初版", "NO_CATALYST_NOTICE": "", "WARN_BAND": '<div class="wrap"><div class="notice"><b>注意：</b>好決算の発表だけでは十分ではありません。現在の高い評価倍率を維持できる追加情報が必要です。</div></div>',
        "DISCLAIMER": "本レポートは情報提供を目的とした条件付き試算であり、売買を推奨するものではありません。", "FOOTER_NOTE": "分析値は2026年8月24日時点で固定しています。",
    }


def write_reports() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "company.html").write_text(render_template("template_stock_guide_v4_unified.html", guide_values()), encoding="utf-8")
    (OUT_DIR / "valuation.html").write_text(render_template("template_scenario_v4_unified.html", scenario_values()), encoding="utf-8")
    (OUT_DIR / "catalysts.html").write_text(render_template("template_catalyst_v1_unified.html", catalyst_values()), encoding="utf-8")


def upsert_site_data() -> None:
    stock_id = "murata-6981"
    stocks_path, prices_path, signals_path = ROOT / "data/stocks.json", ROOT / "data/prices.json", ROOT / "data/signals.json"
    stocks = json.loads(stocks_path.read_text(encoding="utf-8"))
    entry = {"id": stock_id, "order": 13, "ticker": TICKER, "quoteSymbol": "6981.T", "name": COMPANY, "nameEn": "Murata Manufacturing Co., Ltd.", "market": "JP", "marketLabel": "日本株", "exchange": "東京証券取引所プライム市場", "currency": "JPY", "sector": "電子部品・MLCC・通信モジュール", "themes": ["AIデータセンタ", "電子部品", "自動車"], "reports": {"company": {"path": "./stocks/murata-6981/company.html", "available": True}, "valuation": {"path": "./stocks/murata-6981/valuation.html", "available": True}, "catalysts": {"path": "./stocks/murata-6981/catalysts.html", "available": True}}}
    stocks["stocks"] = [s for s in stocks["stocks"] if s["id"] != stock_id] + [entry]
    stocks_path.write_text(json.dumps(stocks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    now = datetime.now(timezone.utc).isoformat()
    prices = json.loads(prices_path.read_text(encoding="utf-8"))
    prices["prices"][stock_id] = {"symbol": "6981.T", "price": P0, "previousClose": PREVIOUS_CLOSE, "change": P0 - PREVIOUS_CLOSE, "changePct": (P0 / PREVIOUS_CLOSE - 1) * 100, "currency": "JPY", "marketTime": "2026-08-21T06:30:00+00:00", "updatedAt": now, "status": "ok"}
    prices["quoteCount"] = len(prices["prices"]); prices["generatedAt"] = now
    prices_path.write_text(json.dumps(prices, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    signals = json.loads(signals_path.read_text(encoding="utf-8"))
    signals["signals"][stock_id] = {"position": 68.3, "zone": "中立", "asOf": DATE, "components": {"valuation": 67.2, "catalysts": 76.0, "businessRisk": 60.0}, "reportRevision": "murata-6981-2026-08-24", "summary": "1Q上振れとAIサーバー需要は強い一方、株価は会社予想EPSの約38倍で成長期待もかなり入っているため中立。"}
    signals["updatedAt"] = now
    signals_path.write_text(json.dumps(signals, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_reports()
    upsert_site_data()


if __name__ == "__main__":
    main()
