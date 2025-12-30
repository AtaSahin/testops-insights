from collections import defaultdict
from typing import NamedTuple

from testops_insight.domain.models import TestSuite


class TrendPoint(NamedTuple):
    run_index: int
    pass_rate: float
    avg_duration: float


def get_pass_rate_trend(test_suite: TestSuite) -> list[TrendPoint]:
    if len(test_suite.test_runs) == 0:
        return []

    trends = []
    for idx, test_run in enumerate(test_suite.test_runs):
        if test_run.total_tests == 0:
            pass_rate = 0.0
        else:
            pass_rate = (test_run.passed / test_run.total_tests) * 100.0

        if test_run.total_tests == 0:
            avg_duration = 0.0
        else:
            avg_duration = test_run.duration / test_run.total_tests

        trends.append(TrendPoint(run_index=idx, pass_rate=pass_rate, avg_duration=avg_duration))

    return trends


def get_last_test_status(test_suite: TestSuite, test_name: str) -> str:
    if len(test_suite.test_runs) == 0:
        return "UNKNOWN"

    for test_run in reversed(test_suite.test_runs):
        for test_case in test_run.test_cases:
            if test_case.full_name == test_name:
                return test_case.status.name

    return "NOT_FOUND"


def get_last_failed_timestamp(test_suite: TestSuite, test_name: str):
    if len(test_suite.test_runs) == 0:
        return None

    for test_run in reversed(test_suite.test_runs):
        for test_case in test_run.test_cases:
            if test_case.full_name == test_name and test_case.status.name in ("FAILED", "ERROR"):
                return test_run.timestamp

    return None

