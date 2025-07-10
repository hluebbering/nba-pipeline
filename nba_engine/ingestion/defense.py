"""
Grab LeagueDash Player-Tracking DEFENSE stats (shots contested, FG% allowed, etc.).
Table: <PROJECT>.<DATASET>.stg_player_defense
"""

import os, datetime as dt, pandas as pd
from google.cloud import bigquery
from nba_api.stats.endpoints import leaguedashptdefend   # pip install nba_api

BQ_TABLE = os.getenv("BQ_DEF_TABLE", "myproj.nba_raw.stg_player_defense")

def fetch(season: str = "2024-25") -> pd.DataFrame:
    df = leaguedashptdefend.LeagueDashPTDefend(
            season=season, per_mode_simple="PerGame"
         ).get_data_frames()[0]
    df["season"] = season
    df["ingest_ts"] = dt.datetime.utcnow()
    return df

def load() -> None:
    df = fetch()
    bigquery.Client().load_table_from_dataframe(
        df, BQ_TABLE,
        job_config={"write_disposition": "WRITE_APPEND"}
    ).result()
    print(f"[defense] {len(df)} rows appended to {BQ_TABLE}")

if __name__ == "__main__":
    load()
