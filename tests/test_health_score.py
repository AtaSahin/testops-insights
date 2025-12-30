from datetime import datetime

import pytest

from testops_insight.analytics.health_score import calculate_health_score
from testops_insight.domain.models import TestCase, TestRun, TestSuite, TestStatus


def create_test_case(name: str, classname: str, status: TestStatus, duration: float = 1.0) -> TestCase:
    return TestCase(
        name=name,
        classname=classname,
        status=status,
        duration=duration,
    )


def test_perfect_health_score():
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
                create_test_case("test1", "ClassA", TestStatus.PASSED),
                create_test_case("test2", "ClassA", TestStatus.PASSED),
            ],
            timestamp=datetime(2024, 1, 1, 11, 0),
        ),
    ]

    suite = TestSuite(name="TestSuite", test_runs=test_runs)
    score = calculate_health_score(suite)

    assert score == 100.0


def test_zero_health_score():
    test_runs = [
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.FAILED),
                create_test_case("test2", "ClassA", TestStatus.FAILED),
            ],
            timestamp=datetime(2024, 1, 1, 10, 0),
        ),
    ]

    suite = TestSuite(name="TestSuite", test_runs=test_runs)
    score = calculate_health_score(suite)

    assert score == 0.0


def test_partial_health_score():
    test_runs = [
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.PASSED),
                create_test_case("test2", "ClassA", TestStatus.FAILED),
            ],
            timestamp=datetime(2024, 1, 1, 10, 0),
        ),
    ]

    suite = TestSuite(name="TestSuite", test_runs=test_runs)
    score = calculate_health_score(suite)

    assert score == 50.0


def test_empty_test_suite():
    suite = TestSuite(name="TestSuite", test_runs=[])
    score = calculate_health_score(suite)

    assert score == 0.0


def test_single_test_run():
    test_runs = [
        TestRun.from_test_cases(
            [
                create_test_case("test1", "ClassA", TestStatus.PASSED),
                create_test_case("test2", "ClassA", TestStatus.PASSED),
                create_test_case("test3", "ClassA", TestStatus.FAILED),
            ],
            timestamp=datetime(2024, 1, 1, 10, 0),
        ),
    ]

    suite = TestSuite(name="TestSuite", test_runs=test_runs)
    score = calculate_health_score(suite)

    expected = (2 / 3) * 100.0
    assert abs(score - expected) < 0.01


def test_health_score_with_recent_trends():
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
                create_test_case("test1", "ClassA", TestStatus.PASSED),
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
    score = calculate_health_score(suite)

    assert score > 50.0
    assert score <= 100.0

