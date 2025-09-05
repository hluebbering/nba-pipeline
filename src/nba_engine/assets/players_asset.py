# nba_engine/assets/players_asset.py
from dagster import asset, MetadataValue, Nothing
from nba_engine.ingestion.players import load as load_players

@asset(name="players_master")
def players_master(context) -> Nothing:
    # load_players() truncates + reloads the BigQuery table
    load_players()
    context.add_output_metadata({"status": "refreshed"})
