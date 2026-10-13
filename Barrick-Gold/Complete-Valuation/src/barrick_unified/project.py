"""Handoff-friendly orchestration for the unified Barrick research project.

Numerical logic remains in the focused domain modules.  This layer owns only
project discovery, structural validation and dispatch to the established
entry points, mirroring the thin ``main.py`` pattern used by Team 8.
"""

from __future__ import annotations

from dataclasses import dataclass
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Sequence


def _operational_artifacts(root: Path) -> list[str]:
    """Scan once, pruning generated outputs before descending into them."""
    suffixes = {".pyc", ".aux", ".log", ".out", ".toc"}
    found = []
    for directory, children, files in os.walk(root):
        children[:] = [name for name in children if name != "outputs"]
        for name in files:
            if Path(name).suffix.lower() in suffixes:
                found.append((Path(directory) / name).relative_to(root).as_posix())
    return sorted(found)


@dataclass(frozen=True)
class ProjectLayout:
    """Canonical, named paths used by people and automation."""

    root: Path

    @property
    def source(self) -> Path:
        return self.root / "src" / "barrick_unified"

    @property
    def data(self) -> Path:
        return self.root / "data"

    @property
    def figures(self) -> Path:
        return self.root / 'outputs/img'

    @property
    def tables(self) -> Path:
        return self.root / 'outputs/tables'

    @property
    def outputs(self) -> Path:
        return self.root / "outputs"

    @property
    def tests(self) -> Path:
        return self.root.parent / 'Utilities-Progetto/Development/tests'

    @property
    def table_index(self) -> Path:
        return self.tables / "publication_table_index.csv"

    def required_directories(self) -> dict[str, Path]:
        return {
            "source": self.source,
            "data": self.data,
            'figures': self.figures,
            'tables': self.tables,
            "outputs": self.outputs,
        }


class UnifiedWorkflow:
    """Small application facade for status checks and existing runners."""

    ENTRY_POINTS = {
        "gold-options-q": "src/tools/calibrate_ib_gold_models.py",
        "copper-options-q": "src/tools/calibrate_ib_copper_models.py",
        "copper-options-oos": "src/tools/run_copper_oos.py",
        "physical-history": "src/tools/fetch_ib_physical_history.py",
        "report-package": "src/tools/package_report.py",
        "gold-basis": "src/tools/audit_gold_physical_basis.py",
        "copper-history": "src/tools/build_copper_physical_history.py",
        "physical-gbm": "src/tools/fit_physical_gbm_diagnostic.py",
        "physical-candidates": "src/tools/fit_physical_candidates.py",
        "joint-density": "src/tools/audit_joint_density.py",
        "physical-refit": "src/tools/refit_physical_candidates.py",
        "physical-origins": "src/tools/recover_gold_origin_surfaces.py",
        "physical-heston-oos": "src/tools/validate_heston_physical_origins.py",
        "physical-gbm-oos": "src/tools/validate_gbm_physical_origins.py",
        "physical-origin-q": "src/tools/calibrate_physical_origin_q.py",
        "physical-origin-p": "src/tools/fit_physical_origin_p.py",
        "physical-oos-summary": "src/tools/summarize_physical_origin_runs.py",
        "physical-origin-gold": "src/tools/validate_origin_gold_basis.py",
        "physical-convergence": "src/tools/check_physical_filter_convergence.py",
        "gold-physical-oos": "src/tools/validate_gold_physical_baseline.py",
        "paper-audit": "src/paper_cli.py",
        "copper-valuation": "src/run_copper_valuation.py",
        "data-ib": 'src/tools/fetch_ib_gold_options.py',
        "data-lse": 'src/tools/fetch_lse_gold_options.py',
        "all-figures": "src/run_all_thesis_figures.py",
        "empirical-figures": "src/run_empirical_thesis_figures.py",
        "valuation": "src/run_multimodel_valuation.py",
        "provisional-valuation": "src/run_provisional_valuation.py",
        "refactored-figures": "src/run_refactored_thesis_figures.py",
        "snapshot": "src/run_research_snapshot.py",
    }

    def __init__(self, root: Path | None = None) -> None:
        discovered = root or next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file())
        self.layout = ProjectLayout(discovered.resolve())
        if not (self.layout.root / "pyproject.toml").is_file():
            raise ValueError(f"Not a Barrick unified project root: {self.layout.root}")

    def status(self) -> dict[str, Any]:
        """Return a deterministic, read-only handoff summary."""

        directories = self.layout.required_directories()
        missing = [name for name, path in directories.items() if not path.is_dir()]
        class_modules = sorted(
            path.relative_to(self.layout.root).as_posix()
            for path in (self.layout.source / "refactored").rglob("*.py")
            if path.name != "__init__.py"
        )
        notebooks = sorted(path.name for path in (self.layout.root / "src").glob("*.ipynb"))
        indexed_tables = 0
        broken_table_links: list[str] = []
        if self.layout.table_index.is_file():
            with self.layout.table_index.open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            indexed_tables = len(rows)
            broken_table_links = [
                row["authoritative_path"]
                for row in rows
                if not (self.layout.root / row["authoritative_path"]).is_file()
            ]
        operational_artifacts = _operational_artifacts(self.layout.root)
        ready = not missing and not broken_table_links and not operational_artifacts
        return {
            "status": "READY" if ready else "ATTENTION_REQUIRED",
            "readiness_scope": "repository structure only; not scientific or publication admission",
            "root": str(self.layout.root),
            "directories": {name: path.is_dir() for name, path in directories.items()},
            "class_modules": class_modules,
            "curated_notebooks": notebooks,
            "indexed_publication_tables": indexed_tables,
            "broken_table_links": broken_table_links,
            "operational_artifacts": operational_artifacts,
        }

    def run_tests(self, extra_args: Sequence[str] = ()) -> int:
        """Run the offline suite without leaving Python or pytest caches."""

        if not self.layout.tests.is_dir():
            raise FileNotFoundError('Development tests are local and are not part of the published repository.')
        environment = os.environ.copy()
        environment['BARRICK_TEST_ROOT'] = str(self.layout.root)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        command = [
            sys.executable,
            "-m",
            "pytest",
            str(self.layout.tests),
            "-p",
            "no:cacheprovider",
            *extra_args,
        ]
        return subprocess.run(
            command,
            cwd=self.layout.root,
            env=environment,
            check=False,
        ).returncode

    def run_entry_point(self, name: str, arguments: Sequence[str] = ()) -> int:
        """Dispatch to a named, existing runner without duplicating its logic."""

        try:
            script = self.ENTRY_POINTS[name]
        except KeyError as exc:
            allowed = ", ".join(sorted(self.ENTRY_POINTS))
            raise ValueError(f"Unknown entry point {name!r}; choose one of: {allowed}") from exc
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, script, *arguments],
            cwd=self.layout.root,
            env=environment,
            check=False,
        ).returncode

    def print_status(self) -> None:
        print(json.dumps(self.status(), indent=2, ensure_ascii=False))
