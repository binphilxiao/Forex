# M1 Timeframe Converter - Design Specification

**Version:** 2.0.0  
**Author:** binphilxiao  
**Date:** 2025-10-05  
**Status:** Approved

---

## 1. System Architecture

### 1.1 Overview

The M1 Timeframe Converter is designed as a standalone Python application that reads M1 forex data from ClickHouse, aggregates it to higher timeframes, and writes the results back to ClickHouse.

```
┌─────────────────────────────────────────────────────────────┐
│                  M1 Timeframe Converter                     │
│                       (Python 3.7+)                         │
└─────────────────────────────────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
    ┌──────────┐      ┌───────────┐     ┌──────────┐
    │   CLI    │      │   Core    │     │  Report  │
    │ Interface│      │ Converter │     │ Generator│
    └──────────┘      └───────────┘     └──────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                             ▼
                  ┌──────────────────┐
                  │   ClickHouse     │
                  │     Client       │
                  └──────────────────┘
                             │
                             ▼
                  ┌──────────────────┐
                  │   ClickHouse     │
                  │    Database      │
                  │ 192.168.2.168    │
                  └──────────────────┘
```

### 1.2 Components

1. **CLI Interface**: Handles command-line arguments and user interaction
2. **Core Converter**: Performs M1 to multi-timeframe aggregation
3. **ClickHouse Client**: Manages database connections and operations
4. **Report Generator**: Creates logs and summary reports
5. **Statistics Tracker**: Monitors and reports processing metrics

---

## 2. Class Design

### 2.1 M1TimeframeConverter Class

**Responsibility:** Main converter class that orchestrates the entire conversion process.

```python
class M1TimeframeConverter:
    """
    M1 to Multi-Timeframe Converter
    
    Attributes:
        AVAILABLE_PAIRS: List of supported currency pairs
        AVAILABLE_TIMEFRAMES: List of supported timeframes
        TIMEFRAME_MINUTES: Mapping of timeframes to minutes
        AGGREGATION_RULES: OHLC aggregation rules
    """
    
    # Class constants
    AVAILABLE_PAIRS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF']
    AVAILABLE_TIMEFRAMES = ['M5', 'M15', 'M30', 'H1']
    TIMEFRAME_MINUTES = {'M5': 5, 'M15': 15, 'M30': 30, 'H1': 60}
    AGGREGATION_RULES = {
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last'
    }
    
    def __init__(self, ch_host, ch_port, ch_user, ch_password, overwrite)
    def connect_clickhouse(self) -> bool
    def disconnect_clickhouse(self)
    def get_table_name(self, pair, timeframe) -> str
    def table_exists(self, table_name) -> bool
    def get_existing_data_range(self, table_name, year) -> Optional[Dict]
    def read_m1_data(self, pair, year) -> Optional[pd.DataFrame]
    def aggregate_to_timeframe(self, df, timeframe) -> pd.DataFrame
    def write_to_clickhouse(self, df, pair, timeframe) -> bool
    def convert_pair_year_timeframe(self, pair, year, timeframe) -> bool
    def convert(self, pairs, timeframes, start_year, end_year) -> bool
```

### 2.2 Key Methods

#### 2.2.1 `__init__`
**Purpose:** Initialize converter with configuration parameters.

**Parameters:**
- `ch_host`: ClickHouse hostname/IP
- `ch_port`: ClickHouse HTTP port
- `ch_user`: ClickHouse username
- `ch_password`: ClickHouse password
- `overwrite`: Whether to overwrite existing data

**Actions:**
- Store configuration
- Initialize statistics
- Setup logging
- Create log directory

#### 2.2.2 `connect_clickhouse`
**Purpose:** Establish connection to ClickHouse database.

**Returns:** Boolean (success/failure)

**Actions:**
- Create ClickHouse client using clickhouse_connect
- Test connection
- Log connection status

#### 2.2.3 `read_m1_data`
**Purpose:** Read M1 data from ClickHouse for a specific pair and year.

**Parameters:**
- `pair`: Currency pair (e.g., 'EURUSD')
- `year`: Year to read (e.g., 2024)

**Returns:** pandas DataFrame or None

**SQL Query:**
```sql
SELECT DateTime, Open, High, Low, Close
FROM forex_{pair}_m1
WHERE toYear(DateTime) = {year}
ORDER BY DateTime
```

#### 2.2.4 `aggregate_to_timeframe`
**Purpose:** Aggregate M1 data to specified timeframe using pandas resampling.

**Parameters:**
- `df`: pandas DataFrame with M1 data
- `timeframe`: Target timeframe ('M5', 'M15', 'M30', 'H1')

**Returns:** pandas DataFrame with aggregated data

**Algorithm:**
1. Set DateTime as index
2. Resample using timeframe interval
3. Apply OHLC aggregation rules
4. Remove periods with no data (NaN)
5. Reset index

**Example:**
```python
# M5 aggregation (5 minutes)
df.set_index('DateTime').resample('5T').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last'
})
```

#### 2.2.5 `write_to_clickhouse`
**Purpose:** Write aggregated data to ClickHouse table.

**Parameters:**
- `df`: pandas DataFrame with aggregated data
- `pair`: Currency pair
- `timeframe`: Timeframe

**Returns:** Boolean (success/failure)

**Actions:**
1. Generate table name
2. Create table if not exists (MergeTree engine)
3. Insert DataFrame using batch insert
4. Update statistics

#### 2.2.6 `convert_pair_year_timeframe`
**Purpose:** Convert M1 data for one pair, year, and timeframe.

**Parameters:**
- `pair`: Currency pair
- `year`: Year to convert
- `timeframe`: Target timeframe

**Returns:** Boolean (success/failure)

**Algorithm:**
1. Check if data exists (if skip mode)
2. Read M1 data from ClickHouse
3. Aggregate to target timeframe
4. Write to ClickHouse
5. Update statistics

#### 2.2.7 `convert`
**Purpose:** Main conversion orchestrator.

**Parameters:**
- `pairs`: List of currency pairs
- `timeframes`: List of timeframes
- `start_year`: Start year
- `end_year`: End year

**Returns:** Boolean (overall success)

**Algorithm:**
```
FOR each pair IN pairs:
    FOR each year IN [start_year...end_year]:
        FOR each timeframe IN timeframes:
            convert_pair_year_timeframe(pair, year, timeframe)
            
Generate summary report
Save statistics
```

---

## 3. Database Schema

### 3.1 ClickHouse Tables

#### 3.1.1 Source Tables (M1 Data)
**Pattern:** `forex_{pair}_m1`  
**Examples:** `forex_eurusd_m1`, `forex_gbpusd_m1`

**Schema:**
```sql
CREATE TABLE forex_eurusd_m1
(
    DateTime DateTime,
    Open Float64,
    High Float64,
    Low Float64,
    Close Float64
)
ENGINE = MergeTree()
ORDER BY DateTime
```

#### 3.1.2 Target Tables (Aggregated Data)
**Pattern:** `forex_{pair}_{timeframe}`  
**Examples:** `forex_eurusd_m5`, `forex_gbpusd_h1`

**Schema:**
```sql
CREATE TABLE forex_eurusd_m5
(
    DateTime DateTime,
    Open Float64,
    High Float64,
    Low Float64,
    Close Float64
)
ENGINE = MergeTree()
ORDER BY DateTime
```

### 3.2 Table Naming Convention

| Pair | Timeframe | Table Name |
|------|-----------|------------|
| EURUSD | M5 | `forex_eurusd_m5` |
| EURUSD | M15 | `forex_eurusd_m15` |
| EURUSD | M30 | `forex_eurusd_m30` |
| EURUSD | H1 | `forex_eurusd_h1` |
| GBPUSD | M5 | `forex_gbpusd_m5` |
| ... | ... | ... |

**Total Tables:** 6 pairs × 4 timeframes = 24 target tables

---

## 4. Data Flow

### 4.1 High-Level Flow

```
Start
  │
  ├─ Parse CLI arguments
  │
  ├─ Initialize converter
  │
  ├─ Connect to ClickHouse
  │
  ├─ FOR each currency pair:
  │   │
  │   ├─ FOR each year:
  │   │   │
  │   │   ├─ FOR each timeframe:
  │   │   │   │
  │   │   │   ├─ Check existing data (skip mode)
  │   │   │   │
  │   │   │   ├─ Read M1 data from ClickHouse
  │   │   │   │     │
  │   │   │   │     └─ SQL: SELECT * FROM forex_{pair}_m1 WHERE year={year}
  │   │   │   │
  │   │   │   ├─ Aggregate to timeframe (pandas resample)
  │   │   │   │     │
  │   │   │   │     ├─ Open: first
  │   │   │   │     ├─ High: max
  │   │   │   │     ├─ Low: min
  │   │   │   │     └─ Close: last
  │   │   │   │
  │   │   │   ├─ Write to ClickHouse
  │   │   │   │     │
  │   │   │   │     └─ INSERT INTO forex_{pair}_{timeframe}
  │   │   │   │
  │   │   │   └─ Update statistics
  │   │   │
  │   │   └─ Next timeframe
  │   │
  │   └─ Next year
  │
  └─ Next pair
  │
  ├─ Generate summary report
  │
  ├─ Disconnect ClickHouse
  │
End
```

### 4.2 Data Transformation Example

**Input (M1 Data):**
```
DateTime             Open    High    Low     Close
2024-01-01 00:00:00  1.1000  1.1005  1.0995  1.1001
2024-01-01 00:01:00  1.1001  1.1006  1.0996  1.1002
2024-01-01 00:02:00  1.1002  1.1007  1.0997  1.1003
2024-01-01 00:03:00  1.1003  1.1008  1.0998  1.1004
2024-01-01 00:04:00  1.1004  1.1009  1.0999  1.1005
```

**Output (M5 Data):**
```
DateTime             Open    High    Low     Close
2024-01-01 00:00:00  1.1000  1.1009  1.0995  1.1005
                     ↑       ↑       ↑       ↑
                   first    max     min    last
```

---

## 5. Aggregation Logic

### 5.1 OHLC Aggregation Rules

For each timeframe period (e.g., 5 minutes):

1. **Open**: Take the **first** Open value in the period
2. **High**: Take the **maximum** High value in the period
3. **Low**: Take the **minimum** Low value in the period
4. **Close**: Take the **last** Close value in the period

### 5.2 Timeframe Intervals

| Timeframe | Minutes | M1 Bars per Period |
|-----------|---------|-------------------|
| M5 | 5 | 5 |
| M15 | 15 | 15 |
| M30 | 30 | 30 |
| H1 | 60 | 60 |

### 5.3 Pandas Resample Implementation

```python
# Set DateTime as index
df = df.set_index('DateTime')

# Resample to target timeframe
if timeframe == 'M5':
    aggregated = df.resample('5T').agg(AGGREGATION_RULES)
elif timeframe == 'M15':
    aggregated = df.resample('15T').agg(AGGREGATION_RULES)
elif timeframe == 'M30':
    aggregated = df.resample('30T').agg(AGGREGATION_RULES)
elif timeframe == 'H1':
    aggregated = df.resample('60T').agg(AGGREGATION_RULES)

# Remove NaN (periods with no data)
aggregated = aggregated.dropna()

# Reset index
aggregated = aggregated.reset_index()
```

### 5.4 Edge Cases

#### 5.4.1 Partial Periods
If M1 data doesn't align perfectly with timeframe boundaries:
- **Behavior:** Create partial period with available data
- **Example:** 45 M1 bars → 1 incomplete H1 bar (instead of 0 bars)

#### 5.4.2 Missing Data
If some M1 minutes are missing:
- **Behavior:** Aggregate available data within period
- **Example:** M5 period with only 3 M1 bars → Valid M5 bar

#### 5.4.3 Empty Periods
If entire period has no data:
- **Behavior:** No bar created (dropna removes it)
- **Example:** Weekend gap → No bars

---

## 6. Error Handling

### 6.1 Connection Errors

**Scenario:** ClickHouse server unavailable

**Handling:**
```python
try:
    client = clickhouse_connect.get_client(...)
except Exception as e:
    logger.error(f"Failed to connect to ClickHouse: {e}")
    return False
```

### 6.2 Data Read Errors

**Scenario:** M1 table doesn't exist or no data for year

**Handling:**
```python
try:
    result = client.query_df(sql)
    if len(result) == 0:
        logger.warning(f"No M1 data for {pair} {year}")
        return None
except Exception as e:
    logger.error(f"Error reading M1 data: {e}")
    return None
```

### 6.3 Aggregation Errors

**Scenario:** Invalid data format or pandas error

**Handling:**
```python
try:
    aggregated = df.resample(...).agg(...)
except Exception as e:
    logger.error(f"Aggregation error: {e}")
    return pd.DataFrame()
```

### 6.4 Write Errors

**Scenario:** Database write failure

**Handling:**
```python
try:
    client.insert_df(table_name, df)
except Exception as e:
    logger.error(f"Error writing to ClickHouse: {e}")
    stats['errors'] += 1
    return False
```

---

## 7. Logging System

### 7.1 Log File Structure

**Location:** `logs/m1_converter_YYYYMMDD_HHMMSS.log`

**Format:**
```
YYYY-MM-DD HH:MM:SS - LEVEL - Message
```

**Example:**
```
2025-10-05 14:30:15 - INFO - Log file: logs/m1_converter_20251005_143015.log
2025-10-05 14:30:15 - INFO - ✅ Connected to ClickHouse at 192.168.2.168:8123
2025-10-05 14:30:16 - INFO - Processing: EURUSD
2025-10-05 14:30:17 - INFO -   📥 Read 525,600 M1 records for EURUSD 2024
2025-10-05 14:30:18 - INFO -   ✅ Wrote 105,120 records to forex_eurusd_m5
```

### 7.2 Log Levels

- **INFO**: Normal operations, progress updates
- **WARNING**: Non-critical issues (missing data, skipped items)
- **ERROR**: Critical failures, exceptions

### 7.3 Dual Logging

Logs output to:
1. **File**: Permanent record in `logs/` directory
2. **Console**: Real-time feedback to user

---

## 8. Statistics Tracking

### 8.1 Statistics Dictionary

```python
stats = {
    'total_pairs_processed': 0,      # Number of pairs completed
    'total_timeframes_generated': 0, # Number of timeframes created
    'total_records_read': 0,         # Total M1 records read
    'total_records_written': 0,      # Total aggregated records written
    'skipped_existing': 0,           # Items skipped (skip mode)
    'errors': 0,                     # Number of errors encountered
    'processing_time': 0             # Total time in seconds
}
```

### 8.2 Statistics Update Points

- **Pairs processed:** +1 after completing all years/timeframes for a pair
- **Timeframes generated:** +1 after successfully writing timeframe data
- **Records read:** +N after reading M1 data
- **Records written:** +N after writing aggregated data
- **Skipped:** +1 when skipping existing data
- **Errors:** +1 on any exception

### 8.3 Report Generation

**File:** `logs/m1_converter_report_YYYYMMDD_HHMMSS.txt`

**Content:**
```
============================================================
M1 to Multi-Timeframe Conversion Report
============================================================

Start Time: 2025-10-05 14:30:15
End Time: 2025-10-05 15:45:30
Duration: 4515.2 seconds

Statistics:
  Pairs Processed: 6
  Timeframes Generated: 24
  Records Read (M1): 23,357,603
  Records Written: 4,671,521
  Skipped (existing): 0
  Errors: 0

============================================================
```

---

## 9. Performance Optimization

### 9.1 Batch Processing

**Strategy:** Process data year by year, not all at once

**Benefits:**
- Lower memory usage
- Better progress tracking
- Easier error recovery

### 9.2 Pandas Optimization

**Techniques:**
- Use `resample()` for efficient aggregation
- Vectorized operations (avoid loops)
- `dropna()` to remove empty periods
- Efficient data types (Float64)

### 9.3 ClickHouse Optimization

**Techniques:**
- Batch inserts (insert entire DataFrame at once)
- MergeTree engine for fast queries
- DateTime ordering for time-series queries
- Connection pooling (single connection per run)

### 9.4 Expected Performance

**Benchmark (estimated):**
- **M1 Read:** 1-2 million records/minute
- **Aggregation:** 2-5 million records/minute
- **ClickHouse Write:** 500k-1M records/minute

**Overall:** ~1-2 million M1 records processed/minute

---

## 10. Security Considerations

### 10.1 Credential Handling

- **Never hardcode** passwords in source code
- Accept credentials via command-line parameters
- Support environment variables (future enhancement)
- Don't log passwords

### 10.2 SQL Injection Prevention

- Use parameterized queries where possible
- Validate currency pair names
- Validate timeframe names
- Use clickhouse-connect's safe methods

### 10.3 Connection Security

- Support SSL/TLS connections (ClickHouse feature)
- Use secure ports when available
- Limit database permissions (read M1, write timeframes)

---

## 11. Testing Strategy

### 11.1 Unit Tests

**Test Cases:**
1. Converter initialization
2. Available pairs/timeframes
3. Table name generation
4. M5 aggregation logic
5. M15 aggregation logic
6. M30 aggregation logic
7. H1 aggregation logic
8. Empty dataframe handling
9. Partial period aggregation
10. Multi-day aggregation
11. Statistics initialization
12. Logging setup
13. OHLC aggregation rules
14. Timeframe minutes mapping
15. Edge cases

### 11.2 Integration Tests (Manual)

**Test Scenarios:**
1. Convert single pair, single timeframe
2. Convert all pairs, all timeframes
3. Skip existing data mode
4. Overwrite existing data mode
5. Custom date range
6. Invalid parameters (error handling)
7. ClickHouse connection failure
8. Missing M1 data

### 11.3 Test Data

**Mock Data:**
- Create small pandas DataFrames
- Known OHLC values for verification
- Edge cases (empty, partial periods)

**Real Data:**
- Use existing ClickHouse M1 data
- Verify against expected results

---

## 12. Deployment

### 12.1 Installation

```bash
# Clone repository
git clone <repository>

# Install dependencies
pip install pandas clickhouse-connect

# Verify installation
python scripts/m1_timeframe_converter.py --help
```

### 12.2 Configuration

**Required:**
- Python 3.7+
- ClickHouse server accessible
- M1 data loaded in ClickHouse

**Optional:**
- Custom ClickHouse host/port
- Custom credentials

### 12.3 Usage

**Basic:**
```bash
python scripts/m1_timeframe_converter.py
```

**Advanced:**
```bash
python scripts/m1_timeframe_converter.py \
    --pairs EURUSD GBPUSD \
    --timeframes M5 H1 \
    --start-year 2020 \
    --end-year 2024 \
    --skip-existing \
    --ch-host 192.168.1.100 \
    --ch-port 8123
```

**Windows Batch:**
```cmd
convert_m1_to_multi_timeframes.bat
```

---

## 13. Monitoring and Maintenance

### 13.1 Log Monitoring

- Check logs for errors and warnings
- Monitor processing time trends
- Verify record counts

### 13.2 Data Quality Checks

- Verify OHLC relationships (High >= Open/Close, Low <= Open/Close)
- Check for gaps in timeframe data
- Compare record counts (M1 vs aggregated)

### 13.3 Performance Monitoring

- Track processing time per pair/year
- Monitor ClickHouse query performance
- Check memory usage

---

## 14. Future Enhancements

### 14.1 Planned Features (Phase 2)

1. **Parallel Processing**: Process multiple pairs concurrently
2. **Resume Capability**: Continue from last checkpoint after interruption
3. **Data Validation**: Verify OHLC relationships and detect anomalies
4. **Progress Bar**: Visual progress indicator (tqdm)
5. **Email Notifications**: Send reports via email
6. **Web Dashboard**: Real-time monitoring via web interface
7. **Additional Timeframes**: Support D1 (daily), W1 (weekly)
8. **Alternative Sources**: Read from CSV, PostgreSQL, etc.

### 14.2 Code Improvements

1. Type hints throughout codebase
2. Async/await for I/O operations
3. Configuration file support (YAML/JSON)
4. Plugin architecture for extensibility

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-10-05 | binphilxiao | Initial design specification |
| 2.0.0 | 2025-10-05 | binphilxiao | Complete rewrite with ClickHouse integration |

---

**Review Status:**  
☑ Design Reviewed  
☑ Ready for Implementation
