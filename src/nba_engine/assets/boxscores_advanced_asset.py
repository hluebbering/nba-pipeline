# src/nba_engine/assets/boxscores_advanced_asset.py
from dagster import asset
from nba_engine.ingestion.boxscores_advanced import (
    fetch_player_boxscores_advanced, load_to_bigquery
)

@asset
def boxscores_advanced_raw():
    df = fetch_player_boxscores_advanced()
    load_to_bigquery(df)
    return df