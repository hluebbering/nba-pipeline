# nba_engine/__init__.py  ← exactly this, nothing fancy
from dagster import Definitions, load_assets_from_modules

# import the Python module that holds your @asset definitions
from . import assets              # nba_engine/assets/__init__.py can be empty
from .assets import leaguegamelog_2025  # ensures the file is imported

defs = Definitions(
    assets=load_assets_from_modules([assets]),
)
