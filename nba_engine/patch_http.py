# nba_engine/patch_http.py
from nba_api.stats.library.http import NBAStatsHTTP
import os

_DEFAULT_HEADERS = {
    "Origin":             "https://www.nba.com",
    "Referer":            "https://www.nba.com/",
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token":  "true",
}

class PatchedHTTP(NBAStatsHTTP):
    """Adds required NBA headers and optional ScraperAPI proxy."""
    HEADERS = {**getattr(NBAStatsHTTP, "HEADERS", {}), **_DEFAULT_HEADERS}

    def _apply_proxy(self):
        key = os.getenv("SCRAPERAPI_KEY")
        if key:                                   # only if user set .env
            self.get_session().proxies.update(
                {"https": f"http://scraperapi:{key}@proxy-server.scraperapi.com:8001"}
            )

    # note: *parameters* (not params), keep the rest of the signature
    def send_api_request(
        self, endpoint, parameters, referer=None, proxy=None,
        headers=None, timeout=30
    ):
        self._apply_proxy()
        merged = {**self.HEADERS, **(headers or {})}

        # ---- PATCH: disable SSL verification on this session ----
        sess = self.get_session()
        sess.verify = False                         # ← trust proxy cert
        import warnings, urllib3
        warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)
        # ---------------------------------------------------------

        # call parent exactly as it expects
        return super().send_api_request(
            endpoint, parameters, referer=referer,
            proxy=proxy, headers=merged, timeout=timeout
        )

# Monkey-patch nba_api globally
import nba_api.stats.library.http as _http
_http.NBAStatsHTTP = PatchedHTTP       # ← one-liner patch
