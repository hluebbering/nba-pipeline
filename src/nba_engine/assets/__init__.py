from .leaguegamelog import leaguegamelog           # or leaguegamelog_2025 if that’s the file
from .injuries_asset import injuries_raw
from .defense_asset import defense_raw
from .players_asset import players_master
from .boxscores_advanced_asset import boxscores_advanced_raw

all_assets = [
    leaguegamelog,
    injuries_raw,
    defense_raw,
    players_master,
    boxscores_advanced_raw
]
