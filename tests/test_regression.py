from pathlib import Path
import unittest

from pvis.regression import run_model_regressions, run_replay_regressions


ROOT = Path(__file__).resolve().parents[1]


class RegressionTests(unittest.TestCase):
    def test_v1_1_model_workbook_regression(self) -> None:
        result = run_model_regressions(
            ROOT / "examples" / "regression" / "v1_1_models.json"
        )
        self.assertTrue(result["passed"], result)
        self.assertEqual(len(result["cases"]), 4)

    def test_v1_0_historical_replay_regression(self) -> None:
        result = run_replay_regressions(
            ROOT / "examples" / "regression" / "historical_replay_v1_0.json"
        )
        self.assertTrue(result["passed"], result)
        self.assertEqual(len(result["cases"]), 4)


if __name__ == "__main__":
    unittest.main()
