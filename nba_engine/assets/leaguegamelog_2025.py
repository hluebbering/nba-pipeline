# nba_engine/assets/leaguegamelog_2025.py
from dagster import asset, Output
import pandas as pd

# --- NEW: hardened HTTP session ---------------------------------
from nba_api.stats.library.http import NBAStatsHTTP          # correct path
import requests
from requests.adapters import HTTPAdapter, Retry

sess = requests.Session()
sess.headers.update(        # mimic real browser
    {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0 Safari/537.36"
        ),
        "Referer": "https://stats.nba.com",
        "Origin": "https://stats.nba.com",
    }
)
# 5 retries, exponential back-off
sess.mount(
    "https://",
    HTTPAdapter(
        max_retries=Retry(
            total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504]
        )
    ),
)
NBAStatsHTTP._session = sess        # monkey-patch the api client
# ----------------------------------------------------------------

from nba_api.stats.endpoints import LeagueGameLog


@asset(key_prefix=["raw"])
def leaguegamelog_2025() -> Output[pd.DataFrame]:
    """Backfill 2024-25 regular-season boxscores."""
    df = LeagueGameLog(season="2024-25", timeout=60).get_data_frames()[0]

    bq = bigquery.Client()
    table_id = "nba_raw.games"
    bq.load_table_from_dataframe(
        df,
        table_id,
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    ).result()

    yield Output(df, metadata={"rows": len(df)})
    return Output(df, metadata={"rows": len(df)})
