"""Update current and previous-close prices for stocks in data/stocks.json."""

from __future__ import annotations

import json
import math
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
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(update_prices())
