"""
Pull (or stub) LeagueDash Pt Defend data.

During the off-season the NBA pulls both the JSON endpoint and the
stats-static CSV host, so we can’t reach 2024-25 yet.  Until the file
reappears, this module:

1.  Returns an **empty DataFrame** with the correct columns.
2.  Logs a friendly message so downstream ops know it’s a stub.
3.  Keeps the fetch() signature identical so you can swap in the real
    implementation by replacing just the `URL` and deleting the `except`
    block below.
"""

from __future__ import annotations

import datetime as dt
import io
import logging
from pathlib import Path

import pandas as pd
import requests

# ──────────────────────────────────────────────────────────────────────
SEASON = "2024-25"
URL = (
    "https://stats-static.nba.com/prod/league/player_stats_defend/"
    "2024_25_league_dash_ptdefend.csv"
)

# Mandatory headers when the file finally appears
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://stats.nba.com/",
    "Origin": "https://stats.nba.com",
    "Host": "stats.nba.com",
}

# Where we’ll drop the CSV once it succeeds, so the sensor stops hitting NBA
CACHE_DIR = Path(__file__).with_suffix("").parent / ".." / "data" / "defense"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_FILE = CACHE_DIR / f"{SEASON.replace('-', '_')}_league_dash_ptdefend.csv"
# ──────────────────────────────────────────────────────────────────────


def _empty_frame() -> pd.DataFrame:
    """Return an empty DF with the expected schema."""
    return pd.DataFrame(
        columns=[
            "PLAYER_ID",
            "PLAYER_NAME",
            "DEFENSE_CATEGORY",
            "GP",
            "D_FGM",
            "D_FGA",
            "D_FG_PCT",
            "NORMALIZED_POS",
            "PLAYER_POSITION",
        ]
    )


def fetch(season: str = SEASON) -> pd.DataFrame:
    """Fetch the CSV if/when it’s online; otherwise return a stub frame."""
    if season != SEASON:
        raise ValueError(f"Only {SEASON} supported until the NBA publishes new files")

    # 1⃣  Serve cached copy if we already grabbed it.
    if CACHE_FILE.exists():
        return pd.read_csv(CACHE_FILE)

    # 2⃣  Try live download (will fail until the NBA restores DNS + file)
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=(10, 60))
        resp.raise_for_status()  # raises on 4xx / 5xx
        df = pd.read_csv(io.StringIO(resp.text))
        df.attrs["downloaded_utc"] = dt.datetime.utcnow().isoformat(timespec="seconds")
        df.to_csv(CACHE_FILE, index=False)  # cache locally for next run
        return df

    except Exception as exc:  # noqa: BLE001
        logging.warning(
            "NBA defensive CSV not available yet (%s) — "
            "returning empty stub frame so pipeline stays green",
            exc,
        )
        return _empty_frame()
