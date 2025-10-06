# ClickHouse Schema Reference

Detailed reference for the tables created by `scripts/create_clickhouse_tables.py`. All objects live in the `forex_data` database and use the MergeTree family for efficient time-series analytics.

## Database: `forex_data`

- **Engine**: `Atomic`
- **Purpose**: Central store for FXCM OHLCV candles across multiple timeframes.
- **Creation**: `CREATE DATABASE IF NOT EXISTS forex_data ENGINE = Atomic`

## Base Fact Tables

### `forex_data.ohlcv_m1`

| Column     | Type     | Default     | Notes |
|------------|----------|-------------|-------|
| `symbol`   | `String` | —           | Currency pair (e.g. `EURUSD`). |
| `timestamp`| `DateTime` | —         | Candle open timestamp in UTC, 1-minute granularity. |
| `open`     | `Float64`| —           | Opening price. |
| `high`     | `Float64`| —           | Highest price inside the minute. |
| `low`      | `Float64`| —           | Lowest price inside the minute. |
| `close`    | `Float64`| —           | Closing price. |
| `volume`   | `UInt64` | `0`         | Volume delivered by FXCM; defaults to 0 when unavailable. |
| `created_at`| `DateTime` | `now()`  | Load timestamp assigned by ClickHouse. |

- **Engine**: `MergeTree()`
- **Partitioning**: `toYYYYMM(timestamp)`
- **Primary key / ORDER BY**: `(symbol, timestamp)`
- **Usage**: Authoritative source for all aggregations and downstream validations.

### `forex_data.ohlcv_d1`

| Column   | Type     | Default | Notes |
|----------|----------|---------|-------|
| `symbol` | `String` | —       | Currency pair. |
| `date`   | `Date`   | —       | Candle date in UTC (daily granularity). |
| `open`   | `Float64`| —       | Opening price. |
| `high`   | `Float64`| —       | Daily high. |
| `low`    | `Float64`| —       | Daily low. |
| `close`  | `Float64`| —       | Closing price. |
| `volume` | `UInt64` | `0`     | FXCM volume (daily sum). |
| `created_at`| `DateTime` | `now()` | Load timestamp. |

- **Engine**: `MergeTree()`
- **Partitioning**: `toYear(date)`
- **Primary key / ORDER BY**: `(symbol, date)`
- **Usage**: Direct ingestion of FXCM daily candles without further aggregation.

## Aggregated Interval Tables

The converter script builds higher timeframes by aggregating `ohlcv_m1`. For each interval the script creates a target table and a materialized view (MV) that feeds it.

### M5 aggregation

- **Table**: `forex_data.ohlcv_m5`
  - Columns: `symbol`, `timestamp`, `open`, `high`, `low`, `close`, `volume`
  - Engine/partition/order: identical to `ohlcv_m1` (partition by month, order by `(symbol, timestamp)`).
- **Materialized view**: `forex_data.ohlcv_m5_mv`
  - Definition: groups by `symbol` and `toStartOfInterval(timestamp, INTERVAL 5 MINUTE)`.
  - Aggregations: `argMin(open, timestamp)`, `max(high)`, `min(low)`, `argMax(close, timestamp)`, `sum(volume)`.
  - Source: `forex_data.ohlcv_m1` (automatically ingests new M1 rows).

### M15 aggregation

- **Table**: `forex_data.ohlcv_m15`
- **Materialized view**: `forex_data.ohlcv_m15_mv`
  - Uses `INTERVAL 15 MINUTE` in `toStartOfInterval` with the same aggregation pattern as M5.

### M30 aggregation

- **Table**: `forex_data.ohlcv_m30`
- **Materialized view**: `forex_data.ohlcv_m30_mv`
  - Uses `INTERVAL 30 MINUTE` with the standard OHLC aggregation set.

### H1 aggregation

- **Table**: `forex_data.ohlcv_h1`
- **Materialized view**: `forex_data.ohlcv_h1_mv`
  - Interval function: `toStartOfHour(timestamp)`.

> All aggregated tables share the same schema (`symbol`, `timestamp`, `open`, `high`, `low`, `close`, `volume`) and MergeTree configuration as the M1 table.

## Refresh Mechanics

- Materialized views are **insert-only**: whenever new rows land in `ohlcv_m1`, ClickHouse computes the aggregated rows and writes them to the target tables.
- Updating or deleting rows in `ohlcv_m1` does **not** automatically back-propagate to higher timeframes; run a full reload if backfilling historical gaps.

## Recreation Workflow

Run the helper script to recreate or verify the schema:

```powershell
python scripts\create_clickhouse_tables.py
```

The script ensures the following order:
1. Create the `forex_data` database.
2. Create `ohlcv_m1` and `ohlcv_d1` base tables.
3. Create aggregated tables (`ohlcv_m5`, `ohlcv_m15`, `ohlcv_m30`, `ohlcv_h1`) and their materialized views.

## Helpful Queries

```sql
-- Inspect monthly partitions for EURUSD minute candles
SELECT partition, sum(rows) AS rows
FROM system.parts
WHERE database = 'forex_data' AND table = 'ohlcv_m1' AND active
  AND partition BETWEEN '202401' AND '202412'
GROUP BY partition
ORDER BY partition;

-- Sample data from 15-minute aggregation
SELECT *
FROM forex_data.ohlcv_m15
WHERE symbol = 'EURUSD'
ORDER BY timestamp DESC
LIMIT 10;
```

## Related Scripts

- `scripts/create_clickhouse_tables.py` — creates all objects.
- `scripts/fxcm_importer.py` — loads raw CSV data into `ohlcv_m1` and optionally `ohlcv_d1`.
- `scripts/m1_timeframe_converter.py` — can re-aggregate data if you prefer CLI-driven batch conversion.
- `scripts/verify_data_consistency.py` — validates row counts between CSV archives and ClickHouse tables.
