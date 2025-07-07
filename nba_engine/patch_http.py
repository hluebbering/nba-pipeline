"""
nba_engine.patch_http
Central place to build *all* outbound HTTP calls so every asset
inherits retry / proxy / header logic automatically.
"""

from __future__ import annotations

import os
import time
import random
import urllib.parse as _u
from typing import Mapping, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# --------------------------------------------------------------------------- #
# 🔑  Config (env-driven so you never hard-code secrets)                      #
# --------------------------------------------------------------------------- #
SA_KEY           = os.getenv("SCRAPERAPI_KEY")  # must be premium-enabled
SA_COUNTRY_POOL  = os.getenv("SCRAPERAPI_COUNTRIES", "eu").split(",")
SA_RETRIES       = int(os.getenv("SCRAPERAPI_RETRIES", 3))
SA_TIMEOUT_MS    = int(os.getenv("SCRAPERAPI_TIMEOUT_MS", 90_000))           # 90 s


# NBA-specific fingerprint headers – change once, apply everywhere
NBA_HEADERS: Mapping[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Referer": "https://stats.nba.com",
    "Origin": "https://www.nba.com",
    "x-nba-stats-token": "true",
    "x-nba-stats-origin": "stats",
}


# --------------------------------------------------------------------------- #
# 🌐  Session factory                                                         #
# --------------------------------------------------------------------------- #
def _retry_adapter() -> HTTPAdapter:
    """Uniform retry policy across all sessions."""
    return HTTPAdapter(
        max_retries=Retry(
            total=SA_RETRIES,
            backoff_factor=0.8,            # exp back-off 0.8, 1.6, 3.2 …
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST"),
            raise_on_status=False,
        )
    )


def make_session() -> requests.Session:
    """Return a pre-wired session that talks through ScraperAPI premium."""
    if not SA_KEY:
        raise RuntimeError(
            "SCRAPERAPI_KEY not found – set it in Codespaces Secrets or your shell."
        )

    s = requests.Session()
    s.headers.update(NBA_HEADERS)
    s.mount("https://", _retry_adapter())
    s.mount("http://", _retry_adapter())
    return s


# --------------------------------------------------------------------------- #
# 🏀  Helper to hit stats.nba.com endpoints                                   #
# --------------------------------------------------------------------------- #
def nba_get(endpoint: str, params: Mapping[str, Any]) -> dict[str, Any]:
    """
    Build the NBA Stats URL, wrap it in a premium ScraperAPI proxy URL,
    fire the request, and return the decoded JSON.
    """
    # 1 – canonical NBA stats URL
    nba_url = (
        "https://stats.nba.com/stats/"
        + endpoint
        + "?"
        + _u.urlencode(params, safe=":,")
    )

    # 2 – proxy params
    proxy_params = {
        "api_key": SA_KEY,
        "premium": "true",
        "keep_headers": "true",
        "country_code": "eu",
        "retry": str(SA_RETRIES),
        "timeout": str(SA_TIMEOUT_MS),
        "url": nba_url,
    }

    url = "https://api.scraperapi.com?" + _u.urlencode(proxy_params, safe=":/?&=")

    sess = make_session()
    resp = sess.get(url, timeout=SA_TIMEOUT_MS / 1000)  # seconds

    if resp.status_code != 200:
        raise RuntimeError(
            f"ScraperAPI {resp.status_code}: {resp.text[:200]} …"
        )
    return resp.json()
