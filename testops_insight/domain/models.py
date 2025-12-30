from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class TestStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestCase:
    name: str
    classname: str
    status: TestStatus
    duration: float
    message: Optional[str] = None
    failure_type: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.classname}.{self.name}"


@dataclass
class TestRun:
    timestamp: datetime
    test_cases: list[TestCase]
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float

    @classmethod
    def from_test_cases(cls, test_cases: list[TestCase], timestamp: Optional[datetime] = None) -> "TestRun":
        if timestamp is None:
            timestamp = datetime.now()

        passed = sum(1 for tc in test_cases if tc.status == TestStatus.PASSED)
        failed = sum(1 for tc in test_cases if tc.status == TestStatus.FAILED)
        skipped = sum(1 for tc in test_cases if tc.status == TestStatus.SKIPPED)
        errors = sum(1 for tc in test_cases if tc.status == TestStatus.ERROR)
        duration = sum(tc.duration for tc in test_cases)

        return cls(
            timestamp=timestamp,
            test_cases=test_cases,
            total_tests=len(test_cases),
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            duration=duration,
        )


@dataclass
class TestSuite:
    name: str
    test_runs: list[TestRun]

    @property
    def total_runs(self) -> int:
        return len(self.test_runs)

    @property
    def all_test_cases(self) -> list[TestCase]:
        all_cases = []
        for test_run in self.test_runs:
            all_cases.extend(test_run.test_cases)
        return all_cases

