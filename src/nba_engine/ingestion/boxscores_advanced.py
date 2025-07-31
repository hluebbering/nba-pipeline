"""
Robust pull for Players ▸ Box Scores ▸ Advanced (Regular Season 2024-25)

It slices the season into 1-week windows so each NBA Stats request
returns quickly, avoiding the 90-second stall you just hit.
"""

from __future__ import annotations

import datetime as dt
from typing import List, Literal

import pandas as pd
import requests
from nba_api.stats.endpoints import leaguedashplayerstats
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from google.cloud import bigquery

# ─── Config ───────────────────────────────────────────────────────────
PROJECT_ID = "nba-insight-dev"
DATASET = "nba_raw"
BQ_TABLE = f"{PROJECT_ID}.{DATASET}.player_boxscores_advanced"

SEASON = "2024-25"
SEASON_START = dt.date(2024, 10, 22)    # opening night (adjust if needed)
SEASON_END   = dt.date(2025, 4, 16)     # last regular-season date
WINDOW_DAYS  = 7                        # 7-day chunks
TIMEOUT_SEC  = 90                       # per-request socket timeout
MAX_RETRIES  = 3                        # per-request retry
# ──────────────────────────────────────────────────────────────────────


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError)),
    reraise=True,
)
def _fetch_window(
    date_from: str,
    date_to: str,
    per_mode: str,
    season_type: str,
) -> pd.DataFrame:
    """One NBA Stats call for a small date range."""
    return (
        leaguedashplayerstats.LeagueDashPlayerStats(
            season=SEASON,
            season_type_all_star=season_type,
            measure_type_detailed_defense="Advanced",
            per_mode_detailed=per_mode,
           date_from_nullable=date_from, date_to_nullable=date_to,
            timeout=TIMEOUT_SEC,
        )
        .get_data_frames()[0]
    )


def _date_windows(
    start: dt.date, end: dt.date, step_days: int = 7
) -> List[tuple[str, str]]:
    """Return list of (YYYY-MM-DD, YYYY-MM-DD) tuples."""
    wnd = []
    cur = start
    while cur <= end:
        nxt = min(cur + dt.timedelta(days=step_days - 1), end)
        wnd.append((cur.isoformat(), nxt.isoformat()))
        cur = nxt + dt.timedelta(days=1)
    return wnd


def fetch_player_boxscores_advanced(
    per_mode: Literal["Totals", "PerGame", "Per36", "Per100Possessions"] = "Totals",
    season_type: Literal["Regular Season", "Playoffs"] = "Regular Season",
) -> pd.DataFrame:
    """Aggregate weekly slices into one DataFrame."""
    pieces: list[pd.DataFrame] = []

    for date_from, date_to in _date_windows(SEASON_START, SEASON_END):
        df = _fetch_window(date_from, date_to, per_mode, season_type)
        if len(df):
            pieces.append(df)

    full = pd.concat(pieces, ignore_index=True) if pieces else pd.DataFrame()
    full.attrs["downloaded_utc"] = dt.datetime.utcnow().isoformat(timespec="seconds")
    return full


def load_to_bigquery(df: pd.DataFrame, table: str = BQ_TABLE) -> None:
    """Overwrite table with the aggregated DataFrame."""
    if df.empty:  # nothing yet (e.g., before opening night)
        return
    cfg = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    bigquery.Client(project=PROJECT_ID).load_table_from_dataframe(
        df, table, job_config=cfg
    ).result()


# ─── CLI / quick test ─────────────────────────────────────────────────
if __name__ == "__main__":
    data = fetch_player_boxscores_advanced()
    print(f"Pulled {len(data):,} rows")
    if not data.empty:
        data.to_csv("player_boxscores_advanced_2024_25.csv", index=False)
        print("Saved player_boxscores_advanced_2024_25.csv")
