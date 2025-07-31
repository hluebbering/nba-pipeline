"""
Players ▸ Box Scores ▸ Advanced  (game-level with MATCHUP, GAME_DATE …)

Endpoint used by https://www.nba.com/stats/players/boxscores-advanced
"""

from __future__ import annotations

import datetime as dt
from typing import List

import pandas as pd
import requests
from nba_api.stats.endpoints import playergamelogs
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.cloud import bigquery

# ─── config ──────────────────────────────────────────────────────────
PROJECT_ID = "nba-insight-dev"
DATASET = "nba_raw"
BQ_TABLE = f"{PROJECT_ID}.{DATASET}.player_boxscores_advanced"

SEASON = "2024-25"
SEASON_START = dt.date(2024, 10, 22)    # adjust if the NBA shifts dates
SEASON_END   = dt.date(2025, 4, 16)
WINDOW_DAYS  = 14                       # two-week chunks are fine here
MAX_RETRIES  = 3
TIMEOUT_SEC  = 60
# ─────────────────────────────────────────────────────────────────────


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError)),
    reraise=True,
)
def _fetch_window(date_from: str, date_to: str) -> pd.DataFrame:
    """One API call for a small date window."""
    return (
        playergamelogs.PlayerGameLogs(
            season_nullable=SEASON,
            season_type_nullable="Regular Season",
            #measure_type_nullable="Advanced",
            measure_type_player_game_logs_nullable="Advanced",  # ← NEW
            per_mode_simple_nullable="Totals",                  # game totals
            date_from_nullable=date_from,
            date_to_nullable=date_to,
            timeout=TIMEOUT_SEC,
        )
        .get_data_frames()[0]
    )


def _date_windows(start: dt.date, end: dt.date, step_days: int) -> List[tuple[str, str]]:
    d = []
    cur = start
    while cur <= end:
        nxt = min(cur + dt.timedelta(days=step_days - 1), end)
        d.append((cur.isoformat(), nxt.isoformat()))
        cur = nxt + dt.timedelta(days=1)
    return d


def fetch_player_boxscores_advanced() -> pd.DataFrame:
    """Aggregate all windows into one DataFrame."""
    pieces: list[pd.DataFrame] = []
    for date_from, date_to in _date_windows(SEASON_START, SEASON_END, WINDOW_DAYS):
        df = _fetch_window(date_from, date_to)
        if not df.empty:
            pieces.append(df)

    full = pd.concat(pieces, ignore_index=True) if pieces else pd.DataFrame()
    full.attrs["downloaded_utc"] = dt.datetime.utcnow().isoformat(timespec="seconds")
    return full


def load_to_bigquery(df: pd.DataFrame, table: str = BQ_TABLE) -> None:
    if df.empty:
        return
    cfg = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    bigquery.Client(project=PROJECT_ID).load_table_from_dataframe(
        df, table, job_config=cfg
    ).result()
    
    


def load_to_bigquery(df: pd.DataFrame, table: str = BQ_TABLE) -> None:
    client = bigquery.Client(project=PROJECT_ID)

    # ── ensure dataset exists ───────────────────────────
    dataset_id = f"{PROJECT_ID}.{DATASET}"
    try:
        client.get_dataset(dataset_id)      # raises 404 if missing
    except Exception:
        client.create_dataset(bigquery.Dataset(dataset_id), exists_ok=True)

    # ── create empty table schema on first run (optional) ──
    if df.empty:
        schema = [
            bigquery.SchemaField("GAME_ID", "STRING"),
            bigquery.SchemaField("PLAYER_ID", "STRING"),
            bigquery.SchemaField("GAME_DATE", "DATE"),
            bigquery.SchemaField("MATCHUP", "STRING"),
            # … add the rest of your columns here
        ]
        client.create_table(bigquery.Table(table, schema=schema), exists_ok=True)
        print("Created empty table →", table)
        return

    cfg = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    job = client.load_table_from_dataframe(df, table, job_config=cfg)
    job.result()
    print("Loaded", len(df), "rows to", table)


# quick manual run
if __name__ == "__main__":
    data = fetch_player_boxscores_advanced()
    print(f"Rows: {len(data):,}")
    if len(data):
        data.to_csv("player_boxscores_advanced_2024_25.csv", index=False)
