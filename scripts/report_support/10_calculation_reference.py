"""SiM MARKET LAB v6.2 calculation reference.

All functions use unrounded inputs. Round only for display.
"""

from __future__ import annotations

import math
from typing import Iterable, Optional, Sequence, Tuple


TOLERANCE = 1e-9


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def clamp(value: float, low: float, high: float) -> float:
    value = _finite(value, "value")
    if low > high:
        raise ValueError("low must not exceed high")
    return min(high, max(low, value))


def pct_change(new_value: float, base_value: float) -> float:
    new_value = _finite(new_value, "new_value")
    base_value = _finite(base_value, "base_value")
    if base_value <= 0:
        raise ValueError("base_value must be positive")
    return (new_value / base_value - 1.0) * 100.0


def market_cap(price: float, diluted_shares: float) -> float:
    price = _finite(price, "price")
    diluted_shares = _finite(diluted_shares, "diluted_shares")
    if price <= 0 or diluted_shares <= 0:
        raise ValueError("price and diluted_shares must be positive")
    return price * diluted_shares


def price_from_equity(equity_value: float, diluted_shares: float) -> float:
    equity_value = _finite(equity_value, "equity_value")
    diluted_shares = _finite(diluted_shares, "diluted_shares")
    if diluted_shares <= 0:
        raise ValueError("diluted_shares must be positive")
    return equity_value / diluted_shares


def expected_price(prices: Sequence[float], probabilities: Sequence[float]) -> float:
    if len(prices) != 3 or len(probabilities) != 3:
        raise ValueError("exactly three prices and probabilities are required")
    ps = [_finite(p, "probability") for p in probabilities]
    if any(p < 0 or p > 1 for p in ps):
        raise ValueError("probabilities must be between 0 and 1")
    if not math.isclose(sum(ps), 1.0, abs_tol=1e-8):
        raise ValueError("probabilities must sum to 1")
    xs = [_finite(x, "price") for x in prices]
    if any(x <= 0 for x in xs):
        raise ValueError("prices must be positive")
    return sum(x * p for x, p in zip(xs, ps))


def band_position(current: float, bear: float, bull: float) -> Tuple[float, float]:
    current = _finite(current, "current")
    bear = _finite(bear, "bear")
    bull = _finite(bull, "bull")
    if bull <= bear:
        raise ValueError("bull must exceed bear")
    raw = (current - bear) / (bull - bear) * 100.0
    return raw, clamp(raw, 0.0, 100.0)


def endpoint_rr(current: float, bear: float, bull: float) -> Optional[float]:
    current = _finite(current, "current")
    bear = _finite(bear, "bear")
    bull = _finite(bull, "bull")
    if not bear < current < bull:
        return None
    return (bull - current) / (current - bear)


def market_score(current: float, bear: float, bull: float) -> int:
    raw, _ = band_position(current, bear, bull)
    return round(clamp(raw, 0.0, 100.0))


def own_score(expected: float, bear: float, bull: float) -> int:
    expected = _finite(expected, "expected")
    bear = _finite(bear, "bear")
    bull = _finite(bull, "bull")
    if bull <= bear:
        raise ValueError("bull must exceed bear")
    raw = (expected - bear) / (bull - bear) * 100.0
    return round(clamp(raw, 0.0, 100.0))


def supplemental_score(current: float, expected: float, bear: float, bear_probability: float) -> int:
    expected_return = pct_change(expected, current)
    bear_downside = max(0.0, (current - bear) / current * 100.0)
    raw = 50.0 + expected_return - _finite(bear_probability, "bear_probability") * bear_downside
    return round(clamp(raw, 0.0, 100.0))


def post_financing_price(
    pre_equity_value: float,
    gross_proceeds: float,
    issuance_costs: float,
    operating_value_change: float,
    pre_shares: float,
    new_shares: float,
) -> float:
    equity = (_finite(pre_equity_value, "pre_equity_value")
              + _finite(gross_proceeds, "gross_proceeds")
              - _finite(issuance_costs, "issuance_costs")
              + _finite(operating_value_change, "operating_value_change"))
    shares = _finite(pre_shares, "pre_shares") + _finite(new_shares, "new_shares")
    return price_from_equity(equity, shares)


def event_impact_price(
    current_price: float,
    current_diluted_shares: float,
    operating_value_change: float,
    net_cash_change: float,
    other_equity_change: float,
    post_event_diluted_shares: float,
) -> Tuple[float, float]:
    current_equity = market_cap(current_price, current_diluted_shares)
    post_equity = (current_equity + _finite(operating_value_change, "operating_value_change")
                   + _finite(net_cash_change, "net_cash_change")
                   + _finite(other_equity_change, "other_equity_change"))
    post_price = price_from_equity(post_equity, post_event_diluted_shares)
    return post_price, pct_change(post_price, current_price)


def priced_in_pct(current_equity: float, event_excluded_equity: float, full_success_increment: float) -> float:
    current_equity = _finite(current_equity, "current_equity")
    event_excluded_equity = _finite(event_excluded_equity, "event_excluded_equity")
    full_success_increment = _finite(full_success_increment, "full_success_increment")
    if full_success_increment <= 0:
        raise ValueError("full_success_increment must be positive")
    return (current_equity - event_excluded_equity) / full_success_increment * 100.0


def implied_binary_probability(current_equity: float, failure_equity: float, success_equity: float) -> float:
    current_equity = _finite(current_equity, "current_equity")
    failure_equity = _finite(failure_equity, "failure_equity")
    success_equity = _finite(success_equity, "success_equity")
    if success_equity <= failure_equity:
        raise ValueError("success_equity must exceed failure_equity")
    return (current_equity - failure_equity) / (success_equity - failure_equity)


def interval_ratio(numerator_range: Sequence[float], positive_denominator_range: Sequence[float]) -> Tuple[float, float]:
    if len(numerator_range) != 2 or len(positive_denominator_range) != 2:
        raise ValueError("ranges must contain exactly two endpoints")
    n0, n1 = map(float, numerator_range)
    d0, d1 = map(float, positive_denominator_range)
    if n0 > n1 or d0 > d1 or d0 <= 0:
        raise ValueError("ranges must be ordered and denominator must be positive")
    values = (n0 / d0, n0 / d1, n1 / d0, n1 / d1)
    return min(values), max(values)


def runway_months(
    unrestricted_cash: float,
    liquid_securities: float,
    restricted_cash: float,
    minimum_operating_cash: float,
    ttm_operating_cash_flow: float,
    ttm_capex: float,
    one_off_adjustments: float = 0.0,
) -> Optional[float]:
    available = (_finite(unrestricted_cash, "unrestricted_cash")
                 + _finite(liquid_securities, "liquid_securities")
                 - _finite(restricted_cash, "restricted_cash")
                 - _finite(minimum_operating_cash, "minimum_operating_cash"))
    annual_fcf = (_finite(ttm_operating_cash_flow, "ttm_operating_cash_flow")
                  - _finite(ttm_capex, "ttm_capex")
                  - _finite(one_off_adjustments, "one_off_adjustments"))
    monthly_burn = max(0.0, -annual_fcf / 12.0)
    if monthly_burn <= TOLERANCE:
        return None
    return max(0.0, available) / monthly_burn
