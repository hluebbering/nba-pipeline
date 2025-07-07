# nba_engine/patch_http.py
import os, warnings
from urllib.parse import urlencode, quote_plus

import nba_api.stats.library.http as _http          # ← exact module used upstream
from nba_api.stats.library.http import NBAStatsHTTP  # base class

_SCRAPER = "https://api.scraperapi.com"
_API_KEY = os.getenv("SCRAPERAPI_KEY") or "YOUR_KEY_HERE"

BASE_HEADERS = _http.HEADERS                        # <- module-level constant ✅


class PatchedHTTP(NBAStatsHTTP):
    """Proxy every NBA-stats call through ScraperAPI."""
    def send_api_request(self, endpoint, parameters, headers=None, **kw):
        # merge custom headers with the library’s defaults
        merged = {**BASE_HEADERS, **(headers or {})}

        # 1️⃣  compose the regular nba.com/stats URL
        nba_url   = f"{self.BASE_URL}/{endpoint}"
        nba_query = urlencode(parameters or {})
        target    = f"{nba_url}?{nba_query}"

        # 2️⃣  wrap it for ScraperAPI
        wrapped = (
            f"{_SCRAPER}/?api_key={_API_KEY}"
            f"&render=true&url={quote_plus(target)}"
        )

        sess = self.get_session()
        sess.verify = False                           # ignore local-cert issues
        warnings.filterwarnings(
            "ignore", message="Unverified HTTPS request"
        )

        return sess.get(wrapped, headers=merged, timeout=kw.get("timeout", 30))


# 🔥  Monkey-patch *the exact symbol* every endpoint imports
_http.NBAStatsHTTP = PatchedHTTP
