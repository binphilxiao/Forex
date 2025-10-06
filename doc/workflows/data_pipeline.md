# Data Pipeline Playbook

This playbook shows how to run the full download → import → transform → verify workflow, either from the command-line or the bundled web UI.

## Prerequisites

1. Install dependencies: `pip install -r requirements.txt` (inside the project virtual environment).
2. (Optional) Provision ClickHouse and make sure it is reachable from the machine running the scripts.
3. Generate a ClickHouse config once:
   ```powershell
   python scripts\clickhouse_configurator.py --host 127.0.0.1 --user default --database forex
   ```
   The wizard stores credentials in `config\clickhouse_config.json`.

## Step 1: Download Historical Data

```powershell
python scripts\fxcm_data_downloader.py \
  --pairs EURUSD GBPUSD USDJPY \
  --timeframes M1 D1 \
  --start-year 2018 --end-year 2025
```

- Files are written to `fxcm_data/<pair>/<timeframe>/<year>.csv`.
- Logs (`logs/fxcm_download_*.log`) include retry counts, skipped files, and totals.

### Tips
- Omit `--pairs` or `--timeframes` to accept all defaults (six pairs, M1 and D1).
- Use `--max-retries` when the public API is flaky.

## Step 2: Import into ClickHouse (optional but recommended)

```powershell
python scripts\fxcm_importer.py \
  --mode fast \
  --pairs EURUSD GBPUSD \
  --timeframes M1 \
  --start-year 2018 --end-year 2025
```

- `--mode fast` validates row counts quickly; `--mode comprehensive` runs additional gap checks.
- The importer reads `config/clickhouse_config.json` unless you override parameters on the CLI.

## Step 3: Build Higher Timeframes

### Local aggregation (no database required)
```powershell
python scripts\m1_timeframe_converter.py \
  --mode local \
  --output-dir fxcm_data_aggregated \
  --targets M5 M15 M30 H1 \
  --pair EURUSD \
  --start-year 2020 --end-year 2025
```

### ClickHouse aggregation
```powershell
python scripts\m1_timeframe_converter.py \
  --mode database \
  --targets M5 H1 \
  --pair EURUSD
```

## Step 4: Verify Data Consistency

```powershell
python scripts\verify_data_consistency.py \
  --pair EURUSD \
  --timeframe M1 \
  --mode comprehensive
```

The report compares CSV row counts against ClickHouse, highlights gaps, and stores a detailed log in `logs/`.

## Alternate Path: Web UI

```powershell
python scripts\start_web.py --host 127.0.0.1 --port 5000
```

- Navigate to `http://127.0.0.1:5000`.
- Buttons trigger the same scripts with sensible defaults.
- Review live status in the terminal that launched the server.

## Housekeeping

- Archive or rotate the `logs/` directory to prevent growth.
- Maintain the ClickHouse connection settings in `config/clickhouse_config.json`.
- Run `python scripts\verify_docs.py` after documentation edits.
