# nba_engine/assets/defense_asset.py
from dagster import asset, MetadataValue, Nothing
from nba_engine.ingestion.defense import fetch
from google.cloud import bigquery

BQ_TABLE = "myproject.nba_raw.stg_player_defense"

@asset(
    name="defense_raw",
    io_manager_key="bigquery_io_manager",
)
def defense_raw(context) -> Nothing:
    df = fetch(season="2024-25")

    bigquery.Client().load_table_from_dataframe(
        df,
        BQ_TABLE,
        job_config={"write_disposition": "WRITE_APPEND"},
    ).result()

    context.add_output_metadata(
        {"rows_added": len(df), "table": MetadataValue.md(f"`{BQ_TABLE}`")}
    )
