# nba_engine/__init__.py
from dagster import Definitions
# 1️⃣  import the ASSET OBJECT, not the module
from .assets.leaguegamelog_2025 import leaguegamelog_2025

# 2️⃣  hand the object to Dagster
defs = Definitions(assets=[leaguegamelog_2025])
