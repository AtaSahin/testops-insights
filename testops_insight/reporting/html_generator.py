from datetime import datetime, timedelta
from pathlib import Path

from testops_insight.analytics import (
    calculate_health_score,
    detect_flaky_tests,
    get_frequent_failures,
    get_last_failed_timestamp,
    get_last_test_status,
    get_pass_rate_trend,
    get_slowest_tests,
)
from testops_insight.domain.models import TestSuite


def generate_html_report(test_suite: TestSuite, output_path: str | Path) -> None:
    health_score = calculate_health_score(test_suite)
    flaky_tests = detect_flaky_tests(test_suite)
    frequent_failures = get_frequent_failures(test_suite)
    slow_tests = get_slowest_tests(test_suite, limit=20)
    trends = get_pass_rate_trend(test_suite)

    html_content = _generate_html_content(
        test_suite, health_score, flaky_tests, frequent_failures, slow_tests, trends
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding="utf-8")


def _generate_html_content(
    test_suite: TestSuite,
    health_score: float,
    flaky_tests: list,
    frequent_failures: list,
    slow_tests: list,
    trends: list,
) -> str:
    time_range = _calculate_time_range(test_suite)
    exec_summary = _calculate_executive_summary(test_suite, flaky_tests, frequent_failures)
    health_explanation = _get_health_explanation(test_suite, health_score, flaky_tests, slow_tests)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TestOps Insights</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #ffffff;
            color: #212529;
            line-height: 1.5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        header {{
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 20px;
            margin-bottom: 40px;
        }}
        h1 {{
            font-size: 28px;
            font-weight: 600;
            color: #212529;
            margin-bottom: 8px;
        }}
        .header-meta {{
            font-size: 14px;
            color: #6c757d;
        }}
        .executive-summary {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 24px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        .metric-label {{
            font-size: 14px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .metric-pass {{ color: #28a745; }}
        .metric-flaky {{ color: #ffc107; }}
        .metric-fail {{ color: #dc3545; }}
        .metric-duration {{ color: #17a2b8; }}
        .health-score-section {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 40px;
            text-align: center;
            margin-bottom: 40px;
        }}
        .health-score-value {{
            font-size: 72px;
            font-weight: 700;
            margin-bottom: 12px;
        }}
        .health-score-label {{
            font-size: 18px;
            color: #6c757d;
            margin-bottom: 16px;
        }}
        .health-explanation {{
            font-size: 14px;
            color: #495057;
            font-style: italic;
        }}
        .score-excellent {{ color: #28a745; }}
        .score-good {{ color: #ffc107; }}
        .score-poor {{ color: #dc3545; }}
        section {{
            margin-bottom: 40px;
        }}
        h2 {{
            font-size: 20px;
            font-weight: 600;
            color: #212529;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e9ecef;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #ffffff;
            border: 1px solid #dee2e6;
        }}
        th {{
            background: #f8f9fa;
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            font-size: 13px;
            color: #495057;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #dee2e6;
        }}
        td {{
            padding: 12px 16px;
            border-bottom: 1px solid #e9ecef;
            font-size: 14px;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .test-name {{
            font-family: 'Courier New', monospace;
            font-size: 13px;
            word-break: break-all;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: 600;
        }}
        .status-passed {{
            background: #d4edda;
            color: #155724;
        }}
        .status-failed {{
            background: #f8d7da;
            color: #721c24;
        }}
        .status-error {{
            background: #f8d7da;
            color: #721c24;
        }}
        .status-skipped {{
            background: #fff3cd;
            color: #856404;
        }}
        .rate-high {{
            color: #dc3545;
            font-weight: 600;
        }}
        .rate-medium {{
            color: #ffc107;
            font-weight: 600;
        }}
        .rate-low {{
            color: #6c757d;
        }}
        .trend-chart {{
            background: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 24px;
            margin-bottom: 40px;
        }}
        .chart-container {{
            margin-top: 20px;
            height: 150px;
            display: flex;
            align-items: flex-end;
            gap: 4px;
            border-bottom: 2px solid #dee2e6;
            padding-bottom: 8px;
        }}
        .chart-bar {{
            flex: 1;
            background: #17a2b8;
            min-width: 4px;
            border-radius: 2px 2px 0 0;
        }}
        .chart-label {{
            font-size: 11px;
            color: #6c757d;
            margin-top: 4px;
        }}
        footer {{
            margin-top: 60px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            text-align: center;
            font-size: 12px;
            color: #6c757d;
        }}
        .no-data {{
            text-align: center;
            padding: 40px;
            color: #6c757d;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>TestOps Insights</h1>
            <div class="header-meta">
                {test_suite.name} • Analyzed {test_suite.total_runs} test run{'' if test_suite.total_runs == 1 else 's'}{time_range}
            </div>
        </header>

        <div class="executive-summary">
            {exec_summary}
        </div>

        <div class="health-score-section">
            <div class="health-score-value {_get_score_class(health_score)}">
                {health_score:.0f} / 100
            </div>
            <div class="health-score-label">Pipeline Health</div>
            <div class="health-explanation">
                {health_explanation}
            </div>
        </div>

        <section>
            <h2>Flaky Tests</h2>
            {_generate_flaky_tests_table(test_suite, flaky_tests)}
        </section>

        <section>
            <h2>Top Failing Tests</h2>
            {_generate_failing_tests_table(test_suite, frequent_failures)}
        </section>

        <section>
            <h2>Slowest Tests</h2>
            {_generate_slow_tests_table(slow_tests)}
        </section>

        {_generate_trend_section(trends) if trends else ''}

        <footer>
            Generated by TestOps Insights<br>
            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </footer>
    </div>
</body>
</html>"""


def _calculate_time_range(test_suite: TestSuite) -> str:
    if len(test_suite.test_runs) == 0:
        return ""

    timestamps = [run.timestamp for run in test_suite.test_runs if run.timestamp]
    if not timestamps:
        return ""

    min_time = min(timestamps)
    max_time = max(timestamps)
    delta = max_time - min_time

    if delta.days > 0:
        return f" (last {delta.days} day{'' if delta.days == 1 else 's'})"
    elif delta.seconds > 3600:
        hours = delta.seconds // 3600
        return f" (last {hours} hour{'' if hours == 1 else 's'})"
    else:
        return ""


def _calculate_executive_summary(test_suite: TestSuite, flaky_tests: list, frequent_failures: list) -> str:
    if len(test_suite.test_runs) == 0:
        return """
            <div class="metric-card">
                <div class="metric-value metric-pass">0%</div>
                <div class="metric-label">Pass Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value metric-flaky">0</div>
                <div class="metric-label">Flaky Tests Count</div>
            </div>
            <div class="metric-card">
                <div class="metric-value metric-fail">0</div>
                <div class="metric-label">Failing Tests Count</div>
            </div>
            <div class="metric-card">
                <div class="metric-value metric-duration">0.0s</div>
                <div class="metric-label">Avg Test Duration</div>
            </div>
        """

    total_tests = sum(run.total_tests for run in test_suite.test_runs)
    total_passed = sum(run.passed for run in test_suite.test_runs)
    total_runs = len(test_suite.test_runs)

    if total_tests > 0:
        pass_rate = (total_passed / total_tests) * 100.0
    else:
        pass_rate = 0.0

    flaky_count = len(flaky_tests)
    failing_count = len(frequent_failures)

    total_duration = sum(run.duration for run in test_suite.test_runs)
    if total_tests > 0:
        avg_duration = total_duration / total_tests
    else:
        avg_duration = 0.0

    return f"""
            <div class="metric-card">
                <div class="metric-value metric-pass">{pass_rate:.1f}%</div>
                <div class="metric-label">Pass Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value metric-flaky">{flaky_count}</div>
                <div class="metric-label">Flaky Tests Count</div>
            </div>
            <div class="metric-card">
                <div class="metric-value metric-fail">{failing_count}</div>
                <div class="metric-label">Failing Tests Count</div>
            </div>
            <div class="metric-card">
                <div class="metric-value metric-duration">{avg_duration:.2f}s</div>
                <div class="metric-label">Avg Test Duration</div>
            </div>
        """


def _get_health_explanation(test_suite: TestSuite, health_score: float, flaky_tests: list, slow_tests: list) -> str:
    reasons = []

    if len(flaky_tests) > 0:
        reasons.append(f"{len(flaky_tests)} flaky test{'s' if len(flaky_tests) != 1 else ''}")

    if len(slow_tests) > 0 and slow_tests[0].avg_duration > 5.0:
        reasons.append("increased average duration")

    if len(test_suite.test_runs) > 0:
        recent_runs = test_suite.test_runs[-min(3, len(test_suite.test_runs)):]
        recent_failures = sum(run.failed + run.errors for run in recent_runs)
        if recent_failures > 0:
            reasons.append("recent test failures")

    if not reasons:
        return "Pipeline is healthy with no significant issues detected."

    return "Reduced due to " + ", ".join(reasons) + "."


def _get_score_class(score: float) -> str:
    if score >= 80:
        return "score-excellent"
    elif score >= 60:
        return "score-good"
    else:
        return "score-poor"


def _generate_flaky_tests_table(test_suite: TestSuite, flaky_tests: list) -> str:
    if not flaky_tests:
        return '<div class="no-data">No flaky tests detected</div>'

    rows = []
    for test in flaky_tests:
        fail_rate = (test.fail_count / test.total_runs) * 100.0
        flaky_score = test.flakiness_rate * 100.0
        last_status = get_last_test_status(test_suite, test.test_name)

        status_class = f"status-{last_status.lower()}"
        rate_class = "rate-high" if fail_rate > 50 else "rate-medium" if fail_rate > 25 else "rate-low"

        rows.append(
            f"""
            <tr>
                <td class="test-name">{test.test_name}</td>
                <td><span class="{rate_class}">{fail_rate:.1f}%</span></td>
                <td><span class="{rate_class}">{flaky_score:.1f}%</span></td>
                <td><span class="status-badge {status_class}">{last_status}</span></td>
            </tr>
            """
        )

    return f"""
        <table>
            <thead>
                <tr>
                    <th>Test Name</th>
                    <th>Fail Rate</th>
                    <th>Flaky Score</th>
                    <th>Last Status</th>
                </tr>
            </thead>
            <tbody>
                {"".join(rows)}
            </tbody>
        </table>
    """


def _generate_failing_tests_table(test_suite: TestSuite, frequent_failures: list) -> str:
    if not frequent_failures:
        return '<div class="no-data">No failing tests detected</div>'

    rows = []
    for failure in frequent_failures:
        last_failed = get_last_failed_timestamp(test_suite, failure.test_name)
        last_failed_str = last_failed.strftime("%Y-%m-%d %H:%M") if last_failed else "N/A"

        rows.append(
            f"""
            <tr>
                <td class="test-name">{failure.test_name}</td>
                <td>{failure.failure_count}</td>
                <td>{last_failed_str}</td>
            </tr>
            """
        )

    return f"""
        <table>
            <thead>
                <tr>
                    <th>Test Name</th>
                    <th>Fail Count</th>
                    <th>Last Failed</th>
                </tr>
            </thead>
            <tbody>
                {"".join(rows)}
            </tbody>
        </table>
    """


def _generate_slow_tests_table(slow_tests: list) -> str:
    if not slow_tests:
        return '<div class="no-data">No test duration data available</div>'

    max_duration = max(test.avg_duration for test in slow_tests) if slow_tests else 1.0

    rows = []
    for test in slow_tests:
        bar_width = (test.avg_duration / max_duration) * 100.0 if max_duration > 0 else 0

        rows.append(
            f"""
            <tr>
                <td class="test-name">{test.test_name}</td>
                <td>
                    <div style="display: flex; align-items: center;">
                        <div style="width: {bar_width}%; background: #17a2b8; height: 20px; margin-right: 8px; min-width: 2px;"></div>
                        <span>{test.avg_duration:.3f}s</span>
                    </div>
                </td>
            </tr>
            """
        )

    return f"""
        <table>
            <thead>
                <tr>
                    <th>Test Name</th>
                    <th>Avg Duration (s)</th>
                </tr>
            </thead>
            <tbody>
                {"".join(rows)}
            </tbody>
        </table>
    """


def _generate_trend_section(trends: list) -> str:
    if len(trends) < 2:
        return ""

    max_pass_rate = max(t.pass_rate for t in trends) if trends else 100.0
    max_duration = max(t.avg_duration for t in trends) if trends else 1.0

    pass_rate_bars = []
    duration_bars = []

    for trend in trends:
        pass_height = (trend.pass_rate / max_pass_rate) * 100.0 if max_pass_rate > 0 else 0
        duration_height = (trend.avg_duration / max_duration) * 100.0 if max_duration > 0 else 0

        pass_rate_bars.append(f'<div class="chart-bar" style="height: {pass_height}%;" title="Run {trend.run_index + 1}: {trend.pass_rate:.1f}%"></div>')
        duration_bars.append(f'<div class="chart-bar" style="height: {duration_height}%;" title="Run {trend.run_index + 1}: {trend.avg_duration:.2f}s"></div>')

    return f"""
        <section>
            <h2>Trends</h2>
            <div class="trend-chart">
                <div style="margin-bottom: 40px;">
                    <strong style="display: block; margin-bottom: 12px;">Pass Rate Trend</strong>
                    <div class="chart-container">
                        {"".join(pass_rate_bars)}
                    </div>
                    <div class="chart-label" style="text-align: center; margin-top: 8px;">
                        {len(trends)} test runs
                    </div>
                </div>
                <div>
                    <strong style="display: block; margin-bottom: 12px;">Average Duration Trend</strong>
                    <div class="chart-container">
                        {"".join(duration_bars)}
                    </div>
                    <div class="chart-label" style="text-align: center; margin-top: 8px;">
                        {len(trends)} test runs
                    </div>
                </div>
            </div>
        </section>
    """
