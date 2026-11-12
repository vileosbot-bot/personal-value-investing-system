"""历史时点复演与股东总回报重建。"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import isfinite
from typing import Any, Iterable


@dataclass(frozen=True)
class DistributionEvent:
    distribution_per_share: float
    reinvestment_price: float
    share_multiplier: float = 1.0

    def validate(self) -> None:
        values = (
            self.distribution_per_share,
            self.reinvestment_price,
            self.share_multiplier,
        )
        if not all(isfinite(value) for value in values):
            raise ValueError("公司行动输入必须是有限数")
        if self.distribution_per_share < 0:
            raise ValueError("每股分配不能为负数")
        if self.distribution_per_share > 0 and self.reinvestment_price <= 0:
            raise ValueError("发生分配时必须提供正的再投资价格")
        if self.share_multiplier <= 0:
            raise ValueError("股数乘数必须为正数")


@dataclass(frozen=True)
class TotalReturnResult:
    ending_shares: float
    terminal_value: float
    total_return: float
    annualized_return: float


@dataclass(frozen=True)
class FrozenPhaseA:
    decision_at: str
    payload: dict[str, Any]
    content_hash: str

    def validate(self) -> None:
        if canonical_hash(self.payload) != self.content_hash:
            raise ValueError("A 区冻结内容已被修改")


@dataclass(frozen=True)
class ReplayEvaluation:
    predicted_annualized_return: float
    actual_annualized_return: float
    forecast_error: float
    benchmark_annualized_return: float | None
    excess_return: float | None
    threshold_classification_consistent: bool


def canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def freeze_phase_a(decision_at: str, payload: dict[str, Any]) -> FrozenPhaseA:
    if not decision_at:
        raise ValueError("决策时点不能为空")
    frozen_payload = json.loads(json.dumps(payload, ensure_ascii=False))
    return FrozenPhaseA(
        decision_at=decision_at,
        payload=frozen_payload,
        content_hash=canonical_hash(frozen_payload),
    )


def reinvested_share_count(
    events: Iterable[DistributionEvent], *, initial_shares: float = 1.0
) -> float:
    if initial_shares <= 0:
        raise ValueError("初始股数必须为正数")
    shares = initial_shares
    for event in events:
        event.validate()
        if event.distribution_per_share > 0:
            shares *= 1.0 + event.distribution_per_share / event.reinvestment_price
        shares *= event.share_multiplier
    return shares


def total_shareholder_return(
    start_price: float,
    end_price: float,
    years: float,
    events: Iterable[DistributionEvent],
) -> TotalReturnResult:
    if start_price <= 0 or end_price <= 0 or years <= 0:
        raise ValueError("起止价格和持有年数必须为正数")
    ending_shares = reinvested_share_count(events)
    terminal_value = end_price * ending_shares
    total_return = terminal_value / start_price - 1.0
    annualized_return = (1.0 + total_return) ** (1.0 / years) - 1.0
    return TotalReturnResult(
        ending_shares=ending_shares,
        terminal_value=terminal_value,
        total_return=total_return,
        annualized_return=annualized_return,
    )


def evaluate_replay(
    frozen_phase_a: FrozenPhaseA,
    actual_annualized_return: float,
    *,
    benchmark_annualized_return: float | None = None,
    threshold: float = 0.15,
) -> ReplayEvaluation:
    frozen_phase_a.validate()
    predicted = float(frozen_phase_a.payload["predicted_annualized_return"])
    excess = (
        None
        if benchmark_annualized_return is None
        else actual_annualized_return - benchmark_annualized_return
    )
    return ReplayEvaluation(
        predicted_annualized_return=predicted,
        actual_annualized_return=actual_annualized_return,
        forecast_error=actual_annualized_return - predicted,
        benchmark_annualized_return=benchmark_annualized_return,
        excess_return=excess,
        threshold_classification_consistent=(predicted >= threshold)
        == (actual_annualized_return >= threshold),
    )
