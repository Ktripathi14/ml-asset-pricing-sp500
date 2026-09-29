"""
STEP 2 -- Load Fama-French factors + risk-free rate, convert to monthly.
Run:  python 02_factor_data.py
In :  data/factors/F-F_Research_Data_5_Factors_2x3.CSV     (Kenneth French, monthly)
      data/factors/F-F_Momentum_Factor.CSV                 (optional, monthly)
Out:  clean/factors_m.parquet   (index=month-end, cols: Mkt_RF,SMB,HML,RMW,CMA,RF[,MOM] as decimals)

DOWNLOAD TONIGHT (Kenneth French Data Library, all as monthly CSV):
  * Fama/French 5 Factors (2x3)
  * (optional) Momentum Factor (Mom)
French's files are in PERCENT with a header block and an annual section lower down;
this script strips both and converts to decimals.
"""
import pandas as pd, numpy as np
import config

def _read_ff(path):
    # find the row where the real monthly table starts (first cell is a 6-digit YYYYMM)
    raw = open(path).read().splitlines()
    start = next(i for i,l in enumerate(raw) if l[:6].strip().isdigit() and len(l.split(",")[0].strip())==6)
    rows = []
    for l in raw[start:]:
        c0 = l.split(",")[0].strip()
        if not (c0.isdigit() and len(c0)==6):   # stop at blank line / annual section
            break
        rows.append(l)
    from io import StringIO
    df = pd.read_csv(StringIO("\n".join(rows)), header=None)
    df[0] = pd.to_datetime(df[0].astype(int).astype(str), format="%Y%m") + pd.offsets.MonthEnd(0)
    return df.set_index(0)

def main():
    ff5 = _read_ff(config.FACTOR_DIR / "F-F_Research_Data_5_Factors_2x3.CSV")
    ff5.columns = ["Mkt_RF","SMB","HML","RMW","CMA","RF"]
    ff5 = ff5 / 100.0                                   # percent -> decimal
    mom_path = config.FACTOR_DIR / "F-F_Momentum_Factor.CSV"
    if mom_path.exists():
        mom = _read_ff(mom_path); mom.columns = ["MOM"]; ff5 = ff5.join(mom/100.0)
    ff5 = ff5.loc[config.START:config.END]
    ff5.index.name = "Date"
    ff5.to_parquet(config.CLEAN_DIR / "factors_m.parquet")
    print("factors:", list(ff5.columns), "| months:", len(ff5),
          "|", ff5.index.min().date(), "->", ff5.index.max().date())
    print("saved: clean/factors_m.parquet")

if __name__ == "__main__":
    main()
