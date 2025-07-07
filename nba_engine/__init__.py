# nba_engine/__init__.py
import nba_engine.patch_http
from dotenv import load_dotenv; load_dotenv()
import nba_engine.proxy_patch  # ← must be first
from dagster import Definitions
from nba_engine.assets.leaguegamelog_2025 import leaguegamelog_2025  # object, not module!

# hand Dagster the real asset objects
defs = Definitions(assets=[leaguegamelog_2025])