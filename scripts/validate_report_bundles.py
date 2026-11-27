"""Validate published reports, their shared evidence bundles and signal alignment.

Standard-library checks run alongside validate_site.py in CI. Independent full JSON
Schema validation can use report_support/report_bundle.schema.json when available.
"""
from __future__ import annotations

import json
import math
from datetime import date, datetime
from pathlib import Path
from typing import Any

from report_support.bundle_validator import Validator, validate_html

ROOT = Path(__file__).resolve().parents[1]


def check_bundle(bundle: dict[str, Any], stock: dict[str, Any], signal: dict[str, Any] | None,
                 html_paths: list[Path]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    stock_id = stock['id']
    result = Validator(bundle).run()
    for item in result['checks']:
        target = errors if item['status'] == 'FAIL' else warnings
        target.append(f"{stock_id}: {item['id']} {item['path']}: {item['message']}")
    for item in validate_html(html_paths):
        target = errors if item.status == 'FAIL' else warnings
        target.append(f'{stock_id}: {item.id}: {item.message}')
    meta = bundle.get('meta', {})
    for key, expected in [('ticker', stock['ticker']), ('currency', stock['currency'])]:
        if meta.get(key) != expected:
            errors.append(f'{stock_id}: bundle {key} does not match stocks.json')
    try:
        basis = date.fromisoformat(meta['valuation_date'])
        cutoff = datetime.fromisoformat(meta['source_cutoff'].replace('Z', '+00:00'))
        price_time = datetime.fromisoformat(meta['price_as_of'].replace('Z', '+00:00'))
        if cutoff.tzinfo is None or price_time.tzinfo is None:
            raise ValueError('source_cutoff/price_as_of require timezone')
        if price_time > cutoff:
            errors.append(f'{stock_id}: price timestamp is after the information cutoff')
        if price_time.date() > basis:
            errors.append(f'{stock_id}: price timestamp is after valuation date')
        for source in bundle.get('sources', []):
            accessed = datetime.fromisoformat(source['accessed_at'].replace('Z', '+00:00'))
            if accessed.tzinfo is None:
                raise ValueError('source accessed_at requires timezone')
            if source.get('published_at') and date.fromisoformat(source['published_at'][:10]) > basis:
                errors.append(f"{stock_id}: source {source['id']} was published after valuation date")
    except (KeyError, TypeError, ValueError) as exc:
        errors.append(f'{stock_id}: invalid date/cutoff: {exc}')
    if signal is not None and signal.get('asOf') != meta.get('valuation_date'):
        errors.append(f'{stock_id}: signal analysis date and bundle valuation date differ')
    if stock.get('reportAsOf') and stock['reportAsOf'] != meta.get('valuation_date'):
        errors.append(f'{stock_id}: stock reportAsOf and bundle valuation date differ')
    if signal is not None and stock.get('reportRevision') and stock['reportRevision'] != signal.get('reportRevision'):
        errors.append(f'{stock_id}: stock and signal report revisions differ')
    required = ('company_name', 'ticker', 'exchange', 'currency', 'valuation_date', 'price_as_of')
    if any(not meta.get(key) for key in required):
        errors.append(f'{stock_id}: incomplete company identity or analysis basis')
    for case in bundle.get('scenario', {}).get('cases', []):
        for key in ('price', 'equity_value', 'diluted_shares', 'probability'):
            value = case.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                errors.append(f'{stock_id}: non-finite {key} in {case.get("label")}')
    overall = bundle.get('catalyst_report', {}).get('overall_priced_in', {})
    if overall.get('quantifiable') and isinstance(overall.get('all_events_excluded_equity_value'), (int, float)) and overall['all_events_excluded_equity_value'] < 0:
        errors.append(f'{stock_id}: negative common-equity failure endpoint must be floored at zero or left unquantified')
    claims = bundle.get('claims', [])
    if not any(item.get('classification') == 'MODEL_ESTIMATE' for item in claims):
        errors.append(f'{stock_id}: valuation has no disclosed model-estimate claims')
    if not any(item.get('is_primary') for item in bundle.get('sources', [])):
        errors.append(f'{stock_id}: no primary evidence source')
    if not bundle.get('guide', {}).get('section_claim_ids'):
        errors.append(f'{stock_id}: guide sections have no evidence mapping')
    return errors, warnings


def validate_report_bundles(root: Path = ROOT) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warnings: list[str] = []
    checked = 0
    stocks = json.loads((root/'data/stocks.json').read_text(encoding='utf-8'))['stocks']
    signals = json.loads((root/'data/signals.json').read_text(encoding='utf-8'))['signals']
    for stock in stocks:
        if not any(report.get('available') for report in stock.get('reports', {}).values()):
            continue
        path = root/'data/reports'/f"{stock['id']}.json"
        if not path.is_file():
            errors.append(f"{stock['id']}: published reports require {path.relative_to(root)}")
            continue
        paths = [root/report['path'].removeprefix('./') for report in stock['reports'].values()
                 if report.get('available')]
        if not all(page.is_file() for page in paths):
            errors.append(f"{stock['id']}: published HTML is missing")
            continue
        try:
            bundle = json.loads(path.read_text(encoding='utf-8'))
            failures, notices = check_bundle(bundle, stock, signals.get(stock['id']), paths)
            errors.extend(failures)
            warnings.extend(notices)
            checked += 1
        except (OSError, ValueError, TypeError, KeyError) as exc:
            errors.append(f"{stock['id']}: bundle validation could not finish: {exc}")
    return errors, warnings, checked


if __name__ == '__main__':
    errors, warnings, checked = validate_report_bundles()
    for message in warnings:
        print('WARN:', message)
    for message in errors:
        print('ERROR:', message)
    print(f'Report bundles checked: {checked}; {len(errors)} error(s), {len(warnings)} warning(s)')
    raise SystemExit(bool(errors))
