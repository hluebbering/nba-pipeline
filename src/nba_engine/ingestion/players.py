"""
Nightly (or one-off) dump of the NBA player master list.
Table is TRUNCATED on each run.
"""

import os, datetime as dt, pandas as pd
from google.cloud import bigquery
from nba_api.stats.static import players as nba_players

BQ_TABLE = os.getenv("BQ_PLAYERS_TABLE", "myproj.nba_raw.raw_players")

def load() -> None:
    df = pd.DataFrame(nba_players.get_players())
    df["ingest_ts"] = dt.datetime.utcnow()
    bigquery.Client().load_table_from_dataframe(
        df, BQ_TABLE,
        job_config={"write_disposition": "WRITE_TRUNCATE"}
    ).result()
    print(f"[players] {len(df)} rows loaded into {BQ_TABLE}")

if __name__ == "__main__":
    load()
