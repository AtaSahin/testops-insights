import json
from datetime import datetime
from pathlib import Path
from typing import Any

from testops_insight.analytics import (
    calculate_health_score,
    detect_flaky_tests,
    get_frequent_failures,
    get_pass_rate_trend,
    get_slowest_tests,
)
from testops_insight.domain.models import TestSuite
from testops_insight.reporting.html_generator import _generate_html_content


def generate_report(test_suite: TestSuite, output_dir: Path) -> dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    assets_dir = output_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    health_score = calculate_health_score(test_suite)
    flaky_tests = detect_flaky_tests(test_suite)
    frequent_failures = get_frequent_failures(test_suite)
    slow_tests = get_slowest_tests(test_suite, limit=20)
    trends = get_pass_rate_trend(test_suite)

    metrics = {
        "health_score": health_score,
        "total_runs": test_suite.total_runs,
        "suite_name": test_suite.name,
        "generated_at": datetime.now().isoformat(),
        "flaky_tests_count": len(flaky_tests),
        "failing_tests_count": len(frequent_failures),
        "flaky_tests": [
            {
                "test_name": t.test_name,
                "pass_count": t.pass_count,
                "fail_count": t.fail_count,
                "total_runs": t.total_runs,
                "flakiness_rate": t.flakiness_rate,
            }
            for t in flaky_tests
        ],
        "frequent_failures": [
            {
                "test_name": f.test_name,
                "failure_count": f.failure_count,
                "total_runs": f.total_runs,
                "failure_rate": f.failure_rate,
            }
            for f in frequent_failures
        ],
        "slowest_tests": [
            {
                "test_name": t.test_name,
                "avg_duration": t.avg_duration,
                "max_duration": t.max_duration,
                "total_runs": t.total_runs,
            }
            for t in slow_tests
        ],
    }

    html_content = _generate_html_content(
        test_suite, health_score, flaky_tests, frequent_failures, slow_tests, trends
    )

    (output_dir / "index.html").write_text(html_content, encoding="utf-8")
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    return metrics

