# nba_engine/__init__.py
from dotenv import load_dotenv; load_dotenv()

import nba_engine.patch_http          # keeps the scraper helper registered
import nba_engine.proxy_patch         # if you still need it elsewhere

# ✅ import the partitioned asset we just created
from nba_engine.assets.leaguegamelog import leaguegamelog

from dagster import Definitions

defs = Definitions(assets=[leaguegamelog])
