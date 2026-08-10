"""Generate Zapata Quantum report HTML files from the bundled SiM templates."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from generate_rocket_lab_reports import dl, li, render_template, th, tr


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stocks" / "zapata-zpta"

COMPANY = "ザパタ・クオンタム"
TICKER = "ZPTA"
DATE = "2026-08-11"
P0 = 0.81
PREVIOUS_CLOSE = 0.7505
SHARES_M = 187.33
MARKET_CAP_M = P0 * SHARES_M

BEAR = 0.30
BASE = 1.20
BULL = 2.35
BAND_POSITION = (P0 - BEAR) / (BULL - BEAR) * 100
SIGNAL_POSITION = round(0.60 * round(BAND_POSITION, 1) + 0.25 * 70.0 + 0.15 * 88.0, 1)

SOURCES = {
    "overview": "https://investors.zapataquantum.com/",
    "presentation": "https://investors.zapataquantum.com/static-files/06b6e9ff-16b4-4999-ae91-8bf38d8f49b4",
    "otcqb": "https://investors.zapataquantum.com/news-releases/news-release-details/zapata-quantum-announces-uplisting-otcqb-market",
    "nvidia": "https://investors.zapataquantum.com/news-releases/news-release-details/zapata-quantum-teams-nvidia-apply-agentic-ai-accelerate-quantum",
    "conference": "https://investors.zapataquantum.com/news-releases/news-release-details/zapata-quantum-present-global-technology-virtual-investor",
    "financing": "https://investors.zapataquantum.com/news-releases/news-release-details/zapata-quantum-completes-oversubscribed-15-million-strategic",
    "faq": "https://investors.zapataquantum.com/resources/investor-faqs",
    "quote": "https://stockanalysis.com/quote/otc/ZPTA/",
    "sec_s1": "https://www.sec.gov/Archives/edgar/data/1843714/000168316826004579/zpat_s1.htm",
}


def usd(value: int | float) -> str:
    return f"${value:,.4f}" if abs(value) < 1 else f"${value:,.2f}" if abs(value) < 100 else f"${value:,.0f}"


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
        f'{source_link("2026年7月投資家向け資料", "presentation")}、'
        f'{source_link("OTCQB上場リリース", "otcqb")}、'
        f'{source_link("NVIDIA連携リリース", "nvidia")}、'
        f'{source_link("株価・統計", "quote")}を確認しました。'
        "本文の数値は2026年8月11日時点で取得できた公開情報に基づきます。"
        '</p><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p></div></details>'
    )
    terms = [
        ("ZPTA", "Zapata Quantumの普通株ティッカーです。ユーザー入力はZATAでしたが、公式FAQではOTCのZPTAと確認できます。"),
        ("OTCQB", "米国OTC市場の一つです。NasdaqやNYSEより流動性と情報量が小さい銘柄が多いです。"),
        ("量子ソフトウェア", "量子コンピュータの用途発見、アルゴリズム開発、実行環境を支えるソフトウェア領域です。"),
        ("ハードウェア非依存", "特定の量子コンピュータ方式に固定されず、複数方式で使える設計です。"),
        ("DARPA Quantum Benchmarking", "量子計算の実用性を評価する米国防高等研究計画局のプログラムです。"),
        ("QIR", "Quantum Intermediate Representationです。量子・ハイブリッド計算の中間表現に関わる技術です。"),
        ("Agentic AI", "AIエージェントを使って、量子アルゴリズムの探索や資源見積もりを自動化する方向性です。"),
        ("アップリスティング", "より上位の市場へ移ることです。OTCQB後はNasdaq/NYSE再上場が材料になります。"),
        ("希薄化", "資金調達で株式数が増え、1株あたり価値が薄まることです。"),
        ("流動性リスク", "売買が薄く、少額の注文でも株価が大きく動くリスクです。"),
    ]
    return {
        "TICKER": TICKER,
        "COMPANY_NAME": COMPANY,
        "INDUSTRY": "量子ソフトウェア・先端AI",
        "DATE": DATE,
        "TAGLINE": "量子コンピューティングの用途発見、アルゴリズム開発、ハードウェア非依存の実行基盤を提供する、OTCQB上場の量子ソフトウェア企業です。",
        "HERO_TAGS": '<span class="hero-tag">米国株</span><span class="hero-tag">OTCQB</span><span class="hero-tag">量子ソフトウェア</span><span class="hero-tag">AI</span>',
        "HERO_STATS": (
            f'<div class="stat"><div class="stat-value">{usd(P0)}</div><div class="stat-label">評価基準株価</div><div class="stat-note">2026/08/07終値</div></div>'
            f'<div class="stat"><div class="stat-value">${MARKET_CAP_M:.1f}M</div><div class="stat-label">時価総額の目安</div><div class="stat-note">約1.87億株で計算</div></div>'
            '<div class="stat"><div class="stat-value up">60+</div><div class="stat-label">特許</div><div class="stat-note">付与・出願中</div></div>'
            '<div class="stat"><div class="stat-value">OTCQB</div><div class="stat-label">市場</div><div class="stat-note">2026/06/16上場</div></div>'
        ),
        "SEC2_LABEL": "事業モデル",
        "SEC3_LABEL": "技術",
        "SEC4_LABEL": "上場・資金",
        "SEC5_LABEL": "競合比較",
        "SEC1_TLDR": li("Zapata Quantumは量子ソフトウェア専業に近い希少な公開企業です。", "*") + li("2026年6月にOTCQBへ上場し、NVIDIA連携と投資家認知拡大が主な材料です。", "*") + li("一方でOTCの超小型株で、売上・契約・資金調達・流動性リスクが非常に大きいです。", "!"),
        "SEC1_FACTS": (
            "<div><dt>正式社名</dt><dd>Zapata Quantum, Inc.</dd></div><div><dt>本社</dt><dd>Boston, Massachusetts</dd></div>"
            "<div><dt>市場</dt><dd>OTCQB（ZPTA）</dd></div><div><dt>業種</dt><dd>ソフトウェア・量子コンピューティング</dd></div>"
            "<div><dt>創業</dt><dd>2017年</dd></div><div><dt>決算期</dt><dd>12月</dd></div>"
        ),
        "SEC1_CARDS": (
            '<div class="card-sm"><span class="card-emoji">🧮</span><div class="card-title">何をしている</div><div class="card-desc">量子アプリの発見・開発・実行を支えるソフトウェアを作ります。</div></div>'
            '<div class="card-sm"><span class="card-emoji">🤝</span><div class="card-title">材料</div><div class="card-desc">NVIDIA連携、DARPA実績、特許、OTCQB上場が注目です。</div></div>'
            '<div class="card-sm"><span class="card-emoji">📈</span><div class="card-title">上値</div><div class="card-desc">Nasdaq/NYSE再上場、商業契約、政府案件で評価が変わります。</div></div>'
            '<div class="card-sm"><span class="card-emoji">⚠️</span><div class="card-title">リスク</div><div class="card-desc">OTC流動性、資金調達、売上未確立、希薄化が大きな注意点です。</div></div>'
        ),
        "SEC1_BIZMODEL": (
            '<li><span class="kp-emoji">🧮</span><span class="kp-text"><b>量子アプリ開発基盤</b>：用途発見、資源見積もり、アルゴリズム開発を支援します。</span></li>'
            '<li><span class="kp-emoji">🧠</span><span class="kp-text"><b>AI連携</b>：Agentic AIで量子アルゴリズム開発を速くする方向です。</span></li>'
            '<li><span class="kp-emoji">🏛️</span><span class="kp-text"><b>公的・企業案件</b>：DARPA、政府、企業との接点が将来収益の材料です。</span></li>'
        ),
        "SEC1_HIGHLIGHT": '<div class="highlight"><h3>ZPTAを見る基本ルール</h3><p>ZPTAは量子テーマだけで買う銘柄ではなく、商業契約、政府プログラム、資金余力、上位市場への再上場可能性をセットで見る銘柄です。OTC銘柄なので流動性リスクも必ず見ます。</p></div>',
        "SEC2_ICON": "🧮",
        "SEC2_TITLE": "量子ソフトウェアの<span class=\"g\">基本</span>",
        "SEC2_SUB": "ハードウェア競争の次に来る応用開発",
        "SEC2_TLDR": li("Zapataは量子ハードそのものではなく、量子アプリケーション開発を支援する企業です。", "*") + li("投資家向け資料では、量子ソフトウェアの応用開発がボトルネックと説明しています。", "*") + li("ただし市場はまだ初期で、売上化の時期と規模は不確実です。", "!"),
        "SEC2_CONTENT": (
            '<p class="lead">Zapataは、量子コンピュータを何に使うか、どの方式が有利か、必要なリソースはどれくらいかを企業や政府が評価するためのソフトウェア基盤を狙います。</p>'
            '<div class="sowhat"><p><b>つまり</b>、ZPTAは「量子ハードを作る会社」ではなく「量子を使えるアプリに落とす会社」として見るのが自然です。</p></div>'
            '<div class="term-list">'
            + details("ハードウェア非依存", "量子方式がまだ固まっていない段階では、特定ハードに縛られないソフトウェアが価値を持ちます。", True)
            + details("Quantum Application Intelligence", "どの用途が量子計算に向いているかを見つけ、事業判断に使える形にする方向です。")
            + details("Quantum Application Engineering", "見つけた用途をアルゴリズム、実装、実行へ進める開発支援です。")
            + details("サブスクリプションと専門サービス", "投資家向け資料では、プラットフォーム提供と高度な技術サービスを組み合わせるモデルが示されています。")
            + "</div>"
        ),
        "SEC3_TITLE": "技術と<span class=\"g\">知財</span>",
        "SEC3_SUB": "DARPA・NVIDIA・特許が評価材料",
        "SEC3_TLDR": li("Zapataは60件超の特許と40本超の論文を強みとして示しています。", "*") + li("DARPA Quantum Benchmarkingの全主要フェーズに関わった点を差別化材料にしています。", "*") + li("NVIDIA連携は話題性がありますが、売上化までの距離は確認が必要です。", "!"),
        "SEC3_CONTENT": (
            '<div class="product-grid"><div class="product-box"><div class="product-symbol">AI</div><div class="product-name">Agentic AI</div><div class="product-use">量子資源見積もりを自動化。</div></div>'
            '<div class="product-box"><div class="product-symbol">QB</div><div class="product-name">DARPA</div><div class="product-use">評価プログラム実績。</div></div>'
            '<div class="product-box"><div class="product-symbol">QIR</div><div class="product-name">知財</div><div class="product-use">中間表現の特許。</div></div></div>'
            '<div class="term-list">'
            + details("NVIDIA連携", "量子アルゴリズム開発のボトルネックであるリソース見積もりにAgentic AIを使う取り組みです。", True)
            + details("DARPA実績", "投資家向け資料では、DARPA Quantum Benchmarkingの3つの重要フェーズ全てに選ばれた唯一の企業と説明されています。")
            + details("QIR特許", "複数ハードやハイブリッド計算をつなぐ中間表現の知財が基盤価値になります。")
            + details("商業化の課題", "技術価値が高くても、継続売上・大型契約・導入事例に変わらないと株価評価は安定しません。")
            + "</div>"
        ),
        "SEC4_TITLE": "OTCQBと<span class=\"g\">資金</span>",
        "SEC4_SUB": "再上場期待と希薄化を同時に見る",
        "SEC4_TLDR": li("2026年6月にOTCQBへアップリスティングしました。", "*") + li("2026年4月に$15Mの戦略的資金調達を完了し、再建後の成長資金を確保しました。", "*") + li("OTC銘柄のため、流動性、追加増資、登録株式の売却圧力が大きな注意点です。", "!"),
        "SEC4_CONTENT": (
            '<ul class="keypoints"><li><span class="kp-emoji">📈</span><span class="kp-text"><b>OTCQB</b>：2026年6月16日からOTCQBで取引されています。</span></li>'
            '<li><span class="kp-emoji">💵</span><span class="kp-text"><b>資金調達</b>：4月に$15Mの戦略的資金調達を完了しました。</span></li>'
            '<li><span class="kp-emoji">⚠️</span><span class="kp-text"><b>登録株式</b>：S-1では売却株主による登録が示され、需給には注意が必要です。</span></li></ul>'
            '<div class="sowhat"><p><b>つまり</b>、再建後の材料はありますが、株価を見る時は「夢」だけでなく「資金が続くか、株式数が増えすぎないか」を必ず確認します。</p></div>'
        ),
        "SEC5_TITLE": "競合と<span class=\"g\">比べる</span>",
        "SEC5_SUB": "量子ハード企業とは評価軸が違う",
        "SEC5_TLDR": li("比較対象は量子ハード企業、AI/量子ソフト企業、研究支援SaaSです。", "*") + li("Zapataはハード非依存と知財を強みにします。", "*") + li("一方、資金力と販売力では大手・上場ハード企業に劣ります。", "!"),
        "SEC5_CONTENT": (
            '<div class="table-wrap"><table class="compare-table"><thead><tr><th>対象</th><th>強み</th><th>注意点</th></tr></thead><tbody>'
            '<tr><td class="me">Zapata</td><td>量子ソフト専業、DARPA実績、NVIDIA連携、特許。</td><td>OTC、売上規模、資金余力、流動性。</td></tr>'
            '<tr><td>量子ハード企業</td><td>ハード進展でテーマ性が強い。</td><td>方式競争と設備投資負担が大きい。</td></tr>'
            '<tr><td>大手クラウド</td><td>資金、顧客、研究者、販売網。</td><td>量子単独の株価感応度は低い。</td></tr>'
            '<tr><td>AIソフト企業</td><td>商業化が近い場合が多い。</td><td>量子専業の希少性は低い。</td></tr>'
            '</tbody></table></div><div class="highlight"><h3>差別化の見方</h3><p>ZPTAは、量子テーマの中でも「応用開発ソフト」に賭ける銘柄です。契約転換と上位市場再上場が見えて初めて、評価が安定しやすくなります。</p></div>'
        ),
        "SEC6_TLDR": li("ZPTA、OTCQB、量子ソフト、NVIDIA、DARPA、希薄化を押さえると読みやすいです。", "*") + li("売上よりも契約化、資金、再上場の進捗が重要です。", "*") + li("OTC銘柄なので、流動性と需給には特に注意です。", "!"),
        "SEC6_CONTENT": '<div class="term-list">' + "".join(details(name, body) for name, body in terms) + "</div>",
        "SEC7_TLDR": li("最大材料は商業契約、政府プログラム、Nasdaq/NYSE再上場の進捗です。", "*") + li("NVIDIA連携や投資家認知拡大は短期材料です。", "*") + li("追加増資、登録株式売却、流動性低下には注意です。", "!"),
        "SEC7_CONTENT": (
            '<div class="timeline"><div class="tl-row"><div class="tl-date">2026/04/23</div><div class="tl-title">$15M戦略的資金調達 <span class="signal bull">資金</span></div><div class="tl-desc">再建後の成長資金として調達を完了。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/06/16</div><div class="tl-title">OTCQBへアップリスティング <span class="signal bull">市場</span></div><div class="tl-desc">視認性と流動性向上、上位市場再上場への一歩。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/06/23</div><div class="tl-title">NVIDIA連携 <span class="signal bull">提携</span></div><div class="tl-desc">Agentic AIで量子アルゴリズム開発を加速する取り組み。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/07/13</div><div class="tl-title">投資家向け資料 <span class="signal neutral">認知</span></div><div class="tl-desc">商業転換、提携、政府案件、再上場をカタリストとして提示。</div></div></div>'
            '<div class="info-row"><div class="info-box info-box-green"><div class="info-title info-title-green">追い風</div><div class="info-text">量子テーマ、NVIDIA、DARPA、知財、OTCQB。</div></div>'
            '<div class="info-box info-box-amber"><div class="info-title info-title-amber">確認</div><div class="info-text">契約転換、資金余力、再上場、売買高。</div></div>'
            '<div class="info-box info-box-red"><div class="info-title info-title-red">リスク</div><div class="info-text">OTC流動性、希薄化、売上未確立、需給悪化。</div></div></div>'
            + source_details
        ),
    }


def scenario_values() -> dict[str, str]:
    probs = {"bear": 0.35, "base": 0.45, "bull": 0.20}
    expected = BEAR * probs["bear"] + BASE * probs["base"] + BULL * probs["bull"]
    own_score = (expected - BEAR) / (BULL - BEAR) * 100
    endpoint_rr = (BULL - P0) / max(P0 - BEAR, 0.01)
    expected_return = expected / P0 - 1
    bear_downside = (P0 - BEAR) / P0
    score = round(max(0, min(100, 50 + expected_return * 100 - probs["bear"] * bear_downside * 100)))
    return {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "OTCQB",
        "VALUATION_DATE": DATE,
        "METHOD": "OTC超小型・テーマ株向けリスク調整シナリオ",
        "VERDICT_STATUS": "材料は強いが超高リスク中立",
        "VERDICT_LINE_1": f"評価基準株価は悲観〜楽観レンジの{BAND_POSITION:.1f}%地点です。量子ソフトの材料は強い一方、OTC流動性と資金調達リスクが大きい局面です。",
        "VERDICT_LINE_2": "この試算は2026年8月11日時点で取得できた公開情報に基づきます。契約転換、再上場、資金調達で更新が必要です。",
        "SCORE": str(score),
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "2026/08/07終値",
        "BASE_PRICE": usd(BASE),
        "BASE_DELTA": pct(BASE / P0 - 1),
        "EXPECTED_VALUE": usd(expected),
        "EXPECTED_DELTA": pct(expected / P0 - 1),
        "RISK_CLASS": "極めて高",
        "RISK_NOTE": "OTCQB、超小型、売上未確立、流動性リスク",
        "WARN_BAND": '<div class="wrap"><div class="notice" style="margin-top:14px"><b>注意：</b>ZPTAはOTCQBの超小型株です。売買高、スプレッド、増資、登録株式売却で株価が大きく変動します。</div></div>',
        "WARN_MESSAGE": "OTC超小型株のため、通常のPER評価ではなくイベント確率と資金・流動性リスクで見ます。",
        "SNAPSHOT_LEAD": "今の株価は悲観寄りです。OTCQB上場と量子ソフトテーマは支えですが、売上化と上位市場再上場はまだ確認待ちです。",
        "BAND_POSITION": f"{BAND_POSITION:.1f}%",
        "ZONE_JUDGE": "悲観寄りの中立圏",
        "ZONE_NOTE": "商業契約や再上場が見えれば標準側へ、資金調達や需給悪化が出れば悲観側へ寄ります。",
        "BEAR_PRICE": usd(BEAR),
        "BULL_PRICE": usd(BULL),
        "ENDPOINT_RR": f"{endpoint_rr:.1f}倍",
        "MARKET_SCORE": str(round(BAND_POSITION)),
        "OWN_SCORE": str(round(own_score)),
        "MARKET_REVERSE_NOTE": "このモデルで逆算すると、市場は量子テーマとNVIDIA材料を評価しつつ、OTC流動性、売上未確立、追加希薄化を強く割り引いています。",
        "SCENARIOS_LEAD": "現在株価から独立して、商業契約、政府プログラム、再上場、資金調達、流動性リスクを置きました。",
        "BEAR_PROB": "35%",
        "BASE_PROB": "45%",
        "BULL_PROB": "20%",
        "BEAR_DELTA": pct(BEAR / P0 - 1),
        "BULL_DELTA": pct(BULL / P0 - 1),
        "BEAR_DL_ROWS": dl([("契約", "進展限定"), ("資金", "追加希薄化"), ("市場", "OTC流動性低下"), ("株価", usd(BEAR))]),
        "BASE_DL_ROWS": dl([("契約", "小型案件が見える"), ("提携", "NVIDIA材料継続"), ("市場", "OTCQBで認知改善"), ("株価", usd(BASE))]),
        "BULL_DL_ROWS": dl([("契約", "商業転換"), ("政府", "大型プログラム"), ("市場", "Nasdaq/NYSE再上場期待"), ("株価", usd(BULL))]),
        "PRICE_ZONE_ROWS": '<div class="zone"><div><b>$0.30未満</b><span>★★★</span></div><p>資金・需給・流動性悪化を強く織り込む価格帯です。</p></div><div class="zone"><div><b>$0.30〜$1.20</b><span>★★★</span></div><p>再建後の材料待ち。今の株価はここです。</p></div><div class="zone"><div><b>$1.20〜$2.35</b><span>★★</span></div><p>契約や再上場期待を評価し始める価格帯です。</p></div><div class="zone"><div><b>$2.35超</b><span>★</span></div><p>商業契約と上位市場再上場の具体化が必要です。</p></div>',
        "SIGNAL_ROWS": '<div class="signal"><div><b>商業契約</b><span class="up">最重要</span></div><p>量子ソフトの売上化を確認します。</p></div><div class="signal"><div><b>NVIDIA連携</b><span class="up">材料</span></div><p>共同開発が製品・契約に進むかを確認します。</p></div><div class="signal"><div><b>上位市場再上場</b><span class="up">上値</span></div><p>Nasdaq/NYSE再上場の進捗を確認します。</p></div><div class="signal"><div><b>希薄化</b><span class="down">注意</span></div><p>登録株式売却や追加資金調達を確認します。</p></div>',
        "POSITIVES": "<li>量子ソフト専業に近い希少な公開企業です。</li><li>NVIDIA連携、DARPA実績、60件超の知財があります。</li><li>OTCQB上場で投資家認知と流動性改善の余地があります。</li><li>量子テーマの注目が高まると株価感応度が大きいです。</li>",
        "CONCERNS": "<li>OTC銘柄で流動性とスプレッドのリスクが大きいです。</li><li>売上・契約の継続性はまだ確認が必要です。</li><li>追加増資や登録株式売却による需給悪化に注意です。</li><li>テーマ先行で実績が追いつかない場合、下落が大きくなります。</li>",
        "FORMULA": "OTC超小型のテーマ株のため、利益倍率ではなく、商業契約、再上場、資金余力、流動性リスクを反映した3点シナリオで見ました。",
        "CALC_TABLE_HEAD": th("ケース", "主な前提", "価値の見方", "計算株価", "確率", "確率加重"),
        "CALC_TABLE_ROWS": tr("悲観", "契約進展なし", "現金・知財を低く評価", usd(BEAR), "35%", "$0.105") + tr("標準", "小型案件と認知改善", "OTCQB後の再評価", usd(BASE), "45%", "$0.540") + tr("楽観", "商業転換・再上場期待", "量子ソフト銘柄として評価", usd(BULL), "20%", "$0.470"),
        "CALC_NOTICE": "現在株価に合わせた逆算ではありません。OTC銘柄のため、売買高と需給で短期価格は大きく振れます。",
        "CONDITIONS": details("悲観ケース：$0.30 / 確率35%", "商業契約や政府案件が見えず、追加希薄化や売却圧力で需給が悪化するケースです。", True) + details("標準ケース：$1.20 / 確率45%", "NVIDIA連携やOTCQB上場の認知改善に加え、小型契約や研究案件が見えるケースです。") + details("楽観ケース：$2.35 / 確率20%", "商業契約、政府プログラム、上位市場再上場期待が重なり、52週高値圏を試すケースです。"),
        "SENSITIVITY_HEAD": th("前提", "弱い", "標準", "強い"),
        "SENSITIVITY_ROWS": tr("契約転換", "なし → $0.30", "小型案件 → $1.20", "大型案件 → $2.35") + tr("市場", "OTC流動性低下", "OTCQBで安定", "Nasdaq/NYSE期待") + tr("資金", "希薄化懸念", "当面の運転資金", "非希薄化資金・契約収入"),
        "SENSITIVITY_NOTE": "OTC銘柄では、事業材料だけでなく売買高と株式需給が同時に株価を動かします。",
        "DIST_LEAD": "モンテカルロではなく、再建後のイベント3点分布です。",
        "DIST_ROWS": '<div class="dist-row"><span>$0.30</span><div class="track"><i style="width:35%"></i></div><b>35%</b></div><div class="dist-row"><span>$1.20</span><div class="track"><i style="width:45%"></i></div><b>45%</b></div><div class="dist-row"><span>$2.35</span><div class="track"><i style="width:20%"></i></div><b>20%</b></div>',
        "DIST_SUMMARY": "期待値は標準ケース付近ですが、流動性が薄いため短期株価は大きく上下しやすいです。",
        "WATCH_ROWS": '<div class="signal"><div><b>商業契約</b></div><p>企業・政府との契約転換や金額を確認します。</p></div><div class="signal"><div><b>上位市場再上場</b></div><p>Nasdaq/NYSEの初期上場基準を満たす進捗を確認します。</p></div><div class="signal"><div><b>資金調達</b></div><p>追加増資、登録株式売却、運転資金を確認します。</p></div>',
        "ASSUMPTIONS_ROWS": tr("評価基準株価", usd(P0), "市場データで確認", DATE, "2026/08/07終値") + tr("時価総額", f"${MARKET_CAP_M:.1f}M", "株価・株式数から計算", DATE, "概算") + tr("OTCQB上場", "2026/06/16", "会社リリース", "2026/06/16", "ZPTA") + tr("戦略的資金調達", "$15M", "会社リリース", "2026/04/23", "再建後の成長資金"),
        "DEEPDIVE_DETAILS": details("手法選定理由", "ZPTAはOTCの超小型テーマ株です。PERよりも、契約転換、再上場、資金余力、需給を反映したシナリオ法が自然です。", True) + details("ティッカーについて", "ユーザー入力はZATAでしたが、公式FAQとOTCQBリリースでは普通株はZPTAと確認できます。") + details("主要出典", f'{source_link("公式IR概要", "overview")}、{source_link("投資家向け資料", "presentation")}、{source_link("OTCQB上場", "otcqb")}、{source_link("NVIDIA連携", "nvidia")}、{source_link("株価・統計", "quote")}。<br><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>'),
        "DISCLAIMER": "本資料は情報提供を目的とした試算です。投資助言ではありません。OTC超小型株は流動性、需給、資金調達で大きく変動します。",
        "FOOTER_NOTE": f"SiM MARKET LAB｜{COMPANY}（{TICKER}）株価シナリオ｜作成日 {DATE}",
    }


def catalyst_values() -> dict[str, str]:
    non_quant = '<div class="priced"><div class="priced-head"><span>主要材料の推定織り込み</span><b>36%</b></div><p>仮定：OTCQB上場後の認知改善を45%、NVIDIA連携期待を40%、商業契約転換を25%、Nasdaq/NYSE再上場期待を20%として置き、OTC流動性と希薄化リスクを控除しました。</p><p>読み方：株価は量子テーマとNVIDIA材料を一部織り込んでいますが、契約・売上・再上場はまだ半分未満の織り込みです。</p><p>次に見る数字：売買高、商業契約、政府プログラム、資金残高、登録株式売却、上位市場の進捗です。</p><p>再計算方法：各材料の成功確率を更新し、レポート2のシナリオ株価を再計算します。</p></div>'
    impact_map = {
        "商業契約・政府プログラム": ("+45〜120%", "-15〜+25%", "-35〜-65%", "売上化の証拠が出るかどうかで、テーマ株から事業株へ評価が変わるため最大レンジにしています。"),
        "NVIDIA連携の進捗": ("+25〜70%", "-8〜+18%", "-18〜-35%", "話題性は高い一方、短期売上化まで距離があるため契約材料より少し小さくしています。"),
        "Nasdaq/NYSE再上場への進捗": ("+35〜90%", "-10〜+20%", "-25〜-50%", "OTC銘柄の流動性ディスカウントが外れる可能性があるため大きめです。"),
        "資金調達・登録株式の需給": ("+12〜30%", "-8〜+8%", "-30〜-60%", "事業価値よりも株式需給に直接効くため、下落側のレンジを大きくしています。"),
    }
    description_map = {
        "商業契約・政府プログラム": "量子ソフトウェアが実際の売上や政府資金に変わるかを確認する材料です。ZPTAにとって、技術力の説明よりも契約転換の証拠が重要です。",
        "NVIDIA連携の進捗": "Agentic AIで量子アルゴリズム開発を加速する取り組みです。共同研究から製品化、顧客導入、売上化へ進むかを見ます。",
        "Nasdaq/NYSE再上場への進捗": "OTCQBから上位市場へ戻れるかは、流動性、機関投資家アクセス、バリュエーションに直結します。",
        "資金調達・登録株式の需給": "OTC超小型株では、追加増資や売却株式の需給が短期株価に強く影響します。資金が必要な成長企業ほど希薄化確認が重要です。",
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
<div class="evidence"><div><h4>根拠</h4><ul>{evidence}</ul></div><div><h4>反証・先行指標</h4><ul><li>売買高が細る</li><li>契約金額が開示されない</li><li>登録株式の売却圧力が強い</li></ul></div></div>
</article>'''

    cards = [
        card("商業契約・政府プログラム", "2026年後半", '<span class="chip">重要度5</span><span class="chip">最重要</span>', '<span>契約</span><i>→</i><span>売上化</span><i>→</i><span>評価</span>', "大型契約や政府プログラムが具体化し、金額や継続性が見える状態です。", "小型案件や実証が増え、売上化の方向は見える状態です。", "契約転換が遅れ、テーマ先行の評価に戻る状態です。", "<li>投資家向け資料では商業転換と政府プログラムを近い材料として提示。</li><li>DARPA実績と高価値ドメインでの用途を説明しています。</li>"),
        card("NVIDIA連携の進捗", "2026/06/23発表", '<span class="chip">重要度4</span><span class="chip blue">提携</span>', '<span>AI連携</span><i>→</i><span>製品化</span><i>→</i><span>顧客導入</span>', "共同開発が製品や顧客案件に進み、売上化の道筋が見える状態です。", "研究・開発協力として認知材料が続く状態です。", "追加進捗がなく、話題性だけで終わる状態です。", "<li>会社はNVIDIAとAgentic AIで量子アルゴリズム開発を加速すると発表。</li><li>投資家向け資料でも主要材料として扱われています。</li>"),
        card("Nasdaq/NYSE再上場への進捗", "未定", '<span class="chip">重要度4</span><span class="chip blue">市場</span>', '<span>基準達成</span><i>→</i><span>再上場期待</span><i>→</i><span>流動性</span>', "上位市場の要件達成や申請方針が明確になり、流動性改善期待が高まる状態です。", "OTCQB上場後の認知改善が続く状態です。", "再上場条件が遠く、OTCディスカウントが残る状態です。", "<li>OTCQB上場リリースで、上位市場上場を目標にする姿勢が示されています。</li><li>投資家向け資料でもNasdaq/NYSEアップリスティングが材料として記載されています。</li>"),
        card("資金調達・登録株式の需給", "継続確認", '<span class="chip">重要度5</span><span class="chip blue">需給</span>', '<span>資金</span><i>→</i><span>希薄化</span><i>→</i><span>株価</span>', "非希薄化資金や契約収入で運転資金懸念が下がる状態です。", "必要資金はあるが、追加希薄化懸念も残る状態です。", "増資や売却圧力が強まり、株価需給が悪化する状態です。", "<li>2026年4月に$15Mの戦略的資金調達を完了。</li><li>S-1では売却株主による株式登録が確認できます。</li>"),
    ]
    return {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "OTCQB",
        "VALUATION_DATE": DATE,
        "LAST_UPDATED": DATE,
        "REPORT_STATUS": "再建後の材料待ち",
        "SUMMARY_LINE_1": "商業契約、NVIDIA連携、上位市場再上場、資金・需給が主な材料です。",
        "SUMMARY_LINE_2": "足りない情報は仮定を置き、主要材料の織り込み度を36%と推定します。",
        "OVERALL_PRICED_IN": "36%",
        "OVERALL_PRICED_LABEL": "主要材料の推定織り込み",
        "PRICED_IN_CONFIDENCE": "低",
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "2026/08/07終値",
        "NEXT_CATALYST_TITLE": "商業契約・政府プログラム",
        "NEXT_CATALYST_WINDOW": "2026年後半",
        "DATE_CONFIDENCE": "会社資料の重点項目",
        "CATALYST_COUNT": "4件",
        "WARN_BAND": "",
        "NO_CATALYST_NOTICE": "",
        "OVERALL_PRICED_BLOCK": non_quant,
        "PRICED_IN_METHOD": "未確定情報に仮定確率を置き、商業契約、NVIDIA連携、再上場、資金需給を標準ケース価値へ重み付けして推定。",
        "SURPRISE_UP": "契約金額のある商業案件、政府プログラム、NVIDIA連携の製品化、上位市場再上場の具体化です。",
        "SURPRISE_DOWN": "追加希薄化、登録株式売却、売買高低下、契約転換の遅れです。",
        "PRIMARY_RISK": "OTC超小型株のため、事業材料が良くても流動性や株式需給で株価が大きく下がる可能性があることです。",
        "TIMELINE_ROWS": '<div class="time-row"><div class="time-date">2026/04/23</div><div class="time-dot"></div><div class="time-body"><b>$15M戦略的資金調達</b><p>再建後の成長資金を確保。</p><div class="time-meta"><span class="chip">資金</span></div></div></div><div class="time-row"><div class="time-date">2026/06/16</div><div class="time-dot"></div><div class="time-body"><b>OTCQB上場</b><p>市場認知と流動性改善への一歩。</p><div class="time-meta"><span class="chip blue">市場</span></div></div></div><div class="time-row"><div class="time-date">2026/06/23</div><div class="time-dot"></div><div class="time-body"><b>NVIDIA連携</b><p>Agentic AIを量子アルゴリズム開発へ応用。</p><div class="time-meta"><span class="chip">提携</span></div></div></div><div class="time-row"><div class="time-date">2026/07/13</div><div class="time-dot"></div><div class="time-body"><b>投資家向け資料</b><p>商業転換、再上場、政府案件をカタリストとして提示。</p><div class="time-meta"><span class="chip">認知</span></div></div></div>',
        "CATALYST_CARDS": "".join(cards) + '<p class="small">※下の％は、この結果が出た後に市場が材料を評価し直した場合の上昇・下落幅の目安です。実際の値動きは地合い、直前の株価上昇、同時ニュースで変わります。</p>',
        "DEPENDENCY_ROWS": '<div class="signal"><div><b>契約と資金</b><span class="up">連動</span></div><p>契約収入が見えるほど追加希薄化懸念が下がります。</p></div><div class="signal"><div><b>再上場と流動性</b><span class="flat">市場</span></div><p>上位市場に近づくほどOTCディスカウントが縮小します。</p></div><div class="signal"><div><b>NVIDIAと商業化</b><span class="up">変換</span></div><p>話題性から製品・契約へ進むかが重要です。</p></div>',
        "WATCH_ROWS": '<div class="signal"><div><b>売買高</b><span class="flat">必須</span></div><p>OTC銘柄なので日々の流動性を確認します。</p></div><div class="signal"><div><b>契約金額</b><span class="up">重要</span></div><p>商業契約や政府案件の金額・期間を確認します。</p></div><div class="signal"><div><b>株式需給</b><span class="down">注意</span></div><p>登録株式、増資、売却圧力を確認します。</p></div><div class="signal"><div><b>再上場基準</b><span class="up">上値</span></div><p>株価、時価総額、株主数などの条件を確認します。</p></div>',
        "ASSUMPTION_ROWS": tr("評価基準株価", usd(P0), "市場データで確認", DATE, "2026/08/07終値") + tr("時価総額", f"${MARKET_CAP_M:.1f}M", "株価・株式数から計算", DATE, "概算") + tr("OTCQB上場", "2026/06/16", "会社リリース", "2026/06/16", "ZPTA") + tr("NVIDIA連携", "2026/06/23", "会社リリース", "2026/06/23", "Agentic AI"),
        "SOURCE_DETAILS": f'<ul><li>{source_link("公式IR概要", "overview")}</li><li>{source_link("投資家向け資料", "presentation")}</li><li>{source_link("OTCQB上場リリース", "otcqb")}</li><li>{source_link("NVIDIA連携リリース", "nvidia")}</li><li>{source_link("株価・統計", "quote")}</li><li>{source_link("SEC S-1", "sec_s1")}</li></ul><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p>',
        "VALIDATION_DETAILS": "<p>PASS：公式IR、投資家向け資料、OTCQB上場リリース、NVIDIA連携リリース、SEC S-1、株価・統計ページを確認。WARN：ユーザー入力はZATAでしたが、公式FAQと会社リリースでは普通株ティッカーはZPTAです。OTC銘柄のため株価更新は取得元の制限を受ける可能性があります。</p>",
        "UPDATE_HISTORY": f"<p>{DATE}：初版作成。ZPTAとして追加。OTCQB上場、NVIDIA連携、$15M資金調達、投資家向け資料を反映。</p>",
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
        "id": "zapata-zpta",
        "order": 9,
        "ticker": "ZPTA",
        "quoteSymbol": "ZPTA",
        "name": "ザパタ・クオンタム",
        "nameEn": "Zapata Quantum, Inc.",
        "market": "US",
        "marketLabel": "米国株",
        "exchange": "OTCQB",
        "currency": "USD",
        "sector": "量子ソフトウェア・先端AI",
        "reports": {
            "company": {"path": "./stocks/zapata-zpta/company.html", "available": True},
            "valuation": {"path": "./stocks/zapata-zpta/valuation.html", "available": True},
            "catalysts": {"path": "./stocks/zapata-zpta/catalysts.html", "available": True},
        },
    }
    stocks_payload["stocks"] = [item for item in stocks_payload["stocks"] if item["id"] != "zapata-zpta"]
    stocks_payload["stocks"].append(stock)
    stocks_payload["stocks"].sort(key=lambda item: item["order"])
    stocks_path.write_text(json.dumps(stocks_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    prices_path = ROOT / "data" / "prices.json"
    prices_payload = json.loads(prices_path.read_text(encoding="utf-8"))
    prices_payload.setdefault("prices", {})["zapata-zpta"] = {
        "symbol": "ZPTA",
        "price": P0,
        "previousClose": PREVIOUS_CLOSE,
        "change": round(P0 - PREVIOUS_CLOSE, 4),
        "changePct": round((P0 - PREVIOUS_CLOSE) / PREVIOUS_CLOSE * 100, 4),
        "currency": "USD",
        "marketTime": "2026-08-07T20:00:00+00:00",
        "updatedAt": "2026-08-11T00:00:00+00:00",
        "status": "ok",
    }
    prices_payload["quoteCount"] = len(prices_payload["prices"])
    prices_path.write_text(json.dumps(prices_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    signals_path = ROOT / "data" / "signals.json"
    signals_payload = json.loads(signals_path.read_text(encoding="utf-8"))
    signals_payload["updatedAt"] = datetime.now(timezone.utc).isoformat()
    signals_payload.setdefault("signals", {})["zapata-zpta"] = {
        "position": SIGNAL_POSITION,
        "zone": "中立",
        "asOf": DATE,
        "components": {
            "valuation": round(BAND_POSITION, 1),
            "catalysts": 70.0,
            "businessRisk": 88.0,
        },
        "reportRevision": "zapata-zpta-2026-08-11",
        "summary": "OTCQB上場、NVIDIA連携、量子ソフトテーマは材料。ただしOTC流動性、売上未確立、希薄化リスクが極めて高いため中立。",
    }
    signals_path.write_text(json.dumps(signals_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_reports()
    upsert_site_data()


if __name__ == "__main__":
    main()
