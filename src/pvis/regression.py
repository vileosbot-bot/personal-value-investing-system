"""冻结参考夹具的模型与历史复演回归入口。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .backtest import (
    DistributionEvent,
    evaluate_replay,
    freeze_phase_a,
    total_shareholder_return,
)
from .valuation import (
    five_year_return_profile,
    growth_dcf,
    residual_income_model,
    value_driver_fcff,
)


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("回归夹具顶层必须是对象")
    return value


def _check(actual: float, expected: float, tolerance: float) -> dict[str, Any]:
    difference = actual - expected
    return {
        "actual": actual,
        "expected": expected,
        "difference": difference,
        "passed": abs(difference) <= tolerance,
    }


def run_model_regressions(path: Path, *, tolerance: float = 1e-8) -> dict[str, Any]:
    fixture = _read_json(path)
    rows: list[dict[str, Any]] = []
    for case in fixture["cases"]:
        route = case["route"]
        inputs = case["inputs"]
        expected = case["expected"]
        if route in {"owner_earnings_dcf", "dcf_sotp"}:
            projection = growth_dcf(
                inputs["starting_cash_flow"],
                inputs["initial_growth"],
                inputs["discount_rate"],
                inputs["perpetual_growth"],
                non_operating_value=inputs.get("non_operating_value", 0.0),
            )
            returns = five_year_return_profile(
                inputs["entry_price"],
                tuple(projection.cash_flows[:5]),
                projection.year_five_exit_value,
            )
            actual = {
                "intrinsic_value": projection.intrinsic_value
                * inputs.get("output_fx", 1.0),
                "five_year_irr": returns.five_year_irr,
                "target_entry_price": returns.target_entry_price
                * inputs.get("output_fx", 1.0),
            }
        elif route == "value_driver_fcff":
            projection = value_driver_fcff(
                inputs["starting_nopat"],
                inputs["shares"],
                inputs["initial_growth"],
                inputs["initial_ronic"],
                inputs["discount_rate"],
                inputs["perpetual_growth"],
                net_debt=inputs.get("net_debt", 0.0),
            )
            returns = five_year_return_profile(
                inputs["entry_price"],
                tuple(projection.fcff_per_share[:5]),
                projection.year_five_exit_value_per_share,
            )
            actual = {
                "intrinsic_value": projection.intrinsic_value_per_share,
                "five_year_irr": returns.five_year_irr,
                "target_entry_price": returns.target_entry_price,
            }
        elif route == "residual_income":
            projection = residual_income_model(
                inputs["beginning_book_value_per_share"],
                inputs["payout_ratio"],
                inputs["initial_roe"],
                inputs["year_five_roe"],
                inputs["cost_of_equity"],
            )
            returns = five_year_return_profile(
                inputs["entry_price"],
                tuple(projection.dividends_per_share[:5]),
                projection.year_five_exit_value_per_share,
            )
            actual = {
                "intrinsic_value": projection.intrinsic_value_per_share,
                "five_year_irr": returns.five_year_irr,
                "target_entry_price": returns.target_entry_price,
            }
        else:
            raise ValueError(f"未知模型路由：{route}")

        checks = {
            key: _check(actual[key], float(expected[key]), tolerance)
            for key in expected
        }
        rows.append(
            {
                "name": case["name"],
                "route": route,
                "passed": all(item["passed"] for item in checks.values()),
                "checks": checks,
            }
        )
    return {
        "suite": fixture["suite"],
        "passed": all(row["passed"] for row in rows),
        "cases": rows,
    }


def run_replay_regressions(path: Path, *, tolerance: float = 1e-10) -> dict[str, Any]:
    fixture = _read_json(path)
    rows: list[dict[str, Any]] = []
    for case in fixture["cases"]:
        events = [DistributionEvent(**item) for item in case["events"]]
        total_return = total_shareholder_return(
            case["start_price"],
            case["end_price"],
            case.get("years", fixture["years"]),
            events,
        )
        frozen = freeze_phase_a(
            fixture["decision_at"],
            {
                "name": case["name"],
                "predicted_annualized_return": case[
                    "predicted_annualized_return"
                ],
            },
        )
        evaluation = evaluate_replay(
            frozen,
            total_return.annualized_return,
            benchmark_annualized_return=case["benchmark_annualized_return"],
        )
        check = _check(
            total_return.annualized_return,
            case["expected_actual_annualized_return"],
            tolerance,
        )
        rows.append(
            {
                "name": case["name"],
                "passed": check["passed"],
                "actual_return_check": check,
                "forecast_error": evaluation.forecast_error,
                "excess_return": evaluation.excess_return,
                "threshold_classification_consistent": (
                    evaluation.threshold_classification_consistent
                ),
            }
        )
    return {
        "suite": fixture["suite"],
        "passed": all(row["passed"] for row in rows),
        "cases": rows,
    }
