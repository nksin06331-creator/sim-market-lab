"""Generate six evidence-backed reports from frozen SpaceX/Tesla inputs.

python scripts/generate_spacex_tesla_reports.py
No network access. Inputs contain source URLs, financial definitions and model assumptions.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from copy import deepcopy
from generate_eli_lilly_reports import esc, row, bullets, detail, guide_box, signal, render
from report_support.bundle_validator import Validator, calc

ROOT = Path(__file__).resolve().parents[1]
MATERIALS = ROOT.parent / 'report-generation-materials'
DATE = '2026-11-28'
HORIZON = '2027-12-31'
REFS = ['S1','S2']
LABELS = ['悲観','標準','楽観']
OUT_LABELS = {'SUCCESS':'期待以上','INLINE':'ほぼ想定どおり','FAILURE':'期待外れ・遅延'}


def usd(x): return f'${x:,.2f}'
def bn(x): return f'{x/1e9:,.2f}十億ドル'
def pct(x): return f'{x:+.1f}%'
def boxes(items): return '<div class="info-row">'+''.join(guide_box(a,esc(b)) for a,b in items)+'</div>'


def model(c, i, sales=None, multiplier_scale=1):
    revenues = c['sales'][i] if sales is None else sales
    ev = sum(a*b*multiplier_scale for a,b in zip(revenues,c['multiples'][i]))
    eq = ev+c['future_cash'][i]+c['other_assets']-c['minimum_cash']-c['future_debt'][i]-c['minority']
    return ev,eq,eq/c['shares'][i]


def inputs_text(c,i,sales=None):
    revenues=c['sales'][i] if sales is None else sales
    segments=' ／ '.join(f'{name}：売上{bn(rev)}×{mul:g}倍、営業利益率{margin*100:g}%' for name,rev,mul,margin in zip(c['segments'],revenues,c['multiples'][i],c['margins'][i]))
    return segments+f'。自由現金・短期証券{bn(c["future_cash"][i])}、その他資産{bn(c["other_assets"]) }、最低運転現金{bn(c["minimum_cash"]) }、負債等{bn(c["future_debt"][i])}、非支配等{bn(c["minority"]) }、将来株式{c["shares"][i]/1e9:g}十億株。'


def make_bundle(c):
    p=c['price'];now=c['source_cutoff'];n=c['diluted'];claims=[]
    def claim(id,text,kind='CONFIRMED',refs=REFS,formula=None):
        claims.append(dict(id=id,statement=text,classification=kind,as_of=DATE,source_ids=refs,calculation_id=formula,confidence='LOW' if kind=='MODEL_ESTIMATE' else 'HIGH'))
    for id,key in [('IDENTITY','identity'),('BUSINESS','business'),('FINANCIAL','financial'),('RISK','risk')]:claim(id,c[key])
    claim('GUIDANCE',c['guidance'],'COMPANY_GUIDANCE')
    claim('CAPITAL',c['capital'],'MODEL_ESTIMATE',REFS,'latest point shares plus disclosed/proxy dilution; securities-by-security TSM unverified')
    claim('LIQUIDITY',c['liquidity'],'MODEL_ESTIMATE',REFS,'cash+securities-minimum operating cash; disclosed cash-flow period; no assumed unused-facility cash')
    claim('ASSETS',c['asset_note'],'MODEL_ESTIMATE',['S1'],'disclosed digital assets plus cost and accumulated fair-value gain of the equity investment')
    claim('COMPETITION',c['competitors'],'MODEL_ESTIMATE',REFS,'qualitative comparison by customer function; market share and multiples unverified')
    claim('MODEL',c['model_note'],'MODEL_ESTIMATE',REFS,'sum(segment_sales*segment_EV_sales)+future_cash+other_assets-minimum_cash-future_debt-minority, divided by future shares')
    claim('FUNDING',c['funding_note'],'MODEL_ESTIMATE',REFS,'future_cash=current_cash+current_securities+OCF-capex+future_debt-current_debt')
    claim('PROB','悲観35%・標準45%・楽観20%。実績と事業化リスクを踏まえた粗い主観配分。高い成長倍率と資金・規制条件の不確実性から下側を厚く置くが統計的成功率ではない。','MODEL_ESTIMATE',REFS,'subjective 0.35+0.45+0.20=1')
    claim('QUOTE',f'基準株価{usd(p)}、時刻{c["price_as_of"]}。米国取引時間中の時点値で終値とは限らない。','CONFIRMED',['S5'])
    cases=[]
    for i,label in enumerate(['BEAR','BASE','BULL']):
        ev,eq,price=model(c,i);net_reinvestment=c['future_cash'][i]-c['cash']-c['securities']-(c['future_debt'][i]-c['debt'])
        conditions=[inputs_text(c,i),f'現在から対象時点までの営業CF−設備投資等の純額を{bn(net_reinvestment)}とする現金ブリッジ。新規借入増減{bn(c["future_debt"][i]-c["debt"])}は現金にも反映する。',c['funding_note'],'事業倍率は同業観測値ではなく当方の将来成長・資本収益に対する仮定。営業利益率と合わせて解釈し、最低運転現金を非事業資産として二重に加算しない。']
        cases.append(dict(label=label,probability=c['probs'][i],enterprise_value=ev,equity_value=eq,diluted_shares=c['shares'][i],price=price,conditions=conditions,assumption_claim_ids=['MODEL','CAPITAL','FUNDING','ASSETS','PROB']))
        claim('MODEL_'+label,'2027年末の'+LABELS[i]+'：'+''.join(conditions),'MODEL_ESTIMATE',REFS,'SOTP model; segment revenues*EV/Sales and explicit balance-sheet bridge')
    xs=[v['price'] for v in cases];expected=calc.expected_price(xs,c['probs']);raw,band=calc.band_position(p,xs[0],xs[2])
    computed=dict(expected_price=expected,expected_delta_pct=calc.pct_change(expected,p),raw_band_position_pct=raw,display_band_position_pct=band,endpoint_rr=calc.endpoint_rr(p,xs[0],xs[2]),market_score=calc.market_score(p,xs[0],xs[2]),own_score=calc.own_score(expected,xs[0],xs[2]),supplemental_score=calc.supplemental_score(p,expected,xs[0],c['probs'][0]))
    sensitivity=[dict(variable='全セグメント売上倍率（標準の比率）',low=.8,base=1,high=1.2,result_prices=[model(c,1,multiplier_scale=x)[2] for x in [.8,1,1.2]]),dict(variable='全セグメント売上（標準の比率）',low=.8,base=1,high=1.2,result_prices=[model(c,1,sales=[v*x for v in c['sales'][1]])[2] for x in [.8,1,1.2]])]
    attempts=[dict(method=m,status=s,reason=t) for m,s,t in [('ENTERPRISE_VALUE_DELTA','REJECTED','同じ設備・顧客・利益を共有するためイベント単独の価値増分を分離できない。'),('CONDITIONAL_SCENARIO','USED','対象セグメント売上だけを結果別に変更し、他の標準入力を固定して共通SOTP式で再計算できる。'),('CONSENSUS_REVISION','NOT_APPLICABLE','同時点の独立した市場予想改定データを取得していない。'),('SAME_COMPANY_EVENT_STUDY','NOT_APPLICABLE','発表前後の異常リターンと同時ニュースを分離した比較標本を作成していない。'),('PEER_EVENT_STUDY','NOT_APPLICABLE','事業構成・規制・資本条件が一致する同業イベント標本を確認していない。')]]
    explanation=dict(reason='複数の材料は同じ顧客・設備・利益と将来倍率に重なり、イベント除外時の独立価値を一次資料から一意に切り出せない。',missing_information=['材料別の増分営業CFと設備費','重複を除いた顧客・売上と独立価値'],next_checks=['事業別収益と設備・資金開示','公式な顧客・運行・開発実績'],recalculation_method='材料を除いたセグメント価値と追加時の価値を同じ倍率・株式・資金条件で再評価できた段階で、基準時価総額との差から個別期待を逆算する。')
    catalysts=[]
    for index,event in enumerate(c['events'],1):
        cid='C'+str(index);claim(cid,event['description'],'CONFIRMED',REFS)
        claim(cid+'_CONDITIONS',' ／ '.join(event[k] for k in ['success','inline','failure']),'MODEL_ESTIMATE',REFS,'conditional segment revenue ranges; all other base-case inputs fixed')
        outs=[]
        for j,label in enumerate(['SUCCESS','INLINE','FAILURE']):
            prices=[];input_notes=[]
            for revenue in event['ranges'][j]:
                sales=list(c['sales'][1]);sales[event['segment']]=revenue;prices.append(model(c,1,sales=sales)[2]);input_notes.append(inputs_text(c,1,sales))
            direction='UP' if min(prices)>p else 'DOWN' if max(prices)<p else 'MIXED'
            note='2027年末の条件付き再評価で、発表直後の値動き予測ではない。対象事業売上のみ変更、倍率・他事業売上・利益率の解釈・資金・株式は標準に固定。下限：'+input_notes[0]+' 上限：'+input_notes[1]+'。良い結果でも基準株価より低い試算となり得る。価格幅は合算しない。'
            outs.append(dict(label=label,conditions=[event[['success','inline','failure'][j]]],direction=direction,quantifiable=True,price_range=prices,price_change_pct_range=[calc.pct_change(v,p) for v in prices],probability=None,method_note=note,quantification_attempts=deepcopy(attempts),non_quantified_explanation=None))
        catalysts.append(dict(id=cid,title=event['title'],category='PRODUCT',status='ONGOING',importance=5 if index==1 else 4,date=dict(display_text='進行中／各決算・公式開示で確認。確定日は未確認',start_date=None,end_date=None,precision='TBD',basis='CONFIRMED',confidence='LOW',timezone=None,source_ids=REFS),plain_language=event['description'],mechanism=['事業KPI・費用の変化','対象事業売上・利益率への接続','共通SOTPによる条件付き株主価値'],outcomes=outs,priced_in=dict(quantifiable=False,method='QUALITATIVE',percent_range=None,raw_implied_pct=None,event_excluded_equity_value=None,full_success_incremental_equity_value=None,confidence='LOW',evidence_for=[c['financial']],evidence_against=[c['risk']],caveats=[explanation['reason']],non_quantified_explanation=deepcopy(explanation)),dependencies=[],dependency_group_id='G1',leading_indicators=event['kpis'].split('、'),sell_the_news_risk='既存期待が高い場合は事業が進んでも価格を支えない。基準価格との差は短期反応の予測ではなく、当方の条件付き価値との比較。',financing_risk=c['liquidity']+' '+c['funding_note'],update_triggers=['事業別決算・会社計画の更新','規制・安全性・開発・資本政策の重要開示'],source_ids=REFS,claim_ids=[cid,cid+'_CONDITIONS','MODEL','RISK','FUNDING']))
    eq0,eq1=cases[0]['equity_value'],cases[2]['equity_value'];overall=calc.priced_in_pct(p*n,eq0,eq1-eq0);display=calc.clamp(overall,0,100)
    # The catalogue uses the documented piecewise base-centred valuation scale.
    val=50*(p-xs[0])/(xs[1]-xs[0]) if p<=xs[1] else 50+50*(p-xs[1])/(xs[2]-xs[1]);val=round(calc.clamp(val+5,0,100),1)
    components=dict(valuation=val,catalysts=c['components'][1],businessRisk=c['components'][2]);position=round(val*.6+components['catalysts']*.25+components['businessRisk']*.15,1);zone='売られすぎ' if position<=30 else '買われすぎ' if position>=70 else '中立'
    signal_data=dict(position=position,zone=zone,asOf=DATE,components=components,reportRevision=c['id']+'-'+DATE+'-v1',summary='事業別SOTPの条件付き評価。高い成長期待と実現・資金・規制リスクを総合。会社の成功確率や売買推奨ではない。')
    claim('SIGNAL',f'現在株価評価{val}、カタリスト{components["catalysts"]}、企業基盤リスク{components["businessRisk"]}。60/25/15%で総合{position}、{zone}。株価スコアは悲観→標準を0→50、標準→楽観を50→100で補間し、SOTP倍率・希薄化・事業化の不確実性で5点加算、0〜100へ制限。材料85は成長実績に対し複数の未完了条件と期待先行が大きいとの主観評価。企業リスクは財務・投資・集中・規制を根拠とする主観評価。日々の株価から自動再計算しない。','MODEL_ESTIMATE',REFS,'piecewise price position +5; valuation*.60+catalysts*.25+businessRisk*.15')
    claim('OVERALL',f'共通の全事業・資金条件を1群にまとめ、失敗側株主価値{bn(eq0)}、成功側{bn(eq1)}から逆算。中心{overall:.1f}%。表示幅は中心±10ポイントを0〜100へ制限し、統計区間・成功率ではない。','MODEL_ESTIMATE',REFS,'(price*current_diluted_shares-bear_equity)/(bull_equity-bear_equity)*100')
    sources=[dict(id=id,title=title,publisher=c['formal'] if id!='S4' else 'SEC',url=url,published_at=published,accessed_at=now,source_type=typ,is_primary=True,supports_claim_ids=[v['id'] for v in claims if id in v['source_ids']]) for id,title,url,published,typ in c['sources']]
    sources.append(dict(id='S5',title='市場価格（日足・時点値）',publisher='Yahoo Finance',url=f'https://query1.finance.yahoo.com/v8/finance/chart/{c["ticker"]}?range=3mo&interval=1d',published_at=None,accessed_at=now,source_type='MARKET_DATA',is_primary=False,supports_claim_ids=['QUOTE']))
    bundle=dict(meta=dict(framework_version='6.2',schema_version='1.2',company_name=c['formal'],ticker=c['ticker'],exchange=c['exchange'],currency='USD',fiscal_year_end='12-31',valuation_date=DATE,source_cutoff=now,generated_at=now,price=p,price_as_of=c['price_as_of'],benchmark=None),capital_structure=dict(basic_shares=c['basic'],diluted_shares=n,market_cap=p*n,cash=c['cash'],liquid_securities=c['securities'],restricted_cash=0,minimum_operating_cash=c['minimum_cash'],debt=c['debt'],preferred_stock=0,minority_interest=c['minority'],other_non_equity_claims=0,ttm_operating_cash_flow=18710000000 if c['ticker']=='TSLA' else None,ttm_capex=15407000000 if c['ticker']=='TSLA' else None,runway_months=None,source_ids=REFS,dilution_notes=[c['capital'],c['funding_note'],'自由現金は制限現金を含まないためrestricted_cash=0として再控除しない。実際の別建て制限現金は'+bn(c['restricted'])+'。',c['asset_note']]),claims=claims,sources=sources,guide=dict(tagline=c['business'],section_claim_ids={'sec1':['IDENTITY','FINANCIAL'],'sec2':['BUSINESS','RISK'],'sec3':['BUSINESS','C1','C2','C3'],'sec4':['CAPITAL','LIQUIDITY'],'sec5':['COMPETITION'],'sec6':['CAPITAL'],'sec7':['C1','C2','C3','RISK']},source_ids=REFS),scenario=dict(horizon_date=HORIZON,primary_method='SOTP',method_explanation=c['model_note'],cases=cases,computed=computed,risk_class='HIGH',risk_reasons=[c['risk'],'大きな将来成長・高い売上倍率と未確定の事業化・資金条件に依存する。'],major_catalyst_id='C1',sensitivity=sensitivity,distribution_method='THREE_POINT',monte_carlo=None),catalyst_report=dict(status='CATALYST_RICH',next_catalyst_id='C1',catalysts=catalysts,dependency_groups=[dict(id='G1',name='事業拡大・設備・資金・規制の共通SOTP',relationship_type='SHARED_VALUE',catalyst_ids=['C1','C2','C3'],aggregation_rule='内部取引・事業売上と設備・資金を重複加算しない。全事業と資本条件の同時シナリオを1群として一度だけ評価。個別価格幅や個別割合を合算しない。',full_success_incremental_equity_value=eq1-eq0)],overall_priced_in=dict(quantifiable=True,percent_range=[max(0,display-10),min(100,display+10)],raw_implied_pct=overall,all_events_excluded_equity_value=eq0,included_group_ids=['G1'],method_note=claims[-1]['statement']+' 現在の評価株式と各ケースの将来株式が違うため、株価帯の位置とは一致しない。',confidence='LOW',non_quantified_explanation=None),watch_items=[dict(item=e['kpis'],frequency='各決算・公式開示時',update_trigger='事業・資金・規制の重要変化',catalyst_ids=['C'+str(i+1)]) for i,e in enumerate(c['events'])]),validation_summary=dict(status='WARN',fail_count=0,warn_count=4,generated_at=now,messages=['将来の売上・利益率・倍率・確率・財務は当方仮定で会社予想ではない。','希薄化は時点と期間平均の違いを含む概算で、証券別TSMの独立検証は未実施。','独立DCF・同業倍率・市場予想・短期イベント統計は未取得。',c['liquidity']]))
    return bundle,signal_data


def outcome_html(outcome):
    label = OUT_LABELS[outcome['label']]
    if outcome['quantifiable']:
        return f'<div class="outcome"><h4>{label}</h4><div class="impact">{usd(outcome["price_range"][0])}〜{usd(outcome["price_range"][1])}</div><p>基準価格比 {pct(outcome["price_change_pct_range"][0])}〜{pct(outcome["price_change_pct_range"][1])}</p><p>{esc(outcome["conditions"][0])}</p>'+detail('計算入力',esc(outcome['method_note']))+'</div>'
    explanation = outcome['non_quantified_explanation']
    direction = {'UP':'上向きの可能性','DOWN':'下向きの可能性','FLAT':'小さい可能性','MIXED':'上下両方の経路','UNKNOWN':'方向は未確認'}[outcome['direction']]
    content = ''.join(f'<p>{name}：{esc(value)}</p>' for name,value in [
        ('理由',explanation['reason']),('不足情報','、'.join(explanation['missing_information'])),
        ('次に確認','、'.join(explanation['next_checks'])),('再計算',explanation['recalculation_method'])])
    return f'<div class="outcome"><h4>{label}</h4><div class="impact">価格幅は未算出</div><p>{direction}</p><p>{esc(outcome["conditions"][0])}</p>'+detail('数値を出さない理由',content)+'</div>'


def render_reports(c,b, enrich=None):
    p=c['price'];sc=b['scenario'];cases=sc['cases'];v=sc['computed'];cat=b['catalyst_report'];claims={x['id']:x['statement'] for x in b['claims']}
    back='<a href="../../index.html">銘柄一覧へ戻る</a>'
    source_html='<ul>'+''.join(f'<li><a href="{esc(x["url"])}" target="_blank" rel="noopener noreferrer">{esc(x["id"]+"："+x["title"])}</a>（公開：{esc(x["published_at"] or "取得時点で確認")}／取得：{DATE}）</li>' for x in b['sources'])+'</ul>'
    basis=f'分析基準株価{usd(p)}／{c["price_as_of"]}。分析基準日{DATE}。対象2027年末。時点値で終値とは限りません。'
    common=dict(COMPANY_NAME=c['name'],TICKER=c['ticker'],EXCHANGE='Nasdaq／USD',VALUATION_DATE=DATE,CURRENT_PRICE=usd(p),CURRENT_PRICE_NOTE=c['price_as_of']+' 時点値',DISCLAIMER='情報提供・教育目的の条件付き分析であり、投資助言・売買推奨ではありません。会社実績・見通しと当方仮定を区別してください。分析値は固定し、配当を価格比較へ含めません。',FOOTER_NOTE=esc(basis)+'<br>'+back)
    warn_text='将来売上・利益率・倍率・資金・株式数は当方仮定です。'+c['risk']
    warn='<div class="wrap"><p class="notice">'+esc(warn_text)+'</p></div>'
    watch=''.join(signal(e['title'],esc(e['plain_language'])+' [S1,S2]') for e in cat['catalysts'])
    terms=[('SOTP','事業ごとの価値を分けて合計する方法。内部売上や同じ資産・収益を二重計上しません。'),('EV/Sales','事業価値を売上の何倍で評価するか。利益率・成長・投資と一緒に見る当方仮定です。'),('営業利益と純利益','営業利益は事業の損益。純利益は利息・税・その他損益等も反映し、現金収支とは別です。'),('営業CFと設備投資','営業の現金収支から設備取得支出等を引いた余力を確認。会計利益と同じではありません。'),('時点株式と平均株式','現在発行済とEPS用の期間加重平均は異なります。制限株や報酬の重複加算に注意します。'),('当方仮定','このレポートの計算条件であり、会社予想・市場コンセンサス・実際の成功率ではありません。'),('監督付きと無人運行','運転者が監督する運転支援と、許可された条件下の無人サービスは区別します。' if c['ticker']=='TSLA' else '開発試験、商業輸送、衛星のサービス開始、顧客課金は別の段階です。')]
    terms.extend(c.get('extra_terms', []))
    guide=dict(COMPANY_NAME=c['name'],TICKER=c['ticker'],DATE=DATE,INDUSTRY=c['industry'],TAGLINE=esc(c['business']),HERO_TAGS=''.join(f'<span class="hero-tag">{esc(x)}</span>' for x in ['Nasdaq','USD',c['industry']]),HERO_STATS=''.join(f'<div class="stat"><div class="stat-value">{a}</div><div class="stat-label">{label}</div><div class="stat-note">{note}</div></div>' for a,label,note in [(usd(p),'評価基準株価',c['price_as_of']),(f"${c.get('headline_revenue',14575000000 if c['ticker']=='SPCX' else 28046000000)/1e9:.2f}B",'2026年3Q売上','7〜9月／米国GAAP [S1]'),(f"${c.get('headline_operating_income',2791000000 if c['ticker']=='SPCX' else 718000000)/1e9:.2f}B",'2026年3Q営業利益','純利益・営業CFとは別 [S1]'),(f"${(c['cash']+c['securities'])/1e9:.2f}B",'現金・短期証券','9月末／制限現金を除く [S1]')]),SEC1_TLDR=bullets(c['business'],c['financial'],'対象期間・事業範囲をそろえて確認します。'),SEC1_FACTS=boxes([('会社情報',c['identity']),('直近の実績',c['financial'])]),SEC1_CARDS=boxes([(x,y) for x,y in c['products']]),SEC1_BIZMODEL=boxes([('どう収益化するか',c['business']),('会社が示す計画',c['guidance'])]),SEC1_HIGHLIGHT=boxes([('最初に区別すること','会社が既に達成した事実と、未完了の開発・顧客獲得・資金条件を分けます。')]),SEC2_ICON='◇',SEC2_LABEL='事業構造',SEC2_TITLE='需要と利益はどこで生まれるか',SEC2_SUB='事業間のつながりと費用を確認',SEC2_TLDR=bullets(c['products'][0][1],c['products'][1][1],'新しい製品発表だけでは売上・利益・現金は確定しません。'),SEC2_CONTENT=boxes([('収益源',c['business']),('制約と競争',c['risk'])]),SEC3_LABEL='製品・サービス',SEC3_TITLE='主力と次の展開を分ける',SEC3_SUB='製品・許認可・顧客採用・収益化は別段階',SEC3_TLDR=bullets(*[a+'：'+t for a,t in c['products'][:3]]),SEC3_CONTENT='<div class="table-wrap"><table class="compare-table"><thead><tr><th>領域</th><th>何を確認するか</th></tr></thead><tbody>'+''.join(row(esc(a),esc(t)+' [S1,S2]') for a,t in c['products'])+'</tbody></table></div>',SEC4_LABEL='財務・株式',SEC4_TITLE='成長を支える資金と1株の取り分',SEC4_SUB='発行済と潜在株・利益と現金収支を区別',SEC4_TLDR=bullets(c['liquidity'],c['risk']),SEC4_CONTENT=boxes([('株式と資産・負債',c['capital']),('資金の確認',c['liquidity']),('その他資産の扱い',c['asset_note'])]),SEC5_LABEL='競合',SEC5_TITLE='同じ顧客課題を解く選択肢',SEC5_SUB='事業・仕様・地域・対象期間をそろえて比較',SEC5_TLDR=bullets(c['competitors'],'未取得の市場シェアや同業倍率を確認済みとして使いません。'),SEC5_CONTENT=boxes([('比較対象と制約',c['competitors']),('競争力とリスク',c['risk'])]),SEC6_TLDR=bullets('会社実績・会社見通し・当方仮定を分けます。','数字の期間・単位・株式数をそろえます。'),SEC6_CONTENT='<div class="term-list">'+''.join(f'<details class="term-item"><summary class="term-header"><span class="term-name">{esc(a)}</span><span class="term-arrow">⌄</span></summary><div class="term-body"><p>{esc(t)}</p></div></details>' for a,t in terms)+'</div>',SEC7_TLDR=bullets(*[e['description'] for e in c['events']]),SEC7_CONTENT=boxes([(e['title'],e['kpis']+' [S1,S2]') for e in c['events']])+detail('主要出典・分析基準',source_html+'<p>'+esc(basis)+'</p>'+back))
    assumptions=[('基準株価',usd(p),'市場の時点値',c['price_as_of']+' [S5]'),('会社実績',c['financial'],'公式情報で確認','対象期間と通貨を固定 [S1]'),('会社計画',c['guidance'],'会社の計画・予定','達成保証ではない [S1,S2]'),('SOTP',c['model_note'],'当方の条件付き仮定','同業観測倍率ではない。'),('株式・財務',c['capital'],'公式数値＋当方概算','時点と期間平均の違い、報酬の重複に注意。'),('資金',c['funding_note'],'当方の条件付き仮定',c['liquidity']),('その他資産',c['asset_note'],'帳簿値起点の当方計算','取得済み資産・子会社を再加算しない。'),('確率','悲観35%／標準45%／楽観20%','粗い主観配分','統計的確率や成功率ではない。')]
    position='悲観未満' if v['raw_band_position_pct']<0 else '楽観超' if v['raw_band_position_pct']>100 else '悲観〜標準の間' if p<cases[1]['price'] else '標準〜楽観の間'
    calculation_rows=[]
    for i,case in enumerate(cases):
        for name,sales,mul,margin in zip(c['segments'],c['sales'][i],c['multiples'][i],c['margins'][i]):
            calculation_rows.append(row(LABELS[i],esc(name),bn(sales),f'{margin*100:g}%',f'{mul:g}倍',bn(sales*mul)))
        calculation_rows.append(row(LABELS[i],'合計EV→株主価値',bn(case['enterprise_value']),'資金・請求権調整後',bn(case['equity_value']),usd(case['price'])+'／株'))
    # Independent cross-check: implied EV/operating profit, not a second fitted price.
    cross=[]
    for i in range(3):
        op=sum(a*m for a,m in zip(c['sales'][i],c['margins'][i]));ev=cases[i]['enterprise_value'];cross.append(f'{LABELS[i]}の想定営業利益{bn(op)}、EV/営業利益'+(f'{ev/op:.1f}倍' if op>0 else '算出対象外（営業赤字）'))
    base_ev=cases[1]['enterprise_value'];implied_ev=p*c['diluted']-c['future_cash'][1]-c['other_assets']+c['minimum_cash']+c['future_debt'][1]+c['minority'];implied_factor=implied_ev/base_ev
    rr='該当なし（基準価格が帯外）' if v['endpoint_rr'] is None else f'{v["endpoint_rr"]:.2f}倍（確率を含まない）'
    values=dict(common,METHOD='事業別SOTP／売上・利益率・資金・株式',VERDICT_STATUS='事業の進展と高い期待を分けて見る',VERDICT_LINE_1=f'標準ケース{usd(cases[1]["price"])}。基準株価は{position}。将来の売上・利益率と資金条件が成立する場合の価値です。',VERDICT_LINE_2='事業別の条件付きSOTPで比較。高い売上倍率は2027年以降の成長も必要とし、成功しても現在価格を支えるとは限りません。',SCORE=str(v['supplemental_score']),BASE_PRICE=usd(cases[1]['price']),BASE_DELTA=pct(calc.pct_change(cases[1]['price'],p)),EXPECTED_VALUE=usd(v['expected_price']),EXPECTED_DELTA=pct(v['expected_delta_pct']),RISK_CLASS='高い',RISK_NOTE='事業化・高い倍率・資金・規制条件に依存',WARN_BAND=warn,WARN_MESSAGE=esc(warn_text),SNAPSHOT_LEAD=esc(basis),BAND_POSITION=f'{v["display_band_position_pct"]:.1f}%',ZONE_JUDGE=position,ZONE_NOTE=f'丸め前の帯位置{v["raw_band_position_pct"]:.1f}%。0〜100%外は表示ピンだけ端へ固定します。真の成功率ではありません。',MARKET_SCORE=str(v['market_score']),OWN_SCORE=str(v['own_score']),MARKET_REVERSE_NOTE=f'標準事業売上と資金条件・現在評価株式を固定すると、基準価格が要求する事業価値は{bn(implied_ev)}。標準の全売上倍率を一斉に{implied_factor:.2f}倍する条件に相当します。実際の市場予想を観測した値ではありません。',SCENARIOS_LEAD='2027年末に2027年の通期収益力とそれ以降の成長期待を評価。現在株価に合わせて標準入力を作っていません。',PRICE_ZONE_ROWS=''.join(f'<div class="zone"><div><b>{a}</b></div><p>{t}</p></div>' for a,t in [(usd(cases[0]['price'])+'未満','当方悲観モデルより低い。前提の追加悪化や別のリスクを再検討。'),(usd(cases[0]['price'])+'〜'+usd(cases[1]['price']),'悲観と標準の間。標準の達成を保証しない。'),(usd(cases[1]['price'])+'〜'+usd(cases[2]['price']),'成長と高い評価倍率、資金・規制条件が必要。'),(usd(cases[2]['price'])+'超','当方楽観ケース以上の収益化・倍率等が必要。売買指示ではない。')]),SIGNAL_ROWS=watch,POSITIVES=bullets(c['business'],c['financial'],c['guidance']),CONCERNS=bullets(c['risk'],c['liquidity'],'独立DCF・同業倍率・市場予想を用いる別手法の検証は未実施。'),FORMULA='EV＝Σ（事業別売上×売上倍率）。株主価値＝EV＋将来自由現金・短期証券＋その他資産−最低運転現金−負債・金融リース−非支配等。1株価値＝株主価値÷将来希薄化株式。',CALC_TABLE_HEAD='<th>ケース</th><th>領域</th><th>売上／合計EV</th><th>営業利益率／調整</th><th>倍率／株主価値</th><th>事業価値／1株価値</th>',CALC_TABLE_ROWS=''.join(calculation_rows),CALC_NOTICE=esc(c['model_note']+' '+c['asset_note']),CONDITIONS=''.join(detail(LABELS[i]+'：'+usd(case['price'])+'／主観確率'+str(round(case['probability']*100))+'%',esc(' '.join(case['conditions']))) for i,case in enumerate(cases)),SENSITIVITY_HEAD='<th>動かす変数</th><th>80%</th><th>100%</th><th>120%</th>',SENSITIVITY_ROWS=''.join(row(esc(x['variable']),*(usd(a) for a in x['result_prices'])) for x in sc['sensitivity']),SENSITIVITY_NOTE='標準の全事業売上、または全事業倍率を1つずつ80/100/120%へ変更。他の変数は固定。売上と倍率を独立確率とみなす表ではありません。',DIST_LEAD='3点の離散分布のみ。モンテカルロ未実施。',DIST_ROWS=''.join(signal(LABELS[i]+'：'+usd(case['price']),f'当方主観確率{case["probability"]*100:g}%') for i,case in enumerate(cases)),DIST_SUMMARY=esc(claims['PROB']),ENDPOINT_RR=rr,WATCH_ROWS=watch,ASSUMPTIONS_ROWS=''.join(row(esc(a),esc(t),esc(k),esc(note)) for a,t,k,note in assumptions),DEEPDIVE_DETAILS=detail('利益との接続・補助比較',esc('。'.join(cross))+'。これはSOTPと同じ入力に基づく妥当性点検で、独立したDCFではありません。赤字や極端な倍率はモデルの弱点として読みます。')+detail('資金・希薄化',esc(c['capital']+' '+c['funding_note']+' '+c['liquidity']))+detail('総合判定',esc(claims['SIGNAL']))+detail('主要出典・制約',source_html+'<p>'+esc(basis)+'</p><p>独立DCF・市場コンセンサス・同業横断倍率・オプション・空売りの取得は未実施。</p>'))
    for i,key in enumerate(['BEAR','BASE','BULL']):
        case=cases[i];values.update({key+'_PRICE':usd(case['price']),key+'_DELTA':pct(calc.pct_change(case['price'],p)),key+'_PROB':f'{case["probability"]*100:g}%',key+'_DL_ROWS':''.join(f'<div><dt>{a}</dt><dd>{esc(t)}</dd></div>' for a,t in [('対象','2027年末'),('事業価値',bn(case['enterprise_value'])),('株主価値',bn(case['equity_value'])),('将来株式',f'{case["diluted_shares"]/1e9:g}十億株')])})
    cards=[]
    for e in cat['catalysts']:
        outcomes=''.join(outcome_html(o) for o in e['outcomes'])
        nq=e['priced_in']['non_quantified_explanation'];nq_html=''.join(f'<p>{label}：{esc(text)}</p>' for label,text in [('理由',nq['reason']),('不足情報','、'.join(nq['missing_information'])),('次に確認','、'.join(nq['next_checks'])),('再計算',nq['recalculation_method'])])
        cards.append(f'<article class="catalyst-card" id="{e["id"].lower()}"><div class="catalyst-head"><h3>{esc(e["title"])}</h3><span class="chip">重要度{e["importance"]}</span></div><p>{esc(e["date"]["display_text"])}</p><p>{esc(e["plain_language"])}</p><p><strong>観測：</strong>{esc("、".join(e["leading_indicators"]))}</p><div class="outcomes">{outcomes}</div>'+detail('個別の期待割合を出さない理由',nq_html)+detail('手法・反証・資金', '<ul>'+bullets(*[x['reason'] for x in e['outcomes'][0]['quantification_attempts']])+'</ul><p>'+esc(e['sell_the_news_risk'])+'</p><p>'+esc(e['financing_risk'])+'</p><p>出典：[S1,S2]／更新条件：決算・公式な事業、規制、資本政策の変化。</p>')+'</article>')
    over=cat['overall_priced_in'];lo,hi=over['percent_range']
    overall_html=f'<div class="priced"><div class="priced-head"><b>{lo:.0f}〜{hi:.0f}%</b><span>当方モデルの条件付き逆算</span></div><p>{esc(over["method_note"])}</p></div>'
    cv=dict(common,LAST_UPDATED=DATE,REPORT_STATUS='3つの進行中材料と期待を確認',SUMMARY_LINE_1='事業の進展と株価に入った期待を分けます。確定日が確認できない材料は予定日を作りません。',SUMMARY_LINE_2='良い結果でも基準価格以下の試算となり得ます。価格幅は2027年末の条件付き評価で、発表直後の反応予測ではありません。',OVERALL_PRICED_IN=f'{lo:.0f}〜{hi:.0f}%',OVERALL_PRICED_LABEL='共通SOTPによる条件付き推定',PRICED_IN_CONFIDENCE='低い',NEXT_CATALYST_TITLE=cat['catalysts'][0]['title'],NEXT_CATALYST_WINDOW=cat['catalysts'][0]['date']['display_text'],DATE_CONFIDENCE='確定日時は未確認',CATALYST_COUNT=f'{len(cat["catalysts"])}件',WARN_BAND=warn,NO_CATALYST_NOTICE='',OVERALL_PRICED_BLOCK=overall_html,PRICED_IN_METHOD=esc(over['method_note']),SURPRISE_UP='事業KPIと利益率が当方標準を上回り、資金・規制・設備の制約を吸収できる。',SURPRISE_DOWN='売上が増えても単価・利益率・投資・株式数の条件が悪化し、1株価値に結び付かない。',PRIMARY_RISK=c['risk'],TIMELINE_ROWS=''.join(f'<div class="time-row"><div class="time-date">進行中</div><div class="time-dot"></div><div class="time-body"><b>{esc(e["title"])}</b><p>各決算・公式開示で確認。確定日は未確認。</p></div></div>' for e in cat['catalysts']),CATALYST_CARDS=''.join(cards),DEPENDENCY_ROWS='<p>事業別に売上を分けても、輸送・通信・AI・設備・資金・規制は相互に関係するため、全体は共通SOTPの1群で評価します。個別の価格幅・割合は合算しません。</p><p>全体逆算は現在評価株式、価格シナリオは将来株式を使い、現金・負債条件も変えるため株価帯の位置とは一致しません。</p>',WATCH_ROWS=watch,ASSUMPTION_ROWS=''.join(row(esc(a),esc(t),esc(k),DATE,esc(note)) for a,t,k,note in assumptions),SOURCE_DETAILS=source_html,VALIDATION_DETAILS='<p>出典ID、算術、確率、日程、依存関係、HTMLを検証。次は分析上の制約です。</p><ul>'+bullets(*b['validation_summary']['messages'])+'</ul>',UPDATE_HISTORY=f'<p>{DATE} 初版作成。3レポートは同じ共通データ・固定の分析基準を使用。</p>')
    out=ROOT/'stocks'/c['id'];out.mkdir(parents=True,exist_ok=True)
    for filename,template,mapping in [('company.html','template_stock_guide_v4_unified.html',guide),('valuation.html','template_scenario_v4_unified.html',values),('catalysts.html','template_catalyst_v1_unified.html',cv)]:
        if enrich is not None:
            mapping = enrich(filename, mapping)
        (out/filename).write_text(render(MATERIALS,template,mapping),encoding='utf-8')
    return source_html,overall_html,cards,basis



def main():
    configs=json.loads((ROOT/'data/report-inputs/spacex-tesla-20261128.json').read_text())
    integrations={}
    for c in configs:
        b,s=make_bundle(c)
        result=Validator(b).run()
        if result['fail_count'] or result['warn_count']:
            print(json.dumps(result,ensure_ascii=False,indent=2))
            if result['fail_count']: raise SystemExit(1)
        (ROOT/'data/reports'/f'{c["id"]}.json').write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
        rendered=render_reports(c,b)
        # Website reports always use the shared templates.
        integrations[c['id']]=(c,b,s,rendered)
    stocks=json.loads((ROOT/'data/stocks.json').read_text());signals=json.loads((ROOT/'data/signals.json').read_text())
    for stock in stocks['stocks']:
        if stock['id'] not in integrations:continue
        c,b,s,_=integrations[stock['id']]
        for report in stock['reports'].values():report['available']=True
        stock['reportAsOf']=DATE;stock['reportRevision']=s['reportRevision'];signals['signals'][stock['id']]=s
        (ROOT/'docs/reports'/f'{stock["id"]}.md').write_text('# '+c['name']+' 出典・分析記録\n\n分析基準日 '+DATE+'。最新決算は2026年3Q。\n\n'+ '\n\n'.join(x['id']+' '+x['title']+'\n'+x['url'] for x in b['sources'])+'\n\n再生成: `python scripts/generate_spacex_tesla_reports.py`\n\n前提は `data/report-inputs/spacex-tesla-20261128.json`。株式は証券別TSMではなく明示した近似、将来売上・倍率・確率は当方仮定。独立DCF・同業倍率・市場コンセンサスは未検証。\n',encoding='utf-8')
        print(c['ticker'], 'prices:', [round(x['price'],2) for x in b['scenario']['cases']], 'signal:',s['position'],s['zone'])
    signals['updatedAt']=datetime.now(timezone.utc).isoformat()
    (ROOT/'data/stocks.json').write_text(json.dumps(stocks,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'data/signals.json').write_text(json.dumps(signals,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
