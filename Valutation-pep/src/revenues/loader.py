from pathlib import Path
import numpy as np
import pandas as pd


def load_and_validate_d04(csv_path: str = "data/D04_ricavi_v1_G1.csv") -> pd.DataFrame:
  
  path = Path(csv_path)
  if not path.exists():
    raise FileNotFoundError(f"File non trovato: {path.resolve()}")

  df = pd.read_csv(path)

  df.columns = df.columns.str.strip().str.lower()

  required_cols = {"year", "revenues_reported", "revenues_adjusted"}
  if not required_cols.issubset(set(df.columns)):
    raise KeyError(
        f"D04 non rispetta il formato. Colonne minime richieste:"
        f" {required_cols}. Trovate: {df.columns.tolist()}"
    )

  df = df.sort_values("year").reset_index(drop=True)

  if len(df) < 10:
    raise ValueError(
        f"Serie storica insufficiente: richiesti almeno 10 anni, trovati"
        f" {len(df)}."
    )

  # Sez. 10.1 test: R_t > 0
  if (df["revenues_adjusted"] <= 0).any():
    raise ValueError(
        "Rilevati ricavi corretti <= 0. La specifica lognormale richiede R > 0."
    )

  return df


def compute_historical_statistics(df: pd.DataFrame) -> dict:
  
  # Sez. 10.1: x_k = log(R_k / R_{k-1}), sigma = sqrt(1/(n-1) * sum(x_k-mean)^2)
  
  r = df["revenues_adjusted"].to_numpy(dtype=float)
  years = df["year"].to_numpy()

  log_returns = np.log(r[1:] / r[:-1])
  n = len(log_returns)

  mean_log_ret = float(np.mean(log_returns))
  sigma_hat = float(np.std(log_returns, ddof=1))

  cagr = float((r[-1] / r[0]) ** (1.0 / (len(r) - 1)) - 1.0)

  # Z = (x - mean) / sigma
  residuals = (log_returns - mean_log_ret) / sigma_hat
  skew = float(np.mean(residuals**3))
  kurt = float(np.mean(residuals**4))  # Kurtosis grezza (3 per normale)
  jb_stat = float((n / 6.0) * (skew**2 + 0.25 * ((kurt - 3.0) ** 2)))

  return {
    "years": years,
    "revenues_adjusted": r,
    "log_returns": log_returns,
    "r0": float(r[-1]),  
    "base_year": int(years[-1]),
    "n_observations": n,
    "sigma_hat": sigma_hat,
    "mean_log_return": mean_log_ret,
    "cagr_historical": cagr,
    "residuals": residuals,
    "skewness": skew,
    "kurtosis": kurt,
    "jarque_bera_stat": jb_stat,
  }
