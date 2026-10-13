"""Shared infrastructure paths for both report editions."""
from pathlib import Path


def project_root(start=None):
    origin=Path(start or __file__).resolve()
    for candidate in [origin,*origin.parents]:
        if (candidate/'pyproject.toml').is_file() and (candidate/'src/barrick_unified').is_dir():
            return candidate
    raise FileNotFoundError('Complete Valuation project root not found')


def migrated_path(root: Path, legacy_path: str) -> Path:
    """Resolve a frozen artifact path without rewriting its source manifest."""
    prefixes = {
        'utilities/reference/': 'data/raw/source_freezes/',
        'utilities/provenance/': 'data/processed/provenance/',
        'src/reference/': 'data/raw/source_freezes/',
        'utilities/python/': 'src/',
        'parity/sources/': 'data/raw/source_freezes/',
        'parity/inputs/': 'data/raw/reference/inputs/',
        'data/manifests/': 'data/processed/manifests/',
        'figures/': 'outputs/img/',
        'tables/': 'outputs/tables/',
        'team8_data/': 'data/raw/team8_freeze/',
        'audit_inputs/': 'data/processed/audit_inputs/',
        'audit_outputs/': 'outputs/paper_audit/',
        'config/': 'data/processed/config/',
    }
    value = legacy_path.replace('\\', '/')
    for old, new in prefixes.items():
        if value.startswith(old):
            value = new + value[len(old):]
            break
    return root / value
