from dagster import asset, Output
from nba_api.stats.endpoints import LeagueGameLog
from nba_api.stats.library.http import NBAStatsHTTP     # ← fix path
from requests.adapters import HTTPAdapter, Retry
import pandas as pd, requests
from google.cloud import bigquery

# 1️⃣ headers & retry
NBAStatsHTTP.return_response_headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://stats.nba.com",
    "Origin": "https://stats.nba.com",
}
sess = requests.Session()
sess.mount("https://", HTTPAdapter(max_retries=Retry(total=5, backoff_factor=1)))
NBAStatsHTTP._session = sess

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



# Load data into BigQuery
# bq = bigquery.Client()
# table_id = "nba_raw.games"
# job_config = bigquery.LoadJobConfig(
#     write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
# )
# load_job = bq.load_table_from_dataframe(df, table_id, job_config=job_config)
# load_job.result()  # Wait for the job to complete

