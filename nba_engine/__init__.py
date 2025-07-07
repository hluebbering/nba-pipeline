from dagster import Definitions
from .assets import leaguegamelog_2025   # 👈 force-import the file

defs = Definitions(assets=[leaguegamelog_2025])