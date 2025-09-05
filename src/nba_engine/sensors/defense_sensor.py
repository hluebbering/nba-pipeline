"""
Daily sensor that checks whether the NBA 2024-25 defensive CSV is live.
As soon as it gets HTTP 200 it triggers a one-asset run to materialize
`defense_raw`, which will also cache the file locally for all future
runs.
"""

from dagster import DefaultSensorStatus, RunRequest, sensor
import requests
from nba_engine.assets.defense_asset import defense_raw
from nba_engine.ingestion.defense import URL

@sensor(
    job_name="__ASSET_JOB_DEFENSE_ONLY__",
    minimum_interval_seconds=60 * 60 * 4,   # every 4 hours
    default_status=DefaultSensorStatus.RUNNING,
)
def defense_csv_ready_sensor(context):
    try:
        # HEAD is lighter than GET & enough to know the file exists
        resp = requests.head(URL, timeout=10)
        if resp.status_code == 200:
            return RunRequest(
                run_key=f"defense_csv_{resp.headers.get('Last-Modified', 'now')}",
                run_config={
                    "ops": {"defense_raw": {}},
                },
                tags={"trigger": "defense_csv_ready_sensor"},
            )
        # else: 404, 503, etc. — just wait for next tick
    except Exception as exc:  # noqa: BLE001
        context.log.debug("CSV still offline: %s", exc)

    # Return None suppresses run creation for this tick
    return None
