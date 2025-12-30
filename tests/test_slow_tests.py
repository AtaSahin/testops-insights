from datetime import datetime

import pytest

from testops_insight.analytics.slow_tests import get_slowest_tests
from testops_insight.domain.models import TestCase, TestRun, TestSuite, TestStatus


def create_test_case(name: str, classname: str, status: TestStatus, duration: float = 1.0) -> TestCase:
    return TestCase(
        name=name,
        classname=classname,
        status=status,
        duration=duration,
    )


def test_get_slowest_tests():
    test_runs = [
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.PASSED, duration=5.0),
                create_test_case("test2", "ClassA", TestStatus.PASSED, duration=1.0),
                create_test_case("test3", "ClassA", TestStatus.PASSED, duration=10.0),
            ],
            timestamp=datetime(2024, 1, 1, 10, 0),
        ),
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.PASSED, duration=6.0),
                create_test_case("test2", "ClassA", TestStatus.PASSED, duration=1.5),
                create_test_case("test3", "ClassA", TestStatus.PASSED, duration=9.0),
            ],
            timestamp=datetime(2024, 1, 1, 11, 0),
        ),
    ]

    suite = TestSuite(name="TestSuite", test_runs=test_runs)
    slow_tests = get_slowest_tests(suite, limit=10)

    assert len(slow_tests) == 3
    assert slow_tests[0].test_name == "ClassA.test3"
    assert slow_tests[0].avg_duration == 9.5
    assert slow_tests[0].max_duration == 10.0
    assert slow_tests[1].test_name == "ClassA.test1"
    assert slow_tests[2].test_name == "ClassA.test2"


def test_limit_parameter():
    test_runs = [
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.PASSED, duration=5.0),
                create_test_case("test2", "ClassA", TestStatus.PASSED, duration=1.0),
                create_test_case("test3", "ClassA", TestStatus.PASSED, duration=10.0),
            ],
            timestamp=datetime(2024, 1, 1, 10, 0),
        ),
    ]

    suite = TestSuite(name="TestSuite", test_runs=test_runs)
    slow_tests = get_slowest_tests(suite, limit=2)

    assert len(slow_tests) == 2
    assert slow_tests[0].test_name == "ClassA.test3"


def test_empty_test_suite():
    suite = TestSuite(name="TestSuite", test_runs=[])
    slow_tests = get_slowest_tests(suite)

    assert len(slow_tests) == 0


def test_single_test():
    test_runs = [
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.PASSED, duration=2.5),
            ],
            timestamp=datetime(2024, 1, 1, 10, 0),
        ),
    ]

    suite = TestSuite(name="TestSuite", test_runs=test_runs)
    slow_tests = get_slowest_tests(suite)

    assert len(slow_tests) == 1
    assert slow_tests[0].avg_duration == 2.5
    assert slow_tests[0].max_duration == 2.5
    assert slow_tests[0].total_runs == 1

