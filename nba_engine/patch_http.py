"""
Monkey-patch nba_api so every stats.nba.com call is proxied through ScraperAPI.

Works with *old* and *new* releases of `nba_api`, even if the   HEADERS
constant moved (or disappeared entirely).
"""

from __future__ import annotations

import os
import warnings
from urllib.parse import urlencode, quote_plus

# --------------------------------------------------------------------------- #
# Locate the base HTTP class *and* the default request headers ― regardless of
# which nba_api version is installed.
# --------------------------------------------------------------------------- #
try:
    # Newer path
    import nba_api.stats.library.http as _http
except ModuleNotFoundError:
    # Older path
    import nba_api.library.http as _http

# The HTTP base class we need to subclass
NBAStatsHTTP = getattr(_http, "NBAStatsHTTP", None)
if NBAStatsHTTP is None:
    raise ImportError("Could not find NBAStatsHTTP in nba_api")

# Default headers live either on the module (old) or on the class (new).  If
# neither exists, fall back to a hard-coded UA that the NBA site accepts.
_BASE_HEADERS = (
    getattr(_http, "HEADERS", None)
    or getattr(NBAStatsHTTP, "HEADERS", None)
    or {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://stats.nba.com",
        "Referer": "https://stats.nba.com",
        "x-nba-stats-token": "true",
        "x-nba-stats-origin": "stats",
    }
)

# --------------------------------------------------------------------------- #
# ScraperAPI configuration
# --------------------------------------------------------------------------- #
_SCRAPER_URL = "https://api.scraperapi.com"
_API_KEY = os.environ.get("SCRAPERAPI_KEY")
if not _API_KEY:
    raise RuntimeError(
        "SCRAPERAPI_KEY environment variable is missing.  "
        "Add it to .env or your Codespace secrets."
    )

# --------------------------------------------------------------------------- #
# The patched class
# --------------------------------------------------------------------------- #
class PatchedHTTP(NBAStatsHTTP):  # type: ignore[misc]
    """Route nba_api traffic through ScraperAPI (handles HTTPS + cert issues)."""

    def send_api_request(
        self,
        endpoint: str,
        parameters: dict | None = None,
        headers: dict | None = None,
        **kw,
    ):
        # Compose the real NBA-stats URL first
        nba_url = f"{self.BASE_URL}/{endpoint}"
        nba_qs  = urlencode(parameters or {})
        target  = f"{nba_url}?{nba_qs}"

        # Wrap with ScraperAPI
        proxied = (
            f"{_SCRAPER_URL}/?api_key={_API_KEY}"
            f"&render=true&country_code=us&url={quote_plus(target)}"
        )

        merged_headers = {**_BASE_HEADERS, **(headers or {})}

        sess = self.get_session()
        sess.verify = False                       # Codespaces often lack root CA
        warnings.filterwarnings(
            "ignore", message="Unverified HTTPS request"
        )

        timeout = kw.pop("timeout", 90)
        # Any **kw left (cookies, allow_redirects, etc.) still get passed through
        return sess.get(proxied, headers=merged_headers, timeout=timeout, **kw)


# --------------------------------------------------------------------------- #
# Monkey-patch nba_api so every subsequent import uses our class
# --------------------------------------------------------------------------- #
_http.NBAStatsHTTP = PatchedHTTP
