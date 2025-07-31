from dagster import asset, MetadataValue, Nothing
from nba_engine.ingestion.defense import fetch
from google.cloud import bigquery
import os

PROJECT  = os.getenv("BIGQUERY_PROJECT")
BQ_TABLE = f"{PROJECT}.nba_raw.stg_player_defense"


@asset(name="defense_raw", compute_kind="python")
def defense_raw(context) -> Nothing:
    df = fetch("2024-25")

    cfg = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    bigquery.Client().load_table_from_dataframe(df, BQ_TABLE, job_config=cfg).result()

    context.add_output_metadata(
        {"rows_added": len(df), "table": MetadataValue.md(f"`{BQ_TABLE}`")}
    )


