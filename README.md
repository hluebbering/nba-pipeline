# NBA Player Performance Prediction Pipeline

> Build a reusable pipeline that ingests multi‑modal NBA data, transforms it in BigQuery, and serves advanced models & dashboards that explain storylines (e.g., Pacers’ Game 7 push) and project future performance (e.g., Timberwolves 2025 season outlook).


This project builds an end-to-end pipeline to predict NBA player performance for upcoming games, with a focus on points scored. It integrates multiple data sources — player game logs, advanced efficiency metrics, lineup and injury data, opponent strength, and analyst projections — to generate features that capture both player trends and matchup context.

## Key highlights:

- Feature Engineering: Rolling averages, efficiency metrics (TS%, EFF, USG%), opponent-specific stats, and lineup adjustments.
- Modeling: Ensemble methods (CatBoost, RandomForest) and Bayesian regression to balance interpretability and predictive accuracy.
- Pipeline Design: Bulk ingestion via NBA API and ESPN scrape, optimized with parallelization and caching to reduce latency.
- Evaluation: RMSE and R² on next-game predictions; scenario testing with injury/rotation shocks.
- Interview Prep Angle: Demonstrates advanced SQL/ETL, causal inference thinking (injury/rotation as natural experiments), and storytelling around model-driven insights.

This pipeline mirrors real-world data science workflows: ingesting messy sports data, building robust features, optimizing pipelines, and translating outputs into actionable insights for decision-making.



---


## Core Questions

1. **Player performance forecasting** – How many points, USG%, TS%, etc. will a player post next game?
2. **Team over/under‑performance** – Which clubs are beating—or falling short of—their underlying metrics and why?
3. **Narrative validation** – Are fatigue, lineup tweaks, or media sentiment driving momentum swings?
4. **Season simulations** – What are team win totals & playoff odds under Monte‑Carlo runs?

## Objectives

- 🏀 **Player Models** – CatBoost/JAX‑Boost next‑game projections.
- 🔮 **Team Sims** – ELO + Gradient‑Boost matchup engine.
- 📊 **Storyline Analytics** – Quantify fatigue, sentiment, clutch streaks.
- ⏱ **Flexible Scheduling** – Daily in‑season, weekly off‑season, on‑demand triggers.

## Architecture

<details>

```mermaid
flowchart TD
  A[Dagster Assets] -->|APIs & Scrapers| B(GCS Raw)
  B --> C(BigQuery Bison: raw -> core -> marts)
  C --> D(dbt 1.9 + Mesh)
  D --> E(Feast Feature Store)
  E --> F[CatBoost GPU / JAX‑Boost]
  D --> G(Streamlit 2.0 Dashboards)
  C --> H(FastAPI + Arrow Flight SQL)
```

</details>




### Pipeline Steps

1. **Ingest** – Dagster + Fugue parallel pulls from `nba_api`, ESPN Inactives, Second Spectrum, Twitter v2, GDELT.
2. **Stage** – Versioned Parquet in GCS; DuckDB Cloud Cache for local dev.
3. **Warehouse** – Partitioned/clustered BigQuery (Bison release).
4. **Transform** – dbt tests, docs, macros; feature marts.
5. **Feature Store** – Feast on BigQuery.
6. **Model** – MLflow 3.0 experiments; scheduled retrain.
7. **Serve** – Streamlit 2.0 dashboards + REST/gRPC endpoints.
8. **CI/CD** – GitHub Actions, Dagster Deployments, dbt Cloud jobs.

## Data Sources

| Domain             | Example Fields              | Primary Source           |
| ------------------ | --------------------------- | ------------------------ |
| Box/Play‑by‑play   | points, fouls, possessions  | `nba_api` bulk endpoints |
| Advanced Metrics   | ORTG, TS%, PACE             | Basketball‑Reference     |
| Injuries & Lineups | player status, DNPs         | ESPN scraper             |
| Player Tracking    | shot distance, speed        | Second Spectrum          |
| Social Sentiment   | tweets per player, polarity | Twitter API v2           |
| News Tone          | headline sentiment          | GDELT RSS                |

## Tech Stack

| Layer               | Tooling                                           |
| ------------------- | ------------------------------------------------- |
| Language            | Python 3.11 (pandas, **polars**, RAPIDS cuDF)     |
| Ingestion           | Dagster 1.6, Fugue, Ray                           |
| Storage             | GCS, BigQuery **Bison**                           |
| Transform           | dbt 1.9 + Mesh                                    |
| Feature Store       | Feast                                             |
| Modeling            | CatBoost GPU, LightGBM v5, **JAX‑Boost**, Prophet |
| Experiment Tracking | MLflow 3.0                                        |
| Visualization       | Streamlit 2.0, Looker Studio                      |
| Orchestration       | Dagster Deployments                               |
| CI/CD               | GitHub Actions, dbt Cloud                         |

## Project Structure

```text
nba-pipeline/
├── .github/workflows/        # CI pipelines
├── dagster/                  # Dagster asset definitions
├── dbt/                      # dbt project (sources, models, tests)
├── notebooks/                # EDA & storyline notebooks
├── src/
│   ├── ingestion/            # API clients & scrapers
│   ├── features/             # Feature engineering code
│   └── models/               # Training & inference
├── streamlit_app/            # Dashboard code
└── README.md
```

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

## Roadmap

| Phase | Target Date | Milestone                                   |
| ----- | ----------- | ------------------------------------------- |
| P0    | **Day 3**   | Repo scaffold + raw games in BigQuery       |
| P1    | **Week 2**  | dbt staging & marts for boxscore + injuries |
| P2    | **Week 4**  | MVP CatBoost player model (RMSE benchmark)  |
| P3    | **Month 2** | Team simulation & sentiment integration     |
| P4    | **Month 3** | Streamlit dashboards + automated scheduling |



- Week 0 – Stand up GCP project, BQ datasets, and Composer; commit repo skeleton.
- Week 1 – Ingest/backfill game logs 2014-2025; populate dim_*, fct_boxscore.
- Week 2 – Build dbt models for rolling player stats + team ELO; validate with Looker.
- Week 3 – Baseline CatBoost model: predict next-game points (features = last-10 rolling stats, minutes, opponent DRTG, rest days).
- Week 4 – Case study: Pacers-OKC series. Join fatigue (games in 14 days), social sentiment, and Net Rating trend; write blog-style notebook.


--------------------------------------


## Results


- Target: Predict player points in next game  
- Planned models: CatBoost, RandomForest, Bayesian Ridge  
- Metrics: RMSE and R² on test set  
- Results will be updated once modeling is complete


•	Example: “Model predicts player points using CatBoost with RMSE ≈ 5.2 and R² ≈ 0.72 across test set.”


--------------------------------------





## Contributing

PRs welcome! See `CONTRIBUTING.md` for guidelines & DCO.

## License

MIT © 2025 Hannah L.

---


