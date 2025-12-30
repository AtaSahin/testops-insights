import argparse
import sys
from pathlib import Path

from testops_insight.cli.config import load_config
from testops_insight.cli.discovery import discover_test_runs
from testops_insight.domain.models import TestSuite
from testops_insight.reporting import generate_report


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="testops-insights",
        description="TestOps Dashboard - Analyze test results to identify flaky tests and assess pipeline health",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="testops-insights 0.1.0",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    analyze_parser = subparsers.add_parser("analyze", help="Analyze test runs and generate dashboard")
    analyze_parser.add_argument(
        "--runs-path",
        type=str,
        help="Path to directory containing test run folders (default: ./test-results or from config)",
    )
    analyze_parser.add_argument(
        "--out",
        type=str,
        help="Output directory for report (default: ./report or from config)",
    )
    analyze_parser.add_argument(
        "--name",
        type=str,
        help="Test suite name (default: 'Test Suite' or from config)",
    )
    analyze_parser.add_argument(
        "--config",
        type=str,
        help="Path to config file (default: testops.yaml or testops.yml in current directory)",
    )
    analyze_parser.add_argument(
        "--last",
        type=int,
        help="Analyze only the most recent N runs",
    )
    analyze_parser.add_argument(
        "--fail-under-health",
        type=float,
        help="Exit with non-zero code if health score is below this threshold",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "analyze":
        run_analyze(args)
    else:
        parser.print_help()
        sys.exit(1)


def run_analyze(args: argparse.Namespace) -> None:
    config = None
    if args.config:
        config = load_config(Path(args.config))
    else:
        config = load_config()

    runs_path = args.runs_path or (config.runs_path if config else "./test-results")
    output_dir = args.out or (config.report.output_dir if config else "./report")
    suite_name = args.name or (config.report.suite_name if config else "Test Suite")
    last_n = args.last or (config.analysis.last_n_runs if config else None)

    runs_path = Path(runs_path)
    if not runs_path.exists():
        print(f"Error: Runs path does not exist: {runs_path}")
        sys.exit(1)

    discovered_runs = discover_test_runs(runs_path, last_n)
    if not discovered_runs:
        print(f"Error: No test runs found in {runs_path}")
        sys.exit(1)

    test_runs = [test_run for _, test_run in discovered_runs]

    for xml_path, test_run in discovered_runs:
        print(f"Parsed: {xml_path} ({test_run.total_tests} tests)")

    test_suite = TestSuite(name=suite_name, test_runs=test_runs)

    output_dir = Path(output_dir)
    metrics = generate_report(test_suite, output_dir)
    print(f"Report generated: {output_dir.absolute()}")

    if args.fail_under_health is not None:
        health_score = metrics["health_score"]
        if health_score < args.fail_under_health:
            print(f"Health score {health_score:.1f} is below threshold {args.fail_under_health}")
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
