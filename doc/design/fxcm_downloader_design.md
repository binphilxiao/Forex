# FXCM Data Downloader Design Documentation

**Project**: FXCM Historical Data Downloader v2.0  
**Author**: binphilxiao  
**Date**: 2025-10-05  
**Version**: 2.0.0

---

## 1. System Architecture

### 1.1 Overview
The FXCM Data Downloader is designed as a single-module Python application with a clear separation of concerns using object-oriented programming principles.

### 1.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                      │
│  ┌──────────────────┐          ┌──────────────────────────┐ │
│  │  Command Line    │          │   Batch File (Windows)   │ │
│  │  (argparse)      │          │   (download_fxcm_data.bat)│ │
│  └────────┬─────────┘          └──────────┬───────────────┘ │
│           │                               │                  │
└───────────┼───────────────────────────────┼──────────────────┘
            │                               │
            └───────────┬───────────────────┘
                        │
┌───────────────────────┼────────────────────────────────────┐
│                Application Layer                            │
│  ┌────────────────────▼────────────────────────────────┐   │
│  │        FXCMDataDownloader (main class)             │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │  - Initialization & Configuration            │  │   │
│  │  │  - HTTP Session Management                   │  │   │
│  │  │  - Logging Setup                             │  │   │
│  │  │  - Statistics Tracking                       │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │  Core Download Methods                       │  │   │
│  │  │  - download()                                │  │   │
│  │  │  - download_pair_timeframe()                 │  │   │
│  │  │  - download_m1_week()                        │  │   │
│  │  │  - download_d1_year()                        │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │  Helper Methods                              │  │   │
│  │  │  - _download_with_retry()                    │  │   │
│  │  │  - _normalize_columns()                      │  │   │
│  │  │  - _setup_logging()                          │  │   │
│  │  │  - _print_header()                           │  │   │
│  │  │  - _print_summary()                          │  │   │
│  │  │  - _save_summary_report()                    │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
            │                               │
┌───────────┼───────────────────────────────┼──────────────────┐
│                 External Dependencies                         │
│  ┌────────────┴────────┐      ┌──────────▼────────────────┐ │
│  │  FXCM Public API    │      │  File System              │ │
│  │  (HTTP/HTTPS)       │      │  - fxcm_data/ (output)    │ │
│  │                     │      │  - logs/ (logs)           │ │
│  └─────────────────────┘      └───────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Class Design

### 2.1 FXCMDataDownloader Class

The core class that handles all download operations.

#### Class Attributes

```python
AVAILABLE_PAIRS: List[str]
    List of supported currency pairs
    ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF']

AVAILABLE_TIMEFRAMES: List[str]
    List of supported timeframes
    ['M1', 'D1']

BASE_URL: str
    FXCM API base URL
    "https://candledata.fxcorporate.com"
```

#### Instance Attributes

```python
project_root: Path
    Project root directory

output_dir: Path
    Directory to save downloaded data (default: fxcm_data/)

log_dir: Path
    Directory to save log files (default: logs/)

max_retries: int
    Maximum number of retry attempts (default: 5)

retry_delay: float
    Delay between retry attempts in seconds (default: 0.5)

session: requests.Session
    HTTP session for API calls

stats: dict
    Download statistics
    {
        'total_files': int,
        'downloaded': int,
        'skipped': int,
        'failed': int,
        'total_records': int
    }

logger: logging.Logger
    Logger instance

log_file: Path
    Current log file path
```

---

## 3. Method Documentation

### 3.1 Public Methods

#### `__init__(output_dir, log_dir, max_retries, retry_delay)`

**Purpose**: Initialize the downloader with configuration

**Parameters**:
- `output_dir` (Path, optional): Output directory for data files
- `log_dir` (Path, optional): Directory for log files
- `max_retries` (int, optional): Maximum retry attempts (default: 5)
- `retry_delay` (float, optional): Delay between retries (default: 0.5)

**Returns**: None

**Side Effects**:
- Creates output and log directories
- Initializes HTTP session
- Sets up logging system
- Initializes statistics

**Example**:
```python
downloader = FXCMDataDownloader(
    output_dir=Path('my_data'),
    max_retries=3
)
```

---

#### `download(pairs, timeframes, start_year, end_year)`

**Purpose**: Main method to download FXCM historical data

**Parameters**:
- `pairs` (List[str], optional): Currency pairs to download (default: all)
- `timeframes` (List[str], optional): Timeframes to download (default: ['M1', 'D1'])
- `start_year` (int, optional): Start year (default: 2015)
- `end_year` (int, optional): End year (default: current year)

**Returns**: dict - Download statistics

**Raises**:
- `ValueError`: If invalid pairs or timeframes provided

**Algorithm**:
1. Validate inputs
2. Print download header
3. For each currency pair:
   - For each timeframe:
     - Call `download_pair_timeframe()`
4. Calculate elapsed time
5. Print summary
6. Save summary report
7. Return statistics

**Example**:
```python
stats = downloader.download(
    pairs=['EURUSD', 'GBPUSD'],
    timeframes=['M1'],
    start_year=2020,
    end_year=2023
)
```

---

#### `download_pair_timeframe(pair, timeframe, start_year, end_year)`

**Purpose**: Download all data for a specific pair and timeframe

**Parameters**:
- `pair` (str): Currency pair
- `timeframe` (str): Timeframe ('M1' or 'D1')
- `start_year` (int): Start year
- `end_year` (int): End year (inclusive)

**Returns**: dict - Statistics for this pair/timeframe

**Algorithm**:

**For M1 timeframe**:
1. For each year in range:
   - Create year directory
   - For each week (1-52):
     - Check if file exists (skip if yes)
     - Download week data
     - Save to CSV
     - Update statistics
     - Sleep 0.1s (rate limiting)

**For D1 timeframe**:
1. Create timeframe directory
2. For each year in range:
   - Check if file exists (skip if yes)
   - Download year data
   - Save to CSV
   - Update statistics
   - Sleep 0.1s (rate limiting)

**Example**:
```python
stats = downloader.download_pair_timeframe(
    'EURUSD', 'M1', 2020, 2023
)
```

---

#### `download_m1_week(pair, year, week)`

**Purpose**: Download M1 data for a specific week

**Parameters**:
- `pair` (str): Currency pair
- `year` (int): Year
- `week` (int): Week number (1-52)

**Returns**: pd.DataFrame or None - Downloaded data

**API Call**: `{BASE_URL}/m1/{pair}/{year}/{week}.csv.gz`

**Example**:
```python
df = downloader.download_m1_week('EURUSD', 2020, 1)
```

---

#### `download_d1_year(pair, year)`

**Purpose**: Download D1 data for a specific year

**Parameters**:
- `pair` (str): Currency pair
- `year` (int): Year

**Returns**: pd.DataFrame or None - Downloaded data

**API Call**: `{BASE_URL}/D1/{pair}/{year}.csv.gz`

**Example**:
```python
df = downloader.download_d1_year('EURUSD', 2020)
```

---

### 3.2 Private Helper Methods

#### `_setup_logging()`

**Purpose**: Configure logging system

**Side Effects**:
- Creates timestamped log file
- Configures file and console handlers
- Sets log levels and formatters

**Log File Format**: `fxcm_download_YYYYMMDD_HHMMSS.log`

**Log Levels**:
- File: DEBUG (all messages)
- Console: INFO (user-facing messages)

---

#### `_download_with_retry(url)`

**Purpose**: Download data from URL with retry mechanism

**Parameters**:
- `url` (str): URL to download

**Returns**: pd.DataFrame or None

**Algorithm**:
1. For attempt in range(max_retries):
   - Try HTTP GET request
   - If 200 OK:
     - Decompress gzip
     - Parse CSV
     - Normalize columns
     - Return DataFrame
   - If 404:
     - Retry if attempts remain
     - Log 404 on final attempt
   - If other error:
     - Log warning
   - On exception:
     - Retry if attempts remain
     - Log error on final attempt
2. Return None if all retries failed

**Error Handling**:
- Network errors: Retry with delay
- HTTP errors: Log and return None
- Decompression errors: Log and return None
- CSV parsing errors: Log and return None

---

#### `_normalize_columns(df)`

**Purpose**: Normalize CSV column names to standard format

**Parameters**:
- `df` (pd.DataFrame): Raw DataFrame from CSV

**Returns**: pd.DataFrame or None

**Algorithm**:
1. Convert columns to lowercase
2. Check for 'datetime' column (required)
3. If 'bidopen' exists (FXCM format):
   - Rename bidopen → Open
   - Rename bidhigh → High
   - Rename bidlow → Low
   - Rename bidclose → Close
   - Rename datetime → DateTime
4. Else (standard format):
   - Rename open → Open
   - Rename high → High
   - Rename low → Low
   - Rename close → Close
   - Rename datetime → DateTime
5. Convert DateTime to pandas datetime
6. Keep only required columns: ['DateTime', 'Open', 'High', 'Low', 'Close']
7. Return normalized DataFrame

**Column Mappings**:
```
FXCM Format:
    datetime → DateTime
    bidopen  → Open
    bidhigh  → High
    bidlow   → Low
    bidclose → Close

Standard Format:
    datetime → DateTime
    open     → Open
    high     → High
    low      → Low
    close    → Close
```

---

#### `_print_header(pairs, timeframes, start_year, end_year)`

**Purpose**: Print download header to console and log

**Parameters**:
- `pairs` (list): Currency pairs
- `timeframes` (list): Timeframes
- `start_year` (int): Start year
- `end_year` (int): End year

**Output Format**:
```
============================================================
FXCM Historical Data Downloader v2.0
============================================================
Currency Pairs: EURUSD, GBPUSD
Timeframes: M1, D1
Date Range: 2015 - 2025
Output Directory: C:\...\fxcm_data
Max Retries: 5
============================================================
```

---

#### `_print_summary(elapsed)`

**Purpose**: Print download summary to console and log

**Parameters**:
- `elapsed` (float): Time elapsed in seconds

**Output Format**:
```
============================================================
Download Summary
============================================================
Total Files Processed: 1000
  ✅ Downloaded: 850
  ⏭️  Skipped (existing): 100
  ❌ Failed/Not Available: 50
Total Records Downloaded: 5,000,000
Time Elapsed: 3600.5 seconds
============================================================
✅ Download completed successfully!
📄 Log file saved: logs/fxcm_download_20251005_120000.log
============================================================
```

---

#### `_save_summary_report(pairs, timeframes, start_year, end_year, elapsed)`

**Purpose**: Save summary report to text file

**Parameters**:
- `pairs` (list): Currency pairs
- `timeframes` (list): Timeframes
- `start_year` (int): Start year
- `end_year` (int): End year
- `elapsed` (float): Time elapsed in seconds

**File Format**: `fxcm_download_summary_YYYYMMDD_HHMMSS.txt`

**Content**:
- Configuration section
- Results section
- Completion timestamp

---

## 4. Data Structures

### 4.1 Directory Structure

```
fxcm_data/                          # Root output directory
├── EURUSD/                         # Currency pair
│   ├── M1/                         # M1 timeframe
│   │   ├── 2015/                   # Year
│   │   │   ├── week_01.csv         # Week 1 data
│   │   │   ├── week_02.csv
│   │   │   └── ...
│   │   │   └── week_52.csv
│   │   ├── 2016/
│   │   └── ...
│   └── D1/                         # D1 timeframe
│       ├── 2015.csv                # Year data
│       ├── 2016.csv
│       └── ...
├── GBPUSD/
│   ├── M1/
│   └── D1/
└── ...
```

### 4.2 CSV File Format

**Columns**: DateTime, Open, High, Low, Close

**Example**:
```csv
DateTime,Open,High,Low,Close
2020-01-01 00:00:00,1.1234,1.1240,1.1230,1.1238
2020-01-01 00:01:00,1.1238,1.1245,1.1235,1.1242
...
```

**Data Types**:
- DateTime: ISO 8601 format (YYYY-MM-DD HH:MM:SS)
- Open, High, Low, Close: Float (price values)

### 4.3 Statistics Dictionary

```python
{
    'total_files': int,      # Total files attempted
    'downloaded': int,       # Successfully downloaded
    'skipped': int,         # Skipped (already exist)
    'failed': int,          # Failed/not available
    'total_records': int    # Total OHLC records
}
```

---

## 5. API Integration

### 5.1 FXCM Public API

**Base URL**: `https://candledata.fxcorporate.com`

**Endpoints**:

#### M1 Data (Minute Candles)
```
GET /{timeframe}/{pair}/{year}/{week}.csv.gz

Example:
https://candledata.fxcorporate.com/m1/EURUSD/2020/1.csv.gz
```

**Parameters**:
- `timeframe`: "m1" (lowercase)
- `pair`: Currency pair (e.g., "EURUSD")
- `year`: Year (e.g., 2020)
- `week`: Week number (1-52)

**Response**: Gzip-compressed CSV file

---

#### D1 Data (Daily Candles)
```
GET /D1/{pair}/{year}.csv.gz

Example:
https://candledata.fxcorporate.com/D1/EURUSD/2020.csv.gz
```

**Parameters**:
- `pair`: Currency pair (e.g., "EURUSD")
- `year`: Year (e.g., 2020)

**Response**: Gzip-compressed CSV file

---

### 5.2 HTTP Status Codes

- **200 OK**: Data available, download successful
- **404 Not Found**: Data not available for this period (expected)
- **500 Internal Server Error**: Server error (retry)
- **Timeout**: Network timeout (retry)

---

## 6. Error Handling

### 6.1 Error Categories

#### Network Errors
- Connection timeout
- DNS resolution failure
- Network unreachable

**Handling**: Retry up to `max_retries` times

---

#### HTTP Errors
- 404 Not Found
- 500 Internal Server Error
- Other HTTP errors

**Handling**:
- 404: Log and skip (data not available)
- Others: Retry up to `max_retries` times

---

#### Data Errors
- Gzip decompression failure
- CSV parsing errors
- Unknown column format

**Handling**: Log error and skip file

---

### 6.2 Error Recovery Strategy

```
┌─────────────────┐
│  Download File  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      Yes     ┌──────────────┐
│  File Exists?   ├─────────────►│ Skip & Log   │
└────────┬────────┘              └──────────────┘
         │ No
         ▼
┌─────────────────┐
│  HTTP Request   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      200 OK  ┌──────────────┐
│  Status Code?   ├─────────────►│ Process Data │
└────────┬────────┘              └──────┬───────┘
         │ 404                          │
         ▼                              ▼
┌─────────────────┐              ┌──────────────┐
│  Max Retries?   │              │  Save CSV    │
└────────┬────────┘              └──────────────┘
         │ Yes
         ▼
┌─────────────────┐
│  Log & Skip     │
└─────────────────┘
```

---

## 7. Performance Considerations

### 7.1 Rate Limiting

**Delay**: 0.1 seconds between requests

**Reason**: Avoid overloading FXCM servers

**Implementation**: `time.sleep(0.1)` after each download

---

### 7.2 Memory Management

**Strategy**: Stream processing

- Download → Decompress → Parse → Save → Release
- No large data accumulation in memory
- Process one file at a time

**Memory Footprint**:
- Single M1 week file: ~1-10 MB
- Single D1 year file: ~1-5 MB
- Peak memory: < 100 MB

---

### 7.3 Disk I/O

**Optimization**:
- Check file existence before download (skip existing)
- Write directly to final location (no temp files)
- Use pandas `to_csv()` for efficient CSV writing

---

## 8. Security Considerations

### 8.1 Data Validation

- Validate URL construction
- Verify gzip decompression
- Check CSV structure
- Sanitize file paths

### 8.2 Input Validation

- Validate currency pairs against whitelist
- Validate timeframes against whitelist
- Validate year ranges (reasonable limits)
- Sanitize command-line arguments

### 8.3 Error Information

- Don't expose internal paths in error messages
- Log sensitive information only to file (not console)
- Handle exceptions gracefully

---

## 9. Testing Strategy

### 9.1 Unit Tests

Test individual methods:
- Initialization
- URL construction
- Column normalization
- Statistics tracking
- Directory creation

### 9.2 Integration Tests

Test full workflows:
- Download single file
- Download multiple files
- Skip existing files
- Handle 404 errors
- Retry mechanism

### 9.3 End-to-End Tests

Test complete scenarios:
- Download full dataset
- Resume interrupted download
- Handle network failures

---

## 10. Deployment

### 10.1 Requirements

- Python 3.7+
- Dependencies: pandas, requests

### 10.2 Installation

```bash
pip install pandas requests
```

### 10.3 Usage

```bash
# Default (all pairs, all timeframes, 2015-now)
python scripts/fxcm_data_downloader.py

# Specific configuration
python scripts/fxcm_data_downloader.py --pairs EURUSD --timeframes M1 --start-year 2020
```

---

## 11. Maintenance

### 11.1 Adding New Currency Pairs

1. Update `AVAILABLE_PAIRS` class attribute
2. Verify data availability on FXCM API
3. Update documentation

### 11.2 Adding New Timeframes

1. Update `AVAILABLE_TIMEFRAMES` class attribute
2. Add URL construction logic
3. Update directory structure logic
4. Update documentation

### 11.3 Logging

Log files are rotated automatically (one per run).

**Retention**: Manual cleanup required

**Recommendation**: Keep recent 30 days, archive older logs

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-05  
**Status**: Final
