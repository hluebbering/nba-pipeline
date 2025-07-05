from dagster import Definitions, load_assets_from_modules
from . import assets  # still nba_engine/assets/*.py

defs = Definitions(
    assets=load_assets_from_modules([assets]),
)
#from google.cloud import bigquery
#client = bigquery.Client()
#print(client.project)   # should print your GCP project ID
