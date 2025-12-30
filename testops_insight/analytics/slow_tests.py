from collections import defaultdict
from typing import NamedTuple

from testops_insight.domain.models import TestSuite


class SlowTest(NamedTuple):
    test_name: str
    avg_duration: float
    max_duration: float
    total_runs: int


def get_slowest_tests(test_suite: TestSuite, limit: int = 10) -> list[SlowTest]:
    if len(test_suite.test_runs) == 0:
        return []

    test_durations = defaultdict(lambda: {"durations": [], "total": 0})

    for test_run in test_suite.test_runs:
        for test_case in test_run.test_cases:
            test_name = test_case.full_name
            test_durations[test_name]["durations"].append(test_case.duration)
            test_durations[test_name]["total"] += 1

    slow_tests = []
    for test_name, stats in test_durations.items():
        durations = stats["durations"]
        if not durations:
            continue

        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)

        slow_tests.append(
            SlowTest(
                test_name=test_name,
                avg_duration=avg_duration,
                max_duration=max_duration,
                total_runs=stats["total"],
            )
        )

    slow_tests.sort(key=lambda x: x.avg_duration, reverse=True)
    return slow_tests[:limit]

