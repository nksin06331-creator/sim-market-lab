# Anthropic レポート作成記録

分析基準日 2026-11-28。上場後10-Qは未提出。確定目論見書・IPO完了8-Kを起点とする。

S1 確定目論見書（424B4、2026年9月期財務・資本・契約）
https://www.sec.gov/Archives/edgar/data/2130357/000162828026074944/anthropicpbc-424b4.htm

S2 IPO・私募完了と資本構造の8-K
https://www.sec.gov/Archives/edgar/data/2130357/000162828026075973/ant-20261119.htm

S3 IPO・追加発行・同時私募完了の公式発表
https://www.anthropic.com/news/ipo-close

S4 AI for Science拡大（無料クレジットと研究段階の区別）
https://www.anthropic.com/news/ai-for-science-expands-foundations-research-institutions

S6 最新SEC提出履歴
https://data.sec.gov/submissions/CIK0002130357.json

S7 公益基金・株式拠出の公式説明
https://www.anthropic.com/news/public-benefit-fund

S8 S&P 500日足・補助比較
https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?range=3mo&interval=1d

S5 市場価格（日足・時点値）
https://query1.finance.yahoo.com/v8/finance/chart/ANT?range=3mo&interval=1d

再生成: `python scripts/generate_anthropic_reports.py`

IPO反映後現金は推計。潜在株・Amazon残存ノートは全転換の経済的近似で、二重に負債控除しない。9月末自己保有公益基金株は現在の経済株式数から除外。金融リース債務の増加を現金調達収入へ加えない。将来条件とDCFは当方仮定。C4の価格幅は代替5手法の検討後も未算出。
