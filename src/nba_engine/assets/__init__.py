from .leaguegamelog import leaguegamelog           # or leaguegamelog_2025 if that’s the file
from .injuries_asset import injuries_raw
from .defense_asset import defense_raw
from .players_asset import players_master

all_assets = [
    leaguegamelog,
    injuries_raw,
    defense_raw,
    players_master,
]
