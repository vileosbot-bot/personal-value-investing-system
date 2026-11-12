"""可审计、无外部依赖的估值模型原语。"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Callable

from .finance import irr, target_entry_price


@dataclass(frozen=True)
class DcfProjection:
    growth_rates: tuple[float, ...]
    cash_flows: tuple[float, ...]
    terminal_value: float
    pv_explicit_cash_flows: float
    pv_terminal_value: float
    operating_value: float
    non_operating_value: float
    intrinsic_value: float
    year_five_exit_value: float


@dataclass(frozen=True)
class ValueDriverProjection:
    growth_rates: tuple[float, ...]
    ronic_rates: tuple[float, ...]
    nopat: tuple[float, ...]
    reinvestment_rates: tuple[float, ...]
    fcff: tuple[float, ...]
    fcff_per_share: tuple[float, ...]
    terminal_value: float
    intrinsic_value_per_share: float
    year_five_exit_value_per_share: float


@dataclass(frozen=True)
class ResidualIncomeProjection:
    roe_rates: tuple[float, ...]
    beginning_book_values: tuple[float, ...]
    earnings_per_share: tuple[float, ...]
    dividends_per_share: tuple[float, ...]
    ending_book_values: tuple[float, ...]
    residual_income: tuple[float, ...]
    intrinsic_value_per_share: float
    year_five_exit_value_per_share: float


@dataclass(frozen=True)
class ReturnProfile:
    five_year_irr: float
    target_entry_price: float


@dataclass(frozen=True)
class SolveResult:
    value: float | None
    residual: float | None
    iterations: int
    converged: bool
    lower_bound: float
    upper_bound: float


def present_value(value: float, rate: float, periods: int) -> float:
    if periods < 0:
        raise ValueError("期间不能为负数")
    if rate <= -1.0:
        raise ValueError("折现率必须大于 -100%")
    return value / ((1.0 + rate) ** periods)


def gordon_terminal_value(
    next_cash_flow: float, discount_rate: float, perpetual_growth: float
) -> float:
    if discount_rate <= perpetual_growth:
        raise ValueError("终值折现率必须高于永续增长率")
    return next_cash_flow / (discount_rate - perpetual_growth)


def fade_path(
    initial: float,
    terminal: float,
    *,
    stable_years: int = 5,
    total_years: int = 10,
) -> tuple[float, ...]:
    """前段保持不变，后段逐年线性收敛到终值。"""

    if stable_years < 1 or total_years <= stable_years:
        raise ValueError("预测期必须包含稳定段和收敛段")
    steps = total_years - stable_years
    values = [initial] * stable_years
    values.extend(
        initial + (terminal - initial) * step / steps
        for step in range(1, steps + 1)
    )
    return tuple(values)


def growth_dcf(
    starting_cash_flow: float,
    initial_growth: float,
    discount_rate: float,
    perpetual_growth: float,
    *,
    non_operating_value: float = 0.0,
    stable_years: int = 5,
    total_years: int = 10,
) -> DcfProjection:
    """所有者收益或普通自由现金流的三阶段简化折现模型。"""

    inputs = (
        starting_cash_flow,
        initial_growth,
        discount_rate,
        perpetual_growth,
        non_operating_value,
    )
    if not all(isfinite(value) for value in inputs):
        raise ValueError("估值输入必须是有限数")
    if starting_cash_flow <= 0:
        raise ValueError("起始现金流必须为正数")
    if initial_growth <= -1.0 or perpetual_growth <= -1.0:
        raise ValueError("增长率必须大于 -100%")
    if discount_rate <= perpetual_growth:
        raise ValueError("折现率必须高于永续增长率")

    growth_rates = fade_path(
        initial_growth,
        perpetual_growth,
        stable_years=stable_years,
        total_years=total_years,
    )
    cash_flows: list[float] = []
    current = starting_cash_flow
    for growth in growth_rates:
        current *= 1.0 + growth
        cash_flows.append(current)

    terminal_value = gordon_terminal_value(
        cash_flows[-1] * (1.0 + perpetual_growth),
        discount_rate,
        perpetual_growth,
    )
    pv_explicit = sum(
        present_value(value, discount_rate, year)
        for year, value in enumerate(cash_flows, start=1)
    )
    pv_terminal = present_value(terminal_value, discount_rate, total_years)
    operating_value = pv_explicit + pv_terminal

    remaining_cash_flows = cash_flows[stable_years:]
    year_five_exit_value = non_operating_value + sum(
        present_value(value, discount_rate, year)
        for year, value in enumerate(remaining_cash_flows, start=1)
    ) + present_value(terminal_value, discount_rate, total_years - stable_years)

    return DcfProjection(
        growth_rates=growth_rates,
        cash_flows=tuple(cash_flows),
        terminal_value=terminal_value,
        pv_explicit_cash_flows=pv_explicit,
        pv_terminal_value=pv_terminal,
        operating_value=operating_value,
        non_operating_value=non_operating_value,
        intrinsic_value=operating_value + non_operating_value,
        year_five_exit_value=year_five_exit_value,
    )


def value_driver_fcff(
    starting_nopat: float,
    shares: float,
    initial_growth: float,
    initial_ronic: float,
    discount_rate: float,
    perpetual_growth: float,
    *,
    net_debt: float = 0.0,
    stable_years: int = 5,
    total_years: int = 10,
) -> ValueDriverProjection:
    """用增长、再投资率和新增资本回报率约束企业自由现金流。"""

    inputs = (
        starting_nopat,
        shares,
        initial_growth,
        initial_ronic,
        discount_rate,
        perpetual_growth,
        net_debt,
    )
    if not all(isfinite(value) for value in inputs):
        raise ValueError("估值输入必须是有限数")
    if starting_nopat <= 0 or shares <= 0:
        raise ValueError("起始税后经营利润和股数必须为正数")
    if initial_ronic <= 0 or discount_rate <= 0:
        raise ValueError("新增资本回报率和资本成本必须为正数")
    if discount_rate <= perpetual_growth:
        raise ValueError("资本成本必须高于永续增长率")

    growth_rates = fade_path(
        initial_growth,
        perpetual_growth,
        stable_years=stable_years,
        total_years=total_years,
    )
    ronic_rates = fade_path(
        initial_ronic,
        discount_rate,
        stable_years=stable_years,
        total_years=total_years,
    )

    nopat: list[float] = []
    reinvestment_rates: list[float] = []
    fcff: list[float] = []
    current_nopat = starting_nopat
    for growth, ronic in zip(growth_rates, ronic_rates, strict=True):
        if ronic <= 0:
            raise ValueError("预测期新增资本回报率必须为正数")
        current_nopat *= 1.0 + growth
        reinvestment_rate = growth / ronic
        current_fcff = current_nopat * (1.0 - reinvestment_rate)
        nopat.append(current_nopat)
        reinvestment_rates.append(reinvestment_rate)
        fcff.append(current_fcff)

    next_nopat = nopat[-1] * (1.0 + perpetual_growth)
    terminal_fcff = next_nopat * (1.0 - perpetual_growth / discount_rate)
    terminal_value = gordon_terminal_value(
        terminal_fcff, discount_rate, perpetual_growth
    )
    pv_explicit = sum(
        present_value(value, discount_rate, year)
        for year, value in enumerate(fcff, start=1)
    )
    equity_value = (
        pv_explicit
        + present_value(terminal_value, discount_rate, total_years)
        - net_debt
    )

    remaining_fcff = fcff[stable_years:]
    year_five_equity_value = (
        sum(
            present_value(value, discount_rate, year)
            for year, value in enumerate(remaining_fcff, start=1)
        )
        + present_value(
            terminal_value, discount_rate, total_years - stable_years
        )
        - net_debt
    )

    return ValueDriverProjection(
        growth_rates=growth_rates,
        ronic_rates=ronic_rates,
        nopat=tuple(nopat),
        reinvestment_rates=tuple(reinvestment_rates),
        fcff=tuple(fcff),
        fcff_per_share=tuple(value / shares for value in fcff),
        terminal_value=terminal_value,
        intrinsic_value_per_share=equity_value / shares,
        year_five_exit_value_per_share=year_five_equity_value / shares,
    )


def residual_income_model(
    beginning_book_value_per_share: float,
    payout_ratio: float,
    initial_roe: float,
    year_five_roe: float,
    cost_of_equity: float,
    *,
    stable_years: int = 5,
    total_years: int = 10,
) -> ResidualIncomeProjection:
    """银行等金融企业的剩余收益模型。"""

    inputs = (
        beginning_book_value_per_share,
        payout_ratio,
        initial_roe,
        year_five_roe,
        cost_of_equity,
    )
    if not all(isfinite(value) for value in inputs):
        raise ValueError("估值输入必须是有限数")
    if beginning_book_value_per_share <= 0 or cost_of_equity <= 0:
        raise ValueError("期初净资产和股东要求回报率必须为正数")
    if not 0.0 <= payout_ratio <= 1.0:
        raise ValueError("分红率必须在 0 到 1 之间")

    first_stage_steps = stable_years - 1
    first_stage = tuple(
        initial_roe
        + (year_five_roe - initial_roe) * step / first_stage_steps
        for step in range(stable_years)
    )
    second_stage_steps = total_years - stable_years
    second_stage = tuple(
        year_five_roe
        + (cost_of_equity - year_five_roe) * step / second_stage_steps
        for step in range(1, second_stage_steps + 1)
    )
    roe_rates = first_stage + second_stage

    beginning_values: list[float] = []
    earnings: list[float] = []
    dividends: list[float] = []
    ending_values: list[float] = []
    residual_income: list[float] = []
    current_book_value = beginning_book_value_per_share
    for roe in roe_rates:
        beginning_values.append(current_book_value)
        eps = current_book_value * roe
        dividend = eps * payout_ratio
        residual = (roe - cost_of_equity) * current_book_value
        current_book_value = current_book_value + eps - dividend
        earnings.append(eps)
        dividends.append(dividend)
        ending_values.append(current_book_value)
        residual_income.append(residual)

    intrinsic_value = beginning_book_value_per_share + sum(
        present_value(value, cost_of_equity, year)
        for year, value in enumerate(residual_income, start=1)
    )
    year_five_exit_value = ending_values[stable_years - 1] + sum(
        present_value(value, cost_of_equity, year)
        for year, value in enumerate(residual_income[stable_years:], start=1)
    )
    return ResidualIncomeProjection(
        roe_rates=roe_rates,
        beginning_book_values=tuple(beginning_values),
        earnings_per_share=tuple(earnings),
        dividends_per_share=tuple(dividends),
        ending_book_values=tuple(ending_values),
        residual_income=tuple(residual_income),
        intrinsic_value_per_share=intrinsic_value,
        year_five_exit_value_per_share=year_five_exit_value,
    )


def five_year_return_profile(
    entry_price: float,
    annual_distributions: tuple[float, ...],
    exit_value: float,
    *,
    target_rate: float = 0.15,
) -> ReturnProfile:
    if len(annual_distributions) != 5:
        raise ValueError("五年回报必须提供五个年度分配")
    cash_flows = [-entry_price, *annual_distributions]
    cash_flows[-1] += exit_value
    return ReturnProfile(
        five_year_irr=irr(cash_flows),
        target_entry_price=target_entry_price(
            annual_distributions, exit_value, target_rate
        ),
    )


def bounded_bisection(
    objective: Callable[[float], float],
    lower: float,
    upper: float,
    *,
    tolerance: float = 1e-10,
    max_iterations: int = 256,
) -> SolveResult:
    if lower >= upper:
        raise ValueError("求解下界必须低于上界")
    lower_value = objective(lower)
    upper_value = objective(upper)
    if not (isfinite(lower_value) and isfinite(upper_value)):
        raise ValueError("目标函数在边界处必须为有限数")
    if lower_value == 0:
        return SolveResult(lower, 0.0, 0, True, lower, upper)
    if upper_value == 0:
        return SolveResult(upper, 0.0, 0, True, lower, upper)
    if lower_value * upper_value > 0:
        return SolveResult(None, None, 0, False, lower, upper)

    lo, hi = lower, upper
    for iteration in range(1, max_iterations + 1):
        midpoint = (lo + hi) / 2.0
        midpoint_value = objective(midpoint)
        if not isfinite(midpoint_value):
            raise ValueError("目标函数在求解过程中出现非有限数")
        if abs(midpoint_value) <= tolerance or (hi - lo) / 2.0 <= tolerance:
            return SolveResult(
                midpoint,
                midpoint_value,
                iteration,
                True,
                lower,
                upper,
            )
        if lower_value * midpoint_value <= 0:
            hi = midpoint
        else:
            lo = midpoint
            lower_value = midpoint_value
    midpoint = (lo + hi) / 2.0
    return SolveResult(
        midpoint,
        objective(midpoint),
        max_iterations,
        False,
        lower,
        upper,
    )


def solve_growth_dcf_rate(
    target_value: float,
    starting_cash_flow: float,
    discount_rate: float,
    perpetual_growth: float,
    *,
    non_operating_value: float = 0.0,
    lower: float = -0.5,
    upper: float = 1.0,
) -> SolveResult:
    """反向估值：求使模型价值等于目标价格的前五年增长率。"""

    if target_value <= 0:
        raise ValueError("目标价值必须为正数")

    def objective(growth: float) -> float:
        return growth_dcf(
            starting_cash_flow,
            growth,
            discount_rate,
            perpetual_growth,
            non_operating_value=non_operating_value,
        ).intrinsic_value - target_value

    return bounded_bisection(objective, lower, upper)
