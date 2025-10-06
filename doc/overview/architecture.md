# System Architecture

The toolkit automates the FXCM data lifecycle. The architecture is intentionally simple so that you can operate it from scripts or the bundled web UI.

```
┌─────────────┐      ┌────────────────┐      ┌────────────────────┐      ┌────────────────────┐
│ FXCM API    │ ---> │ Downloader     │ ---> │ ClickHouse Database│ ---> │ Consistency Checks │
└─────────────┘      │ fxcm_data_*.py │      │ (optional for M1)  │      │ verify_*.py        │
                     └────────────────┘      └────────────────────┘      └────────────────────┘
                                     ↘                                ↗
                                      └─────┬────────────┬────────────┘
                                            │            │
                                            │            └─► Multi-timeframe converter (`m1_timeframe_converter.py`)
                                            └─► Web UI orchestrator (`start_web.py` + `flask_app.py`)
```

## Core Components

- **Data acquisition** — `scripts/fxcm_data_downloader.py` pulls historical candles by pair, timeframe, and year range. Files are written to `fxcm_data/` and every run logs to `logs/`.
- **Database configuration** — `scripts/clickhouse_configurator.py` captures ClickHouse credentials and writes `config/clickhouse_config.json`. Helper scripts (`create_clickhouse_tables.py`, `view_clickhouse_tables.py`) reuse the same config.
- **Data import** — `scripts/fxcm_importer.py` loads the CSV archive into ClickHouse with fast or comprehensive validation modes.
- **Transformation** — `scripts/m1_timeframe_converter.py` aggregates M1 candles locally or in ClickHouse to produce higher timeframes.
- **Quality verification** — `scripts/verify_data_consistency.py` compares CSV files versus the database to confirm row counts, date ranges, and gap checks.
- **User interface** — `scripts/start_web.py` hosts a Flask dashboard (defined in `scripts/flask_app.py`) that wires the same pipeline into buttons.

## Directories at a Glance

| Directory        | Role                                                       |
|------------------|------------------------------------------------------------|
| `fxcm_data/`     | Downloaded CSV exports organised by pair/timeframe/year.   |
| `logs/`          | Execution logs and summary reports for downloader/importer.|
| `config/`        | Generated `clickhouse_config.json` connection profile.      |
| `scripts/`       | Python entry points and support utilities.                 |
| `templates/`     | HTML templates used by the Flask web UI.                   |

## External Dependencies

- **Python 3.8+** with `requests`, `pandas`, `clickhouse-driver`, and Flask for the optional UI.
- **ClickHouse** (local or remote) when you need database-backed importing or aggregation. Local CSV workflows work without it.
- **FXCM public candle API** accessible via HTTPS.

## Security Considerations

- Secrets stay inside `config/clickhouse_config.json`; do not commit this file.
- Logs may include connection targets and summary stats—scrub before sharing externally.
- When exposing the web UI, run it behind authentication or a VPN; there is no built-in access control.
