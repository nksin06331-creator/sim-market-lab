"""Create Anthropic's three standard reports from one frozen evidence/model snapshot.

Run: python scripts/generate_anthropic_reports.py
The supplied v6.2 templates and validators remain in use. No network calls.
"""
from __future__ import annotations
import json
from pathlib import Path
from copy import deepcopy
from datetime import datetime,timezone
import generate_spacex_tesla_reports as shared
from generate_eli_lilly_reports import esc, row, bullets, detail, guide_box
from report_support.bundle_validator import Validator, validate_html

ROOT=Path(__file__).resolve().parents[1]
DATE='2026-11-28'


def dcf_value(c,rate=.12,growth=.03):
    # Unlevered FCF after cash operating costs, taxes and investment, before financing.
    flows=[-5e9,5e9,15e9,30e9,45e9,60e9,70e9,80e9,90e9,100e9]
    ev=sum(value/(1+rate)**year for year,value in enumerate(flows,1))
    ev+=flows[-1]*(1+growth)/(rate-growth)/(1+rate)**len(flows)
    equity=ev+c['future_cash'][1]-c['minimum_cash']-c['future_debt'][1]
    return ev,equity,equity/c['shares'][1]


def make_report(c):
    b,s=shared.make_bundle(c)
    b['scenario']['primary_method']='EV_SALES'
    b['meta']['benchmark']='S&P 500 (^GSPC)'
    s['summary']='最新の確定目論見書とIPO完了を反映。連結EV/Sales、独立DCF、希薄化・計算資源契約・公益目的構造を点検した条件付き評価。'
    cap=b['capital_structure'];cap.update(ttm_operating_cash_flow=5956000000,ttm_capex=945000000,runway_months=None)
    cap['dilution_notes'].extend(['現在の評価株式は全転換・潜在株の経済的近似で、実際の発行済株式や法定EPS分母ではない。',c['liquidity'],'設備等前払のTTM19.58億ドルを控除するとCF余力は30.53億。過去のプラスCFを将来の設備・供給契約の保証とはしない。'])
    claims={x['id']:x for x in b['claims']}
    for i,case in enumerate(b['scenario']['cases']):
        net_cf=c['future_cash'][i]-c['cash']-c['securities']
        case['conditions'][1]=f'IPO後推計の自由現金・短期証券2,445.52億ドルを起点に、対象時点までの営業CF−設備投資・前払等を{net_cf/1e9:.3f}十億ドルと仮定。金融リース債務の増加は非現金の設備取得で、現金借入収入とはしない。'
        claims['MODEL_'+case['label']]['statement']='2027年末の'+shared.LABELS[i]+'：'+''.join(case['conditions'])
        claims['MODEL_'+case['label']]['calculation_id']='consolidated forward revenue*EV/Sales + future cash - minimum cash - finance leases; divided by if-converted future shares'
    claims['ASSETS']['calculation_id']='no additional nonoperating assets credited; restricted cash excluded from free cash; fund self-holdings excluded from economic current shares'
    claims['SIGNAL']['statement']=claims['SIGNAL']['statement'].replace('SOTP倍率','売上倍率')
    claims['FUNDING']['statement']=c['funding_note']
    claims['FUNDING']['calculation_id']='future_cash = IPO_adjusted_cash_and_securities + operating_cash_flow - cash_capex_and_prepayments; new_cash_equity_financing=0; cash_debt_draws=0'
    for x in b['claims']:
        if x['id'] in ['C3','C3_CONDITIONS','BUSINESS']:x['source_ids']=list(dict.fromkeys(x['source_ids']+['S4']))
        if x['id']=='CAPITAL':x['source_ids']+=['S7']
    def claim(id,text,kind='MODEL_ESTIMATE',refs=['S1','S2'],formula=None):
        item=dict(id=id,statement=text,classification=kind,as_of=DATE,source_ids=refs,calculation_id=formula,confidence='LOW' if kind!='CONFIRMED' else 'HIGH');b['claims'].append(item);return item
    claim('IPO_CASH','9月末自由現金・短期証券1,318.45億。IPO等反映後の目論見書推計2,323.51億＋全量行使の追加147百万株×83ドル（手数料なし）＝2,445.52億ドル。実測の最新現金残高ではない。',formula='232351e6 + 147000000*83; split as estimated cash 208269e6 plus securities 36283e6')
    claim('DILUTION',c['capital'],refs=['S1','S2','S7'],formula='IPO-adjusted economic basic shares + options*(1-2.91/basis_price) + unsettled RSUs + acquisition holdback + matching obligation + Amazon if-converted shares; exclude voting-only shares and subsidiary-held fund stock')
    claim('UNKNOWN_SCHEDULE','次回決算発表の確定日時と個別製品・設備稼働の確定日程は、取得した公式資料では確認できず。','UNKNOWN',refs=['S1','S2','S3','S6'])
    claim('NRR_RUNRATE','9月末のTTM売上10万ドル以上の顧客は11,900超、会社定義のNRRは約900%。10月末Run-Rate Revenueは約810億ドル。NRRは対象顧客・期間定義があり、Run-Rateは利用・課金の年換算で年次実績・受注残ではない。','CONFIRMED',refs=['S1'])
    m=c['market_context']
    market_note=f'上場後の日足は{m["observed_sessions"]}営業日で、観測安値{shared.usd(m["observed_low"])}〜高値{shared.usd(m["observed_high"])}。52週の上場履歴はない。ANTの20営業日騰落率・同期間の相対騰落は算出不可。S&P 500の直近20営業日騰落率は{m["benchmark_return_20d"]:+.1f}%（{m["benchmark_as_of"]}時点）だが、ANTの短い履歴とは同期間比較しない。'
    claim('MARKET_CONTEXT',market_note,'CONFIRMED',refs=['S5','S8'])
    flows='2028〜2037年の無杠杆FCFを-50／50／150／300／450／600／700／800／900／1,000億ドルとする独立の当方仮定。費用・税・現金投資と営業賃料の後、金融利息・元本支払前。設備リースの非現金取得を借入現金収入へは入れない。'
    ev,eq,price=dcf_value(c)
    dcf_text=flows+f'割引率12%、永久成長率3%、2037年末終価を2027年末へ割引く。EV {ev/1e9:.2f}十億ドル。標準の自由現金1,900億−最低運転現金600億−金融リース120億を加減し、188億株で割ると{shared.usd(price)}。主手法との平均は取らない。DCFも長期CFと終価への感応度が高く、独立した観測事実ではない。'
    claim('DCF',dcf_text,formula='sum(FCF_t/(1+r)^t) + FCF_10*(1+g)/(r-g)/(1+r)^10 + base_cash - minimum_cash - base_finance_leases; divide by base_future_shares')
    # A known share-supply window is shown without inventing a one-day price move.
    nq=dict(reason='売却制限の解除は新株発行そのものではない。実際の売却量・需要・同時ニュースが不明で、機械的な株価下落率や企業価値差分を置けない。',missing_information=['実際に売却する保有者・数量と時期','同時点の需給・市場予想改定・比較イベントの異常リターン'],next_checks=['目論見書の早期解除条件と今後の登録・保有開示','実際の売却、発行済株式、転換・報酬の更新'],recalculation_method='新株発行と既存株売却を分ける。新規発行は純調達現金と追加株式を共通モデルへ反映。既存売却は同時ニュースを調整した十分な比較標本がそろった段階で短期需給を別途評価する。')
    attempts=[dict(method=method,status='REJECTED' if i<2 else 'NOT_APPLICABLE',reason=text) for i,(method,text) in enumerate([
        ('ENTERPRISE_VALUE_DELTA','企業価値差分：既存株の売却制限解除だけでは営業CFの増減を確定できない。'),
        ('CONDITIONAL_SCENARIO','共通シナリオ：新規発行・純調達現金・実行株数が未定で、解除株数を希薄化として流用できない。'),
        ('CONSENSUS_REVISION','市場予想改定：前後をそろえた独立した業績予想改定データを取得していない。'),
        ('SAME_COMPANY_EVENT_STUDY','同社イベント比較：上場直後で同社の比較可能な解除イベント標本がない。'),
        ('PEER_EVENT_STUDY','同業イベント比較：時価総額・浮動株・成長・同時ニュースをそろえた十分な対照標本を作成していない。')])]
    conditions=['売却・希薄化の実行が限定され、需要と資本配分・開示の透明性が保たれる。','予定された売却可能化と株式報酬・転換が既存想定内で進む。','売却・報酬・公益目的拠出・資金条件が既存株主の取り分や需給を想定以上に圧迫する。']
    outcomes=[dict(label=label,conditions=[text],direction=direction,quantifiable=False,price_range=None,price_change_pct_range=None,probability=None,method_note=nq['reason'],quantification_attempts=deepcopy(attempts),non_quantified_explanation=deepcopy(nq)) for label,text,direction in zip(['SUCCESS','INLINE','FAILURE'],conditions,['MIXED','MIXED','DOWN'])]
    fourth=dict(id='C4',title='IPO後の売却制限・報酬・公益目的拠出',category='FINANCING',status='CONTINGENT',importance=4,date=dict(display_text='保有者別に目論見書日から最大180日／365日。決算後・価格等の早期解除条項あり',start_date=None,end_date=None,precision='TBD',basis='CONFIRMED',confidence='MEDIUM',timezone=None,source_ids=['S1','S2']),plain_language='一般保有者は目論見書日から最大180日、創業者等は最大365日の売却制限があるが、決算後等の早期解除と例外がある。解除可能な全株が売却されるとはしない。公益基金・報酬・転換と既存株の売却を分けて追う。',mechanism=['売却制限・実行条件','流通株・新株発行の区別','需給と1株の取り分の確認'],outcomes=outcomes,priced_in=dict(quantifiable=False,method='QUALITATIVE',percent_range=None,raw_implied_pct=None,event_excluded_equity_value=None,full_success_incremental_equity_value=None,confidence='LOW',evidence_for=['IPO後の開示・資本政策を確認できる。'],evidence_against=[c['risk']],caveats=[nq['reason']],non_quantified_explanation=deepcopy(nq)),dependencies=[],dependency_group_id=None,leading_indicators=['実際の売却・登録','発行済株式と転換','基金の外部移転と報酬'],sell_the_news_risk='解除可能日を固定の売り日・下落率に置き換えない。良い事業ニュースと売却・追加報酬が同時に起こる場合もある。',financing_risk=c['funding_note'],update_triggers=['解除・登録・保有・転換・報酬の公式開示','新規発行と純調達現金の確定'],source_ids=['S1','S2','S7'],claim_ids=['C4','CAPITAL','DILUTION','RISK'])
    b['catalyst_report']['catalysts'].append(fourth)
    b['catalyst_report']['watch_items'].append(dict(item='実際の売却、転換、報酬、基金の外部移転',frequency='各公式開示時',update_trigger='新規発行・純調達現金・保有状況の変化',catalyst_ids=['C4']))
    claim('C4',fourth['plain_language'],'CONFIRMED',refs=['S1','S2'])
    b['guide']['section_claim_ids']['sec7'].append('C4')
    b['catalyst_report']['dependency_groups'][0]['name']='Claude共通の有償需要・供給・品質'
    b['catalyst_report']['dependency_groups'][0]['aggregation_rule']='同じClaude連結売上・資金条件を変える材料C1〜C3は共通価値を1回だけ評価。C4の純粋な既存株需給は事業価値の成功増分へ加算しない。'
    overall=b['catalyst_report']['overall_priced_in']
    overall['method_note']=overall['method_note'].replace('全事業','連結Claude事業')+' この全体値はC1〜C3の事業・資本条件を対象とし、C4の純粋な既存株需給は含めない。'
    b['validation_summary']['messages']=[
        '最新財務はIPOの確定目論見書であり、上場後の最新実測残高や四半期報告書ではない。',
        'IPO後現金と潜在株式は開示からの計算。全転換・RSU・寄付対応・基金移転には不確実性がある。',
        '将来売上・利益率・倍率・確率・DCFは当方仮定。市場予想・同業横断倍率・短期イベント統計は未取得。',
        'C4の既存株需給による価格幅は、代替5手法を検討しても根拠ある端点を作れず未算出。',
        c['liquidity']]
    b['validation_summary']['warn_count']=len(b['validation_summary']['messages'])
    for source in b['sources']:
        if source['id']=='S8':source.update(publisher='Yahoo Finance',is_primary=False)
        source['supports_claim_ids']=[x['id'] for x in b['claims'] if source['id'] in x['source_ids']]
    return b,s,dcf_text


def main():
    c=json.loads((ROOT/'data/report-inputs/anthropic-20261128.json').read_text())
    b,s,dcf_text=make_report(c)
    result=Validator(b).run()
    if result['fail_count'] or result['warn_count']:
        print(json.dumps(result,ensure_ascii=False,indent=2))
        if result['fail_count']:raise SystemExit(1)
    def enrich(filename,mapping):
        # Use the standard shared templates with complete Anthropic-specific bindings.
        if filename=='company.html':
            n=c['diluted'];market=c['price']*n
            mapping['HERO_STATS']=''.join(f'<div class="stat"><div class="stat-value">{value}</div><div class="stat-label">{label}</div><div class="stat-note">{note}</div></div>' for value,label,note in [
                (shared.usd(c['price']),'評価基準株価',DATE+'／時点値 [S5]'),(f'${market/1e12:.2f}T','評価時価総額（潜在株込み）','全転換等の当方計算 [S1,S2]'),('$16.96B','2026年7〜9月売上','未監査・米国GAAP [S1]'),('−$0.57B','2026年7〜9月営業損益','純損失・資金消費とは別 [S1]')])
            mapping['SEC1_CARDS']=shared.boxes([('何をする会社',c['business']),('主力',c['products'][0][1]+' '+c['products'][1][1]+' [S1]'),('直近業績',c['financial']),('なぜ注目', '企業での有償利用が急拡大する一方、計算設備契約・上場後の資本構造と公益目的の仕組みが1株の取り分に関わる。[S1,S2]')])
            mapping['SEC4_LABEL']='計算基盤・規制・財務'
            mapping['SEC4_TITLE']='供給と安全性、資金・株式の条件'
            mapping['SEC4_SUB']='契約・稼働・有償利用・現金収支を分ける'
            mapping['SEC4_CONTENT']=shared.boxes([('計算設備と残工程','Anthropic Directは直接調達・リースと専用施設の組合せ。契約、機器設置、利用開始、費用効率、実際の現金負担を分ける。未稼働設備を収益化済みと数えない。[S1]'),('安全性・規制','能力・安全性・顧客データ管理や著作権・訴訟が利用範囲と費用へ影響する。研究発表やベンチマークを一律の承認・独立保証としない。[S1,S4]'),('財務と株式',c['capital']),('資金',c['liquidity'])])
            sources='<ul>'+''.join(f'<li><a href="{esc(x["url"])}" target="_blank" rel="noopener noreferrer">{esc(x["id"]+"："+x["title"])}</a></li>' for x in b['sources'])+'</ul>'
            mapping['SEC7_CONTENT']+=shared.boxes([('売却制限と1株の取り分',b['catalyst_report']['catalysts'][-1]['plain_language'])])
            mapping['SEC7_CONTENT']+='<div class="term-list"><details class="term-item"><summary class="term-header"><span class="term-name">主要出典</span><span class="term-arrow">⌄</span></summary><div class="term-body">'+sources+'</div></details></div>'
        else:
            mapping={key:value.replace('事業別SOTP','連結EV/Sales').replace('共通SOTP','共通の連結評価').replace('SOTP','連結評価') if isinstance(value,str) else value for key,value in mapping.items()}
        if filename=='valuation.html':
            mapping['METHOD']='連結EV/Sales／利益率・資金・希薄化'
            mapping['VERDICT_LINE_2']=f'独立DCFでは{shared.usd(dcf_value(c)[2])}。主手法より低く、長期CF・終価・売上倍率に大きく依存します。平均して差を消さず、確信度を低く置きます。'
            market_claim=next(x['statement'] for x in b['claims'] if x['id']=='MARKET_CONTEXT')
            mapping['DEEPDIVE_DETAILS']+=detail('市場データ・取得範囲',esc(market_claim)+' [S5,S8]')
            mapping['SIGNAL_ROWS']+=shared.signal('上場後の売却制限・株式報酬',esc(b['catalyst_report']['catalysts'][-1]['plain_language'])+' [S1,S2]')
            mapping['DEEPDIVE_DETAILS']+=detail('独立DCFとの照合',esc(dcf_text)+'<div class="table-wrap"><table><thead><tr><th>割引率／永久成長率</th><th>2%</th><th>3%</th><th>4%</th></tr></thead><tbody>'+''.join(row(f'{rate*100:g}%',*(shared.usd(dcf_value(c,rate,g)[2]) for g in [.02,.03,.04])) for rate in [.10,.12,.14])+'</tbody></table></div><p>主手法との差は将来成長・資本効率と終価の前提に依存。平均して差を消さず、確信度を低く置きます。</p>')
        if filename=='catalysts.html':
            over=b['catalyst_report']['overall_priced_in'];lo,hi=over['percent_range']
            mapping['REPORT_STATUS']='4つの材料・資本条件を区別'
            mapping['SUMMARY_LINE_2']='Claudeの有償需要・供給・品質は共通の売上へ重なるため一度だけ評価。既存株の売却制限解除は新株発行と分け、機械的な価格幅を置きません。'
            mapping['DEPENDENCY_ROWS']='<p>C1〜C3は同じ連結売上・資金条件を共有し、共通の価値を1回だけ評価します。個別の価格幅・割合は合算しません。</p><p>C4の既存株の売却可能化は、事業価値増分や新株発行ではありません。実際の新規発行・純調達・転換等が判明した時点で共通株式モデルを更新します。</p>'
            mapping['OVERALL_PRICED_BLOCK']=f'<div class="priced"><div class="priced-head"><b>{lo:.0f}〜{hi:.0f}%</b><span>当方モデルの条件付き逆算</span></div><div class="range-meter"><span class="range-band" style="left:{lo:.3f}%;width:{hi-lo:.3f}%"></span></div><p>{esc(over["method_note"])}</p></div>'
            old='<p>各決算・公式開示で確認。確定日は未確認。</p>'
            i=mapping['TIMELINE_ROWS'].rfind(old)
            if i>=0:mapping['TIMELINE_ROWS']=mapping['TIMELINE_ROWS'][:i]+'<p>保有者別に最大180／365日と早期解除条項。実際の解除・売却を確認。</p>'+mapping['TIMELINE_ROWS'][i+len(old):]
        return mapping
    shared.render_reports(c,b,enrich=enrich)
    paths=[ROOT/'stocks'/c['id']/f'{key}.html' for key in ['company','valuation','catalysts']]
    problems=validate_html(paths)
    if problems:raise RuntimeError(problems)
    (ROOT/'data/reports'/f'{c["id"]}.json').write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
    stocks=json.loads((ROOT/'data/stocks.json').read_text());signals=json.loads((ROOT/'data/signals.json').read_text())
    for stock in stocks['stocks']:
        if stock['id']==c['id']:
            stock['reportAsOf']=DATE;stock['reportRevision']=s['reportRevision']
            for report in stock['reports'].values():report['available']=True
    signals['signals'][c['id']]=s;signals['updatedAt']=datetime.now(timezone.utc).isoformat()
    (ROOT/'data/stocks.json').write_text(json.dumps(stocks,ensure_ascii=False,indent=2)+'\n');(ROOT/'data/signals.json').write_text(json.dumps(signals,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'docs/reports/anthropic-ant.md').write_text('# Anthropic レポート作成記録\n\n分析基準日 '+DATE+'。上場後10-Qは未提出。確定目論見書・IPO完了8-Kを起点とする。\n\n'+ '\n\n'.join(x['id']+' '+x['title']+'\n'+x['url'] for x in b['sources'])+'\n\n再生成: `python scripts/generate_anthropic_reports.py`\n\nIPO反映後現金は推計。潜在株・Amazon残存ノートは全転換の経済的近似で、二重に負債控除しない。9月末自己保有公益基金株は現在の経済株式数から除外。金融リース債務の増加を現金調達収入へ加えない。将来条件とDCFは当方仮定。C4の価格幅は代替5手法の検討後も未算出。\n')
    print('ANT cases:',[round(x['price'],2) for x in b['scenario']['cases']],'DCF:',round(dcf_value(c)[2],2),'signal:',s['position'],s['zone'])


if __name__=='__main__':main()
