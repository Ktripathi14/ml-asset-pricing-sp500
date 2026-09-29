"""config.py -- all settings in one place."""
from pathlib import Path
from pandas import __version__ as _pv

BASE=Path(__file__).resolve().parent
RAW_DIR=BASE/"data"/"stocks"; FACTOR_DIR=BASE/"data"/"factors"
CLEAN_DIR=BASE/"clean"; RESULT_DIR=BASE/"results"
for d in (CLEAN_DIR,RESULT_DIR): d.mkdir(parents=True,exist_ok=True)

START="2010-01-01"; END="2026-06-30"
_mj,_mn=(int(x) for x in _pv.split(".")[:2]); FREQ="ME" if (_mj,_mn)>=(2,2) else "M"
TRAIN=("2010-01-01","2015-12-31"); VALID=("2016-01-01","2018-12-31"); TEST=("2019-01-01","2026-06-30")
SUBPERIODS={"pre_covid":("2019-01-01","2020-01-31"),"covid":("2020-02-01","2020-12-31"),"post_covid":("2021-01-01","2026-06-30")}
BETA_WINDOW=252; VOL_WINDOW=252; ROLL_OLS_WINDOW=60; WINSOR=0.01

# ---------- PANEL: "full" (all stocks) or "balanced" (only stocks with full history) ----------
PANEL="balanced"                 # set to "balanced" for the square-panel robustness run
BALANCED_START="2010-06-30"  # a stock must have data on/before this to enter the balanced panel

# ---------- FAST vs FULL grids ----------
# FAST = smaller grids for a quick run before a meeting. FULL = the complete search.
FAST=True

# LASSO penalty grid -- includes 0.01 and 0.1 (supervisor's suggestion) so the tuning
# TESTS them; the log will show they drop all features on this standardised data.
LASSO_ALPHAS=[1e-6,3e-6,1e-5,3e-5,1e-4,3e-4,1e-3,1e-2,1e-1]

if FAST:
    RF_GRID={"n_estimators":[300],"max_depth":[3,6],"max_features":["sqrt"]}
    SVM_SPECS=[
        {"kernel":"linear","C":[1],"epsilon":[0.1]},
        {"kernel":"rbf","C":[1,10],"gamma":["scale"],"epsilon":[0.1]},
        {"kernel":"poly","C":[1],"gamma":["scale"],"degree":[2],"epsilon":[0.1]},
    ]
    NN_GRID={"hidden_layer_sizes":[(32,),(32,16)],"alpha":[1e-3],"max_iter":[300]}
else:
    RF_GRID={"n_estimators":[500],"max_depth":[3,5,8],"max_features":["sqrt",0.33]}
    SVM_SPECS=[
        {"kernel":"linear","C":[0.1,1,10],"epsilon":[0.01,0.1]},
        {"kernel":"rbf","C":[0.1,1,10],"gamma":["scale",0.01],"epsilon":[0.01,0.1]},
        {"kernel":"poly","C":[1,10],"gamma":["scale"],"degree":[2,3],"epsilon":[0.1]},
    ]
    NN_GRID={"hidden_layer_sizes":[(32,),(32,16),(64,32,16)],"alpha":[1e-4,1e-3,1e-2],"max_iter":[500]}
