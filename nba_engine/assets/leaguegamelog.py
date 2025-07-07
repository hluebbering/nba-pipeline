# nba_engine/assets/leaguegamelog.py
from dagster import (
    asset,
    Output,
    StaticPartitionsDefinition,
    AssetOut,
    multi_asset,
    MetadataValue,
)
from nba_engine.patch_http import nba_get
from google.cloud import bigquery
import pandas as pd

SEASONS = [f"{yr}-{str(yr+1)[2:]}" for yr in range(2014, 2025)]  # 2014-15 … 2024-25
partitions = StaticPartitionsDefinition(SEASONS)


@asset(partitions_def=partitions, key_prefix=["raw"])
def leaguegamelog(context) -> Output[pd.DataFrame]:
    season = context.partition_key

    raw = nba_get(
        "leaguegamelog",
        {
            "Counter": 0,
            "Direction": "ASC",
            "LeagueID": "00",
            "PlayerOrTeam": "T",
            "Season": season,
            "SeasonType": "Regular Season",
            "Sorter": "DATE",
        },
    )
    df = pd.DataFrame(
        raw["resultSets"][0]["rowSet"],
        columns=raw["resultSets"][0]["headers"],
    )

    table = f"nba_raw.games_{season.replace('-', '_')}"
    bigquery.Client().load_table_from_dataframe(
        df,
        table,
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE"),
    ).result()

    return Output(
        df,
        metadata={
            "rows": len(df),
            "bq_table": MetadataValue.md(f"`{table}`"),
        },
    )






# # nba_engine/assets/leaguegamelog_2025.py
# from dagster import asset, Output
# from nba_engine.patch_http import nba_get        # ← your working helper
# from google.cloud import bigquery
# import pandas as pd

# @asset(key_prefix=["raw"])
# def leaguegamelog_2025() -> Output[pd.DataFrame]:
#     """
#     Loads 2024-25 regular-season team game logs from stats.nba.com
#     through ScraperAPI premium (country_code=eu) and writes them to
#     BigQuery table nba_raw.games_2025.
#     """

#     raw = nba_get(
#         "leaguegamelog",
#         {
#             "Counter": 0,
#             "Direction": "ASC",
#             "LeagueID": "00",
#             "PlayerOrTeam": "T",
#             "Season": "2024-25",
#             "SeasonType": "Regular Season",
#             "Sorter": "DATE",
#         },
#     )

#     df = pd.DataFrame(
#         raw["resultSets"][0]["rowSet"],
#         columns=raw["resultSets"][0]["headers"],
#     )

#     bigquery.Client().load_table_from_dataframe(
#         df,
#         "nba_raw.games_2025",
#         job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE"),
#     ).result()

#     return Output(df, metadata={"rows": len(df)})
