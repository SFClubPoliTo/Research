"""Compile from Overleaf only; deliver complete portable source projects."""
from pathlib import Path
import argparse
import shutil
import subprocess
import zipfile
import json
import hashlib
import re
from layout import ROOT, OUTPUTS


def copy_sources(source,destination):
    for path in source.rglob('*'):
        if path.is_file() and path.suffix not in {'.aux','.log','.out','.toc','.zip','.pdf'}:
            target=destination/path.relative_to(source)
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(path,target)
        elif path.is_file() and path.name=='Copertina_research.pdf':
            shutil.copy2(path,destination/path.name)


def dependencies(folder):
    pending=[Path('Articolo.tex')]
    visited=set()
    while pending:
        relative=pending.pop()
        if relative in visited:continue
        visited.add(relative)
        path=folder/relative
        if not path.exists():raise FileNotFoundError(path)
        if path.suffix!='.tex':continue
        text=path.read_text(encoding='utf-8')
        text=re.sub(r'(?<!\\)%[^\n]*','',text)
        for match in re.finditer(r'\\(?:input|include|includegraphics|includepdf)(?:\[[^\]]*\])?\{([^}]+)\}',text):
            if '#' in match[1]:continue  # Parameter inside a macro definition, not a concrete file.
            item=Path(match[1])
            if not item.suffix:item=item.with_suffix('.tex')
            if item.is_absolute() or '..' in item.parts:raise ValueError('Nonportable report dependency '+str(item))
            pending.append(item)
    return visited


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('edition',choices=['unificato','paper','all'])
    parser.add_argument('--sync-only',action='store_true')
    args=parser.parse_args()
    workspace=ROOT
    result=[]
    for edition in ['unificato','paper'] if args.edition=='all' else [args.edition]:
        canonical=OUTPUTS/f'report_{edition}'
        overleaf=canonical
        overleaf.mkdir(parents=True,exist_ok=True)
        # Sources already exported into their self-contained report directory.
        if args.sync_only:continue
        build=OUTPUTS/'build/latex'/edition
        build.mkdir(parents=True,exist_ok=True)
        for iteration in range(3):
            process=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-output-directory='+str(build),'Articolo.tex'],cwd=overleaf,capture_output=True,text=True,encoding='utf-8',errors='replace')
            (build/f'pass-{iteration+1}.txt').write_text(process.stdout+process.stderr,encoding='utf-8')
            if process.returncode:
                print(process.stdout[-2400:]+process.stderr[-500:]);raise SystemExit(process.returncode)
        pdf=build/'Articolo.pdf'
        shutil.copy2(pdf,canonical/'Articolo.pdf')
        drive=canonical
        drive.mkdir(parents=True,exist_ok=True)
        # PDF has been copied once to canonical above.
        zip_path=drive/'Articolo.zip'
        pending_zip=build/'Articolo.zip'
        with zipfile.ZipFile(pending_zip,'w',zipfile.ZIP_DEFLATED) as archive:
            for relative in sorted(dependencies(overleaf)):
                archive.write(overleaf/relative,relative.as_posix())
        shutil.copy2(pending_zip,zip_path)
        # ZIP already resides in canonical.
        log=(build/'Articolo.log').read_text(encoding='utf-8',errors='replace')
        result.append({'edition':edition,'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'zip_files':len(zipfile.ZipFile(zip_path).namelist()),'undefined':bool('undefined' in log),'overfull':log.count('Overfull')})
    if result:
        (ROOT/'data/processed/provenance/report-delivery.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
