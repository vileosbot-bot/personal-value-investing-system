import math
import unittest

from pvis.valuation import (
    bounded_bisection,
    fade_path,
    five_year_return_profile,
    gordon_terminal_value,
    growth_dcf,
    residual_income_model,
    solve_growth_dcf_rate,
    value_driver_fcff,
)


class ValuationTests(unittest.TestCase):
    def test_growth_fade_reaches_terminal_rate(self) -> None:
        path = fade_path(0.10, 0.03)
        self.assertEqual(path[:5], (0.10,) * 5)
        self.assertAlmostEqual(path[-1], 0.03)

    def test_terminal_requires_discount_rate_above_growth(self) -> None:
        with self.assertRaises(ValueError):
            gordon_terminal_value(100.0, 0.03, 0.03)

    def test_owner_earnings_baseline(self) -> None:
        projection = growth_dcf(63.0, 0.04, 0.09, 0.025)
        returns = five_year_return_profile(
            1297.4,
            projection.cash_flows[:5],
            projection.year_five_exit_value,
        )
        self.assertAlmostEqual(projection.intrinsic_value, 1081.6558558683628)
        self.assertAlmostEqual(returns.five_year_irr, 0.04678180959257583)

    def test_value_driver_baseline(self) -> None:
        projection = value_driver_fcff(
            38.0, 9.117197565, 0.10, 0.13, 0.095, 0.03
        )
        self.assertAlmostEqual(
            projection.intrinsic_value_per_share, 53.10901262585897
        )
        self.assertAlmostEqual(projection.reinvestment_rates[0], 0.10 / 0.13)

    def test_residual_income_baseline(self) -> None:
        projection = residual_income_model(45.4, 0.35, 0.13, 0.12, 0.10)
        self.assertAlmostEqual(
            projection.intrinsic_value_per_share, 51.89715398445987
        )
        self.assertAlmostEqual(projection.roe_rates[-1], 0.10)

    def test_bounded_solver_and_reverse_growth(self) -> None:
        direct = bounded_bisection(lambda value: value * value - 4.0, 0.0, 3.0)
        self.assertTrue(direct.converged)
        self.assertAlmostEqual(direct.value or 0.0, 2.0, places=8)

        reverse = solve_growth_dcf_rate(1297.4, 63.0, 0.09, 0.025)
        self.assertTrue(reverse.converged)
        self.assertTrue(math.isclose(reverse.value or 0.0, 0.0725, abs_tol=0.0013))


if __name__ == "__main__":
    unittest.main()
