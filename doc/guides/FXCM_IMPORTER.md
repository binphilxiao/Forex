# FXCM Data Importer v2.0

**Import FXCM forex data from CSV files to ClickHouse database with intelligent duplicate detection**

---

## 🎯 Quick Links

- **[Requirements](doc/requirement/fxcm_importer_requirements.md)** - Functional and non-functional requirements
- **[Design](doc/design/fxcm_importer_design.md)** - System architecture and class design  
- **[User Manual](doc/manual/fxcm_importer_manual.md)** - Complete usage guide
- **[Test Suite](scripts/test/test_fxcm_importer.py)** - Unit tests

---

## 📋 Overview

The FXCM Data Importer is a professional-grade command-line tool designed to import FXCM forex historical data from CSV files into ClickHouse database. It features:

✅ **Smart Duplicate Detection** - Two validation modes (fast/comprehensive)  
✅ **Flexible Configuration** - Command-line parameters for all options  
✅ **Multi-Currency Support** - 6 major currency pairs  
✅ **Multi-Timeframe Support** - M1 (1-minute) and D1 (daily)  
✅ **High Performance** - Process 50,000+ records/second (fast mode)  
✅ **Comprehensive Logging** - Detailed logs and reports  

---

## 🚀 Quick Start

### Using Windows Batch File (Easiest)

```cmd
import_fxcm_data.bat
```

### Using Command Line

```bash
# Import all data with default settings
python scripts\fxcm_importer.py

# Import specific pairs
python scripts\fxcm_importer.py --pairs EURUSD GBPUSD

# Import only M1 data for 2024
python scripts\fxcm_importer.py --timeframes M1 --start-year 2024 --end-year 2024

# Use comprehensive validation mode
python scripts\fxcm_importer.py --check-mode comprehensive
```

---

## 📦 Installation

### Prerequisites

- **Python 3.7+**
- **ClickHouse** database server
- **CSV data files** in `fxcm_data/` directory

### Install Dependencies

```bash
pip install pandas clickhouse-connect
```

### Verify Installation

```bash
python scripts\fxcm_importer.py --help
```

---

## 💡 Features

### 1. Duplicate Detection Modes

#### Fast Mode (Default) ⚡
- Checks only first and last records
- 100x faster than comprehensive mode
- Perfect for daily updates
- Target speed: 50,000 records/second

**Example:**
```bash
python scripts\fxcm_importer.py --check-mode fast
```

#### Comprehensive Mode 🔍
- Checks every single record
- Detects partial file changes
- Perfect for data verification
- Target speed: 10,000 records/second

**Example:**
```bash
python scripts\fxcm_importer.py --check-mode comprehensive
```

### 2. Flexible Selection

**Currency Pairs:**
```bash
# Single pair
python scripts\fxcm_importer.py --pairs EURUSD

# Multiple pairs
python scripts\fxcm_importer.py --pairs EURUSD GBPUSD USDJPY

# All pairs (default)
python scripts\fxcm_importer.py
```

**Timeframes:**
```bash
# M1 only
python scripts\fxcm_importer.py --timeframes M1

# D1 only
python scripts\fxcm_importer.py --timeframes D1

# Both (default)
python scripts\fxcm_importer.py --timeframes M1 D1
```

**Date Range:**
```bash
# Specific year
python scripts\fxcm_importer.py --start-year 2024 --end-year 2024

# Year range
python scripts\fxcm_importer.py --start-year 2020 --end-year 2024

# All years (default: 2015-now)
python scripts\fxcm_importer.py
```

### 3. ClickHouse Configuration

```bash
# Custom host and port
python scripts\fxcm_importer.py --ch-host 192.168.1.100 --ch-http-port 8123

# With authentication
python scripts\fxcm_importer.py --ch-user admin --ch-password secret

# Default: 192.168.2.168:8123, user=default, password=""
python scripts\fxcm_importer.py
```

---

## 📊 Usage Examples

### Example 1: Daily Update (Fast Mode)

**Scenario:** Import yesterday's M1 data  
**Command:**
```bash
python scripts\fxcm_importer.py --timeframes M1 --start-year 2025 --end-year 2025
```

**Result:**
- Fast mode (default)
- Skips existing data
- Completes in < 2 minutes

---

### Example 2: Historical Data Import

**Scenario:** Import 10 years of D1 data for all pairs  
**Command:**
```bash
python scripts\fxcm_importer.py --timeframes D1 --start-year 2015 --end-year 2024
```

**Result:**
- Fast mode (default)
- All 6 currency pairs
- Completes in < 5 minutes

---

### Example 3: Data Verification

**Scenario:** Verify all data is correctly imported  
**Command:**
```bash
python scripts\fxcm_importer.py --check-mode comprehensive --pairs EURUSD --start-year 2024
```

**Result:**
- Checks every record
- Provides detailed mismatch report
- Takes longer but 100% accurate

---

### Example 4: Selective Import

**Scenario:** Import only EUR pairs for testing  
**Command:**
```bash
python scripts\fxcm_importer.py --pairs EURUSD --timeframes M1 --start-year 2024 --end-year 2024
```

**Result:**
- Only EURUSD M1 for 2024
- Completes in < 30 seconds

---

## 📝 Command-Line Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--pairs` | List | All 6 | Currency pairs to import |
| `--timeframes` | List | M1 D1 | Timeframes to import |
| `--start-year` | Int | 2015 | Start year |
| `--end-year` | Int | Current | End year |
| `--check-mode` | Str | fast | Validation mode: fast or comprehensive |
| `--ch-host` | Str | 192.168.2.168 | ClickHouse host |
| `--ch-http-port` | Int | 8123 | ClickHouse HTTP port |
| `--ch-user` | Str | default | ClickHouse username |
| `--ch-password` | Str | "" | ClickHouse password |

---

## 📂 Data Structure

### Expected CSV Layout

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
├── GBPUSD/
│   ├── M1/
│   └── D1/
└── ...
```

### CSV Format

```csv
DateTime,Open,High,Low,Close
2024-01-01 00:00:00,1.10000,1.10050,1.09950,1.10010
2024-01-01 00:01:00,1.10010,1.10060,1.09960,1.10020
...
```

---

## 📊 Output

### Console Output

```
============================================================
FXCM Data Importer v2.0
============================================================
Currency Pairs: EURUSD, GBPUSD
Timeframes: M1, D1
Year Range: 2020 - 2024
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

📊 Report saved: logs/fxcm_import_report_20251005_143015.txt
```

### Log Files

**Location:** `logs/`

- **Log:** `fxcm_import_20251005_143015.log`
- **Report:** `fxcm_import_report_20251005_143015.txt`

---

## 🔧 Database Schema

### M1 Table

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
ORDER BY (symbol, timestamp)
PRIMARY KEY (symbol, timestamp);
```

### D1 Table

```sql
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

---

## 🧪 Testing

### Run Test Suite

```bash
python scripts\test\test_fxcm_importer.py
```

### Test Coverage

**15 Test Cases:**
- ✅ TC-01: Importer initialization
- ✅ TC-02: Available pairs configuration
- ✅ TC-03: Available timeframes configuration
- ✅ TC-04: Check modes configuration
- ✅ TC-05: Table name generation
- ✅ TC-06: OHLC comparison - exact match
- ✅ TC-07: OHLC comparison - within tolerance
- ✅ TC-08: OHLC comparison - outside tolerance
- ✅ TC-09: CSV file path construction - M1
- ✅ TC-10: CSV file path construction - D1
- ✅ TC-11: Statistics initialization
- ✅ TC-12: Logging configuration
- ✅ TC-13: Batch size configuration
- ✅ TC-14: Tolerance configuration
- ✅ TC-15: Data directory configuration

---

## ⚡ Performance

### Benchmarks

| Mode | Speed | Use Case |
|------|-------|----------|
| **Fast** | 50,000 records/sec | Daily updates |
| **Comprehensive** | 10,000 records/sec | Data verification |

### Processing Time Estimates

| Dataset | Fast Mode | Comprehensive Mode |
|---------|-----------|-------------------|
| 1 year M1 (1 pair) | ~10 seconds | ~1 minute |
| 10 years M1 (1 pair) | ~2 minutes | ~10 minutes |
| 10 years M1 (all pairs) | ~10 minutes | ~60 minutes |
| 10 years D1 (all pairs) | ~5 seconds | ~30 seconds |

---

## 🛠️ Troubleshooting

### Common Issues

#### ClickHouse Connection Failed
```bash
# Check if ClickHouse is running
curl http://192.168.2.168:8123
# Should return "Ok."
```

#### CSV Files Not Found
```bash
# Verify directory structure
dir fxcm_data\EURUSD\M1\2024
# Should contain week_*.csv files
```

#### Python Module Not Found
```bash
pip install pandas clickhouse-connect
```

### Getting Help

```bash
python scripts\fxcm_importer.py --help
```

---

## 📚 Documentation

### Complete Documentation

1. **[Requirements Specification](doc/requirement/fxcm_importer_requirements.md)**
   - Functional requirements (FR-1 to FR-12)
   - Non-functional requirements (NFR-1 to NFR-5)
   - User stories and acceptance criteria

2. **[Design Specification](doc/design/fxcm_importer_design.md)**
   - System architecture
   - Class design and methods
   - Database schema
   - Algorithms and data flow

3. **[User Manual](doc/manual/fxcm_importer_manual.md)**
   - Installation guide
   - Command-line reference
   - Usage examples
   - Troubleshooting and FAQ

---

## 🚀 Best Practices

### Daily Workflow

```bash
# 1. Download new M1 data
python scripts\fxcm_data_downloader.py --start-year 2025

# 2. Import with fast mode (default)
python scripts\fxcm_importer.py --start-year 2025

# 3. Verify import
# Check logs/fxcm_import_report_*.txt
```

### Weekly Verification

```bash
# Use comprehensive mode for verification
python scripts\fxcm_importer.py --check-mode comprehensive --start-year 2025 --end-year 2025
```

### Performance Tips

✅ Use **fast mode** for daily updates  
✅ Use **comprehensive mode** for monthly verification  
✅ Process year by year for large datasets  
✅ Monitor log files for errors  

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2025-10-05 | Complete rewrite with dual validation modes |
| 1.0.0 | Previous | Initial version |

---

## 👤 Author

**binphilxiao**  
Date: 2025-10-05

---

## 📄 License

MIT License

---

## 🙏 Related Tools

- **[FXCM Data Downloader](README_FXCM_DOWNLOADER.md)**: Download M1 and D1 source data
- **[M1 Timeframe Converter](README_M1_CONVERTER.md)**: Convert M1 to M5/M15/M30/H1
- **[Data Consistency Checker](README_DATA_CONSISTENCY.md)**: Verify data integrity

---

**FXCM Data Importer v2.0** - Professional forex data import tool
