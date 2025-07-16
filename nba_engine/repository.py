from dagster import Definitions, define_asset_job, ScheduleDefinition
# from dagster_gcp_pandas.bigquery import build_bigquery_io_manager   # ← NEW
from nba_engine.assets import all_assets

# ------------------------------------------------------------------
# Build the IO-manager instance
# ------------------------------------------------------------------
# bq_io_manager = build_bigquery_io_manager(
#     project="YOUR_GCP_PROJECT_ID",
#     location="US",                   # or your region
#     default_dataset="nba_raw",       # dataset all tables land in
# )

# Daily job & schedule (unchanged)
daily_job = define_asset_job("nba_daily_job", selection=all_assets)
daily_schedule = ScheduleDefinition(job=daily_job, cron_schedule="0 7 * * *")

# Definitions with the resource registered
defs = Definitions(
    assets=all_assets,
    schedules=[daily_schedule],
    #resources={"bigquery_io_manager": bq_io_manager},
)
