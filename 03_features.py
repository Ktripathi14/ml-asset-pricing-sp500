"""
STEP 3 -- Build modelling table: monthly target + price/volume features + factors.
Adds two Set-B features: overnight_m and intraday_m (monthly averages of daily
overnight and intraday returns). Set A ignores them; Set B uses them (chosen in step 5).
In : clean/panel_long.parquet, clean/factors_m.parquet   Out: clean/model_data.parquet
"""
import pandas as pd, numpy as np
import config

def monthly_features(g):
    g = g.set_index("Date").sort_index()
    dret = g.Ret
    m = pd.DataFrame({"Close": g.Close.resample(config.FREQ).last(),
                      "Vol":   g.Volume.resample(config.FREQ).mean()})
    m["mret"]     = g.Close.resample(config.FREQ).last().pct_change()
    m["rev_1m"]   = m["mret"]
    m["mom_6_1"]  = m["mret"].shift(1).rolling(5).sum()
    m["mom_12_1"] = m["mret"].shift(1).rolling(11).sum()
    m["vol_21d"]  = dret.rolling(21).std().resample(config.FREQ).last()
    m["vol_252d"] = dret.rolling(config.VOL_WINDOW).std().resample(config.FREQ).last()
    m["maxret_21d"]= dret.rolling(21).max().resample(config.FREQ).last()
    dollar = (g.Close*g.Volume).replace(0,np.nan)
    m["amihud"]   = (dret.abs()/dollar).rolling(21).mean().resample(config.FREQ).last()
    m["turn_21d"] = np.log(g.Volume.rolling(21).mean()/g.Volume.rolling(252).mean()).resample(config.FREQ).last()
    # --- Set B extras: monthly average overnight & intraday return ---
    m["overnight_m"] = g.overnight.resample(config.FREQ).mean()
    m["intraday_m"]  = g.intraday.resample(config.FREQ).mean()
    m["open2open_m"] = g.open2open.resample(config.FREQ).mean()
    return m

def add_beta(g, mkt):
    g = g.set_index("Date").sort_index()
    d = pd.DataFrame({"r":g.Ret}).join(mkt, how="left").dropna()
    cov = d["r"].rolling(config.BETA_WINDOW).cov(d["Mkt_RF"])
    var = d["Mkt_RF"].rolling(config.BETA_WINDOW).var()
    beta = cov/var
    resid = d["r"] - beta*d["Mkt_RF"]
    ivol = resid.rolling(config.BETA_WINDOW).std()
    return pd.DataFrame({"beta_252d":beta.resample(config.FREQ).last(),
                         "ivol_252d":ivol.resample(config.FREQ).last()})

def main():
    panel = pd.read_parquet(config.CLEAN_DIR/"panel_long.parquet")
    fac   = pd.read_parquet(config.CLEAN_DIR/"factors_m.parquet")
    daily_mkt = panel.groupby("Date").Ret.mean().rename("Mkt_RF").to_frame()
    rows=[]
    for tkr,g in panel.groupby("Ticker"):
        f = monthly_features(g.copy()).join(add_beta(g.copy(), daily_mkt))
        f["Ticker"]=tkr; rows.append(f)
    feats = pd.concat(rows).reset_index().rename(columns={"index":"Date"})
    feats["Date"]=pd.to_datetime(feats["Date"])
    facr = fac.reset_index(); facr.columns=["Date"]+list(facr.columns[1:])
    feats = feats.merge(facr,on="Date",how="left").sort_values(["Ticker","Date"])
    feats["y_excess_next"] = feats.groupby("Ticker")["mret"].shift(-1) - feats["RF"]

    feat_cols = ["mom_12_1","mom_6_1","rev_1m","vol_21d","vol_252d","beta_252d",
                 "ivol_252d","amihud","maxret_21d","turn_21d","overnight_m","intraday_m","open2open_m"]
    def cs(s):
        lo,hi=s.quantile(config.WINSOR),s.quantile(1-config.WINSOR)
        s=s.clip(lo,hi); return (s-s.mean())/s.std()
    for c in feat_cols:
        feats[c]=feats.groupby("Date")[c].transform(cs)

    keep=["Date","Ticker","mret","y_excess_next","RF","Mkt_RF","SMB","HML","RMW","CMA"]+feat_cols
    model_data=feats[keep].dropna(subset=["y_excess_next"]+feat_cols)
    # --- balanced ("square") panel option: keep only stocks with full early history ---
    # NOTE: judge "full history" on the RAW panel (starts 2010), not model_data (starts ~2012
    # after the feature lookback), otherwise every stock is dropped.
    if getattr(config,"PANEL","full")=="balanced":
        raw_first=panel.groupby("Ticker").Date.min()
        keep_tk=raw_first[raw_first<=pd.Timestamp(config.BALANCED_START)].index
        model_data=model_data[model_data.Ticker.isin(keep_tk)]
        print(f"[balanced panel] kept {len(keep_tk)} stocks with raw history from <= {config.BALANCED_START}")
    model_data.to_parquet(config.CLEAN_DIR/"model_data.parquet",index=False)
    print(f"model_data: {model_data.shape[0]:,} rows x {model_data.shape[1]} cols")
    print("features (13):", feat_cols)
    print("saved: clean/model_data.parquet")

if __name__ == "__main__":
    main()
