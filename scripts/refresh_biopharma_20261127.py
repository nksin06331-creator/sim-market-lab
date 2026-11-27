"""Render the two clinical-stage reports from the audited 2026-11-27 bundles.

Requires the user-provided v6.2 templates. Does not change site registration,
quotes or signals. Content files retain model assumptions for reproduction.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
from generate_eli_lilly_reports import esc,usd,pct,row,bullets,detail,guide_box,signal,render
ROOT=Path(__file__).resolve().parents[1]
IDS=['abcellera-abcl','moonlake-mltx']

def conditional_price(d,x,primary_prob=None,secondary_prob=None,primary_cf_scale=1.0,spend=None):
 param=x['caseparams'][1];prob,scale,discount,dev,base_spend,draw,other,sbc=param
 asset=0
 for j,(_,flows,_) in enumerate(x['assets']):
  pr=(primary_prob if primary_prob is not None else prob) if j==0 else (secondary_prob if secondary_prob is not None else max(.05,prob-.25))
  cfscale=scale*(primary_cf_scale if j==0 else 1)
  asset+=pr*sum(v*cfscale*1e6/(1+discount)**(i+1) for i,v in enumerate(flows))
 if d['meta']['ticker']=='ABCL':asset+=sum(10e6*scale/(1+discount)**i for i in range(1,11))
 cap=d['capital_structure'];cash=cap['cash']-cap['restricted_cash']+cap['liquid_securities']-(base_spend if spend is None else spend)*1e6+draw*1e6
 eq=asset-dev*1e6+cash-(cap['debt']+draw*1e6)-other*1e6
 mi=x['model_inputs'];n=cap['basic_shares']+mi['rsu']+mi['prefunded']+sbc*1e6;price=eq/n;previous=[]
 for _ in range(12):
  options=[o for o in mi['option_groups'] if price>o['strike']];proceeds=sum(o['shares']*o['strike'] for o in options);shares=sum(o['shares'] for o in options);price=(eq+proceeds)/(n+shares)
  if options==previous:break
  previous=options
 return price


def refresh_outcomes(d,x):
 p=d['meta']['price'];base=x['caseparams'][1]
 assert math.isclose(conditional_price(d,x),d['scenario']['cases'][1]['price'],rel_tol=1e-10)
 for idx,e in enumerate(d['catalyst_report']['catalysts']):
  for outcome,label,shift in zip(e['outcomes'],['期待以上','ほぼ想定どおり','期待外れ・遅延'],[.10,0,-.10]):
   if idx==0:
    low,high=[base[0]+shift+v for v in [-.025,.025]];values=[conditional_price(d,x,primary_prob=v) for v in [low,high]]
    note=f'主資産の成功確率を{low*100:g}～{high*100:g}%へ変更。他資産の確率とCF・費用・株式条件は標準に固定。'
    condition=label+'：規制・臨床の情報を主資産の成功確率へ反映する当方条件。'
   elif idx==1 and d['meta']['ticker']=='MLTX':
    low,high=[base[0]-.25+shift+v for v in [-.025,.025]];values=[conditional_price(d,x,secondary_prob=v) for v in [low,high]]
    note=f'PsA資産の成功確率のみ{low*100:g}～{high*100:g}%へ変更。HS成功確率、CF、費用、株式条件は標準固定。'
    condition=label+'：IZAR/P-OLARIS情報をPsAの確率へ反映する当方条件。'
   elif idx==1:
    low,high=[1+shift+v for v in [-.025,.025]];values=[conditional_price(d,x,primary_cf_scale=v) for v in [low,high]]
    note=f'ABCL635の成功時CFを標準の{low:g}～{high:g}倍へ変更。確率・割引率・費用・株式条件は固定。新規IND候補の別価値は加算しない。'
    condition=label+'：VMSの適応・普及の見通しを635成功時CF幅へ反映する当方条件。IND準備だけで承認成功としない。'
   else:
    # Financing does not create enterprise value: proceeds and matching debt cancel.
    low,high=base[4]-shift*300-10,base[4]-shift*300+10;values=[conditional_price(d,x,spend=v) for v in [low,high]]
    note=f'2027年末までの純支出を{low:g}～{high:g}百万USDへ変更。他の確率・CF・残存費・借入・株式は標準固定。追加借入は現金と負債を同額計上し、その受領だけで価値を増やさない。'
    condition=label+'：開発・事業化準備の純支出と資金効率が標準より改善・維持・悪化する当方条件。'
   values.sort();outcome['price_range']=values;outcome['price_change_pct_range']=[(v/p-1)*100 for v in values];outcome['method_note']='このレポートの条件付き試算。'+note+'短期反応や市場の真の成功確率ではない。';outcome['conditions']=[condition]
 return d


def build(id,materials):
 d=json.loads((ROOT/f'data/reports/{id}.json').read_text());x=json.loads((ROOT/f'data/reports/{id}-content.json').read_text());d=refresh_outcomes(d,x);(ROOT/f'data/reports/{id}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');m=d['meta'];sc=d['scenario'];cap=d['capital_structure'];cat=d['catalyst_report'];cl={c['id']:c['statement'] for c in d['claims']};p=m['price'];co=sc['computed'];cases=sc['cases'];bear,base,bull=cases;name=x['name'];ticker=m['ticker'];date=m['valuation_date'];back='<a href="../../index.html">SiM MARKET LABの銘柄一覧へ戻る</a>'
 sources='<ul>'+''.join(f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(s["id"]+"："+s["title"])}</a>（取得 {esc(s["accessed_at"][:10])}）</li>' for s in d['sources'])+'</ul>'
 basis=f'評価基準株価{usd(p)}／市場時刻{m["price_as_of"]}。分析基準日{date}、評価対象2027年末。'
 warning='未承認資産の価値を扱う高リスクの条件付き試算です。将来の患者数、価格、成功時CF、成功確率、開発費は当方仮定で、会社予想や臨床成功の統計予測ではありません。借入条件・規制判断・希薄化も確認してください。'
 warn='<div class="wrap"><p class="notice">'+warning+'</p></div>'
 common=dict(COMPANY_NAME=name,TICKER=ticker,EXCHANGE='Nasdaq／USD',VALUATION_DATE=date,CURRENT_PRICE=usd(p),CURRENT_PRICE_NOTE='米国2026/11/25取引分',DISCLAIMER='情報提供・教育目的の条件付き分析です。投資助言・売買推奨ではありません。未承認薬の有効性・安全性・販売成功を保証せず、臨床・規制・資金条件で大きく変わります。価格比較は配当を含みません。',FOOTER_NOTE=esc(basis)+'<br>'+back)
 def fact(k):return esc(cl[k])
 def boxes(items):return '<div class="info-row">'+''.join(guide_box(a,b) for a,b in items)+'</div>'
 terms=[('抗体医薬','特定の標的に結合する抗体を利用する薬。標的の理屈だけで臨床での有効性は確定しません。'),('臨床試験','人で安全性・有効性を調べる試験。第1相、第2相、第3相では目的と必要証拠が異なります。'),('主要評価項目','治験で中心となる判定指標。複数指標や解析集団の違いを混同しません。'),('BLA','米国で生物学的製剤の承認を求める申請。提出、受理、承認は別の段階です。'),('IND','米国で治験を行うための手続き。提出だけで全試験の実施許可を保証するものではありません。'),('PDUFA目標日','FDAの審査判断の目安。割当て前に確定日を創作せず、承認確約とも扱いません。'),('成功確率','モデル上の不確実性を表す仮定。臨床で実測した確率や市場の真の予想ではありません。'),('rNPV','将来の成功時現金収支を割引き、開発リスクを調整した資産価値。確率を重ね掛けしません。'),('残存開発費','今後必要となる治験・開発費。2027年末前の支出と2028年以降を分け、二重控除しません。'),('前払ワラント','大部分の行使代金を払った株式取得権。普通株に加えて潜在株へ反映します。'),('資金ランウェイ','過去支出からみた簡易的な資金余力。将来の試験費や借入条件が変われば変化します。'),('希薄化','株式報酬や資金調達で1株の取り分が減ること。行使現金と追加株式を同時に反映します。')]
 guide=dict(COMPANY_NAME=name,TICKER=ticker,INDUSTRY='臨床段階バイオ・抗体医薬',DATE=date,TAGLINE=fact('BUSINESS'),HERO_TAGS=''.join(f'<span class="hero-tag">{z}</span>' for z in ['米国株','Nasdaq','臨床開発','承認前']),HERO_STATS=''.join(f'<div class="stat"><div class="stat-value">{v}</div><div class="stat-label">{k}</div><div class="stat-note">{n}</div></div>' for v,k,n in [(usd(p),'評価基準株価','米国2026/11/25取引分'),(f'${(cap["cash"]-cap["restricted_cash"]+cap["liquid_securities"])/1e6:.1f}M','現金等','2026年9月末・自由現金＋有価証券'),('ABCL635' if ticker=='ABCL' else 'SLK','主な開発資産','未承認・開発中')]),SEC1_TLDR=bullets('承認前の開発企業で、臨床・規制と資金の両方が重要です。','臨床データの達成と、承認・保険採用・販売成功を区別します。','会社の予定と当方の価値モデルを分けて表示します。'),SEC1_FACTS=boxes([('会社と沿革',fact('IDENTITY')+(' [S1,S2,S4]' if ticker=='ABCL' else ' [S1,S2]')),('直近業績',fact('FINANCIAL')+' [S1,S2]')]),SEC1_CARDS='<div class="card-grid">'+''.join(guide_box(a,b) for a,b in [('何をする会社',fact('BUSINESS')+' [S1,S2]'),('主力',('ABCL635と抗体探索・提携。ABCL575の第1相以降の開発価値は加算しません。' if ticker=='ABCL' else 'Sonelokimabの炎症性疾患向け開発。承認済み薬として扱いません。')+' [S2]'),('直近業績',fact('FINANCIAL')+' [S1,S2]'),('注目点','臨床・規制の不確実性を減らせるか。費用・資金・希薄化とセットで確認します。[S1,S2]')])+'</div>',SEC1_BIZMODEL=boxes([('収益と投資',fact('BUSINESS')+' [S1,S2]'),('資金の読み方',fact('FUNDING')+' [S1,S2]')]),SEC1_HIGHLIGHT='<div class="highlight-box">未承認薬です。試験結果、申請提出、受理、審査目標日、承認、販売開始は別の事実です。</div>',SEC2_ICON='◇',SEC2_LABEL='業界',SEC2_TITLE='薬効・規制・採用が価値を作る',SEC2_SUB='良いデータだけでは売上が確定しない',SEC2_TLDR=bullets('治験・規制・製造・保険アクセスを順に確認します。','別の試験の反応率をそのまま横比較しません。','市場規模・将来シェアは未確認の数値を置きません。'),SEC2_CONTENT=boxes([('患者と医療現場','薬の効果だけでなく安全性・忍容性・投与頻度が選択に影響します。保険採用と自己負担が普及を左右します。'),('開発から販売','治験設計と評価項目を満たし、規制判断・製造・販売体制を整える必要があります。[S1,S2]'),('競争の軸',fact('COMPETITION')+' [S1,S2]')]),SEC3_LABEL='開発候補',SEC3_TITLE='主要候補の現在地',SEC3_SUB='最新公式開示と未確定事項',SEC3_TLDR=bullets('完了した試験・提出と今後の判断を分けます。','取得資料で確認できない受理・承認を既成事実化しません。','開発継続を止める候補は価値に足しません。'),SEC3_CONTENT=boxes([('開発状況',fact('PRODUCT')+' [S1,S2]'),('事業の広がり',fact('BUSINESS')+' [S1,S2]')]),SEC4_LABEL='資金',SEC4_TITLE='開発を続けるための財務余力',SEC4_SUB='未使用枠は今の現金ではない',SEC4_TLDR=bullets('現金・有価証券と制限現金を分けます。','条件付き融資や政府枠を自由現金へ足しません。','試験費・発売準備・希薄化の変化を追います。'),SEC4_CONTENT=boxes([('現在の資金',fact('FINANCIAL')+' [S1,S2]'),('会社の資金見通し',fact('FUNDING')+' [S1,S2]'),('簡易資金余力',fact('RUNWAY')+' [S2]'),('リスク',fact('RISKS')+' [S1,S2]')]),SEC5_LABEL='競合',SEC5_TITLE='同じ患者課題を解く治療と比べる',SEC5_SUB='薬効と事業化条件を揃える',SEC5_TLDR=bullets('承認済み薬には販売・安全性の蓄積があります。','新薬候補の優位は同じ比較条件で確認します。','取得していない競合売上や市場シェアは表示しません。'),SEC5_CONTENT=boxes([('治療選択肢',fact('COMPETITION')+' [S1,S2]'),('確認する差','有効性、安全性、投与負担、対象患者、価格、保険採用を比較します。別試験の数値だけで優劣を断定しません。')]),SEC6_TLDR=bullets('申請の提出・受理・承認は別です。','成功確率は当方のモデル仮定です。','融資は実行条件と返済条件まで確認します。'),SEC6_CONTENT='<div class="term-list">'+''.join(f'<details class="term-item"><summary class="term-header"><span class="term-name">{esc(a)}</span><span class="term-arrow">⌄</span></summary><div class="term-body"><p>{esc(b)}</p></div></details>' for a,b in terms)+'</div>',SEC7_TLDR=bullets('臨床・規制の次の確認点を追います。','試験・製造・上市準備の費用と資金を見ます。','一つの資産へ重なる材料を別価値として足しません。'),SEC7_CONTENT=boxes([('公式の進捗',fact('C1')+' [S1,S2]'),('次の開発',fact('C2')+' [S1,S2]'),('資金と事業化',fact('C3')+' [S1,S2]')])+detail('主要出典と基準',sources+'<p>'+esc(basis)+'</p><p>'+back+'</p>'))
 watch=''.join(signal(e['item'],esc(e['frequency']+'：'+e['update_trigger'])) for e in cat['watch_items'])
 model_rows=''.join(row(label,f'{params[0]*100:g}%',f'{params[1]:g}倍',f'{params[2]*100:g}%',f'${params[3]:g}M',f'${ar["ev"]/1e6:.1f}M',f'${ar["cash"]/1e6:.1f}M',f'${ar["debt"]/1e6:.1f}M',f'{case["diluted_shares"]/1e6:.2f}M',usd(case['price'])) for label,case,params,ar in zip(['悲観','標準','楽観'],cases,x['caseparams'],x['asset_rows']))
 assets=''.join(detail(a[0],esc(a[2])+'<p>成功時CF（百万USD、2028年から年順）：'+esc('、'.join(str(v) for v in a[1]))+'</p>') for a in x['assets'])
 assumptions=[('基準株価',usd(p),'市場データ',m['price_as_of']+' [S3]'),('株式数',f'{cap["diluted_shares"]/1e6:.2f}百万株','このレポートの推定',cl['SHARES']),('成功確率・CF・費用','ケース別に表示','このレポートの推定','患者数・単価・普及率・CF率を条件に置く。会社予想ではない。'),('現金・有価証券',f'${(cap["cash"]-cap["restricted_cash"]+cap["liquid_securities"])/1e6:.3f}M','公式情報で確認済み','2026年9月末 [S2]'),('将来支出・借入・株式','2027年末前後を分ける','このレポートの推定',cl['BUDGET']),('総合判定',cl['SIGNAL'],'このレポートの推定','3レポートの事業・材料・評価リスクを分析日時点で再評価。')]
 rr='N/A（基準株価がシナリオ帯外）' if co['endpoint_rr'] is None else f'{co["endpoint_rr"]:.2f}倍'
 zone='楽観端点を上回る' if co['raw_band_position_pct']>100 else '悲観端点を下回る' if co['raw_band_position_pct']<0 else '悲観～楽観帯の中'
 vals=dict(common,METHOD='資産別rNPV＋資金・希薄化調整',VERDICT_STATUS='臨床と資金の条件を分けて読む',VERDICT_LINE_1=f'標準ケース{usd(base["price"])}、3ケース加重値{usd(co["expected_price"])}。現在価格は{zone}。',VERDICT_LINE_2='未承認資産の成功時CFを割引き、成功確率を1回だけ反映。費用・資金と将来株式も明示します。',SCORE=str(co['supplemental_score']),BASE_PRICE=usd(base['price']),BASE_DELTA=pct((base['price']/p-1)*100),EXPECTED_VALUE=usd(co['expected_price']),EXPECTED_DELTA=pct(co['expected_delta_pct']),RISK_CLASS='高い',RISK_NOTE='臨床・規制・将来CFと希薄化に依存',WARN_BAND=warn,WARN_MESSAGE=warning,SNAPSHOT_LEAD=esc(basis),BAND_POSITION=f'{co["display_band_position_pct"]:.1f}%',ZONE_JUDGE=zone,ZONE_NOTE=f'丸め前の価格帯位置は{co["raw_band_position_pct"]:.1f}%。帯外でも表示ピンのみ0～100%へ固定し、真の成功確率とは扱いません。',MARKET_SCORE=str(co['market_score']),OWN_SCORE=str(co['own_score']),MARKET_REVERSE_NOTE='同じ資産CFと資金条件を市場も使うという仮定で、悲観・楽観の株主価値端点から現在時価総額の位置を逆算します。現値に合うよう成功CFを先に調整していません。独立DCF・市場コンセンサスによる検証は未実施です。',SCENARIOS_LEAD='対象は2027年末。2028～2037年の成功時税後CFを割引き、資産別成功確率を反映して残存開発費を控除。2027年末前の支出と2028年以降の開発費を分けます。',PRICE_ZONE_ROWS=''.join(f'<div class="zone"><div><b>{a}</b></div><p>{b}</p></div>' for a,b in [(f'{usd(bear["price"])}未満','悲観モデル外。臨床・資金の追加悪化を検討。'),(f'{usd(bear["price"])}～{usd(base["price"])}','悲観と標準の間。標準達成を保証しない。'),(f'{usd(base["price"])}～{usd(bull["price"])}','開発成功・採用と資金の強い条件が必要。'),(f'{usd(bull["price"])}超','今回の楽観端点以外の価値が必要。前提の再検証が重要。')]),SIGNAL_ROWS=''.join(signal(e['title'],esc(e['plain_language'])+' [S1,S2]') for e in cat['catalysts'])+signal('臨床と財務の反証',fact('RISKS')+' [S1,S2]'),POSITIVES=bullets('主要候補について臨床・規制の次の開発計画を会社が説明。[S1,S2]','現金・有価証券を保有。未使用枠と区別して計上。[S2]','成功時の適応・普及拡大余地を検討できるが、保証ではない。'),CONCERNS=bullets(cl['RISKS'],'成功時CF・価格・費用・確率への感応度が大きい。','臨床成功だけで承認・上市・保険採用は保証されない。'),FORMULA=esc(sc['method_explanation']),CALC_TABLE_HEAD=''.join(f'<th>{v}</th>' for v in ['ケース','主資産確率','CF倍率','割引率','残存開発費PV','資産価値','期末現金等','借入','将来株式','価格']),CALC_TABLE_ROWS=model_rows,CALC_NOTICE='将来CFと成功確率は当方仮定。資産価値は残存開発費控除後。その他請求権・行使現金・追加株式を株主価値の橋渡しで処理。現金と融資枠を重複加算しません。',CONDITIONS=''.join(detail(f'{label}：{usd(case["price"])}／{case["probability"]*100:g}%',esc(' '.join(case['conditions']))) for label,case in zip(['悲観','標準','楽観'],cases)),SENSITIVITY_HEAD='<th>変数</th><th>低位</th><th>標準</th><th>高位</th>',SENSITIVITY_ROWS=''.join(row(esc(s['variable']),*(usd(v) for v in s['result_prices'])) for s in sc['sensitivity']),SENSITIVITY_NOTE='主要資産成功確率と割引率を1つずつ変更。他は標準ケースに固定し、オプション行使を必要に応じ再判定。CFと確率の独立性を保証する表ではありません。',DIST_LEAD='3点の離散分布のみ。モンテカルロは未実施。',DIST_ROWS=''.join(signal(f'{label}：{usd(case["price"])}',f'当方主観確率 {case["probability"]*100:g}%') for label,case in zip(['悲観','標準','楽観'],cases)),DIST_SUMMARY='悲観30%／標準45%／楽観25%の主観配分。臨床・規制・資金リスクを悲観側へやや厚く置く分析上の仮定で、実測成功率ではありません。',ENDPOINT_RR=rr,WATCH_ROWS=watch,ASSUMPTIONS_ROWS=''.join(row(*(esc(v) for v in a)) for a in assumptions),DEEPDIVE_DETAILS=assets+detail('現在株式・潜在株',fact('SHARES')+' [S2]')+detail('資金・将来支出',fact('BUDGET')+' '+fact('RUNWAY')+' [S2]')+detail('3レポート総合判定',fact('SIGNAL'))+detail('市場データの補助情報',fact('QUOTE_STATS')+' [S3]')+detail('主要出典・更新履歴',sources+f'<p>{date} 全面再作成。</p>'))
 for n,case in zip(['BEAR','BASE','BULL'],cases):
  vals.update({f'{n}_PRICE':usd(case['price']),f'{n}_DELTA':pct((case['price']/p-1)*100),f'{n}_PROB':f'{case["probability"]*100:g}%',f'{n}_DL_ROWS':''.join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a,b in [('対象','2027年末'),('資産価値',f'${case["enterprise_value"]/1e6:.1f}M'),('株主価値',f'${case["equity_value"]/1e6:.1f}M'),('将来株式',f'{case["diluted_shares"]/1e6:.2f}M')])})
 cards=[];labels={'SUCCESS':'期待以上','INLINE':'ほぼ想定どおり','FAILURE':'期待外れ・遅延'}
 for e in cat['catalysts']:
  outs=''.join(f'<div class="outcome"><h4>{labels[o["label"]]}</h4><div class="impact">{usd(o["price_range"][0])}～{usd(o["price_range"][1])}</div><p>基準価格比 {pct(o["price_change_pct_range"][0])}～{pct(o["price_change_pct_range"][1])}</p><p>{esc(o["conditions"][0])}</p><p>{esc(o["method_note"])}</p></div>' for o in e['outcomes']);nq=e['priced_in']['non_quantified_explanation']
  cards.append(f'<article class="catalyst-card"><div class="catalyst-head"><h3>{esc(e["title"])}</h3><span class="chip">重要度{e["importance"]}</span></div><div class="date-box"><b>{esc(e["date"]["display_text"])}</b></div><p>{esc(e["plain_language"])}</p><p>結果は当方モデル条件との比較です。短期反応率・市場予想の実測差・臨床成功確率を示すものではありません。</p><div class="outcomes">{outs}</div><div class="priced unknown"><b>個別の期待割合は出していません</b>'+''.join(f'<p>{a}：{esc(b)}</p>' for a,b in [('出していない理由',nq['reason']),('足りない情報','、'.join(nq['missing_information'])),('次に見る数字','、'.join(nq['next_checks'])),('再計算方法',nq['recalculation_method'])])+'</div>'+detail('根拠・反証・資金・更新','出典 [S1,S2]。'+fact('RISKS')+'<p>資金：'+esc(e['financing_risk'])+'</p><p>先行指標：'+esc('、'.join(e['leading_indicators']))+'</p><p>更新：'+esc('、'.join(e['update_triggers']))+'</p><p>材料出尽くし：'+esc(e['sell_the_news_risk'])+'</p>')+detail('価格幅の手法検討','企業価値差分は共有する開発資産を単独で分離できず不採用。共通条件付き資産モデルを採用。独立した市場予想改定、同社・他社イベント比較は同条件の標本を未取得のため不採用・適用外。')+'</article>')
 over=cat['overall_priced_in'];lo,hi=over['percent_range'];cv=dict(common,LAST_UPDATED=date,REPORT_STATUS='臨床・規制・事業化の条件を確認',SUMMARY_LINE_1='最新の公式発表・決算と未完了の材料を区別。臨床段階の不確実性を残した条件付き評価です。',SUMMARY_LINE_2='同じ資産の臨床・規制・上市・資金を共通価値グループに束ね、段階ごとの価格や割合を足しません。',OVERALL_PRICED_IN=f'{lo:.0f}～{hi:.0f}%',OVERALL_PRICED_LABEL='共通資産価値による推定',PRICED_IN_CONFIDENCE='低い',NEXT_CATALYST_TITLE=cat['catalysts'][0]['title'],NEXT_CATALYST_WINDOW=cat['catalysts'][0]['date']['display_text'],DATE_CONFIDENCE='会社見通し・条件付き',CATALYST_COUNT='3件',WARN_BAND=warn,NO_CATALYST_NOTICE='',OVERALL_PRICED_BLOCK=f'<div class="priced"><div class="priced-head"><b>{lo:.0f}～{hi:.0f}%</b><span>このレポートの条件付き推定</span></div><p>丸め前の逆算値{over["raw_implied_pct"]:.1f}%。0～100%外は帯外として表示だけ端へ固定。</p><p>{esc(over["method_note"])}</p></div>',PRICED_IN_METHOD=esc(over['method_note']),SURPRISE_UP='公式な規制・臨床の進展で不確実性が下がり、当方標準の成功CF・費用条件を上回る。',SURPRISE_DOWN='追加試験、審査・上市遅延、安全性・採用・資金支出が標準を下回る。',PRIMARY_RISK=cl['RISKS'],TIMELINE_ROWS=''.join(f'<div class="time-row"><div class="time-date">会社予定</div><div class="time-dot"></div><div class="time-body"><b>{esc(e["title"])}</b><p>{esc(e["date"]["display_text"])}</p></div></div>' for e in cat['catalysts']),CATALYST_CARDS=''.join(cards),DEPENDENCY_ROWS='<p>同じ開発資産の臨床・規制・上市・資金を1回だけ評価。HSとPsAは別の患者需要を置いても、薬剤・資金・安全性の相関リスクが残ります。ABCLの未選択候補価値やMLTXのPPP価値を別加算しません。</p>',WATCH_ROWS=watch,ASSUMPTION_ROWS=''.join(row(esc(a),esc(b),esc(k),date,esc(note)) for a,b,k,note in assumptions),SOURCE_DETAILS=sources,VALIDATION_DETAILS='<p>JSON形式・算術・出典参照・確率・日程・依存関係・HTMLを検証。次は分析上の制約。</p><ul>'+bullets(*d['validation_summary']['messages'])+'</ul>',UPDATE_HISTORY=f'<p>{date} 全面再作成。各3レポートは同じ共通データと分析基準を使用。</p>')
 out=ROOT/'stocks'/id
 for file,template,v in [('company.html','template_stock_guide_v4_unified.html',guide),('valuation.html','template_scenario_v4_unified.html',vals),('catalysts.html','template_catalyst_v1_unified.html',cv)]:
  (out/file).write_text(render(materials,template,v),encoding='utf-8');print(out/file)

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--materials',type=Path,default=ROOT.parent/'report-generation-materials');args=ap.parse_args()
 for id in IDS:build(id,args.materials)
