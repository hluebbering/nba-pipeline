# nba_engine/patch_http.py
"""
Proxy every stats.nba.com request through ScraperAPI so that dagster
executions inside GitHub Codespaces (or other locked-down networks)
can still reach the NBA Stats API.
"""
import os
import warnings
from urllib.parse import urlencode, quote_plus

import nba_api.stats.library.http as _http          # ✅ correct module
from nba_api.stats.library.http import NBAStatsHTTP # ✅ base class

_SCRAPER   = "https://api.scraperapi.com"
_API_KEY   = os.getenv("SCRAPERAPI_KEY") or "YOUR_KEY_HERE"
_BASE_HDRS = _http.HEADERS                          # module-level constant


class PatchedHTTP(NBAStatsHTTP):
    """Override `.send_api_request()` to wrap the URL in ScraperAPI."""
    def send_api_request(self, endpoint, parameters=None, headers=None, **kw):
        # headers the endpoints expect
        merged = {**_BASE_HDRS, **(headers or {})}

        # 1️⃣ the normal (unproxied) NBA-Stats URL
        nba_url   = f"{self.BASE_URL}/{endpoint}"
        query     = urlencode(parameters or {})
        target    = f"{nba_url}?{query}"

        # 2️⃣ wrap it through ScraperAPI
        wrapped   = (
            f"{_SCRAPER}/?api_key={_API_KEY}"
            f"&render=true&country_code=us"
            f"&url={quote_plus(target)}"
        )

        # ScraperAPI’s cert chain sometimes fails inside Codespaces
        sess = self.get_session()
        sess.verify = False
        warnings.filterwarnings(
            "ignore", message="Unverified HTTPS request"
        )

        timeout = kw.pop("timeout", 30)
        return sess.get(wrapped, headers=merged, timeout=timeout, **kw)


# Monkey-patch so every future import gets our version
_http.NBAStatsHTTP = PatchedHTTP
