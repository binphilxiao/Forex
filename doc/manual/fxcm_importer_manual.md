# FXCM Data Importer v2.0 - User Manual

**Complete guide to importing FXCM forex data to ClickHouse**

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation](#2-installation)
3. [Quick Start](#3-quick-start)
4. [Command-Line Reference](#4-command-line-reference)
5. [Understanding Validation Modes](#5-understanding-validation-modes)
6. [Usage Examples](#6-usage-examples)
7. [Configuration](#7-configuration)
8. [Output and Reports](#8-output-and-reports)
9. [Troubleshooting](#9-troubleshooting)
10. [FAQ](#10-faq)

---

## 1. Introduction

### 1.1 Overview

The FXCM Data Importer v2.0 is a professional command-line tool that imports FXCM forex historical data from CSV files into ClickHouse database with intelligent duplicate detection.

### 1.2 Key Features

- ✅ **Smart Duplicate Detection**: Two validation modes (fast/comprehensive)
- ✅ **Multi-Currency Support**: 6 major pairs (EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF)
- ✅ **Multi-Timeframe Support**: M1 (1-minute) and D1 (daily)
- ✅ **Flexible Configuration**: Command-line parameters for all options
- ✅ **High Performance**: Process 50,000+ records/second (fast mode)
- ✅ **Comprehensive Logging**: Detailed logs and reports
- ✅ **Windows-Friendly**: Includes batch launcher

### 1.3 System Requirements

**Software:**
- Python 3.7 or higher
- ClickHouse database server (v21.3+)
- 4GB RAM minimum (8GB recommended for large datasets)
- 100GB disk space (for CSV files and database)

**Python Libraries:**
- pandas
- clickhouse-connect

**Operating System:**
- Windows 10/11 (primary)
- Linux (compatible)
- macOS (compatible)

---

## 2. Installation

### 2.1 Install Python

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run installer and check "Add Python to PATH"
3. Verify installation:
```bash
python --version
```

### 2.2 Install Dependencies

```bash
pip install pandas clickhouse-connect
```

**Verify installation:**
```bash
python -c "import pandas, clickhouse_connect; print('OK')"
```

### 2.3 Set Up ClickHouse

**Install ClickHouse:**
- Windows: [ClickHouse Download](https://clickhouse.com/docs/en/getting-started/install/)
- Linux: `sudo apt install clickhouse-server clickhouse-client`

**Create database and tables:**
```sql
-- Create database
CREATE DATABASE IF NOT EXISTS forex_data;

-- Create M1 table
CREATE TABLE forex_data.ohlcv_m1 (
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
PRIMARY KEY (symbol, timestamp);

-- Create D1 table
CREATE TABLE forex_data.ohlcv_d1 (
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
PRIMARY KEY (symbol, date);
```

**Alternatively, use the creation script:**
```bash
python scripts\create_clickhouse_tables.py
```

### 2.4 Verify Installation

```bash
python scripts\fxcm_importer.py --help
```

If you see the help message, installation is successful.

---

## 3. Quick Start

### 3.1 Prepare CSV Data

Ensure your CSV files are organized correctly:

```
fxcm_data/
├── EURUSD/
│   ├── M1/
│   │   ├── 2024/
│   │   │   ├── week_01.csv
│   │   │   ├── week_02.csv
│   │   │   └── ...
│   │   └── 2025/
│   └── D1/
│       ├── 2024.csv
│       └── 2025.csv
└── ...
```

**CSV format:**
```csv
DateTime,Open,High,Low,Close
2024-01-01 00:00:00,1.10000,1.10050,1.09950,1.10010
2024-01-01 00:01:00,1.10010,1.10060,1.09960,1.10020
```

### 3.2 Basic Import (Windows)

**Method 1: Double-click batch file**
```
import_fxcm_data.bat
```

**Method 2: Command line**
```bash
python scripts\fxcm_importer.py
```

This will import all pairs, all timeframes, from 2015 to current year.

### 3.3 Check Results

**Console output:**
- Shows progress in real-time
- Displays statistics at the end

**Log files:** `logs/fxcm_import_*.log`
- Detailed processing log

**Report:** `logs/fxcm_import_report_*.txt`
- Summary statistics

---

## 4. Command-Line Reference

### 4.1 Basic Syntax

```bash
python scripts\fxcm_importer.py [OPTIONS]
```

### 4.2 Parameters

#### Currency Pairs

```bash
--pairs PAIR1 [PAIR2 ...]
```

**Available pairs:**
- EURUSD
- GBPUSD
- USDJPY
- AUDUSD
- USDCAD
- USDCHF

**Default:** All 6 pairs

**Examples:**
```bash
# Single pair
--pairs EURUSD

# Multiple pairs
--pairs EURUSD GBPUSD USDJPY

# All pairs (default)
(omit --pairs parameter)
```

---

#### Timeframes

```bash
--timeframes TF1 [TF2 ...]
```

**Available timeframes:**
- M1 (1-minute candles)
- D1 (daily candles)

**Default:** M1 D1 (both)

**Examples:**
```bash
# M1 only
--timeframes M1

# D1 only
--timeframes D1

# Both (default)
--timeframes M1 D1
```

---

#### Date Range

```bash
--start-year YYYY
--end-year YYYY
```

**Default:** 
- Start: 2015
- End: Current year

**Examples:**
```bash
# Specific year
--start-year 2024 --end-year 2024

# Year range
--start-year 2020 --end-year 2024

# From 2015 to now (default)
(omit parameters)
```

---

#### Validation Mode

```bash
--check-mode MODE
```

**Available modes:**
- `fast` (default): Check only first and last records
- `comprehensive`: Check every single record

**Default:** fast

**Examples:**
```bash
# Fast mode (default)
--check-mode fast

# Comprehensive mode
--check-mode comprehensive
```

---

#### ClickHouse Configuration

```bash
--ch-host HOST
--ch-http-port PORT
--ch-user USERNAME
--ch-password PASSWORD
```

**Defaults:**
- Host: 192.168.2.168
- Port: 8123
- User: default
- Password: (empty)

**Examples:**
```bash
# Custom host
--ch-host 192.168.1.100

# Custom port
--ch-http-port 9000

# With authentication
--ch-user admin --ch-password secret123

# Complete configuration
--ch-host 192.168.1.100 --ch-http-port 8123 --ch-user admin --ch-password secret
```

### 4.3 Help

```bash
python scripts\fxcm_importer.py --help
```

---

## 5. Understanding Validation Modes

### 5.1 Fast Mode (Default)

**How it works:**
1. Read first and last record from CSV file
2. Query database for these specific records
3. Compare OHLC values with tolerance (0.00001)
4. If both match → file already imported (skip)
5. If mismatch → import entire file

**Characteristics:**
- ⚡ Speed: 50,000 records/second
- ⚡ Database queries: Only 2 per file
- ⚡ Memory usage: Very low
- ⚠️ Limitation: May miss partial file changes

**Algorithm complexity:** O(1) per file

**Best for:**
- Daily updates
- Regular imports
- Large datasets
- When files are never modified after import

**Example:**
```bash
python scripts\fxcm_importer.py --check-mode fast
```

---

### 5.2 Comprehensive Mode

**How it works:**
1. Read all records from CSV file
2. Query database for all records in the same time range
3. Compare every single record
4. If 100% match → file already imported (skip)
5. If any mismatch → import entire file

**Characteristics:**
- 🔍 Speed: 10,000 records/second (slower but thorough)
- 🔍 Database queries: Multiple range queries
- 🔍 Memory usage: Moderate
- ✅ Accuracy: 100% - detects all changes

**Algorithm complexity:** O(N) per file (N = number of records)

**Best for:**
- Data verification
- Integrity checks
- Detecting partial file corruption
- Monthly audits

**Example:**
```bash
python scripts\fxcm_importer.py --check-mode comprehensive
```

---

### 5.3 Comparison Table

| Aspect | Fast Mode | Comprehensive Mode |
|--------|-----------|-------------------|
| Speed | 50,000 rec/sec | 10,000 rec/sec |
| DB Queries | 2 per file | Multiple per file |
| Memory | Very Low | Moderate |
| Accuracy | 99%+ | 100% |
| Detection | First/last only | Every record |
| Use Case | Daily updates | Data verification |

---

### 5.4 Choosing the Right Mode

**Use Fast Mode when:**
- ✅ Running daily updates
- ✅ Files are never modified after creation
- ✅ Speed is critical
- ✅ Processing large datasets (10+ years)

**Use Comprehensive Mode when:**
- ✅ Verifying data integrity
- ✅ Investigating data issues
- ✅ After database maintenance
- ✅ Monthly/quarterly audits
- ✅ When files may have been modified

**Recommended workflow:**
```bash
# Daily: Fast mode
python scripts\fxcm_importer.py --check-mode fast --start-year 2025

# Weekly: Fast mode
python scripts\fxcm_importer.py --check-mode fast --start-year 2025

# Monthly: Comprehensive mode (verification)
python scripts\fxcm_importer.py --check-mode comprehensive --start-year 2025
```

---

## 6. Usage Examples

### 6.1 Daily Update Workflow

**Scenario:** Import yesterday's M1 data

```bash
# Step 1: Download new data (if needed)
python scripts\fxcm_data_downloader.py --start-year 2025

# Step 2: Import with fast mode
python scripts\fxcm_importer.py --timeframes M1 --start-year 2025 --end-year 2025

# Step 3: Check report
type logs\fxcm_import_report_*.txt
```

**Expected time:** < 2 minutes

---

### 6.2 Historical Data Import

**Scenario:** Import 10 years of D1 data for all pairs

```bash
python scripts\fxcm_importer.py --timeframes D1 --start-year 2015 --end-year 2024
```

**Expected time:** < 5 minutes (fast mode)

---

### 6.3 Selective Import

**Scenario:** Import only EURUSD M1 for January 2024

```bash
python scripts\fxcm_importer.py --pairs EURUSD --timeframes M1 --start-year 2024 --end-year 2024
```

**Expected time:** < 30 seconds

---

### 6.4 Data Verification

**Scenario:** Verify all 2024 data is correctly imported

```bash
python scripts\fxcm_importer.py --check-mode comprehensive --start-year 2024 --end-year 2024
```

**Expected time:** 5-10 minutes (depends on data size)

---

### 6.5 Custom ClickHouse Server

**Scenario:** Import to remote ClickHouse server

```bash
python scripts\fxcm_importer.py --ch-host 10.0.0.100 --ch-http-port 8123 --ch-user trader --ch-password mysecret
```

---

### 6.6 Re-import After Database Reset

**Scenario:** Database was dropped, re-import all data

```bash
# Step 1: Recreate tables
python scripts\create_clickhouse_tables.py

# Step 2: Import all data (fast mode is fine since DB is empty)
python scripts\fxcm_importer.py --start-year 2015
```

**Expected time:** 10-30 minutes (depending on data size)

---

## 7. Configuration

### 7.1 Default Configuration

**Default values (when no parameters provided):**

```python
{
    'pairs': ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF'],
    'timeframes': ['M1', 'D1'],
    'start_year': 2015,
    'end_year': 2025,  # Current year
    'check_mode': 'fast',
    'ch_host': '192.168.2.168',
    'ch_http_port': 8123,
    'ch_user': 'default',
    'ch_password': '',
    'data_dir': 'fxcm_data',
    'batch_size': 1000,
    'tolerance': 0.00001
}
```

### 7.2 Modifying Configuration

**Option 1: Command-line parameters (recommended)**
```bash
python scripts\fxcm_importer.py --pairs EURUSD --timeframes M1
```

**Option 2: Modify script defaults**

Edit `scripts/fxcm_importer.py`:
```python
# Line ~650
parser.add_argument('--ch-host', default='192.168.2.168', ...)
```

Change `default='192.168.2.168'` to your preferred host.

### 7.3 Environment Variables (Future Feature)

Not yet supported. Use command-line parameters.

---

## 8. Output and Reports

### 8.1 Console Output

**During processing:**
```
============================================================
FXCM Data Importer v2.0
============================================================
Currency Pairs: EURUSD, GBPUSD
Timeframes: M1, D1
Year Range: 2024 - 2024
Check Mode: Fast
ClickHouse: 192.168.2.168:8123
============================================================

============================================================
Processing: EURUSD
============================================================

⏱️  Timeframe: M1

📅 Year: 2024
  📊 Found 52 files
  📄 Processing: week_01.csv
    ⏭️  Skipped: File exists in DB (10,080 records)
  📄 Processing: week_02.csv
    ✅ Imported: 10,080 records
  ...
```

**Final summary:**
```
============================================================
Import Summary
============================================================

Statistics:
  Total Files Found: 240
  Files Processed: 240
  Files Skipped (duplicate): 120
  
  Total Records Read: 12,500,000
  Records Imported: 6,250,000
  Records Skipped: 6,250,000
  Errors: 0
  
Processing Time: 125.5 seconds (2.1 minutes)
Average Speed: 99,601 records/second

Status: ✅ Import completed successfully
============================================================
```

### 8.2 Log Files

**Location:** `logs/`

**Filename format:** `fxcm_import_YYYYMMDD_HHMMSS.log`

**Content:**
```
2025-01-05 14:30:15 - INFO - FXCM Data Importer v2.0 started
2025-01-05 14:30:15 - INFO - Processing: EURUSD
2025-01-05 14:30:15 - INFO - Timeframe: M1
2025-01-05 14:30:15 - INFO - Year: 2024
2025-01-05 14:30:15 - INFO - Found 52 files
2025-01-05 14:30:15 - INFO - Processing: week_01.csv
2025-01-05 14:30:15 - INFO - File exists in DB (fast mode check), skipping
2025-01-05 14:30:16 - INFO - Processing: week_02.csv
2025-01-05 14:30:16 - INFO - Importing 10,080 records
...
```

### 8.3 Report Files

**Location:** `logs/`

**Filename format:** `fxcm_import_report_YYYYMMDD_HHMMSS.txt`

**Content:**
```
============================================================
FXCM Data Importer v2.0 - Import Report
============================================================

Generated: 2025-01-05 14:32:30

Configuration:
  Currency Pairs: EURUSD, GBPUSD
  Timeframes: M1, D1
  Year Range: 2024 - 2024
  Check Mode: fast
  ClickHouse: 192.168.2.168:8123

Statistics:
  Total Files Found: 240
  Files Processed: 240
  Files Skipped: 120
  
  Total Records Read: 12,500,000
  Records Imported: 6,250,000
  Records Skipped: 6,250,000
  Errors: 0

Performance:
  Processing Time: 125.5 seconds
  Average Speed: 99,601 records/second

Status: SUCCESS
============================================================
```

---

## 9. Troubleshooting

### 9.1 ClickHouse Connection Issues

**Error:**
```
Error: Cannot connect to ClickHouse at 192.168.2.168:8123
```

**Solutions:**

1. **Check if ClickHouse is running:**
```bash
curl http://192.168.2.168:8123
# Should return: Ok.
```

2. **Test with clickhouse-client:**
```bash
clickhouse-client --host 192.168.2.168 --port 9000
```

3. **Check firewall:**
```bash
# Windows: Allow port 8123 in Windows Firewall
# Linux: sudo ufw allow 8123
```

4. **Verify host/port:**
```bash
python scripts\fxcm_importer.py --ch-host localhost --ch-http-port 8123
```

---

### 9.2 CSV Files Not Found

**Error:**
```
Error: No CSV files found for EURUSD M1 2024
```

**Solutions:**

1. **Check directory structure:**
```bash
dir fxcm_data\EURUSD\M1\2024
```

2. **Verify file naming:**
   - M1 files: `week_01.csv` to `week_52.csv`
   - D1 files: `YYYY.csv` (e.g., `2024.csv`)

3. **Download missing data:**
```bash
python scripts\fxcm_data_downloader.py --pairs EURUSD --start-year 2024
```

---

### 9.3 Python Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'pandas'
```

**Solution:**
```bash
pip install pandas clickhouse-connect
```

---

### 9.4 Memory Error

**Error:**
```
MemoryError: Unable to allocate array
```

**Solutions:**

1. **Process year by year:**
```bash
python scripts\fxcm_importer.py --start-year 2024 --end-year 2024
```

2. **Process one pair at a time:**
```bash
python scripts\fxcm_importer.py --pairs EURUSD
```

3. **Use fast mode:**
```bash
python scripts\fxcm_importer.py --check-mode fast
```

---

### 9.5 Database Table Not Found

**Error:**
```
Error: Table forex_data.ohlcv_m1 does not exist
```

**Solution:**
```bash
python scripts\create_clickhouse_tables.py
```

Or create manually:
```sql
CREATE TABLE forex_data.ohlcv_m1 (
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
ORDER BY (symbol, timestamp);
```

---

### 9.6 Slow Import Speed

**Issue:** Import is too slow

**Solutions:**

1. **Use fast mode (if not already):**
```bash
python scripts\fxcm_importer.py --check-mode fast
```

2. **Check ClickHouse performance:**
```sql
-- Check if too many parts
SELECT table, count() AS parts
FROM system.parts
WHERE database = 'forex_data'
GROUP BY table;

-- Optimize if needed
OPTIMIZE TABLE forex_data.ohlcv_m1;
```

3. **Check disk I/O:**
   - Use SSD instead of HDD
   - Close other applications

---

## 10. FAQ

### Q1: How long does it take to import 10 years of M1 data?

**A:** Approximately 10-30 minutes depending on:
- Check mode (fast vs comprehensive)
- Number of pairs
- Hardware (SSD vs HDD)
- ClickHouse configuration

**Example timing:**
- Fast mode, 1 pair, SSD: ~5 minutes
- Fast mode, 6 pairs, SSD: ~20 minutes
- Comprehensive mode, 6 pairs, SSD: ~2 hours

---

### Q2: Can I run multiple imports in parallel?

**A:** Not recommended. ClickHouse can handle it, but:
- File I/O may become a bottleneck
- Memory usage increases
- Log files may interleave

**Better approach:** Process year by year or pair by pair sequentially.

---

### Q3: What happens if import is interrupted?

**A:** 
- ✅ Already imported files remain in database
- ✅ Partially imported files are rolled back (transaction safety)
- ✅ Re-run the same command to resume

**Example:**
```bash
# Import interrupted at 50%
# Just re-run:
python scripts\fxcm_importer.py

# Fast mode will skip already imported files
# Only remaining files will be processed
```

---

### Q4: How do I verify data integrity?

**A:** Use comprehensive mode:
```bash
python scripts\fxcm_importer.py --check-mode comprehensive --start-year 2024
```

This checks every single record against the database.

---

### Q5: Can I import to multiple ClickHouse databases?

**A:** Yes, specify different hosts:

```bash
# Production
python scripts\fxcm_importer.py --ch-host 192.168.2.168

# Testing
python scripts\fxcm_importer.py --ch-host 192.168.2.169
```

---

### Q6: How much disk space do I need?

**A:** Estimate:
- **M1 CSV files:** ~50GB per pair per 10 years
- **D1 CSV files:** ~1MB per pair per 10 years
- **ClickHouse database:** ~30% of CSV size (compression)

**Total for 6 pairs (10 years):**
- CSV: ~300GB
- Database: ~100GB
- **Total: ~400GB**

---

### Q7: What's the difference between M1 and D1 import?

**A:**

| Aspect | M1 | D1 |
|--------|----|----|
| File count | 52 per year | 1 per year |
| Records per file | 10,080 (1 week) | 252 (1 year) |
| Import time | Longer | Very fast |
| Use case | Intraday analysis | Daily analysis |

---

### Q8: How often should I run comprehensive mode?

**A:** Recommended schedule:
- **Daily:** Fast mode
- **Weekly:** Fast mode
- **Monthly:** Comprehensive mode (verification)
- **After DB maintenance:** Comprehensive mode

---

### Q9: Can I customize the tolerance for OHLC comparison?

**A:** Yes, edit `scripts/fxcm_importer.py`:
```python
# Line ~30
self.tolerance = 0.00001  # Change this value
```

Lower value = stricter comparison  
Higher value = more lenient comparison

---

### Q10: How do I check what's already in the database?

**A:** Use ClickHouse client:
```sql
-- Count records by symbol
SELECT symbol, count() AS records
FROM forex_data.ohlcv_m1
GROUP BY symbol;

-- Check date range
SELECT symbol,
       min(timestamp) AS first_record,
       max(timestamp) AS last_record
FROM forex_data.ohlcv_m1
GROUP BY symbol;
```

---

**For more questions, check:**
- [Requirements](../requirement/fxcm_importer_requirements.md)
- [Design](../design/fxcm_importer_design.md)
- [README](../../README_FXCM_IMPORTER.md)

---

**FXCM Data Importer v2.0** - Complete User Manual
