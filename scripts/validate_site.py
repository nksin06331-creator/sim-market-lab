"""Validate SiM MARKET LAB data and report-link integrity before publishing."""

from __future__ import annotations

import json
import math
import re
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORT_KEYS = ("company", "valuation", "catalysts")
ALLOWED_MARKETS = {"JP": ("日本株", "JPY"), "US": ("米国株", "USD")}
ALLOWED_ZONES = {"売られすぎ", "中立", "買われすぎ"}
SIGNAL_METHOD = "three-report-weighted-synthesis-v1"
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attributes = dict(attrs)
        if attributes.get("href"):
            self.links.append(str(attributes["href"]))


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def load_json(path: Path, validation: Validation) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        validation.error(f"{path.relative_to(ROOT)}: JSONを読み込めません: {error}")
        return {}
    if not isinstance(value, dict):
        validation.error(f"{path.relative_to(ROOT)}: ルートはJSON objectである必要があります")
        return {}
    return value


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def expected_zone(position: float) -> str:
    if position <= 30:
        return "売られすぎ"
    if position >= 70:
        return "買われすぎ"
    return "中立"


def contains_forbidden_indicator(value: Any, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            if str(key).lower() in {"rsi", "rsi14"}:
                found.append(child_path)
            found.extend(contains_forbidden_indicator(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(contains_forbidden_indicator(child, f"{path}[{index}]"))
    return found


def validate_report_file(path: Path, stock_id: str, report_key: str, validation: Validation) -> None:
    try:
        html = path.read_text(encoding="utf-8")
    except OSError as error:
        validation.error(f"{stock_id}.{report_key}: HTMLを読み込めません: {error}")
        return
    parser = LinkParser()
    parser.feed(html)
    normalized_links = [link.split("#", 1)[0].split("?", 1)[0] for link in parser.links]
    if "../../index.html" not in normalized_links:
        validation.error(f"{stock_id}.{report_key}: ../../index.html へ直接戻るリンクがありません")
    sibling_names = {"company.html", "valuation.html", "catalysts.html"} - {path.name}
    forbidden = [link for link in normalized_links if Path(link).name in sibling_names]
    if forbidden:
        validation.error(f"{stock_id}.{report_key}: 他レポートへの直接リンクがあります: {forbidden}")
    if "history.back(" in html or "history.go(" in html:
        validation.error(f"{stock_id}.{report_key}: 履歴依存の戻る処理は禁止です")


def validate_stocks(payload: dict[str, Any], validation: Validation) -> tuple[dict[str, dict[str, Any]], set[str]]:
    raw_stocks = payload.get("stocks")
    if not isinstance(raw_stocks, list):
        validation.error("data/stocks.json: stocksは配列である必要があります")
        return {}, set()

    stocks: dict[str, dict[str, Any]] = {}
    tickers: set[str] = set()
    quote_symbols: set[str] = set()
    for index, stock in enumerate(raw_stocks):
        location = f"data/stocks.json stocks[{index}]"
        if not isinstance(stock, dict):
            validation.error(f"{location}: objectではありません")
            continue
        required = ("id", "ticker", "quoteSymbol", "name", "nameEn", "market", "marketLabel", "currency", "reports")
        for field in required:
            if stock.get(field) in (None, ""):
                validation.error(f"{location}: {field}がありません")
        stock_id = str(stock.get("id", ""))
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", stock_id):
            validation.error(f"{location}: idは小文字英数字とハイフンだけにしてください")
        if stock_id in stocks:
            validation.error(f"{location}: idが重複しています: {stock_id}")
        stocks[stock_id] = stock

        ticker = str(stock.get("ticker", "")).upper()
        if ticker in tickers:
            validation.error(f"{location}: tickerが重複しています: {ticker}")
        tickers.add(ticker)
        quote_symbol = str(stock.get("quoteSymbol", "")).upper()
        if quote_symbol in quote_symbols:
            validation.error(f"{location}: quoteSymbolが重複しています: {quote_symbol}")
        quote_symbols.add(quote_symbol)

        market = stock.get("market")
        if market not in ALLOWED_MARKETS:
            validation.error(f"{location}: marketが不正です: {market}")
        else:
            expected_label, expected_currency = ALLOWED_MARKETS[market]
            if stock.get("marketLabel") != expected_label:
                validation.error(f"{location}: marketLabelは{expected_label}である必要があります")
            if stock.get("currency") != expected_currency:
                validation.error(f"{location}: currencyは{expected_currency}である必要があります")

        reports = stock.get("reports")
        if not isinstance(reports, dict):
            validation.error(f"{location}: reportsがobjectではありません")
            continue
        for report_key in REPORT_KEYS:
            report = reports.get(report_key)
            if not isinstance(report, dict):
                validation.error(f"{location}: reports.{report_key}がありません")
                continue
            report_path = report.get("path")
            available = report.get("available")
            if not isinstance(report_path, str) or not report_path.startswith("./stocks/"):
                validation.error(f"{location}: reports.{report_key}.pathが不正です")
                continue
            if not isinstance(available, bool):
                validation.error(f"{location}: reports.{report_key}.availableはbooleanにしてください")
                continue
            absolute_path = ROOT / report_path.removeprefix("./")
            if available and not absolute_path.is_file():
                validation.error(f"{location}: 公開中レポートが存在しません: {report_path}")
            if available and absolute_path.is_file():
                validate_report_file(absolute_path, stock_id, report_key, validation)
            if not available and absolute_path.is_file():
                validation.warn(f"{location}: HTMLは存在しますが未公開です: {report_path}")
    return stocks, quote_symbols


def validate_prices(payload: dict[str, Any], stocks: dict[str, dict[str, Any]], validation: Validation) -> None:
    prices = payload.get("prices")
    if not isinstance(prices, dict):
        validation.error("data/prices.json: pricesはobjectである必要があります")
        return
    for forbidden in contains_forbidden_indicator(payload):
        validation.error(f"data/prices.json: 使用しないテクニカル指標があります: {forbidden}")
    unknown_ids = set(prices) - set(stocks)
    if unknown_ids:
        validation.error(f"data/prices.json: 未登録の銘柄IDがあります: {sorted(unknown_ids)}")
    for stock_id, stock in stocks.items():
        price = prices.get(stock_id)
        if price is None:
            validation.warn(f"{stock_id}: 株価は初回取得前です")
            continue
        if not isinstance(price, dict):
            validation.error(f"{stock_id}: 株価データがobjectではありません")
            continue
        if not is_number(price.get("price")) or price["price"] <= 0:
            validation.error(f"{stock_id}: priceは0より大きい数値が必要です")
        if price.get("currency") != stock.get("currency"):
            validation.error(f"{stock_id}: 株価通貨と銘柄通貨が一致しません")
        if price.get("status") not in {"ok", "stale"}:
            validation.error(f"{stock_id}: statusはokまたはstaleにしてください")
        if not price.get("marketTime"):
            validation.error(f"{stock_id}: marketTimeがありません")


def validate_signals(payload: dict[str, Any], stocks: dict[str, dict[str, Any]], validation: Validation) -> None:
    if payload.get("method") != SIGNAL_METHOD:
        validation.error(f"data/signals.json: methodは{SIGNAL_METHOD}である必要があります")
    signals = payload.get("signals")
    if not isinstance(signals, dict):
        validation.error("data/signals.json: signalsはobjectである必要があります")
        return
    unknown_ids = set(signals) - set(stocks)
    if unknown_ids:
        validation.error(f"data/signals.json: 未登録の銘柄IDがあります: {sorted(unknown_ids)}")

    for stock_id, signal in signals.items():
        if not isinstance(signal, dict):
            validation.error(f"{stock_id}: signalがobjectではありません")
            continue
        position = signal.get("position")
        if not is_number(position) or not 0 <= position <= 100:
            validation.error(f"{stock_id}: positionは0～100の数値が必要です")
            continue
        zone = signal.get("zone")
        if zone not in ALLOWED_ZONES:
            validation.error(f"{stock_id}: zoneが不正です: {zone}")
        elif zone != expected_zone(float(position)):
            validation.error(f"{stock_id}: positionとzoneが一致しません")
        as_of = signal.get("asOf")
        if not isinstance(as_of, str) or not DATE_PATTERN.fullmatch(as_of):
            validation.error(f"{stock_id}: asOfはYYYY-MM-DD形式が必要です")
        else:
            try:
                date.fromisoformat(as_of)
            except ValueError:
                validation.error(f"{stock_id}: asOfが実在する日付ではありません")

        components = signal.get("components")
        component_keys = ("valuation", "catalysts", "businessRisk")
        if not isinstance(components, dict) or any(not is_number(components.get(key)) for key in component_keys):
            validation.error(f"{stock_id}: 3つのcomponents数値が必要です")
        else:
            values = [float(components[key]) for key in component_keys]
            if any(not 0 <= value <= 100 for value in values):
                validation.error(f"{stock_id}: componentsは0～100にしてください")
            calculated = round(values[0] * 0.60 + values[1] * 0.25 + values[2] * 0.15, 1)
            if abs(calculated - float(position)) > 0.11:
                validation.error(f"{stock_id}: 加重計算は{calculated}ですがpositionは{position}です")
        if not str(signal.get("reportRevision", "")).strip():
            validation.error(f"{stock_id}: reportRevisionがありません")
        if not str(signal.get("summary", "")).strip():
            validation.error(f"{stock_id}: summaryがありません")

        reports = stocks[stock_id].get("reports") or {}
        if any(not reports.get(key, {}).get("available") for key in REPORT_KEYS):
            validation.error(f"{stock_id}: 3レポート公開前にsignalを登録できません")


def validate_frontend(validation: Validation) -> None:
    for path in (ROOT / "index.html", ROOT / "assets" / "js" / "app.js", ROOT / "assets" / "css" / "styles.css"):
        if not path.is_file():
            validation.error(f"必須ファイルがありません: {path.relative_to(ROOT)}")
    try:
        app_source = (ROOT / "assets" / "js" / "app.js").read_text(encoding="utf-8")
    except OSError:
        return
    for required in ("data/stocks.json", "data/prices.json", "data/signals.json"):
        if required not in app_source:
            validation.error(f"assets/js/app.js: {required}を参照していません")


def main() -> int:
    validation = Validation()
    stocks_payload = load_json(DATA_DIR / "stocks.json", validation)
    prices_payload = load_json(DATA_DIR / "prices.json", validation)
    signals_payload = load_json(DATA_DIR / "signals.json", validation)
    stocks, _ = validate_stocks(stocks_payload, validation)
    validate_prices(prices_payload, stocks, validation)
    validate_signals(signals_payload, stocks, validation)
    validate_frontend(validation)

    for warning in validation.warnings:
        print(f"WARN: {warning}")
    for error in validation.errors:
        print(f"ERROR: {error}", file=sys.stderr)
    print(f"Validation complete: {len(validation.errors)} error(s), {len(validation.warnings)} warning(s)")
    return 1 if validation.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
