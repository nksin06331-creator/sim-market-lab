"""Generate SEALSQ report HTML files from the bundled SiM templates."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from generate_rocket_lab_reports import dl, li, render_template, th, tr


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stocks" / "sealsq-laes"

COMPANY = "シールエスキュー"
TICKER = "LAES"
DATE = "2026-08-13"
P0 = 2.34
PREVIOUS_CLOSE = 2.48
SHARES_M = 222.77
MARKET_CAP_M = P0 * SHARES_M

BEAR = 1.40
BASE = 3.20
BULL = 5.80
BAND_POSITION = (P0 - BEAR) / (BULL - BEAR) * 100
CATALYST_SCORE = 68.0
BUSINESS_RISK_SCORE = 42.0
SIGNAL_POSITION = round(0.60 * round(BAND_POSITION, 1) + 0.25 * CATALYST_SCORE + 0.15 * BUSINESS_RISK_SCORE, 1)

SOURCES = {
    "about": "https://www.sealsq.com/about/about-us",
    "h1": "https://www.sec.gov/Archives/edgar/data/1738699/000121390026076377/ea029728301ex99-1.htm",
    "quantum": "https://www.sealsq.com/investors/news-releases/sealsq-establishes-pure-play-quantum-platform-through-strategic-acquisitions-and-investments-across-leading-quantum-computing-companies",
    "annual": "https://www.sec.gov/Archives/edgar/data/1951222/000110465926037706/laes-20251231x20f.htm",
    "quote": "https://stockanalysis.com/stocks/laes/",
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
        f'{source_link("会社概要", "about")}、'
        f'{source_link("H1 2026予備決算リリース", "h1")}、'
        f'{source_link("量子プラットフォーム発表", "quantum")}、'
        f'{source_link("2025年Form 20-F", "annual")}、'
        f'{source_link("株価・統計", "quote")}を確認しました。'
        "本文の数値は2026年8月13日時点で取得できた公開情報に基づきます。"
        '</p><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p></div></details>'
    )
    terms = [
        ("PQC", "Post-Quantum Cryptographyの略です。量子コンピューターでも破られにくい暗号方式への移行を指します。"),
        ("QS7001", "SEALSQのポスト量子対応セキュアエレメントです。NIST標準アルゴリズムをハードウェア側に組み込む設計です。"),
        ("QVault TPM", "端末やサーバーの信頼の起点になるTPM製品です。ポスト量子対応のハードウェアルート・オブ・トラストを狙います。"),
        ("Vault-IC", "既存のセキュアエレメント製品群です。H1 2026の増収要因として会社が説明しています。"),
        ("PKI", "公開鍵基盤です。証明書の発行・管理により、機器やデータの信頼性を支えます。"),
        ("IC'ALPS", "ASIC設計会社です。2025年に取得し、設計能力と売上寄与を広げています。"),
        ("Root-to-Qubit", "暗号の信頼基盤から量子コンピューティング側までを一体で押さえる会社の戦略です。"),
        ("パイプライン", "将来売上になり得る商談候補です。受注残ではなく、転換リスクがあります。"),
        ("希薄化", "増資などで1株あたり価値が薄まることです。LAESは資金調達額が大きいため重要です。"),
        ("ソブリン半導体", "国や地域が自前で管理できる半導体・認証基盤です。欧州や米国の安全保障需要と関係します。"),
    ]
    return {
        "TICKER": TICKER,
        "COMPANY_NAME": COMPANY,
        "INDUSTRY": "ポスト量子セキュリティ半導体・PKI",
        "DATE": DATE,
        "TAGLINE": "量子時代に備えたセキュア半導体、PKI、TPM、ASIC設計を展開するスイス発の小型テクノロジー企業です。",
        "HERO_TAGS": '<span class="hero-tag">米国株</span><span class="hero-tag">半導体</span><span class="hero-tag">量子</span><span class="hero-tag">Nasdaq</span>',
        "HERO_STATS": (
            f'<div class="stat"><div class="stat-value">{usd(P0)}</div><div class="stat-label">評価基準株価</div><div class="stat-note">2026/07/28確認値</div></div>'
            f'<div class="stat"><div class="stat-value">${MARKET_CAP_M:.0f}M</div><div class="stat-label">時価総額の目安</div><div class="stat-note">約2.23億株で計算</div></div>'
            '<div class="stat"><div class="stat-value up">$11M</div><div class="stat-label">H1 2026売上</div><div class="stat-note">予備値、前年比+120%</div></div>'
            '<div class="stat"><div class="stat-value">$495M</div><div class="stat-label">現金・短期投資</div><div class="stat-note">2026/06/30時点</div></div>'
        ),
        "SEC2_LABEL": "事業モデル",
        "SEC3_LABEL": "製品",
        "SEC4_LABEL": "決算",
        "SEC5_LABEL": "競合比較",
        "SEC1_TLDR": li("SEALSQはポスト量子暗号に対応するセキュア半導体とPKIを提供します。", "*") + li("H1 2026予備売上は約1,100万ドル、前年比120%増で、FY2026は50〜100%成長見通しです。", "*") + li("現金は厚い一方、商用化・パイプライン転換・希薄化リスクが大きい銘柄です。", "!"),
        "SEC1_FACTS": (
            "<div><dt>正式社名</dt><dd>SEALSQ Corp</dd></div><div><dt>本社</dt><dd>Geneva / Switzerland</dd></div>"
            "<div><dt>上場</dt><dd>Nasdaq（LAES）</dd></div><div><dt>業種</dt><dd>セキュア半導体・PKI</dd></div>"
            "<div><dt>主な製品</dt><dd>Vault-IC、QS7001、QVault TPM、PKI、ASIC設計</dd></div><div><dt>親会社</dt><dd>WISeKeyグループ系</dd></div>"
        ),
        "SEC1_CARDS": (
            '<div class="card-sm"><span class="card-emoji">🔐</span><div class="card-title">何をしている</div><div class="card-desc">IoTや産業機器の認証を支えるセキュアチップを作ります。</div></div>'
            '<div class="card-sm"><span class="card-emoji">🧬</span><div class="card-title">成長テーマ</div><div class="card-desc">量子耐性暗号、TPM、ソブリン半導体が焦点です。</div></div>'
            '<div class="card-sm"><span class="card-emoji">💵</span><div class="card-title">財務余力</div><div class="card-desc">2026年6月末で現金・短期投資は約4.95億ドルです。</div></div>'
            '<div class="card-sm"><span class="card-emoji">⚠️</span><div class="card-title">注意</div><div class="card-desc">小型株で、商用化遅れ・希薄化・株価変動が大きいです。</div></div>'
        ),
        "SEC1_BIZMODEL": (
            '<li><span class="kp-emoji">🔐</span><span class="kp-text"><b>Secure chips</b>：Vault-ICやQS7001などのセキュアエレメントを販売します。</span></li>'
            '<li><span class="kp-emoji">📜</span><span class="kp-text"><b>PKI</b>：証明書発行・管理で機器の本人性を支えます。</span></li>'
            '<li><span class="kp-emoji">🧩</span><span class="kp-text"><b>ASIC設計</b>：IC’ALPS取得でカスタム半導体設計を拡大します。</span></li>'
        ),
        "SEC1_HIGHLIGHT": '<div class="highlight"><h3>LAESを見る基本ルール</h3><p>売上成長だけでなく、QS7001/QVaultの認証、顧客評価から量産売上への転換、現金の使い方、希薄化をセットで確認します。</p></div>',
        "SEC2_ICON": "🔐",
        "SEC2_TITLE": "信頼の起点を作る<span class=\"g\">半導体</span>",
        "SEC2_SUB": "IoT・産業機器・防衛向けの認証基盤",
        "SEC2_TLDR": li("SEALSQの核は、機器の中に入るセキュアチップと証明書管理です。", "*") + li("量子コンピューター時代に備え、PQC対応のQS7001とQVault TPMを商用化しようとしています。", "*") + li("テーマ性は強いですが、まだ商用化と顧客転換の確認が必要です。", "!"),
        "SEC2_CONTENT": (
            '<p class="lead">SEALSQは、IoT機器、産業機器、スマートメーター、防衛・航空宇宙、医療などで使う認証・暗号の土台を提供します。</p>'
            '<div class="sowhat"><p><b>つまり</b>、LAESは量子コンピューター関連そのものというより、量子時代に必要になる「守りの半導体」として見ます。</p></div>'
            '<div class="term-list">'
            + details("セキュアエレメント", "秘密鍵や証明書を安全に保管し、機器の本人確認を支えるチップです。", True)
            + details("PKI", "公開鍵基盤です。機器や利用者の証明書を発行・管理します。")
            + details("ASIC", "用途に合わせて設計するカスタム半導体です。IC’ALPS取得でこの能力が強化されました。")
            + details("ソブリン半導体", "国や地域の安全保障・規制対応に沿った半導体認証基盤です。")
            + "</div>"
        ),
        "SEC3_TITLE": "QS7001と<span class=\"g\">QVault</span>",
        "SEC3_SUB": "ポスト量子対応製品の量産化が焦点",
        "SEC3_TLDR": li("QS7001はポスト量子暗号対応のセキュアエレメントです。", "*") + li("QVault TPMはポスト量子対応のハードウェアルート・オブ・トラストを狙います。", "*") + li("初期売上がH2 2026に出るか、2027に拡大するかが重要です。", "!"),
        "SEC3_CONTENT": (
            '<div class="product-grid"><div class="product-box"><div class="product-symbol">QS</div><div class="product-name">QS7001</div><div class="product-use">PQC対応セキュアエレメント。</div></div>'
            '<div class="product-box"><div class="product-symbol">TPM</div><div class="product-name">QVault TPM</div><div class="product-use">端末の信頼の起点。</div></div>'
            '<div class="product-box"><div class="product-symbol">ASIC</div><div class="product-name">IC’ALPS</div><div class="product-use">カスタム半導体設計。</div></div></div>'
            '<div class="term-list">'
            + details("QS7001", "NIST標準化アルゴリズムをハードウェア側に組み込むことを狙う次世代製品です。", True)
            + details("QVault TPM", "PC、サーバー、産業機器などの信頼基盤になるTPM市場を狙う製品です。")
            + details("顧客評価", "会社は15社超の見込み顧客・パートナーがQS7001とSDKを評価中と説明しています。")
            + details("認証", "FIPS 140-3やCommon Criteriaなどの認証進捗が採用の前提になります。")
            + "</div>"
        ),
        "SEC4_TITLE": "H1 2026は<span class=\"g\">増収</span>",
        "SEC4_SUB": "ただし黒字化より商用化フェーズ確認",
        "SEC4_TLDR": li("H1 2026予備売上は約1,100万ドルで前年比120%増です。", "*") + li("会社はFY2026売上を前年比50〜100%増と再確認しました。", "*") + li("パイプラインは大きいですが、受注残ではないため転換リスクがあります。", "!"),
        "SEC4_CONTENT": (
            '<ul class="keypoints"><li><span class="kp-emoji">📈</span><span class="kp-text"><b>H1売上</b>：約$11M、前年比+120%。</span></li>'
            '<li><span class="kp-emoji">💵</span><span class="kp-text"><b>現金</b>：2026年6月末で現金・短期投資は約$495M。</span></li>'
            '<li><span class="kp-emoji">🔁</span><span class="kp-text"><b>見通し</b>：FY2026売上は$27M〜$36M程度のレンジ。</span></li></ul>'
            '<div class="sowhat"><p><b>つまり</b>、売上規模に対して手元資金が大きく、事業拡大と投資の余地はあります。ただし、収益化の実行力を毎決算で確認する段階です。</p></div>'
        ),
        "SEC5_TITLE": "競合と<span class=\"g\">比べる</span>",
        "SEC5_SUB": "テーマ性は強いが規模は小さい",
        "SEC5_TLDR": li("比較対象はNXP、Infineon、STMicroelectronics、Microchip、各種サイバーセキュリティ企業です。", "*") + li("LAESはポスト量子対応とセキュアチップの専門性で差別化します。", "*") + li("大手と比べて規模・販売網・収益安定性は弱いです。", "!"),
        "SEC5_CONTENT": (
            '<div class="table-wrap"><table class="compare-table"><thead><tr><th>対象</th><th>強み</th><th>注意点</th></tr></thead><tbody>'
            '<tr><td class="me">SEALSQ</td><td>PQC対応セキュアチップ、PKI、ASIC設計、量子テーマ。</td><td>小型株で実行・希薄化・変動リスクが大きい。</td></tr>'
            '<tr><td>NXP / Infineon</td><td>セキュアMCU、車載、産業向けの規模と販売網。</td><td>大型でテーマ性は分散される。</td></tr>'
            '<tr><td>STMicro / Microchip</td><td>MCU、セキュリティ、産業顧客基盤。</td><td>ポスト量子専業ではない。</td></tr>'
            '<tr><td>サイバー各社</td><td>ソフトウェア側の防御と運用基盤。</td><td>ハードウェアルート・オブ・トラストとは領域が違う。</td></tr>'
            '</tbody></table></div><div class="highlight"><h3>差別化の見方</h3><p>LAESは「PQC対応の小型半導体株」として期待されます。大手より伸びしろはありますが、売上規模が小さいため、案件遅延の影響も大きくなります。</p></div>'
        ),
        "SEC6_TLDR": li("PQC、QS7001、QVault TPM、PKI、IC’ALPS、パイプラインを押さえると読みやすいです。", "*") + li("規制と認証が進むほど採用の追い風になります。", "*") + li("パイプラインは売上確定ではありません。", "!"),
        "SEC6_CONTENT": '<div class="term-list">' + "".join(details(name, body) for name, body in terms) + "</div>",
        "SEC7_TLDR": li("最大材料はH1 2026正式決算、QS7001/QVaultの認証と商用売上です。", "*") + li("Quantix Edge Security、Miraex、Quoblyなどの投資効果も確認します。", "*") + li("増資・希薄化、商用化遅れ、パイプライン未転換には注意です。", "!"),
        "SEC7_CONTENT": (
            '<div class="timeline"><div class="tl-row"><div class="tl-date">2026/06/05</div><div class="tl-title">量子プラットフォーム拡大 <span class="signal bull">テーマ</span></div><div class="tl-desc">EeroQ、Quobly、Miraexなどを含むRoot-to-Qubit戦略を説明。</div></div>'
            '<div class="tl-row"><div class="tl-date">2026/07/06</div><div class="tl-title">H1 2026予備決算 <span class="signal bull">増収</span></div><div class="tl-desc">H1売上約$11M、前年比+120%、FY2026見通しを再確認。</div></div>'
            '<div class="tl-row"><div class="tl-date">H2 2026</div><div class="tl-title">QS7001/QVaultの商用化 <span class="signal bull">最重要</span></div><div class="tl-desc">初期商用売上と顧客評価の量産転換を確認。</div></div>'
            '<div class="tl-row"><div class="tl-date">2027</div><div class="tl-title">生産売上の拡大確認 <span class="signal neutral">確認</span></div><div class="tl-desc">12〜18か月の評価サイクル後に売上化できるか。</div></div></div>'
            '<div class="info-row"><div class="info-box info-box-green"><div class="info-title info-title-green">追い風</div><div class="info-text">PQC規制、現金余力、Vault-IC増収、量子テーマ。</div></div>'
            '<div class="info-box info-box-amber"><div class="info-title info-title-amber">確認</div><div class="info-text">認証、商用売上、パイプライン転換、希薄化。</div></div>'
            '<div class="info-box info-box-red"><div class="info-title info-title-red">リスク</div><div class="info-text">小型株の変動、商用化遅れ、競争、追加調達。</div></div></div>'
            + source_details
        ),
    }


def scenario_values() -> dict[str, str]:
    probs = {"bear": 0.30, "base": 0.45, "bull": 0.25}
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
        "METHOD": "ポスト量子半導体・小型成長株向けシナリオ評価",
        "VERDICT_STATUS": "現金厚いが商用化待ち",
        "VERDICT_LINE_1": f"評価基準株価は悲観〜楽観レンジの{BAND_POSITION:.1f}%地点です。現金余力は大きい一方、売上化の確認はこれからです。",
        "VERDICT_LINE_2": "この試算は2026年8月13日時点で取得できた公開情報に基づきます。H1正式決算とH2商用化進捗で更新が必要です。",
        "SCORE": str(score),
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "2026/07/28確認値",
        "BASE_PRICE": usd(BASE),
        "BASE_DELTA": pct(BASE / P0 - 1),
        "EXPECTED_VALUE": usd(expected),
        "EXPECTED_DELTA": pct(expected / P0 - 1),
        "RISK_CLASS": "高",
        "RISK_NOTE": "小型株、商用化、希薄化、テーマ変動",
        "WARN_BAND": "",
        "WARN_MESSAGE": "小型株で値動きが大きく、公開情報も予備値を含みます。",
        "SNAPSHOT_LEAD": "今の株価は悲観寄りから標準ケースへ向かう途中です。現金は厚いですが、株価の上振れにはQS7001/QVaultの商用売上とパイプライン転換が必要です。",
        "BAND_POSITION": f"{BAND_POSITION:.1f}%",
        "ZONE_JUDGE": "悲観寄り",
        "ZONE_NOTE": "H2 2026の商用化と認証進捗が良ければ標準側へ、希薄化や遅延が出ると悲観側に戻ります。",
        "BEAR_PRICE": usd(BEAR),
        "BULL_PRICE": usd(BULL),
        "ENDPOINT_RR": f"{endpoint_rr:.1f}倍",
        "MARKET_SCORE": str(round(BAND_POSITION)),
        "OWN_SCORE": str(round(own_score)),
        "MARKET_REVERSE_NOTE": "市場は量子・PQCテーマを評価していますが、まだ商用売上の確度は十分に織り切っていないと見ます。",
        "SCENARIOS_LEAD": "現在株価から独立して、現金余力、H1成長、PQC製品の商用化、希薄化、パイプライン転換を置きました。",
        "BEAR_PROB": "30%",
        "BASE_PROB": "45%",
        "BULL_PROB": "25%",
        "BEAR_DELTA": pct(BEAR / P0 - 1),
        "BULL_DELTA": pct(BULL / P0 - 1),
        "BEAR_DL_ROWS": dl([("商用化", "遅延"), ("資金", "希薄化懸念"), ("倍率", "テーマ剥落"), ("株価", usd(BEAR))]),
        "BASE_DL_ROWS": dl([("成長", "FY2026見通し達成"), ("製品", "初期商用売上"), ("現金", "投資余力維持"), ("株価", usd(BASE))]),
        "BULL_DL_ROWS": dl([("成長", "上振れ"), ("PQC", "認証・量産転換"), ("量子投資", "再評価"), ("株価", usd(BULL))]),
        "PRICE_ZONE_ROWS": '<div class="zone"><div><b>$1.40未満</b><span>★★</span></div><p>商用化遅れや希薄化を強く織り込む価格帯です。</p></div><div class="zone"><div><b>$1.40〜$3.20</b><span>★★★</span></div><p>現金価値と成長期待を見ながら、実行力を確認する価格帯です。</p></div><div class="zone"><div><b>$3.20〜$5.80</b><span>★★</span></div><p>H2商用化とFY2026上振れを評価する価格帯です。</p></div><div class="zone"><div><b>$5.80超</b><span>★</span></div><p>複数製品の量産売上とパイプライン転換が必要です。</p></div>',
        "SIGNAL_ROWS": '<div class="signal"><div><b>H1予備決算</b><span class="up">強い</span></div><p>売上約$11M、前年比+120%。</p></div><div class="signal"><div><b>現金</b><span class="up">厚い</span></div><p>現金・短期投資は約$495M。</p></div><div class="signal"><div><b>商用化</b><span class="flat">確認</span></div><p>QS7001/QVaultの量産売上はこれから。</p></div><div class="signal"><div><b>希薄化</b><span class="down">注意</span></div><p>大きな資金調達後の株式数変動に注意。</p></div>',
        "POSITIVES": "<li>H1 2026予備売上は前年比120%増でした。</li><li>現金・短期投資が約$495Mあり、売上規模に比べて財務余力が大きいです。</li><li>QS7001/QVault、IC’ALPS、Quantix Edge Securityなど成長材料があります。</li><li>PQC規制・量子セキュリティ移行は中長期テーマです。</li>",
        "CONCERNS": "<li>売上規模はまだ小さく、黒字化より商用化確認の段階です。</li><li>パイプラインは受注残ではなく、転換できない可能性があります。</li><li>増資や投資により希薄化リスクがあります。</li><li>量子テーマ株として株価変動が大きいです。</li>",
        "FORMULA": "売上規模が小さいためPERではなく、現金余力、FY2026売上レンジ、PQC製品の商用化、希薄化リスクをまとめたシナリオ法で見ました。",
        "CALC_TABLE_HEAD": th("ケース", "主な前提", "価値の見方", "計算株価", "確率", "確率加重"),
        "CALC_TABLE_ROWS": tr("悲観", "商用化遅延", "現金価値と希薄化懸念", usd(BEAR), "30%", "$0.42") + tr("標準", "FY2026見通し達成", "初期商用売上を評価", usd(BASE), "45%", "$1.44") + tr("楽観", "PQC量産転換", "量子セキュリティ株として再評価", usd(BULL), "25%", "$1.45"),
        "CALC_NOTICE": "現在株価に合わせた逆算ではありません。パイプラインは契約済み売上ではないため、確率を控えめに置いています。",
        "CONDITIONS": details("悲観ケース：$1.40 / 確率30%", "QS7001/QVaultの商用化が遅れ、追加調達や希薄化懸念が強まるケースです。", True) + details("標準ケース：$3.20 / 確率45%", "FY2026売上見通しを達成し、H2に初期商用売上が確認されるケースです。") + details("楽観ケース：$5.80 / 確率25%", "認証、量産転換、パイプライン契約化、量子投資の再評価が重なるケースです。"),
        "SENSITIVITY_HEAD": th("前提", "弱い", "標準", "強い"),
        "SENSITIVITY_ROWS": tr("FY2026売上", "下限未達 → $1.40", "50〜100%成長 → $3.20", "上限超え → $5.80") + tr("PQC商用化", "遅延", "初期売上", "量産転換") + tr("資本政策", "希薄化懸念", "現金活用", "戦略投資が成果化"),
        "SENSITIVITY_NOTE": "LAESは売上規模が小さいため、数百万ドル単位の上振れ・遅れでも評価が動きやすいです。",
        "DIST_LEAD": "モンテカルロではなく、H2 2026商用化前の3点シナリオです。",
        "DIST_ROWS": '<div class="dist-row"><span>$1.40</span><div class="track"><i style="width:30%"></i></div><b>30%</b></div><div class="dist-row"><span>$3.20</span><div class="track"><i style="width:45%"></i></div><b>45%</b></div><div class="dist-row"><span>$5.80</span><div class="track"><i style="width:25%"></i></div><b>25%</b></div>',
        "DIST_SUMMARY": "期待値は標準ケース付近です。ただし、商用化遅れと希薄化が同時に出ると悲観側へ寄ります。",
        "WATCH_ROWS": '<div class="signal"><div><b>H1 2026正式決算</b></div><p>予備値との差、費用、現金、株式数を確認します。</p></div><div class="signal"><div><b>QS7001/QVault</b></div><p>認証進捗、顧客評価、初期商用売上を確認します。</p></div><div class="signal"><div><b>資本政策</b></div><p>追加調達、投資、希薄化、現金の使い道を確認します。</p></div>',
        "ASSUMPTIONS_ROWS": tr("評価基準株価", usd(P0), "市場データで確認", DATE, "2026/07/28確認値") + tr("H1 2026売上", "約$11M", "会社リリース", "2026/07/06", "予備値、前年比+120%") + tr("FY2026売上見通し", "$27M〜$36M", "会社リリース", "2026/07/06", "前年比50〜100%成長") + tr("現金・短期投資", "約$495M", "会社リリース", "2026/06/30", "資金調達後"),
        "DEEPDIVE_DETAILS": details("手法選定理由", "LAESは売上規模がまだ小さく、利益倍率だけでは見にくい銘柄です。現金余力、商用化、認証、希薄化を分けてシナリオ化します。", True) + details("株価水準について", "現金が厚い一方、テーマ株として期待と失望の振れが大きいです。現在地バーはprices.jsonの現在株価とBear/Bullから表示時に再計算されます。") + details("主要出典", f'{source_link("H1 2026予備決算リリース", "h1")}、{source_link("会社概要", "about")}、{source_link("量子プラットフォーム発表", "quantum")}、{source_link("2025年Form 20-F", "annual")}。<br><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>'),
        "DISCLAIMER": "本資料は情報提供を目的とした試算です。投資助言ではありません。小型株・テーマ株は決算、資本政策、需給で大きく変動します。",
        "FOOTER_NOTE": f"SiM MARKET LAB｜{COMPANY}（{TICKER}）株価シナリオ｜作成日 {DATE}",
    }


def catalyst_values() -> dict[str, str]:
    non_quant = '<div class="priced"><div class="priced-head"><span>主要材料の推定織り込み</span><b>50%</b></div><p>仮定：H1 2026増収を70%、FY2026ガイダンスを60%、QS7001/QVault商用化を40%、量子投資ポートフォリオを30%として置き、パイプライン転換と希薄化リスクを控除しました。</p><p>読み方：足元の増収と現金余力はかなり評価されていますが、PQC製品の量産売上はまだ十分には織り込まれていません。</p><p>次に見る数字：H1正式売上、FY2026見通し、現金、株式数、QS7001/QVaultの認証と初期売上、パイプラインの契約化です。</p><p>再計算方法：各材料の成功確率を更新し、レポート2のシナリオ株価を再計算します。</p></div>'
    impact_map = {
        "H1 2026正式決算とFY2026見通し": ("+18〜38%", "-8〜+10%", "-18〜-32%", "売上規模が小さいため、数百万ドルの差でも成長率と資金効率の見方が大きく変わるためです。"),
        "QS7001とQVault TPMの認証・商用売上": ("+25〜55%", "-6〜+14%", "-20〜-40%", "LAESの中核テーマそのもので、顧客評価から売上化へ移るかが評価レンジを直接変えるためです。"),
        "パイプラインの契約化と顧客拡大": ("+16〜36%", "-5〜+10%", "-15〜-30%", "会社のパイプラインは大きい一方で受注残ではないため、契約化の確認が必要だからです。"),
        "量子投資とRoot-to-Qubit戦略": ("+10〜24%", "-4〜+8%", "-8〜-18%", "テーマ評価は上げますが、短期売上への直結度は商用製品より低いためです。"),
    }
    description_map = {
        "H1 2026正式決算とFY2026見通し": "予備値で示されたH1売上約1,100万ドル、前年比120%増が正式値でも確認されるかを見ます。費用、現金、株式数も同時に確認します。",
        "QS7001とQVault TPMの認証・商用売上": "PQC対応セキュアエレメントとTPMが、評価キットや顧客検証から初期商用売上へ進むかを確認します。",
        "パイプラインの契約化と顧客拡大": "会社が示す2.25億ドル超の商談機会が、実際の契約・量産・売上に変わるかを確認します。",
        "量子投資とRoot-to-Qubit戦略": "EeroQ、Quobly、Miraexなどへの投資が、単なるテーマではなく事業上の優位性に変わるかを見ます。",
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
<div class="evidence"><div><h4>根拠</h4><ul>{evidence}</ul></div><div><h4>反証・先行指標</h4><ul><li>売上成長率の鈍化</li><li>追加調達や株式数の増加</li><li>認証・顧客評価の遅延</li></ul></div></div>
</article>'''

    cards = [
        card("H1 2026正式決算とFY2026見通し", "H2 2026", '<span class="chip">重要度4</span><span class="chip">決算</span>', '<span>予備値</span><i>→</i><span>正式値</span><i>→</i><span>見通し</span>', "売上・見通し・現金が強く、株式数増加も限定的なら上振れです。", "予備値どおりなら標準ケースを維持します。", "売上未達や費用増、追加希薄化が目立つと下落要因です。", "<li>H1 2026予備売上は約$11M、前年比+120%。</li><li>FY2026売上は前年比50〜100%増を再確認。</li>"),
        card("QS7001とQVault TPMの認証・商用売上", "H2 2026", '<span class="chip">重要度5</span><span class="chip blue">PQC</span>', '<span>認証</span><i>→</i><span>顧客評価</span><i>→</i><span>初期売上</span>', "認証進捗と初期商用売上が同時に確認されれば楽観側です。", "評価継続と少額売上なら中立です。", "認証や顧客統合が遅れるとテーマ剥落です。", "<li>QS7001はNIST SP 800-90B ESVを取得。</li><li>QVault TPMはH2 2026の初期商用売上が期待されています。</li>"),
        card("パイプラインの契約化と顧客拡大", "2026〜2029", '<span class="chip">重要度4</span><span class="chip blue">商談</span>', '<span>商談</span><i>→</i><span>契約</span><i>→</i><span>量産</span>', "大口契約や顧客数拡大が確認されれば上振れです。", "商談継続だけなら株価反応は限定的です。", "商談が売上化しない場合は下押しです。", "<li>会社は2029年までに$225M超のパイプラインを説明。</li><li>QS7001/QVault関連は$60M超と説明。</li>"),
        card("量子投資とRoot-to-Qubit戦略", "継続確認", '<span class="chip">重要度3</span><span class="chip blue">量子</span>', '<span>投資</span><i>→</i><span>連携</span><i>→</i><span>事業化</span>', "投資先連携が製品・契約に結びつけば上振れです。", "発表中心なら中立です。", "投資先評価損や資金流出が意識されると下落要因です。", "<li>会社はEeroQ、Quobly、Miraexなどを含む量子戦略を説明。</li><li>SEALQuantum Fundの目標配分は$200M。</li>"),
    ]
    return {
        "COMPANY_NAME": COMPANY,
        "TICKER": TICKER,
        "EXCHANGE": "Nasdaq",
        "VALUATION_DATE": DATE,
        "LAST_UPDATED": DATE,
        "REPORT_STATUS": "商用化進捗待ち",
        "SUMMARY_LINE_1": "H1正式決算、QS7001/QVault商用化、パイプライン契約化、量子投資の実効性が主な材料です。",
        "SUMMARY_LINE_2": "足りない情報は仮定を置き、主要材料の織り込み度を50%と推定します。",
        "OVERALL_PRICED_IN": "50%",
        "OVERALL_PRICED_LABEL": "主要材料の推定織り込み",
        "PRICED_IN_CONFIDENCE": "中",
        "CURRENT_PRICE": usd(P0),
        "CURRENT_PRICE_NOTE": "2026/07/28確認値",
        "NEXT_CATALYST_TITLE": "H1 2026正式決算とH2商用化進捗",
        "NEXT_CATALYST_WINDOW": "H2 2026",
        "DATE_CONFIDENCE": "会社発表ベース",
        "CATALYST_COUNT": "4件",
        "WARN_BAND": "",
        "NO_CATALYST_NOTICE": "",
        "OVERALL_PRICED_BLOCK": non_quant,
        "PRICED_IN_METHOD": "H1増収、FY2026ガイダンス、PQC商用化、パイプライン、量子投資、希薄化リスクを重み付けして推定。",
        "SURPRISE_UP": "QS7001/QVaultの初期商用売上、パイプライン契約化、FY2026売上上限超えが同時に確認されることです。",
        "SURPRISE_DOWN": "正式決算での費用増、商用化遅れ、追加希薄化、パイプライン未転換です。",
        "PRIMARY_RISK": "パイプラインが大きくても受注残ではなく、商用化が遅れるとテーマ期待が剥落しやすいことです。",
        "TIMELINE_ROWS": '<div class="time-row"><div class="time-date">2026/06/05</div><div class="time-dot"></div><div class="time-body"><b>量子プラットフォーム拡大</b><p>Root-to-Qubit戦略を説明。</p><div class="time-meta"><span class="chip blue">量子</span></div></div></div><div class="time-row"><div class="time-date">2026/07/06</div><div class="time-dot"></div><div class="time-body"><b>H1 2026予備決算</b><p>売上約$11M、前年比+120%。</p><div class="time-meta"><span class="chip">増収</span></div></div></div><div class="time-row"><div class="time-date">H2 2026</div><div class="time-dot"></div><div class="time-body"><b>QS7001/QVault商用化</b><p>初期商用売上と認証進捗を確認。</p><div class="time-meta"><span class="chip">最重要</span></div></div></div><div class="time-row"><div class="time-date">2027</div><div class="time-dot"></div><div class="time-body"><b>量産売上の拡大</b><p>顧客評価から契約・量産へ進むか。</p><div class="time-meta"><span class="chip">確認</span></div></div></div>',
        "CATALYST_CARDS": "".join(cards) + '<p class="small">※下の％は、この結果が出た後に市場が材料を評価し直した場合の上昇・下落幅の目安です。実際の値動きは地合い、直前の株価上昇、同時ニュースで変わります。</p>',
        "DEPENDENCY_ROWS": '<div class="signal"><div><b>認証と商用化</b><span class="up">連動</span></div><p>認証が進むほど顧客採用の確度が上がります。</p></div><div class="signal"><div><b>現金と希薄化</b><span class="flat">重要</span></div><p>現金余力は追い風ですが、追加調達は株価の重しです。</p></div><div class="signal"><div><b>量子投資</b><span class="down">注意</span></div><p>テーマ性は強い一方、短期売上との距離を確認します。</p></div>',
        "WATCH_ROWS": '<div class="signal"><div><b>H1正式売上</b><span class="up">重要</span></div><p>予備値約$11Mとの差を確認します。</p></div><div class="signal"><div><b>QS7001/QVault</b><span class="up">最重要</span></div><p>認証、顧客評価、初期商用売上。</p></div><div class="signal"><div><b>株式数</b><span class="down">注意</span></div><p>希薄化と資金使途を確認します。</p></div><div class="signal"><div><b>パイプライン</b><span class="flat">確認</span></div><p>商談から契約への転換。</p></div>',
        "ASSUMPTION_ROWS": tr("評価基準株価", usd(P0), "市場データで確認", DATE, "2026/07/28確認値") + tr("H1 2026売上", "約$11M", "会社リリース", "2026/07/06", "予備値、前年比+120%") + tr("FY2026売上見通し", "$27M〜$36M", "会社リリース", "2026/07/06", "前年比50〜100%成長") + tr("現金・短期投資", "約$495M", "会社リリース", "2026/06/30", "資金調達後"),
        "SOURCE_DETAILS": f'<ul><li>{source_link("会社概要", "about")}</li><li>{source_link("H1 2026予備決算リリース", "h1")}</li><li>{source_link("量子プラットフォーム発表", "quantum")}</li><li>{source_link("2025年Form 20-F", "annual")}</li><li>{source_link("株価・統計", "quote")}</li></ul><p><a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a></p>',
        "VALIDATION_DETAILS": "<p>PASS：会社概要、H1 2026予備決算リリース、量子プラットフォーム発表、2025年Form 20-F、株価・統計ページを確認。</p>",
        "UPDATE_HISTORY": f"<p>{DATE}：初版作成。H1 2026予備決算、FY2026見通し、QS7001/QVault、量子投資戦略を反映。</p>",
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
        "id": "sealsq-laes",
        "order": 11,
        "ticker": "LAES",
        "quoteSymbol": "LAES",
        "name": "シールエスキュー",
        "nameEn": "SEALSQ Corp",
        "market": "US",
        "marketLabel": "米国株",
        "exchange": "Nasdaq",
        "currency": "USD",
        "sector": "ポスト量子セキュリティ半導体・PKI",
        "themes": ["半導体", "量子", "サイバーセキュリティ"],
        "reports": {
            "company": {"path": "./stocks/sealsq-laes/company.html", "available": True},
            "valuation": {"path": "./stocks/sealsq-laes/valuation.html", "available": True},
            "catalysts": {"path": "./stocks/sealsq-laes/catalysts.html", "available": True},
        },
    }
    stocks_payload["stocks"] = [item for item in stocks_payload["stocks"] if item["id"] != "sealsq-laes"]
    stocks_payload["stocks"].append(stock)
    stocks_payload["stocks"].sort(key=lambda item: item["order"])
    stocks_path.write_text(json.dumps(stocks_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    prices_path = ROOT / "data" / "prices.json"
    prices_payload = json.loads(prices_path.read_text(encoding="utf-8"))
    prices_payload.setdefault("prices", {})["sealsq-laes"] = {
        "symbol": "LAES",
        "price": P0,
        "previousClose": PREVIOUS_CLOSE,
        "change": round(P0 - PREVIOUS_CLOSE, 4),
        "changePct": round((P0 - PREVIOUS_CLOSE) / PREVIOUS_CLOSE * 100, 4),
        "currency": "USD",
        "marketTime": "2026-07-28T19:47:48+00:00",
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "ok",
    }
    prices_payload["quoteCount"] = len(prices_payload["prices"])
    prices_path.write_text(json.dumps(prices_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    signals_path = ROOT / "data" / "signals.json"
    signals_payload = json.loads(signals_path.read_text(encoding="utf-8"))
    signals_payload["updatedAt"] = datetime.now(timezone.utc).isoformat()
    signals_payload.setdefault("signals", {})["sealsq-laes"] = {
        "position": SIGNAL_POSITION,
        "zone": "中立",
        "asOf": DATE,
        "components": {
            "valuation": round(BAND_POSITION, 1),
            "catalysts": CATALYST_SCORE,
            "businessRisk": BUSINESS_RISK_SCORE,
        },
        "reportRevision": "sealsq-laes-2026-08-13",
        "summary": "H1 2026予備売上は強く現金余力も大きい。QS7001/QVaultの商用化とパイプライン転換が確認できれば再評価余地がある一方、希薄化と小型株リスクは高い。",
    }
    signals_path.write_text(json.dumps(signals_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_reports()
    upsert_site_data()


if __name__ == "__main__":
    main()
