# FXCM Data Importer - Design Specification

**Version:** 2.0.0  
**Author:** binphilxiao  
**Date:** 2025-10-05  
**Status:** Active

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FXCM Data Importer                        │
│                                                               │
│  ┌────────────┐    ┌─────────────┐    ┌──────────────┐     │
│  │    CLI     │───▶│   Importer  │───▶│  ClickHouse  │     │
│  │  Interface │    │    Core     │    │   Database   │     │
│  └────────────┘    └─────────────┘    └──────────────┘     │
│                           │                                   │
│                           ▼                                   │
│                    ┌─────────────┐                           │
│                    │   Logger &  │                           │
│                    │   Reporter  │                           │
│                    └─────────────┘                           │
└─────────────────────────────────────────────────────────────┘

Input: CSV files in fxcm_data/
Output: ClickHouse tables + Log files
```

### 1.2 Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                  FXCMDataImporter Class                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  + __init__(config)                                          │
│  + import_data(pairs, timeframes, years, check_mode)        │
│  + _process_pair(pair, timeframe, year)                     │
│  + _process_file(file_path, pair, timeframe, check_mode)    │
│  + _validate_fast(file_data, pair, timeframe)               │
│  + _validate_comprehensive(file_data, pair, timeframe)      │
│  + _insert_batch(data, timeframe)                           │
│  + _generate_report()                                        │
│                                                               │
│  - ch_client: ClickHouseClient                              │
│  - logger: Logger                                            │
│  - stats: Dict[str, int]                                    │
└──────────────────────────────────────────────────────────────┘
         │
         ├──────────────────────────────────────┐
         │                                       │
         ▼                                       ▼
┌────────────────────┐                 ┌────────────────────┐
│ ClickHouseClient   │                 │    FileValidator   │
├────────────────────┤                 ├────────────────────┤
│                    │                 │                    │
│ + connect()        │                 │ + validate_fast()  │
│ + execute_query()  │                 │ + validate_comp()  │
│ + batch_insert()   │                 │ + compare_ohlc()   │
│ + check_exists()   │                 └────────────────────┘
│ + disconnect()     │
└────────────────────┘
```

---

## 2. Class Design

### 2.1 FXCMDataImporter

**Purpose:** Main class orchestrating the import process

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `config` | dict | Configuration parameters |
| `ch_client` | ClickHouseClient | ClickHouse connection handler |
| `logger` | Logger | Logging instance |
| `stats` | dict | Import statistics |
| `data_dir` | Path | Base directory for CSV files |
| `log_dir` | Path | Directory for log files |

#### Methods

##### `__init__(config: dict)`
**Purpose:** Initialize importer with configuration

**Parameters:**
- `config` (dict): Configuration dictionary with keys:
  - `ch_host` (str): ClickHouse host
  - `ch_http_port` (int): HTTP port
  - `ch_user` (str): Username
  - `ch_password` (str): Password
  - `data_dir` (str): Data directory path
  - `log_dir` (str): Log directory path

**Returns:** None

**Example:**
```python
config = {
    'ch_host': '192.168.2.168',
    'ch_http_port': 8123,
    'ch_user': 'default',
    'ch_password': '',
    'data_dir': 'fxcm_data',
    'log_dir': 'logs'
}
importer = FXCMDataImporter(config)
```

---

##### `import_data(pairs, timeframes, start_year, end_year, check_mode)`
**Purpose:** Main entry point for import process

**Parameters:**
- `pairs` (list): List of currency pairs (e.g., ['EURUSD', 'GBPUSD'])
- `timeframes` (list): List of timeframes (e.g., ['M1', 'D1'])
- `start_year` (int): Start year (e.g., 2015)
- `end_year` (int): End year (e.g., 2024)
- `check_mode` (str): 'fast' or 'comprehensive'

**Returns:** bool - True if successful, False otherwise

**Algorithm:**
```
1. Print header with configuration
2. For each pair in pairs:
   3. For each timeframe in timeframes:
      4. For each year in range(start_year, end_year+1):
         5. Get list of CSV files for (pair, timeframe, year)
         6. For each file:
            7. Process file with check_mode
            8. Update statistics
9. Generate report
10. Return success status
```

**Example:**
```python
success = importer.import_data(
    pairs=['EURUSD', 'GBPUSD'],
    timeframes=['M1', 'D1'],
    start_year=2020,
    end_year=2024,
    check_mode='fast'
)
```

---

##### `_process_file(file_path, pair, timeframe, check_mode)`
**Purpose:** Process a single CSV file

**Parameters:**
- `file_path` (Path): Path to CSV file
- `pair` (str): Currency pair
- `timeframe` (str): Timeframe (M1/D1)
- `check_mode` (str): Validation mode

**Returns:** tuple - (records_imported, records_skipped)

**Algorithm:**
```
1. Read CSV file into DataFrame
2. Add 'symbol' column with pair value
3. Rename columns to match DB schema
4. Convert datetime formats
5. If check_mode == 'fast':
   6. Call _validate_fast(df, pair, timeframe)
   7. If validation passes (file exists in DB):
      8. Return (0, len(df))  # Skip entire file
   9. Else:
      10. Call _insert_batch(df, timeframe)
      11. Return (len(df), 0)  # Import entire file
12. Elif check_mode == 'comprehensive':
   13. Call _validate_comprehensive(df, pair, timeframe)
   14. Get list of new/modified records
   15. Call _insert_batch(new_records, timeframe)
   16. Return (len(new_records), len(df) - len(new_records))
```

---

##### `_validate_fast(df, pair, timeframe)`
**Purpose:** Fast validation - check first and last records only

**Parameters:**
- `df` (DataFrame): CSV data
- `pair` (str): Currency pair
- `timeframe` (str): Timeframe

**Returns:** bool - True if file exists (skip), False if needs import

**Algorithm:**
```
1. Get first row: first_time, first_ohlc
2. Get last row: last_time, last_ohlc
3. Query DB:
   SELECT timestamp, open, high, low, close
   FROM ohlcv_{timeframe.lower()}
   WHERE symbol = '{pair}'
     AND timestamp IN ('{first_time}', '{last_time}')
4. Parse results
5. If 2 records found:
   6. Compare first_ohlc with DB first record (tolerance 1e-5)
   7. Compare last_ohlc with DB last record (tolerance 1e-5)
   8. If both match: Return True (skip file)
9. Return False (import file)
```

**Performance:** O(1) - Constant time, only 2 DB queries

---

##### `_validate_comprehensive(df, pair, timeframe)`
**Purpose:** Comprehensive validation - check all records

**Parameters:**
- `df` (DataFrame): CSV data
- `pair` (str): Currency pair
- `timeframe` (str): Timeframe

**Returns:** DataFrame - New/modified records to import

**Algorithm:**
```
1. Get time range from df: min_time, max_time
2. Query DB for existing data in range:
   SELECT timestamp, open, high, low, close
   FROM ohlcv_{timeframe.lower()}
   WHERE symbol = '{pair}'
     AND timestamp >= '{min_time}'
     AND timestamp <= '{max_time}'
3. Build hash map: existing_data = {timestamp: (o,h,l,c)}
4. Filter df:
   new_records = []
   For each row in df:
      timestamp = row['timestamp']
      If timestamp not in existing_data:
         new_records.append(row)  # New record
      Else:
         db_ohlc = existing_data[timestamp]
         csv_ohlc = (row.open, row.high, row.low, row.close)
         If not _compare_ohlc(csv_ohlc, db_ohlc):
            new_records.append(row)  # Modified record
5. Return DataFrame(new_records)
```

**Performance:** O(N) - Linear time, where N = number of records in file

---

##### `_compare_ohlc(csv_ohlc, db_ohlc, tolerance=1e-5)`
**Purpose:** Compare OHLC values with tolerance

**Parameters:**
- `csv_ohlc` (tuple): (open, high, low, close) from CSV
- `db_ohlc` (tuple): (open, high, low, close) from DB
- `tolerance` (float): Acceptable difference

**Returns:** bool - True if values match within tolerance

**Algorithm:**
```
1. For i in range(4):
   2. If abs(csv_ohlc[i] - db_ohlc[i]) > tolerance:
      3. Return False
4. Return True
```

---

##### `_insert_batch(df, timeframe, batch_size=1000)`
**Purpose:** Insert data in batches

**Parameters:**
- `df` (DataFrame): Data to insert
- `timeframe` (str): Timeframe (M1/D1)
- `batch_size` (int): Records per batch

**Returns:** int - Number of records inserted

**Algorithm:**
```
1. table = 'ohlcv_' + timeframe.lower()
2. total_inserted = 0
3. For batch in df.groupby(range(0, len(df), batch_size)):
   4. Convert batch to CSV format string
   5. Execute INSERT query:
      INSERT INTO forex_data.{table}
      (symbol, timestamp, open, high, low, close, volume)
      FORMAT CSV
      {csv_data}
   6. If success:
      7. total_inserted += len(batch)
   8. Else:
      9. Log error
      10. Continue with next batch
11. Return total_inserted
```

---

### 2.2 ClickHouseClient

**Purpose:** Handle ClickHouse database operations

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `host` | str | ClickHouse host |
| `http_port` | int | HTTP port |
| `user` | str | Username |
| `password` | str | Password |
| `client` | Client | clickhouse-connect client |

#### Methods

##### `connect()`
**Purpose:** Establish connection to ClickHouse

**Returns:** bool - True if connected

**Example:**
```python
client = ClickHouseClient(host='192.168.2.168', http_port=8123)
if client.connect():
    print("Connected!")
```

---

##### `execute_query(query, data=None)`
**Purpose:** Execute SQL query

**Parameters:**
- `query` (str): SQL query
- `data` (str, optional): Data for INSERT queries

**Returns:** tuple - (success: bool, result: str)

**Example:**
```python
success, result = client.execute_query(
    "SELECT count() FROM forex_data.ohlcv_m1"
)
```

---

##### `batch_insert(table, df, batch_size=1000)`
**Purpose:** Insert DataFrame in batches

**Parameters:**
- `table` (str): Table name
- `df` (DataFrame): Data to insert
- `batch_size` (int): Batch size

**Returns:** int - Records inserted

---

##### `check_record_exists(table, symbol, timestamp, ohlc)`
**Purpose:** Check if specific record exists

**Parameters:**
- `table` (str): Table name
- `symbol` (str): Currency pair
- `timestamp` (str): Timestamp
- `ohlc` (tuple): (open, high, low, close)

**Returns:** bool - True if exists with matching values

---

## 3. Data Structures

### 3.1 Configuration Dictionary

```python
config = {
    # ClickHouse connection
    'ch_host': str,           # e.g., '192.168.2.168'
    'ch_http_port': int,      # e.g., 8123
    'ch_native_port': int,    # e.g., 9000
    'ch_user': str,           # e.g., 'default'
    'ch_password': str,       # e.g., ''
    
    # Import settings
    'pairs': list,            # e.g., ['EURUSD', 'GBPUSD']
    'timeframes': list,       # e.g., ['M1', 'D1']
    'start_year': int,        # e.g., 2015
    'end_year': int,          # e.g., 2024
    'check_mode': str,        # 'fast' or 'comprehensive'
    
    # Paths
    'data_dir': str,          # e.g., 'fxcm_data'
    'log_dir': str,           # e.g., 'logs'
    
    # Performance
    'batch_size': int,        # e.g., 1000
    'tolerance': float,       # e.g., 1e-5
}
```

### 3.2 Statistics Dictionary

```python
stats = {
    'total_files': int,           # Total files found
    'processed_files': int,       # Files processed
    'skipped_files': int,         # Files skipped (duplicates)
    'total_records_read': int,    # Records read from CSV
    'records_imported': int,      # Records inserted to DB
    'records_skipped': int,       # Records skipped (duplicates)
    'errors': int,                # Number of errors
    'start_time': datetime,       # Start timestamp
    'end_time': datetime,         # End timestamp
    'processing_time': float,     # Total seconds
}
```

### 3.3 File Metadata Structure

```python
file_metadata = {
    'path': Path,              # Full file path
    'pair': str,               # Currency pair
    'timeframe': str,          # M1 or D1
    'year': int,               # Year
    'week': int,               # Week number (M1 only)
    'size': int,               # File size in bytes
    'record_count': int,       # Number of records
    'first_timestamp': str,    # First record time
    'last_timestamp': str,     # Last record time
}
```

---

## 4. Database Schema

### 4.1 M1 Table

```sql
CREATE TABLE IF NOT EXISTS forex_data.ohlcv_m1 (
    symbol String,
    timestamp DateTime,
    open Float64,
    high Float64,
    low Float64,
    close Float64,
    volume UInt64 DEFAULT 0,
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (symbol, timestamp)
PRIMARY KEY (symbol, timestamp)
SETTINGS index_granularity = 8192;
```

**Indexes:**
- Primary: (symbol, timestamp) - O(log N) lookups
- Partition: toYYYYMM(timestamp) - Fast range queries

### 4.2 D1 Table

```sql
CREATE TABLE IF NOT EXISTS forex_data.ohlcv_d1 (
    symbol String,
    date Date,
    open Float64,
    high Float64,
    low Float64,
    close Float64,
    volume UInt64 DEFAULT 0,
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYear(date)
ORDER BY (symbol, date)
PRIMARY KEY (symbol, date)
SETTINGS index_granularity = 8192;
```

**Indexes:**
- Primary: (symbol, date) - O(log N) lookups
- Partition: toYear(date) - Fast year-based queries

---

## 5. Algorithms

### 5.1 Fast Mode Algorithm

**Time Complexity:** O(F) where F = number of files  
**Space Complexity:** O(1) - Constant memory

```
Algorithm: FastModeImport
Input: files[], check_mode='fast'
Output: statistics

1. For each file in files:
   2. Read first row → (ts1, o1, h1, l1, c1)
   3. Read last row → (ts2, o2, h2, l2, c2)
   4. Query DB:
      SELECT * FROM table 
      WHERE symbol=pair AND timestamp IN (ts1, ts2)
   5. If 2 results returned:
      6. Compare ohlc1 with db_result[0] (tolerance 1e-5)
      7. Compare ohlc2 with db_result[1] (tolerance 1e-5)
      8. If both match:
         9. stats.skipped_files++
         10. Continue  # Skip entire file
   11. Read entire file into memory
   12. Batch insert to DB
   13. stats.imported_files++
14. Return stats
```

**Pros:**
- Extremely fast (100x faster)
- Low memory usage
- Suitable for daily updates

**Cons:**
- May miss partial file changes
- Less accurate than comprehensive mode

---

### 5.2 Comprehensive Mode Algorithm

**Time Complexity:** O(F × R × log N) where:
- F = number of files
- R = records per file
- N = existing records in DB

**Space Complexity:** O(R) - Linear with file size

```
Algorithm: ComprehensiveModeImport
Input: files[], check_mode='comprehensive'
Output: statistics

1. For each file in files:
   2. Read entire file → df (R records)
   3. Get time_range: (min_ts, max_ts) from df
   4. Query DB:
      SELECT timestamp, o, h, l, c FROM table
      WHERE symbol=pair 
        AND timestamp >= min_ts 
        AND timestamp <= max_ts
   5. Build hash_map: {timestamp: (o,h,l,c)}
   6. new_records = []
   7. For each row in df:
      8. ts = row['timestamp']
      9. If ts not in hash_map:
         10. new_records.append(row)  # New
      11. Else:
         12. csv_ohlc = (row.o, row.h, row.l, row.c)
         13. db_ohlc = hash_map[ts]
         14. If not compare_ohlc(csv_ohlc, db_ohlc):
            15. new_records.append(row)  # Modified
   16. If len(new_records) > 0:
      17. Batch insert new_records to DB
      18. stats.imported_records += len(new_records)
   19. stats.skipped_records += (R - len(new_records))
20. Return stats
```

**Pros:**
- 100% accurate
- Detects partial file changes
- Suitable for data verification

**Cons:**
- Slower (10-20x slower than fast mode)
- Higher memory usage
- Higher DB load

---

## 6. File Processing Flow

### 6.1 M1 Data Flow

```
fxcm_data/EURUSD/M1/2024/week_01.csv
    │
    ├─ Read CSV (10,080 records for 1 week)
    │
    ├─ Validate (fast or comprehensive)
    │   │
    │   ├─ Fast Mode:
    │   │   ├─ Check first record: 2024-01-01 00:00:00
    │   │   ├─ Check last record: 2024-01-07 23:59:00
    │   │   └─ Decision: Skip or Import ALL
    │   │
    │   └─ Comprehensive Mode:
    │       ├─ Query DB for week range
    │       ├─ Compare all 10,080 records
    │       └─ Decision: Import only NEW/MODIFIED
    │
    └─ Insert to ClickHouse
        └─ forex_data.ohlcv_m1 (batches of 1000)
```

### 6.2 D1 Data Flow

```
fxcm_data/EURUSD/D1/2024.csv
    │
    ├─ Read CSV (260 trading days)
    │
    ├─ Validate (fast or comprehensive)
    │   │
    │   ├─ Fast Mode:
    │   │   ├─ Check first record: 2024-01-01
    │   │   ├─ Check last record: 2024-12-31
    │   │   └─ Decision: Skip or Import ALL
    │   │
    │   └─ Comprehensive Mode:
    │       ├─ Query DB for year 2024
    │       ├─ Compare all 260 records
    │       └─ Decision: Import only NEW/MODIFIED
    │
    └─ Insert to ClickHouse
        └─ forex_data.ohlcv_d1 (single batch)
```

---

## 7. Error Handling Strategy

### 7.1 Error Categories

| Category | Severity | Action |
|----------|----------|--------|
| File Not Found | Warning | Log + Continue |
| Malformed CSV | Error | Log + Skip File |
| DB Connection Lost | Critical | Retry 3x + Fail |
| Invalid Data | Warning | Log + Skip Record |
| Duplicate Key | Info | Skip Record |

### 7.2 Retry Logic

```python
def execute_with_retry(operation, max_retries=3, delay=1):
    for attempt in range(max_retries):
        try:
            return operation()
        except TransientError as e:
            if attempt < max_retries - 1:
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
                continue
            else:
                raise
```

---

## 8. Performance Optimization

### 8.1 Batch Processing

- Insert in batches of 1000 records
- Use CSV format for fastest insertion
- Connection pooling (reuse connections)

### 8.2 Memory Management

- Stream large files (don't load entirely)
- Clear DataFrame after each file
- Garbage collection after each pair

### 8.3 Database Optimization

- Use PRIMARY KEY for fast lookups
- Partition tables by month/year
- Enable compression (LZ4)

---

## 9. Security Considerations

1. **SQL Injection Prevention**
   - Use parameterized queries
   - Sanitize all inputs

2. **Authentication**
   - Support password authentication
   - Never log passwords

3. **Data Validation**
   - Validate OHLC relationships
   - Check timestamp formats
   - Reject malformed data

---

## 10. Testing Strategy

### 10.1 Unit Tests

- Test each method independently
- Mock ClickHouse connection
- Test edge cases

### 10.2 Integration Tests

- Test with real ClickHouse instance
- Test with sample CSV files
- Test both fast and comprehensive modes

### 10.3 Performance Tests

- Benchmark fast mode: 50,000 records/sec target
- Benchmark comprehensive mode: 10,000 records/sec target
- Memory usage < 500MB

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-05  
**Approved By:** binphilxiao
