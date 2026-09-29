# Machine Learning vs Factor Models: Predicting S&P 500 Stock Returns (2010–2026)

MSc Finance dissertation, Dublin City University (2026)
**Author:** Kalpana Tripathi · [LinkedIn](https://www.linkedin.com/in/kalpana-tripathi/)

> **Research question:** Do machine learning models outperform traditional asset pricing models (CAPM, Fama-French 3-factor and 5-factor) in predicting stock returns?

This repository contains the full Python research pipeline: data cleaning, feature engineering, model training, and statistical and economic evaluation.

---

## At a glance

| | |
|---|---|
| **Universe** | 503 S&P 500 constituents, daily data, Jan 2010 – Jun 2026 |
| **Benchmarks** | CAPM, Fama-French 3-factor, Fama-French 5-factor (rolling 60-month OLS) |
| **ML models** | LASSO, Random Forest, SVM (linear / RBF / polynomial), MLP |
| **Features** | 13 stock characteristics (momentum, reversal, volatility, liquidity, intraday returns) |
| **Evaluation** | Out-of-sample R², Diebold-Mariano tests, Spearman rank IC, portfolio Sharpe ratios and alpha |
| **Stack** | Python, pandas, NumPy, scikit-learn, Jupyter |

---

## Key findings

| Measure | Machine learning | Factor models |
|---|---|---|
| Out-of-sample R² | around +1.2% (LASSO, RF, SVM) | −0.5% to −9.9% |
| Best portfolio Sharpe ratio | 0.59 (LASSO) | 0.74 (CAPM), 0.73 (FF3) |
| Significant alpha | No | Yes (CAPM, FF3) |

- **ML wins statistically:** ML forecasts are significantly more accurate out of sample (Diebold-Mariano tests).
- **Factor models win economically:** better forecast accuracy did not translate into better portfolios. Factor-model portfolios delivered higher Sharpe ratios and significant alpha.
- **ML results are fragile:** adding a single feature moved individual ML portfolio Sharpe ratios by 0.3–0.4, so feature choice matters a lot.
- **Contrast with the literature:** results differ from Gu, Kelly & Xiu (2020). A likely explanation is the shorter, more recent test window and narrower universe.

The gap between statistical accuracy and tradable performance is the central takeaway of this project.

---

## Data

| Source | Content |
|---|---|
| Bloomberg | Daily OHLCV and total-return data for S&P 500 constituents |
| Kenneth French Data Library | Fama-French factors |

**Bloomberg data is not included in this repository** because its licence does not allow redistribution. The code expects the data in the format described in `config.py`. Fama-French factors are freely available from the [Kenneth French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html).

### Data quality work

- **Pre-listing price history:** 84 stocks that listed after 2010 had price history before their real first trading day. A listing-date table (`listing_dates.py`) trims each stock to its true first trading day.
- **Survivorship bias:** the universe uses current constituents. A 421-stock balanced panel with continuous history is used as a robustness check, and the limitation is discussed openly below.
- **No look-ahead bias:** features are computed per stock using only information available at each point in time.

---

## Methodology

### Sample split
| Period | Use |
|---|---|
| 2010 – 2015 | Training |
| 2016 – 2018 | Validation (hyperparameter tuning) |
| 2019 – Jun 2026 | Out-of-sample test |

The test period is also analysed across three market regimes: pre-COVID (Jan 2019 – Feb 2020), COVID (Mar 2020 – Dec 2021), and post-COVID (Jan 2022 – Jun 2026).

### Features
- **Set A (10 features):** 12-1 and 6-1 month momentum, 1-month reversal, 21-day and 252-day volatility, 252-day beta, idiosyncratic volatility, Amihud illiquidity, maximum daily return, turnover
- **Set B (13 features):** Set A plus overnight, intraday, and open-to-open returns

### Design choices
- **Tuning on Spearman rank IC instead of MSE.** For cross-sectional return prediction, ranking stocks correctly matters more than predicting exact returns. Tuning on MSE caused LASSO to collapse to a constant prediction.
- **Out-of-sample R² against a zero benchmark,** following Gu, Kelly & Xiu (2020), rather than the historical mean.

---

## Repository structure

```
ml-vs-factor-models-sp500/
├── README.md
├── requirements.txt
├── config.py                   # paths, dates, and parameters
├── listing_dates.py            # true first trading days for post-2010 listings
├── panel_diagnostic.py         # checks on panel coverage and data quality
├── 01_build_panel.py           # load, clean, and align the daily stock panel
├── 02_factor_data.py           # load and align Fama-French factors
├── 03_features.py              # engineer the 13 stock characteristics
├── 04_traditional_models.py    # rolling CAPM, FF3, FF5 forecasts
├── 05_ml_models.py             # train, tune, and predict with LASSO, RF, SVM, MLP
├── 06_evaluate.py              # OOS R², Diebold-Mariano, rank IC, portfolios, alpha
├── 07_turnover_net_sharpe.py   # portfolio turnover and Sharpe ratios after costs
└── results/                    # summary tables and charts (no raw data)
```

## How to run

```bash
pip install -r requirements.txt
```

1. Place the Bloomberg data files in the location set in `config.py`
2. Run the scripts in numbered order, `01` to `07`. In Jupyter: `%run 01_build_panel.py`, and so on
3. Restart the Jupyter kernel after changing `config.py`

---

## Limitations and ongoing work

This is active research, and some parts are being revised:

- **Current constituents only:** using today's S&P 500 members introduces survivorship bias. The balanced panel is a robustness check, not a full fix. Point-in-time constituent data would be the proper solution.
- **Static ML vs rolling factor models:** ML models are trained once, while factor models re-estimate monthly. A periodic-retraining robustness test is in progress.
- **Factor model forecasts** use realised factor values in the forecast month, so they act as a conditional benchmark. This design is being revised.

Results may change as these revisions are completed.

---

## Contact

Happy to discuss the methodology or results: [LinkedIn](https://www.linkedin.com/in/kalpana-tripathi/)
