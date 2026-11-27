#!/usr/bin/env python3
"""Pure-Python validator for SiM MARKET LAB report_bundle.json.

This validator checks rules that JSON Schema alone cannot express: arithmetic,
references, date order, probability sums, dependency cycles and cross-report
consistency. It has no third-party dependency.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set

from importlib.util import module_from_spec, spec_from_file_location


HERE = Path(__file__).resolve().parent
CALC_PATH = HERE / "10_calculation_reference.py"
SPEC = spec_from_file_location("sim_calculations", CALC_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load calculation reference: {CALC_PATH}")
calc = module_from_spec(SPEC)
SPEC.loader.exec_module(calc)

QUANTIFICATION_METHODS = {
    "ENTERPRISE_VALUE_DELTA",
    "CONDITIONAL_SCENARIO",
    "CONSENSUS_REVISION",
    "SAME_COMPANY_EVENT_STUDY",
    "PEER_EVENT_STUDY",
}


@dataclass
class Issue:
    id: str
    status: str
    path: str
    message: str


class Validator:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data
        self.issues: List[Issue] = []

    def fail(self, check_id: str, path: str, message: str) -> None:
        self.issues.append(Issue(check_id, "FAIL", path, message))

    def warn(self, check_id: str, path: str, message: str) -> None:
        self.issues.append(Issue(check_id, "WARN", path, message))

    @staticmethod
    def close(actual: float, expected: float, rel: float = 1e-6, abs_: float = 1e-6) -> bool:
        return math.isclose(float(actual), float(expected), rel_tol=rel, abs_tol=abs_)

    @staticmethod
    def parse_date(value: Optional[str]) -> Optional[date]:
        if value is None:
            return None
        return date.fromisoformat(value[:10])

    def require_top_level(self) -> None:
        required = {"meta", "capital_structure", "claims", "sources", "guide", "scenario", "catalyst_report", "validation_summary"}
        missing = sorted(required - set(self.data))
        for key in missing:
            self.fail("S01", "$", f"必須項目 {key} がありません")
        allowed = required
        for key in sorted(set(self.data) - allowed):
            self.fail("S02", f"$.{key}", "未定義の最上位項目です")

    def validate_meta_and_capital(self) -> None:
        meta = self.data.get("meta", {})
        cap = self.data.get("capital_structure", {})
        for key in ("company_name", "ticker", "exchange", "currency", "valuation_date", "price", "price_as_of"):
            if meta.get(key) in (None, ""):
                self.fail("X01", f"$.meta.{key}", "対象と評価基準の必須値がありません")
        if meta.get("framework_version") != "6.2" or meta.get("schema_version") != "1.2":
            self.fail("S03", "$.meta", "framework_version=6.2、schema_version=1.2が必要です")
        try:
            self.parse_date(meta.get("valuation_date"))
        except Exception:
            self.fail("X02", "$.meta.valuation_date", "YYYY-MM-DD形式の日付ではありません")
        try:
            price = float(meta["price"])
            diluted = float(cap["diluted_shares"])
            basic = float(cap["basic_shares"])
            stated_market_cap = float(cap["market_cap"])
            if price <= 0 or diluted <= 0 or basic <= 0:
                raise ValueError
            if diluted + 1e-9 < basic:
                self.fail("X10", "$.capital_structure.diluted_shares", "希薄化後株式数が基本株式数を下回っています")
            expected = calc.market_cap(price, diluted)
            if not self.close(stated_market_cap, expected):
                self.fail("X02", "$.capital_structure.market_cap", f"時価総額が price×diluted_shares と一致しません（期待値 {expected}）")
        except (KeyError, TypeError, ValueError):
            self.fail("X02", "$.capital_structure", "株価・株式数・時価総額は正の数で必要です")
        self.validate_runway(cap)

    def validate_runway(self, cap: Dict[str, Any]) -> None:
        fields = ("cash", "liquid_securities", "restricted_cash", "minimum_operating_cash", "ttm_operating_cash_flow", "ttm_capex")
        values = [cap.get(x) for x in fields]
        stated = cap.get("runway_months")
        if any(v is None for v in values):
            if stated is not None:
                self.warn("X23", "$.capital_structure.runway_months", "資金余力の基礎値が不足しているため再計算できません")
            return
        try:
            expected = calc.runway_months(
                cap["cash"], cap["liquid_securities"], cap["restricted_cash"],
                cap["minimum_operating_cash"], cap["ttm_operating_cash_flow"],
                cap["ttm_capex"], cap.get("burn_one_off_adjustments") or 0.0,
            )
            if expected is None and stated is not None:
                self.fail("X23", "$.capital_structure.runway_months", "キャッシュバーンがない計算なのにrunwayが数値です")
            if expected is not None and (stated is None or not self.close(stated, expected)):
                self.fail("X23", "$.capital_structure.runway_months", f"資金余力月数が式と一致しません（期待値 {expected}）")
        except (TypeError, ValueError):
            self.fail("X23", "$.capital_structure", "資金余力の入力が不正です")

    @staticmethod
    def duplicate_ids(items: Sequence[Dict[str, Any]]) -> Set[str]:
        seen: Set[str] = set()
        duplicates: Set[str] = set()
        for item in items:
            value = item.get("id")
            if value in seen:
                duplicates.add(value)
            seen.add(value)
        return duplicates

    def validate_sources_and_claims(self) -> None:
        sources = self.data.get("sources", [])
        claims = self.data.get("claims", [])
        source_ids = {x.get("id") for x in sources if x.get("id")}
        claim_ids = {x.get("id") for x in claims if x.get("id")}
        for dup in self.duplicate_ids(sources):
            self.fail("X06", "$.sources", f"source ID {dup} が重複しています")
        for dup in self.duplicate_ids(claims):
            self.fail("X06", "$.claims", f"claim ID {dup} が重複しています")
        for i, source in enumerate(sources):
            url = source.get("url", "")
            if not isinstance(url, str) or not url.startswith("https://"):
                self.fail("X06", f"$.sources[{i}].url", "出典URLはhttps://が必要です")
            for claim_id in source.get("supports_claim_ids", []):
                if claim_id not in claim_ids:
                    self.fail("X06", f"$.sources[{i}].supports_claim_ids", f"存在しないclaim ID: {claim_id}")
        for i, claim in enumerate(claims):
            classification = claim.get("classification")
            refs = claim.get("source_ids", [])
            for source_id in refs:
                if source_id not in source_ids:
                    self.fail("X06", f"$.claims[{i}].source_ids", f"存在しないsource ID: {source_id}")
            if classification in {"CONFIRMED", "COMPANY_GUIDANCE", "CONSENSUS"} and not refs:
                self.fail("X05", f"$.claims[{i}]", f"{classification}には出典が必要です")
            if classification == "MODEL_ESTIMATE" and not claim.get("calculation_id"):
                self.fail("X05", f"$.claims[{i}].calculation_id", "当方推定にはcalculation_idが必要です")
            if classification == "UNKNOWN" and claim.get("calculation_id"):
                self.warn("X05", f"$.claims[{i}]", "UNKNOWNに計算IDが設定されています")
        guide = self.data.get("guide", {})
        for source_id in guide.get("source_ids", []):
            if source_id not in source_ids:
                self.fail("X22", "$.guide.source_ids", f"存在しないsource ID: {source_id}")
        for section, refs in guide.get("section_claim_ids", {}).items():
            for claim_id in refs:
                if claim_id not in claim_ids:
                    self.fail("X22", f"$.guide.section_claim_ids.{section}", f"存在しないclaim ID: {claim_id}")

    def validate_scenario(self) -> None:
        meta = self.data.get("meta", {})
        scenario = self.data.get("scenario", {})
        cases = scenario.get("cases", [])
        if len(cases) != 3:
            self.fail("X08", "$.scenario.cases", "3シナリオが必要です")
            return
        by_label = {x.get("label"): x for x in cases}
        if set(by_label) != {"BEAR", "BASE", "BULL"}:
            self.fail("X09", "$.scenario.cases", "BEAR / BASE / BULLが1件ずつ必要です")
            return
        bear, base, bull = (by_label[x] for x in ("BEAR", "BASE", "BULL"))
        try:
            probabilities = [float(x["probability"]) for x in (bear, base, bull)]
            if any(p < 0 or p > 1 for p in probabilities) or not self.close(sum(probabilities), 1.0, abs_=1e-8):
                self.fail("X08", "$.scenario.cases[*].probability", "3シナリオの確率合計が100%ではありません")
            for label, case in by_label.items():
                expected_case_price = calc.price_from_equity(case["equity_value"], case["diluted_shares"])
                if not self.close(case["price"], expected_case_price):
                    self.fail("X07", f"$.scenario.cases[{label}].price", f"equity_value÷diluted_sharesと一致しません（期待値 {expected_case_price}）")
            prices = [float(x["price"]) for x in (bear, base, bull)]
            if not prices[0] < prices[1] < prices[2]:
                self.fail("X09", "$.scenario.cases[*].price", "原則 Pbear < Pbase < Pbull が必要です")
            expected_price = calc.expected_price(prices, probabilities)
            current = float(meta["price"])
            expected_delta = calc.pct_change(expected_price, current)
            raw_band, display_band = calc.band_position(current, prices[0], prices[2])
            rr = calc.endpoint_rr(current, prices[0], prices[2])
            mscore = calc.market_score(current, prices[0], prices[2])
            oscore = calc.own_score(expected_price, prices[0], prices[2])
            sscore = calc.supplemental_score(current, expected_price, prices[0], probabilities[0])
            computed = scenario.get("computed", {})
            expected_values = {
                "expected_price": expected_price,
                "expected_delta_pct": expected_delta,
                "raw_band_position_pct": raw_band,
                "display_band_position_pct": display_band,
                "market_score": mscore,
                "own_score": oscore,
                "supplemental_score": sscore,
            }
            for key, expected in expected_values.items():
                if key not in computed or not self.close(computed[key], expected, abs_=1e-6):
                    self.fail("X07", f"$.scenario.computed.{key}", f"参照式と一致しません（期待値 {expected}）")
            stated_rr = computed.get("endpoint_rr")
            if rr is None and stated_rr is not None:
                self.fail("X07", "$.scenario.computed.endpoint_rr", "現値がシナリオ帯外のためN/Aが必要です")
            elif rr is not None and (stated_rr is None or not self.close(stated_rr, rr)):
                self.fail("X07", "$.scenario.computed.endpoint_rr", f"上値下値比が一致しません（期待値 {rr}）")
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
            self.fail("X07", "$.scenario", f"シナリオ計算を再現できません: {exc}")
        sensitivity = scenario.get("sensitivity", [])
        if len(sensitivity) < 2:
            self.fail("X07", "$.scenario.sensitivity", "感応度は最低2変数必要です")
        if scenario.get("distribution_method") == "MONTE_CARLO":
            mc = scenario.get("monte_carlo") or {}
            if int(mc.get("trials", 0)) < 10000 or mc.get("seed") is None:
                self.fail("X07", "$.scenario.monte_carlo", "モンテカルロは10,000回以上と固定seedが必要です")

    @staticmethod
    def validate_range(value: Any) -> bool:
        return (isinstance(value, list) and len(value) == 2
                and all(isinstance(x, (int, float)) and math.isfinite(float(x)) for x in value)
                and value[0] <= value[1])

    @staticmethod
    def has_specific_explanation(value: Any) -> bool:
        if not isinstance(value, str):
            return False
        normalized = "".join(value.split())
        generic = {
            "数字では判断できない",
            "定性的評価",
            "不明",
            "算出不能",
            "数値化できない",
        }
        return len(normalized) >= 20 and normalized not in generic

    def validate_non_quantified_explanation(self, value: Any, path: str) -> None:
        if not isinstance(value, dict):
            self.fail("X13", path, "理由・不足情報・次に見る数字・再計算方法が必要です")
            return
        if not self.has_specific_explanation(value.get("reason")):
            self.fail("X13", f"{path}.reason", "数値を出さない具体的な理由が必要です")
        for key, label in (("missing_information", "足りない情報"), ("next_checks", "次に見る数字")):
            items = value.get(key)
            if not isinstance(items, list) or not items or not all(isinstance(x, str) and len("".join(x.split())) >= 5 for x in items):
                self.fail("X13", f"{path}.{key}", f"具体的な{label}が1件以上必要です")
        method = value.get("recalculation_method")
        if not isinstance(method, str) or len("".join(method.split())) < 15:
            self.fail("X13", f"{path}.recalculation_method", "情報が判明した後の再計算方法が必要です")

    def validate_quantification_attempts(self, value: Any, path: str, quantifiable: bool) -> None:
        if not isinstance(value, list):
            self.fail("X13", path, "数値化手法5種類の検討記録が必要です")
            return
        methods = [item.get("method") for item in value if isinstance(item, dict)]
        if len(value) != 5 or len(methods) != 5 or set(methods) != QUANTIFICATION_METHODS:
            self.fail("X13", path, "企業価値差分・条件付きシナリオ・コンセンサス改定・同社事例・同業事例を1回ずつ検討します")
        statuses = []
        for index, item in enumerate(value):
            item_path = f"{path}[{index}]"
            if not isinstance(item, dict):
                self.fail("X13", item_path, "検討記録はobjectで必要です")
                continue
            status = item.get("status")
            statuses.append(status)
            if status not in {"USED", "REJECTED", "NOT_APPLICABLE"}:
                self.fail("X13", f"{item_path}.status", "USED / REJECTED / NOT_APPLICABLEが必要です")
            reason = item.get("reason")
            if not isinstance(reason, str) or len("".join(reason.split())) < 10:
                self.fail("X13", f"{item_path}.reason", "採用・不採用・適用外の具体的理由が必要です")
        if quantifiable and "USED" not in statuses:
            self.fail("X13", path, "数値を表示する場合は採用した手法が最低1つ必要です")
        if not quantifiable and "USED" in statuses:
            self.fail("X13", path, "数値を表示しない結果でUSEDは設定できません")

    def validate_priced_in(self, priced: Dict[str, Any], path: str, current_equity: float) -> None:
        quantifiable = priced.get("quantifiable")
        if not quantifiable:
            if priced.get("percent_range") is not None or priced.get("raw_implied_pct") is not None:
                self.fail("X13", path, "定量不能なのに織り込み数値があります")
            caveats = priced.get("caveats", [])
            if not any(self.has_specific_explanation(item) for item in caveats):
                self.fail("X13", f"{path}.caveats", "割合を出さない具体的な理由が必要です")
            self.validate_non_quantified_explanation(priced.get("non_quantified_explanation"), f"{path}.non_quantified_explanation")
            return
        if priced.get("non_quantified_explanation") is not None:
            self.fail("X13", f"{path}.non_quantified_explanation", "数値を表示する場合はnullにします")
        percent_range = priced.get("percent_range")
        if not self.validate_range(percent_range) or percent_range[0] < 0 or percent_range[1] > 100:
            self.fail("X14", f"{path}.percent_range", "表示レンジは0～100で下限<=上限が必要です")
        method = priced.get("method")
        if method == "EQUITY_VALUE":
            try:
                expected = calc.priced_in_pct(
                    current_equity,
                    priced["event_excluded_equity_value"],
                    priced["full_success_incremental_equity_value"],
                )
                if not self.close(priced.get("raw_implied_pct"), expected):
                    self.fail("X15", f"{path}.raw_implied_pct", f"企業価値方式の計算と一致しません（期待値 {expected}）")
                if (expected < 0 or expected > 100) and not priced.get("caveats"):
                    self.fail("X16", f"{path}.caveats", "rawが0～100%外の理由が必要です")
            except (KeyError, TypeError, ValueError) as exc:
                self.fail("X15", path, f"織り込み度を再計算できません: {exc}")
        elif method not in {"BINARY_REVERSE"}:
            self.fail("X15", f"{path}.method", "定量値にはEQUITY_VALUEまたはBINARY_REVERSEが必要です")

    def validate_catalysts(self) -> None:
        meta = self.data.get("meta", {})
        cap = self.data.get("capital_structure", {})
        report = self.data.get("catalyst_report", {})
        catalysts = report.get("catalysts", [])
        source_ids = {x.get("id") for x in self.data.get("sources", [])}
        claim_ids = {x.get("id") for x in self.data.get("claims", [])}
        catalyst_ids = {x.get("id") for x in catalysts if x.get("id")}
        if len(catalyst_ids) != len(catalysts):
            self.fail("X06", "$.catalyst_report.catalysts", "カタリストIDの欠落または重複があります")
        try:
            valuation_date = self.parse_date(meta.get("valuation_date"))
            current_equity = calc.market_cap(meta["price"], cap["diluted_shares"])
        except Exception:
            valuation_date = None
            current_equity = float("nan")
        group_ids = {x.get("id") for x in report.get("dependency_groups", []) if x.get("id")}
        for i, catalyst in enumerate(catalysts):
            path = f"$.catalyst_report.catalysts[{i}]"
            date_window = catalyst.get("date", {})
            try:
                start = self.parse_date(date_window.get("start_date"))
                end = self.parse_date(date_window.get("end_date"))
                if start and end and start > end:
                    self.fail("X11", f"{path}.date", "start_dateがend_dateより後です")
                if valuation_date and end and end < valuation_date and catalyst.get("status") != "ONGOING":
                    self.fail("X11", f"{path}.date", "評価基準日より前に完了したイベントが今後一覧にあります")
            except ValueError:
                self.fail("X11", f"{path}.date", "日付形式が不正です")
            for source_id in catalyst.get("source_ids", []) + date_window.get("source_ids", []):
                if source_id not in source_ids:
                    self.fail("X06", path, f"存在しないsource ID: {source_id}")
            for claim_id in catalyst.get("claim_ids", []):
                if claim_id not in claim_ids:
                    self.fail("X06", path, f"存在しないclaim ID: {claim_id}")
            for dependency in catalyst.get("dependencies", []):
                if dependency not in catalyst_ids:
                    self.fail("X17", f"{path}.dependencies", f"存在しない依存ID: {dependency}")
                if dependency == catalyst.get("id"):
                    self.fail("X17", f"{path}.dependencies", "自己依存は禁止です")
            group_id = catalyst.get("dependency_group_id")
            if group_id is not None and group_id not in group_ids:
                self.fail("X17", f"{path}.dependency_group_id", f"存在しないgroup ID: {group_id}")
            outcomes = catalyst.get("outcomes", [])
            labels = [x.get("label") for x in outcomes]
            if catalyst.get("importance", 0) >= 3 and sorted(labels) != sorted(["SUCCESS", "INLINE", "FAILURE"]):
                self.fail("X12", f"{path}.outcomes", "重要度3以上は3結果が1件ずつ必要です")
            probs = [x.get("probability") for x in outcomes]
            if any(x is not None for x in probs):
                if not all(isinstance(x, (int, float)) for x in probs) or not self.close(sum(probs), 1.0, abs_=1e-8):
                    self.fail("X08", f"{path}.outcomes[*].probability", "結果確率は3つすべて表示し合計100%にします")
            for j, outcome in enumerate(outcomes):
                opath = f"{path}.outcomes[{j}]"
                quant = outcome.get("quantifiable")
                price_range = outcome.get("price_range")
                pct_range = outcome.get("price_change_pct_range")
                direction = outcome.get("direction")
                self.validate_quantification_attempts(outcome.get("quantification_attempts"), f"{opath}.quantification_attempts", bool(quant))
                if direction not in {"UP", "FLAT", "DOWN", "MIXED", "UNKNOWN"}:
                    self.fail("X13", f"{opath}.direction", "結果の方向表示が必要です")
                if not quant:
                    if price_range is not None or pct_range is not None:
                        self.fail("X13", opath, "定量不能なのに価格レンジがあります")
                    if not self.has_specific_explanation(outcome.get("method_note")):
                        self.fail("X13", f"{opath}.method_note", "数値を出さない具体的な理由が必要です")
                    self.validate_non_quantified_explanation(outcome.get("non_quantified_explanation"), f"{opath}.non_quantified_explanation")
                else:
                    if outcome.get("non_quantified_explanation") is not None:
                        self.fail("X13", f"{opath}.non_quantified_explanation", "数値を表示する場合はnullにします")
                    if not self.validate_range(price_range) or not self.validate_range(pct_range):
                        self.fail("X14", opath, "定量結果には順序が正しい2端点レンジが必要です")
                    else:
                        expected_pct = [calc.pct_change(x, meta["price"]) for x in price_range]
                        if not all(self.close(a, b, abs_=1e-5) for a, b in zip(pct_range, expected_pct)):
                            self.fail("X13", opath, f"価格レンジと変化率が不一致です（期待値 {expected_pct}）")
            if math.isfinite(current_equity):
                self.validate_priced_in(catalyst.get("priced_in", {}), f"{path}.priced_in", current_equity)
        self.validate_dependency_graph(catalysts)
        self.validate_groups(report, catalyst_ids)
        self.validate_overall_priced_in(report, current_equity)
        for key in ("next_catalyst_id",):
            ref = report.get(key)
            if ref is not None and ref not in catalyst_ids:
                self.fail("X18", f"$.catalyst_report.{key}", f"存在しないカタリストID: {ref}")
        major = self.data.get("scenario", {}).get("major_catalyst_id")
        next_id = report.get("next_catalyst_id")
        if major != next_id:
            self.fail("X18", "$.scenario.major_catalyst_id", "シナリオとカタリストの主要材料IDが一致しません")
        for i, item in enumerate(report.get("watch_items", [])):
            for ref in item.get("catalyst_ids", []):
                if ref not in catalyst_ids:
                    self.fail("X06", f"$.catalyst_report.watch_items[{i}]", f"存在しないカタリストID: {ref}")

    def validate_dependency_graph(self, catalysts: Sequence[Dict[str, Any]]) -> None:
        graph = {x.get("id"): list(x.get("dependencies", [])) for x in catalysts}
        visiting: Set[str] = set()
        visited: Set[str] = set()

        def visit(node: str) -> None:
            if node in visiting:
                self.fail("X17", "$.catalyst_report.catalysts", f"依存関係が循環しています: {node}")
                return
            if node in visited:
                return
            visiting.add(node)
            for parent in graph.get(node, []):
                if parent in graph:
                    visit(parent)
            visiting.remove(node)
            visited.add(node)

        for node in graph:
            visit(node)

    def validate_groups(self, report: Dict[str, Any], catalyst_ids: Set[str]) -> None:
        groups = report.get("dependency_groups", [])
        if len({x.get("id") for x in groups}) != len(groups):
            self.fail("X17", "$.catalyst_report.dependency_groups", "group IDの欠落または重複があります")
        catalyst_map = {x.get("id"): x for x in report.get("catalysts", [])}
        for i, group in enumerate(groups):
            path = f"$.catalyst_report.dependency_groups[{i}]"
            members = group.get("catalyst_ids", [])
            for member in members:
                if member not in catalyst_ids:
                    self.fail("X17", path, f"存在しないカタリストID: {member}")
                elif catalyst_map[member].get("dependency_group_id") != group.get("id"):
                    self.fail("X17", path, f"{member}側のdependency_group_idと不一致です")
            if group.get("relationship_type") in {"CHAIN", "SHARED_VALUE"} and group.get("full_success_incremental_equity_value") is None:
                self.warn("X15", path, "価値を定量表示するならグループ単位の成功増分価値が必要です")

    def validate_overall_priced_in(self, report: Dict[str, Any], current_equity: float) -> None:
        overall = report.get("overall_priced_in", {})
        path = "$.catalyst_report.overall_priced_in"
        if not overall.get("quantifiable"):
            if overall.get("percent_range") is not None or overall.get("raw_implied_pct") is not None:
                self.fail("X15", path, "全体が定量不能なのに数値があります")
            if not self.has_specific_explanation(overall.get("method_note")):
                self.fail("X15", f"{path}.method_note", "全体割合を出さない具体的な理由が必要です")
            self.validate_non_quantified_explanation(overall.get("non_quantified_explanation"), f"{path}.non_quantified_explanation")
            return
        if overall.get("non_quantified_explanation") is not None:
            self.fail("X15", f"{path}.non_quantified_explanation", "数値を表示する場合はnullにします")
        groups = {x.get("id"): x for x in report.get("dependency_groups", [])}
        included = overall.get("included_group_ids", [])
        try:
            increments = []
            for group_id in included:
                if group_id not in groups:
                    raise ValueError(f"存在しないgroup ID: {group_id}")
                value = groups[group_id].get("full_success_incremental_equity_value")
                if value is None or value <= 0:
                    raise ValueError(f"{group_id}の成功増分価値がありません")
                increments.append(value)
            if not increments:
                raise ValueError("included_group_idsが空です")
            expected = calc.priced_in_pct(current_equity, overall["all_events_excluded_equity_value"], sum(increments))
            if not self.close(overall.get("raw_implied_pct"), expected):
                self.fail("X15", f"{path}.raw_implied_pct", f"全体織り込み度が価値合計方式と一致しません（期待値 {expected}）")
            if not self.validate_range(overall.get("percent_range")):
                self.fail("X14", f"{path}.percent_range", "表示レンジが不正です")
        except (KeyError, TypeError, ValueError) as exc:
            self.fail("X15", path, f"全体織り込み度を再計算できません: {exc}")

    def validate_validation_summary(self) -> None:
        summary = self.data.get("validation_summary", {})
        status = summary.get("status")
        fail_count = summary.get("fail_count", 0)
        warn_count = summary.get("warn_count", 0)
        if status == "PASS" and (fail_count != 0 or warn_count != 0):
            self.fail("X28", "$.validation_summary", "PASSはfail=0かつwarn=0が必要です")
        if status == "WARN" and (fail_count != 0 or warn_count < 1):
            self.fail("X28", "$.validation_summary", "WARNはfail=0かつwarn>=1が必要です")
        if status == "FAIL" and fail_count < 1:
            self.fail("X28", "$.validation_summary", "FAILはfail>=1が必要です")

    def run(self) -> Dict[str, Any]:
        self.require_top_level()
        if any(x.status == "FAIL" for x in self.issues):
            return self.result()
        self.validate_meta_and_capital()
        self.validate_sources_and_claims()
        self.validate_scenario()
        self.validate_catalysts()
        self.validate_validation_summary()
        return self.result()

    def result(self) -> Dict[str, Any]:
        fails = sum(x.status == "FAIL" for x in self.issues)
        warns = sum(x.status == "WARN" for x in self.issues)
        status = "FAIL" if fails else "WARN" if warns else "PASS"
        return {
            "status": status,
            "fail_count": fails,
            "warn_count": warns,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "checks": [asdict(x) for x in self.issues],
        }


PUBLIC_ENUMS = re.compile(r"\b(HIGH|MEDIUM|LOW|SUCCESS|INLINE|FAILURE|CONFIRMED|COMPANY_GUIDANCE|CONSENSUS|MODEL_ESTIMATE|UNKNOWN|CATALYST_RICH|EXPECTATIONS_HIGH)\b")
PLACEHOLDER = re.compile(r"\{\{[A-Z0-9_]+\}\}")
DANGEROUS_URL = re.compile(r"javascript\s*:", re.IGNORECASE)
INLINE_EVENT = re.compile(r"\son[a-z]+\s*=", re.IGNORECASE)


def validate_html(paths: Sequence[Path]) -> List[Issue]:
    issues: List[Issue] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        placeholders = sorted(set(PLACEHOLDER.findall(text)))
        if placeholders:
            issues.append(Issue("X25", "FAIL", str(path), f"未置換placeholder: {', '.join(placeholders[:8])}"))
        if DANGEROUS_URL.search(text) or INLINE_EVENT.search(text):
            issues.append(Issue("X26", "FAIL", str(path), "危険URLまたはinline event属性があります"))
        enums = sorted(set(PUBLIC_ENUMS.findall(text)))
        if enums:
            issues.append(Issue("X31", "FAIL", str(path), f"読者向けに未変換の英語分類: {', '.join(enums)}"))
        if "@media(max-width:520px)" not in text.replace(" ", "") and "@media(max-width:480px)" not in text.replace(" ", ""):
            issues.append(Issue("X32", "WARN", str(path), "スマホ専用CSSを確認できません"))
    return issues


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate SiM report_bundle.json")
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--html", type=Path, nargs="*", default=[])
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.bundle.read_text(encoding="utf-8"))
    except Exception as exc:
        result = {"status": "FAIL", "fail_count": 1, "warn_count": 0, "checks": [{"id": "S00", "status": "FAIL", "path": str(args.bundle), "message": f"JSONを読めません: {exc}"}]}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1
    result = Validator(data).run()
    html_issues = validate_html(args.html)
    if html_issues:
        result["checks"].extend(asdict(x) for x in html_issues)
        result["fail_count"] += sum(x.status == "FAIL" for x in html_issues)
        result["warn_count"] += sum(x.status == "WARN" for x in html_issues)
        result["status"] = "FAIL" if result["fail_count"] else "WARN"
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
