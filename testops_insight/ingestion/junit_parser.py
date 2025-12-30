import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Optional

from testops_insight.domain.models import TestCase, TestRun, TestStatus


def parse_junit_xml(file_path: str | Path) -> TestRun:
    tree = ET.parse(file_path)
    root = tree.getroot()

    if root.tag == "testsuites":
        timestamp = _parse_timestamp(root.get("timestamp"))
        test_cases = []
        for testsuite in root.findall("testsuite"):
            test_cases.extend(_parse_testsuite(testsuite))
    elif root.tag == "testsuite":
        timestamp = _parse_timestamp(root.get("timestamp"))
        test_cases = _parse_testsuite(root)
    else:
        raise ValueError(f"Unexpected root element: {root.tag}")

    return TestRun.from_test_cases(test_cases, timestamp)


def _parse_testsuite(testsuite: ET.Element) -> list[TestCase]:
    test_cases = []
    classname = testsuite.get("name", "")

    for testcase in testsuite.findall("testcase"):
        name = testcase.get("name", "")
        test_classname = testcase.get("classname", classname)
        duration = float(testcase.get("time", "0.0"))

        status = TestStatus.PASSED
        message = None
        failure_type = None

        failure = testcase.find("failure")
        if failure is not None:
            status = TestStatus.FAILED
            message = failure.get("message") or failure.text
            failure_type = failure.get("type", "failure")

        error = testcase.find("error")
        if error is not None:
            status = TestStatus.ERROR
            message = error.text
            failure_type = error.get("type", "error")

        skipped = testcase.find("skipped")
        if skipped is not None:
            status = TestStatus.SKIPPED
            message = skipped.text

        test_cases.append(
            TestCase(
                name=name,
                classname=test_classname,
                status=status,
                duration=duration,
                message=message,
                failure_type=failure_type,
            )
        )

    return test_cases


def _parse_timestamp(timestamp_str: Optional[str]) -> Optional[datetime]:
    if not timestamp_str:
        return None

    try:
        return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        try:
            return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None

