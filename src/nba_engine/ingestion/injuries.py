"""
Scrape ESPN NBA injuries → return a DataFrame with BigQuery-safe column names.
"""

import datetime as dt
import re
import pandas as pd
import requests

ESPN_URL = "https://www.espn.com/nba/injuries"


def _scrape() -> pd.DataFrame:
    """Returns a tidy DF ready for BigQuery."""
    tables = pd.read_html(ESPN_URL)           # one per team
    frames = []

    for raw in tables:
        if "COMMENT" not in raw.columns:      # skip ads
            continue

        team_header = raw.columns[0]          # “Golden State Warriors Injuries”
        team = re.sub(r"\s+Injuries.*$", "", team_header).strip()

        df = raw.rename(
            columns={
                "NAME": "player",
                "POS": "pos",
                "EST. RETURN": "est_return_date",
                "STATUS": "status",
                "COMMENT": "comment",
            }
        )
        df["team"] = team
        frames.append(df)

    if not frames:
        raise RuntimeError("ESPN layout changed – no injury tables found")

    out = pd.concat(frames, ignore_index=True)

    # BigQuery-safe column names (already renamed above, but be safe)
    out.columns = (
        out.columns.str.lower()
        .str.replace(r"[ .]", "_", regex=True)
        .str.replace(r"__+", "_", regex=True)
        .str.strip("_")
    )

    out["scraped_at"] = dt.datetime.utcnow()
    return out
