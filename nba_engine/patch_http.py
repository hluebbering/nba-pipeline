"""
Monkey-patch nba_api so every request to stats.nba.com is routed through
ScraperAPI.  Handles *every* known nba_api version (old, new, broken, you name
it) — no more HEADERS / BASE_URL surprises.
"""
from __future__ import annotations

import os
import warnings
from urllib.parse import urlencode, quote_plus

# ---------------------------------------------------------------------------
# Locate the right module, class, and constants — no assumptions.
# ---------------------------------------------------------------------------
try:                                       # newest place
    import nba_api.stats.library.http as _http
except ModuleNotFoundError:                # old place
    import nba_api.library.http as _http   # type: ignore

NBAStatsHTTP = getattr(_http, "NBAStatsHTTP", None)
if NBAStatsHTTP is None:
    raise ImportError("nba_api: cannot find NBAStatsHTTP")

# HEADERS may sit on the *module* (very old) or the *class* (newer).
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
        "x-nba-stats-origin": "stats",
        "x-nba-stats-token": "true",
    }
)

_BASE_URL = (
    getattr(_http, "BASE_URL", None)
    or getattr(NBAStatsHTTP, "BASE_URL", None)
    or "https://stats.nba.com/stats"
)

# ---------------------------------------------------------------------------
# ScraperAPI
# ---------------------------------------------------------------------------
_API_KEY = os.getenv("SCRAPERAPI_KEY")
if not _API_KEY:
    raise RuntimeError(
        "SCRAPERAPI_KEY env-var missing — add it to .env or Codespace secrets."
    )
_SCRAPER = "https://api.scraperapi.com"

# ---------------------------------------------------------------------------
# Patched class
# ---------------------------------------------------------------------------
class PatchedHTTP(NBAStatsHTTP):  # type: ignore[misc]
    """Replace nba_api’s HTTP layer with a ScraperAPI proxy."""

    def send_api_request(          # noqa: D401  (we’re copying nba_api’s sig)
        self,
        endpoint: str,
        parameters: dict | None = None,
        headers: dict | None = None,
        **kw,
    ):
        # 1️⃣ Build the *real* stats.nba.com URL
        real_qs  = urlencode(parameters or {})
        target   = f"{_BASE_URL}/{endpoint}?{real_qs}"

        # 2️⃣ Wrap through ScraperAPI
        proxied  = (
            f"{_SCRAPER}/?api_key={_API_KEY}&render=true"
            f"&country_code=us&url={quote_plus(target)}"
        )

        merged   = {**_BASE_HEADERS, **(headers or {})}

        sess = self.get_session()
        sess.verify = False                     # Codespaces CA chain is flaky
        warnings.filterwarnings(
            "ignore", message="Unverified HTTPS request"
        )

        timeout = kw.pop("timeout", 90)
        return sess.get(proxied, headers=merged, timeout=timeout, **kw)


# ---------------------------------------------------------------------------
# Activate patch globally
# ---------------------------------------------------------------------------
_http.NBAStatsHTTP = PatchedHTTP
