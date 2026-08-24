# SiM MARKET LAB — Windows PC引き継ぎデータ

作成日: 2026-08-24
対象リポジトリ: `nksin06331-creator/sim-market-lab`
公開URL: https://nksin06331-creator.github.io/sim-market-lab/
現在の最新確認コミット: `6c93935 chore: update stock prices`

## 1. Windows PCへ渡すもの

Windows PCでも同じ運用をするには、次の2つを渡す。

1. GitHubリポジトリ
   - URL: `https://github.com/nksin06331-creator/sim-market-lab.git`
   - GitHub DesktopでCloneする。
   - サイト本体、既存レポート、株価更新、検証スクリプト、GitHub Actions設定が入っている。

2. レポート作成資料フォルダ
   - Mac側の場所: `/Users/nakayamatoshinobu/Desktop/SiM 運用フォルダ最新/report-generation-materials`
   - Windows側では、リポジトリと同じ親フォルダ直下に置く。
   - 例:

```text
SiM 運用フォルダ最新/
├─ sim-market-lab/
└─ report-generation-materials/
```

`sim-market-lab`だけでは既存サイトの確認と公開はできるが、新しい銘柄レポートを同じ形式で作るには`report-generation-materials`も必要。

## 2. report-generation-materialsの中身

Windowsへ渡す必要があるファイルは次の通り。

```text
01_combined_master_prompt_v6_2.md
02_source_evidence_rules_v1.md
03_stock_guide_analysis_rules_v5.md
04_scenario_analysis_rules_v3.txt
05_catalyst_analysis_rules_v2.txt
06_cross_report_validation_rules_v1.txt
07_html_binding_rules_v1.md
08_reader_language_mobile_ui_rules_v1.md
09_report_bundle_schema_v1.json
10_calculation_reference.py
11_validate_report_bundle.py
12_report_bundle.example.json
template_stock_guide_v4_unified.html
template_scenario_v4_unified.html
template_catalyst_v1_unified.html
```

特に重要なのは3つのHTMLテンプレート。

- `template_stock_guide_v4_unified.html`
- `template_scenario_v4_unified.html`
- `template_catalyst_v1_unified.html`

## 3. Windows側に必要なソフト

- GitHub Desktop
- Python 3
- ブラウザ
- Codex
- 任意: Visual Studio Code

Node.jsは通常運用では必須ではない。JavaScript構文確認をWindowsでも行う場合だけ必要。

## 4. 最初のセットアップ

GitHub Desktopで次をCloneする。

```text
https://github.com/nksin06331-creator/sim-market-lab.git
```

Clone後、同じ親フォルダに`report-generation-materials`を置く。

PowerShellでリポジトリに移動する例。

```powershell
cd "C:\Users\ユーザー名\Desktop\SiM 運用フォルダ最新\sim-market-lab"
```

Python確認。

```powershell
python --version
```

サイト検証。

```powershell
python scripts\validate_site.py
```

ローカル表示確認。

```powershell
python -m http.server 8000
```

ブラウザで開く。

```text
http://localhost:8000/
```

## 5. Codexへ最初に送る指示

Windows側でCodexに開かせるフォルダは`sim-market-lab`。

最初に送る文面。

```text
WINDOWS_HANDOFF.md、AGENTS.md、README.md、docs/signal-methodology.mdを読んでください。
SiM MARKET LABの作業をWindows PCで引き継ぎます。
既存の古いサイトや以前の会話履歴は参照しないでください。
report-generation-materialsフォルダは、sim-market-labと同じ親フォルダに置いてあります。
まずGitの状態、全ファイル、公開前検査を確認してから作業してください。
外部公開前に、公開対象と検証結果を私に報告してください。
GitHubへの公開は、私がGitHub DesktopでPush originを押します。
```

## 6. 現在登録済みの銘柄

現在は12銘柄。

```text
01 285A  kioxia-285a              キオクシアホールディングス
02 RKLB  rocket-lab-rklb          ロケット・ラボ
03 RDW   redwire-rdw              レッドワイヤー
04 4015  paycloud-4015            ペイクラウドホールディングス
05 5802  sumitomo-electric-5802   住友電気工業
06 ABCL  abcellera-abcl           アブセレラ
07 ASPI  asp-isotopes-aspi        ASPアイソトープス
08 MLTX  moonlake-mltx            ムーンレイク・イミュノセラピューティクス
09 ZETA  zeta-global-zeta         ゼータ・グローバル・ホールディングス
10 CRDO  credo-crdo               クレド・テクノロジー・グループ
11 LAES  sealsq-laes              シールエスキュー
12 5801  furukawa-electric-5801   古河電気工業
```

## 7. 重要ファイル

サイト本体。

```text
index.html
assets/css/styles.css
assets/js/app.js
lab/assets/js/live-report-price.js
```

データ。

```text
data/stocks.json
data/prices.json
data/signals.json
```

検証・更新。

```text
scripts/update_prices.py
scripts/validate_site.py
```

レポート生成スクリプト。

```text
scripts/generate_kioxia_reports.py
scripts/generate_rocket_lab_reports.py
scripts/generate_redwire_reports.py
scripts/generate_paycloud_reports.py
scripts/generate_sumitomo_electric_reports.py
scripts/generate_abcellera_reports.py
scripts/generate_asp_isotopes_reports.py
scripts/generate_moonlake_reports.py
scripts/generate_zeta_global_reports.py
scripts/generate_credo_reports.py
scripts/generate_sealsq_reports.py
scripts/generate_furukawa_electric_reports.py
```

既存レポート。

```text
stocks/*/company.html
stocks/*/valuation.html
stocks/*/catalysts.html
```

GitHub Actions。

```text
.github/workflows/update-prices.yml
.github/workflows/deploy-pages.yml
.github/workflows/validate-site.yml
```

## 8. 株価更新の方法

手動更新。

```powershell
python scripts\update_prices.py
```

この処理で行うこと。

- `data/stocks.json`の`quoteSymbol`を読む。
- Yahoo Finance chart endpointから株価を取得する。
- `data/prices.json`を更新する。
- レポート2のBear/Bull価格と現在株価から、表示用の現在地バーに使う`data/signals.json`の`components.valuation`と`position`を補助更新する。

取得に失敗した銘柄は、前回値を残して`stale`になる。

## 9. バー位置の現在仕様

メインサイトとレポート2の現在地バーは、表示時に次で再計算される。

```text
現在地バー = (prices.jsonの現在株価 - レポート2のBear価格) / (Bull価格 - Bear価格) × 100
```

0未満は0、100超は100に丸める。

対象ファイル。

```text
assets/js/app.js
lab/assets/js/live-report-price.js
scripts/update_prices.py
```

注意: `docs/signal-methodology.md`には初期方針として「毎朝の株価更新では総合判定を変更しない」とあるが、現在の実装では価格バーのズレを防ぐため、株価更新時に`signals.json`のvaluation位置と総合位置も補助更新している。今後、方針を固定するならドキュメント側を現仕様に合わせて更新する。

## 10. 新しい銘柄を追加する時の作業

基本手順。

1. 公式IR、決算、SEC/EDINET、株価情報を確認する。
2. 既存の`generate_*.py`を参考に、新しい生成スクリプトを作る。
3. `report-generation-materials`の3テンプレートから3レポートを生成する。
4. `data/stocks.json`へ銘柄を追加する。
5. `data/prices.json`へ初期株価を入れる。
6. `data/signals.json`へ初期シグナルを入れる。
7. `python scripts\update_prices.py`で現在株価を更新する。
8. `python scripts\validate_site.py`で検証する。
9. ローカルHTTPで表示確認する。
10. GitHub DesktopでCommitする。
11. 公開前報告後、GitHub DesktopでPush originする。

## 11. 公開前検査

最低限、次を実行する。

```powershell
python scripts\validate_site.py
```

ローカル表示確認。

```powershell
python -m http.server 8000
```

ブラウザで次を確認する。

```text
http://localhost:8000/
```

確認項目。

- メインページが開く。
- 検索できる。
- 日本株・米国株フィルターが動く。
- 並び替えが動く。
- カード・一覧切替が動く。
- スマホ幅で一覧が見にくくない。
- 各銘柄の3レポートに移動できる。
- 各レポートの戻るリンクがメインページに戻る。
- レポート同士への直接リンクがない。

## 12. 公開方法

CodexからGitHubへ直接pushしない運用。

1. Codexが作業する。
2. Codexが公開対象と検証結果を報告する。
3. GitHub Desktopで変更内容を確認する。
4. GitHub DesktopでCommitする。Codexがコミット済みなら不要。
5. GitHub Desktopで`Push origin`を押す。
6. GitHub Pagesの反映を待つ。
7. 公開URLを確認する。

公開URL。

```text
https://nksin06331-creator.github.io/sim-market-lab/
```

## 13. Windowsへ渡さなくていいもの

- Codexの過去会話履歴
- APIキー、トークン、パスワード
- 古いサイトのファイル
- ブラウザキャッシュ
- Mac固有の`.DS_Store`
- GitHub Desktopの内部設定

## 14. Windows側で詰まった時に確認すること

GitHubから最新版を取る。

```powershell
git pull --ff-only
```

状態確認。

```powershell
git status
```

検証。

```powershell
python scripts\validate_site.py
```

株価更新。

```powershell
python scripts\update_prices.py
```

ローカル表示。

```powershell
python -m http.server 8000
```

## 15. 重要な運用ルール

- 既存の古いサイトや過去会話履歴は参照しない。
- 公開前に必ず検証結果を報告する。
- 3レポートは独立。レポート同士を直接リンクしない。
- 戻るリンクは必ず`../../index.html`へ戻す。
- 秘密情報をGitに入れない。
- レポート作成資料は`report-generation-materials`を正本にする。
- 株価とバー位置は`prices.json`とレポート2のBear/Base/Bullで整合させる。
