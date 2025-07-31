from dagster import asset
from nba_engine.ingestion.boxscores_advanced import (
    fetch_player_boxscores_advanced, load_to_bigquery
)
import pathlib

@asset
def boxscores_advanced_raw():
    df = fetch_player_boxscores_advanced()
    load_to_bigquery(df)

    # optional local CSV drop (for debugging)
    if not df.empty:
        out = pathlib.Path("/tmp/player_boxscores_advanced_2024_25.csv")
        df.to_csv(out, index=False)
        print("Wrote copy to", out)

    return df
