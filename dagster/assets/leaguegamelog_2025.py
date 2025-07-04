from dagster import asset, Output
from nba_api.stats.endpoints import LeagueGameLog
import pandas as pd
from google.cloud import bigquery

@asset(key_prefix=["raw"])
def leaguegamelog_2025() -> Output[pd.DataFrame]:
    """Backfill 2024-25 regular-season boxscores."""
    df = LeagueGameLog(season="2024-25").get_data_frames()[0]

    bq = bigquery.Client()
    table_id = "nba_raw.games"
    bq.load_table_from_dataframe(
        df,
        table_id,
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    ).result()

    yield Output(df, metadata={"rows": len(df)})
