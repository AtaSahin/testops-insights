from testops_insight.domain.models import TestSuite


def calculate_health_score(test_suite: TestSuite) -> float:
    if len(test_suite.test_runs) == 0:
        return 0.0

    if len(test_suite.test_runs) == 1:
        test_run = test_suite.test_runs[0]
        if test_run.total_tests == 0:
            return 0.0
        return (test_run.passed / test_run.total_tests) * 100.0

    total_tests = 0
    total_passed = 0

    for test_run in test_suite.test_runs:
        total_tests += test_run.total_tests
        total_passed += test_run.passed

    if total_tests == 0:
        return 0.0

    base_score = (total_passed / total_tests) * 100.0

    recent_runs = test_suite.test_runs[-min(5, len(test_suite.test_runs)) :]
    recent_total = sum(run.total_tests for run in recent_runs)
    recent_passed = sum(run.passed for run in recent_runs)

    if recent_total > 0:
        recent_score = (recent_passed / recent_total) * 100.0
        return (base_score * 0.6 + recent_score * 0.4)
    else:
        return base_score

