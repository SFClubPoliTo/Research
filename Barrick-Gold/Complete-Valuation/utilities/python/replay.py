from pathlib import Path
import sys,json
R = next(p for p in Path(__file__).resolve().parents if (p/'pyproject.toml').is_file());sys.path.insert(0,str(R/'utilities/python'))
from barrick_unified.multimodel_valuation import run_multimodel_valuation
c=json.loads((R/'data/processed/config/multimodel_valuation_20260902_team8_refresh.json').read_text())
r=run_multimodel_valuation(R,c)
print([(m,x.valuation.value_per_share_proxy_usd.mean()) for m,x in r.models.items()])
