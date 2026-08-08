# SiM MARKET LAB — MacBook Air引き継ぎ

## MacのCodexへ最初に送る指示

このフォルダをCodexのローカルプロジェクトとして開き、次の文章を送る。

```text
MAC_HANDOFF.md、AGENTS.md、README.md、docs/signal-methodology.mdを読んでください。
SiM MARKET LABの作業をWindows PCから引き継ぎます。
まず全ファイルを検証し、GitHubアカウント nksin06331-creator に
新しい公開リポジトリ sim-market-lab を作成してGitHub Pagesで公開する準備を続けてください。
既存の古いサイトや以前の会話履歴は参照しないでください。
外部公開前に変更内容と公開対象を確認してください。
```

## プロジェクトの目的

日本株・米国株について、銘柄ごとに次の3レポートを掲載する。

1. 企業について
2. 現在の株価
3. 今後のカタリスト

メインページから各レポートへ移動できる。レポート同士は直接移動できず、各レポートのサイト内戻るボタンは必ずメインページへ戻る。

## 確定済み仕様

- サイト名：SiM MARKET LAB
- 公開先候補：`nksin06331-creator/sim-market-lab`
- 公開方法：GitHub Pages
- 登録テスト銘柄：キオクシアホールディングス（285A.T）、Rocket Lab（RKLB）
- 現在株価と前日比：毎日、日本時間8時にGitHub Actionsで更新
- 暫定株価取得元：Yahoo Finance chart endpoint
- 取得失敗時：前回の正常値を残してstale表示
- 検索、日本株・米国株フィルター、並び替え、カード・一覧切替を維持
- レポート未作成のボタンは無効化し、存在しないページへ移動させない
- 最初の約10銘柄は人が確認してから公開し、安定後に自動公開へ移行

## 売られすぎ・中立・買われすぎ

テクニカル指標は使用しない。3レポートから総合判定する。

- レポート② 現在株価：60%
- レポート③ カタリスト：25%
- レポート① 企業基盤・リスク：15%
- 0.0～30.0：売られすぎ
- 30.1～69.9：中立
- 70.0～100.0：買われすぎ
- 3レポートが揃わない、または根拠不足：判定保留

詳細は`docs/signal-methodology.md`を正本とする。毎朝の株価更新で総合判定を変更してはいけない。

## 現在の完成状況

- メインページ初期版：完成
- レスポンシブCSS：完成
- 銘柄検索・フィルター・並び替え：完成
- カード・一覧切替：完成
- 株価・前日比取得：2銘柄で動作確認済み
- GitHub Actions株価更新：作成済み
- GitHub Pagesデプロイワークフロー：作成済み
- 公開前データ・リンク検査：作成済み
- 3種類のレポート本文：未作成
- GitHubリポジトリ：未作成
- GitHubへのpush：未実施

## 重要ファイル

- `index.html`：メインページ
- `assets/css/styles.css`：デザイン
- `assets/js/app.js`：検索・表示処理
- `data/stocks.json`：銘柄固定情報
- `data/prices.json`：現在株価・前日比
- `data/signals.json`：レポート総合判定
- `scripts/update_prices.py`：株価取得処理
- `scripts/validate_site.py`：公開前の一括検査
- `.github/workflows/`：株価更新とPages公開
- `AGENTS.md`：Codexが必ず守るリポジトリ規則
- `docs/signal-methodology.md`：総合判定仕様

## 公開前の検証

1. JSONをすべてパースする。
2. JavaScriptとPythonの構文を確認する。
3. ローカルHTTPサーバーで表示する。
4. 検索、市場切替、並び替え、カード・一覧切替を確認する。
5. レポート準備中ボタンが移動できないことを確認する。
6. GitHub Actionsの権限とPages設定を確認する。
7. 公開対象に秘密情報がないことを確認する。

## PCの役割

- MacBook Air：GitHubとサイトの主管理端末
- WindowsゲーミングPC：予備・Windows表示確認
- 会社Windows PC：ChatGPT Workへの指示と公開サイト確認。APIキーを保存しない
