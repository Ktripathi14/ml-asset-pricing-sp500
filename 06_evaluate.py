"""
STEP 6 -- Evaluation comparing traditional models + ML Set A + ML Set B.
Reads: results/pred_traditional.parquet, results/pred_ml_A.parquet, results/pred_ml_B.parquet
Writes: results/metrics.csv, dm_tests.csv, portfolio_stats.csv, figures.
The A-vs-B comparison shows whether overnight/intraday features (Set B) add value.
"""
import pandas as pd, numpy as np, statsmodels.api as sm
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.stats import norm
import config

def oos_r2(y,p): return 1-np.sum((y-p)**2)/np.sum(y**2)
def rmse(y,p):   return np.sqrt(np.mean((y-p)**2))
def mae(y,p):    return np.mean(np.abs(y-p))

def load_all():
    trad=pd.read_parquet(config.RESULT_DIR/"pred_traditional.parquet")
    frames={"trad":trad}
    for s in ["A","B"]:
        f=config.RESULT_DIR/f"pred_ml_{s}.parquet"
        if f.exists():
            ml=pd.read_parquet(f).rename(columns={c:f"{c}_{s}" for c in ["pred_LASSO","pred_RF","pred_SVM","pred_NN"]})
            frames[s]=ml
    df=trad
    for s in ["A","B"]:
        if s in frames: df=df.merge(frames[s].drop(columns=["y_true"]),on=["Date","Ticker"],how="inner")
    return df

def main():
    df=load_all()
    preds=[c for c in df.columns if c.startswith("pred_")]

    # statistical metrics: full test + sub-periods
    rows=[]; spans={"full_test":config.TEST, **config.SUBPERIODS}
    for name,(lo,hi) in spans.items():
        sub=df[(df.Date>=lo)&(df.Date<=hi)]
        for c in preds:
            y,p=sub["y_true"].values, sub[c].values
            rows.append([name,c.replace("pred_",""),oos_r2(y,p),rmse(y,p),mae(y,p),len(sub)])
    pd.DataFrame(rows,columns=["period","model","OOS_R2","RMSE","MAE","n"]).to_csv(config.RESULT_DIR/"metrics.csv",index=False)

    # long-short portfolios
    fac=pd.read_parquet(config.CLEAN_DIR/"factors_m.parquet"); ps=[]
    for c in preds:
        rets={}
        for t,gm in df.groupby("Date"):
            gm=gm.dropna(subset=[c])
            if len(gm)<20: continue
            d=gm.assign(dec=pd.qcut(gm[c],10,labels=False,duplicates="drop"))
            rets[t]=d[d.dec==d.dec.max()]["y_true"].mean()-d[d.dec==d.dec.min()]["y_true"].mean()
        pr=pd.Series(rets).sort_index()
        if len(pr)<5: continue
        sharpe=np.sqrt(12)*pr.mean()/pr.std()
        al=pr.to_frame("r").join(fac).dropna()
        ff=sm.OLS(al["r"],sm.add_constant(al[["Mkt_RF","SMB","HML","RMW","CMA"]])).fit()
        ps.append([c.replace("pred_",""),pr.mean()*12,sharpe,ff.params["const"]*12,ff.tvalues["const"]])
    pd.DataFrame(ps,columns=["model","ann_ret","Sharpe","FF5_alpha_ann","alpha_t"]).to_csv(config.RESULT_DIR/"portfolio_stats.csv",index=False)

    # Diebold-Mariano vs FF5
    dm=[]
    for c in preds:
        if c=="pred_FF5": continue
        d=(df["y_true"]-df[c])**2-(df["y_true"]-df["pred_FF5"])**2
        stat=d.mean()/np.sqrt(np.var(d,ddof=0)/len(d))
        dm.append([c.replace("pred_",""),"vs FF5",stat,2*(1-norm.cdf(abs(stat)))])
    pd.DataFrame(dm,columns=["model","benchmark","DM_stat","p_value"]).to_csv(config.RESULT_DIR/"dm_tests.csv",index=False)

    met=pd.read_csv(config.RESULT_DIR/"metrics.csv")
    piv=met[met.period=="full_test"].set_index("model")["OOS_R2"]
    piv.plot(kind="bar",title="Out-of-sample R² (full test)").figure.savefig(config.RESULT_DIR/"fig_oos_r2.png",bbox_inches="tight"); plt.close()
    print("=== OOS R2 (full test) ===\n", piv.round(4).to_string())
    print("\nsaved: metrics.csv, dm_tests.csv, portfolio_stats.csv, fig_oos_r2.png")

if __name__=="__main__":
    main()
