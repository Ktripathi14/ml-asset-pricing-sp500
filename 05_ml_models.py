"""
STEP 5 -- ML models: LASSO, Random Forest, SVM (linear/rbf/poly), Neural Network.
Runs TWO feature sets (A=10, B=12). Tunes hyperparameters on validation IC (ranking).
Logs EVERY parameter combination + its validation IC to results/tuning_log_{set}.csv,
and prints the CHOSEN parameters per model (answers "which parameters, what accuracy,
which combination is best").
Out: results/pred_ml_A.parquet, results/pred_ml_B.parquet, results/tuning_log_*.csv
"""
import pandas as pd, numpy as np, itertools
from sklearn.linear_model import Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from scipy.stats import spearmanr
import config

BASE=["mom_12_1","mom_6_1","rev_1m","vol_21d","vol_252d","beta_252d",
      "ivol_252d","amihud","maxret_21d","turn_21d"]
FEATURE_SETS={"A":BASE,"B":BASE+["overnight_m","intraday_m","open2open_m"]}

def sl(df,p): lo,hi=pd.Timestamp(p[0]),pd.Timestamp(p[1]); return df[(df.Date>=lo)&(df.Date<=hi)]
def gd(g): k=list(g); return [dict(zip(k,v)) for v in itertools.product(*[g[x] for x in k])]
def val_ic(m,v,F):
    v=v.copy(); v["_p"]=m.predict(v[F].values)
    ics=[spearmanr(x["_p"],x["y_excess_next"]).correlation for _,x in v.groupby("Date") if len(x)>10]
    ics=[z for z in ics if z==z]; return np.mean(ics) if ics else -np.inf

def candidates(kind):
    """Return list of (label, estimator) for a model type."""
    out=[]
    if kind=="LASSO":
        for a in config.LASSO_ALPHAS: out.append((f"alpha={a}", Lasso(alpha=a,max_iter=50000)))
    elif kind=="RF":
        for p in gd(config.RF_GRID): out.append((str(p), RandomForestRegressor(n_jobs=-1,random_state=0,**p)))
    elif kind=="SVM":
        for spec in config.SVM_SPECS:
            k=spec["kernel"]; grid={x:spec[x] for x in spec if x!="kernel"}
            for p in gd(grid): out.append((f"kernel={k},{p}", SVR(kernel=k,**p)))
    elif kind=="NN":
        for p in gd(config.NN_GRID):
            out.append((str(p), MLPRegressor(random_state=0,early_stopping=True,**p)))
    return out

def tune(kind,Xtr,ytr,vdf,F,log):
    best,bic,blabel=None,-np.inf,None
    for label,m in candidates(kind):
        m.fit(Xtr,ytr); ic=val_ic(m,vdf,F)
        log.append([kind,label,ic])
        if best is None or ic>bic: best,bic,blabel=m,ic,label
    return best,bic,blabel

def run_set(df,name,F):
    tr,va,te=sl(df,config.TRAIN),sl(df,config.VALID),sl(df,config.TEST)
    trva=pd.concat([tr,va])
    res=te[["Date","Ticker"]].copy(); res["y_true"]=te["y_excess_next"].values
    log=[]
    for kind in ["LASSO","RF","SVM","NN"]:
        m,ic,label=tune(kind,tr[F].values,tr["y_excess_next"].values,va,F,log)
        m.fit(trva[F].values,trva["y_excess_next"].values)
        res[f"pred_{kind}"]=m.predict(te[F].values)
        print(f"  [Set {name}] {kind:5} best IC={ic:+.4f}  params: {label}")
    pd.DataFrame(log,columns=["model","params","val_IC"]).to_csv(config.RESULT_DIR/f"tuning_log_{name}.csv",index=False)
    res.to_parquet(config.RESULT_DIR/f"pred_ml_{name}.parquet",index=False)
    print(f"  saved: pred_ml_{name}.parquet + tuning_log_{name}.csv")

def main():
    df=pd.read_parquet(config.CLEAN_DIR/"model_data.parquet")
    print(f"PANEL={config.PANEL} | FAST={config.FAST} | rows={len(df):,} | stocks={df.Ticker.nunique()}")
    for name,F in FEATURE_SETS.items():
        print(f"=== Feature Set {name} ({len(F)} features) ===")
        run_set(df,name,F)

if __name__=="__main__":
    main()
