from dagster import asset
from nba_engine.ingestion.boxscores_advanced import (
    fetch_player_boxscores_advanced, load_to_bigquery
)

@asset(
    io_manager_key="io_manager",
    
)
def boxscores_advanced_raw():
    """Players ▸ Box Scores ▸ Advanced (Regular-season, 2024-25)."""
    df = fetch_player_boxscores_advanced()    # DataFrame
    load_to_bigquery(df)                      # writes to BigQuery
    return df
