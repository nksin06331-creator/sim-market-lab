"""Generate Paycloud report HTML files from the bundled SiM templates."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from generate_rocket_lab_reports import dl, li, render_template, th, tr


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stocks" / "paycloud-4015"

COMPANY = "ペイクラウドホールディングス"
TICKER = "4015"
DATE = "2026-08-08"
P0 = 540
PREVIOUS_CLOSE = 540
SHARES_M = 15.96
MARKET_CAP_BN = P0 * SHARES_M / 1000

SOURCES = {
    "ir": "https://www.paycloud.inc/ir/?lang=ja",
    "q3_summary": "https://disclosure.catr.jp/companies/75be7/84566/tdnet/fbd5b/742154",
    "yahoo_financials": "https://finance.yahoo.co.jp/quote/4015.T/financials",
    "disclosure": "https://finance.yahoo.co.jp/quote/4015.T/disclosure",
    "movie": "https://www.paycloud.inc/ir/movie/?lang=japage%2F2%2Fpage%2F2%2Fpage%2F3%2Fpage%2F2%2Fpage%2F4%2F",
    "faq": "https://www.paycloud.inc/ir/faq/",
    "note_q3": "https://note.com/paycloud/n/nd2c4e226f4c8?hl=en",
    "benefit": "https://www.paycloud.inc/ir/benefit/",
    "price": "https://jp.investing.com/equities/arara-inc-historical-data",
}


def yen(value: int | float) -> str:
    return f"{int(round(value)):,}円"


def details(title: str, body: str, open_: bool = False) -> str:
    return f"<details{' open' if open_ else ''}><summary>{title}</summary><p>{body}</p></details>"


def source_link(label: str, key: str) -> str:
    return f'<a href="{SOURCES[key]}" target="_blank" rel="noopener noreferrer">{label}</a>'


def guide_values() -> dict[str, str]:
    source_details = (
        '<details class="term-item" open><summary class="term-header"><span class="term-name">主要出典</span><span class="term-arrow">⌄</span></summary>'
        '<div class="term-body"><p>'
        f'{source_link("ペイクラウド公式IR", "ir")}、'
        f'{source_link("2026年8月期3Q決算情報", "q3_summary")}、'
        f'{source_link("Yahoo!ファイナンス決算要約", "yahoo_financials")}、'
        f'{source_link("適時開示一覧", "disclosure")}、'
        f'{source_link("3Q決算説明動画・書き起こし", "movie")}を確認しました。'
        "本文の数値は2026年8月8日時点の公開情報に基づきます。"
        '</p><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p></div></details>'
    )
    terms = [
        ("独自Pay", "企業や店舗が自社ブランドで電子マネー・ポイント・デジタルギフトを発行する仕組みです。"),
        ("バリューデザイン", "ペイクラウドグループのキャッシュレスサービス中核会社です。独自Pay、株主優待電子化、ギフト関連を担います。"),
        ("キャッシュレスサービス", "独自Pay、電子マネー、ポイント、ギフトなど、決済・販促をデジタル化する事業です。"),
        ("デジタルサイネージ", "店舗や施設の電子看板・広告配信システムです。導入や納品時期で売上が振れます。"),
        ("ソリューション事業", "システム開発やデジタル施策支援です。顧客のDX需要を取り込みます。"),
        ("調整後EBITDA", "営業利益に減価償却などを足し戻した収益力の目安です。3Q累計は10.56億円でした。"),
        ("月次業績報告", "会社が毎月開示する取扱高や事業KPIの確認資料です。短期の勢いを見る材料になります。"),
        ("株主優待電子化", "紙の優待券をデジタル化するサービスです。外食・小売などで導入余地があります。"),
        ("自己株式取得", "会社が自社株を買う施策です。需給と1株価値にプラスになり得ます。"),
        ("東証グロース", "成長企業向け市場です。小型株が多く、流動性や値動きには注意が必要です。"),
        ("進捗率", "通期予想に対してどこまで達成したかを見る指標です。3Q売上進捗は70.0%でした。"),
        ("PER", "株価が1株利益の何倍かを見る指標です。成長期待が高いとPERは高くなりやすいです。"),
    ]
    return {
        "TICKER": TICKER,
        "COMPANY_NAME": COMPANY,
        "INDUSTRY": "キャッシュレス決済・デジタルサイネージ",
        "DATE": DATE,
        "TAGLINE": "独自Pay、デジタルギフト、株主優待電子化、デジタルサイネージを展開するキャッシュレス・DX支援企業です。",
        "HERO_TAGS": '<span class="hero-tag">日本株</span><span class="hero-tag">独自Pay</span><span class="hero-tag">キャッシュレス決済</span><span class="hero-tag">東証グロース</span>',
        "HERO_STATS": (
            f'<div class="stat"><div class="stat-value">{yen(P0)}</div><div class="stat-label">評価基準株価</div><div class="stat-note">2026/07/30終値</div></div>'
            f'<div class="stat"><div class="stat-value">{MARKET_CAP_BN:.1f}億円</div><div class="stat-label">時価総額の目安</div><div class="stat-note">約1,596万株で計算</div></div>'
            '<div class="stat"><div class="stat-value up">80.57億円</div><div class="stat-label">2026年8月期3Q売上</div><div class="stat-note">前年同期比+5.4%</div></div>'
            '<div class="stat"><div class="stat-value">10.56億円</div><div class="stat-label">3Q調整後EBITDA</div><div class="stat-note">進捗率81.2%</div></div>'
        ),
        "SEC2_LABEL": "事業モデル",
        "SEC3_LABEL": "独自Pay",
        "SEC4_LABEL": "サイネージ",
        "SEC5_LABEL": "競合比較",
        "SEC1_TLDR": li("独自Pay、株主優待電子化、デジタルサイネージを展開する小型グロース株です。", "*") + li("2026年8月期3Qは売上80.57億円、営業利益6.61億円で増収増益でした。", "*") + li("通期予想への進捗は順調ですが、成長率・小型株の流動性・納品時期には注意です。", "!"),
        "SEC1_FACTS": (
            "<div><dt>正式社名</dt><dd>ペイクラウドホールディングス</dd></div><div><dt>本社</dt><dd>東京都港区南青山</dd></div>"
            "<div><dt>上場</dt><dd>東証グロース（4015）</dd></div><div><dt>決算期</dt><dd>8月</dd></div>"
            "<div><dt>主な子会社</dt><dd>バリューデザイン</dd></div><div><dt>事業</dt><dd>キャッシュレス / サイネージ / ソリューション</dd></div>"
        ),
        "SEC1_CARDS": (
            '<div class="card-sm"><span class="card-emoji">💳</span><div class="card-title">何をしている</div><div class="card-desc">店舗・企業向けに独自Payやデジタルギフトを提供します。</div></div>'
            '<div class="card-sm"><span class="card-emoji">🎫</span><div class="card-title">注目サービス</div><div class="card-desc">株主優待券の電子化支援が外食・小売向けに広がっています。</div></div>'
            '<div class="card-sm"><span class="card-emoji">📺</span><div class="card-title">もう一つの柱</div><div class="card-desc">デジタルサイネージ関連事業も売上を作ります。</div></div>'
            '<div class="card-sm"><span class="card-emoji">📈</span><div class="card-title">直近業績</div><div class="card-desc">3Q累計で売上80.57億円、営業利益6.61億円です。</div></div>'
        ),
        "SEC1_BIZMODEL": (
            '<li><span class="kp-emoji">💳</span><span class="kp-text"><b>キャッシュレス</b>：独自Pay、ポイント、デジタルギフトで店舗の販促と決済を支援します。</span></li>'
            '<li><span class="kp-emoji">📺</span><span class="kp-text"><b>サイネージ</b>：電子看板・広告配信などの導入で売上を作ります。</span></li>'
            '<li><span class="kp-emoji">🧩</span><span class="kp-text"><b>ソリューション</b>：顧客ごとのシステム開発やDX支援を行います。</span></li>'
        ),
        "SEC1_HIGHLIGHT": '<div class="highlight"><h3>ペイクラウドを見る基本ルール</h3><p>独自Payと株主優待電子化は継続成長のテーマです。一方で、サイネージの納品時期や小型株の流動性により、四半期ごとの見え方は変わりやすいです。</p></div>',
        "SEC2_ICON": "💳",
        "SEC2_TITLE": "事業モデルの<span class=\"g\">基本</span>",
        "SEC2_SUB": "決済・販促・店舗DXをまとめて見る",
        "SEC2_TLDR": li("キャッシュレスサービスが成長の中心です。", "*") + li("デジタルサイネージは納品タイミングで売上が振れます。", "*") + li("ソリューション事業は顧客DX需要を拾います。", "*"),
        "SEC2_CONTENT": (
            '<p class="lead">ペイクラウドは、企業や店舗のキャッシュレス化、販促、デジタル表示、株主優待電子化を支援します。単なる決済会社ではなく、店舗と顧客をつなぐデジタル基盤を提供する会社です。</p>'
            '<div class="sowhat"><p><b>つまり</b>、4015は「決済回数」だけでなく「導入企業数」「ギフト・優待電子化」「サイネージ納品」を見る銘柄です。</p></div>'
            '<div class="term-list">'
            + details("キャッシュレスサービス", "独自Pay、電子マネー、ポイント、デジタルギフトを提供します。小売、外食、自治体、イベントなどに導入余地があります。", True)
            + details("デジタルサイネージ", "店舗や施設に設置する電子看板です。導入案件の納品時期で四半期売上が変わることがあります。")
            + details("株主優待電子化", "紙の優待券をデジタル化します。一風堂を中心に展開する力の源HDなどの支援事例が出ています。")
            + details("月次開示", "毎月の業績報告が出るため、決算前に事業の勢いを確認しやすい点があります。")
            + "</div>"
        ),
        "SEC3_TITLE": "独自Payと<span class=\"g\">優待電子化</span>",
        "SEC3_SUB": "店舗・外食・小売のDX需要を拾う",
        "SEC3_TLDR": li("独自Payは企業ブランドで使える決済・販促基盤です。", "*") + li("株主優待電子化は紙券の管理コストを下げるテーマです。", "*") + li("導入社数、取扱高、継続率が重要です。", "!"),
        "SEC3_CONTENT": (
            '<div class="product-grid"><div class="product-box"><div class="product-symbol">PAY</div><div class="product-name">独自Pay</div><div class="product-use">自社ブランドの電子マネー・ポイント。</div></div>'
            '<div class="product-box"><div class="product-symbol">GIFT</div><div class="product-name">デジタルギフト</div><div class="product-use">販促・優待・キャンペーンに利用。</div></div>'
            '<div class="product-box"><div class="product-symbol">DX</div><div class="product-name">優待電子化</div><div class="product-use">紙券からデジタルへ移行。</div></div></div>'
            '<div class="term-list">'
            + details("独自Payの強み", "顧客企業が自社ブランドで決済やポイントを運用でき、店舗と顧客の接点を増やせます。", True)
            + details("株主優待電子化", "優待券の発送、利用、管理をデジタル化します。外食・小売で導入余地があります。")
            + details("おまいりPay", "寺院・神社専用キャッシュレス決済の提供など、用途特化型の展開もあります。")
            + details("確認指標", "導入件数、利用額、月次業績、解約率、粗利率を見ます。")
            + "</div>"
        ),
        "SEC4_TITLE": "サイネージと<span class=\"g\">業績の振れ</span>",
        "SEC4_SUB": "納品タイミングが四半期を動かす",
        "SEC4_TLDR": li("サイネージは大型案件の納品時期で売上が動きます。", "*") + li("1Hの遅れは3Qで回復したと会社側は説明しています。", "*") + li("通期達成には4Qの納品と月次推移が重要です。", "!"),
        "SEC4_CONTENT": (
            '<ul class="keypoints"><li><span class="kp-emoji">📺</span><span class="kp-text"><b>納品型売上</b>：サイネージは案件納品の時期で四半期売上が振れます。</span></li>'
            '<li><span class="kp-emoji">📈</span><span class="kp-text"><b>3Q回復</b>：会社説明では、上期の遅れを3Qで取り戻したとされています。</span></li>'
            '<li><span class="kp-emoji">🗓️</span><span class="kp-text"><b>月次確認</b>：月次業績報告で、期末へ向けた勢いを確認します。</span></li></ul>'
            '<div class="sowhat"><p><b>つまり</b>、四半期だけで判断せず、月次と納品時期を合わせて見る必要があります。</p></div>'
        ),
        "SEC5_TITLE": "競合と<span class=\"g\">比べる</span>",
        "SEC5_SUB": "決済・販促DXの小型株として見る",
        "SEC5_TLDR": li("比較対象は決済、ポイント、販促DX、サイネージ関連企業です。", "*") + li("独自Payと優待電子化の組み合わせが特徴です。", "*") + li("大手決済会社に比べると規模と流動性は小さいです。", "!"),
        "SEC5_CONTENT": (
            '<div class="table-wrap"><table class="compare-table"><thead><tr><th>企業群</th><th>主な強み</th><th>注意点</th></tr></thead><tbody>'
            '<tr><td class="me">ペイクラウド</td><td>独自Pay、デジタルギフト、優待電子化、サイネージ。</td><td>小型株、納品時期、成長率の振れ。</td></tr>'
            '<tr><td>大手決済会社</td><td>加盟店網、資本力、決済量。</td><td>汎用決済中心で、独自Pay特化とは違う。</td></tr>'
            '<tr><td>販促DX企業</td><td>CRM、ポイント、キャンペーン運用。</td><td>決済基盤を自前で持つかは企業ごとに違う。</td></tr>'
            '<tr><td>サイネージ企業</td><td>広告・店舗表示システム。</td><td>案件型売上で時期が振れやすい。</td></tr>'
            '</tbody></table></div><div class="highlight"><h3>差別化の見方</h3><p>ペイクラウドは、決済、ギフト、株主優待、サイネージを横断できる点が特徴です。小型株なので、導入事例と月次KPIが評価を左右しやすいです。</p></div>'
        ),
        "SEC6_TLDR": li("独自Pay、調整後EBITDA、月次、納品時期を押さえると読みやすいです。", "*") + li("優待電子化は分かりやすい成長テーマです。", "*") + li("小型株の流動性リスクは忘れないことが大事です。", "!"),
        "SEC6_CONTENT": '<div class="term-list">' + "".join(details(name, body) for name, body in terms) + "</div>",
        "SEC7_TLDR": li("4Q決算、月次業績、自社株取得終了、株主優待が主な材料です。", "*") + li("3Qで上期遅れを回復した点は追い風です。", "*") + li("通期達成度と来期成長率が次の焦点です。", "!"),
        "SEC7_CONTENT": (
            '<div class="timeline"><div class="tl-row"><div class="tl-date">2026/07/14</div><div class="tl-title">3Q決算 <span class="signal bull">追い風</span></div><div class="tl-desc">売上80.57億円、営業利益6.61億円。増収増益で上期遅れを回復。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/07/28</div><div class="tl-title">6月月次・自己株式取得終了 <span class="signal neutral">確認</span></div><div class="tl-desc">月次の勢いと資本政策の進捗を確認します。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/10ごろ</div><div class="tl-title">通期決算 <span class="signal bull">重要</span></div><div class="tl-desc">通期予想の達成度と来期見通しが次の大きな材料です。</div></div></div>'
            '<div class="info-row"><div class="info-box info-box-green"><div class="info-title info-title-green">追い風</div><div class="info-text">3Q売上・営業利益の過去最高、月次開示、優待電子化テーマ。</div></div>'
            '<div class="info-box info-box-amber"><div class="info-title info-title-amber">確認</div><div class="info-text">4Q納品、通期予想達成、来期成長率、自己株式取得後の需給。</div></div>'
            '<div class="info-box info-box-red"><div class="info-title info-title-red">リスク</div><div class="info-text">小型株の流動性、納品期ズレ、成長鈍化、無配。</div></div></div>'
            + source_details
        ),
    }


def scenario_values() -> dict[str, str]:
    bear, base, bull = 407, 543, 679
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
        "EXCHANGE": "東京証券取引所グロース市場",
        "VALUATION_DATE": DATE,
        "METHOD": "小型成長株向けPER・EV/EBITDAシナリオ",
        "VERDICT_STATUS": "標準ケース付近の中立圏",
        "VERDICT_LINE_1": "評価基準株価は悲観〜楽観レンジの48.9%地点です。3Qの回復は評価できますが、通期達成と来期成長率の確認が必要です。",
        "VERDICT_LINE_2": "この試算は2026年8月8日時点の公開情報で固定しています。株価は2026年7月30日の終値540円を基準にしています。",
        "SCORE": str(score),
        "CURRENT_PRICE": yen(P0),
        "CURRENT_PRICE_NOTE": "2026/07/30 15:30",
        "BASE_PRICE": yen(base),
        "BASE_DELTA": "+0.6%",
        "EXPECTED_VALUE": yen(expected),
        "EXPECTED_DELTA": "+0.6%",
        "RISK_CLASS": "中〜高",
        "RISK_NOTE": "小型株、納品時期、成長率の振れ",
        "WARN_BAND": '<div class="wrap"><div class="notice" style="margin-top:14px"><b>注意：</b>3Qは順調ですが、通期達成と来期見通しは未確定です。小型株のため出来高と需給にも注意してください。</div></div>',
        "SNAPSHOT_LEAD": "今の株価は、3Qの好決算をある程度評価し、標準ケース付近にいます。さらに上を見るには、4Qと来期見通しの強さが必要です。",
        "BAND_POSITION": f"{band:.1f}%",
        "ZONE_JUDGE": "標準ケース近辺",
        "ZONE_NOTE": "通期達成と来期増益が見えれば標準〜楽観側へ寄ります。",
        "BEAR_PRICE": yen(bear),
        "BULL_PRICE": yen(bull),
        "ENDPOINT_RR": f"{endpoint_rr:.1f}倍",
        "MARKET_SCORE": str(round(band)),
        "OWN_SCORE": str(round(own_score)),
        "MARKET_REVERSE_NOTE": "このモデルで逆算すると、今の株価は会社予想EPSに対してPER24倍前後、または調整後EBITDAの成長継続を織り込む水準です。市場全体の予想ではなく、このモデル上の逆算です。",
        "SCENARIOS_LEAD": "現在株価から独立して、通期営業利益、EPS、調整後EBITDA、来期成長率を置きました。小型株なのでPERとEV/EBITDAの両方を参考にします。",
        "BEAR_PROB": "25%",
        "BASE_PROB": "50%",
        "BULL_PROB": "25%",
        "BEAR_DELTA": "-24.6%",
        "BULL_DELTA": "+25.7%",
        "BEAR_DL_ROWS": dl([("EPS", "19円"), ("PER", "21.4倍"), ("前提", "4Q弱含み"), ("営業利益", "7.0億円")]),
        "BASE_DL_ROWS": dl([("EPS", "22.6円"), ("PER", "24.0倍"), ("前提", "通期計画達成"), ("営業利益", "8.0億円")]),
        "BULL_DL_ROWS": dl([("EPS", "27円"), ("PER", "25.1倍"), ("前提", "来期成長加速"), ("営業利益", "9億円超")]),
        "PRICE_ZONE_ROWS": '<div class="zone"><div><b>407円未満</b><span>★★★★</span></div><p>悲観ケース以下。通期未達や成長鈍化をかなり織り込む価格帯です。</p></div><div class="zone"><div><b>407〜543円</b><span>★★★</span></div><p>標準ケース手前。今の株価はこの範囲です。</p></div><div class="zone"><div><b>543〜679円</b><span>★★</span></div><p>通期達成と来期成長を評価する価格帯です。</p></div><div class="zone"><div><b>679円超</b><span>★</span></div><p>楽観ケース超。強い来期見通しや成長率拡大が必要です。</p></div>',
        "SIGNAL_ROWS": '<div class="signal"><div><b>3Q増収増益</b><span class="up">追い風</span></div><p>売上80.57億円、営業利益6.61億円でした。</p></div><div class="signal"><div><b>調整後EBITDA進捗</b><span class="up">追い風</span></div><p>3Q累計10.56億円、進捗率81.2%です。</p></div><div class="signal"><div><b>4Q納品</b><span class="flat">確認</span></div><p>サイネージなどの納品時期を確認します。</p></div><div class="signal"><div><b>小型株需給</b><span class="down">注意</span></div><p>出来高が薄い局面では値動きが大きくなります。</p></div>',
        "POSITIVES": "<li>2026年8月期3Qは売上80.57億円、営業利益6.61億円で増収増益でした。</li><li>調整後EBITDAは10.56億円、通期予想に対する進捗率は81.2%です。</li><li>独自Pay、株主優待電子化、月次開示という分かりやすい成長材料があります。</li><li>自己株式取得終了など、資本政策面の材料もあります。</li>",
        "CONCERNS": "<li>売上進捗率は70.0%で、4Qの納品と伸びが重要です。</li><li>デジタルサイネージは納品時期で四半期業績が振れます。</li><li>小型株で出来高が限られ、需給による値動きが大きくなりやすいです。</li><li>期末配当予想は0円で、株主還元は優待と自社株取得が中心です。</li>",
        "FORMULA": "主計算はPERです。補助的にEV/EBITDAを見ます。通期会社予想と3Q進捗をもとに、悲観・標準・楽観を置きました。",
        "CALC_TABLE_HEAD": th("ケース", "EPS", "PER", "計算株価", "確率", "確率加重"),
        "CALC_TABLE_ROWS": tr("悲観", "19円", "21.4倍", yen(bear), "25%", "102円") + tr("標準", "22.6円", "24.0倍", yen(base), "50%", "272円") + tr("楽観", "27円", "25.1倍", yen(bull), "25%", "170円"),
        "CALC_NOTICE": "現在株価に合わせて標準ケースを置いていません。通期会社計画、3Q進捗、月次、納品時期を踏まえた条件付き試算です。",
        "CONDITIONS": details("悲観ケース：407円 / 確率25%", "4Qが弱く、来期成長率への期待も下がるケースです。", True) + details("標準ケース：543円 / 確率50%", "通期計画をおおむね達成し、来期も緩やかな成長が続くケースです。") + details("楽観ケース：679円 / 確率25%", "独自Payと優待電子化の導入が進み、来期成長率と倍率が上がるケースです。"),
        "SENSITIVITY_HEAD": th("前提", "弱い", "標準", "強い"),
        "SENSITIVITY_ROWS": tr("EPS", "20円 → 480円", "22.6円 → 543円", "25円 → 600円") + tr("PER", "20倍 → 452円", "24倍 → 543円", "28倍 → 633円"),
        "SENSITIVITY_NOTE": "1変数だけを動かした簡易感応度です。実際にはEPSとPERが同時に動きます。",
        "DIST_LEAD": "モンテカルロではなく、悲観・標準・楽観の3点分布です。",
        "DIST_ROWS": '<div class="dist-row"><span>407円</span><div class="track"><i style="width:25%"></i></div><b>25%</b></div><div class="dist-row"><span>543円</span><div class="track"><i style="width:50%"></i></div><b>50%</b></div><div class="dist-row"><span>679円</span><div class="track"><i style="width:25%"></i></div><b>25%</b></div>',
        "DIST_SUMMARY": "中心は標準ケースです。小型株なので、決算と月次の受け止めで上下へ振れやすいです。",
        "WATCH_ROWS": '<div class="signal"><div><b>2026年8月期通期決算</b></div><p>売上115億円、営業利益8億円の達成度を確認します。</p></div><div class="signal"><div><b>月次業績報告</b></div><p>独自Payや事業KPIの勢いを確認します。</p></div><div class="signal"><div><b>優待電子化の導入事例</b></div><p>外食・小売での導入拡大を確認します。</p></div>',
        "ASSUMPTIONS_ROWS": tr("評価基準株価", yen(P0), "市場データで確認済み", "2026/07/30終値") + tr("3Q売上", "80.57億円", "公開情報で確認済み", "2026/07/14") + tr("3Q営業利益", "6.61億円", "公開情報で確認済み", "2026/07/14") + tr("通期会社予想", "売上115億円、営業利益8億円", "会社の目標・予定", "2026年8月期"),
        "DEEPDIVE_DETAILS": details("手法選定理由", "ペイクラウドは黒字の小型成長株です。PERを主に使い、調整後EBITDAを補助的に見ます。", True) + details("株価基準について", "評価基準株価は2026年7月30日終値540円を使っています。流動性が低い小型株のため、直近値は変動しやすい点に注意してください。") + details("主要出典", f'{source_link("公式IR", "ir")}、{source_link("3Q決算情報", "q3_summary")}、{source_link("Yahoo!ファイナンス決算要約", "yahoo_financials")}、{source_link("株価時系列", "price")}。<br><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>'),
        "DISCLAIMER": "本資料は情報提供を目的とした試算です。投資助言ではありません。小型成長株は業績、流動性、需給、開示内容により大きく変動します。",
        "FOOTER_NOTE": f"SiM MARKET LAB｜{COMPANY}（{TICKER}）株価シナリオ｜作成日 {DATE}",
    }


def catalyst_values() -> dict[str, str]:
    non_quant = '<div class="priced"><div class="priced-head"><span>主要材料の推定織り込み</span><b>46%</b></div><p>仮定：4Q決算の標準達成を50%、月次KPI改善を45%、優待電子化の導入拡大を40%、自社株取得後の需給改善を55%として置き、重複を控除しました。</p><p>読み方：3Q進捗は一部評価済みですが、通期決算と来期見通しがまだ残っているため、織り込みは半分弱です。</p><p>次に見る数字：通期売上、営業利益、調整後EBITDA、月次推移です。</p><p>再計算方法：EPS、PER、調整後EBITDA、株式数を分け、株価シナリオと同じモデルで更新します。</p></div>'
    outcome_common = "<ul><li>目安：下の％は、この結果が出た後に市場が材料を評価し直した場合の上昇・下落幅です。</li><li>実際の値動きは地合い、直前の株価上昇、同時ニュースで変わります。</li></ul>"
    impact_map = {
        "2026年8月期通期決算": ("+12〜28%", "-5〜+8%", "-14〜-28%", "小型成長株では通期実績と来期見通しがPERを直接動かすため、最も大きいレンジです。"),
        "月次業績報告": ("+6〜16%", "-3〜+5%", "-8〜-18%", "毎月出る継続材料なので単発決算より小さい一方、トレンド変化には効きます。"),
        "株主優待電子化の導入拡大": ("+8〜20%", "-4〜+7%", "-8〜-16%", "導入事例は成長テーマを補強しますが、売上寄与の確認まで時間差があるため中程度です。"),
        "自己株式取得終了後の需給": ("+3〜10%", "-3〜+4%", "-6〜-14%", "需給材料であり事業価値を直接変えないため、他の事業材料より小さくしています。"),
    }
    description_map = {
        "2026年8月期通期決算": "通期決算は、3Qまでの好調が最後まで続いたか、来期も成長できるかを確認する最大材料です。売上、営業利益、調整後EBITDA、来期見通しがそろって強いほど評価されやすくなります。",
        "月次業績報告": "月次業績報告は、決算前に事業の勢いを確認できる継続材料です。独自Payや関連サービスの伸びが続けば、通期決算や来期見通しへの期待が高まります。",
        "株主優待電子化の導入拡大": "株主優待電子化は、同社のデジタルギフトや独自Payの用途が広がるかを見る材料です。導入企業が増えるほど、単発案件ではなく継続収益のテーマとして評価されます。",
        "自己株式取得終了後の需給": "自社株買い終了後の需給は、買い支えがなくなった後でも業績期待で株価を保てるかを見る材料です。事業価値を直接変えるものではないため、決算材料より影響は小さめです。",
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
<div class="evidence"><div><h4>根拠</h4><ul>{evidence}</ul></div><div><h4>反証・先行指標</h4><ul><li>月次の鈍化</li><li>サイネージ納品の遅れ</li><li>通期予想未達</li></ul></div></div>
</article>'''

    cards = [
        card("2026年8月期通期決算", "2026/10ごろ", '<span class="chip">重要度5</span><span class="chip blue">時期推定</span>', '<span>通期実績</span><i>→</i><span>EPS</span><i>→</i><span>PER</span>', "売上115億円・営業利益8億円を上回り、来期見通しも強い状態です。", "通期計画近辺で、来期見通しは慎重な状態です。", "4Qが弱く、通期未達または来期成長率が低い状態です。", "<li>3Q売上進捗70.0%、調整後EBITDA進捗81.2%と公表。</li><li>通期予想は売上115億円、営業利益8億円です。</li>"),
        card("月次業績報告", "毎月", '<span class="chip">重要度4</span><span class="chip">継続材料</span>', '<span>月次KPI</span><i>→</i><span>成長率</span><i>→</i><span>倍率</span>', "独自Payや関連KPIが加速し、4Q・来期の期待が上がる状態です。", "月次は安定推移し、決算確認待ちの状態です。", "月次が鈍化し、成長期待が下がる状態です。", "<li>会社は月次業績報告を継続開示しています。</li><li>2026年6月月次も7月28日に開示されています。</li>"),
        card("株主優待電子化の導入拡大", "2026年後半", '<span class="chip">重要度4</span><span class="chip">導入事例</span>', '<span>導入社数</span><i>→</i><span>利用額</span><i>→</i><span>継続収益</span>', "外食・小売で導入事例が増え、独自Payの用途が広がる状態です。", "導入事例は出るが、売上寄与は段階的な状態です。", "導入拡大が限定的で、テーマ先行と見られる状態です。", "<li>力の源HDの株主優待券電子化支援が開示されています。</li><li>自社の株主優待も独自Pay導入顧客のデジタルギフトを活用します。</li>"),
        card("自己株式取得終了後の需給", "2026/07/28以降", '<span class="chip amber">重要度3</span><span class="chip">終了済み</span>', '<span>買付終了</span><i>→</i><span>需給</span><i>→</i><span>株価</span>', "買付終了後も業績評価で株価が保たれ、流動性も改善する状態です。", "自社株買い終了の需給影響は限定的な状態です。", "買い支え終了が意識され、出来高減少とともに下がる状態です。", "<li>2026年7月28日に自己株式取得状況および取得終了が開示されています。</li><li>小型株では需給材料として確認が必要です。</li>"),
    ]
    return {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "東京証券取引所グロース市場",
        "VALUATION_DATE": DATE,
        "LAST_UPDATED": DATE,
        "REPORT_STATUS": "重要材料が複数",
        "SUMMARY_LINE_1": "通期決算、月次、優待電子化、自社株買い終了後の需給が今後の主な材料です。",
        "SUMMARY_LINE_2": "足りない情報は仮定を置き、主要材料の織り込み度を46%と推定します。",
        "OVERALL_PRICED_IN": "46%",
        "OVERALL_PRICED_LABEL": "主要材料の推定織り込み",
        "PRICED_IN_CONFIDENCE": "ふつう",
        "CURRENT_PRICE": yen(P0),
        "CURRENT_PRICE_NOTE": "2026/07/30 15:30",
        "NEXT_CATALYST_TITLE": "2026年8月期通期決算",
        "NEXT_CATALYST_WINDOW": "2026年10月ごろ",
        "DATE_CONFIDENCE": "当方推定",
        "CATALYST_COUNT": "4件",
        "WARN_BAND": "",
        "NO_CATALYST_NOTICE": "",
        "OVERALL_PRICED_BLOCK": non_quant,
        "PRICED_IN_METHOD": "未確定情報に仮定確率を置き、4Q決算、月次KPI、優待電子化、自社株取得後の需給を標準ケース価値へ重み付けして推定。",
        "SURPRISE_UP": "通期上振れ、強い来期見通し、月次加速、優待電子化の導入拡大です。",
        "SURPRISE_DOWN": "4Q失速、通期未達、来期成長鈍化、自社株買い終了後の需給悪化です。",
        "PRIMARY_RISK": "3Qの好調が株価に入った後で、4Qや来期見通しが普通だと失望される可能性です。",
        "TIMELINE_ROWS": '<div class="time-row"><div class="time-date">毎月</div><div class="time-dot"></div><div class="time-body"><b>月次業績報告</b><p>独自Payや事業KPIの勢いを確認します。</p><div class="time-meta"><span class="chip">継続材料</span></div></div></div><div class="time-row"><div class="time-date">2026/07/28</div><div class="time-dot"></div><div class="time-body"><b>自己株式取得終了</b><p>買付終了後の需給を確認します。</p><div class="time-meta"><span class="chip">開示済み</span></div></div></div><div class="time-row"><div class="time-date">2026/10ごろ</div><div class="time-dot"></div><div class="time-body"><b>通期決算</b><p>通期予想の達成度と来期見通しを確認します。</p><div class="time-meta"><span class="chip blue">時期推定</span></div></div></div>',
        "CATALYST_CARDS": "".join(cards),
        "DEPENDENCY_ROWS": '<div class="signal"><div><b>月次と通期決算</b><span class="up">連動</span></div><p>月次が強いほど通期達成と来期見通しを支えます。</p></div><div class="signal"><div><b>優待電子化と独自Pay</b><span class="up">同じ経路</span></div><p>導入事例は独自Pay利用拡大の一部として見ます。</p></div><div class="signal"><div><b>自社株買いと需給</b><span class="flat">確認</span></div><p>終了後は業績評価で株価を保てるかを見ます。</p></div>',
        "WATCH_ROWS": '<div class="signal"><div><b>売上進捗</b><span class="up">最重要</span></div><p>通期115億円に対する4Q達成度を確認します。</p></div><div class="signal"><div><b>営業利益率</b><span class="up">重要</span></div><p>売上成長が利益へ変わっているかを見ます。</p></div><div class="signal"><div><b>月次KPI</b><span class="flat">確認</span></div><p>決算前の勢いを確認します。</p></div><div class="signal"><div><b>出来高</b><span class="down">注意</span></div><p>小型株なので需給の荒れを確認します。</p></div>',
        "ASSUMPTION_ROWS": tr("評価基準株価", yen(P0), "市場データで確認済み", DATE, "2026/07/30終値") + tr("3Q売上", "80.57億円", "公開情報で確認済み", "2026/07/14", "進捗率70.0%") + tr("3Q営業利益", "6.61億円", "公開情報で確認済み", "2026/07/14", "前年同期比+6.2%") + tr("調整後EBITDA", "10.56億円", "公開情報で確認済み", "2026/07/14", "進捗率81.2%"),
        "SOURCE_DETAILS": f'<ul><li>{source_link("公式IR", "ir")}</li><li>{source_link("3Q決算情報", "q3_summary")}</li><li>{source_link("適時開示一覧", "disclosure")}</li><li>{source_link("3Q説明動画", "movie")}</li><li>{source_link("株主優待", "benefit")}</li></ul><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p>',
        "VALIDATION_DETAILS": "<p>PASS：3Q決算、通期予想、月次開示、自己株式取得終了、株主優待関連を確認。WARN：通期決算日は当方推定のため確定日として扱っていません。</p>",
        "UPDATE_HISTORY": f"<p>{DATE}：初版作成。3Q決算、月次、自己株式取得終了、株主優待電子化テーマを反映。</p>",
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
        "id": "paycloud-4015",
        "order": 4,
        "ticker": "4015",
        "quoteSymbol": "4015.T",
        "name": "ペイクラウドホールディングス",
        "nameEn": "Paycloud Holdings Inc.",
        "market": "JP",
        "marketLabel": "日本株",
        "exchange": "東京証券取引所グロース市場",
        "currency": "JPY",
        "sector": "キャッシュレス決済・デジタルサイネージ",
        "reports": {
            "company": {"path": "./stocks/paycloud-4015/company.html", "available": True},
            "valuation": {"path": "./stocks/paycloud-4015/valuation.html", "available": True},
            "catalysts": {"path": "./stocks/paycloud-4015/catalysts.html", "available": True},
        },
    }
    stocks_payload["stocks"] = [item for item in stocks_payload["stocks"] if item["id"] != "paycloud-4015"]
    stocks_payload["stocks"].append(stock)
    stocks_path.write_text(json.dumps(stocks_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    prices_path = ROOT / "data" / "prices.json"
    prices_payload = json.loads(prices_path.read_text(encoding="utf-8"))
    prices_payload.setdefault("prices", {})["paycloud-4015"] = {
        "symbol": "4015.T",
        "price": P0,
        "previousClose": PREVIOUS_CLOSE,
        "change": P0 - PREVIOUS_CLOSE,
        "changePct": 0.0,
        "currency": "JPY",
        "marketTime": "2026-07-30T06:30:00+00:00",
        "updatedAt": "2026-08-08T13:00:00+00:00",
        "status": "ok",
    }
    prices_payload["quoteCount"] = len(prices_payload["prices"])
    prices_path.write_text(json.dumps(prices_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    signals_path = ROOT / "data" / "signals.json"
    signals_payload = json.loads(signals_path.read_text(encoding="utf-8"))
    signals_payload["updatedAt"] = datetime.now(timezone.utc).isoformat()
    signals_payload.setdefault("signals", {})["paycloud-4015"] = {
        "position": 53.9,
        "zone": "中立",
        "asOf": DATE,
        "components": {
            "valuation": 48.9,
            "catalysts": 66.0,
            "businessRisk": 54.0,
        },
        "reportRevision": "paycloud-4015-2026-08-08",
        "summary": "3Q増収増益と調整後EBITDA進捗は強い一方、現在株価は標準ケース付近で、通期決算と来期見通し確認前のため中立。",
    }
    signals_path.write_text(json.dumps(signals_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_reports()
    upsert_site_data()


if __name__ == "__main__":
    main()
