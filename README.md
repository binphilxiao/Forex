# Forex Data Pipeline Toolkit

A batteries-included toolkit for downloading, importing, transforming, and validating FXCM historical forex data. The project bundles command-line tools and a lightweight web UI so you can automate or orchestrate the full pipeline end to end.

![Version](https://img.shields.io/badge/version-5.0.7-blue.svg) ![Python](https://img.shields.io/badge/python-3.8+-green.svg) ![License](https://img.shields.io/badge/license-MIT-orange.svg)

## Why It Exists

- Collect reliable FXCM candle data (M1 and D1) across six core currency pairs.
- Centralise configuration and logging for repeatable data operations.
- Offer fast and comprehensive validation paths before analytics or trading use.
- Provide both CLI automation and a guided web front-end for analysts.

## Key Components

| Stage | Tooling | Highlights |
|-------|---------|------------|
| Download | `scripts/fxcm_data_downloader.py` | Retry-aware downloader that stores CSV data under `fxcm_data/` and writes detailed logs. |
| Configure | `scripts/clickhouse_configurator.py` | Interactive wizard that builds `config/clickhouse_config.json` for all database-aware scripts. |
| Import | `scripts/fxcm_importer.py` | Bulk loader for ClickHouse with fast vs comprehensive validation modes. |
| Transform | `scripts/m1_timeframe_converter.py` | Aggregates M1 data locally or via ClickHouse into higher timeframes. |
| Verify | `scripts/verify_data_consistency.py` | Ensures CSV files and database tables stay in sync. |
| Orchestrate | `scripts/start_web.py` + `scripts/flask_app.py` | Flask UI with buttons for the full workflow. |

## Requirements

- Python 3.8 or newer
- `pip install -r requirements.txt`
- Optional: ClickHouse server (local or remote) when you need database storage or SQL aggregation

## Quick Start

```powershell
# 1. Activate your virtual environment and install dependencies
pip install -r requirements.txt

# 2. Download the default data set (all pairs, M1 and D1, 2015-present)
python scripts\fxcm_data_downloader.py

# 3. Create a ClickHouse connection profile (optional but recommended)
python scripts\clickhouse_configurator.py --host 127.0.0.1 --database forex

# 4. Import into ClickHouse with fast validation
python scripts\fxcm_importer.py --mode fast

# 5. Convert M1 -> M5/M15 locally
python scripts\m1_timeframe_converter.py --mode local --targets M5 M15

# 6. Verify CSV vs database consistency
python scripts\verify_data_consistency.py --pair EURUSD --timeframe M1
```

Launch the helper UI instead of the CLI by running `python scripts\start_web.py`.

## Documentation Map

- `QUICKSTART.md` — hands-on walkthrough with ready-to-run command blocks
- `doc/README.md` — documentation hub and navigation
- `doc/workflows/data_pipeline.md` — detailed pipeline guide
- `doc/reference/script_catalog.md` — script cheat sheet
- `doc/reference/configuration.md` — ClickHouse configuration schema
- `doc/operations/troubleshooting.md` — common issues and resolutions
- `doc/CHANGELOG.md` — release history

## Project Layout

```
Forex/
├── config/                  # Generated ClickHouse configuration
├── doc/                     # Documentation hub (see doc/README.md)
├── fxcm_data/               # Downloaded CSV data
├── logs/                    # Execution logs and summary reports
├── scripts/                 # Python entry points and helpers
├── templates/               # Flask UI templates
├── QUICKSTART.md            # Extended tutorial
└── README.md                # This file
```

## Contributing

1. Create a feature branch.
2. Update or add documentation alongside code changes.
3. Run `python scripts\verify_docs.py` and relevant tests before opening a pull request.
4. Describe behavioural changes in `doc/CHANGELOG.md`.

MIT licensed. Built by data engineers for repeatable forex data workflows.
