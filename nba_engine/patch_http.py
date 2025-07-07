# nba_engine/patch_http.py
from nba_api.stats.library.http import NBAStatsHTTP   # correct import path
import os, functools

_BASE_HEADERS = getattr(NBAStatsHTTP, "HEADERS", {})  # defined *first*

class PatchedHTTP(NBAStatsHTTP):
    """Adds nba.com headers and (optionally) a ScraperAPI proxy."""

    HEADERS = {
        **_BASE_HEADERS,
        "Origin":            "https://www.nba.com",
        "Referer":           "https://www.nba.com/",
        "x-nba-stats-origin":"stats",
        "x-nba-stats-token": "true",
    }

    # --- helper ---------------------------------------------------
    def _apply_proxy(self):
        key = os.getenv("SCRAPERAPI_KEY")
        if key:
            self.get_session().proxies.update(
                {"https": f"http://scraperapi:{key}@proxy-server.scraperapi.com:8001"}
            )

    # --- override -------------------------------------------------
    def send_api_request(self, endpoint, params=None, headers=None, **kw):
        """
        Same signature nba-api expects; just tack on proxy + headers
        before delegating to the parent implementation.
        """
        self._apply_proxy()
        # merge our headers with any that the caller provided
        hdrs = {**self.HEADERS, **(headers or {})}
        return super().send_api_request(endpoint, params=params, headers=hdrs, **kw)

# monkey-patch so the rest of nba-api uses it
import nba_api.stats.library.http as _http_mod
_http_mod.NBAStatsHTTP = PatchedHTTP
