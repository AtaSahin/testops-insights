# TestOps Insights

A tool for analyzing test results from CI/CD pipelines. Parses JUnit XML outputs, finds flaky tests, and tracks pipeline health over time.

<p align="center">
  <img src="docs/images/dashboard-full.png" alt="TestOps Insights Dashboard" width="800">
</p>

## What's the difference from Allure?

**Allure** is great for debugging a single test run. You get detailed logs, screenshots, and step-by-step execution info to figure out why something failed.

**TestOps Insights** looks at multiple test runs to find patterns. It spots flaky tests that sometimes pass and sometimes fail, calculates overall pipeline health, and shows trends over time.

Use both: Allure when you need to debug a specific failure, TestOps Insights when you want to understand test reliability.

## Features

- Parse JUnit XML files from multiple test runs
- Automatically find test runs in folder structures
- Detect flaky tests (ones that pass and fail inconsistently)
- List tests that fail most often
- Find slow tests
- Calculate a pipeline health score
- Generate HTML dashboard
- Config file support (testops.yaml)
- Exit codes for CI quality gates
- JSON metrics output

## Installation

```bash
pip install -r requirements.txt
```

Or for development:

```bash
pip install -e .
```

After install, `testops-insights` command is available.

## Quick Start

1. Put your test results in folders like this:

```
test-results/
  run_001/
    junit.xml
  run_002/
    junit.xml
  run_003/
    junit.xml
```

2. Run analysis:

```bash
testops-insights analyze --runs-path ./test-results --out ./report
```

3. Open the dashboard:

Open `report/index.html` in your browser.

## Usage

### Basic command

```bash
testops-insights analyze --runs-path <runs_directory> --out <output_directory>
```

### Options

- `--runs-path`: Directory with test run folders (default: `./test-results`)
- `--out`: Output directory (default: `./report`)
- `--name`: Test suite name (default: "Test Suite")
- `--config`: Config file path (default: `testops.yaml` or `testops.yml`)
- `--last N`: Only analyze the last N runs
- `--fail-under-health SCORE`: Exit with error if health score is below this

### Config file

Create `testops.yaml` in your project root:

```yaml
runs_path: ./test-results
analysis:
  flaky_threshold: 0.3
  slow_test_threshold_sec: 2.0
  last_n_runs: 20
report:
  output_dir: ./report
  suite_name: Production Tests
```

Then just run:

```bash
testops-insights analyze
```

It uses the config file automatically.

### Examples

Analyze sample data:

```bash
testops-insights analyze --runs-path ./sample-data/runs --out ./report
```

Use config file:

```bash
testops-insights analyze
```

Only last 5 runs:

```bash
testops-insights analyze --runs-path ./test-results --last 5
```

Fail build if health below 70:

```bash
testops-insights analyze --runs-path ./test-results --fail-under-health 70
```

Custom name:

```bash
testops-insights analyze --runs-path ./test-results --out ./report --name "CI Pipeline"
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Test Analysis

on:
  push:
    branches: [main]
  pull_request:

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.8"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .

      - name: Run tests and collect results
        run: |
          pytest --junitxml=test-results/run_$(date +%s)/junit.xml

      - name: Analyze test results
        run: |
          testops-insights analyze --runs-path ./test-results --out ./report

      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: testops-report
          path: report/

      - name: Check health score
        run: |
          testops-insights analyze --runs-path ./test-results --fail-under-health 70
```

### Jenkins

```groovy
pipeline {
    agent any

    stages {
        stage('Test') {
            steps {
                sh 'pytest --junitxml=test-results/run_${BUILD_NUMBER}/junit.xml'
            }
        }

        stage('Analyze') {
            steps {
                sh '''
                    pip install -r requirements.txt
                    pip install -e .
                    testops-insights analyze --runs-path ./test-results --out ./report
                '''
            }
        }

        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'report/**', fingerprint: true
                publishHTML([
                    reportDir: 'report',
                    reportFiles: 'index.html',
                    reportName: 'TestOps Dashboard'
                ])
            }
        }

        stage('Quality Gate') {
            steps {
                sh 'testops-insights analyze --runs-path ./test-results --fail-under-health 70'
            }
        }
    }
}
```

## Output

The tool creates a report folder:

```
report/
  index.html          # Dashboard
  metrics.json        # Metrics in JSON
  assets/             # CSS and other files
```

## Project Structure

```
testops_insight/
  ingestion/        # JUnit XML parsing
  domain/           # Models (TestCase, TestRun, TestSuite)
  analytics/        # Analysis functions
  reporting/        # HTML generation
  cli/              # Command line interface
tests/              # Tests
sample-data/        # Sample data
```

## Dashboard

The dashboard shows:

1. **Summary**: Pass rate, flaky count, failing count, average duration
2. **Health score**: Overall score (0-100) with explanation
3. **Flaky tests**: Tests that pass and fail inconsistently
4. **Failing tests**: Tests that fail frequently
5. **Slow tests**: Performance issues
6. **Trends**: How pass rate and duration change over time

<p align="center">
  <img src="docs/images/dashboard-summary.png" alt="Executive Summary and Health Score" width="800">
</p>

<p align="center">
  <img src="docs/images/dashboard-details.png" alt="Flaky Tests and Failures" width="800">
</p>

## Running Tests

```bash
pytest tests/
```

Verbose output:

```bash
python -m pytest tests/ -v
```

## Architecture

- **Ingestion**: Parses JUnit XML into structured data
- **Domain**: Core models (TestCase, TestRun, TestSuite)
- **Analytics**: Pure functions for analysis (flaky detection, health score, etc.)
- **Reporting**: Generates HTML dashboard
- **CLI**: Command-line interface for CI/CD

Modules are independent. Analytics are pure functions with no side effects.

## Requirements

- Python 3.8+
- pytest
- pyyaml

## License

This project is part of a TestOps demonstration and is designed to showcase best practices in test operations and pipeline health monitoring.
