"""Five small workflow notebooks dispatch shared implementations."""
from pathlib import Path
import nbformat
from layout import ROOT

STAGES=[('00_Overview','status'),('01_Classical_Market_Making','classic'),('02_Rough_State_and_HJB','rough-hjb'),('03_Lifted_HJB_and_Multiasset','multiasset'),('04_Validation_and_Reports','audit')]
for title,stage in STAGES:
    text='''from pathlib import Path
import sys
sys.dont_write_bytecode = True
import runpy
repo = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "src/main.py").exists())
sys.path.insert(0, str(repo / "src"))
sys.argv = ["main.py", "status"]
runpy.run_path(str(repo / "src/main.py"), run_name="__main__")
'''
    run='''# Enable explicitly to run the stage; numerical implementations remain in shared modules.
RUN_STAGE = False
if RUN_STAGE:
    sys.argv = ["main.py", "run", "'''+stage+'''"]
    runpy.run_path(str(repo / "src/main.py"), run_name="__main__")
'''
    notebook=nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell('# '+title.replace('_',' ')+'\n\nShared HFT research workflow. Default execution reports status; enable the stage cell for computations.'),nbformat.v4.new_code_cell(text),nbformat.v4.new_code_cell(run)],metadata={'kernelspec':{'name':'python3','display_name':'Python 3','language':'python'}})
    nbformat.write(notebook,ROOT/'src'/f'{title}.ipynb')
print('Five shared-stage notebooks generated')
