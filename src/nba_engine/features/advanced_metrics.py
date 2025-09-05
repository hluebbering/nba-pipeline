"""
Pure-Python helpers for TS%, eFG%, USG% – can be called inside dbt, Dagster, or notebooks.
"""

import pandas as pd
TS_DEN = lambda row: (2 * (row.FGA + 0.44 * row.FTA))

def add_advanced_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ts_pct"]  = out.apply(lambda r: r.PTS / TS_DEN(r) if TS_DEN(r) else None, axis=1)
    out["efg_pct"] = (out.FGM + 0.5 * out.FG3M) / out.FGA.replace(0, pd.NA)
    out["usg_pct"] = 100 * (
        (out.FGA + 0.44 * out.FTA + out.TOV) * (out.TEAM_MIN / 5)
    ) / (
        out.MIN * (out.TEAM_FGA + 0.44 * out.TEAM_FTA + out.TEAM_TOV)
    )
    return out
