from pathlib import Path
from typing import Optional

from testops_insight.ingestion import parse_junit_xml
from testops_insight.domain.models import TestRun


def discover_test_runs(runs_path: Path, last_n: Optional[int] = None) -> list[tuple[Path, TestRun]]:
    runs_path = Path(runs_path)
    if not runs_path.exists():
        return []

    runs = []

    for run_dir in sorted(runs_path.iterdir()):
        if not run_dir.is_dir():
            continue

        junit_files = list(run_dir.glob("junit.xml"))
        if not junit_files:
            junit_files = list(run_dir.glob("*.xml"))

        for xml_file in junit_files:
            try:
                test_run = parse_junit_xml(xml_file)
                runs.append((xml_file, test_run))
                break
            except Exception:
                continue

    if last_n and len(runs) > last_n:
        runs = runs[-last_n:]

    return runs

