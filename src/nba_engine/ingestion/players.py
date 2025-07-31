"""
Nightly (or one-off) dump of the NBA player master list.
Table is TRUNCATED on each run.
"""

import os, datetime as dt, pandas as pd
from google.cloud import bigquery
from nba_api.stats.static import players as nba_players

#BQ_TABLE = "myproject.nba_raw.raw_players"     # adjust to your project.dataset
BQ_TABLE = "nba-insight-dev.nba_raw.raw_players"

def load() -> None:
    # 1  create dataframe
    df = pd.DataFrame(nba_players.get_players())
    df["ingest_ts"] = dt.datetime.utcnow()

    # 2  build a proper LoadJobConfig object
    cfg = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        # you can add other options here later (schema, partitioning, etc.)
    )

    # 3  launch the load job
    client = bigquery.Client()
    client.load_table_from_dataframe(df, BQ_TABLE, job_config=cfg).result()

    print(f"[players] loaded {len(df)} rows into {BQ_TABLE}")




if __name__ == "__main__":
    load()
