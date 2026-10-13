"""Compute article figures and audit them against immutable manuscript assets."""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys

import matplotlib
import numpy as np
from PIL import Image
from layout import ROOT, DATA, OUTPUTS, FIGURES

EXCEPTIONS = {
    'hft1-py3.png': 'Historical representative-path seed 42 was recovered by comparison with the received raster and restored. Monte Carlo seed 3000 and all published parameters are preserved; the reconstructed renderer has minor raster geometry differences, with the same data, four panels and palette.',
    'hft1-Corr.png': 'Correlation entries and coolwarm scale are exact; original PDF raster extraction has different bounding-box geometry. The numerical renderer preserves labels and colors.',
    'hft2-img_4.png': 'Original convergence random stream is unavailable. Replay uses seed 123, the historical grid sizes and variance diagnostic, with the same one-panel log-log layout and blue/orange palette.',
    'hft2-img_5.png': 'Original convergence random stream is unavailable. Replay uses seed 123, historical sample sizes and covariance diagnostic, with the same one-panel log-log layout and blue/orange palette.',
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def publication_figures():
    project = DATA / 'processed/manuscript_authoring'
    text = '\n'.join(path.read_text(encoding='utf-8') for path in (project / 'chapters').glob('*.tex'))
    return [project / name for name in sorted(set(re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', text)))]


def computed_path(name):
    family, filename = name.split('-', 1)
    if family == 'hft1':
        return FIGURES / family / filename
    if family == 'hft3':
        return FIGURES / family / filename
    folder = '2' if filename.startswith('hjb_') else 'generated'
    if filename.startswith(('fgm', 'ML', 'iterative', 'volterra')):
        filename = filename.replace('_', '.')
    return FIGURES / family / folder / filename


def audit():
    rows = []
    for reference in publication_figures():
        computed = computed_path(reference.name)
        if not computed.exists():
            raise FileNotFoundError(f'Run the figure computations first: {computed}')
        with Image.open(reference) as original, Image.open(computed) as replay:
            exact = original.size == replay.size and original.convert('RGB').tobytes() == replay.convert('RGB').tobytes()
            sizes = {'reference_size': list(original.size), 'replay_size': list(replay.size)}
        if not exact and reference.name not in EXCEPTIONS:
            raise RuntimeError('Unexpected article figure mismatch: ' + reference.name)
        rows.append({'figure': reference.name, 'reference': reference.relative_to(ROOT).as_posix(),
                     'computed': computed.relative_to(ROOT).as_posix(),
                     'reference_sha256': sha256(reference), 'computed_sha256': sha256(computed),
                     'pixels_identical': exact, **sizes,
                     'qualification': 'Same numerical run and rendered pixels' if exact else EXCEPTIONS[reference.name]})
    result = {'scientific_figures': len(rows), 'exact_computed_figures': sum(row['pixels_identical'] for row in rows),
              'qualified_historical_rerenders': sum(not row['pixels_identical'] for row in rows),
              'publication_assets': 'Immutable original PNGs; historical rerenders do not replace manuscript figures',
              'environment': {'python': platform.python_version(), 'numpy': np.__version__, 'matplotlib': matplotlib.__version__},
              'rows': rows}
    out = DATA / 'processed/provenance/article-figure-replay.json'
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ['scientific_figures', 'exact_computed_figures', 'qualified_historical_rerenders']}, indent=2))
    return result


def restore():
    destination = FIGURES / 'overleaf'
    destination.mkdir(parents=True, exist_ok=True)
    for path in publication_figures():
        shutil.copy2(path, destination / path.name)
        assert sha256(path) == sha256(destination / path.name)
    print('Original Overleaf scientific assets exported byte for byte to ' + str(destination))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['compute', 'audit', 'restore'])
    args = parser.parse_args()
    if args.action == 'restore':
        restore()
        return
    if args.action == 'compute':
        for stage in ['classic', 'rough-figures', 'rough-hjb', 'temporal-figures', 'market', 'multiasset']:
            subprocess.run([sys.executable, '-B', str(ROOT / 'src/main.py'), 'run', stage], cwd=ROOT, check=True)
    audit()


if __name__ == '__main__':
    main()
