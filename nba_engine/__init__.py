# nba_engine/__init__.py
from dagster import Definitions
from nba_engine.assets.leaguegamelog_2025 import leaguegamelog_2025  # object, not module!

defs = Definitions(
    assets=[leaguegamelog_2025],   # hand Dagster the real asset objects
)
