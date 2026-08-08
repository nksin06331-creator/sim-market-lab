# SiM MARKET LAB

日本株・米国株について、企業概要、現在株価、今後のカタリストの3種類のレポートを掲載する静的サイトです。

## 現在の構成

- `index.html`：メインページ
- `assets/`：メインページのCSSとJavaScript
- `data/stocks.json`：銘柄の固定情報とレポートの公開状態
- `data/prices.json`：自動更新される株価と前日比
- `data/signals.json`：3つのレポートから作成する売られすぎ・中立・買われすぎ判定
- `docs/signal-methodology.md`：レポート総合判定の計算・保留ルール
- `scripts/update_prices.py`：暫定株価取得処理
- `scripts/validate_site.py`：銘柄、株価、総合判定、レポートリンクの公開前検査
- `.github/workflows/update-prices.yml`：日本時間8時の自動更新
- `.github/workflows/deploy-pages.yml`：GitHub Pagesへの公開

## ローカル確認

ブラウザの制約により、`index.html`を直接開くのではなくHTTPサーバーを使用します。

```text
python -m http.server 8000
```

その後、`http://localhost:8000/`を開きます。

## 公開前の注意

現在の株価取得元は開発用の暫定構成です。公開規模が大きくなる前に、外部表示・再配信が許可された正式なデータ提供契約へ切り替えてください。

公開前には次を実行します。

```text
python scripts/validate_site.py
```
