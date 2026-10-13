"""Create a self-contained Overleaf archive from one shared report edition.

Archive copies are delivery artifacts; the source figures remain canonical in
outputs/img/publication. Build by-products and executable/data files are excluded.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file())


def package(edition):
    report = ROOT/f'outputs/report_{edition}'
    files = {}
    figures = set()
    pattern = re.compile(r'\.\./img/publication/([^{}]+)')
    for source in sorted(report.rglob('*')):
        if not source.is_file() or source.suffix.lower() not in ['.tex', '.bib', '.cls', '.sty', '.pdf']:
            continue
        relative = source.relative_to(report).as_posix()
        content = source.read_bytes()
        if source.suffix == '.tex':
            text = content.decode('utf-8')
            figures.update(pattern.findall(text))
            content = pattern.sub(lambda match: 'img/'+match.group(1), text).encode('utf-8')
        files[relative] = content
    for name in sorted(figures):
        source = (ROOT/'outputs/img/publication'/name).resolve()
        if not source.is_relative_to((ROOT/'outputs/img/publication').resolve()):
            raise ValueError('image path escapes shared figure directory')
        files['img/'+name] = source.read_bytes()
    archive = report/'Articolo.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as stream:
        for name, content in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 7, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            stream.writestr(info, content)
    ledger = dict(edition=edition, archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                  file_count=len(files), shared_images=len(figures),
                  files=[dict(path=name, sha256=hashlib.sha256(content).hexdigest())
                         for name, content in sorted(files.items())])
    (ROOT/f'data/processed/provenance/report_{edition}_package.json').write_text(
        json.dumps(ledger, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in ledger.items() if key != 'files'}))
    return archive


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('edition', choices=['unificato', 'paper'])
    package(parser.parse_args().edition)
