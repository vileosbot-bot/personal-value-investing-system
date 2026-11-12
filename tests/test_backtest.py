import unittest

from pvis.backtest import (
    DistributionEvent,
    evaluate_replay,
    freeze_phase_a,
    total_shareholder_return,
)


class BacktestTests(unittest.TestCase):
    def test_dividend_reinvestment_and_share_split(self) -> None:
        result = total_shareholder_return(
            100.0,
            40.0,
            5.0,
            [
                DistributionEvent(10.0, 100.0),
                DistributionEvent(0.0, 0.0, 3.0),
            ],
        )
        self.assertAlmostEqual(result.ending_shares, 3.3)
        self.assertAlmostEqual(result.terminal_value, 132.0)

    def test_frozen_phase_a_rejects_tampering(self) -> None:
        frozen = freeze_phase_a(
            "2021-08-30", {"predicted_annualized_return": 0.10}
        )
        frozen.payload["predicted_annualized_return"] = 0.20
        with self.assertRaises(ValueError):
            frozen.validate()

    def test_replay_separates_forecast_and_outcome(self) -> None:
        frozen = freeze_phase_a(
            "2021-08-30", {"predicted_annualized_return": 0.10}
        )
        result = evaluate_replay(
            frozen,
            0.02,
            benchmark_annualized_return=0.03,
        )
        self.assertAlmostEqual(result.forecast_error, -0.08)
        self.assertAlmostEqual(result.excess_return or 0.0, -0.01)
        self.assertTrue(result.threshold_classification_consistent)


if __name__ == "__main__":
    unittest.main()
