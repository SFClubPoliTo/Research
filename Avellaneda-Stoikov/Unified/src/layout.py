"""One portable runtime layout; no dependency on local review utilities."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
OUTPUTS = ROOT / 'outputs'
FIGURES = OUTPUTS / 'img' / 'publication'


def output_dir(*parts):
    path = OUTPUTS.joinpath(*parts)
    path.mkdir(parents=True, exist_ok=True)
    return path
