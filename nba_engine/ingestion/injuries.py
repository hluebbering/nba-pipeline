"""
Pull current NBA injury statuses from ESPN and append to BigQuery.
Table: <PROJECT>.<DATASET>.stg_injury_updates
"""

import os, re, datetime as dt, pandas as pd, requests
from google.cloud import bigquery

ESPN_URL = "https://www.espn.com/nba/injuries"
BQ_TABLE = os.getenv("BQ_INJURY_TABLE", "myproj.nba_raw.stg_injury_updates")

def _scrape() -> pd.DataFrame:
    # ESPN prints one HTML table per team
    tables = pd.read_html(ESPN_URL)          # columns: NAME | POS | EST. RETURN | STATUS | COMMENT
    frames = []
    for raw in tables:
        if "COMMENT" not in raw.columns:     # skip ad junk
            continue
        team = re.sub(r" Injuries.*", "", raw.columns[0])   # header holds "Golden State Warriors Injuries"
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
        raise RuntimeError("No injury tables parsed from ESPN")
    out = pd.concat(frames, ignore_index=True)
    out["scraped_at"] = dt.datetime.utcnow()
    return out

def load() -> None:
    df = _scrape()
    bigquery.Client().load_table_from_dataframe(
        df, BQ_TABLE,
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_APPEND"),
    ).result()
    print(f"[injuries] {len(df)} rows appended to {BQ_TABLE}")

if __name__ == "__main__":
    load()
