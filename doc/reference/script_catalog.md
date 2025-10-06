# Script Catalogue

A two-minute reference for the Python entry points located in `scripts/`.

| Script | Purpose | Most Useful Flags |
|--------|---------|-------------------|
| `fxcm_data_downloader.py` | Fetch FXCM historical candles to `fxcm_data/`. | `--pairs`, `--timeframes`, `--start-year`, `--end-year`, `--max-retries` |
| `fxcm_importer.py` | Load downloaded CSV data into ClickHouse. | `--mode`, `--pairs`, `--timeframes`, `--start-year`, `--end-year`, `--config` |
| `m1_timeframe_converter.py` | Create aggregated timeframes from M1 data (local or ClickHouse). | `--mode`, `--targets`, `--pair`, `--start-year`, `--end-year`, `--output-dir` |
| `verify_data_consistency.py` | Compare CSV data versus ClickHouse for gaps and mismatches. | `--pair`, `--timeframe`, `--mode`, `--start-year`, `--end-year` |
| `clickhouse_configurator.py` | Interactive wizard to create `config/clickhouse_config.json`. | `--host`, `--port`, `--user`, `--database`, `--no-test` |
| `create_clickhouse_tables.py` | Create or refresh ClickHouse tables using the shared config. | `--config`, `--database`, `--force` |
| `view_clickhouse_tables.py` | List ClickHouse tables and row counts. | `--config`, `--database`, `--tables` |
| `convert_m1_to_multi_timeframes.py` | Legacy converter preserved for compatibility; prefer `m1_timeframe_converter.py`. | `--output-dir`, `--pairs`, `--timeframes` |
| `start_web.py` | Launch the Flask orchestration UI. | `--host`, `--port`, `--debug` |
| `flask_app.py` | Flask application module used by the web UI. | Environment variables: `FXCM_WEB_DEBUG`, `FLASK_RUN_PORT` |
| `verify_docs.py` | Markdown link validator and structure checker. | `--root`, `--verbose` |

## Usage Notes

- Each script exposes `--help` for the full argument list and defaults.
- Scripts look for `config/clickhouse_config.json`; override with `--config` when needed.
- Windows batch wrappers are optional; the Python commands are the source of truth.
