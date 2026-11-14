#!/usr/bin/env python3
"""Monte Carlo calibration for the Phase 0 HH+t3 monitoring stop rule.

This is an analysis-only reproduction script. It does not import or modify
frozen valuation-model code. The reported calibration table is unconditional:
non-evaluable repetitions count as non-triggers in the denominator.

Random-number specification: NumPy Generator(PCG64), seed 20261114. For each
scenario, the same simulated innovations are shifted by each candidate mu
(common random numbers), matching the stated calibration design.
"""

from __future__ import annotations

import math
import numpy as np

N = 20
L = 4
WINDOW = L + 1
REPETITIONS = 200_000
SEED = 20261114
ANNUAL_INCREMENT_VARIANCE = 2_000.0  # pp^2
THRESHOLD_PP = -3.0
T_CRIT = 3.182446  # t_(3, 0.975), first evaluable look
MU_GRID = (-3.0, 0.0, -20.0, -30.0)
THRESHOLD_GRID = (-2.0, -3.0, -5.0)
CORRECTION_FACTOR = 1.0 - (2 * L + 1) / N


def rolling_five_year_means(increments: np.ndarray) -> np.ndarray:
    """Return N consecutive five-year rolling means from N+4 increments."""
    if increments.ndim != 2 or increments.shape[1] != N + L:
        raise ValueError(f"expected shape (repetitions, {N + L})")
    windows = np.lib.stride_tricks.sliding_window_view(
        increments, window_shape=WINDOW, axis=1
    )
    return windows.mean(axis=-1)


def hh_variance_of_mean(delta: np.ndarray, lag: int = L) -> tuple[np.ndarray, np.ndarray]:
    """De-meaned HH equal-weight lag-1..lag estimate for Var(mean(delta)).

    Missing calendar years are not compressed. A repetition is non-evaluable
    if any lag has no valid pair, any delta is non-finite, or the raw variance
    estimate is non-positive.
    """
    n = delta.shape[1]
    finite = np.isfinite(delta)
    all_finite = finite.all(axis=1)
    safe_delta = np.where(finite, delta, 0.0)
    counts = finite.sum(axis=1)
    means = np.divide(
        safe_delta.sum(axis=1),
        counts,
        out=np.zeros(delta.shape[0], dtype=float),
        where=counts > 0,
    )
    residuals = safe_delta - means[:, None]

    numerator = np.sum(np.where(finite, residuals * residuals, 0.0), axis=1)
    has_pairs_for_every_lag = np.ones(delta.shape[0], dtype=bool)
    for ell in range(1, lag + 1):
        pair_mask = finite[:, :-ell] & finite[:, ell:]
        pair_count = pair_mask.sum(axis=1)
        has_pairs_for_every_lag &= pair_count > 0
        cross_products = residuals[:, :-ell] * residuals[:, ell:]
        numerator += 2.0 * np.sum(np.where(pair_mask, cross_products, 0.0), axis=1)

    raw_variance = numerator / (n * n)
    evaluable = all_finite & has_pairs_for_every_lag & np.isfinite(raw_variance) & (raw_variance > 0.0)
    return raw_variance, evaluable


def rates_for_mu(
    mean_noise: np.ndarray,
    raw_variance: np.ndarray,
    evaluable: np.ndarray,
    mu: float,
    critical_value: float = T_CRIT,
    threshold: float = THRESHOLD_PP,
    corrected: bool = True,
) -> tuple[float, float]:
    """Return unconditional and evaluable-only trigger rates."""
    factor = CORRECTION_FACTOR if corrected else 1.0
    se = np.sqrt(np.maximum(raw_variance, 0.0) / factor)
    trigger = evaluable & ((mean_noise + mu + critical_value * se) < threshold)
    unconditional = float(trigger.mean())
    conditional = float(trigger.sum() / evaluable.sum()) if evaluable.any() else math.nan
    return unconditional, conditional


def iid_calibration() -> None:
    rng = np.random.Generator(np.random.PCG64(SEED))
    increments_noise = rng.normal(
        loc=0.0,
        scale=math.sqrt(ANNUAL_INCREMENT_VARIANCE),
        size=(REPETITIONS, N + L),
    )
    delta_noise = rolling_five_year_means(increments_noise)
    raw_variance, evaluable = hh_variance_of_mean(delta_noise)
    mean_noise = delta_noise.mean(axis=1)

    print("BASELINE IID MA(4)")
    print(f"N={N}; L={L}; annual increments={N + L}; repetitions={REPETITIONS}; seed={SEED}")
    print(f"annual increment variance={ANNUAL_INCREMENT_VARIANCE:.0f} pp^2; Var(Delta)=400 pp^2")
    print(f"planning Var(mean)=100 pp^2; planning SE=10 pp; correction factor={CORRECTION_FACTOR:.2f}")
    print(f"P(non-evaluable)={1.0 - evaluable.mean():.4%}; median corrected SE={np.median(np.sqrt(raw_variance[evaluable] / CORRECTION_FACTOR)):.4f} pp")

    print("mu_pp | unconditional | evaluable_only")
    for mu in MU_GRID:
        unconditional, conditional = rates_for_mu(mean_noise, raw_variance, evaluable, mu)
        print(f"{mu:>6.1f} | {unconditional * 100:>8.2f}% | {conditional * 100:>8.2f}%")

    print("threshold sensitivity: rows=mu; columns=threshold -2/-3/-5 pp")
    for mu in (-3.0, 0.0, -30.0):
        row = []
        for threshold in THRESHOLD_GRID:
            unconditional, _ = rates_for_mu(
                mean_noise, raw_variance, evaluable, mu, threshold=threshold
            )
            row.append(unconditional * 100)
        print(f"mu={mu:>5.1f}: " + " / ".join(f"{x:.2f}%" for x in row))
        print(
            f"  span={max(row) - min(row):.2f} pp; relative to -3pp threshold: "
            f"{row[0] - row[1]:+.2f} / {row[2] - row[1]:+.2f} pp"
        )

    # Selection effect from dropping non-positive raw HH variance estimates.
    uncorrected_unconditional, uncorrected_conditional = rates_for_mu(
        mean_noise, raw_variance, evaluable, -3.0, corrected=False
    )
    print(
        "uncorrected HH, mu=-3pp: evaluable-only="
        f"{uncorrected_conditional * 100:.2f}%; unconditional="
        f"{uncorrected_unconditional * 100:.2f}%"
    )

    # Empirical critical value c* for uncorrected HH at a 2.5% conditional rate.
    se_raw = np.sqrt(raw_variance[evaluable])
    standardized = mean_noise[evaluable] / se_raw
    c_star = -float(np.quantile(standardized, 0.025))
    asymptotic_check = T_CRIT / math.sqrt(CORRECTION_FACTOR)
    print(f"empirical c*={c_star:.4f}; t3/sqrt(0.55)={asymptotic_check:.3f}")


def ar1_sensitivity() -> None:
    rho = 0.9
    persistent_variance = 0.25 * ANNUAL_INCREMENT_VARIANCE
    white_variance = 0.75 * ANNUAL_INCREMENT_VARIANCE
    innovation_variance = persistent_variance * (1.0 - rho * rho)

    rng = np.random.Generator(np.random.PCG64(SEED))
    white_noise = rng.normal(
        loc=0.0,
        scale=math.sqrt(white_variance),
        size=(REPETITIONS, N + L),
    )
    persistent = np.empty((REPETITIONS, N + L), dtype=float)
    persistent[:, 0] = rng.normal(
        loc=0.0, scale=math.sqrt(persistent_variance), size=REPETITIONS
    )
    innovation_scale = math.sqrt(innovation_variance)
    for t in range(1, N + L):
        persistent[:, t] = (
            rho * persistent[:, t - 1]
            + rng.normal(loc=0.0, scale=innovation_scale, size=REPETITIONS)
        )

    increments_noise = white_noise + persistent
    delta_noise = rolling_five_year_means(increments_noise)
    raw_variance, evaluable = hh_variance_of_mean(delta_noise)
    mean_noise = delta_noise.mean(axis=1)

    print("AR(1) PERSISTENT-COMPONENT SENSITIVITY")
    print(
        f"rho={rho:.1f}; persistent share={persistent_variance / ANNUAL_INCREMENT_VARIANCE:.0%}; "
        f"total annual variance={ANNUAL_INCREMENT_VARIANCE:.0f} pp^2"
    )
    print(f"P(non-evaluable)={1.0 - evaluable.mean():.4%}")
    print("mu_pp | corrected unconditional | corrected evaluable_only")
    for mu in MU_GRID:
        unconditional, conditional = rates_for_mu(mean_noise, raw_variance, evaluable, mu)
        print(f"{mu:>6.1f} | {unconditional * 100:>8.2f}% | {conditional * 100:>8.2f}%")

    uncorrected_unconditional, _ = rates_for_mu(
        mean_noise, raw_variance, evaluable, -3.0, corrected=False
    )
    print(f"uncorrected HH, mu=-3pp: {uncorrected_unconditional * 100:.2f}%")


def main() -> None:
    if not np.isclose(CORRECTION_FACTOR, 0.55):
        raise RuntimeError("unexpected N=20, L=4 correction factor")
    iid_calibration()
    print()
    ar1_sensitivity()


if __name__ == "__main__":
    main()
