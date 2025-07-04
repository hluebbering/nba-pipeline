# NBA Insight Engine

> Build a reusable pipeline that ingests multi‑modal NBA data, transforms it in BigQuery, and serves advanced models & dashboards that explain storylines (e.g., Pacers’ Game 7 push) and project future performance (e.g., Timberwolves 2025 season outlook).


- [Core Questions](#core-questions)
- [Objectives](#objectives)
- [Architecture](#architecture)
- [Data Sources](#data-sources)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Quickstart](#quickstart)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

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
# clone repo
$ git clone https://github.com/<your-handle>/nba-pipeline.git
$ cd nba-pipeline

# create env
$ conda env create -f env.yml
$ conda activate nba-engine

# copy configs
$ cp .env.example .env  # fill in API keys
```

## Quickstart

```bash
# Run Dagster locally
dagster dev

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

## Contributing

PRs welcome! See `CONTRIBUTING.md` for guidelines & DCO.

## License

MIT © 2025 Hannah L.

---
