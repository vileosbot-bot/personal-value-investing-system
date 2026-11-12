"""个人价值投资系统的确定性计算内核。"""

from .evidence import EvidenceRecord, is_point_in_time_eligible
from .finance import irr, max_drawdown, target_entry_price
from .scenario import Scenario, analyze_scenarios
from .valuation import (
    five_year_return_profile,
    growth_dcf,
    residual_income_model,
    value_driver_fcff,
)

__all__ = [
    "EvidenceRecord",
    "Scenario",
    "analyze_scenarios",
    "five_year_return_profile",
    "growth_dcf",
    "irr",
    "is_point_in_time_eligible",
    "max_drawdown",
    "residual_income_model",
    "target_entry_price",
    "value_driver_fcff",
]

__version__ = "0.2.0"
