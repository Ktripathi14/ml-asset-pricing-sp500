"""
STEP 1 -- Clean raw stock CSVs into one panel of daily total returns.
Now also keeps Open and computes daily overnight & intraday returns (for Set B features).
In :  data/stocks/*.csv   Out: clean/panel_long.parquet, clean/coverage_report.csv
"""
import pandas as pd, numpy as np, glob, os
import config
from listing_dates import LISTING_DATES

EXPECTED = ["Date","Open","High","Low","Close","Volume"]

def load_one(path):
    tkr = os.path.splitext(os.path.basename(path))[0].upper()
    df = pd.read_csv(path, parse_dates=["Date"])
    if list(df.columns) != EXPECTED:
        raise ValueError(f"{tkr}: unexpected columns {list(df.columns)}")
    df = df.sort_values("Date").drop_duplicates("Date")
    df = df[(df.Date>=config.START)&(df.Date<=config.END)]
    if tkr in LISTING_DATES:
        df = df[df.Date >= pd.Timestamp(LISTING_DATES[tkr])]
    df["Ticker"]  = tkr
    df["Ret"]     = df.Close.pct_change()
    df["LogRet"]  = np.log(df.Close).diff()
    df["overnight"] = df.Open / df.Close.shift(1) - 1     # last close -> today open
    df["intraday"]  = df.Close / df.Open - 1              # today open -> today close
    df["open2open"] = df.Open / df.Open.shift(1) - 1      # yesterday open -> today open
    return df

def main():
    files = sorted(glob.glob(str(config.RAW_DIR/"*.csv")))
    if not files: raise SystemExit(f"No CSVs in {config.RAW_DIR}")
    frames, report = [], []
    for f in files:
        try:
            d = load_one(f); frames.append(d)
            report.append([d.Ticker.iloc[0], len(d), d.Date.min().date(), d.Date.max().date()])
        except Exception as e:
            report.append([os.path.basename(f), "ERROR", str(e), ""])
    panel = pd.concat(frames, ignore_index=True)
    long_panel = panel[["Date","Ticker","Open","Close","Volume","Ret","LogRet","overnight","intraday","open2open"]].dropna(subset=["Ret"])
    long_panel.to_parquet(config.CLEAN_DIR/"panel_long.parquet", index=False)
    pd.DataFrame(report,columns=["Ticker","Rows","Start","End"]).to_csv(config.CLEAN_DIR/"coverage_report.csv",index=False)
    print(f"Loaded {len(files)} files -> {len(long_panel):,} stock-day returns")
    print(f"Date range: {long_panel.Date.min().date()} -> {long_panel.Date.max().date()}")
    print("saved: clean/panel_long.parquet + clean/coverage_report.csv")

if __name__ == "__main__":
    main()
