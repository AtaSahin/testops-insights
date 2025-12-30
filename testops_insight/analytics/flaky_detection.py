from collections import defaultdict
from typing import NamedTuple

from testops_insight.domain.models import TestCase, TestSuite


class FlakyTest(NamedTuple):
    test_name: str
    pass_count: int
    fail_count: int
    total_runs: int
    flakiness_rate: float


def detect_flaky_tests(test_suite: TestSuite, min_runs: int = 2) -> list[FlakyTest]:
    if len(test_suite.test_runs) < min_runs:
        return []

    test_stats = defaultdict(lambda: {"passed": 0, "failed": 0, "total": 0})

    for test_run in test_suite.test_runs:
        test_names = {tc.full_name for tc in test_run.test_cases}
        test_results = {tc.full_name: tc.status.name for tc in test_run.test_cases}

        for test_name in test_names:
            test_stats[test_name]["total"] += 1
            if test_results.get(test_name) == "PASSED":
                test_stats[test_name]["passed"] += 1
            elif test_results.get(test_name) in ("FAILED", "ERROR"):
                test_stats[test_name]["failed"] += 1

    flaky_tests = []
    for test_name, stats in test_stats.items():
        if stats["total"] < min_runs:
            continue

        pass_count = stats["passed"]
        fail_count = stats["failed"]
        total = stats["total"]

        if pass_count > 0 and fail_count > 0:
            flakiness_rate = min(pass_count, fail_count) / total
            flaky_tests.append(
                FlakyTest(
                    test_name=test_name,
                    pass_count=pass_count,
                    fail_count=fail_count,
                    total_runs=total,
                    flakiness_rate=flakiness_rate,
                )
            )

    flaky_tests.sort(key=lambda x: x.flakiness_rate, reverse=True)
    return flaky_tests

