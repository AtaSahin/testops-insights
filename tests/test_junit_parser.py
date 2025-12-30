import tempfile
from pathlib import Path
from datetime import datetime

import pytest

from testops_insight.domain.models import TestCase, TestRun, TestStatus
from testops_insight.ingestion.junit_parser import parse_junit_xml


def test_parse_simple_testsuite():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <testsuite name="TestSuite" tests="2" failures="1" errors="0" skipped="0" time="1.5">
        <testcase classname="TestClass" name="test_pass" time="0.5"/>
        <testcase classname="TestClass" name="test_fail" time="1.0">
            <failure message="Assertion failed">Expected True but got False</failure>
        </testcase>
    </testsuite>
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write(xml_content)
        temp_path = f.name

    try:
        test_run = parse_junit_xml(temp_path)

        assert isinstance(test_run, TestRun)
        assert test_run.total_tests == 2
        assert test_run.passed == 1
        assert test_run.failed == 1
        assert test_run.skipped == 0
        assert test_run.errors == 0
        assert abs(test_run.duration - 1.5) < 0.01

        assert len(test_run.test_cases) == 2
        assert test_run.test_cases[0].name == "test_pass"
        assert test_run.test_cases[0].status == TestStatus.PASSED
        assert test_run.test_cases[1].name == "test_fail"
        assert test_run.test_cases[1].status == TestStatus.FAILED
        assert "Assertion failed" in test_run.test_cases[1].message
    finally:
        Path(temp_path).unlink()


def test_parse_testsuites():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <testsuites>
        <testsuite name="Suite1" tests="1" time="0.5">
            <testcase classname="Class1" name="test1" time="0.5"/>
        </testsuite>
        <testsuite name="Suite2" tests="1" time="0.3">
            <testcase classname="Class2" name="test2" time="0.3"/>
        </testsuite>
    </testsuites>
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write(xml_content)
        temp_path = f.name

    try:
        test_run = parse_junit_xml(temp_path)

        assert test_run.total_tests == 2
        assert test_run.passed == 2
        assert len(test_run.test_cases) == 2
    finally:
        Path(temp_path).unlink()


def test_parse_with_skipped():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <testsuite name="TestSuite" tests="2" skipped="1">
        <testcase classname="TestClass" name="test_pass" time="0.5"/>
        <testcase classname="TestClass" name="test_skip" time="0.0">
            <skipped message="Not implemented"/>
        </testcase>
    </testsuite>
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write(xml_content)
        temp_path = f.name

    try:
        test_run = parse_junit_xml(temp_path)

        assert test_run.skipped == 1
        skipped_test = next(tc for tc in test_run.test_cases if tc.status == TestStatus.SKIPPED)
        assert skipped_test.name == "test_skip"
    finally:
        Path(temp_path).unlink()


def test_parse_with_error():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <testsuite name="TestSuite" tests="1">
        <testcase classname="TestClass" name="test_error" time="0.1">
            <error type="Exception" message="Something went wrong">Traceback...</error>
        </testcase>
    </testsuite>
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write(xml_content)
        temp_path = f.name

    try:
        test_run = parse_junit_xml(temp_path)

        assert test_run.errors == 1
        error_test = test_run.test_cases[0]
        assert error_test.status == TestStatus.ERROR
        assert error_test.failure_type == "Exception"
    finally:
        Path(temp_path).unlink()


def test_parse_empty_testsuite():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <testsuite name="TestSuite" tests="0" time="0.0">
    </testsuite>
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write(xml_content)
        temp_path = f.name

    try:
        test_run = parse_junit_xml(temp_path)

        assert test_run.total_tests == 0
        assert len(test_run.test_cases) == 0
        assert test_run.duration == 0.0
    finally:
        Path(temp_path).unlink()


def test_parse_single_test():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <testsuite name="TestSuite" tests="1" time="2.5">
        <testcase classname="MyClass" name="single_test" time="2.5"/>
    </testsuite>
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write(xml_content)
        temp_path = f.name

    try:
        test_run = parse_junit_xml(temp_path)

        assert test_run.total_tests == 1
        assert test_run.test_cases[0].full_name == "MyClass.single_test"
        assert test_run.test_cases[0].duration == 2.5
    finally:
        Path(temp_path).unlink()

