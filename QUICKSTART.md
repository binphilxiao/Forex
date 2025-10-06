# Quick Start

This guide trims the pipeline down to the essentials so you can go from zero to a verified ClickHouse dataset in minutes.

## 1. Prepare the Environment

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Optional but handy:
- Add `.venv/`, `logs/`, and `fxcm_data/` to your `.gitignore` (already configured).
- Export `CLICKHOUSE_HOST`, `CLICKHOUSE_USER`, and `CLICKHOUSE_PASSWORD` if you do not want to store secrets on disk.

## 2. Configure ClickHouse (once)

```powershell
python scripts\clickhouse_configurator.py \
  --host 127.0.0.1 \
  --port 9000 \
  --database forex
```

The wizard writes `config\clickhouse_config.json`. Use `--no-test` when ClickHouse is unreachable but you still want to prepare the file.

## 3. Download Data

```powershell
python scripts\fxcm_data_downloader.py \
  --pairs EURUSD GBPUSD USDJPY \
  --timeframes M1 D1 \
  --start-year 2018 --end-year 2025
```

Outputs land in `fxcm_data/<pair>/<timeframe>/<year>.csv` and the run is logged in `logs/fxcm_download_<timestamp>.log`.

### Common Variations

| Goal | Command |
|------|---------|
| Download a single pair | `python scripts\fxcm_data_downloader.py --pairs EURUSD`
| Only daily candles | `python scripts\fxcm_data_downloader.py --timeframes D1`
| Short burst for testing | `python scripts\fxcm_data_downloader.py --start-year 2024 --end-year 2024`

## 4. Import into ClickHouse

```powershell
python scripts\fxcm_importer.py \
  --mode fast \
  --pairs EURUSD GBPUSD \
  --timeframes M1 \
  --start-year 2018 --end-year 2025
```

- `--mode fast` checks row counts quickly. Switch to `--mode comprehensive` for gap detection.
- Override the config path with `--config <file>` when needed.

## 5. Build Higher Timeframes

```powershell
python scripts\m1_timeframe_converter.py \
  --mode local \
  --pair EURUSD \
  --targets M5 M15 H1 \
  --start-year 2020 --end-year 2025 \
  --output-dir fxcm_data_aggregated
```

For database aggregation swap `--mode database` and remove `--output-dir` (results are written back to ClickHouse).

## 6. Verify Consistency

```powershell
python scripts\verify_data_consistency.py \
  --pair EURUSD \
  --timeframe M1 \
  --mode comprehensive
```

The script produces a terminal summary and stores a full report in `logs/verify_data_consistency_<timestamp>.log`.

## 7. Optional Web Interface

```powershell
python scripts\start_web.py --host 127.0.0.1 --port 5000
```

Open `http://127.0.0.1:5000` and use the buttons to trigger download, import, conversion, and verification jobs. Progress streams to the console.

## 8. Clean Up and Maintain

- Rotate or archive `logs/` periodically.
- Re-run the configurator when credentials change.
- Use `python scripts\verify_docs.py` after editing documentation.
- Record noteworthy workflow updates in `doc/CHANGELOG.md`.

For deeper dives, see `doc/workflows/data_pipeline.md` and `doc/reference/script_catalog.md`.
