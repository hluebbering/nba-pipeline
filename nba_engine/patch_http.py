# nba_engine/patch_http.py
import os, warnings
from urllib.parse import urlencode, quote

# 👉 import the SAME module the endpoints use
import nba_api.stats.library.http as _http
from nba_api.stats.library.http import NBAStatsHTTP         

_SCRAPER   = "https://api.scraperapi.com"
_API_KEY   = os.getenv("SCRAPERAPI_KEY") or "YOUR_KEY_HERE"

class PatchedHTTP(NBAStatsHTTP):
    """Wrap every nba_api request through ScraperAPI."""
    def send_api_request(self, endpoint, parameters, *a, **kw):
        headers = {**self.HEADERS, **kw.pop("headers", {})}

        # build original NBA stats URL
        nba_url   = f"{self.BASE_URL}/{endpoint}"
        nba_query = urlencode(parameters or {})
        target    = f"{nba_url}?{nba_query}"

        # wrap via proxy
        wrapped = (
            f"{_SCRAPER}/?api_key={_API_KEY}"
            f"&render=true&url={quote(target)}"
        )

        sess = self.get_session()
        sess.verify = False                           # ignore cert issues
        warnings.filterwarnings(
            "ignore", message="Unverified HTTPS request"
        )

        timeout = kw.get("timeout", 30)
        return sess.get(wrapped, headers=headers, timeout=timeout)

# 💥  THIS is the critical line — replace the class globally
_http.NBAStatsHTTP = PatchedHTTP
