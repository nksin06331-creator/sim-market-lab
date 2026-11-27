# テスラ 出典・分析記録

分析基準日 2026-11-28。最新決算は2026年3Q。

S1 2026年3Q Form 10-Q
https://www.sec.gov/Archives/edgar/data/1318605/000162828026066775/tsla-20260930.htm

S2 Q3 2026 Update（決算添付資料）
https://www.sec.gov/Archives/edgar/data/1318605/000162828026066738/exhibit9914.htm

S3 2026年3Q 生産・引渡し・蓄電池設置発表
https://www.sec.gov/Archives/edgar/data/1318605/000162828026064366/exhibit991111111.htm

S4 最新SEC提出履歴
https://data.sec.gov/submissions/CIK0001318605.json

S5 市場価格（日足・時点値）
https://query1.finance.yahoo.com/v8/finance/chart/TSLA?range=3mo&interval=1d

再生成: `python scripts/generate_spacex_tesla_reports.py`

前提は `data/report-inputs/spacex-tesla-20261128.json`。株式は証券別TSMではなく明示した近似、将来売上・倍率・確率は当方仮定。独立DCF・同業倍率・市場コンセンサスは未検証。
