"""命令行入口。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .regression import run_model_regressions, run_replay_regressions
from .scenario import Scenario, analyze_scenarios


def _load_case(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("案例文件顶层必须是对象")
    return value


def _scenario_from_dict(value: dict[str, Any]) -> Scenario:
    return Scenario(
        name=str(value["name"]),
        probability=float(value["probability"]),
        annual_distributions=tuple(float(item) for item in value["annual_distributions"]),
        exit_value=float(value["exit_value"]),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="个人价值投资系统计算内核")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze = subparsers.add_parser("analyze", help="分析一个固定输入的三情景案例")
    analyze.add_argument("case", type=Path, help="案例 JSON 路径")
    regression = subparsers.add_parser("regression", help="运行冻结基线回归")
    regression.add_argument(
        "--models",
        type=Path,
        default=Path("examples/regression/v1_1_models.json"),
        help="V1.1 模型回归夹具路径",
    )
    regression.add_argument(
        "--replay",
        type=Path,
        default=Path("examples/regression/historical_replay_v1_0.json"),
        help="历史复演 V1.0 回归夹具路径",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "analyze":
        case = _load_case(args.case)
        result = analyze_scenarios(
            entry_price=float(case["entry_price"]),
            scenarios=[_scenario_from_dict(item) for item in case["scenarios"]],
            target_rate=float(case.get("target_rate", 0.15)),
        )
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "regression":
        result = {
            "models": run_model_regressions(args.models),
            "historical_replay": run_replay_regressions(args.replay),
        }
        result["passed"] = all(item["passed"] for item in result.values())
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result["passed"] else 1
    raise AssertionError("未知命令")
