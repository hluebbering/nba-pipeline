# src/nba_engine/assets/injuries_asset.py
from dagster import asset, MetadataValue, Nothing
from nba_engine.ingestion.injuries import _scrape
from google.cloud import bigquery
import os
import re

# ---- BigQuery target -------------------------------------------------------
PROJECT  = os.getenv("BIGQUERY_PROJECT")         # export BIGQUERY_PROJECT=<your-proj>
BQ_TABLE = f"{PROJECT}.nba_raw.stg_injury_updates"
# ----------------------------------------------------------------------------


def _bq_safe_cols(columns):
    """Convert column names to BigQuery-legal snake_case."""
    return (
        columns.str.lower()                          # lower-case
        .str.replace(r"[ .]", "_", regex=True)       # spaces & dots → _
        .str.replace(r"[^0-9a-z_]", "", regex=True)  # strip anything else
        .str.replace(r"__+", "_", regex=True)        # collapse repeats
        .str.strip("_")                              # no leading / trailing _
    )


@asset(name="injuries_raw", compute_kind="python")
def injuries_raw(context) -> Nothing:
    # 1 ▸ scrape ESPN tables
    df = _scrape()

    # 2 ▸ ensure **every** column name is BigQuery-safe
    df.columns = _bq_safe_cols(df.columns)

    # 3 ▸ load to BigQuery
    cfg = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
    bigquery.Client().load_table_from_dataframe(df, BQ_TABLE, job_config=cfg).result()

    # 4 ▸ metadata back to Dagster
    context.add_output_metadata(
        {"rows_added": len(df), "table": MetadataValue.md(f"`{BQ_TABLE}`")}
    )
