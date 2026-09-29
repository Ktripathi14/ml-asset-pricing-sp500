"""
STEP 4 -- Traditional benchmarks: CAPM, FF3, FF5 as DIRECT out-of-sample predictors.
Run:  python 04_traditional_models.py
In :  clean/model_data.parquet
Out:  results/pred_traditional.parquet   (Date,Ticker,y_true, pred_CAPM,pred_FF3,pred_FF5)

Method (realised-factor, standard in ML-vs-factor comparisons):
  For each stock and each test month t, factor loadings (alpha + betas) are estimated
  by OLS on the trailing ROLL_OLS_WINDOW months (strictly before t). The predicted
  excess return for month t+1 is:  alpha + betas . F(t+1), where F(t+1) is the REALISED
  factor vector in the prediction month. Betas are estimated only on past data (no
  look-ahead in estimation); the realised-factor assumption is stated in the methodology.
"""
import pandas as pd, numpy as np, statsmodels.api as sm
import config

MODELS = {"CAPM":["Mkt_RF"], "FF3":["Mkt_RF","SMB","HML"], "FF5":["Mkt_RF","SMB","HML","RMW","CMA"]}
ALL_FACS = ["Mkt_RF","SMB","HML","RMW","CMA"]

def main():
    df = pd.read_parquet(config.CLEAN_DIR / "model_data.parquet").sort_values(["Ticker","Date"])
    test_lo, test_hi = pd.Timestamp(config.TEST[0]), pd.Timestamp(config.TEST[1])
    W = config.ROLL_OLS_WINDOW
    out = []
    for tkr, g in df.groupby("Ticker"):
        g = g.reset_index(drop=True)
        # realised factors of the NEXT month (the target month), aligned to each row
        Fnext = g[ALL_FACS].shift(-1)
        for i in range(len(g)):
            t = g.loc[i, "Date"]
            if not (test_lo <= t <= test_hi): continue
            if Fnext.iloc[i].isna().any(): continue          # no realised factors for target month
            hist = g.iloc[max(0, i-W):i]                     # strictly before t
            if len(hist) < max(24, W//2): continue
            y = hist["mret"] - hist["RF"]                    # contemporaneous excess returns
            row = {"Date": t, "Ticker": tkr, "y_true": g.loc[i, "y_excess_next"]}
            for name, facs in MODELS.items():
                X = sm.add_constant(hist[facs])
                b = sm.OLS(y, X, missing="drop").fit().params
                f_target = Fnext.iloc[i][facs]               # realised factors, prediction month
                row[f"pred_{name}"] = b.get("const", 0.0) + float((b[facs] * f_target).sum())
            out.append(row)
    res = pd.DataFrame(out)
    res.to_parquet(config.RESULT_DIR / "pred_traditional.parquet", index=False)
    print(f"traditional predictions: {len(res):,} rows")
    print("saved: results/pred_traditional.parquet")

if __name__ == "__main__":
    main()
