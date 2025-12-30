from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class AnalysisConfig:
    flaky_threshold: float = 0.3
    slow_test_threshold_sec: float = 2.0
    last_n_runs: Optional[int] = None


@dataclass
class ReportConfig:
    output_dir: str = "./report"
    suite_name: str = "Test Suite"


@dataclass
class Config:
    runs_path: str = "./test-results"
    analysis: AnalysisConfig = None
    report: ReportConfig = None

    def __post_init__(self):
        if self.analysis is None:
            self.analysis = AnalysisConfig()
        if self.report is None:
            self.report = ReportConfig()


def load_config(config_path: Optional[Path] = None) -> Optional[Config]:
    if yaml is None:
        return None

    if config_path is None:
        config_path = Path("testops.yaml")
        if not config_path.exists():
            config_path = Path("testops.yml")
            if not config_path.exists():
                return None

    if not config_path.exists():
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        analysis_data = data.get("analysis", {})
        report_data = data.get("report", {})

        return Config(
            runs_path=data.get("runs_path", "./test-results"),
            analysis=AnalysisConfig(
                flaky_threshold=analysis_data.get("flaky_threshold", 0.3),
                slow_test_threshold_sec=analysis_data.get("slow_test_threshold_sec", 2.0),
                last_n_runs=analysis_data.get("last_n_runs"),
            ),
            report=ReportConfig(
                output_dir=report_data.get("output_dir", "./report"),
                suite_name=report_data.get("suite_name", "Test Suite"),
            ),
        )
    except Exception:
        return None

