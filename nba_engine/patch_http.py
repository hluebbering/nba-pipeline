# nba_engine/patch_http.py
"""
Route every nba_api request through ScraperAPI.

IMPORT **BEFORE** any nba_api.endpoint is imported.
"""

from __future__ import annotations
import os, requests
from urllib.parse import urlencode, quote

# ──────────────────── config
_API_KEY = os.getenv("SCRAPERAPI_KEY")
if not _API_KEY or _API_KEY == "your_real_key":
    raise RuntimeError("Set SCRAPERAPI_KEY (export or .env) with a real key")

_STATS   = "https://stats.nba.com"
_SCRAPER = "https://api.scraperapi.com"

# Minimum headers NBA gateway insists on
_HDRS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Referer": "https://stats.nba.com",
    "Origin":  "https://stats.nba.com",
    "Accept":  "application/json, text/plain, */*",
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token":  "true",
}

def _send_via_scraper(self, endpoint, parameters=None, *_, timeout=30, **__):
    # build native NBA URL
    qs   = urlencode(parameters or {}, doseq=True)
    tgt  = f"{_STATS}/stats/{endpoint}?{qs}"

    # wrap through ScraperAPI
    proxy = (
        f"{_SCRAPER}"
        f"?api_key={_API_KEY}"
        "&premium=true"             # <-- use paid pool (needs at least “Starter” plan)
        "&country_code=de"
        #"&country_code=us"
        "&keep_headers=true"
        "&render=false"               # we only need raw JSON
        f"&url={quote(tgt, safe='')}"
    )

    r = requests.get(proxy, headers=_HDRS, timeout=timeout, verify=False)
    r.raise_for_status()
    return r

def _install():
    import nba_api.library.http as core
    core.NBAHTTP.send_api_request = _send_via_scraper
    try:
        import nba_api.stats.library.http as stats
        stats.NBAStatsHTTP.send_api_request = _send_via_scraper
    except ModuleNotFoundError:
        pass

_install()
print("✅  patch_http active – nba_api now pipes through ScraperAPI")
