from dagster import asset, Output, MetadataValue
from nba_api.stats.endpoints import LeagueGameLog
import pandas as pd
from google.cloud import bigquery

@asset(key_prefix=["raw"])
def leaguegamelog_2025() -> Output[pd.DataFrame]:
    """One-off backfill for the 2024-25 season."""
    df = LeagueGameLog(season="2024-25").get_data_frames()[0]
    client = bigquery.Client()
    table_id = "nba_raw.games"
    client.load_table_from_dataframe(
        df, table_id,
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    ).result()

    yield Output(
        df,
        metadata={"rows": len(df), "preview": MetadataValue.md(df.head().to_markdown())}
    )
