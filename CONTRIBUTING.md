
## Setup

```bash
# 0.  make sure bzip2 is present (usually is)
sudo apt-get update -y && sudo apt-get install -y bzip2

# 1.  fetch + unpack straight into /usr/local/bin
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest \
| sudo tar -xvjf - -C /usr/local/bin --strip-components=1 bin/micromamba

# 2.  verify
micromamba --version

# 3.  create & activate the env
micromamba create -y -n nba-engine -f env.yml
# eval "$(micromamba shell hook --shell bash)" # add micromamba hook to this shell only
micromamba activate nba-engine
```


--------------------------------------



## Quickstart

```bash
# Run Dagster locally
pip install -e . 
pkill -f dagster || true   # stop old server
dagster dev -w workspace.yaml

# Backfill 2023‑24 game logs
python src/ingestion/backfill_games.py --season 2024

# Build dbt models
dbt build --select tag:core
```



--------------------------------------


# Notes

export SCRAPERAPI_KEY="xxxxxxx"
echo 'export GOOGLE_APPLICATION_CREDENTIALS=/workspaces/.gcp/key.json' >> ~/.bashrc


--------------------------------------


curl -i \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36" \
  -H "Referer: https://stats.nba.com" \
  -H "Origin: https://www.nba.com" \
  -H "x-nba-stats-token: true" \
  -H "x-nba-stats-origin: stats" \
  "https://api.scraperapi.com?api_key=$KEY&premium=true&keep_headers=true&country_code=eu&retry=3&timeout=90000&url=https%3A%2F%2Fstats.nba.com%2Fstats%2Fleaguegamelog%3FCounter%3D0%26Direction%3DASC%26LeagueID%3D00%26PlayerOrTeam%3DT%26Season%3D2024-25%26SeasonType%3DRegular%2BSeason%26Sorter%3DDATE"



python - <<'PY'
from nba_engine.patch_http import nba_get
rows = nba_get(
    "leaguegamelog",
    {
        "Counter": 0, "Direction": "ASC",
        "LeagueID": "00", "PlayerOrTeam": "T",
        "Season": "2024-25", "SeasonType": "Regular Season",
        "Sorter": "DATE",
    },
)["resultSets"][0]["rowSet"]
print("leaguegamelog rows →", len(rows))
PY



# start Dagster UI
dagster dev -m nba_engine.repository
export BIGQUERY_PROJECT="nba-insight-dev"
dagster asset materialize --select injuries_raw -m nba_engine.repository




git clone https://github.com/hluebbering/nba-pipeline.git ~/nba-pipeline

python3 ~/nba-pipeline/src/nba_engine/ingestion/boxscores_advanced.py --bq

# Player boxscores-advanced → BigQuery  (03:15 UTC every day)
15 3 * * * . $HOME/nba-venv/bin/activate && GOOGLE_APPLICATION_CREDENTIALS=$HOME/nba-loader.json python $HOME/nba-pipeline/src/nba_engine/ingestion/boxscores_advanced.py --bq >> $HOME/boxscores.log 2>&1


```bash
export GOOGLE_APPLICATION_CREDENTIALS=$HOME/nba-loader.json
export PYTHONPATH=$HOME/nba-pipeline/src:$PYTHONPATH

python - <<'PY'
import json, pprint, datetime as dt
from google.cloud import bigquery
from nba_engine.ingestion import boxscores_advanced as bx

PROJECT   = "nba-insight-dev"
TABLE_ID  = "nba_raw.player_boxscores_advanced"   # short form ok

df = bx.fetch_player_boxscores_advanced()
print("• DataFrame rows =", len(df))

client = bigquery.Client(project=PROJECT)
job = client.load_table_from_dataframe(
        df,
        TABLE_ID,
        job_config=bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",
            # Uncomment next line if your dataset is *US*:
            # location="US",
        ),
)
print("• Job ID:", job.job_id)
job.result(retry=None)         # wait for finish

if job.error_result:
    print("\n=== BIGQUERY ERROR RESULT ===")
    pprint.pp(job.error_result)
    print("\n=== BIGQUERY ERRORS (list) ===")
    pprint.pp(job.errors)
else:
    tbl = client.get_table(TABLE_ID)
    print(f"\n✓ Loaded {tbl.num_rows:,} rows at",
          dt.datetime.utcnow().isoformat(timespec='seconds'))
PY

```
