from datetime import datetime

import pytest

from testops_insight.analytics.flaky_detection import detect_flaky_tests
from testops_insight.domain.models import TestCase, TestRun, TestSuite, TestStatus


def create_test_case(name: str, classname: str, status: TestStatus, duration: float = 1.0) -> TestCase:
    return TestCase(
        name=name,
        classname=classname,
        status=status,
        duration=duration,
    )


def test_detect_flaky_test():
    test_runs = [
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.PASSED),
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
                create_test_case("test2", "ClassA", TestStatus.PASSED),
            ],
            timestamp=datetime(2024, 1, 1, 12, 0),
        ),
    ]

    suite = TestSuite(name="TestSuite", test_runs=test_runs)
    flaky = detect_flaky_tests(suite)

    assert len(flaky) == 1
    assert flaky[0].test_name == "ClassA.test1"
    assert flaky[0].pass_count == 2
    assert flaky[0].fail_count == 1
    assert flaky[0].total_runs == 3
    assert abs(flaky[0].flakiness_rate - 1/3) < 0.01


def test_no_flaky_tests():
    test_runs = [
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.PASSED),
            ],
            timestamp=datetime(2024, 1, 1, 10, 0),
        ),
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.PASSED),
            ],
            timestamp=datetime(2024, 1, 1, 11, 0),
        ),
    ]

    suite = TestSuite(name="TestSuite", test_runs=test_runs)
    flaky = detect_flaky_tests(suite)

    assert len(flaky) == 0


def test_single_test_run():
    test_runs = [
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.PASSED),
            ],
            timestamp=datetime(2024, 1, 1, 10, 0),
        ),
    ]

    suite = TestSuite(name="TestSuite", test_runs=test_runs)
    flaky = detect_flaky_tests(suite, min_runs=2)

    assert len(flaky) == 0


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
    flaky = detect_flaky_tests(suite)

    assert len(flaky) == 0


def test_multiple_flaky_tests_sorted():
    test_runs = [
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.PASSED),
                create_test_case("test2", "ClassA", TestStatus.PASSED),
            ],
            timestamp=datetime(2024, 1, 1, 10, 0),
        ),
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.FAILED),
                create_test_case("test2", "ClassA", TestStatus.FAILED),
            ],
            timestamp=datetime(2024, 1, 1, 11, 0),
        ),
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.PASSED),
                create_test_case("test2", "ClassA", TestStatus.PASSED),
            ],
            timestamp=datetime(2024, 1, 1, 12, 0),
        ),
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.PASSED),
                create_test_case("test2", "ClassA", TestStatus.FAILED),
            ],
            timestamp=datetime(2024, 1, 1, 13, 0),
        ),
    ]

    suite = TestSuite(name="TestSuite", test_runs=test_runs)
    flaky = detect_flaky_tests(suite)

    assert len(flaky) == 2
    assert flaky[0].flakiness_rate >= flaky[1].flakiness_rate


def test_empty_test_suite():
    suite = TestSuite(name="TestSuite", test_runs=[])
    flaky = detect_flaky_tests(suite)

    assert len(flaky) == 0

