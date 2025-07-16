"""
Downloads the LeagueDash player-tracking DEFENSE stats for one season
and appends to BigQuery.
"""

import datetime as dt
import os

import pandas as pd
from google.cloud import bigquery
from nba_api.stats.endpoints import leaguedashptdefend


BQ_TABLE = os.getenv("BQ_DEF_TABLE",
                     "myproject.nba_raw.stg_player_defense")


def fetch(season: str = "2024-25") -> pd.DataFrame:
    # NOTE: correct class name is LeagueDashPtDefend  (lower-case “t”)
    df = leaguedashptdefend.LeagueDashPtDefend(
        season=season,
        per_mode_simple="PerGame",
    ).get_data_frames()[0]

    df["season"] = season
    df["ingest_ts"] = dt.datetime.utcnow()
    return df



def load() -> None:
    df = fetch()

    client = bigquery.Client()
    client.load_table_from_dataframe(
        df,
        BQ_TABLE,
        job_config={"write_disposition": "WRITE_APPEND"}
    ).result()

    print(f"[defense] Loaded {len(df)} rows into {BQ_TABLE}")


if __name__ == "__main__":
    load()
