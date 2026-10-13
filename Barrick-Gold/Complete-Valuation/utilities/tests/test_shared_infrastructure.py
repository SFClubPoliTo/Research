"""Check shared entry points and standalone report delivery boundaries."""
import hashlib
import json
from pathlib import Path
import re
import zipfile

from barrick_unified.project import UnifiedWorkflow

ROOT = Path(__file__).resolve().parents[2]


def test_every_registered_stage_exists_in_shared_source_tree():
    for name, relative in UnifiedWorkflow.ENTRY_POINTS.items():
        assert relative.startswith('utilities/python/'), name
        assert (ROOT/relative).is_file(), name


def test_both_reports_resolve_shared_images_and_have_self_contained_archives():
    for edition in ['unificato', 'paper']:
        report = ROOT/f'outputs/report_{edition}'
        for tex in report.rglob('*.tex'):
            for name in re.findall(r'\.\./img/publication/([^{}]+)', tex.read_text(encoding='utf-8')):
                assert (ROOT/'outputs/img/publication'/name).is_file(), (tex, name)
        manifest = json.loads((ROOT/f'utilities/provenance/report_{edition}_package.json').read_text())
        archive = report/'Articolo.zip'
        assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256']
        with zipfile.ZipFile(archive) as stream:
            assert set(stream.namelist()) == {row['path'] for row in manifest['files']}
            for row in manifest['files']:
                content = stream.read(row['path'])
                assert hashlib.sha256(content).hexdigest() == row['sha256']
                assert row['path'].split('/')[0] not in ['src', 'data', 'utilities']
                if row['path'].endswith('.tex'):
                    assert b'../img/publication/' not in content
                    canonical=(report/row['path']).read_bytes().decode('utf-8')
                    expected=re.sub(r'\.\./img/publication/([^{}]+)',
                                    lambda match: 'img/'+match.group(1), canonical)
                    assert content == expected.encode('utf-8')
            assert stream.read('Articolo.pdf') == (report/'Articolo.pdf').read_bytes()
