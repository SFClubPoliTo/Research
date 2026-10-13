from barrick_unified.project import _operational_artifacts


def test_artifact_scan_preserves_non_output_findings(tmp_path):
    for relative in ['a/run.log', 'b/cache.pyc', 'b/article.aux',
                     'outputs/run.log', 'a/outputs/article.toc', 'a/input.csv']:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('fixture', encoding='utf-8')
    assert _operational_artifacts(tmp_path) == [
        'a/run.log', 'b/article.aux', 'b/cache.pyc']
