"""
panel_diagnostic.py -- helps choose the balanced ('square') panel start date.
Reports, for each candidate start year, how many stocks have data from then to the end.
Run:  python panel_diagnostic.py
"""
import pandas as pd
import config

def main():
    p=pd.read_parquet(config.CLEAN_DIR/"panel_long.parquet")
    first=p.groupby("Ticker").Date.min()
    end=p.Date.max()
    print(f"Panel ends: {end.date()} | total stocks: {len(first)}")
    print("\nIf you require full history from START DATE -> END, stocks retained:")
    print(f'{"start":>12}{"stocks kept":>14}')
    for yr in range(2010,2024):
        thr=pd.Timestamp(f"{yr}-06-30")
        kept=(first<=thr).sum()
        print(f'{str(thr.date()):>12}{kept:>14}')
    print("\n'balanced' panel in config uses BALANCED_START =", config.BALANCED_START,
          f"-> {(first<=pd.Timestamp(config.BALANCED_START)).sum()} stocks")

if __name__=="__main__":
    main()
