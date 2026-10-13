"""Replay audited Paper outputs; original dated fits are preserved."""
import os
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
from pathlib import Path
import argparse,subprocess,sys,hashlib,json
from barrick_unified.layout import migrated_path
R = next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file())
if '--copper' in sys.argv:
    remaining=[v for v in sys.argv[1:] if v != '--copper']
    command=[sys.executable,str(R/'src/run_copper_valuation.py'),
        '--calibration-dir',str(R/'data/processed/copper/snapshot_20260902'),
        '--gold-config',str(R/'data/processed/config/paper_copper_measure_audited_20261005.json'),
        '--oos-dir',str(R/'outputs/validation/copper_temporal_oos_budget112_20261003'),
        '--fixed-oos-dir',str(R/'outputs/validation/copper_fixed_origin_20261003'),*remaining]
    raise SystemExit(subprocess.call(command,cwd=R))
p=argparse.ArgumentParser();p.add_argument('--recalibrate',action='store_true');a=p.parse_args()
for row in json.loads((R/'data/processed/provenance/DATA_MANIFEST.json').read_text())['files']:
    assert hashlib.sha256((migrated_path(R,row['path'])).read_bytes()).hexdigest()==row['sha256'],row['path']
scripts=['audit.py']
if a.recalibrate:scripts+=['refine_hawkes.py']
scripts+=['build_audited_results.py','build_terminal_audit.py','numerical_sensitivity.py']
for script in scripts:subprocess.run([sys.executable,str(R/'src'/script)],check=True,cwd=R)
print('Audited operating-proxy outputs complete. This is not a corporate fair-value model.')
