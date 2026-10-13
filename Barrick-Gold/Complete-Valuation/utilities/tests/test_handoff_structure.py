from __future__ import annotations

import csv
import json
from pathlib import Path

from barrick_unified.project import UnifiedWorkflow


ROOT = next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file())


def test_handoff_status_is_ready() -> None:
    status = UnifiedWorkflow(ROOT).status()
    assert status["status"] == "READY"
    assert all(status["directories"].values())
    assert status["curated_notebooks"] == sorted(p.name for p in (ROOT/'src').glob('*.ipynb'))
    assert len(status["curated_notebooks"]) == 5
    assert all(p.is_file() and p.suffix == '.ipynb' for p in (ROOT/'src').iterdir())
    assert status["indexed_publication_tables"] == 7
    assert status["broken_table_links"] == []
    assert status["operational_artifacts"] == []


def test_curated_notebook_is_thin_and_valid() -> None:
    notebook = json.loads((ROOT / "src/00_Overview.ipynb").read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4
    assert len(notebook["cells"]) == 4
    code = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    )
    assert "from barrick_unified.project import UnifiedWorkflow" in code
    assert "workflow.status()" in code


def test_publication_table_index_points_to_real_outputs() -> None:
    index_path = ROOT / 'outputs/tables' / "publication_table_index.csv"
    with index_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 7
    assert len({row["table_id"] for row in rows}) == len(rows)
    for row in rows:
        assert (ROOT / row["authoritative_path"]).is_file(), row
