from collections import defaultdict
from typing import NamedTuple

from testops_insight.domain.models import TestSuite


class FrequentFailure(NamedTuple):
    test_name: str
    failure_count: int
    total_runs: int
    failure_rate: float


def get_frequent_failures(test_suite: TestSuite, min_runs: int = 1) -> list[FrequentFailure]:
    if len(test_suite.test_runs) == 0:
        return []

    test_failures = defaultdict(lambda: {"failures": 0, "total": 0})

    for test_run in test_suite.test_runs:
        test_names = {tc.full_name for tc in test_run.test_cases}
        test_results = {tc.full_name: tc.status.name for tc in test_run.test_cases}

        for test_name in test_names:
            test_failures[test_name]["total"] += 1
            if test_results.get(test_name) in ("FAILED", "ERROR"):
                test_failures[test_name]["failures"] += 1

    failures = []
    for test_name, stats in test_failures.items():
        if stats["total"] < min_runs:
            continue

        failure_count = stats["failures"]
        if failure_count == 0:
            continue

        total = stats["total"]
        failure_rate = failure_count / total

        failures.append(
            FrequentFailure(
                test_name=test_name,
                failure_count=failure_count,
                total_runs=total,
                failure_rate=failure_rate,
            )
        )

    failures.sort(key=lambda x: (x.failure_rate, x.failure_count), reverse=True)
    return failures

