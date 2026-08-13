"""Update current and previous-close prices for stocks in data/stocks.json."""

from __future__ import annotations

import json
import math
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
STOCKS_PATH = ROOT / "data" / "stocks.json"
PRICES_PATH = ROOT / "data" / "prices.json"
SIGNALS_PATH = ROOT / "data" / "signals.json"
SOURCE_NAME = "Yahoo Finance chart endpoint (provisional)"


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def finite_number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def fetch_chart(symbol: str) -> dict[str, Any]:
    encoded = quote(symbol, safe="")
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}?range=3mo&interval=1d&events=div%2Csplits"
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; SiM-Market-Lab/1.0)",
            "Accept": "application/json",
        },
    )
    with urlopen(request, timeout=25) as response:
        return json.load(response)


def parse_quote(stock: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    chart = payload.get("chart") or {}
    if chart.get("error"):
        raise ValueError(str(chart["error"]))
    results = chart.get("result") or []
    if not results:
        raise ValueError("Yahoo Finance returned no chart result")

    result = results[0]
    meta = result.get("meta") or {}
    timestamps = result.get("timestamp") or []
    quote_rows = ((result.get("indicators") or {}).get("quote") or [{}])[0]
    raw_closes = quote_rows.get("close") or []
    close_points = [
        (timestamp, close)
        for timestamp, raw in zip(timestamps, raw_closes)
        if (close := finite_number(raw)) is not None
    ]
    if not close_points:
        raise ValueError("No valid closing prices were returned")

    closes = [close for _, close in close_points]
    market_price = finite_number(meta.get("regularMarketPrice")) or closes[-1]
    previous_close = closes[-2] if len(closes) >= 2 else finite_number(meta.get("chartPreviousClose"))
    change = None if previous_close in (None, 0) else market_price - previous_close
    change_pct = None if change is None else (change / previous_close) * 100
    market_timestamp = finite_number(meta.get("regularMarketTime")) or close_points[-1][0]
    market_time = datetime.fromtimestamp(market_timestamp, tz=timezone.utc).isoformat()

    return {
        "symbol": stock["quoteSymbol"],
        "price": round(market_price, 4),
        "previousClose": None if previous_close is None else round(previous_close, 4),
        "change": None if change is None else round(change, 4),
        "changePct": None if change_pct is None else round(change_pct, 4),
        "currency": stock["currency"],
        "marketTime": market_time,
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "ok",
    }


def parse_scenario_price(text: str) -> float | None:
    normalized = re.sub(r"[^\d.-]", "", text.replace(",", ""))
    return finite_number(normalized)


def scenario_bounds(stock: dict[str, Any]) -> tuple[float, float] | None:
    path = stock.get("reports", {}).get("valuation", {}).get("path")
    if not path:
        return None
    report_path = ROOT / path.removeprefix("./")
    if not report_path.exists():
        return None
    html = report_path.read_text(encoding="utf-8")
    match = re.search(r'<div class="position-labels">(.*?)</div>', html, flags=re.S)
    if not match:
        return None
    labels = re.findall(r"<span>(.*?)</span>", match.group(1), flags=re.S)
    if len(labels) < 3:
        return None
    bear = parse_scenario_price(re.sub(r"<.*?>", "", labels[0]))
    bull = parse_scenario_price(re.sub(r"<.*?>", "", labels[2]))
    if bear is None or bull is None or bear == bull:
        return None
    return bear, bull


def valuation_position(price: float, bear: float, bull: float) -> float:
    return max(0.0, min(100.0, (price - bear) / (bull - bear) * 100))


def update_signal_valuation(stocks: list[dict[str, Any]], prices: dict[str, Any]) -> None:
    if not SIGNALS_PATH.exists():
        return
    signals_payload = read_json(SIGNALS_PATH)
    signals = signals_payload.get("signals")
    if not isinstance(signals, dict):
        return

    changed = False
    for stock in stocks:
        stock_id = stock["id"]
        signal = signals.get(stock_id)
        price = finite_number(prices.get(stock_id, {}).get("price"))
        bounds = scenario_bounds(stock)
        if not isinstance(signal, dict) or price is None or bounds is None:
            continue
        bear, bull = bounds
        components = signal.setdefault("components", {})
        components["valuation"] = round(valuation_position(price, bear, bull), 1)
        catalysts = finite_number(components.get("catalysts"))
        business_risk = finite_number(components.get("businessRisk"))
        if catalysts is not None and business_risk is not None:
            signal["position"] = round(components["valuation"] * 0.60 + catalysts * 0.25 + business_risk * 0.15, 1)
        changed = True

    if changed:
        signals_payload["updatedAt"] = datetime.now(timezone.utc).isoformat()
        with SIGNALS_PATH.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(signals_payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")


def update_prices() -> int:
    stock_payload = read_json(STOCKS_PATH)
    existing_payload = read_json(PRICES_PATH) if PRICES_PATH.exists() else {}
    existing_prices = existing_payload.get("prices") or {}
    updated_prices: dict[str, Any] = {}
    errors: dict[str, str] = {}

    for index, stock in enumerate(stock_payload.get("stocks") or []):
        stock_id = stock["id"]
        try:
            updated_prices[stock_id] = parse_quote(stock, fetch_chart(stock["quoteSymbol"]))
            print(f"updated {stock['quoteSymbol']}")
        except (HTTPError, URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError) as error:
            errors[stock_id] = f"{type(error).__name__}: {error}"
            previous = existing_prices.get(stock_id)
            if previous:
                updated_prices[stock_id] = {
                    **previous,
                    "status": "stale",
                    "checkedAt": datetime.now(timezone.utc).isoformat(),
                }
            print(f"failed {stock.get('quoteSymbol', stock_id)}: {error}", file=sys.stderr)
        if index + 1 < len(stock_payload.get("stocks") or []):
            time.sleep(0.4)

    output = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": SOURCE_NAME,
        "quoteCount": sum(1 for item in updated_prices.values() if item.get("status") == "ok"),
        "errorCount": len(errors),
        "errors": errors,
        "prices": updated_prices,
    }
    with PRICES_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(output, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    update_signal_valuation(stock_payload.get("stocks") or [], updated_prices)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(update_prices())
