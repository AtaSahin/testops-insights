from .flaky_detection import detect_flaky_tests
from .frequent_failures import get_frequent_failures
from .health_score import calculate_health_score
from .slow_tests import get_slowest_tests
from .trends import get_last_failed_timestamp, get_last_test_status, get_pass_rate_trend

__all__ = [
    "detect_flaky_tests",
    "get_frequent_failures",
    "calculate_health_score",
    "get_slowest_tests",
    "get_pass_rate_trend",
    "get_last_test_status",
    "get_last_failed_timestamp",
]

