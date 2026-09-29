# ML vs Traditional Asset Pricing — Code Pipeline

Run the scripts **in number order**. Each reads the previous step's output and saves its own,
so if one fails you fix and re-run just that step. Run from a terminal (`python 01_build_panel.py`)
or in Jupyter (`%run 01_build_panel.py`).

## One-time setup
```
pip install -r requirements.txt
```
Folder layout (create `data/stocks` and `data/factors`):
```
proj/
  config.py            <- ALL settings live here; edit only this
  listing_dates.py     <- real first-trading-day for post-2010 IPOs (ABNB seeded)
  data/stocks/         <- put your 503 ticker CSVs here (AVY.csv, AAPL.csv, ...)
  data/factors/        <- put the Kenneth French CSVs here
  clean/               <- auto-filled intermediate files
  results/             <- auto-filled outputs (tables + figures)
```

## DOWNLOAD TONIGHT — Kenneth French Data Library (monthly CSV)
https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
1. **Fama/French 5 Factors (2x3)**  -> save as `data/factors/F-F_Research_Data_5_Factors_2x3.CSV`
2. (optional) **Momentum Factor (Mom)** -> `data/factors/F-F_Momentum_Factor.CSV`
Leave the files exactly as downloaded — step 2 strips the header/annual blocks itself.

## Run order
| # | Script | Does | Output |
|---|--------|------|--------|
| 1 | 01_build_panel.py | clean stock CSVs, total returns, trim phantom history | clean/panel_long.parquet, coverage_report.csv |
| 2 | 02_factor_data.py | load FF5 + RF, monthly, decimals | clean/factors_m.parquet |
| 3 | 03_features.py | build target + price/volume features + factors | clean/model_data.parquet |
| 4 | 04_traditional_models.py | CAPM/FF3/FF5 rolling OOS predictions | results/pred_traditional.parquet |
| 5 | 05_ml_models.py | LASSO/RF/SVM, tuned on validation | results/pred_ml.parquet |
| 6 | 06_evaluate.py | R²/RMSE/MAE, Diebold-Mariano, Sharpe, FF5 alpha, figures | results/*.csv, results/*.png |

## After step 1 — one manual check
Open `clean/coverage_report.csv`. Any stock that IPO'd after 2010 but still shows Start = 2010
has phantom history: add it to `listing_dates.py` and re-run step 1. (ABNB is already handled.)
I'm compiling the full post-2010 listing-date table from your ticker list separately.

## Design choices set in config.py (confirm with supervisor)
- Predict **monthly** excess returns (features from daily data). Daily return prediction is mostly noise.
- Split: train 2010–2015, validation 2016–2018, **test 2019–2026** — test window contains
  pre-COVID / COVID / post-COVID so the sub-period analysis is clean (fixes the proposal's clash).
- Features are **price/volume-based only** (your data is OHLCV; no fundamentals available).
