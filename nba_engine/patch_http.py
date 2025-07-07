# nba_engine/patch_http.py   ❶ FIXED import paths
import os, warnings
from urllib.parse import urlencode, quote_plus

import nba_api.library.http as _http          # ← right module
from nba_api.library.http import NBAStatsHTTP # ← base class

_SCRAPER = "https://api.scraperapi.com"
_API_KEY = os.getenv("SCRAPERAPI_KEY") or "YOUR_KEY_HERE"

BASE_HEADERS = _http.HEADERS                  # ← constant now exists ✅


class PatchedHTTP(NBAStatsHTTP):
    """Proxy every nba.com/stats request through ScraperAPI."""
    def send_api_request(self, endpoint, parameters, headers=None, **kw):
        merged = {**BASE_HEADERS, **(headers or {})}

        # build the original stats.nba.com URL
        nba_url   = f"{self.BASE_URL}/{endpoint}"
        target    = f"{nba_url}?{urlencode(parameters or {})}"

        # wrap with ScraperAPI
        wrapped = (
            f"{_SCRAPER}/?api_key={_API_KEY}"
            f"&render=true&url={quote_plus(target)}"
        )

        sess = self.get_session()
        sess.verify = False          # ignore local-cert chain in Codespaces
        warnings.filterwarnings(
            "ignore", message="Unverified HTTPS request"
        )

        return sess.get(wrapped, headers=merged, timeout=kw.get("timeout", 30))


# monkey-patch the symbol every endpoint references
_http.NBAStatsHTTP = PatchedHTTP
