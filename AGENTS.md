# SiM MARKET LAB repository guidance

## Purpose

This repository contains the public SiM MARKET LAB static website and its stock-report data pipeline.

## Durable rules

- Keep the site deployable as a static GitHub Pages project.
- Do not add frameworks or build dependencies unless the user explicitly approves them.
- Keep stock metadata in `data/stocks.json` and dynamic quotes in `data/prices.json`.
- Keep report-derived market signals in `data/signals.json`. Do not calculate them from technical indicators or daily price changes.
- Follow `docs/signal-methodology.md` exactly when creating or updating a signal.
- Do not publish a signal until all three reports are complete and their required evidence passes validation.
- Never place API keys, tokens, passwords, or private data in tracked files.
- Use UTF-8 and preserve Japanese text.
- Every stock must use a stable lowercase `id` and a provider-specific `quoteSymbol`.
- The three report pages are independent. Do not add navigation from one report to another.
- Every report page must contain a direct link to `../../index.html`; do not implement history-based back navigation.
- Reports 2 and 3 may show the shared current quote, but live quotes must not silently recalculate report conclusions or historical valuation assumptions.
- A report button becomes active only when its file exists and its `available` value is `true`.
- If quote retrieval fails, preserve the last valid quote and mark it stale.
- Daily quote updates must never change the report-derived signal.
- Treat all displayed market data as informational and show its timestamp.

## Verification

- Run `python scripts/validate_site.py`; publishing must stop if it reports an error.
- Parse every changed JSON file.
- Run `python scripts/update_prices.py` when network access is available.
- Test search, market filters, sorting, card/list switching, and mobile layout.
- Check that enabled report links exist and disabled report links cannot be opened.
