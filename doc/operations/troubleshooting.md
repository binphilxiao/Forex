# Troubleshooting

Common problems you may encounter while running the toolkit and how to fix them.

## Downloading Data

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| "HTTP 403" in downloader logs | FXCM API temporarily rejecting requests. | Wait a few minutes and retry, or reduce concurrency by leaving default options. |
| Continuous retries until failure | Network outage or proxy interference. | Test `https://candledata.fxcorporate.com/` in a browser; configure outbound proxy if required. |
| Empty CSV files | Requesting a timeframe that does not exist for the pair. | Double-check with `--help`; FXCM provides M1 and D1 for the supplied pairs. |

## Importing into ClickHouse

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `Code: 516` authentication errors | Wrong username or password. | Regenerate `config/clickhouse_config.json` and rerun. |
| Duplicate key violations | Existing data overlaps with imports. | Run with `--mode comprehensive` to let the importer skip duplicates, or truncate tables manually. |
| Slow performance | Using comprehensive validation on large ranges. | Start with `--mode fast`; rerun comprehensive checks after confirming ingest. |

## Converting Timeframes

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Converter exits immediately | Missing source files. | Ensure `fxcm_data/<pair>/M1/<year>.csv` exists and matches the requested range. |
| Database mode fails | ClickHouse config missing or misconfigured. | Provide `--config <path>` or regenerate the JSON file. |

## Verification

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Report flags gaps for certain days | Market holidays or missing CSV segments. | Re-download the affected pair/timeframe or mark holidays as expected gaps. |
| ClickHouse mismatch | Import skipped rows or timezone mismatch. | Re-run the importer for the specific range; confirm both systems use UTC timestamps. |

## Web UI

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Page does not load | Flask server not running. | Start it via `python scripts\start_web.py` and keep the terminal open. |
| Buttons appear idle | Long-running script in progress. | Check the terminal logs; operations run in background threads and stream progress there. |

## General

- Run `python scripts\verify_docs.py --root .` to ensure documentation links stay valid.
- Use a Python virtual environment to avoid dependency clashes.
- Keep `logs/` under version control ignore rules; clean it before committing.
