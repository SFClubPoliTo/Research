import argparse
import sys

from config import DATA_RAW_DIR, END_DATE, START_DATE, TICKERS

RAW_FILE = DATA_RAW_DIR / "yahoo_raw_download.csv"


def validate_download(raw) -> list:
    """Return a list of problems; an empty list means the download is usable."""
    if raw is None or raw.empty:
        return ["the download returned no rows"]
    if "Adj Close" not in raw.columns.get_level_values(0):
        return ["the download has no 'Adj Close' field"]

    problems = []
    adj_close = raw["Adj Close"]
    for name, ticker in TICKERS.items():
        if ticker not in adj_close.columns or adj_close[ticker].dropna().empty:
            problems.append(f"no data for {ticker} ({name})")
    return problems


def use_frozen_copy(reason: str):
    if not RAW_FILE.exists() or RAW_FILE.stat().st_size == 0:
        sys.exit(
            f"ERROR: {reason}, and no frozen raw file is available at {RAW_FILE}. "
            "Cannot continue."
        )
    print(f"WARNING: {reason}.")
    print(f"Using the frozen raw download already in the repository: {RAW_FILE}")
    print("The file is left unchanged; downstream results reproduce the preserved data.")


def main():
    parser = argparse.ArgumentParser(description="Download raw Yahoo Finance data.")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip the Yahoo Finance download and use the frozen data/raw/yahoo_raw_download.csv.",
    )
    args = parser.parse_args()

    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)

    if args.offline:
        use_frozen_copy("offline mode requested (--offline)")
        return

    try:
        import yfinance as yf

        raw = yf.download(
            list(TICKERS.values()),
            start=START_DATE,
            end=END_DATE,
            auto_adjust=False,
            progress=False,
        )
    except Exception as exc:
        use_frozen_copy(f"the Yahoo Finance download failed ({exc!r})")
        return

    problems = validate_download(raw)
    if problems:
        # Never overwrite the frozen file with an empty or incomplete download.
        use_frozen_copy("the Yahoo Finance download is empty or incomplete: " + "; ".join(problems))
        return

    print("Raw head:\n", raw.head())
    print("\nRaw columns:\n", raw.columns)

    raw.to_csv(RAW_FILE)


if __name__ == "__main__":
    main()
