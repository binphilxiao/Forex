# Configuration Reference

All scripts that talk to ClickHouse share the same configuration file: `config/clickhouse_config.json`.

## Schema

```json
{
  "host": "127.0.0.1",
  "port": 9000,
  "http_port": 8123,
  "interserver_http_port": 9009,
  "user": "default",
  "password": "***",
  "database": "forex"
}
```

- `host` — ClickHouse server hostname or IP.
- `port` — Native TCP port (default 9000).
- `http_port` — HTTP interface (used by health checks).
- `interserver_http_port` — Optional; leave default for single-node setups.
- `user` / `password` — Credentials with read/write access to the target database.
- `database` — Logical database that stores forex datasets.

## Managing the File

1. Generate it with `python scripts\clickhouse_configurator.py` and answer the prompts.
2. Store secrets securely; do not commit this file.
3. Regenerate or edit the file whenever server credentials change.

## Consuming the Config

The following scripts read the JSON by default. Each provides a `--config` flag if you want to point at an alternate path.

- `scripts/fxcm_importer.py`
- `scripts/m1_timeframe_converter.py` (database mode)
- `scripts/verify_data_consistency.py`
- `scripts/clickhouse_configurator.py` (for reuse/testing)
- `scripts/create_clickhouse_tables.py`
- `scripts/view_clickhouse_tables.py`

## Environment Variables

Set these when you do not want to store secrets on disk:

```powershell
$env:CLICKHOUSE_HOST = '127.0.0.1'
$env:CLICKHOUSE_PORT = '9000'
$env:CLICKHOUSE_USER = 'default'
$env:CLICKHOUSE_PASSWORD = 'super-secret'
```

The configurator prefers CLI flags, then environment variables, then existing JSON values.
