# Data Consistency Verification Tool - Design Document

**Project:** FXCM Data Management System  
**Component:** Data Consistency Verification Tool  
**Version:** 1.0.0  
**Date:** 2025-10-05  
**Author:** FXCM Data Team

---

## 1. Architecture Overview

### 1.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  CLI Entry   │  │  Batch File  │  │  Python API  │      │
│  │    Point     │  │  (.bat)      │  │   Import     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────┐
│                  Core Verification Engine                     │
│                             │                                 │
│         ┌───────────────────┴────────────────────┐           │
│         │  DataConsistencyChecker (Main Class)   │           │
│         └───────────────────┬────────────────────┘           │
│                             │                                 │
│    ┌────────────┬───────────┼───────────┬──────────┐        │
│    │            │           │           │          │        │
│    ▼            ▼           ▼           ▼          ▼        │
│  ┌──────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌──────┐   │
│  │Config│  │  File  │  │Database│  │Verifi- │  │Report│   │
│  │Loader│  │Scanner │  │ Query  │  │cation  │  │ Gen  │   │
│  └──────┘  └────────┘  └────────┘  └────────┘  └──────┘   │
└───────────────────────────────────────────────────────────────┘
          │            │            │            │
          ▼            ▼            ▼            ▼
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│   Config   │  │    CSV     │  │ ClickHouse │  │   HTML     │
│    File    │  │   Files    │  │  Database  │  │   Report   │
│   (.json)  │  │  (fxcm_    │  │            │  │   (logs/)  │
│            │  │   data/)   │  │            │  │            │
└────────────┘  └────────────┘  └────────────┘  └────────────┘
```

### 1.2 Design Principles

1. **Single Responsibility:** Each class and method has one clear purpose
2. **Fail-Safe:** Errors in one file don't stop processing of others
3. **Read-Only:** Never modify source data or database
4. **Performance:** Minimize database queries and memory usage
5. **Transparency:** Provide detailed logging and progress feedback

---

## 2. Class Design

### 2.1 DataConsistencyChecker Class

**Purpose:** Main orchestrator for data verification process

#### 2.1.1 Class Attributes

```python
class DataConsistencyChecker:
    # Constants
    STATUS_NO_DATA = 'no_data'        # CSV file missing or DB empty
    STATUS_INCONSISTENT = 'inconsistent'  # Data mismatch
    STATUS_CONSISTENT = 'consistent'  # Data matches
    
    # ANSI color codes for terminal output
    COLOR_RED = '\033[91m'
    COLOR_YELLOW = '\033[93m'
    COLOR_GREEN = '\033[92m'
    COLOR_BLUE = '\033[94m'
    COLOR_RESET = '\033[0m'
    
    # Instance attributes
    config: dict              # ClickHouse configuration
    base_url: str            # HTTP endpoint URL
    auth: tuple              # (username, password)
    mode: str                # 'fast' or 'comprehensive'
    results: list            # Verification results
    stats: dict              # Statistics counters
```

#### 2.1.2 Class Methods

##### Constructor

```python
def __init__(self, config_path='config/clickhouse_config.json', mode='fast'):
    """
    Initialize the consistency checker.
    
    Args:
        config_path (str): Path to ClickHouse config file
        mode (str): 'fast' or 'comprehensive'
    
    Initializes:
        - Loads configuration from JSON
        - Sets up database connection parameters
        - Initializes statistics counters
        - Sets verification mode
    """
```

##### Configuration Methods

```python
def _load_config(self, config_path):
    """
    Load ClickHouse configuration from JSON file.
    
    Args:
        config_path (str): Path to configuration file
        
    Returns:
        dict: Configuration with keys:
            - host: Database hostname
            - http_port: HTTP interface port (default 8123)
            - port: Native protocol port (default 9000)
            - native_port: Alternative native port (default 9009)
            - user: Username
            - password: Password
            - database: Database name
            
    Raises:
        SystemExit: If config file not found or invalid JSON
    """
```

##### Database Methods

```python
def execute_query(self, query, timeout=60):
    """
    Execute SQL query on ClickHouse via HTTP interface.
    
    Args:
        query (str): SQL query string
        timeout (int): Request timeout in seconds
        
    Returns:
        tuple: (success: bool, result: str)
            - success: True if query succeeded
            - result: Query result or error message
            
    Implementation:
        - Uses HTTP POST to base_url
        - Includes Basic Auth credentials
        - Encodes query as UTF-8
        - Handles connection errors
    """
```

##### CSV Processing Methods

```python
def get_csv_boundaries(self, csv_path, timeframe):
    """
    Extract first and last timestamps from CSV file.
    
    Args:
        csv_path (Path): Path to CSV file
        timeframe (str): 'M1' or 'D1'
        
    Returns:
        tuple: (first_timestamp, last_timestamp, total_rows)
            Returns (None, None, 0) on error
            
    Implementation:
        - Uses pandas.read_csv()
        - Reads entire file (acceptable for ~52K rows max)
        - Gets first column as timestamp
        - Returns first and last values
        
    Performance:
        - ~100ms per file for M1 weekly files
        - ~500ms for D1 yearly files
    """
```

##### Fast Mode Methods

```python
def check_boundaries_in_db(self, symbol, timeframe, first_time, last_time):
    """
    Check if first and last timestamps exist in database.
    
    Args:
        symbol (str): Currency pair (e.g., 'EURUSD')
        timeframe (str): 'M1' or 'D1'
        first_time (str): First timestamp from CSV
        last_time (str): Last timestamp from CSV
        
    Returns:
        str: 'both' | 'partial' | 'none'
            - 'both': Both timestamps found → file likely complete
            - 'partial': Only one found → needs investigation
            - 'none': Neither found → not imported
            
    SQL Query:
        SELECT COUNT(*) 
        FROM forex_data.ohlcv_{timeframe}
        WHERE symbol = '{symbol}'
          AND {time_field} IN ('{first_time}', '{last_time}')
          
    Performance:
        - Uses indexed columns (symbol, timestamp/date)
        - Single query per file
        - ~50ms average query time
    """
```

##### Comprehensive Mode Methods

```python
def check_comprehensive(self, csv_path, symbol, timeframe):
    """
    Comprehensive verification: compare all CSV records with database.
    
    Args:
        csv_path (Path): Path to CSV file
        symbol (str): Currency pair
        timeframe (str): 'M1' or 'D1'
        
    Returns:
        dict: {
            'status': 'consistent' | 'inconsistent' | 'no_data' | 'error',
            'total': int,        # Total records in CSV
            'matched': int,      # Exact matches
            'missing': int,      # In CSV but not in DB
            'mismatched': int,   # In both but values differ
            'error': str         # Error message if status='error'
        }
        
    Algorithm:
        1. Read entire CSV file into DataFrame
        2. Query database for same time range
        3. Build dictionary of DB records: {timestamp: [o,h,l,c,v]}
        4. Iterate CSV rows:
           - If timestamp not in DB → missing++
           - If timestamp in DB:
             - If values match (within tolerance) → matched++
             - Else → mismatched++
        5. Determine overall status:
           - matched == total → 'consistent'
           - matched == 0 → 'no_data'
           - else → 'inconsistent'
           
    Performance:
        - Slower than fast mode (~2-5 seconds per file)
        - Memory usage: ~10-50 MB per file
        - Database query time: ~500ms-2s per file
        
    Comparison Tolerance:
        - Float comparison tolerance: 0.00001
        - Handles floating-point precision issues
    """
```

##### Main Verification Methods

```python
def verify_file(self, csv_path, symbol, timeframe):
    """
    Verify a single CSV file against database.
    
    Args:
        csv_path (Path): Path to CSV file
        symbol (str): Currency pair
        timeframe (str): 'M1' or 'D1'
        
    Returns:
        dict: Verification result structure (see section 3.1)
        
    Process Flow:
        1. Extract year and week from file path
        2. Read CSV boundaries
        3. If mode == 'fast':
             - Call check_boundaries_in_db()
             - Map result to status
        4. If mode == 'comprehensive':
             - Call check_comprehensive()
             - Get detailed statistics
        5. Build result dictionary
        6. Return result
        
    Error Handling:
        - CSV read errors → status='no_data'
        - Database errors → status='no_data', error in details
        - All errors logged but don't raise exceptions
    """

def verify_data(self, symbols=None, timeframes=None, 
                start_year=2015, end_year=None):
    """
    Main verification function - orchestrates entire process.
    
    Args:
        symbols (list): Currency pairs to check (default: all 6)
        timeframes (list): ['M1', 'D1'] (default: both)
        start_year (int): Start year (default: 2015)
        end_year (int): End year (default: current year)
        
    Returns:
        list: List of verification results (see section 3.1)
        
    Process Flow:
        1. Set defaults for optional parameters
        2. Initialize results list
        3. Validate data directory exists
        4. Print header with parameters
        5. For each symbol:
             For each timeframe:
               For each year in range:
                 If M1: For each week file:
                   - Call verify_file()
                   - Append to results
                   - Update statistics
                   - Print status
                 If D1: For year file:
                   - Call verify_file()
                   - etc.
        6. Print summary
        7. Return results
        
    File Discovery:
        - M1: fxcm_data/{symbol}/M1/{year}/week_{nn}.csv
        - D1: fxcm_data/{symbol}/D1/{year}.csv
        - Uses pathlib.glob() for pattern matching
        - Sorts files for consistent ordering
    """
```

##### Statistics Methods

```python
def _update_stats(self, status):
    """
    Update statistics counters based on verification status.
    
    Args:
        status (str): Verification status
        
    Updates:
        - stats['consistent'] if status == STATUS_CONSISTENT
        - stats['inconsistent'] if status == STATUS_INCONSISTENT
        - stats['no_data'] if status == STATUS_NO_DATA
    """
```

##### Output Methods

```python
def _print_file_status(self, result):
    """
    Print color-coded status line for a single file.
    
    Args:
        result (dict): Verification result
        
    Output Format:
        {icon} {identifier:35s} {color}{status}{reset}
        
    Examples:
        ✅ EURUSD M1 2015 Week-01            CONSISTENT
        ⚠️  GBPUSD M1 2020 Week-15            INCONSISTENT
        ❌ USDJPY D1 2018                    NO DATA
        
    Color Mapping:
        - Green: Consistent
        - Yellow: Inconsistent
        - Red: No Data
    """

def _print_summary(self):
    """
    Print verification summary with statistics.
    
    Output:
        ========================================
          📋 Verification Summary
        ========================================
        Total files checked: 300
        ✅ Consistent:    250 ( 83.3%)
        ⚠️  Inconsistent:   30 ( 10.0%)
        ❌ No data:        20 (  6.7%)
        ========================================
    """
```

##### Report Generation Methods

```python
def generate_html_report(self, output_path=None):
    """
    Generate HTML report with visual data representation.
    
    Args:
        output_path (str): Output file path
            Default: logs/consistency_report_{timestamp}.html
            
    Returns:
        str: Path to generated HTML file
        
    Process:
        1. Create logs/ directory if needed
        2. Organize results by symbol/timeframe/year/week
        3. Generate HTML content
        4. Write to file
        5. Return file path
        
    HTML Structure:
        - Header: Title, timestamp, gradient background
        - Statistics: Summary boxes with numbers
        - Content: One section per symbol
          - Subsections per timeframe
          - Year grids showing weeks
          - Color-coded cells
        - Legend: Explanation of colors
        - Footer: Version and copyright
    """

def _generate_html_content(self, organized):
    """
    Generate actual HTML markup.
    
    Args:
        organized (dict): Nested dict structure:
            {symbol: {timeframe: {year: {week: result}}}}
            
    Returns:
        str: Complete HTML document
        
    HTML Features:
        - Responsive design (CSS Grid)
        - Modern gradient styling
        - Hover effects on cells
        - Embedded CSS (no external dependencies)
        - Self-contained (works offline)
        
    Color Scheme:
        - Primary gradient: #667eea → #764ba2 (purple)
        - Consistent: #28a745 (green)
        - Inconsistent: #ffc107 (yellow/amber)
        - No data: #dc3545 (red)
        
    Browser Compatibility:
        - Chrome/Edge 90+
        - Firefox 88+
        - Safari 14+
    """
```

---

## 3. Data Structures

### 3.1 Verification Result Structure

Each verification result is a dictionary with the following schema:

```python
{
    'symbol': str,        # Currency pair (e.g., 'EURUSD')
    'timeframe': str,     # 'M1' or 'D1'
    'year': int,          # Year (e.g., 2015)
    'week': int,          # Week number (1-52 for M1, 0 for D1)
    'file': str,          # Full path to CSV file
    'status': str,        # 'no_data' | 'inconsistent' | 'consistent'
    'details': {          # Additional information
        'csv_rows': int,         # Total rows in CSV
        'first_time': str,       # First timestamp
        'last_time': str,        # Last timestamp
        'db_check': str,         # Fast mode: check result
        # Comprehensive mode additional fields:
        'total': int,            # Total records checked
        'matched': int,          # Records that match
        'missing': int,          # Records not in DB
        'mismatched': int,       # Records with different values
        'error': str             # Error message if applicable
    }
}
```

### 3.2 Statistics Structure

```python
{
    'total_files': int,    # Total files checked
    'no_data': int,        # Count of no_data status
    'inconsistent': int,   # Count of inconsistent status
    'consistent': int,     # Count of consistent status
    'errors': int          # Count of errors (not currently used)
}
```

### 3.3 Configuration Structure

```python
{
    "host": str,           # ClickHouse host (e.g., "192.168.2.168")
    "http_port": int,      # HTTP interface port (default: 8123)
    "port": int,           # Native protocol port (default: 9000)
    "native_port": int,    # Alternative native port (default: 9009)
    "user": str,           # Username (e.g., "default")
    "password": str,       # Password
    "database": str        # Database name (e.g., "default")
}
```

### 3.4 Organized Results Structure (for HTML)

```python
{
    'EURUSD': {
        'M1': {
            2015: {
                1: result_dict,
                2: result_dict,
                ...
                52: result_dict
            },
            2016: {...},
            ...
        },
        'D1': {
            2015: {
                0: result_dict  # Week 0 for D1 (full year)
            },
            ...
        }
    },
    'GBPUSD': {...},
    ...
}
```

---

## 4. Algorithm Details

### 4.1 Fast Mode Algorithm

```
FUNCTION check_file_fast(csv_path, symbol, timeframe):
    // Step 1: Read CSV boundaries
    first_time, last_time, row_count = read_csv_boundaries(csv_path)
    IF first_time is NULL:
        RETURN status='no_data'
    
    // Step 2: Check database
    table = timeframe == 'M1' ? 'ohlcv_m1' : 'ohlcv_d1'
    time_field = timeframe == 'M1' ? 'timestamp' : 'date'
    
    query = "
        SELECT COUNT(*) 
        FROM forex_data.{table}
        WHERE symbol = '{symbol}'
          AND {time_field} IN ('{first_time}', '{last_time}')
    "
    
    count = execute_query(query)
    
    // Step 3: Determine status
    IF count == 2:
        RETURN status='consistent'   // Both boundaries found
    ELSE IF count == 1:
        RETURN status='inconsistent' // Only one found
    ELSE:
        RETURN status='no_data'      // Neither found
```

**Time Complexity:** O(1) per file (constant database lookups)  
**Space Complexity:** O(1) (no large data structures)  
**Database Queries:** 1 per file

### 4.2 Comprehensive Mode Algorithm

```
FUNCTION check_file_comprehensive(csv_path, symbol, timeframe):
    // Step 1: Read CSV file
    df = read_csv(csv_path)
    IF df is empty:
        RETURN status='no_data', total=0, matched=0, missing=0
    
    first_time = df[0]['timestamp']
    last_time = df[-1]['timestamp']
    
    // Step 2: Query database for same range
    table = timeframe == 'M1' ? 'ohlcv_m1' : 'ohlcv_d1'
    time_field = timeframe == 'M1' ? 'timestamp' : 'date'
    
    query = "
        SELECT {time_field}, open, high, low, close, volume
        FROM forex_data.{table}
        WHERE symbol = '{symbol}'
          AND {time_field} >= '{first_time}'
          AND {time_field} <= '{last_time}'
        ORDER BY {time_field}
    "
    
    db_results = execute_query(query)
    
    // Step 3: Build database lookup dictionary
    db_data = {}
    FOR each row in db_results:
        db_data[row['timestamp']] = [row['open'], row['high'], 
                                      row['low'], row['close'], 
                                      row['volume']]
    
    // Step 4: Compare each CSV record
    matched = 0
    missing = 0
    mismatched = 0
    
    FOR each row in df:
        csv_values = [row['BidOpen'], row['BidHigh'], 
                      row['BidLow'], row['BidClose'], 
                      row['Volume']]
        
        IF row['timestamp'] NOT IN db_data:
            missing++
        ELSE:
            db_values = db_data[row['timestamp']]
            IF values_match(csv_values, db_values, tolerance=0.00001):
                matched++
            ELSE:
                mismatched++
    
    // Step 5: Determine overall status
    total = len(df)
    IF matched == total:
        status = 'consistent'
    ELSE IF matched == 0:
        status = 'no_data'
    ELSE:
        status = 'inconsistent'
    
    RETURN {
        status: status,
        total: total,
        matched: matched,
        missing: missing,
        mismatched: mismatched
    }
```

**Time Complexity:** O(n) where n = rows in CSV (~10,000-50,000)  
**Space Complexity:** O(n) for database lookup dictionary  
**Database Queries:** 1 per file (but returns all data)

### 4.3 File Discovery Algorithm

```
FUNCTION discover_files(symbols, timeframes, start_year, end_year):
    files = []
    
    FOR each symbol IN symbols:
        FOR each timeframe IN timeframes:
            IF timeframe == 'M1':
                // M1: Year folders with week files
                FOR year FROM start_year TO end_year:
                    path = "fxcm_data/{symbol}/M1/{year}/"
                    IF path exists:
                        week_files = glob(path + "week_*.csv")
                        FOR each file IN sorted(week_files):
                            files.append({
                                'path': file,
                                'symbol': symbol,
                                'timeframe': 'M1',
                                'year': year,
                                'week': extract_week_number(file)
                            })
            
            ELSE IF timeframe == 'D1':
                // D1: Year files directly in D1 folder
                FOR year FROM start_year TO end_year:
                    file = "fxcm_data/{symbol}/D1/{year}.csv"
                    IF file exists:
                        files.append({
                            'path': file,
                            'symbol': symbol,
                            'timeframe': 'D1',
                            'year': year,
                            'week': 0
                        })
    
    RETURN files
```

**Time Complexity:** O(s × t × y × w) where:
- s = number of symbols (~6)
- t = number of timeframes (1-2)
- y = number of years (~10)
- w = weeks per year (~52 for M1, 1 for D1)

**Result:** ~3,000-6,000 files typically

---

## 5. Database Schema

### 5.1 M1 Table Structure

```sql
CREATE TABLE forex_data.ohlcv_m1 (
    symbol String,           -- Currency pair (e.g., 'EURUSD')
    timestamp DateTime,      -- Minute timestamp
    open Float64,           -- Opening price
    high Float64,           -- Highest price
    low Float64,            -- Lowest price
    close Float64,          -- Closing price
    volume Float64          -- Volume
) ENGINE = MergeTree()
ORDER BY (symbol, timestamp);
```

**Indexes:** Primary key on (symbol, timestamp)  
**Typical Row Count:** ~26 million rows

### 5.2 D1 Table Structure

```sql
CREATE TABLE forex_data.ohlcv_d1 (
    symbol String,           -- Currency pair
    date Date,              -- Daily date
    open Float64,
    high Float64,
    low Float64,
    close Float64,
    volume Float64
) ENGINE = MergeTree()
ORDER BY (symbol, date);
```

**Indexes:** Primary key on (symbol, date)  
**Typical Row Count:** ~15,000 rows

---

## 6. Performance Analysis

### 6.1 Fast Mode Performance

| Component | Time | Notes |
|-----------|------|-------|
| CSV boundary read | 50-100ms | Pandas read_csv with full file |
| Database query | 20-50ms | Indexed lookup (2 values) |
| Status determination | <1ms | Simple comparison |
| **Per file total** | **~100ms** | Average |
| **All files (~3000)** | **~5 minutes** | Target met |

### 6.2 Comprehensive Mode Performance

| Component | Time | Notes |
|-----------|------|-------|
| CSV full read | 200-500ms | Full DataFrame load |
| Database query | 500ms-2s | Range query with all rows |
| Comparison loop | 100-500ms | Python iteration |
| **Per file total** | **~2-5s** | Average |
| **All files (~3000)** | **~3-5 hours** | Not for routine use |

### 6.3 Memory Usage

| Component | Memory | Notes |
|-----------|--------|-------|
| CSV DataFrame | 5-50 MB | Depends on file size |
| Database results | 5-50 MB | Similar to CSV |
| Lookup dictionary | 5-50 MB | Python dict overhead |
| **Peak per file** | **~150 MB** | Comprehensive mode |
| **Total (serial)** | **~200 MB** | Includes overhead |

### 6.4 Network Usage

| Mode | Queries/File | Data Transfer/File | Total (3000 files) |
|------|--------------|--------------------|--------------------|
| Fast | 1 | ~500 bytes | ~1.5 MB |
| Comprehensive | 1 | 1-10 MB | ~15 GB |

---

## 7. Error Handling

### 7.1 Error Categories

| Error Type | Handling Strategy | User Impact |
|------------|------------------|-------------|
| Config file not found | Exit with error message | Script stops |
| Invalid JSON config | Exit with error message | Script stops |
| Database unreachable | Mark files as 'error', continue | Some files show error |
| CSV file not readable | Mark as 'no_data', continue | Individual file error |
| CSV parsing error | Mark as 'no_data', continue | Individual file error |
| Query timeout | Retry once, then mark error | Slow queries detected |
| HTML write failure | Print error, return results | Report not saved |

### 7.2 Error Recovery

```python
# Pattern used throughout codebase
try:
    result = risky_operation()
except SpecificException as e:
    log_error(e)
    return safe_default_value()
finally:
    cleanup_if_needed()
```

### 7.3 Logging Strategy

- **Console Output:** Real-time progress, color-coded status
- **HTML Report:** Persistent record of verification
- **Return Data:** Programmatic access to errors
- **No Log Files:** Keep it simple, terminal + HTML sufficient

---

## 8. Security Considerations

### 8.1 Database Access

- **Authentication:** Uses ClickHouse username/password
- **Connection:** HTTP (not HTTPS) - assumes trusted network
- **SQL Injection:** Uses parameterized queries (f-strings with validated inputs)
- **Read-Only:** Tool never modifies data (SELECT queries only)

### 8.2 File System Access

- **Read Permissions:** Needs read access to:
  - config/clickhouse_config.json
  - fxcm_data/ directory tree
- **Write Permissions:** Needs write access to:
  - logs/ directory
- **No Sensitive Data:** HTML reports contain statistics only, no passwords

### 8.3 Recommendations

1. **Network:** Run on trusted network or use SSH tunnel for remote DB
2. **Config:** Protect clickhouse_config.json (contains password)
3. **Reports:** HTML reports safe to share (no credentials)

---

## 9. Testing Strategy

### 9.1 Unit Tests

Test individual methods in isolation:

```python
# Test configuration loading
test_load_valid_config()
test_load_missing_config()
test_load_invalid_json()

# Test CSV reading
test_read_valid_csv()
test_read_empty_csv()
test_read_corrupt_csv()

# Test database queries
test_execute_valid_query()
test_execute_invalid_query()
test_execute_with_timeout()

# Test verification logic
test_verify_consistent_file()
test_verify_inconsistent_file()
test_verify_missing_file()
```

### 9.2 Integration Tests

Test complete workflows:

```python
# Fast mode end-to-end
test_fast_mode_single_symbol()
test_fast_mode_all_symbols()

# Comprehensive mode end-to-end
test_comprehensive_mode_single_file()

# Report generation
test_generate_html_report()
test_html_report_content()
```

### 9.3 Performance Tests

```python
test_fast_mode_performance()  # Should complete in < 5 min
test_memory_usage()           # Should stay under 500 MB
test_concurrent_queries()     # Database load test
```

### 9.4 Acceptance Tests

Based on user stories:

```python
test_quick_health_check()     # US-1
test_deep_dive_investigation() # US-2
test_visual_report_review()   # US-3
test_automated_integration()  # US-4
```

---

## 10. Future Enhancements

### 10.1 Performance Optimizations

**Parallel Processing:**
```python
# Current: Serial processing
for file in files:
    result = verify_file(file)

# Future: Parallel processing
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(verify_file, files)
```

**Batch Queries:**
```python
# Current: One query per file
query = f"SELECT ... WHERE file = '{file}'"

# Future: Batch multiple files
query = f"SELECT ... WHERE file IN {tuple(files)}"
```

### 10.2 Additional Features

1. **Diff Reporting:** Show exact differences when values mismatch
2. **Trend Analysis:** Track consistency over time
3. **Auto-Remediation:** Automatically re-import inconsistent files
4. **Email Notifications:** Send reports via email
5. **Web Dashboard:** Real-time monitoring interface

### 10.3 Code Quality Improvements

1. **Type Hints:** Add full type annotations
2. **Logging Framework:** Replace prints with logging module
3. **Configuration Validation:** JSON schema validation
4. **Progress Bars:** Add tqdm for better progress indication

---

## 11. Dependencies

### 11.1 External Libraries

```python
# Standard library
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import time

# Third-party (requires pip install)
import pandas         # CSV processing
import requests       # HTTP communication
```

### 11.2 System Requirements

- **Python:** 3.7 or higher
- **Operating System:** Windows 10/11, Linux
- **Memory:** 512 MB minimum, 1 GB recommended
- **Network:** Access to ClickHouse server
- **Disk Space:** 10 MB for script, 100 MB for logs

---

## 12. Deployment

### 12.1 Installation

```bash
# 1. Clone/download project
cd /path/to/Forex

# 2. Install dependencies
pip install pandas requests

# 3. Configure database
# Edit config/clickhouse_config.json with correct credentials

# 4. Test connection
python scripts/test/test_verify_consistency.py
```

### 12.2 Configuration

Edit `config/clickhouse_config.json`:

```json
{
    "host": "192.168.2.168",
    "http_port": 8123,
    "port": 9000,
    "native_port": 9009,
    "user": "default",
    "password": "your_password_here",
    "database": "default"
}
```

### 12.3 Execution

```bash
# Windows
verify_consistency.bat

# Linux/Mac
python scripts/verify_data_consistency.py

# With options
python scripts/verify_data_consistency.py --mode comprehensive --symbols EURUSD GBPUSD
```

---

## 13. Maintenance

### 13.1 Regular Tasks

- **Weekly:** Review consistency reports for trends
- **Monthly:** Archive old reports from logs/
- **Quarterly:** Update dependencies (`pip install --upgrade`)

### 13.2 Troubleshooting

| Issue | Diagnosis | Solution |
|-------|-----------|----------|
| "Config file not found" | Missing config | Copy from template |
| "Database connection failed" | Network/credentials | Check config, ping host |
| "No files found" | Wrong directory | Run from project root |
| "Out of memory" | Large dataset in comprehensive mode | Use fast mode or increase RAM |

---

## 14. Glossary

| Term | Definition |
|------|------------|
| Boundary Check | Verifying only first and last records |
| OHLCV | Open, High, Low, Close, Volume |
| Consistency | Exact match between CSV and database |
| Fast Mode | Verification using boundary checks only |
| Comprehensive Mode | Verification of all records |
| Status | Classification result (consistent/inconsistent/no_data) |

---

## 15. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-10-05 | FXCM Data Team | Initial design document |

---

**Document Status:** APPROVED  
**Implementation Status:** COMPLETE  
**Next Review:** 2025-11-05
