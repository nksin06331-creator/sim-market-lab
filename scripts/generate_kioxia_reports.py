"""Generate Kioxia report HTML files from the bundled SiM templates."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATERIALS = ROOT.parent / "report-generation-materials"
OUT_DIR = ROOT / "stocks" / "kioxia-285a"

COMPANY = "キオクシアホールディングス"
TICKER = "285A"
DATE = "2026-09-30"
P0 = 18345
N0_M = 1656.6
MARKET_CAP_TN = round(P0 * N0_M / 1_000_000, 1)

SOURCES = {
    "q1": "https://ssl4.eir-parts.net/doc/285A/tdnet/2859908/00.pdf",
    "annual": "https://www.kioxia-holdings.com/content/dam/kioxia-hd/en-jp/ir/library/securities/asset/Annual-Securities-Report-FY2025-EN.pdf",
    "investor_day": "https://www.kioxia-holdings.com/ja-jp/news/2026/20260602-1.html",
    "bics10": "https://apac.kioxia.com/en-apac/about/news/2026/20260703-1.html",
    "split": "https://ssl4.eir-parts.net/doc/285A/tdnet/2859912/00.pdf",
    "buyback": "https://ssl4.eir-parts.net/doc/285A/tdnet/2859923/00.pdf",
    "lawsuit": "https://ssl4.eir-parts.net/doc/285A/tdnet/2861255/00.pdf",
}


def yen(value: int | float) -> str:
    return f"{int(round(value)):,}円"


def tr(*cells: str) -> str:
    return "<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>"


def th(*cells: str) -> str:
    return "".join(f"<th>{cell}</th>" for cell in cells)


def dl(rows: list[tuple[str, str]]) -> str:
    return "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in rows)


def li(text: str, emoji: str = "•") -> str:
    return f'<li data-emoji="{emoji}">{text}</li>'


def details(title: str, body: str, open_: bool = False) -> str:
    return f"<details{' open' if open_ else ''}><summary>{title}</summary><p>{body}</p></details>"


def source_link(label: str, key: str) -> str:
    return f'<a href="{SOURCES[key]}" target="_blank" rel="noopener noreferrer">{label}</a>'


def strip_comments(html: str) -> str:
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
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
        f'{source_link("2026年3月期 有価証券報告書", "annual")}、'
        f'{source_link("2027年3月期1Q決算短信", "q1")}、'
        f'{source_link("Investor Day 2026", "investor_day")}、'
        f'{source_link("第10世代BiCS FLASHサンプル出荷", "bics10")}を確認しました。'
        "本文の数値は2026年9月30日時点の公開情報に基づきます。"
        '</p><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p></div></details>'
    )
    terms = [
        ("NANDフラッシュ", "電源を切ってもデータが残るメモリです。スマホ、SSD、データセンターで使われます。キオクシアの主力製品です。"),
        ("SSD", "半導体メモリで作る記憶装置です。HDDより高速です。キオクシアではPC、データセンター、企業向けが中心です。"),
        ("BiCS FLASH", "キオクシアの3次元フラッシュ技術のブランドです。層を積み重ねて容量を増やします。第10世代は332層を使います。"),
        ("TLC / QLC", "1つのセルに何ビット保存するかの方式です。TLCは性能と耐久のバランス、QLCは大容量向けです。"),
        ("ASP", "平均販売単価です。メモリ市況が強いと上がりやすく、利益を大きく動かします。"),
        ("ビット出荷", "売ったメモリ容量の量です。価格だけでなく数量面の需要を見る指標です。"),
        ("データセンター", "AIやクラウドを動かす大型設備です。高容量SSDへの需要が増えています。"),
        ("KVキャッシュ", "AI推論で過去の計算結果を保存するデータです。高速・大容量SSDの用途になり得ます。"),
        ("LTA", "複数年の売買契約です。市況変動が激しいメモリ事業で売上の見通しを安定させる狙いがあります。"),
        ("設備投資", "工場や製造装置への投資です。成長に必要ですが、需要が弱い時は固定費負担になります。"),
        ("為替感応度", "円安なら円建て売上・利益に追い風になりやすい性質です。逆に円高は注意点です。"),
        ("株式分割", "1株を複数株に分けることです。キオクシアは1対3の株式分割を実施し、2026年9月29日から分割後の株価で取引されています。"),
    ]
    return {
        "TICKER": TICKER,
        "COMPANY_NAME": COMPANY,
        "INDUSTRY": "半導体・フラッシュメモリ",
        "DATE": DATE,
        "TAGLINE": "NANDフラッシュメモリとSSDを開発・製造・販売する半導体会社です。AIデータセンター向け需要の強さが、売上と利益を大きく動かしています。",
        "HERO_TAGS": '<span class="hero-tag">NANDフラッシュ</span><span class="hero-tag">SSD</span><span class="hero-tag">AIデータセンター</span><span class="hero-tag">東証プライム</span>',
        "HERO_STATS": (
            f'<div class="stat"><div class="stat-value">{yen(P0)}</div><div class="stat-label">評価基準株価</div><div class="stat-note">2026/09/30 10時台</div></div>'
            f'<div class="stat"><div class="stat-value">{MARKET_CAP_TN}兆円</div><div class="stat-label">時価総額の目安</div><div class="stat-note">分割後の希薄化後約16.57億株で計算</div></div>'
            '<div class="stat"><div class="stat-value up">1.77兆円</div><div class="stat-label">2027年3月期1Q売上</div><div class="stat-note">2026年4〜6月</div></div>'
            '<div class="stat"><div class="stat-value">1対3</div><div class="stat-label">実施済み株式分割</div><div class="stat-note">2026/09/29から分割後価格</div></div>'
        ),
        "SEC2_LABEL": "NAND業界",
        "SEC3_LABEL": "製品と技術",
        "SEC4_LABEL": "工場と規制",
        "SEC5_LABEL": "競合比較",
        "SEC1_TLDR": li("NANDフラッシュとSSDを作る、日本発のメモリ専業大手です。", "🏭") + li("2027年3月期1QはAIデータセンター需要で大幅増収増益でした。", "📈") + li("市況、為替、設備投資の波で利益が大きく振れます。", "⚠️"),
        "SEC1_FACTS": (
            "<div><dt>正式社名</dt><dd>キオクシアホールディングス</dd></div><div><dt>本社</dt><dd>東京都港区芝浦</dd></div>"
            "<div><dt>上場</dt><dd>東証プライム（285A）</dd></div><div><dt>決算期</dt><dd>3月</dd></div>"
            "<div><dt>代表</dt><dd>太田 博男 CEO</dd></div><div><dt>事業</dt><dd>メモリ関連製品</dd></div>"
        ),
        "SEC1_CARDS": (
            '<div class="card-sm"><span class="card-emoji">💾</span><div class="card-title">何をしている</div><div class="card-desc">データを保存するNANDフラッシュと、それを使ったSSDを作ります。</div></div>'
            '<div class="card-sm"><span class="card-emoji">🏢</span><div class="card-title">主力</div><div class="card-desc">SSD & Storageが2027年3月期1Q売上1.17兆円を占めました。</div></div>'
            '<div class="card-sm"><span class="card-emoji">📊</span><div class="card-title">直近業績</div><div class="card-desc">2027年3月期1Q売上は1.77兆円、営業利益は1.27兆円です。</div></div>'
            '<div class="card-sm"><span class="card-emoji">🤖</span><div class="card-title">注目点</div><div class="card-desc">AI推論向けSSDと第10世代BiCS FLASHの立ち上がりです。</div></div>'
        ),
        "SEC1_BIZMODEL": (
            '<li><span class="kp-emoji">💾</span><span class="kp-text"><b>製品販売</b>：NANDメモリ、SSD、組み込みメモリを顧客へ販売します。</span></li>'
            '<li><span class="kp-emoji">🏭</span><span class="kp-text"><b>製造能力</b>：四日市・北上などの大型拠点と共同投資が競争力の土台です。</span></li>'
            '<li><span class="kp-emoji">📈</span><span class="kp-text"><b>利益の源泉</b>：ASP、ビット出荷、為替、稼働率で粗利が大きく変わります。</span></li>'
        ),
        "SEC1_HIGHLIGHT": '<div class="highlight"><h3>📏 キオクシアを見る基本ルール</h3><p>メモリは好況時に利益が急拡大します。一方で、供給過剰や価格下落では利益が急に縮みます。だから「成長企業」としてだけでなく、景気循環株として見る必要があります。</p></div>',
        "SEC2_ICON": "💽",
        "SEC2_TITLE": "NAND業界の<span class=\"g\">基本</span>",
        "SEC2_SUB": "需要はAI、PC、スマホ。利益は市況で動く",
        "SEC2_TLDR": li("NANDは保存用メモリ。AIでもデータ保存量が増えています。", "💾") + li("価格は需給で大きく動き、業績の振れ幅が大きいです。", "📉") + li("データセンター向けSSDの比率上昇が利益の質を左右します。", "🏢"),
        "SEC2_CONTENT": (
            '<p class="lead">NAND業界は、データを保存する半導体の量と価格で決まる市場です。スマホやPCだけでなく、AIデータセンターの保存需要が重要になっています。</p>'
            '<div class="sowhat"><p><b>つまり</b>、キオクシアの株価は「AI需要が本物か」と「NAND価格が高く保てるか」を同時に見ます。</p></div>'
            '<div class="term-list">'
            + details("需要を動かすもの", "スマホ、PC、データセンター、企業向けSSDの採用が需要を作ります。2027年3月期1Qはデータセンター顧客の生成AI需要が増収の主因でした。", True)
            + details("価格を動かすもの", "NANDは供給過剰になると価格が下がります。逆に供給が絞られ、AI向け需要が強いとASPが上がりやすくなります。")
            + details("利益率の見方", "工場の稼働率、製品ミックス、為替、先端品の歩留まりで変わります。売上が増える局面では固定費効果も出ます。")
            + details("バリューチェーン", "材料・装置からウエハ製造、パッケージ、SSD製品化、顧客販売へ進みます。キオクシアは製造と製品化の中核を担います。")
            + "</div>"
        ),
        "SEC3_TITLE": "主力製品と<span class=\"g\">技術</span>",
        "SEC3_SUB": "SSD、組み込みメモリ、BiCS FLASHを分けて見る",
        "SEC3_TLDR": li("SSD & Storageが直近の成長ドライバーです。", "🚀") + li("第10世代BiCS FLASHは332層、4.8Gb/s interfaceを会社が公表しています。", "🔬") + li("AI向けはCM、GP、LCシリーズが注目製品です。", "🤖"),
        "SEC3_CONTENT": (
            '<div class="product-grid"><div class="product-box"><div class="product-symbol">SSD</div><div class="product-name">SSD & Storage</div><div class="product-use">PC、データセンター、企業向け。</div></div>'
            '<div class="product-box"><div class="product-symbol">SD</div><div class="product-name">Smart Devices</div><div class="product-use">スマホ、車載、産業機器向け。</div></div>'
            '<div class="product-box"><div class="product-symbol">AI</div><div class="product-name">CM / GP / LC</div><div class="product-use">AI推論、GPU拡張、大容量保存。</div></div></div>'
            '<div class="term-list">'
            + details("第10世代BiCS FLASH", "2026年7月に1Tb TLC品のサンプル出荷開始を公表しました。332層、インターフェース速度4.8Gb/s、ビット密度59%向上が会社説明です。", True)
            + details("CMシリーズ", "AI推論のKVキャッシュ保存に向けた高帯域SSDです。NVIDIAのContext Memory Storageにも対応すると会社は説明しています。")
            + details("GPシリーズ", "GPUのメモリ領域を拡張するSuper High IOPS SSDです。会社は100M IOPS以上を掲げています。")
            + details("LCシリーズ", "生成結果データの増加に対応する大容量SSDです。245TBモデルをラインアップしています。")
            + "</div>"
        ),
        "SEC4_TITLE": "工場・投資・<span class=\"g\">規制</span>",
        "SEC4_SUB": "量産力は強み。ただし投資額も大きい",
        "SEC4_TLDR": li("北上Fab2で第10世代BiCS FLASHの生産を予定しています。", "🏭") + li("今後3年、設備投資は年約4,700億円が会社方針です。", "💰") + li("訴訟、輸出規制、為替はリスクとして残ります。", "⚖️"),
        "SEC4_CONTENT": (
            '<ul class="keypoints"><li><span class="kp-emoji">🏭</span><span class="kp-text"><b>量産</b>：第10世代品は北上工場Fab2での生産予定と公表されています。</span></li>'
            '<li><span class="kp-emoji">💸</span><span class="kp-text"><b>投資</b>：AI市場向け成長投資として、今後3年間の設備投資は年約4,700億円、研究開発投資は年約2,300億円です。</span></li>'
            '<li><span class="kp-emoji">⚖️</span><span class="kp-text"><b>訴訟</b>：Viasat訴訟では36.6億円相当を1Qに引当計上しました。会社は争う方針です。</span></li></ul>'
            '<div class="sowhat"><p><b>つまり</b>、成長投資が売上へつながれば強い一方、価格下落時は大きな固定費が負担になります。</p></div>'
        ),
        "SEC5_TITLE": "競合と<span class=\"g\">比べる</span>",
        "SEC5_SUB": "大手メモリ企業との比較軸",
        "SEC5_TLDR": li("競合はSamsung、SK hynix、Micron、Sandiskなどです。", "⚔️") + li("キオクシアはNAND専業色が強く、市況感応度が高いです。", "📊") + li("AI向けSSDで製品ミックス改善を狙います。", "🤖"),
        "SEC5_CONTENT": (
            '<div class="table-wrap"><table class="compare-table"><thead><tr><th>企業</th><th>主な強み</th><th>注意点</th></tr></thead><tbody>'
            '<tr><td class="me">キオクシア</td><td>NANDとSSDに集中。AI向けSSD戦略を強化。</td><td>NAND市況への感応度が高い。</td></tr>'
            '<tr><td>Samsung</td><td>メモリ、ロジック、最終製品まで幅広い。</td><td>事業が広く、NAND単体の比較は難しい。</td></tr>'
            '<tr><td>SK hynix</td><td>AI向けHBMで強い存在感。</td><td>NANDだけでなくDRAM動向も大きい。</td></tr>'
            '<tr><td>Micron</td><td>DRAMとNANDを持つ米国大手。</td><td>メモリ市況の波を受ける。</td></tr>'
            '</tbody></table></div><div class="highlight"><h3>差別化の見方</h3><p>キオクシアはNAND専業に近いため、AIストレージ需要の恩恵が見えやすい反面、NAND価格下落の影響も受けやすい構造です。</p></div>'
        ),
        "SEC6_TLDR": li("NAND、ASP、設備投資の3つを押さえると読みやすいです。", "📌") + li("AI向けSSDは成長期待、株式分割と自社株取得は資本政策です。", "💡") + li("非GAAPは会社管理指標で、IFRS利益とは分けて見ます。", "🧾"),
        "SEC6_CONTENT": '<div class="term-list">' + "".join(details(name, body) for name, body in terms) + "</div>",
        "SEC7_TLDR": li("一番大きいのはNAND価格とAI向け需要です。", "📈") + li("1Qの好業績が続くか、2Q見通しの達成度を見ます。", "🔍") + li("訴訟、投資負担、円高は下向き要因です。", "⚠️"),
        "SEC7_CONTENT": (
            '<div class="timeline"><div class="tl-row"><div class="tl-date">2026/07/31</div><div class="tl-title">1Q決算 <span class="signal bull">追い風</span></div><div class="tl-desc">売上1.77兆円、営業利益1.27兆円。AIデータセンター需要とASP上昇が主因です。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/08-10</div><div class="tl-title">自社株取得枠 <span class="signal neutral">中立〜追い風</span></div><div class="tl-desc">上限8,000億円、3,000万株。実際の取得ペースを確認します。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/09/29</div><div class="tl-title">分割後価格で取引開始 <span class="signal neutral">実施済み</span></div><div class="tl-desc">1対3の株式分割を反映した価格で取引されています。法的な効力発生日は10月1日です。</div></div></div>'
            '<div class="info-row"><div class="info-box info-box-green"><div class="info-title info-title-green">追い風</div><div class="info-text">AIサーバー向けSSD需要、ASP上昇、LTA進展。</div></div>'
            '<div class="info-box info-box-amber"><div class="info-title info-title-amber">確認</div><div class="info-text">2Q売上2.39兆円・営業利益1.89兆円の見通し達成度。</div></div>'
            '<div class="info-box info-box-red"><div class="info-title info-title-red">リスク</div><div class="info-text">NAND価格下落、円高、訴訟追加費用、設備投資負担。</div></div></div>'
            + source_details
        ),
    }


def scenario_values() -> dict[str, str]:
    bear, base, bull = 10000, 17667, 25667
    probs = {"bear": 0.25, "base": 0.50, "bull": 0.25}
    expected = bear * probs["bear"] + base * probs["base"] + bull * probs["bull"]
    band = (P0 - bear) / (bull - bear) * 100
    own_score = (expected - bear) / (bull - bear) * 100
    endpoint_rr = (bull - P0) / (P0 - bear)
    expected_return = expected / P0 - 1
    bear_downside = (P0 - bear) / P0
    score = round(max(0, min(100, 50 + expected_return * 100 - probs["bear"] * bear_downside * 100)))
    common = {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "東京証券取引所プライム市場",
        "VALUATION_DATE": DATE,
        "METHOD": "景気循環企業向けPERシナリオ",
        "VERDICT_STATUS": "標準ケース付近の中立圏",
        "VERDICT_LINE_1": f"評価基準株価は分割後の悲観〜楽観レンジの{band:.1f}%地点です。AI向け需要は強い一方、大型投資とNAND市況の反転には注意が必要です。",
        "VERDICT_LINE_2": "9月29日の権利落ち日から1対3株式分割後の価格で取引されています。株価、EPS、株式数、シナリオ価格をすべて分割後基準へ統一しています。",
        "SCORE": str(score),
        "CURRENT_PRICE": yen(P0),
        "CURRENT_PRICE_NOTE": "2026/09/30 10時台",
        "BASE_PRICE": yen(base),
        "BASE_DELTA": f"{(base / P0 - 1) * 100:+.1f}%",
        "EXPECTED_VALUE": yen(expected),
        "EXPECTED_DELTA": f"{(expected / P0 - 1) * 100:+.1f}%",
        "RISK_CLASS": "やや高い",
        "RISK_NOTE": "市況株として振れ幅が大きい",
        "WARN_BAND": '<div class="wrap"><div class="notice" style="margin-top:14px"><b>注意：</b>Q2以降のNAND価格とAI向け需要は変動します。通期会社計画は開示されていないため、12〜18か月の正規化EPSをこのレポートで推定しています。</div></div>',
        "SNAPSHOT_LEAD": "今の株価は標準ケース付近です。AI需要を一定程度評価する一方、楽観ケースをすべて織り込む水準ではありません。",
        "BAND_POSITION": f"{band:.1f}%",
        "ZONE_JUDGE": "標準ケース付近",
        "ZONE_NOTE": "1Qの利益水準が続くほど標準〜楽観側へ寄ります。",
        "BEAR_PRICE": yen(bear),
        "BULL_PRICE": yen(bull),
        "ENDPOINT_RR": f"{endpoint_rr:.1f}倍",
        "MARKET_SCORE": str(round(band)),
        "OWN_SCORE": str(round(own_score)),
        "MARKET_REVERSE_NOTE": "同じPERモデルで見ると、今の株価は分割後正規化EPS約1,930円、PER9.5倍前後を織り込む水準です。市場の本当の予想ではなく、このモデル上の逆算です。",
        "SCENARIOS_LEAD": "現在株価から独立して、12〜18か月先の正規化EPSとPERを置きました。メモリ市況の山谷をならすため、単四半期利益をそのまま年換算していません。",
        "BEAR_PROB": "25%",
        "BASE_PROB": "50%",
        "BULL_PROB": "25%",
        "BEAR_DELTA": f"{(bear / P0 - 1) * 100:+.1f}%",
        "BULL_DELTA": f"{(bull / P0 - 1) * 100:+.1f}%",
        "BEAR_DL_ROWS": dl([("正規化EPS", "1,250円"), ("PER", "8.0倍"), ("利益前提", "NAND価格が反落"), ("株式数", "約16.57億株")]),
        "BASE_DL_ROWS": dl([("正規化EPS", "1,860円"), ("PER", "9.5倍"), ("利益前提", "AI向けSSDが堅調"), ("株式数", "約16.57億株")]),
        "BULL_DL_ROWS": dl([("正規化EPS", "2,440円"), ("PER", "10.5倍"), ("利益前提", "高ASPとLTAが継続"), ("株式数", "約16.57億株")]),
        "PRICE_ZONE_ROWS": (
            '<div class="zone"><div><b>1万円未満</b><span>★★★★★</span></div><p>悲観ケース以下。市況悪化をかなり織り込む価格帯です。</p></div>'
            '<div class="zone"><div><b>1万〜1.77万円</b><span>★★★</span></div><p>標準ケースの手前です。</p></div>'
            '<div class="zone"><div><b>1.77万〜2.57万円</b><span>★★</span></div><p>AI需要継続をかなり評価する価格帯で、今の株価はここです。</p></div>'
            '<div class="zone"><div><b>2.57万円超</b><span>★</span></div><p>楽観ケース超。さらに強いNAND市況か倍率拡大が必要です。</p></div>'
        ),
        "SIGNAL_ROWS": (
            '<div class="signal"><div><b>AI向けSSD需要</b><span class="up">追い風</span></div><p>データセンター顧客の需要が1Q増収の主因でした。</p></div>'
            '<div class="signal"><div><b>NAND価格</b><span class="up">追い風</span></div><p>ASP上昇は利益率に強く効きます。反落時は逆回転します。</p></div>'
            '<div class="signal"><div><b>自社株取得</b><span class="flat">確認</span></div><p>上限8,000億円ですが、実際の取得額と価格が重要です。</p></div>'
            '<div class="signal"><div><b>訴訟・規制</b><span class="down">注意</span></div><p>Viasat訴訟は引当済みですが、今後の法的手続きは残ります。</p></div>'
        ),
        "POSITIVES": "<li>2027年3月期1Qは売上1.77兆円、営業利益1.27兆円と大幅に伸びました。</li><li>2Q見通しも売上2.39兆円、営業利益1.89兆円と強い会社見通しです。</li><li>AI推論向けSSDと第10世代BiCS FLASHで製品ミックス改善を狙えます。</li><li>上限8,000億円の自社株取得枠は資本効率の改善要因です。</li>",
        "CONCERNS": "<li>NAND市況は短期で大きく変わります。価格下落時は利益が急縮小します。</li><li>通期見通しは出ていません。Q1・Q2の強さをそのまま通年化できません。</li><li>設備投資と研究開発投資が大きく、需要鈍化時は固定費負担になります。</li><li>訴訟、為替、輸出規制など外部要因もあります。</li>",
        "FORMULA": "主計算はPERです。PERは、1株利益に何倍の評価をつけるかを見る方法です。景気循環の強いメモリ企業なので、直近単四半期ではなく正規化EPSを使いました。",
        "CALC_TABLE_HEAD": th("ケース", "正規化EPS", "PER", "計算株価", "確率", "確率加重"),
        "CALC_TABLE_ROWS": tr("悲観", "1,250円", "8.0倍", yen(bear), "25%", "2,500円") + tr("標準", "1,860円", "9.5倍", yen(base), "50%", "8,834円") + tr("楽観", "2,440円", "10.5倍", yen(bull), "25%", "6,417円"),
        "CALC_NOTICE": "現在株価に合わせて標準ケースを置いていません。Q2会社見通し、NAND市況、AI向け製品ミックスを踏まえ、12〜18か月の利益水準を推定しています。",
        "CONDITIONS": details("悲観ケース：1万円 / 確率25%", "AI向け需要は残るものの、NAND価格が反落し、分割後正規化EPSが1,250円程度に下がるケースです。", True) + details("標準ケース：1.77万円 / 確率50%", "データセンター需要が堅調で、FY2027前半の強さが一部続くケースです。") + details("楽観ケース：2.57万円 / 確率25%", "高ASP、LTA、AI向けSSDの製品ミックス改善が重なり、PERもやや拡大するケースです。"),
        "SENSITIVITY_HEAD": th("前提", "弱い", "標準", "強い"),
        "SENSITIVITY_ROWS": tr("正規化EPS", "1,600円 → 15,200円", "1,860円 → 17,667円", "2,130円 → 20,235円") + tr("PER", "8.5倍 → 15,810円", "9.5倍 → 17,667円", "10.5倍 → 19,530円"),
        "SENSITIVITY_NOTE": "1変数だけを動かした簡易感応度です。実際にはEPSとPERが同時に動くことがあります。",
        "DIST_LEAD": "モンテカルロではなく、悲観・標準・楽観の3点分布です。",
        "DIST_ROWS": '<div class="dist-row"><span>1万円</span><div class="track"><i style="width:25%"></i></div><b>25%</b></div><div class="dist-row"><span>1.77万円</span><div class="track"><i style="width:50%"></i></div><b>50%</b></div><div class="dist-row"><span>2.57万円</span><div class="track"><i style="width:25%"></i></div><b>25%</b></div>',
        "DIST_SUMMARY": "中心は標準ケースです。ただしメモリ市況株なので、両端への振れも小さくありません。",
        "WATCH_ROWS": '<div class="signal"><div><b>2026年7〜9月期の実績</b></div><p>会社見通しの売上2.39兆円、営業利益1.89兆円に対する達成度を確認します。</p></div><div class="signal"><div><b>SSD & Storage売上</b></div><p>AIデータセンター需要がどの程度続くかを見ます。</p></div><div class="signal"><div><b>自社株取得の進捗</b></div><p>上限枠に対して実際にどれだけ取得したかを確認します。</p></div>',
        "ASSUMPTIONS_ROWS": tr("評価基準株価", yen(P0), "公式市場データで確認済み", "2026/09/30 10時台") + tr("希薄化後株式数", "約16.57億株", "このレポートの推定", "分割後換算") + tr("1Q売上", "1.77兆円", "公式情報で確認済み", "2026年4〜6月") + tr("2Q売上見通し", "2.39兆円", "会社の目標・予定", "2026年7〜9月") + tr("株式分割", "1株を3株", "会社発表", "2026/09/29から分割後価格で取引"),
        "DEEPDIVE_DETAILS": details("手法選定理由", "キオクシアは黒字化済みですが、NAND価格に左右される景気循環企業です。そのため、単純DCFよりも正規化EPSにPERをかける方法を主にしました。", True) + details("希薄化と株式分割", "Q1の希薄化EPSから分割後約16.57億株へ換算しました。株価、EPS、株式数、シナリオ価格はすべて1対3株式分割後の単位です。") + details("主要出典", f'{source_link("1Q決算短信", "q1")}、{source_link("有価証券報告書", "annual")}、{source_link("Investor Day", "investor_day")}、{source_link("株式分割", "split")}、{source_link("自社株取得枠", "buyback")}。<br><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>'),
        "DISCLAIMER": "本資料は情報提供を目的とした試算です。投資助言ではありません。半導体メモリ株は市況、為替、顧客投資、規制で大きく変動します。",
        "FOOTER_NOTE": f"SiM MARKET LAB｜{COMPANY}（{TICKER}）株価シナリオ｜作成日 {DATE}",
    }
    return common


def catalyst_values() -> dict[str, str]:
    non_quant = (
        '<div class="priced"><div class="priced-head"><span>主要材料の推定織り込み</span><b>58%</b></div>'
        '<p>仮定：2Q会社見通しの達成を60%、AI向けSSD採用を55%、自社株取得の実行を70%、株式分割後の需給改善を45%として置き、重複を控除しました。</p>'
        '<p>読み方：AI需要と自社株取得はある程度株価に入っていますが、2Q実績とASPが強ければまだ標準ケース側へ余地があります。</p>'
        '<p>次に見る数字：SSD & Storage売上、ASP、2Q実績、自社株取得進捗です。</p>'
        '<p>再計算方法：売上、EPS、株式数へ分解し、株価シナリオと同じPERモデルで織り込み度を更新します。</p></div>'
    )
    cards = []
    impact_map = {
        "2026年7〜9月期決算と会社見通しの達成度": ("+10〜24%", "-5〜+8%", "-15〜-30%", "メモリ株では決算とASPがEPSを直接動かすため、短期材料として最大級です。"),
        "自社株取得枠の実行": ("+6〜14%", "-3〜+5%", "-6〜-14%", "株式数と需給には効きますが、NAND市況や利益水準そのものは変えないため中程度です。"),
        "株式分割後の需給定着": ("+2〜7%", "-2〜+3%", "-4〜-8%", "分割後の売買代金と投資家層の変化は需給に影響しますが、企業価値を直接変えないため小さくしています。"),
        "第10世代BiCS FLASHとAI向けSSDの立ち上がり": ("+12〜28%", "-5〜+10%", "-12〜-26%", "AI向けSSDは製品ミックスと将来PERを動かすため、決算に近い大きさで見ます。"),
    }
    description_map = {
        "2026年7〜9月期決算と会社見通しの達成度": "次回決算は、NAND市況とAI向けSSD需要が利益にどれだけ反映されたかを見る材料です。売上、営業利益、ASP、在庫の方向感がそろうと、メモリ株として評価されやすくなります。",
        "自社株取得枠の実行": "自社株取得は、株式数の減少と需給改善を通じて1株価値を押し上げる材料です。ただし事業利益そのものを増やすわけではないため、決算や市況材料とは分けて見ます。",
        "株式分割後の需給定着": "1対3の株式分割はすでに価格へ反映されています。ここで確認するのは、投資単位の低下が売買代金や個人投資家の参加につながるかです。",
        "第10世代BiCS FLASHとAI向けSSDの立ち上がり": "第10世代BiCS FLASHとAI向けSSDは、製品ミックスを高付加価値側へ寄せられるかを見る中期材料です。採用や量産が進めば、将来の利益率とPERを支えます。",
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
<div class="evidence"><div><h4>根拠</h4><ul>{evidence}</ul></div><div><h4>反証・先行指標</h4><ul><li>SSD & Storage売上の減速</li><li>ASP低下や在庫増加</li><li>設備投資負担の増加</li></ul></div></div>
</article>'''
    cards.append(card(
        "2026年7〜9月期決算と会社見通しの達成度",
        "2026年11月ごろ",
        '<span class="chip">重要度5</span><span class="chip blue">当方推定の時期</span>',
        '<span>2Q実績</span><i>→</i><span>正規化EPS</span><i>→</i><span>PER評価</span>',
        "売上2.39兆円、営業利益1.89兆円を上回り、AI需要の持続が確認される状態です。",
        "会社見通し近辺で、AI需要の強さは続くが追加上振れは限られる状態です。",
        "見通し未達、ASP低下、在庫増加が見える状態です。",
        "<li>1Q決算で2Q売上2.39兆円、営業利益1.89兆円の見通しを開示。</li><li>会社はデータセンター需要が強いと説明。</li>",
    ))
    cards.append(card(
        "自社株取得枠の実行",
        "2026/08/03〜10/30",
        '<span class="chip">重要度4</span><span class="chip">日程確定</span>',
        '<span>取得額</span><i>→</i><span>株式数</span><i>→</i><span>EPS</span>',
        "上限8,000億円に近い取得が進み、平均取得単価も過度に高くない状態です。",
        "一部取得にとどまり、EPS押し上げ効果が限定的な状態です。",
        "市場環境により取得が少ない、または高値取得で効果が薄い状態です。",
        "<li>上限3,000万株、8,000億円の取得枠を公表。</li><li>期間は2026年8月3日から10月30日。</li>",
    ))
    cards.append(card(
        "株式分割後の需給定着",
        "2026/09/29以降",
        '<span class="chip amber">重要度2</span><span class="chip">分割実施済み</span>',
        '<span>投資単位低下</span><i>→</i><span>流動性</span><i>→</i><span>投資家層</span>',
        "分割後に売買代金と個人投資家参加が増え、需給が安定する状態です。",
        "売買代金や投資家層に大きな変化がなく、企業価値への直接影響も小さい状態です。",
        "分割後に短期需給が荒れ、業績評価より値動きが先行する状態です。",
        "<li>2026年9月29日から1対3分割後の価格で取引を開始。</li><li>法的な効力発生日は2026年10月1日。</li><li>投資単位を下げる目的と会社は説明。</li>",
    ))
    cards.append(card(
        "第10世代BiCS FLASHとAI向けSSDの立ち上がり",
        "2026年後半〜2027年",
        '<span class="chip">重要度4</span><span class="chip blue">期間のみ公表</span>',
        '<span>サンプル</span><i>→</i><span>採用</span><i>→</i><span>高付加価値売上</span>',
        "CM/GP/LC系の採用が進み、AI向けSSDの売上比率が上がる状態です。",
        "サンプルや評価は進むが、売上寄与は段階的な状態です。",
        "顧客採用や量産が遅れ、設備投資だけが先行する状態です。",
        "<li>第10世代BiCS FLASH 1Tb TLC品のサンプル出荷開始を公表。</li><li>Investor DayでAI推論向け製品群を説明。</li>",
    ))
    return {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "東京証券取引所プライム市場",
        "VALUATION_DATE": DATE,
        "LAST_UPDATED": DATE,
        "REPORT_STATUS": "重要材料が複数ある",
        "SUMMARY_LINE_1": "決算、自社株取得、分割後の需給、AI向けSSDの立ち上がりが今後の主な材料です。",
        "SUMMARY_LINE_2": "足りない情報は仮定を置き、主要材料の織り込み度を58%と推定します。",
        "OVERALL_PRICED_IN": "58%",
        "OVERALL_PRICED_LABEL": "主要材料の推定織り込み",
        "PRICED_IN_CONFIDENCE": "ふつう",
        "CURRENT_PRICE": yen(P0),
        "CURRENT_PRICE_NOTE": "2026/09/30 10時台",
        "NEXT_CATALYST_TITLE": "2Q決算",
        "NEXT_CATALYST_WINDOW": "2026年11月ごろ",
        "DATE_CONFIDENCE": "一部確定",
        "CATALYST_COUNT": "4件",
        "WARN_BAND": "",
        "NO_CATALYST_NOTICE": "",
        "OVERALL_PRICED_BLOCK": non_quant,
        "PRICED_IN_METHOD": "未確定情報に仮定確率を置き、2Q実績、AI向けSSD、自社株取得、分割後の需給を標準ケース価値へ重み付けして推定。",
        "SURPRISE_UP": "2Q決算が会社見通しを上回り、SSD & Storage売上とASPの強さが続くことです。",
        "SURPRISE_DOWN": "NAND価格の反落、AI向け需要の鈍化、在庫増加、訴訟費用の追加です。",
        "PRIMARY_RISK": "好業績がすでに株価へ入ったあとで、少しの未達でも失望になりやすい点です。",
        "TIMELINE_ROWS": (
            '<div class="time-row"><div class="time-date">2026/08-10</div><div class="time-dot"></div><div class="time-body"><b>自社株取得枠</b><p>上限8,000億円、3,000万株。市場買付。</p><div class="time-meta"><span class="chip">日程確定</span></div></div></div>'
            '<div class="time-row"><div class="time-date">2026/09/29</div><div class="time-dot"></div><div class="time-body"><b>分割後価格で取引開始</b><p>1対3分割後の売買代金と投資家層の変化を確認します。</p><div class="time-meta"><span class="chip">実施済み</span></div></div></div>'
            '<div class="time-row"><div class="time-date">2026/11ごろ</div><div class="time-dot"></div><div class="time-body"><b>2Q決算</b><p>会社見通しに対する達成度を確認します。</p><div class="time-meta"><span class="chip blue">当方推定</span></div></div></div>'
            '<div class="time-row"><div class="time-date">2026後半</div><div class="time-dot"></div><div class="time-body"><b>AI向けSSD・BiCS10</b><p>サンプル、採用、量産への進み方を確認します。</p><div class="time-meta"><span class="chip blue">期間のみ公表</span></div></div></div>'
        ),
        "CATALYST_CARDS": "".join(cards) + '<p class="small">※下の％は、この結果が出た後に市場が材料を評価し直した場合の上昇・下落幅の目安です。実際の値動きは地合い、直前の株価上昇、同時ニュースで変わります。</p>',
        "DEPENDENCY_ROWS": '<div class="signal"><div><b>AI向けSSDとBiCS10</b><span class="up">同じ価値経路</span></div><p>技術発表、サンプル、顧客採用、売上認識は段階イベントです。単純に足しません。</p></div><div class="signal"><div><b>自社株取得と株式分割</b><span class="flat">別経路</span></div><p>自社株取得は株式数、株式分割は流動性に主に効きます。</p></div>',
        "WATCH_ROWS": '<div class="signal"><div><b>SSD & Storage売上</b><span class="up">最重要</span></div><p>AI需要の継続を見る中心指標です。</p></div><div class="signal"><div><b>ASPとビット出荷</b><span class="up">重要</span></div><p>価格と数量のどちらで伸びたかを分けます。</p></div><div class="signal"><div><b>自社株取得進捗</b><span class="flat">確認</span></div><p>取得株数、取得額、平均単価を確認します。</p></div><div class="signal"><div><b>訴訟の続報</b><span class="down">注意</span></div><p>追加費用や法的手続きの進展を確認します。</p></div>',
        "ASSUMPTION_ROWS": tr("評価基準株価", yen(P0), "公式市場データで確認済み", DATE, "2026/09/30 10時台") + tr("2Q会社見通し", "売上2.39兆円、営業利益1.89兆円", "会社の目標・予定", "2026/07/31", "2026年7〜9月") + tr("自社株取得枠", "上限8,000億円", "会社の目標・予定", "2026/07/31", "実際の取得は市場次第") + tr("株式分割", "1株を3株", "公式情報で確認済み", "2026/09/29", "分割後価格で取引開始（効力発生日は10/01）"),
        "SOURCE_DETAILS": f'<ul><li>{source_link("1Q決算短信", "q1")}</li><li>{source_link("Investor Day 2026", "investor_day")}</li><li>{source_link("自社株取得枠", "buyback")}</li><li>{source_link("株式分割", "split")}</li><li>{source_link("第10世代BiCS FLASH", "bics10")}</li><li>{source_link("Viasat訴訟判断", "lawsuit")}</li></ul><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p>',
        "VALIDATION_DETAILS": "<p>PASS：重要カタリストは公式資料で確認。WARN：2Q決算日は当方推定のため、確定日として表示していません。</p>",
        "UPDATE_HISTORY": f"<p>{DATE}：初版作成。1Q決算、Investor Day、自社株取得枠、訴訟判断を反映。株価・EPS・株式数・シナリオは1対3分割後基準で統一。</p>",
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
        if stock["id"] == "kioxia-285a":
            for report in stock["reports"].values():
                report["available"] = True
    stocks_path.write_text(json.dumps(stocks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    signals_path = ROOT / "data" / "signals.json"
    signals = json.loads(signals_path.read_text(encoding="utf-8"))
    signals["updatedAt"] = datetime.now(timezone.utc).isoformat()
    signals["signals"]["kioxia-285a"] = {
        "position": round(0.60 * max(0.0, min(100.0, (P0 - 10000) / (25667 - 10000) * 100)) + 0.25 * 65.0 + 0.15 * 55.0, 1),
        "zone": "中立",
        "asOf": DATE,
        "components": {
            "valuation": round(max(0.0, min(100.0, (P0 - 10000) / (25667 - 10000) * 100)), 1),
            "catalysts": 65.0,
            "businessRisk": 55.0,
        },
        "reportRevision": "kioxia-285a-2026-09-30",
        "summary": "1対3分割後の標準ケース付近。AI向け需要と自社株取得が支えだが、NAND市況の反落リスクは残る。",
    }
    signals_path.write_text(json.dumps(signals, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_live_price_helper() -> None:
    helper = ROOT / "lab" / "assets" / "js" / "live-report-price.js"
    helper.parent.mkdir(parents=True, exist_ok=True)
    helper.write_text(
        """(() => {
  const body = document.body;
  const ticker = body?.dataset?.stockTicker;
  const source = body?.dataset?.priceSource;
  if (!ticker || !source) return;

  function parseScenarioPrice(text) {
    if (!text) return null;
    const normalized = String(text).replace(/,/g, "").replace(/[^\\d.-]/g, "");
    const value = Number(normalized);
    return Number.isFinite(value) ? value : null;
  }

  function clampPercent(value) {
    if (!Number.isFinite(value)) return null;
    return Math.min(100, Math.max(0, value));
  }

  function updateValuationPosition(price) {
    const labels = Array.from(document.querySelectorAll(".position-labels span"));
    if (labels.length < 3) return;
    const bear = parseScenarioPrice(labels[0].textContent);
    const bull = parseScenarioPrice(labels[2].textContent);
    if (!Number.isFinite(bear) || !Number.isFinite(bull) || bear === bull) return;

    const position = clampPercent(((price - bear) / (bull - bear)) * 100);
    if (!Number.isFinite(position)) return;
    const positionText = `${position.toFixed(1)}%`;
    const scoreText = String(Math.round(position));

    document.querySelectorAll(".position-line .pin").forEach((pin) => {
      pin.style.left = positionText;
      pin.setAttribute("aria-label", `現在株価の位置 ${positionText}`);
    });

    const snapshot = document.querySelector("#snapshot");
    const positionParagraph = snapshot?.querySelector(".grid-2 > div:first-child p:not(.lead)");
    const positionValue = positionParagraph?.querySelector("b");
    if (positionValue) positionValue.textContent = positionText;

    const marketCompare = snapshot?.querySelector(".compare > div:first-child");
    const marketLabel = marketCompare?.querySelector("b");
    const marketMeter = marketCompare?.querySelector(".meter i");
    if (marketLabel) marketLabel.textContent = `今の株価 ${scoreText}/100`;
    if (marketMeter) marketMeter.style.width = `${Math.round(position)}%`;
  }

  fetch(source, { cache: "no-store" })
    .then((response) => response.ok ? response.json() : null)
    .then((payload) => {
      const prices = payload?.prices || {};
      const entry = Object.values(prices).find((item) => item?.symbol?.replace(".T", "") === ticker || item?.symbol === `${ticker}.T`);
      if (!entry || !Number.isFinite(Number(entry.price))) return;
      const price = Number(entry.price);
      const formatter = new Intl.NumberFormat("ja-JP", {
        style: "currency",
        currency: entry.currency || "JPY",
        maximumFractionDigits: entry.currency === "JPY" ? 0 : 2
      });
      document.querySelectorAll("[data-live-price]").forEach((node) => { node.textContent = formatter.format(price); });
      updateValuationPosition(price);
      if (entry.marketTime) {
        const date = new Intl.DateTimeFormat("ja-JP", {
          timeZone: "Asia/Tokyo",
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit"
        }).format(new Date(entry.marketTime));
        document.querySelectorAll("[data-live-price-date]").forEach((node) => { node.textContent = `${date}（分析基準値）`; });
      }
    })
    .catch(() => {});
})();
""",
        encoding="utf-8",
    )


def main() -> None:
    write_reports()
    write_live_price_helper()
    update_site_data()


if __name__ == "__main__":
    main()
