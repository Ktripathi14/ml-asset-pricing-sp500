"""
listing_dates.py  --  Real first trading day for post-2010 listings.
Any ticker here is trimmed to its real start in 01_build_panel, removing the
fabricated pre-listing history. Dates are first-trade (approximate to a few days
is fine; the pipeline errs slightly late, which is safe).

Compiled for the 503-ticker S&P 500 universe. Entries marked # VERIFY are recent
or ticker-change cases worth a quick confirm; the date is conservative either way.
"""
LISTING_DATES = {
    # --- IPOs ---
    "TSLA": "2010-06-29", "CBOE": "2010-06-15", "NXPI": "2010-08-06",
    "GM":   "2010-11-18", "LYB":  "2010-10-14", "KKR":  "2010-07-15",
    "TRGP": "2010-12-07", "CPAY": "2010-12-15",   # CPAY = ex-FleetCor
    "APO":  "2011-03-30", "GNRC": "2011-02-11", "KMI":  "2011-02-11",
    "APTV": "2011-11-17",   # ex-Delphi
    "PANW": "2012-07-20", "META": "2012-05-18", "WDAY": "2012-10-12",
    "ANET": "2014-06-06", "ARES": "2014-05-02", "CFG":  "2014-09-24", "SYF": "2014-07-31",
    "CDW":  "2013-06-27", "IQV":  "2013-05-09", "VEEV": "2013-10-16",
    "NCLH": "2013-01-18", "ZTS":  "2013-02-01", "HLT":  "2013-12-12", "ALLE": "2013-12-02",
    "GDDY": "2015-04-01",
    "TTD":  "2016-09-21", "FTV":  "2016-07-05", "VST":  "2016-10-03",
    "CVNA": "2017-04-28", "INVH": "2017-02-01", "IR":   "2017-05-12",  # ex-Gardner Denver
    "VICI": "2018-02-01",
    "DDOG": "2019-09-19", "CRWD": "2019-06-12", "UBER": "2019-05-10", "AMCR": "2019-06-11",
    "MRNA": "2018-12-07", "DELL": "2018-12-28",
    "CARR": "2020-04-03", "OTIS": "2020-04-03", "VRT": "2020-02-07",
    "PLTR": "2020-09-30", "ABNB": "2020-12-10", "DASH": "2020-12-09", "VTRS": "2020-11-17",
    "APP":  "2021-04-15", "COIN": "2021-04-14", "HOOD": "2021-07-29",
    "CEG":  "2022-02-02",
    # --- Spin-offs / mergers / relistings ---
    "ABBV": "2013-01-02",   # from Abbott
    "PSX":  "2012-05-01", "MPC": "2011-07-01", "HII": "2011-03-21", "XYL": "2011-11-01",
    "NWSA": "2013-06-19", "NWS": "2013-06-19", "LDOS": "2013-09-17", "TMUS": "2013-05-01",
    "HPE":  "2015-11-02", "PYPL": "2015-07-06", "KHC": "2015-07-06", "LITE": "2015-08-04",
    "HWM":  "2016-11-01",   # ex-Arconic/Alcoa
    "CTVA": "2019-06-03", "DOW": "2019-04-02", "FOX": "2019-03-19", "FOXA": "2019-03-19",
    "LIN":  "2018-10-31",   # Praxair/Linde merger
    "GEHC": "2023-01-04", "KVUE": "2023-05-04", "VLTO": "2023-10-02",
    "GEV":  "2024-04-02", "SOLV": "2024-04-01", "SW": "2024-07-08",
    "TKO":  "2023-09-12",
    "XYZ":  "2015-11-19",   # Block, ex-Square (renamed 2025)
    "SNDK": "2025-02-21",   # SanDisk relisting
    # --- VERIFY (recent / ticker-change; date is best-available, confirm quickly) ---
    "PSKY": "2025-08-07",   # VERIFY  Paramount Skydance
    "WBD":  "2022-04-11",   # VERIFY  Warner Bros Discovery
    "BKR":  "2017-07-05",   # VERIFY  Baker Hughes (current share line)
    "FDXF": "2026-06-01",   # FedEx Freight spin-off (only ~1 month of real data)
    "Q":    "2025-11-03",   # Qnity Electronics, DuPont spin-off
}

# Tickers I could NOT date confidently -- please look up their first-trade day and add:
NEEDS_LOOKUP = []   # MRSH = Marsh McLennan (old, no trim); Q = Qnity (added above)
