# FXCM Data Importer - Requirements Specification

**Version:** 2.0.0  
**Author:** binphilxiao  
**Date:** 2025-10-05  
**Status:** Active

---

## 1. Overview

### 1.1 Purpose
The FXCM Data Importer is a professional-grade command-line tool designed to import FXCM forex historical data from CSV files into ClickHouse database with intelligent duplicate detection and flexible validation modes.

### 1.2 Scope
- Import M1 (1-minute) and D1 (daily) forex data
- Support 6 major currency pairs
- Smart duplicate detection with two validation modes
- ClickHouse database integration
- Comprehensive logging and reporting

---

## 2. Functional Requirements

### FR-1: Currency Pair Selection
**Priority:** High  
**Description:** User can select specific currency pairs or import all pairs

**Acceptance Criteria:**
- `--pairs` parameter accepts one or more currency pairs
- Default: All 6 pairs (EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF)
- Validate input against supported pairs
- Display selected pairs before import

**Example:**
```bash
python fxcm_importer.py --pairs EURUSD GBPUSD
python fxcm_importer.py  # Default: all pairs
```

---

### FR-2: Timeframe Selection
**Priority:** High  
**Description:** User can select M1, D1, or both timeframes

**Acceptance Criteria:**
- `--timeframes` parameter accepts M1, D1, or both
- Default: Both M1 and D1
- Validate timeframe input
- Display selected timeframes before import

**Example:**
```bash
python fxcm_importer.py --timeframes M1
python fxcm_importer.py --timeframes M1 D1  # Default
```

---

### FR-3: Date Range Selection
**Priority:** High  
**Description:** User can specify custom date range for import

**Acceptance Criteria:**
- `--start-year` parameter for start year
- `--end-year` parameter for end year
- Default: 2015 to current year
- Validate year range (2015-current)
- Support flexible year format

**Example:**
```bash
python fxcm_importer.py --start-year 2020 --end-year 2024
python fxcm_importer.py  # Default: 2015-now
```

---

### FR-4: Duplicate Detection - Fast Mode
**Priority:** High  
**Description:** Quick validation by checking first and last records only

**Acceptance Criteria:**
- Check if first record exists in database
- Check if last record exists in database
- If both exist with matching OHLC values → Skip file
- If either missing or values differ → Import file
- 100x faster than comprehensive mode
- Default validation mode

**Logic:**
```
File: week_01.csv (10,000 records)
1. Read first row: 2024-01-01 00:00:00, O:1.1000, H:1.1005, L:1.0995, C:1.1001
2. Read last row:  2024-01-07 23:59:00, O:1.1050, H:1.1055, L:1.1045, C:1.1051
3. Query DB for these two timestamps
4. Compare OHLC values
5. If match → Skip entire file
6. If no match → Import entire file
```

---

### FR-5: Duplicate Detection - Comprehensive Mode
**Priority:** Medium  
**Description:** Thorough validation by checking every record

**Acceptance Criteria:**
- Read all records from CSV file
- Query existing data for same time range from database
- Compare each record's OHLC values
- Skip records that exist with matching values
- Import only new or modified records
- Provide detailed skip/import statistics

**Logic:**
```
File: week_01.csv (10,000 records)
1. Read all 10,000 rows into memory
2. Query DB for same date range (e.g., 2024-01-01 to 2024-01-07)
3. Build hash map of existing data: {timestamp: (O,H,L,C)}
4. For each CSV row:
   a. Check if timestamp exists in hash map
   b. If exists, compare OHLC values (tolerance: 1e-5)
   c. If match → Skip row
   d. If different or new → Queue for import
5. Batch insert queued records
```

---

### FR-6: Validation Mode Selection
**Priority:** High  
**Description:** User can choose between fast and comprehensive validation

**Acceptance Criteria:**
- `--check-mode` parameter accepts 'fast' or 'comprehensive'
- Default: 'fast'
- Display current mode before import
- Show performance impact (est. time)

**Example:**
```bash
python fxcm_importer.py --check-mode fast          # Default
python fxcm_importer.py --check-mode comprehensive # Thorough
```

---

### FR-7: ClickHouse Configuration
**Priority:** High  
**Description:** Flexible ClickHouse connection configuration

**Acceptance Criteria:**
- `--ch-host` parameter (default: 192.168.2.168)
- `--ch-http-port` parameter (default: 8123)
- `--ch-native-port` parameter (default: 9000)
- `--ch-user` parameter (default: default)
- `--ch-password` parameter (default: empty)
- Test connection before import
- Clear error messages for connection failures

**Example:**
```bash
python fxcm_importer.py --ch-host 192.168.1.100 --ch-http-port 8123
```

---

### FR-8: Database Schema Compatibility
**Priority:** High  
**Description:** Import data according to existing ClickHouse schema

**M1 Table Schema:**
```sql
CREATE TABLE forex_data.ohlcv_m1 (
    symbol String,           -- e.g., 'EURUSD'
    timestamp DateTime,      -- e.g., '2024-01-01 00:00:00'
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
PRIMARY KEY (symbol, timestamp);
```

**D1 Table Schema:**
```sql
CREATE TABLE forex_data.ohlcv_d1 (
    symbol String,
    date Date,               -- e.g., '2024-01-01'
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
PRIMARY KEY (symbol, date);
```

---

### FR-9: CSV File Processing
**Priority:** High  
**Description:** Process CSV files with correct structure

**M1 CSV Structure:**
```
fxcm_data/
├── EURUSD/
│   ├── M1/
│   │   ├── 2015/
│   │   │   ├── week_01.csv
│   │   │   ├── week_02.csv
│   │   │   └── ...
│   │   ├── 2016/
│   │   └── ...
│   └── D1/
│       ├── 2015.csv
│       ├── 2016.csv
│       └── ...
```

**CSV Format:**
```csv
DateTime,Open,High,Low,Close
2024-01-01 00:00:00,1.10000,1.10050,1.09950,1.10010
2024-01-01 00:01:00,1.10010,1.10060,1.09960,1.10020
...
```

**Acceptance Criteria:**
- Auto-detect CSV structure
- Handle headers correctly
- Parse datetime formats (M1: DateTime, D1: Date)
- Validate OHLC data (High >= Low, Open/Close in range)
- Handle missing or malformed data gracefully

---

### FR-10: Logging and Reporting
**Priority:** High  
**Description:** Comprehensive logging and reporting

**Acceptance Criteria:**
- Log file saved to `logs/` directory
- Filename format: `fxcm_import_YYYYMMDD_HHMMSS.log`
- Log levels: INFO, WARNING, ERROR
- Report file format: `fxcm_import_report_YYYYMMDD_HHMMSS.txt`
- Include statistics summary
- Display progress during import

**Log Content:**
- Start/end timestamps
- Configuration parameters
- File processing status
- Database operations
- Errors and warnings
- Final statistics

**Report Content:**
```
============================================================
FXCM Data Import Report
============================================================

Configuration:
  Pairs: EURUSD, GBPUSD
  Timeframes: M1, D1
  Date Range: 2020-2024
  Check Mode: fast
  ClickHouse: 192.168.2.168:8123

Statistics:
  Total Files: 240
  Processed Files: 240
  Skipped Files (duplicate): 120
  Imported Files: 120
  Total Records Read: 12,500,000
  Records Imported: 6,250,000
  Records Skipped: 6,250,000
  Errors: 0
  
Processing Time: 1,247.5 seconds (20.8 minutes)
Average Speed: 10,020 records/second

Status: ✅ Import completed successfully
============================================================
```

---

### FR-11: Error Handling
**Priority:** High  
**Description:** Robust error handling and recovery

**Acceptance Criteria:**
- Continue processing on non-fatal errors
- Log all errors with context
- Provide actionable error messages
- Support graceful shutdown (Ctrl+C)
- Resume capability (skip already imported files)

**Error Scenarios:**
1. **File not found** → Log warning, continue
2. **Malformed CSV** → Log error, skip file
3. **Database connection lost** → Retry 3 times, then fail
4. **Invalid data values** → Log warning, skip record
5. **Duplicate key** → Handle per check mode

---

### FR-12: Performance Optimization
**Priority:** Medium  
**Description:** Efficient data processing

**Acceptance Criteria:**
- Batch insert (1000 records per batch)
- Connection pooling (reuse connections)
- Fast mode should be 50-100x faster than comprehensive
- Memory efficient (stream large files)
- Progress indicator for long operations

**Performance Targets:**
- Fast mode: 50,000 records/second
- Comprehensive mode: 10,000 records/second
- Memory usage: < 500MB for typical operation

---

## 3. Non-Functional Requirements

### NFR-1: Usability
- Clear command-line interface
- Helpful error messages
- Progress indicators
- Default values for all parameters
- `--help` documentation

### NFR-2: Reliability
- 99.9% success rate for valid data
- Atomic operations (transaction support)
- Data integrity validation
- Automatic retry on transient failures

### NFR-3: Maintainability
- Well-documented code
- Modular design
- Unit test coverage > 80%
- Clear logging

### NFR-4: Portability
- Windows and Linux compatible
- Python 3.7+ support
- Minimal external dependencies

### NFR-5: Performance
- Process 1M records in < 2 minutes (fast mode)
- Process 1M records in < 10 minutes (comprehensive mode)
- Concurrent file processing support (future)

---

## 4. User Stories

### US-1: Daily Data Update
**As a** forex trader  
**I want to** import yesterday's M1 data quickly  
**So that** I can backtest my strategies with latest data

**Acceptance:**
```bash
python fxcm_importer.py --timeframes M1 --start-year 2025 --end-year 2025
# Fast mode by default, skips existing data
# Complete in < 2 minutes
```

---

### US-2: Historical Data Import
**As a** data analyst  
**I want to** import 10 years of D1 data for all pairs  
**So that** I can perform long-term statistical analysis

**Acceptance:**
```bash
python fxcm_importer.py --timeframes D1 --start-year 2015 --end-year 2024
# Fast mode, processes all pairs
# Complete in < 5 minutes
```

---

### US-3: Data Verification
**As a** quality engineer  
**I want to** verify all data is correctly imported  
**So that** I can ensure data integrity

**Acceptance:**
```bash
python fxcm_importer.py --check-mode comprehensive --pairs EURUSD --start-year 2024
# Checks every record
# Provides detailed mismatch report
```

---

### US-4: Selective Import
**As a** developer  
**I want to** import only EUR pairs for testing  
**So that** I can quickly test my application

**Acceptance:**
```bash
python fxcm_importer.py --pairs EURUSD --timeframes M1 --start-year 2024 --end-year 2024
# Processes only EURUSD M1 for 2024
# Complete in < 30 seconds
```

---

## 5. Constraints

### Technical Constraints
- ClickHouse 20.3+ required
- Python 3.7+ required
- CSV files must follow FXCM format
- Sufficient disk space for logs

### Business Constraints
- Free and open-source
- No proprietary dependencies
- MIT License

---

## 6. Assumptions

1. CSV files are in standard FXCM format
2. ClickHouse server is accessible
3. User has write permissions to `logs/` directory
4. Sufficient network bandwidth for database operations
5. System time is synchronized (for timestamps)

---

## 7. Success Criteria

1. ✅ Import 1 million M1 records in < 2 minutes (fast mode)
2. ✅ Zero data loss for valid CSV files
3. ✅ 99.9% uptime during import
4. ✅ Clear error messages for all failure scenarios
5. ✅ Complete documentation coverage
6. ✅ 80%+ unit test coverage

---

## 8. Future Enhancements

### Phase 2 (Optional)
- Parallel processing (multi-threading)
- Incremental import (only new data since last run)
- Data validation rules (spike detection, gap detection)
- Email notifications on completion
- Web-based monitoring dashboard
- PostgreSQL support
- Parquet file export

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-05  
**Approved By:** binphilxiao
