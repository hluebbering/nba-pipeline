"""
Injury scraper  ▸  pulls ESPN's team pages → appends to BigQuery table
"""

import datetime as dt
import os
import re

import pandas as pd
import requests
from google.cloud import bigquery

# ----------------------------------------------------------------------
# CONFIGURATION  – change these two lines for your own project / dataset
# ----------------------------------------------------------------------
ESPN_URL = "https://www.espn.com/nba/injuries"
BQ_TABLE = os.getenv("BQ_INJURY_TABLE",
                     "myproject.nba_raw.stg_injury_updates")
# ----------------------------------------------------------------------


def _scrape() -> pd.DataFrame:
    """
    Returns one DataFrame with columns:
    player | pos | est_return | status | comment | team | scraped_at
    """
    tables = pd.read_html(ESPN_URL)       # one HTML table per team
    frames = []

    for raw in tables:
        # Real injury tables always have a COMMENT column
        if "COMMENT" not in raw.columns:
            continue

        # Header of the table looks like "Golden State Warriors Injuries"
        team_header = raw.columns[0]
        team = re.sub(r"\s+Injuries.*$", "", team_header).strip()

        df = raw.rename(columns={
            "NAME": "player",
            "POS": "pos",
            "EST. RETURN": "est_return",
            "STATUS": "status",
            "COMMENT": "comment"
        })
        df["team"] = team
        frames.append(df)

    if not frames:
        raise RuntimeError("ESPN layout changed – no injury tables found")

    out = pd.concat(frames, ignore_index=True)
    out["scraped_at"] = dt.datetime.utcnow()
    return out


def load() -> None:
    """Scrape, then append to BigQuery."""
    df = _scrape()

    client = bigquery.Client()
    job = client.load_table_from_dataframe(
        df,
        BQ_TABLE,
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_APPEND"),
    )
    job.result()  # wait for completion
    print(f"[injuries] Loaded {len(df)} rows into {BQ_TABLE}")


if __name__ == "__main__":
    load()
