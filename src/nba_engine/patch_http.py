"""
nba_engine.patch_http
Central place to build *all* outbound HTTP calls so every asset
inherits retry / proxy / header logic automatically.
"""

from __future__ import annotations

import os
import random
import urllib.parse as _u
from typing import Mapping, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ── Config ──────────────────────────────────────────────────────────────────
SA_KEY        = os.getenv("SCRAPERAPI_KEY")            # must be premium-enabled
SA_RETRIES    = int(os.getenv("SCRAPERAPI_RETRIES", 3))
SA_TIMEOUT_MS = int(os.getenv("SCRAPERAPI_TIMEOUT_MS", 90_000))  # 90 s

# 👉 hard-wired because only “eu” works for you
SA_COUNTRY = "eu"

NBA_HEADERS: Mapping[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Referer": "https://stats.nba.com",
    "Origin": "https://www.nba.com",
    "x-nba-stats-token": "true",
    "x-nba-stats-origin": "stats",
}

# ── Session factory ─────────────────────────────────────────────────────────
def _retry_adapter() -> HTTPAdapter:
    return HTTPAdapter(
        max_retries=Retry(
            total=SA_RETRIES,
            backoff_factor=0.8,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
            raise_on_status=False,
        )
    )

def _make_session() -> requests.Session:
    if not SA_KEY:
        raise RuntimeError("SCRAPERAPI_KEY env var missing.")
    s = requests.Session()
    s.headers.update(NBA_HEADERS)
    s.mount("https://", _retry_adapter())
    s.mount("http://", _retry_adapter())
    return s

# ── Public helper ───────────────────────────────────────────────────────────
def nba_get(endpoint: str, params: Mapping[str, Any]) -> dict[str, Any]:
    """
    Call stats.nba.com/{endpoint} through ScraperAPI premium with
    NBA headers forwarded. Returns parsed JSON or raises RuntimeError.
    """
    nba_url = (
        "https://stats.nba.com/stats/"
        + endpoint
        + "?"
        + _u.urlencode(params, safe=":,")
    )

    encoded = _u.quote(nba_url, safe="")
    proxy_params = {
        "api_key":     SA_KEY,
        "premium":     "true",
        "keep_headers":"true",
        "country_code": SA_COUNTRY,     # "eu"
        "retry":        str(SA_RETRIES),
        "timeout":      str(SA_TIMEOUT_MS),
        "url":          encoded,
    }
    proxy_url = "https://api.scraperapi.com?" + _u.urlencode(proxy_params, safe="%")
    

    resp = _make_session().get(proxy_url, timeout=SA_TIMEOUT_MS / 1000)

    if resp.status_code != 200:
        raise RuntimeError(f"ScraperAPI {resp.status_code}: {resp.text[:200]} …")

    return resp.json()


