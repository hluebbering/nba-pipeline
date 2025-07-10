# nba_engine/assets/injuries_asset.py
from dagster import asset, MetadataValue, Nothing
from nba_engine.ingestion.injuries import _scrape  # reuse scraper already written
from google.cloud import bigquery

BQ_TABLE = "myproject.nba_raw.stg_injury_updates"   # <- adjust once

@asset(
    name="injuries_raw",                # shows up as that name in Dagster UI
    io_manager_key="bigquery_io_manager",
    compute_kind="python",
)
def injuries_raw(context) -> Nothing:
    df = _scrape()

    bigquery.Client().load_table_from_dataframe(
        df,
        BQ_TABLE,
        job_config={"write_disposition": "WRITE_APPEND"},
    ).result()

    context.add_output_metadata(
        {
            "rows_added": len(df),
            "table": MetadataValue.md(f"`{BQ_TABLE}`"),
        }
    )
