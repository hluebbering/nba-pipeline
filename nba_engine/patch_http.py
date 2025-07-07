# nba_engine/patch_http.py
import os
import warnings
from urllib.parse import urlencode, quote

from nba_api.library.http import NBAStatsHTTP         # ← correct path
import nba_api.library.http as _http                  # for monkey-patch

_BASE_URL = "https://api.scraperapi.com"
_API_KEY  = os.getenv("SCRAPERAPI_KEY") or "YOUR_KEY"

class PatchedHTTP(NBAStatsHTTP):
    def send_api_request(self, endpoint, parameters, *a, **kw):
        headers = {**self.HEADERS, **kw.pop("headers", {})}

        # build the original NBA URL exactly as nba_api would
        nba_url   = f"{self.BASE_URL}/{endpoint}"
        nba_query = urlencode(parameters or {})
        target    = f"{nba_url}?{nba_query}"

        # wrap through ScraperAPI
        wrapped = (
            f"{_BASE_URL}/?api_key={_API_KEY}&render=true&url={quote(target)}"
        )

        sess = self.get_session()
        sess.verify = False                           # ignore bad certs
        warnings.filterwarnings(
            "ignore",
            message="Unverified HTTPS request",       # silence urllib3 warn
        )

        timeout = kw.get("timeout", 30)
        return sess.get(wrapped, headers=headers, timeout=timeout)

# 🔑  make EVERY nba_api endpoint see the patched class
_http.NBAStatsHTTP = PatchedHTTP
