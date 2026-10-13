"""Import both editions into the shared tree without changing article content.

Publication images are stored once, by content hash. Paths in TeX are the
only transformations; the source-to-destination hash ledger records them.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def migrate(source_root):
    assets = ROOT/'outputs/img/publication'
    assets.mkdir(parents=True, exist_ok=True)
    known = {digest(p): p for p in assets.iterdir() if p.is_file()}
    ledger = []
    for edition in ['unificato', 'paper']:
        source = source_root/edition
        target = ROOT/f'outputs/report_{edition}'
        target.mkdir(parents=True, exist_ok=True)
        replacements = {}
        for directory in ['img', 'figures']:
            for image in sorted((source/directory).rglob('*')):
                if not image.is_file():
                    continue
                sha = digest(image)
                if sha not in known:
                    destination = assets/f'{sha[:16]}_{image.name}'
                    shutil.copyfile(image, destination)
                    known[sha] = destination
                old = image.relative_to(source).as_posix()
                new = '../img/publication/'+known[sha].name
                replacements[old] = new
                ledger.append(dict(edition=edition, kind='image', source=old,
                                   destination=known[sha].relative_to(ROOT).as_posix(),
                                   source_sha256=sha, destination_sha256=sha))
        for file in sorted(source.rglob('*')):
            if not file.is_file() or file.parts[-2] in ['img', 'figures']:
                continue
            relative = file.relative_to(source)
            if relative.parts[0] in ['img', 'figures'] or file.stem == 'articolo-revisionato':
                continue
            if file.suffix.lower() not in ['.tex', '.bib', '.sty', '.cls', '.pdf']:
                continue
            destination = target/relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if file.suffix == '.tex':
                text = file.read_text(encoding='utf-8')
                for old in sorted(replacements, key=len, reverse=True):
                    text = text.replace('{'+old+'}', '{'+replacements[old]+'}')
                destination.write_text(text, encoding='utf-8')
            else:
                shutil.copyfile(file, destination)
            ledger.append(dict(edition=edition, kind='report', source=relative.as_posix(),
                               destination=destination.relative_to(ROOT).as_posix(),
                               source_sha256=digest(file), destination_sha256=digest(destination)))
    output = ROOT/'utilities/provenance/report_source_migration.json'
    output.write_text(json.dumps(dict(status='PATH_ONLY_MIGRATION_REQUIRES_COMPILE_PARITY',
                                      files=ledger), indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(report_records=sum(r['kind']=='report' for r in ledger),
                          image_references=sum(r['kind']=='image' for r in ledger),
                          unique_images=len(known))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_root', type=Path)
    migrate(parser.parse_args().source_root.resolve())
