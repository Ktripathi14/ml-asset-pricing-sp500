"""
Turnover + net-of-cost Sharpe for long-short decile portfolios.
Add to 06_evaluate.py (or run standalone after it, loading saved predictions).

INPUT CONTRACT — adapt the three column names at the top to match your
predictions DataFrame. It must be long-form with one row per
(rebalance date, ticker, model prediction):
    date | ticker | pred | fwd_ret
where fwd_ret is the realised next-period excess return used in your
existing long-short portfolio (same one 06_evaluate already uses).

Run once per model (pass each model's prediction column / frame).
"""

import numpy as np
import pandas as pd

DATE, TICKER, PRED, RET = "date", "ticker", "pred", "fwd_ret"

PERIODS_PER_YEAR = 12   # <-- set 12 if you rebalance monthly, 252 if daily
COSTS_BPS = [5, 10]     # one-way cost per trade, in basis points


def longshort_with_turnover(df, n_deciles=10):
    """Return per-period DataFrame: gross L/S return, turnover, decile members."""
    out = []
    prev_long, prev_short = None, None
    for date, g in df.sort_values(DATE).groupby(DATE):
        g = g.dropna(subset=[PRED, RET])
        if len(g) < n_deciles * 2:
            continue
        # decile sort on predictions (same convention as 06_evaluate)
        g = g.copy()
        g["dec"] = pd.qcut(g[PRED].rank(method="first"), n_deciles,
                           labels=False, duplicates="drop")
        long_names = set(g.loc[g["dec"] == g["dec"].max(), TICKER])
        short_names = set(g.loc[g["dec"] == g["dec"].min(), TICKER])
        gross = (g.loc[g[TICKER].isin(long_names), RET].mean()
                 - g.loc[g[TICKER].isin(short_names), RET].mean())

        # one-way turnover per leg = fraction of names replaced this rebalance
        if prev_long is None:
            to_long = to_short = 1.0  # initial full establishment
        else:
            to_long = 1 - len(long_names & prev_long) / max(len(long_names), 1)
            to_short = 1 - len(short_names & prev_short) / max(len(short_names), 1)
        prev_long, prev_short = long_names, short_names

        out.append({"date": date, "gross": gross,
                    "to_long": to_long, "to_short": to_short})
    return pd.DataFrame(out)


def net_sharpe_table(df, model_name, n_deciles=10):
    """Gross Sharpe, avg one-way turnover, net Sharpe at each cost level."""
    ls = longshort_with_turnover(df, n_deciles)
    ann = np.sqrt(PERIODS_PER_YEAR)
    res = {
        "model": model_name,
        "gross_sharpe": ls["gross"].mean() / ls["gross"].std() * ann,
        "avg_oneway_turnover_per_leg": ls[["to_long", "to_short"]].mean().mean(),
    }
    for bps in COSTS_BPS:
        c = bps / 1e4
        # traded notional per rebalance = 2 * turnover per leg (sell + buy),
        # summed over both legs; cost drag = c * total traded notional
        drag = c * 2 * (ls["to_long"] + ls["to_short"])
        net = ls["gross"] - drag
        res[f"net_sharpe_{bps}bps"] = net.mean() / net.std() * ann
    return res


# ---------------------------------------------------------------------------
# Example hook — adapt to however 06_evaluate stores predictions per model:
#
# rows = []
# for model_name, pred_df in all_model_predictions.items():
#     rows.append(net_sharpe_table(pred_df, model_name))
# result = pd.DataFrame(rows).round(3)
# result.to_csv("net_sharpe_turnover.csv", index=False)
# print(result)
# ---------------------------------------------------------------------------
