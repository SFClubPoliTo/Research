"""Mirror canonical reports into an explicitly supplied local SF workspace.

The shared repository remains authoritative. No cloud or Git operation occurs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from package_report import ROOT, package


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--build-root', type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    if (workspace/'Github-Branch').resolve() != ROOT.resolve():
        parser.error('workspace must contain this canonical Github-Branch')
    ledger = json.loads((ROOT/'utilities/provenance/report_source_migration.json').read_text())
    deliveries = []
    for edition in ['unificato', 'paper']:
        report = ROOT/f'outputs/report_{edition}'
        build = args.build_root.resolve()/edition
        pdf = build/'Articolo.pdf'
        log = (build/'Articolo.log').read_text(errors='replace')
        if not pdf.is_file() or 'Output written on' not in log:
            raise ValueError(f'missing successful build: {edition}')
        if 'undefined' in log or 'Overfull' in log:
            raise ValueError(f'unresolved LaTeX diagnostics: {edition}')
        shutil.copy2(pdf, report/'Articolo.pdf')
        package(edition)
        mirror = workspace/'Overleaf'/edition
        mirror.mkdir(parents=True, exist_ok=True)
        images = [r for r in ledger['files'] if r['edition'] == edition and r['kind'] == 'image']
        for source in report.rglob('*'):
            if not source.is_file() or source.suffix.lower() not in ['.tex','.bib','.cls','.sty','.pdf']:
                continue
            target = mirror/source.relative_to(report)
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.suffix == '.tex':
                text = source.read_text(encoding='utf-8')
                for row in images:
                    text = text.replace('../img/publication/'+Path(row['destination']).name, row['source'])
                target.write_text(text, encoding='utf-8')
            else:
                shutil.copy2(source, target)
        for row in images:
            target = mirror/row['source']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT/row['destination'], target)
        shutil.copy2(mirror/'Articolo.tex', mirror/'articolo-revisionato.tex')
        shutil.copy2(mirror/'Articolo.pdf', mirror/'articolo-revisionato.pdf')
        delivery = workspace/'Drive'/edition
        delivery.mkdir(parents=True, exist_ok=True)
        for name in ['Articolo.pdf','Articolo.zip']:
            shutil.copy2(report/name, delivery/name)
            deliveries.append(dict(edition=edition, file=name,
                                   sha256=hashlib.sha256((delivery/name).read_bytes()).hexdigest()))
    (workspace/'Utilities-Progetto/REPORT-DELIVERY-LATEST.json').write_text(
        json.dumps(dict(publication_ready=False, files=deliveries), indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
