import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "01_data_download.py",
    "02_data_preparation.py",
    "03_descriptive_analysis.py",
    "04_gold_regressions.py",
    "05_silver_regressions.py",
    "06_stylized_facts.py",
    "06b_ar_mean_models.py",
    "06c_arma_mean_models.py",
    "06d_arima_mean_models.py",
    "07_garch_estimation.py",
    "08_arfima_analysis.py",
    "09_regression_tables.py"
]


def main():
    parser = argparse.ArgumentParser(description="Run the full empirical pipeline.")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Do not download from Yahoo Finance; use the frozen data/raw/yahoo_raw_download.csv.",
    )
    args = parser.parse_args()

    src_dir = Path(__file__).resolve().parent

    for script in SCRIPTS:
        print(f"\n>>> Running {script}")
        cmd = [sys.executable, str(src_dir / script)]
        if script == "01_data_download.py" and args.offline:
            cmd.append("--offline")
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
