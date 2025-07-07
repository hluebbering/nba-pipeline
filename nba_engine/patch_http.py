# nba_engine/patch_http.py  ← full working example
from nba_api.stats.library.http import NBAStatsHTTP   # ← note the .stats. path change
import os

# ------------------------------------------------------------------
# 1)  Make sure this line comes *before* the class; otherwise it
#     isn't yet defined when we build PatchedHTTP.                   |
# ------------------------------------------------------------------
_BASE_HEADERS = getattr(NBAStatsHTTP, "HEADERS", {})  # falls back to {}

class PatchedHTTP(NBAStatsHTTP):
    """Adds the headers that nba.com expects and (optionally) a proxy."""
    HEADERS = {
        **_BASE_HEADERS,           # safe on every nba-api version
        "Origin": "https://www.nba.com",
        "Referer": "https://www.nba.com/",
        "x-nba-stats-origin": "stats",
        "x-nba-stats-token":  "true",
    }

    def send_api_request(self, *a, **kw):
        # ScraperAPI proxy (only if key present)
        proxy_key = os.getenv("SCRAPERAPI_KEY")
        if proxy_key:
            kw["proxies"] = {"https": f"http://scraperapi:{proxy_key}@proxy-server.scraperapi.com:8001"}
        # allow caller-provided timeout to pass straight through
        return super().send_api_request(*a, **kw)

# ------------------------------------------------------------------
# 2)  Monkey-patch nba_api so everything else picks up the new class.
# ------------------------------------------------------------------
import nba_api.stats.library.http as http_module
http_module.NBAStatsHTTP = PatchedHTTP
