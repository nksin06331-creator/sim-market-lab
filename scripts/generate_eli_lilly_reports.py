"""Render LLY's three reports from one verified bundle and the supplied v6.2 templates.

Usage: python scripts/generate_eli_lilly_reports.py --materials /workspace/report-generation-materials
The materials directory is the report-generation-materials folder in the user-supplied ZIP.
This renderer does not fetch data, revise assumptions, or change stock publication flags.
"""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / 'data/reports/eli-lilly-lly.json'
OUT = ROOT / 'stocks/eli-lilly-lly'


def esc(value):
    return html.escape(str(value), quote=True)


def usd(value):
    return f'${value:,.2f}'


def pct(value):
    return f'{value:+.1f}%'


def row(*values):
    return '<tr>' + ''.join(f'<td>{v}</td>' for v in values) + '</tr>'


def bullets(*values):
    return ''.join(f'<li>{esc(v)}</li>' for v in values)


def detail(title, text):
    return f'<details><summary>{esc(title)}</summary><p>{text}</p></details>'


def guide_box(title, text):
    return f'<div class="info-box"><div class="info-title">{esc(title)}</div><div class="info-text">{text}</div></div>'


def signal(title, text):
    return f'<div class="signal"><div><b>{esc(title)}</b></div><p>{text}</p></div>'


def render(materials, name, values):
    template = (materials / name).read_text(encoding='utf-8')
    required = set(re.findall(r'{{([A-Z0-9_]+)}}', template))
    if missing := required - values.keys():
        raise ValueError(f'{name}: missing {sorted(missing)}')
    # Only placeholder substitution. Keep the supplied CSS, HTML skeleton and JS unchanged.
    return re.sub(r'{{([A-Z0-9_]+)}}', lambda m: values[m[1]], template)


def build(materials):
    d = json.loads(BUNDLE.read_text(encoding='utf-8'))
    meta, cap, sc, cat = (d[x] for x in ['meta', 'capital_structure', 'scenario', 'catalyst_report'])
    p = meta['price']; c = sc['computed']; cases = sc['cases']; bear, base, bull = cases
    date = meta['valuation_date']; company = 'イーライリリー'; ticker = meta['ticker']
    claim = {x['id']: x['statement'] for x in d['claims']}
    back = '<a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>'
    sources = '<ul>' + ''.join(f'<li><a href="{esc(x["url"])}" target="_blank" rel="noopener noreferrer">{esc(x["id"] + "：" + x["title"])}</a>（取得：{esc(x["accessed_at"][:10])}）</li>' for x in d['sources']) + '</ul>'
    warnings = '注意：2027年の利益・倍率・確率はこのレポートの仮定で、会社予想ではありません。時点株式数は信託と潜在株を調整した推定です。個別材料の価格幅は短期予測ではなく、重複するため足し合わせません。'
    warn_band = f'<div class="wrap"><p class="notice">{warnings}</p></div>'
    disclaimer = '情報提供・教育目的の条件付き試算です。投資助言や売買推奨ではありません。薬価、治験、安全性、競合、為替、倍率で結果は大きく変わります。配当は価格比較へ含めていません。'
    basis = f'分析基準株価 {usd(p)}／{esc(meta["price_as_of"])}（米国2026/10/30取引分）。分析値は固定。'
    common = dict(COMPANY_NAME=company, TICKER=ticker, EXCHANGE='NYSE／USD', VALUATION_DATE=date, CURRENT_PRICE=usd(p), CURRENT_PRICE_NOTE='米国2026/10/30取引分', DISCLAIMER=disclaimer, FOOTER_NOTE=f'{basis}<br>{back}')
    # The guide deliberately excludes scenario prices, probabilities and valuation judgements.
    terms = [
        ('GLP-1', '食後に働くホルモンの経路です。血糖・食欲に関係し、LLYの代謝疾患治療の基盤です。'),
        ('GIP', 'GLP-1と同様に血糖調節へ関わる経路です。TirzepatideはGIPとGLP-1の両方を標的とします。'),
        ('Tirzepatide', 'Mounjaro・Zepboundの同一有効成分です。ブランド違いを独立した新薬として数えません。'),
        ('Orforglipron', '経口GLP-1受容体作動薬です。会社はFoundayoとして米国肥満症で販売開始と説明しています。'),
        ('Retatrutide', 'GLP-1・GIP・グルカゴンの3経路を標的にする開発中の薬です。既存の承認薬と区別します。'),
        ('保険償還', '保険が薬の費用を負担する仕組みです。対象患者・自己負担・割引が採用と実現価格を左右します。'),
        ('実現価格', '割引やリベートを差し引いた実際の売上単価です。定価が同じでも収益は変わります。'),
        ('非GAAP利益', '会社が一定項目を調整した利益です。米国会計基準の純利益と置き換えて扱いません。'),
        ('買収IPR&D', '買収した開発途中の研究資産に関する費用です。LLYでは非GAAP EPSにも含まれる項目があるため確認が必要です。'),
        ('製造品質基準', '薬の製造に必要な品質管理です。工場の建設完了だけで承認・商業出荷が保証されるわけではありません。'),
        ('希薄化', '株式報酬などで1株の取り分が薄まることです。信託株式・加重平均株式・時点株式の定義を揃えます。'),
        ('主要評価項目', '治験で有効性を判定する中心の指標です。達成だけで承認や販売成功が確定するわけではありません。'),
    ]
    guide = dict(COMPANY_NAME=company, TICKER=ticker, INDUSTRY='医薬品・糖尿病・肥満症治療', DATE=date, TAGLINE=esc(d['guide']['tagline']),
        HERO_TAGS=''.join(f'<span class="hero-tag">{x}</span>' for x in ['米国株', 'NYSE', '糖尿病・肥満症', '創薬・製造・販売']),
        HERO_STATS=''.join(f'<div class="stat"><div class="stat-value">{v}</div><div class="stat-label">{label}</div><div class="stat-note">{note}</div></div>' for v,label,note in [(usd(p),'評価基準株価','米国2026/10/30取引分'),('$24.397B','2026年3Q売上','前年同期比39%増 [S1]'),('$6.451B','2026年3Q純利益','米国会計基準 [S1]'),('$16.075B','Mounjaro＋Zepbound','2026年3Q売上 [S1]')]),
        SEC1_TLDR=bullets('医薬品を研究開発し、製造・販売して収益を得ます。','現在の成長の中心は糖尿病・肥満症治療薬です。','数量拡大と薬価下落の両方を確認する必要があります。'),
        SEC1_FACTS='<div class="facts-table">' + ''.join(guide_box(a,esc(b)) for a,b in [('正式社名・上場','Eli Lilly and Company／NYSE: LLY／USD'),('創業・本社・決算','1876年創業、1901年法人化／インディアナポリス／12月決算 [S4]'),('直近四半期','2026年7～9月：売上243.97億ドル、純利益64.51億ドル [S1]'),('情報の基準','2026年10月31日JST時点。最新10-Qは10月29日提出 [S2]')])+'</div>',
        SEC1_CARDS='<div class="card-grid">'+''.join(guide_box(a,b) for a,b in [('何をする会社','薬の発見・臨床試験・承認取得・製造・販売を一貫して行います。'),('主力','MounjaroとZepboundは同一成分の異なるブランド。合計売上は3Q全体の約65.9%。[S1]'),('直近業績','3Q売上39%増、GAAP純利益16%増。数量53%増を実現価格15%減が一部相殺。[S1]'),('注目点','Foundayo販売、保険アクセス、次世代薬と製造能力。承認済みの事実と今後の課題を分けます。[S1–S3]')])+'</div>',
        SEC1_BIZMODEL='<div class="info-row">'+guide_box('販売の仕組み','医療機関・薬局・卸などを通じて患者へ届けます。米国では保険者や給付管理会社との採用・割引条件が実現価格に影響します。[S4]')+guide_box('利益の使い道','研究開発、工場、提携・買収へ再投資します。3Qの研究開発費は42.47億ドル、取得研究開発費は41.81億ドルでした。[S1]')+'</div>',
        SEC1_HIGHLIGHT='<div class="highlight-box">成長率だけでなく、継続する製品売上と一時的な売上押上げを分けることが重要です。3Qは約9億ドルの押上げ要因を含みます。[S1]</div>',
        SEC2_ICON='◇', SEC2_LABEL='業界', SEC2_TITLE='需要と薬価で決まる収益', SEC2_SUB='患者が増えても、売上が同率で増えるとは限らない',
        SEC2_TLDR=bullets('患者への有効性・安全性に加え、保険採用と供給が重要です。','処方量と実現価格を別々に見ます。','市場規模やシェアの未確認数値は置いていません。'),
        SEC2_CONTENT='<div class="info-row">'+guide_box('需要','糖尿病・肥満症など慢性疾患の治療を支えます。患者の継続使用、自己負担、医師の判断が需要を左右します。[S4]')+guide_box('支払う人','患者・民間保険・公的保険が関わります。アクセス拡大は数量を増やしても割引拡大で単価を下げ得ます。[S1–S3]')+guide_box('供給と規制','製造・品質・流通と承認範囲が販売可能量を制約します。着工と出荷を混同しません。[S2]')+'</div>',
        SEC3_LABEL='製品', SEC3_TITLE='販売中の薬と開発中の薬', SEC3_SUB='製品ブランドと有効成分を分ける',
        SEC3_TLDR=bullets('Mounjaro・Zepboundが主要な売上源です。','Foundayoは経口薬として販売拡大が焦点です。','Retatrutideは開発中で、承認済みとは扱いません。'),
        SEC3_CONTENT='<div class="table-wrap"><table class="compare-table"><thead><tr><th>成分・製品</th><th>領域・段階</th><th>見る点</th></tr></thead><tbody>'+row('Tirzepatide／Mounjaro・Zepbound','糖尿病・肥満症など／販売中','保険採用、数量、単価、供給。用途は地域・承認で異なる。')+row('Orforglipron／Foundayo','経口GLP-1／会社は米国肥満症で発売済みと報告','既存注射薬との置換と純増、追加適応・地域。')+row('Retatrutide','代謝疾患／開発中','3相データ、安全性、申請・審査。次の確定日は未確認。')+row('Verzenio・Kisunlaなど','がん・神経疾患など／販売ポートフォリオ','代謝疾患以外の収益分散。ただし薬ごとの承認・安全性を確認。')+'</tbody></table></div><p>[S1–S4] 薬効や適応を医療上の使用推奨として示すものではありません。</p>',
        SEC4_LABEL='財務・規制', SEC4_TITLE='営業キャッシュフローと大型投資', SEC4_SUB='黒字でも投資・借入・品質管理を確認',
        SEC4_TLDR=bullets('2026年1～9月営業CFは274.20億ドル。','9月末借入は約495.03億ドル、現金48.85億ドル。','工場は建設→認証→稼働→出荷の順で確認します。'),
        SEC4_CONTENT='<div class="info-row">'+guide_box('財務（9月末）','現金48.85億ドル、短期借入等25.17億ドル、長期借入469.86億ドル。単純な借入－現金は446.18億ドル。全てUSD。[S2]')+guide_box('投資と買収','1～9月の事業開発支払は182億ドルと会社説明。製造能力と研究開発の強化には支出が先行します。[S2]')+guide_box('株式数の定義',esc(claim['SHARES'])+' [S2,S4] 期中平均と時点の差があるため推定です。')+'</div><p>現金・借入を評価へ重複加算しないこと、承認・品質・製造日程を別々に追うことが重要です。</p>',
        SEC5_LABEL='競合', SEC5_TITLE='効果だけでなく採用・価格・供給で競う', SEC5_SUB='同じ患者課題に対する治療の選択肢',
        SEC5_TLDR=bullets('Novo Nordiskなどの既存薬・新薬と競争します。','比較試験は用量・対象患者・期間を揃えて読みます。','競合の最新売上やシェアは未調査のため数値比較していません。'),
        SEC5_CONTENT='<div class="table-wrap"><table class="compare-table"><thead><tr><th>競争軸</th><th>LLYで見る点</th><th>代替治療との比較</th></tr></thead><tbody>'+row('効果と安全性','臨床試験・実臨床での有効性と継続性','試験をまたぐ単純な優劣付けは避ける。')+row('使いやすさ','注射薬と経口薬、投与頻度・忍容性','経口なら必ず選ばれるとは限らない。')+row('保険と価格','自己負担・採用条件・割引後単価','安価な選択肢、競合の保険採用が影響。')+row('供給','品質・稼働・配送の安定性','供給不足は患者の他剤への切替につながる。')+'</tbody></table></div><p>競争相手の特定と業界の販売構造は年次開示[S4]。競合が劣るという断定や未確認のシェアは置いていません。</p>',
        SEC6_TLDR=bullets('実現価格は割引後の単価です。','非GAAP利益と会計上の利益は異なります。','開発中の薬はデータが良くても承認・販売が保証されません。'),
        SEC6_CONTENT='<div class="term-list">'+''.join(f'<details class="term-item"><summary class="term-header"><span class="term-name">{esc(a)}</span><span class="term-arrow">⌄</span></summary><div class="term-body"><p>{esc(b)}</p></div></details>' for a,b in terms)+'</div>',
        SEC7_TLDR=bullets('処方量増がネット価格低下を上回るか。','臨床・承認・製造拡大が収益へつながるか。','買収費・設備投資と借入増のバランスを確認。'),
        SEC7_CONTENT='<div class="info-row">'+guide_box('追い風','主力薬の数量拡大、経口薬の販売、保険アクセス。3Q売上成長は確認済みですが将来の継続を保証しません。[S1–S3]')+guide_box('中立・要確認','規制進捗と設備投資は収益化までの時間が必要です。日付未確認の承認を予定表へ作りません。[S2,S3]')+guide_box('注意','実現価格低下、主力薬集中、競合、訴訟・安全性、借入と買収費。これらが複数同時に起こる可能性があります。[S2,S4]')+'</div>'+detail('次に確認する指標','製品別売上、数量と価格、粗利率、研究開発費、営業CF、設備投資、借入、工場稼働と公式な規制判断。')+detail('主要出典・情報の基準',sources+f'<p>{basis}</p><p>{back}</p>'))
    own_per = p / (120e9*.36/895e6)
    guidance_per = p / 35.5
    calc_rows = ''.join(row(name, f'${rev/1e9:g}B', f'{margin*100:g}%', f'${rev*margin/1e9:g}B', f'{pe:g}倍', f'{shares/1e6:g}百万株', usd(case['price'])) for case,(name,rev,margin,pe,shares) in zip(cases,[('悲観',105e9,.32,26,900e6),('標準',120e9,.36,32,895e6),('楽観',135e9,.39,38,890e6)]))
    assumptions = [('評価基準株価',usd(p),'市場データ',meta['price_as_of']+' [S5]'),('現在株式数',f'{cap["diluted_shares"]/1e6:.3f}百万株','このレポートの推定',claim['SHARES']+' [S2,S4]'),('現在株主価値',f'${cap["market_cap"]/1e9:,.2f}B','このレポートの推定','評価株価×推定株式数。市場公表時価総額の転載ではない。'),('2026年会社予想','売上$91～92B／非GAAP EPS$35～36','会社の目標・予定','9月末後の取得研究開発費を含まない。[S1]'),('2027年利益・倍率','売上×純利益率×PER','このレポートの推定',claim['MODEL']),('希薄化と買戻し','900／895／890百万株','このレポートの推定',claim['DILUTION']),('現金・借入','$4.885B／$49.503B','公式情報で確認済み','2026年9月末。PER法では株主価値へ二重加減しない。[S2]'),('確率','25%／50%／25%','このレポートの推定','2026年3Qの数量成長を標準中心とし、薬価・規制・供給の上下不確実性を対称に置く主観配分。統計確率ではない。')]
    watch = ''.join(signal(x['item'],esc(x['frequency']+'：'+x['update_trigger'])) for x in cat['watch_items'])
    vals = dict(common, METHOD='2027年調整後利益×PER（利益倍率）', VERDICT_STATUS='成長と期待負担を分けて見る', VERDICT_LINE_1=f'評価基準株価は悲観～楽観帯の{c["display_band_position_pct"]:.1f}%地点。標準価格は{usd(base["price"])}です。', VERDICT_LINE_2='主力薬の成長は強い一方、薬価低下・買収費・規制・倍率低下を考慮します。会社予想と当方の2027年仮定を分けます。', SCORE=str(c['supplemental_score']), BASE_PRICE=usd(base['price']), BASE_DELTA=pct((base['price']/p-1)*100), EXPECTED_VALUE=usd(c['expected_price']), EXPECTED_DELTA=pct(c['expected_delta_pct']), RISK_CLASS='やや高い', RISK_NOTE='規制・薬価と広い評価レンジに依存', WARN_BAND=warn_band, WARN_MESSAGE=warnings, SNAPSHOT_LEAD=f'分析時点は{date}。株価は米国10月30日取引分。3ケースは2027年末を対象とする条件付き評価です。', BAND_POSITION=f'{c["display_band_position_pct"]:.1f}%', ZONE_JUDGE='悲観と標準の間', ZONE_NOTE='基準価格は固定。現在株価が動いても利益前提・期待値・分析バーを自動再計算しません。', MARKET_SCORE=str(c['market_score']), OWN_SCORE=str(c['own_score']), MARKET_REVERSE_NOTE=f'2027年標準EPS {usd(120e9*.36/895e6)}を固定すると、現値に対応するPERは{own_per:.1f}倍。会社の2026年非GAAP EPS中点$35.50基準では約{guidance_per:.1f}倍です。期間が異なるため両倍率を同じ予想として扱いません。', SCENARIOS_LEAD='安定黒字の製薬事業としてPER法を採用。未承認薬を個別に評価したrNPV（成功確率調整価値）の足し算は行いません。開発の不確実性は事業条件と評価倍率の幅に反映し、同じ成功確率を重ね掛けしません。', PRICE_ZONE_ROWS=''.join(f'<div class="zone"><div><b>{a}</b></div><p>{b}</p></div>' for a,b in [(f'{usd(bear["price"])}未満','悲観モデルより低い価格。事業前提の悪化有無を再確認。'),(f'{usd(bear["price"])}～{usd(base["price"])}','悲観と標準の間。標準達成を保証する価格ではない。'),(f'{usd(base["price"])}～{usd(bull["price"])}','販売・利益率・成長持続の強い条件が必要。'),(f'{usd(bull["price"])}超','楽観モデル外。さらに強い業績か高倍率の根拠が必要。')]), SIGNAL_ROWS=signal('数量と実現価格','3Qは数量53%増、価格15%減。単価と継続使用を確認。[S1]')+signal('経口薬・保険採用','Foundayo発売とアクセス拡大は進行中。価格低下との両面。[S2,S3]')+signal('開発・規制','Retatrutideは開発中。未確認の申請・承認日を置かない。[S2,S3]')+signal('供給・費用・借入','工場増強の品質・稼働と買収費を確認。[S1–S3]'), POSITIVES=bullets('3Q売上39%増。主力薬の数量拡大を確認。[S1]','2026年通期売上会社予想を910～920億ドルへ引上げ。[S1]','1～9月営業CF274.20億ドルと製造・開発への投資能力。[S2]'), CONCERNS=bullets('実現価格15%減。数量拡大だけでは利益成長を保証しない。[S1]','主力2ブランドで3Q売上の約65.9%。同一成分への集中。[S1]','買収IPR&D費用と大型設備投資、9月末借入約495億ドル。[S1,S2]','倍率・利益率仮定への感応度が高い。競合・規制・安全性にも依存。[S2,S4]'), FORMULA=esc(sc['method_explanation']), CALC_TABLE_HEAD=''.join(f'<th>{x}</th>' for x in ['ケース','2027年売上','純利益率','調整後純利益','PER','希薄化株式','1株価値']), CALC_TABLE_ROWS=calc_rows, CALC_NOTICE='米国会計基準ではなくモデル調整後純利益を使います。企業買収・薬価・製造費・税負担でGAAP利益との差は拡大し得ます。倍率26～38倍は市場予想ではなく感応度用の評価仮定。現金・借入を別加減せず、将来株式数に報酬・買戻しを反映します。', CONDITIONS=''.join(detail(f'{name}：{usd(case["price"])}／確率{case["probability"]*100:g}%',' '.join(esc(x) for x in case['conditions'])) for name,case in zip(['悲観','標準','楽観'],cases)), SENSITIVITY_HEAD='<th>変数</th><th>低位</th><th>標準</th><th>高位</th>', SENSITIVITY_ROWS=''.join(row(esc(x['variable']),*(usd(v) for v in x['result_prices'])) for x in sc['sensitivity']), SENSITIVITY_NOTE='売上108／120／132十億USD（利益率36%、PER32倍固定）、PER26／32／38倍（売上120十億USD、利益率36%固定）。株式895百万株。他条件を固定する局所感応度で、独立確率を意味しません。', DIST_LEAD='モンテカルロは未実施。3点の離散分布のみを表示します。', DIST_ROWS=''.join(signal(f'{name}：{usd(case["price"])}',f'このレポートの主観確率 {case["probability"]*100:g}%') for name,case in zip(['悲観','標準','楽観'],cases)), DIST_SUMMARY=f'25%／50%／25%の合計100%。確率でならした価格は{usd(c["expected_price"])}。保証価格ではありません。', ENDPOINT_RR=f'{c["endpoint_rr"]:.2f}倍', WATCH_ROWS=watch, ASSUMPTIONS_ROWS=''.join(row(esc(a),esc(b),esc(k),esc(note)) for a,b,k,note in assumptions), DEEPDIVE_DETAILS=detail('株式数・信託・希薄化',esc(claim['SHARES'])+' '+esc(claim['DILUTION']))+detail('利益率と倍率の仮定',esc(claim['MARGIN'])+' '+esc(claim['MULTIPLE']))+detail('独立した照合と未取得情報',f'2026年会社EPS中点でのPERは{guidance_per:.1f}倍、モデル2027年標準EPSでは{own_per:.1f}倍です。これは同じ式の期間照合であり独立評価法による裏付けではありません。独立したDCFや同業倍率の最新比較は未実施。市場コンセンサスを会社予想の代用で表示していません。')+detail('市場データの補助情報',esc(claim['QUOTE_STATS'])+' これらを総合判定や材料の期待割合へ直接使っていません。')+detail('メインページの3レポート総合判定',esc(claim['SIGNAL'])+' 株価シナリオの補助スコア53とは別の尺度です。')+detail('出典と更新履歴',sources+f'<p>{date}初版。全ての分析値は共通bundleから生成。</p>'))
    for name,case in zip(['BEAR','BASE','BULL'],cases):
        rev,margin,pe = {'BEAR':(105,.32,26),'BASE':(120,.36,32),'BULL':(135,.39,38)}[name]
        vals.update({f'{name}_PRICE':usd(case['price']),f'{name}_PROB':f'{case["probability"]*100:g}%',f'{name}_DELTA':pct((case['price']/p-1)*100),f'{name}_DL_ROWS':''.join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a,b in [('売上',f'${rev}B'),('調整後純利益率',f'{margin*100:g}%'),('PER',f'{pe}倍'),('希薄化株式',f'{case["diluted_shares"]/1e6:g}百万株')])})
    overall=cat['overall_priced_in']; lo,hi=overall['percent_range']
    labels={'SUCCESS':'期待以上','INLINE':'ほぼ想定どおり','FAILURE':'期待外れ・遅延'}
    cards=[]
    for event in cat['catalysts']:
        outcomes=''.join(f'<div class="outcome"><h4>{labels[o["label"]]}</h4><div class="impact">{usd(o["price_range"][0])}～{usd(o["price_range"][1])}</div><p>基準価格比 {pct(o["price_change_pct_range"][0])}～{pct(o["price_change_pct_range"][1])}</p><p>{esc(o["conditions"][0])}</p><p>{esc(o["method_note"])}</p></div>' for o in event['outcomes'])
        ex=event['priced_in']['non_quantified_explanation']
        nonquant=f'<div class="priced unknown"><b>個別の期待割合は出していません</b><p>出していない理由：{esc(ex["reason"])}</p><p>足りない情報：{esc("、".join(ex["missing_information"]))}</p><p>次に見る数字：{esc("、".join(ex["next_checks"]))}</p><p>再計算方法：{esc(ex["recalculation_method"])}</p></div>'
        cards.append(f'<article class="catalyst-card"><div class="catalyst-head"><h3>{esc(event["title"])}</h3><span class="chip">重要度{event["importance"]}</span></div><div class="date-box"><b>{esc(event["date"]["display_text"])}</b></div><p>{esc(event["plain_language"])}</p><div class="mechanism">'+''.join(f'<span>{esc(x)}</span>' for x in event['mechanism'])+f'</div><p>共通モデルの条件付き再評価です。市場コンセンサスとの実測比較ではなく、下記の当方条件との比較です。結果別の主観確率は表示しません。</p><div class="outcomes">{outcomes}</div>{nonquant}'+detail('根拠・反証・更新条件',f'<p>出典：{esc("、".join(event["source_ids"]))}</p><p>根拠：{esc("、".join(event["priced_in"]["evidence_for"]))}</p><p>反証：{esc("、".join(event["priced_in"]["evidence_against"]))}</p><p>先行指標：{esc("、".join(event["leading_indicators"]))}</p><p>材料出尽くし：{esc(event["sell_the_news_risk"])}</p><p>資金需要：{esc(event["financing_risk"])}</p><p>更新条件：{esc("、".join(event["update_triggers"]))}</p>')+detail('価格幅に用いた手法の検討','<ul>'+bullets(*[{'ENTERPRISE_VALUE_DELTA':'企業価値差分','CONDITIONAL_SCENARIO':'共通シナリオ再評価','CONSENSUS_REVISION':'市場予想改定','SAME_COMPANY_EVENT_STUDY':'同社イベント比較','PEER_EVENT_STUDY':'同業イベント比較'}[x['method']]+'：'+('採用' if x['status']=='USED' else '不採用・適用外')+'。'+x['reason'] for x in event['outcomes'][0]['quantification_attempts']])+'</ul>')+'</article>')
    cv=dict(common, LAST_UPDATED=date, REPORT_STATUS='販売・開発・供給の進捗を確認', SUMMARY_LINE_1='販売と保険アクセス、Retatrutideの開発・規制、製造能力を確認します。完了済みの肥満症向け経口薬承認は未来イベントに数えません。', SUMMARY_LINE_2='同じ成長価値への影響を1グループに集約。個別割合の平均や価格幅の足し算をしません。', OVERALL_PRICED_IN=f'{lo:.0f}～{hi:.0f}%', OVERALL_PRICED_LABEL='共通成長モデルでの期待の入り方', PRICED_IN_CONFIDENCE='低い', NEXT_CATALYST_TITLE='販売・保険採用', NEXT_CATALYST_WINDOW='進行中・各四半期に確認', DATE_CONFIDENCE='日程未確定を含む', CATALYST_COUNT='3件', WARN_BAND=warn_band, NO_CATALYST_NOTICE='', OVERALL_PRICED_BLOCK=f'<div class="priced"><div class="priced-head"><b>{lo:.0f}～{hi:.0f}%</b><span>このレポートの条件付き推定</span></div><p>中心値{overall["raw_implied_pct"]:.1f}%。個別イベントの成功確率や短期リターンではありません。</p><p>{esc(overall["method_note"])}</p></div>', PRICED_IN_METHOD='失敗側の既存事業価値を残し、3材料の共通成功増分を1回だけ計上する価値端点方式。', SURPRISE_UP='主力薬の数量と経口薬の純増が薬価低下を上回り、純利益率・供給効率が標準モデル以上へ進む。', SURPRISE_DOWN='値引き・継続率・競合・安全性・規制・製造費で2027年利益が下振れする。', PRIMARY_RISK='同じ代謝疾患成長に依存する材料が多く、薬価・供給・規制が同時に悪化する可能性。', TIMELINE_ROWS=''.join(f'<div class="time-row"><div class="time-date">{"進行中" if x["status"]=="ONGOING" else "時期未定"}</div><div class="time-dot"></div><div class="time-body"><b>{esc(x["title"])}</b><p>{esc(x["date"]["display_text"])}</p></div></div>' for x in sorted(cat['catalysts'],key=lambda x:x['status']=='TBD')), CATALYST_CARDS=''.join(cards), DEPENDENCY_ROWS='<p>販売・保険採用、次世代薬、製造拡大を「代謝疾患薬の共通成長」1グループに束ねます。需要・供給・承認は同じ患者と利益に影響するため、個別の価格幅と割合を合算しません。</p><p>全体の失敗側と成功側は2027年株主価値モデルの端点です。個別ケースは標準株式数895百万株、全体ケースは900／895／890百万株を使うため、市場逆算の位置と全体期待中心には差が出ます。</p>', WATCH_ROWS=watch, ASSUMPTION_ROWS=''.join(row(esc(a),esc(b),esc(k),date,esc(note)) for a,b,k,note in assumptions), SOURCE_DETAILS=sources, VALIDATION_DETAILS='<p>共通JSONの形式、算術、ID、日付、確率、依存関係、HTML未置換・安全性を検証。次の3点は公開注記付きの制約です。</p><ul>'+bullets(*d['validation_summary']['messages'])+'</ul>', UPDATE_HISTORY=f'<p>{date} 初版。2026年3Q決算・10-Q・説明会資料と米国10月30日株価を共通bundleへ固定。</p>')
    OUT.mkdir(parents=True,exist_ok=True)
    for name,template,mapping in [('company.html','template_stock_guide_v4_unified.html',guide),('valuation.html','template_scenario_v4_unified.html',vals),('catalysts.html','template_catalyst_v1_unified.html',cv)]:
        text=render(materials,template,mapping)
        if re.search(r'{{[A-Z0-9_]+}}',text):raise ValueError('Unresolved placeholder')
        (OUT/name).write_text(text,encoding='utf-8')
        print(OUT/name)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--materials',type=Path,default=ROOT.parent/'report-generation-materials')
    build(parser.parse_args().materials)
