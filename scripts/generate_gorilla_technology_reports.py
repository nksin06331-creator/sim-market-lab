"""Generate Gorilla Technology Group report HTML files from the SiM templates."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATERIALS = ROOT.parent / "report-generation-materials"
OUT_DIR = ROOT / "stocks" / "gorilla-technology-grrr"

COMPANY = "ゴリラ・テクノロジー・グループ"
TICKER = "GRRR"
DATE = "2026-10-03"
P0 = 13.17
PREVIOUS_CLOSE = 13.58
SHARES_M = 27.51
FULLY_DILUTED_M = 38.4
MARKET_CAP_B = P0 * SHARES_M / 1000

BEAR = 8.00
BASE = 20.00
BULL = 32.00
PROBS = {"bear": 0.30, "base": 0.50, "bull": 0.20}
BAND_POSITION = max(0.0, min(100.0, (P0 - BEAR) / (BULL - BEAR) * 100))
CATALYST_SCORE = 45.0
BUSINESS_RISK_SCORE = 78.0
SIGNAL_POSITION = round(0.60 * BAND_POSITION + 0.25 * CATALYST_SCORE + 0.15 * BUSINESS_RISK_SCORE, 1)

SOURCES = {
    "ir": "https://investors.gorilla-technology.com/",
    "h1": "https://investors.gorilla-technology.com/gorilla-technology-h1-revenue-surges-99-to-us78-4-million-raises-fy2026-revenue-outlook-to-at-least-us200-million/",
    "h1_sec": "https://www.sec.gov/Archives/edgar/data/1903145/000143774926028827/ex_974013.htm",
    "june_notes": "https://www.sec.gov/Archives/edgar/data/1903145/000121390026065898/ea0293736-6k_gorilla.htm",
    "july_notes": "https://www.sec.gov/Archives/edgar/data/1903145/000121390026079193/ea0298371-6k_gorilla.htm",
    "yotta": "https://investors.gorilla-technology.com/gorilla-technology-yotta-expand-india-ai-infrastructure-collaboration-in-project-valued-at-approximately-us2-8-billion/",
    "batam": "https://investors.gorilla-technology.com/gorilla-technology-secures-transformational-us2-5-billion-five-year-ai-gpuaas-compute-contract-converting-ai-data-centre-capacity-into-long-term-contracted-revenue/",
    "taiwan": "https://investors.gorilla-technology.com/gorilla-technology-wins-major-national-ai-intelligence-infrastructure-expansion-in-taiwan/",
    "quote": "https://stockanalysis.com/stocks/grrr/",
}


def tr(*cells: str) -> str:
    return "<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>"


def li(text: str, emoji: str = "*") -> str:
    return f'<li data-emoji="{emoji}">{text}</li>'


def dl(rows: list[tuple[str, str]]) -> str:
    return "".join(f"<div><dt>{label}</dt><dd>{value}</dd></div>" for label, value in rows)


def th(*cells: str) -> str:
    return "".join(f"<th>{cell}</th>" for cell in cells)


def render_template(name: str, values: dict[str, str]) -> str:
    template = (MATERIALS / name).read_text(encoding="utf-8")
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    template = re.sub(r"<!--.*?-->", "", template, flags=re.S)
    template = re.sub(r"/\*.*?\*/", "", template, flags=re.S)
    template = template.replace("{{ }}", "プレースホルダー")
    template = template.replace("ドパガキ株価シナリオ", "株価シナリオ")
    leftovers = sorted(set(re.findall(r"{{[A-Z0-9_]+}}", template)))
    if leftovers:
        raise RuntimeError(f"{name}: unresolved placeholders: {leftovers}")
    return template


def usd(value: int | float) -> str:
    return f"${value:,.2f}" if abs(value) < 100 else f"${value:,.0f}"


def pct(value: float) -> str:
    return f"{value * 100:+.1f}%"


def details(title: str, body: str, open_: bool = False) -> str:
    return f"<details{' open' if open_ else ''}><summary>{title}</summary><p>{body}</p></details>"


def source_link(label: str, key: str) -> str:
    return f'<a href="{SOURCES[key]}" target="_blank" rel="noopener noreferrer">{label}</a>'


def guide_values() -> dict[str, str]:
    terms = [
        ("AIインフラ", "GPU、ネットワーク、データセンター、運用ソフトを組み合わせ、AIの計算基盤を導入・運用する事業です。"),
        ("GPUaaS", "GPU as a Serviceです。GPU計算資源を顧客がサービスとして利用します。"),
        ("Yotta", "インドのデータセンター事業者です。GRRRはGPU基盤の大型導入を進めています。"),
        ("NeutraDC Batam", "インドネシアのAIデータセンター拠点で、GPUaaS案件の導入先です。"),
        ("契約資産", "作業は進んだものの、請求条件へ到達していない金額です。現金回収とは別に確認します。"),
        ("調整後EBITDA", "株式報酬や一時費用を除いた指標です。IFRS営業損益と並べて見ます。"),
        ("転換社債", "条件を満たすと株式へ転換できる社債です。成長資金になる一方、1株価値の希薄化要因になります。"),
        ("ソブリンAI", "政府や国内機関が自国で管理するAI基盤です。安全保障とデータ主権が重視されます。"),
    ]
    source_details = (
        '<details class="term-item" open><summary class="term-header"><span class="term-name">主要出典</span><span class="term-arrow">⌄</span></summary><div class="term-body"><p>'
        f'{source_link("2026年上期決算", "h1")}、{source_link("2026年上期SEC提出資料", "h1_sec")}、'
        f'{source_link("Yotta案件", "yotta")}、{source_link("Batam GPUaaS案件", "batam")}、{source_link("台湾案件", "taiwan")}を確認しました。'
        "本文は2026年10月3日時点の公開情報に基づきます。</p><p><a href=\"../../index.html\">SiM MARKET LABの銘柄一覧へ戻る</a></p></div></details>"
    )
    return {
        "TICKER": TICKER,
        "COMPANY_NAME": COMPANY,
        "INDUSTRY": "AIインフラ・スマートシティ・セキュリティ",
        "DATE": DATE,
        "TAGLINE": "政府・大企業向けに、AI計算基盤、データセンター、映像解析、サイバーセキュリティを組み合わせて提供する企業です。",
        "HERO_TAGS": '<span class="hero-tag">米国株</span><span class="hero-tag">AIインフラ</span><span class="hero-tag">スマートシティ</span><span class="hero-tag">Nasdaq</span>',
        "HERO_STATS": (
            f'<div class="stat"><div class="stat-value">{usd(P0)}</div><div class="stat-label">評価基準株価</div><div class="stat-note">2026/10/02終値</div></div>'
            f'<div class="stat"><div class="stat-value">${MARKET_CAP_B:.2f}B</div><div class="stat-label">時価総額の目安</div><div class="stat-note">現在株式数で計算</div></div>'
            '<div class="stat"><div class="stat-value up">$78.4M</div><div class="stat-label">2026年上期売上</div><div class="stat-note">前年同期比+99%</div></div>'
            '<div class="stat"><div class="stat-value">$179.4M</div><div class="stat-label">6月末現金</div><div class="stat-note">転換社債調達後</div></div>'
        ),
        "SEC2_LABEL": "事業モデル", "SEC3_LABEL": "AIインフラ", "SEC4_LABEL": "決算と資金", "SEC5_LABEL": "競合比較",
        "SEC1_TLDR": li("GRRRはAIデータセンターと政府向けセキュリティを両方手掛けます。") + li("2026年上期売上は$78.4Mで、前年同期比99%増でした。") + li("大型契約の総額と実際の売上・回収は分けて見ます。", "!"),
        "SEC1_FACTS": "<div><dt>正式社名</dt><dd>Gorilla Technology Group Inc.</dd></div><div><dt>主要拠点</dt><dd>ロンドン・台北</dd></div><div><dt>上場</dt><dd>Nasdaq（GRRR）</dd></div><div><dt>設立</dt><dd>2001年</dd></div><div><dt>CEO</dt><dd>Jayesh Chandan</dd></div><div><dt>決算期</dt><dd>12月期</dd></div>",
        "SEC1_CARDS": '<div class="card-sm"><span class="card-emoji">AI</span><div class="card-title">AIインフラ</div><div class="card-desc">GPU、ネットワーク、データセンター運用を提供。</div></div><div class="card-sm"><span class="card-emoji">SI</span><div class="card-title">セキュリティ</div><div class="card-desc">政府向け映像解析・ネットワーク分析。</div></div><div class="card-sm"><span class="card-emoji">99%</span><div class="card-title">高成長</div><div class="card-desc">上期売上は前年同期比99%増。</div></div><div class="card-sm"><span class="card-emoji">!</span><div class="card-title">注意</div><div class="card-desc">赤字、大型設備投資、転換社債、回収リスク。</div></div>',
        "SEC1_BIZMODEL": '<li><span class="kp-emoji">AI</span><span class="kp-text"><b>AI計算基盤</b>：GPU調達、設置、運用、ワークロード提供まで手掛けます。</span></li><li><span class="kp-emoji">SI</span><span class="kp-text"><b>政府・安全保障</b>：映像、捜査、サイバー、ネットワーク分析を提供します。</span></li><li><span class="kp-emoji">DC</span><span class="kp-text"><b>長期契約</b>：設備導入から複数年の利用料・運用収入へつなげるモデルです。</span></li>',
        "SEC1_HIGHLIGHT": '<div class="highlight"><h3>GRRRを見る基本ルール</h3><p>プレスリリースの契約総額ではなく、四半期売上、粗利、調整後EBITDA、営業キャッシュフロー、契約資産の回収を確認します。</p></div>',
        "SEC2_ICON": "AI", "SEC2_TITLE": "何で稼ぐかを<span class=\"g\">分ける</span>", "SEC2_SUB": "大型機器販売と継続収益は別物",
        "SEC2_TLDR": li("GPU機器の調達・導入は売上が大きくても利益率に注意が必要です。") + li("GPUaaSと運用収入が増えると継続収益性が高まります。") + li("大型契約は資金調達、納入、稼働率、回収まで確認します。", "!"),
        "SEC2_CONTENT": '<p class="lead">GRRRはソフトウェア会社というより、AIインフラの導入と運用をまとめるプロジェクト企業に近い構造です。</p><div class="sowhat"><p><b>つまり</b>、契約額が大きいほど運転資金と実行管理も重くなります。</p></div><div class="term-list">' + details("AIインフラ", "YottaやBatamでGPU基盤を導入し、計算資源と運用を提供します。", True) + details("セキュリティインテリジェンス", "台湾、タイ、エジプトなどで政府・公共機関向け案件を展開します。") + details("売上認識", "機器の納入や進捗条件に応じて売上が認識され、四半期ごとの変動が大きくなります。") + details("現金回収", "売上認識後も請求・入金まで時間がかかることがあります。") + "</div>",
        "SEC3_TITLE": "アジアの<span class=\"g\">AI基盤</span>", "SEC3_SUB": "YottaとBatamが中心",
        "SEC3_TLDR": li("YottaではB200/B300 GPUの大規模導入を進めています。") + li("Batamでは5年間のGPUaaS契約を導入する計画です。") + li("9月30日までのYotta追加納入は、完了の公式確認待ちです。", "!"),
        "SEC3_CONTENT": '<div class="product-grid"><div class="product-box"><div class="product-symbol">YT</div><div class="product-name">Yotta</div><div class="product-use">インドのソブリンAI基盤。</div></div><div class="product-box"><div class="product-symbol">BT</div><div class="product-name">Batam</div><div class="product-use">インドネシアのGPUaaS。</div></div><div class="product-box"><div class="product-symbol">TW</div><div class="product-name">Taiwan</div><div class="product-use">捜査・知能分析基盤。</div></div></div><div class="term-list">' + details("Yotta", "2026年9月8日にサイト準備、電力、冷却、ステージングが進んでいると発表されました。", True) + details("Batam", "初期約1,000台のB300 GPUサーバー導入と、複数年の計算サービス収入を計画しています。") + details("台湾案件", "2026年9月22日、既存政府顧客向けの複数年拡張契約を発表しました。") + details("見る順番", "納入完了、設備稼働、顧客利用、売上認識、現金回収の順で確認します。") + "</div>",
        "SEC4_TITLE": "高成長と<span class=\"g\">負債</span>", "SEC4_SUB": "現金は多いが調達資金",
        "SEC4_TLDR": li("2026年上期売上は$78.4M、営業キャッシュ流出は$4.3Mでした。") + li("会社は2026年通期売上を最低$200M、2027年を$450M〜$500Mと計画しています。") + li("調整後EBITDAは赤字で、転換社債の金利・返済・希薄化に注意が必要です。", "!"),
        "SEC4_CONTENT": '<ul class="keypoints"><li><span class="kp-emoji">99%</span><span class="kp-text"><b>売上</b>：上期$78.4M、前年同期比+99.3%。</span></li><li><span class="kp-emoji">-</span><span class="kp-text"><b>利益</b>：調整後EBITDAは$14.6Mの赤字。</span></li><li><span class="kp-emoji">$</span><span class="kp-text"><b>資金</b>：6月と7月の転換社債元本は合計$232M、年利7.5%。</span></li></ul><div class="sowhat"><p><b>つまり</b>、目先の資金余力はありますが、プロジェクトが利益と現金に変わらないと重い負債が残ります。</p></div>',
        "SEC5_TITLE": "競合と<span class=\"g\">差別化</span>", "SEC5_SUB": "単純なAIソフト株ではない",
        "SEC5_TLDR": li("PalantirやBigBear.aiと政府AIで比較されます。") + li("SupermicroやHPEとは機器統合・AI基盤で重なる部分があります。") + li("小さい企業で大型案件を同時実行する管理能力が最大の評価点です。", "!"),
        "SEC5_CONTENT": '<div class="table-wrap"><table class="compare-table"><thead><tr><th>対象</th><th>強み</th><th>注意点</th></tr></thead><tbody><tr><td class="me">Gorilla</td><td>政府AIとデータセンターを一体提供。</td><td>資金集約・契約回収・希薄化。</td></tr><tr><td>Palantir</td><td>政府・企業向けAIソフトと収益性。</td><td>企業規模とビジネスモデルが異なる。</td></tr><tr><td>BigBear.ai</td><td>政府・防衛向けAI分析。</td><td>データセンター資産の比重が異なる。</td></tr><tr><td>Supermicro / HPE</td><td>AIサーバー、調達力、顧客基盤。</td><td>GRRRは地域案件統合と運用を担う。</td></tr></tbody></table></div><div class="highlight"><h3>差別化の見方</h3><p>機器販売で終わらず、長期GPUaaS、セキュリティ分析、運用支援へ収入を広げられるかが重要です。</p></div>',
        "SEC6_TLDR": li("GPUaaS、Yotta、Batam、契約資産、転換社債を押さえると読みやすいです。") + li("契約額と年間売上は同じではありません。") + li("納入完了と現金回収が信頼度を上げます。", "!"),
        "SEC6_CONTENT": '<div class="term-list">' + "".join(details(name, body) for name, body in terms) + "</div>",
        "SEC7_TLDR": li("最大材料はYotta納入とBatam初期導入の完了確認です。") + li("Q3売上$48M〜$50Mと通期$200M以上の達成度を見ます。") + li("契約資産の増加、支払い遅延、転換社債利払いに注意します。", "!"),
        "SEC7_CONTENT": '<div class="timeline"><div class="tl-row"><div class="tl-date">2026/09/08</div><div class="tl-title">Yotta物理導入段階 <span class="signal bull">進行中</span></div><div class="tl-desc">サイト準備、電力、冷却、機器ステージングを実行。</div></div><div class="tl-row"><div class="tl-date">2026/09/22</div><div class="tl-title">台湾政府案件 <span class="signal bull">受注</span></div><div class="tl-desc">数千万ドル規模の複数年拡張契約。</div></div><div class="tl-row"><div class="tl-date">2026年秋</div><div class="tl-title">Q3進捗確認 <span class="signal neutral">最重要</span></div><div class="tl-desc">売上$48M〜$50M、粗利、現金回収を確認。</div></div><div class="tl-row"><div class="tl-date">2026/12</div><div class="tl-title">Batam第2トランシェ <span class="signal neutral">計画</span></div><div class="tl-desc">GPUaaS設備の納入と顧客利用開始を確認。</div></div></div><div class="info-row"><div class="info-box info-box-green"><div class="info-title info-title-green">追い風</div><div class="info-text">AI計算需要、政府案件、大型長期契約。</div></div><div class="info-box info-box-amber"><div class="info-title info-title-amber">確認</div><div class="info-text">納入、稼働率、粗利、契約資産の回収。</div></div><div class="info-box info-box-red"><div class="info-title info-title-red">リスク</div><div class="info-text">赤字、実行遅延、転換社債、顧客集中。</div></div></div>' + source_details,
    }


def scenario_values() -> dict[str, str]:
    expected = BEAR * PROBS["bear"] + BASE * PROBS["base"] + BULL * PROBS["bull"]
    own_score = (expected - BEAR) / (BULL - BEAR) * 100
    endpoint_rr = (BULL - P0) / (P0 - BEAR)
    score = round(max(0, min(100, 50 + (expected / P0 - 1) * 100 - PROBS["bear"] * ((P0 - BEAR) / P0) * 100)))
    return {
        "COMPANY_NAME": COMPANY, "TICKER": TICKER, "EXCHANGE": "Nasdaq", "VALUATION_DATE": DATE,
        "METHOD": "AIインフラ・プロジェクト企業向けEV/Sシナリオ",
        "VERDICT_STATUS": "成長余地と実行リスクが併存",
        "VERDICT_LINE_1": f"評価基準株価は悲観〜楽観レンジの{BAND_POSITION:.1f}%地点です。大型AI契約は上値材料ですが、納入・利益・回収の確認前です。",
        "VERDICT_LINE_2": "転換社債込み約3,840万株の潜在希薄化株式数を強気側の評価に反映し、契約総額をそのまま企業価値にしていません。",
        "SCORE": str(score), "CURRENT_PRICE": usd(P0), "CURRENT_PRICE_NOTE": "2026/10/02終値",
        "BASE_PRICE": usd(BASE), "BASE_DELTA": pct(BASE / P0 - 1), "EXPECTED_VALUE": usd(expected), "EXPECTED_DELTA": pct(expected / P0 - 1),
        "RISK_CLASS": "高", "RISK_NOTE": "小型株、赤字、大型資本投下、転換社債、回収リスク",
        "WARN_BAND": "", "WARN_MESSAGE": "契約額の発表と実際の売上・利益・現金回収には時間差と実行リスクがあります。",
        "SNAPSHOT_LEAD": "今の株価は悲観ケースから標準ケースの間です。通期$200M達成と大型設備の稼働が確認できれば標準側へ近づきます。",
        "BAND_POSITION": f"{BAND_POSITION:.1f}%", "ZONE_JUDGE": "悲観〜標準の間", "ZONE_NOTE": "Q3とYotta/Batamの実行確認で標準側へ、遅延や追加調達で悲観側へ寄ります。",
        "BEAR_PRICE": usd(BEAR), "BULL_PRICE": usd(BULL), "ENDPOINT_RR": f"{endpoint_rr:.1f}倍", "MARKET_SCORE": str(round(BAND_POSITION)), "OWN_SCORE": str(round(own_score)),
        "MARKET_REVERSE_NOTE": "市場は2026年の増収を一部評価しつつ、2027年計画の実行と転換社債負担に大きな割引を置いていると見ます。",
        "SCENARIOS_LEAD": "現在株価から独立して、2027年売上、利益率、キャッシュ回収、転換社債、希薄化を置きました。",
        "BEAR_PROB": "30%", "BASE_PROB": "50%", "BULL_PROB": "20%", "BEAR_DELTA": pct(BEAR / P0 - 1), "BULL_DELTA": pct(BULL / P0 - 1),
        "BEAR_DL_ROWS": dl([("2027売上", "$250M前後"), ("実行", "遅延・低稼働"), ("資金", "負債負担が残る"), ("株価", usd(BEAR))]),
        "BASE_DL_ROWS": dl([("2027売上", "$450M前後"), ("実行", "Yotta/Batamを段階稼働"), ("利益", "EBITDA黒字化"), ("株価", usd(BASE))]),
        "BULL_DL_ROWS": dl([("2027売上", "$500M以上"), ("実行", "高稼働・追加案件"), ("資金", "回収改善・転換後も吸収"), ("株価", usd(BULL))]),
        "PRICE_ZONE_ROWS": '<div class="zone"><div><b>$8未満</b><span>★★</span></div><p>大型案件の遅延や資金負担を強く織り込む価格帯です。</p></div><div class="zone"><div><b>$8〜$20</b><span>★★★</span></div><p>実行確認待ちの価格帯で、今の株価はここです。</p></div><div class="zone"><div><b>$20〜$32</b><span>★★</span></div><p>2027年成長と黒字化を評価する価格帯です。</p></div><div class="zone"><div><b>$32超</b><span>★</span></div><p>複数案件の高稼働と希薄化吸収が必要です。</p></div>',
        "SIGNAL_ROWS": '<div class="signal"><div><b>売上成長</b><span class="up">強い</span></div><p>上期+99%、Q3計画$48M〜$50M。</p></div><div class="signal"><div><b>大型契約</b><span class="up">材料</span></div><p>Yotta、Batam、台湾案件。</p></div><div class="signal"><div><b>利益</b><span class="down">赤字</span></div><p>上期調整後EBITDAは-$14.6M。</p></div><div class="signal"><div><b>負債・希薄化</b><span class="down">注意</span></div><p>$232Mの転換社債と潜在株式。</p></div>',
        "POSITIVES": "<li>2026年上期売上は前年同期比99%増です。</li><li>営業キャッシュ流出は$4.3Mへ縮小しました。</li><li>Yotta、Batam、台湾で実行中の案件があります。</li><li>ソブリンAIと国家セキュリティの需要は中期追い風です。</li>",
        "CONCERNS": "<li>上期調整後EBITDAは$14.6Mの赤字です。</li><li>契約資産は6月末に$104.8Mへ増え、回収確認が必要です。</li><li>6月と7月の転換社債元本は合計$232Mです。</li><li>大型案件の同時実行と顧客集中にリスクがあります。</li>",
        "FORMULA": "2027年売上レンジに実行確率を反映したEV/Sを置き、負債・現金と潜在希薄化後株式数で調整しました。",
        "CALC_TABLE_HEAD": th("ケース", "2027年売上前提", "価値の見方", "計算株価", "確率", "確率加重"),
        "CALC_TABLE_ROWS": tr("悲観", "$250M前後", "遅延・低倍率", usd(BEAR), "30%", "$2.40") + tr("標準", "$450M前後", "段階稼働・黒字化", usd(BASE), "50%", "$10.00") + tr("楽観", "$500M以上", "高稼働・追加案件", usd(BULL), "20%", "$6.40"),
        "CALC_NOTICE": "契約総額をそのまま時価総額にせず、年間売上、利益率、資金負担、潜在株式数を反映した条件付き試算です。",
        "CONDITIONS": details("悲観ケース：$8 / 確率30%", "Yotta/Batamが遅延し、黒字化が遠のき、負債負担が重く残るケースです。", True) + details("標準ケース：$20 / 確率50%", "通期$200M以上を達成し、2027年にYotta/Batamを段階稼働させるケースです。") + details("楽観ケース：$32 / 確率20%", "2027年売上$500M以上、EBITDA黒字化、現金回収改善を同時に確認するケースです。"),
        "SENSITIVITY_HEAD": th("前提", "弱い", "標準", "強い"),
        "SENSITIVITY_ROWS": tr("2027売上", "$250M → $8", "$450M → $20", "$500M+ → $32") + tr("利益", "EBITDA赤字継続", "黒字化", "高稼働で利益拡大") + tr("完全希薄化後株式数", "追加増加", f"約{FULLY_DILUTED_M:.1f}M", "回収と成長で吸収"),
        "SENSITIVITY_NOTE": "強気ケースで株価が転換価格に近づくほど、転換社債の希薄化を重く見る必要があります。",
        "DIST_LEAD": "モンテカルロではなく、実行進捗を置いた3点シナリオです。",
        "DIST_ROWS": '<div class="dist-row"><span>$8</span><div class="track"><i style="width:30%"></i></div><b>30%</b></div><div class="dist-row"><span>$20</span><div class="track"><i style="width:50%"></i></div><b>50%</b></div><div class="dist-row"><span>$32</span><div class="track"><i style="width:20%"></i></div><b>20%</b></div>',
        "DIST_SUMMARY": f"確率加重価格は{usd(expected)}ですが、納入と資金調達のニュースで大きく変動します。",
        "WATCH_ROWS": '<div class="signal"><div><b>Q3売上・粗利</b></div><p>$48M〜$50Mと利益率を確認します。</p></div><div class="signal"><div><b>Yotta/Batam納入</b></div><p>台数、稼働、顧客利用開始を確認します。</p></div><div class="signal"><div><b>契約資産と現金</b></div><p>請求・回収と資本支出を確認します。</p></div>',
        "ASSUMPTIONS_ROWS": tr("評価基準株価", usd(P0), "市場データで確認", DATE, "2026/10/02終値") + tr("現在株式数", "約27.5M", "市場データ", DATE, "転換社債転換前") + tr("潜在希薄化後株式数", "約38.4M", "転換価格から試算", DATE, "$232Mを$25.4826で転換、RSU等を含む概算") + tr("2026年売上見通し", "$200M以上", "会社の目標・予定", "2026/08/24", "Q3計画$48M〜$50M") + tr("転換社債", "$232M・年利7.5%", "SEC提出資料", "2026/07/17", "初期転換価格$25.4826"),
        "DEEPDIVE_DETAILS": details("手法選定理由", "GRRRは利益が安定せず、大型契約の実行時期で売上が変動するため、PERよりも実行調整後EV/Sシナリオを使いました。", True) + details("契約額の扱い", "$2.8Bや$2.5Bは複数年の計画値であり、当年売上や利益とは異なります。") + details("主要出典", f'{source_link("2026年上期決算", "h1")}、{source_link("SEC上期資料", "h1_sec")}、{source_link("6月転換社債", "june_notes")}、{source_link("7月転換社債", "july_notes")}、{source_link("株価・統計", "quote")}。<br><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>'),
        "DISCLAIMER": "本資料は情報提供を目的とした試算です。投資助言ではありません。GRRRは大型案件の実行、資金調達、希薄化、為替、政府顧客で大きく変動します。",
        "FOOTER_NOTE": f"SiM MARKET LAB｜{COMPANY}（{TICKER}）株価シナリオ｜作成日 {DATE}",
    }


def catalyst_values() -> dict[str, str]:
    impact_map = {
        "Q3決算と通期$200M達成度": ("+25〜45%", "-8〜+12%", "-25〜-40%", "上期の高成長が続くかと、大型案件が利益に変わるかを同時に確認するためです。"),
        "Yotta GPU基盤の納入・稼働": ("+35〜70%", "-12〜+20%", "-30〜-50%", "会社規模に対して非常に大きい案件で、完了確認の有無が信頼度を大きく変えるためです。"),
        "Batam GPUaaS第1フェーズ": ("+30〜65%", "-10〜+18%", "-28〜-48%", "複数年の継続収入に変わる可能性がある一方、設備資金と稼働リスクが大きいためです。"),
        "契約資産の回収と資金管理": ("+18〜35%", "-6〜+10%", "-20〜-35%", "売上発表よりも現金回収と負債管理が1株価値を支えるためです。"),
    }
    description_map = {
        "Q3決算と通期$200M達成度": "Q3売上$48M〜$50Mの達成と、2026年通期売上$200M以上が現実的かを確認します。売上だけでなく粗利、調整後EBITDA、営業キャッシュフローが焦点です。",
        "Yotta GPU基盤の納入・稼働": "Yotta案件はインドのソブリンAI基盤です。9月・10月の納入、設置、通電、顧客利用、売上認識までを順に確認します。",
        "Batam GPUaaS第1フェーズ": "Batamは初期約1,000台のB300 GPUサーバーを使う計画です。設備が実際に稼働し、複数年のサービス収入が始まるかを見ます。",
        "契約資産の回収と資金管理": "6月末の契約資産は$104.8Mへ増加しました。請求マイルストーンの達成、現金回収、設備投資、転換社債の利払いを一緒に確認します。",
    }

    def card(title: str, date: str, chips: str, mechanism: str, success: str, inline: str, failure: str, evidence: str) -> str:
        up, flat, down, reason = impact_map[title]
        return f'''<article class="catalyst-card">
<div class="catalyst-head"><div><span class="pill">重要材料</span><h3>{title}</h3><div class="chips">{chips}</div></div><div class="date-box"><b>{date}</b><span>会社公表または推定</span></div></div>
<p class="lead">{description_map[title]}</p><div class="mechanism">{mechanism}</div><div class="outcomes">
<div class="outcome success"><b>期待以上</b><div class="impact up">{up}</div><p>{success}</p></div>
<div class="outcome inline"><b>ほぼ想定どおり</b><div class="impact flat">{flat}</div><p>{inline}</p></div>
<div class="outcome failure"><b>期待外れ・遅延</b><div class="impact down">{down}</div><p>{failure}</p></div></div>
<p class="notice"><b>この％にした理由：</b>{reason}</p><div class="evidence"><div><h4>根拠</h4><ul>{evidence}</ul></div><div><h4>反証・先行指標</h4><ul><li>納入完了の公式確認がない</li><li>契約資産が売上より速く増える</li><li>利益率と営業キャッシュフローが改善しない</li></ul></div></div></article>'''

    cards = [
        card("Q3決算と通期$200M達成度", "2026年秋", '<span class="chip">重要度5</span><span class="chip">最重要</span>', '<span>売上</span><i>→</i><span>利益</span><i>→</i><span>現金</span>', "Q3売上が$50Mを上回り、粗利・EBITDA・営業現金が同時に改善する状態です。", "Q3が会社計画内で、通期$200M以上を維持する状態です。", "売上未達、粗利低下、赤字拡大、通期見通し引き下げの状態です。", "<li>会社はQ3売上$48M〜$50Mを計画。</li><li>2026年通期売上見通しを$200M以上へ引き上げ。</li>"),
        card("Yotta GPU基盤の納入・稼働", "2026年Q4", '<span class="chip">重要度5</span><span class="chip blue">インド</span>', '<span>納入</span><i>→</i><span>稼働</span><i>→</i><span>売上認識</span>', "B300・B200設備の納入台数、通電、顧客利用、売上認識が数値で確認できる状態です。", "物理導入は進むが、売上と回収は段階的な状態です。", "納入延期、資金条件悪化、顧客利用開始の遅延が出る状態です。", "<li>9月8日に会社は物理実行段階への移行を発表。</li><li>4月発表の追加導入は9月30日までの完了計画。</li>"),
        card("Batam GPUaaS第1フェーズ", "2026年Q4〜2027年上期", '<span class="chip">重要度5</span><span class="chip blue">インドネシア</span>', '<span>資金</span><i>→</i><span>設備</span><i>→</i><span>GPUaaS収入</span>', "初期約1,000台が完成し、高稼働と長期顧客収入が確認される状態です。", "設備は段階稼働し、売上は2027年へ移行する状態です。", "融資未確定、建設・機器遅延、低稼働で収益化が遅れる状態です。", "<li>5年間で約$2.5Bの契約価値を会社が発表。</li><li>会社は機器等の想定コスト約70%を覆う融資提案を受領と説明。</li>"),
        card("契約資産の回収と資金管理", "次回決算以降", '<span class="chip">重要度4</span><span class="chip amber">財務</span>', '<span>進捗</span><i>→</i><span>請求</span><i>→</i><span>現金回収</span>', "契約資産が売掛金・現金へ変わり、営業キャッシュフローが黒字化する状態です。", "契約資産は増えるが、回収も並行し追加調達を避ける状態です。", "契約資産だけが増え、現金が急減し、追加増資や株式利払いが増える状態です。", "<li>6月末契約資産は$104.8M。</li><li>6月と7月の転換社債は合計$232M、年利7.5%。</li>"),
    ]
    non_quant = '<div class="priced"><div class="priced-head"><span>主要材料の推定織り込み</span><b>38%</b></div><p>仮定：2026年$200M達成を60%、Yotta稼働を45%、Batam第1フェーズを35%、契約資産の良好な回収を40%と置き、転換社債・実行リスクを控除しました。</p><p>読み方：現在株価は上期増収を評価していますが、2027年計画の完全達成はまだ強く織り込んでいません。</p><p>次に見る数字：Q3売上、粗利、調整後EBITDA、営業現金、契約資産、実稼働GPU台数です。</p><p>再計算方法：納入・稼働・回収の成功確率と完全希薄化後株式数を更新し、Bear/Base/Bullを再計算します。</p></div>'
    return {
        "COMPANY_NAME": COMPANY, "TICKER": TICKER, "EXCHANGE": "Nasdaq", "VALUATION_DATE": DATE, "LAST_UPDATED": DATE,
        "REPORT_STATUS": "大型案件の実行確認待ち", "SUMMARY_LINE_1": "Q3決算、Yotta稼働、Batam GPUaaS、契約資産の回収が主な材料です。", "SUMMARY_LINE_2": "足りない情報に仮定を置き、主要材料の織り込み度を38%と推定します。",
        "OVERALL_PRICED_IN": "38%", "OVERALL_PRICED_LABEL": "主要材料の推定織り込み", "PRICED_IN_CONFIDENCE": "低〜中", "CURRENT_PRICE": usd(P0), "CURRENT_PRICE_NOTE": "2026/10/02終値",
        "NEXT_CATALYST_TITLE": "Q3決算とYotta実行確認", "NEXT_CATALYST_WINDOW": "2026年秋", "DATE_CONFIDENCE": "一部推定", "CATALYST_COUNT": "4件", "WARN_BAND": "", "NO_CATALYST_NOTICE": "", "OVERALL_PRICED_BLOCK": non_quant,
        "PRICED_IN_METHOD": "2026年通期決算、Yotta、Batam、回収・負債管理を同じ価値経路ごとに束ね、重複を除いて推定。",
        "SURPRISE_UP": "YottaとBatamの納入・稼働が数値で確認され、Q3利益率と営業現金も改善することです。",
        "SURPRISE_DOWN": "納入遅延、利益率低下、契約資産の急増、追加増資、転換社債利払いの株式化です。",
        "PRIMARY_RISK": "小さい企業に対して契約と資本投下が急拡大し、納入・稼働・回収・負債管理を同時に実行する必要がある点です。",
        "TIMELINE_ROWS": '<div class="time-row"><div class="time-date">2026/09/08</div><div class="time-dot"></div><div class="time-body"><b>Yotta物理実行</b><p>電力・冷却・ステージングを進行。</p><div class="time-meta"><span class="chip">発表済み</span></div></div></div><div class="time-row"><div class="time-date">2026/09/22</div><div class="time-dot"></div><div class="time-body"><b>台湾案件</b><p>数千万ドル規模の複数年受注。</p><div class="time-meta"><span class="chip">受注</span></div></div></div><div class="time-row"><div class="time-date">2026年秋</div><div class="time-dot"></div><div class="time-body"><b>Q3決算</b><p>$48M〜$50Mの達成と利益・回収を確認。</p><div class="time-meta"><span class="chip blue">時期推定</span></div></div></div><div class="time-row"><div class="time-date">2026/12</div><div class="time-dot"></div><div class="time-body"><b>Batam第2トランシェ</b><p>GPUaaS導入と顧客利用を確認。</p><div class="time-meta"><span class="chip blue">会社計画</span></div></div></div>',
        "CATALYST_CARDS": "".join(cards) + '<p class="small">※下の％は、この結果が出た後に市場が材料を評価し直した場合の上昇・下落幅の目安です。実際の値動きは地合い、直前の株価上昇、同時ニュースで変わります。</p>',
        "DEPENDENCY_ROWS": '<div class="signal"><div><b>YottaとQ3売上</b><span class="up">同じ価値経路</span></div><p>納入が売上認識へ変わるため単純合算しません。</p></div><div class="signal"><div><b>Batamと資金調達</b><span class="flat">依存</span></div><p>融資条件が設備規模と1株価値を同時に動かします。</p></div><div class="signal"><div><b>台湾案件</b><span class="up">分散</span></div><p>AIデータセンター以外の政府・セキュリティ収入を支えます。</p></div>',
        "WATCH_ROWS": '<div class="signal"><div><b>Q3売上・粗利</b><span class="up">最重要</span></div><p>成長が利益へ変わるかを確認します。</p></div><div class="signal"><div><b>GPU納入・稼働台数</b><span class="up">実行</span></div><p>発表額ではなく実績を確認します。</p></div><div class="signal"><div><b>契約資産</b><span class="down">回収</span></div><p>$104.8Mから現金へ変わるかを確認します。</p></div><div class="signal"><div><b>完全希薄化後株式数</b><span class="down">注意</span></div><p>転換社債、RSU、ワラントを確認します。</p></div>',
        "ASSUMPTION_ROWS": tr("評価基準株価", usd(P0), "市場データで確認", DATE, "2026/10/02終値") + tr("Q3売上計画", "$48M〜$50M", "会社の目標・予定", "2026/08/24", "Q2決算で引き上げ") + tr("Yotta追加導入", "B300 20,736枚", "会社の目標・予定", "2026/04/29", "9/30までの完了計画。完了発表は確認待ち") + tr("契約資産", "$104.8M", "SEC提出資料", "2026/06/30", "請求マイルストーン前を含む") + tr("転換社債", "$232M", "SEC提出資料", "2026/07/17", "初期転換価格$25.4826"),
        "SOURCE_DETAILS": f'<ul><li>{source_link("2026年上期決算", "h1")}</li><li>{source_link("SEC上期資料", "h1_sec")}</li><li>{source_link("Yotta拡張案件", "yotta")}</li><li>{source_link("Batam GPUaaS契約", "batam")}</li><li>{source_link("台湾拡張契約", "taiwan")}</li><li>{source_link("6月転換社債", "june_notes")}</li><li>{source_link("7月転換社債", "july_notes")}</li></ul><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p>',
        "VALIDATION_DETAILS": "<p>PASS：2026年上期決算、SEC提出資料、Yotta、Batam、台湾契約を確認。WARN：Yottaの9月30日完了とBatamの実稼働は公式確認待ち。</p>",
        "UPDATE_HISTORY": f"<p>{DATE}：初版作成。2026年上期決算、Yotta・Batam・台湾案件、6月・7月転換社債を反映。</p>",
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
        "id": "gorilla-technology-grrr", "order": 14, "ticker": "GRRR", "quoteSymbol": "GRRR",
        "name": COMPANY, "nameEn": "Gorilla Technology Group Inc.", "market": "US", "marketLabel": "米国株",
        "exchange": "Nasdaq", "currency": "USD", "sector": "AIインフラ・スマートシティ・セキュリティ",
        "themes": ["AIインフラ", "データセンタ", "サイバーセキュリティ"],
        "reports": {
            "company": {"path": "./stocks/gorilla-technology-grrr/company.html", "available": True},
            "valuation": {"path": "./stocks/gorilla-technology-grrr/valuation.html", "available": True},
            "catalysts": {"path": "./stocks/gorilla-technology-grrr/catalysts.html", "available": True},
        },
    }
    stocks_payload["stocks"] = [item for item in stocks_payload["stocks"] if item["id"] != stock["id"]]
    stocks_payload["stocks"].append(stock)
    stocks_payload["stocks"].sort(key=lambda item: item["order"])
    stocks_path.write_text(json.dumps(stocks_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    prices_path = ROOT / "data" / "prices.json"
    prices_payload = json.loads(prices_path.read_text(encoding="utf-8"))
    prices_payload.setdefault("prices", {})[stock["id"]] = {
        "symbol": TICKER, "price": P0, "previousClose": PREVIOUS_CLOSE,
        "change": round(P0 - PREVIOUS_CLOSE, 4), "changePct": round((P0 - PREVIOUS_CLOSE) / PREVIOUS_CLOSE * 100, 4),
        "currency": "USD", "marketTime": "2026-10-02T20:00:00+00:00", "updatedAt": datetime.now(timezone.utc).isoformat(), "status": "ok",
    }
    prices_payload["quoteCount"] = len(prices_payload["prices"])
    prices_path.write_text(json.dumps(prices_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    signals_path = ROOT / "data" / "signals.json"
    signals_payload = json.loads(signals_path.read_text(encoding="utf-8"))
    signals_payload["updatedAt"] = datetime.now(timezone.utc).isoformat()
    signals_payload.setdefault("signals", {})[stock["id"]] = {
        "position": SIGNAL_POSITION, "zone": "中立", "asOf": DATE,
        "components": {"valuation": round(BAND_POSITION, 1), "catalysts": CATALYST_SCORE, "businessRisk": BUSINESS_RISK_SCORE},
        "reportRevision": "gorilla-technology-grrr-2026-10-03",
        "summary": "上期99%増収と大型AI案件は強い一方、赤字、納入・回収、$232Mの転換社債と希薄化リスクから中立。",
    }
    signals_path.write_text(json.dumps(signals_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_reports()
    upsert_site_data()


if __name__ == "__main__":
    main()
