from datetime import datetime

import pytest

from testops_insight.analytics.frequent_failures import get_frequent_failures
from testops_insight.domain.models import TestCase, TestRun, TestSuite, TestStatus


def create_test_case(name: str, classname: str, status: TestStatus, duration: float = 1.0) -> TestCase:
    return TestCase(
        name=name,
        classname=classname,
        status=status,
        duration=duration,
    )


def test_frequent_failure_detection():
    test_runs = [
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.FAILED),
                create_test_case("test2", "ClassA", TestStatus.PASSED),
            ],
            timestamp=datetime(2024, 1, 1, 10, 0),
        ),
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.FAILED),
                create_test_case("test2", "ClassA", TestStatus.PASSED),
            ],
            timestamp=datetime(2024, 1, 1, 11, 0),
        ),
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.PASSED),
                create_test_case("test2", "ClassA", TestStatus.FAILED),
            ],
            timestamp=datetime(2024, 1, 1, 12, 0),
        ),
    ]

    suite = TestSuite(name="TestSuite", test_runs=test_runs)
    failures = get_frequent_failures(suite)

    assert len(failures) == 2
    test1_failure = next(f for f in failures if f.test_name == "ClassA.test1")
    assert test1_failure.failure_count == 2
    assert test1_failure.total_runs == 3
    assert abs(test1_failure.failure_rate - 2/3) < 0.01


def test_no_failures():
    test_runs = [
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.PASSED),
            ],
            timestamp=datetime(2024, 1, 1, 10, 0),
        ),
    ]

    suite = TestSuite(name="TestSuite", test_runs=test_runs)
    failures = get_frequent_failures(suite)

    assert len(failures) == 0


def test_empty_test_suite():
    suite = TestSuite(name="TestSuite", test_runs=[])
    failures = get_frequent_failures(suite)

    assert len(failures) == 0


def test_always_failing_test():
    test_runs = [
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.FAILED),
            ],
            timestamp=datetime(2024, 1, 1, 10, 0),
        ),
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.FAILED),
            ],
            timestamp=datetime(2024, 1, 1, 11, 0),
        ),
    ]

    suite = TestSuite(name="TestSuite", test_runs=test_runs)
    failures = get_frequent_failures(suite)

    assert len(failures) == 1
    assert failures[0].failure_rate == 1.0
    assert failures[0].failure_count == 2


def test_sorted_by_failure_rate():
    test_runs = [
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.FAILED),
                create_test_case("test2", "ClassA", TestStatus.FAILED),
            ],
            timestamp=datetime(2024, 1, 1, 10, 0),
        ),
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.FAILED),
                create_test_case("test2", "ClassA", TestStatus.PASSED),
            ],
            timestamp=datetime(2024, 1, 1, 11, 0),
        ),
    ]

    suite = TestSuite(name="TestSuite", test_runs=test_runs)
    failures = get_frequent_failures(suite)

    assert len(failures) == 2
    assert failures[0].failure_rate >= failures[1].failure_rate

