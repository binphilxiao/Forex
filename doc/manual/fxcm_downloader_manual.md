# FXCM Data Downloader User Manual

**Project**: FXCM Historical Data Downloader v2.0  
**Author**: binphilxiao  
**Date**: 2025-10-05  
**Version**: 2.0.0

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation](#2-installation)
3. [Quick Start](#3-quick-start)
4. [Command-Line Options](#4-command-line-options)
5. [Usage Examples](#5-usage-examples)
6. [Understanding the Output](#6-understanding-the-output)
7. [Directory Structure](#7-directory-structure)
8. [Log Files](#8-log-files)
9. [Troubleshooting](#9-troubleshooting)
10. [FAQ](#10-faq)
11. [Best Practices](#11-best-practices)

---

## 1. Introduction

### 1.1 What is FXCM Data Downloader?

The FXCM Data Downloader is a Python script that downloads historical forex data from FXCM's public API. It supports:

- **6 Major Currency Pairs**: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF
- **2 Timeframes**: M1 (1-minute candles), D1 (daily candles)
- **10+ Years of Data**: From 2015 to present
- **Automatic Resume**: Skips already downloaded files
- **Comprehensive Logging**: Detailed logs for every operation

### 1.2 Who Should Use This?

- Forex traders building backtesting systems
- Quantitative analysts studying forex markets
- Researchers analyzing currency movements
- Developers creating trading algorithms

### 1.3 System Requirements

- **Operating System**: Windows, Linux, or macOS
- **Python**: Version 3.7 or higher
- **Dependencies**: pandas, requests
- **Disk Space**: Approximately 50-100 GB for full dataset
- **Internet**: Stable connection required

---

## 2. Installation

### 2.1 Install Python

If you don't have Python installed:

**Windows**:
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer, check "Add Python to PATH"
3. Verify: `python --version`

**Linux/macOS**:
```bash
# Usually pre-installed
python3 --version

# If not, install via package manager
# Ubuntu/Debian:
sudo apt install python3 python3-pip

# macOS (with Homebrew):
brew install python3
```

### 2.2 Install Dependencies

```bash
pip install pandas requests
```

### 2.3 Download the Script

The script is located at:
```
scripts/fxcm_data_downloader.py
```

---

## 3. Quick Start

### 3.1 Basic Usage (Windows)

**Option 1: Use Batch File (Easiest)**
```batch
# Double-click or run in Command Prompt
download_fxcm_data.bat
```

**Option 2: Command Line**
```batch
python scripts\fxcm_data_downloader.py
```

### 3.2 Basic Usage (Linux/macOS)

```bash
python3 scripts/fxcm_data_downloader.py
```

### 3.3 What Happens?

By default, the script will:
1. Download data for all 6 currency pairs
2. Download both M1 and D1 timeframes
3. Download data from 2015 to current year
4. Skip files that already exist
5. Save data to `fxcm_data/` directory
6. Save logs to `logs/` directory

### 3.4 Typical Output

```
============================================================
FXCM Historical Data Downloader v2.0
============================================================
Currency Pairs: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF
Timeframes: M1, D1
Date Range: 2015 - 2025
Output Directory: C:\...\fxcm_data
Max Retries: 5
============================================================

============================================================
Processing: EURUSD
============================================================

==================================================
Timeframe: M1
==================================================

📥 Downloading EURUSD 2015 M1 data...
  Week 01/52...
    ✅ 7180 records -> week_01.csv
  Week 02/52...
    ✅ 7200 records -> week_02.csv
  ...
```

---

## 4. Command-Line Options

### 4.1 Overview

```bash
python scripts/fxcm_data_downloader.py [OPTIONS]
```

### 4.2 Available Options

#### `--pairs`
Specify which currency pairs to download.

**Syntax**: `--pairs PAIR1 [PAIR2 ...]`

**Choices**: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF

**Default**: All pairs

**Examples**:
```bash
# Single pair
python scripts/fxcm_data_downloader.py --pairs EURUSD

# Multiple pairs
python scripts/fxcm_data_downloader.py --pairs EURUSD GBPUSD USDJPY
```

---

#### `--timeframes`
Specify which timeframes to download.

**Syntax**: `--timeframes TF1 [TF2 ...]`

**Choices**: M1, D1

**Default**: M1 D1 (both)

**Examples**:
```bash
# Only M1 data
python scripts/fxcm_data_downloader.py --timeframes M1

# Only D1 data
python scripts/fxcm_data_downloader.py --timeframes D1

# Both (same as default)
python scripts/fxcm_data_downloader.py --timeframes M1 D1
```

---

#### `--start-year`
Specify the starting year for downloads.

**Syntax**: `--start-year YEAR`

**Default**: 2015

**Examples**:
```bash
# Download from 2020 onwards
python scripts/fxcm_data_downloader.py --start-year 2020
```

---

#### `--end-year`
Specify the ending year for downloads.

**Syntax**: `--end-year YEAR`

**Default**: Current year

**Examples**:
```bash
# Download up to 2023
python scripts/fxcm_data_downloader.py --end-year 2023

# Download specific range
python scripts/fxcm_data_downloader.py --start-year 2018 --end-year 2023
```

---

#### `--max-retries`
Specify maximum retry attempts for failed downloads.

**Syntax**: `--max-retries N`

**Default**: 5

**Examples**:
```bash
# Reduce retries for faster failure
python scripts/fxcm_data_downloader.py --max-retries 2

# Increase retries for unstable connection
python scripts/fxcm_data_downloader.py --max-retries 10
```

---

#### `--help`
Display help message with all options.

**Syntax**: `--help` or `-h`

**Example**:
```bash
python scripts/fxcm_data_downloader.py --help
```

---

## 5. Usage Examples

### 5.1 Download All Data (Default)

Download everything available:

```bash
python scripts/fxcm_data_downloader.py
```

**What it downloads**:
- All 6 currency pairs
- Both M1 and D1 timeframes
- From 2015 to current year
- Approximately 50-100 GB

**Time required**: 2-4 hours (depending on connection)

---

### 5.2 Download Specific Currency Pair

Download only EURUSD data:

```bash
python scripts/fxcm_data_downloader.py --pairs EURUSD
```

**What it downloads**:
- EURUSD only
- Both M1 and D1 timeframes
- From 2015 to current year
- Approximately 8-15 GB

**Time required**: 20-40 minutes

---

### 5.3 Download Multiple Specific Pairs

Download EURUSD and GBPUSD:

```bash
python scripts/fxcm_data_downloader.py --pairs EURUSD GBPUSD
```

---

### 5.4 Download Only M1 Data

Download minute-level data only:

```bash
python scripts/fxcm_data_downloader.py --timeframes M1
```

**What it downloads**:
- All 6 pairs
- M1 timeframe only
- From 2015 to current year
- Approximately 45-90 GB

---

### 5.5 Download Only D1 Data

Download daily data only:

```bash
python scripts/fxcm_data_downloader.py --timeframes D1
```

**What it downloads**:
- All 6 pairs
- D1 timeframe only
- From 2015 to current year
- Approximately 5-10 GB

**Time required**: 5-10 minutes

---

### 5.6 Download Recent Data Only

Download only the last 3 years:

```bash
python scripts/fxcm_data_downloader.py --start-year 2022
```

**Tip**: This is much faster and uses less disk space.

---

### 5.7 Download Specific Date Range

Download data from 2018 to 2021:

```bash
python scripts/fxcm_data_downloader.py --start-year 2018 --end-year 2021
```

---

### 5.8 Complex Example

Download EURUSD and GBPUSD, M1 only, from 2020 to 2023:

```bash
python scripts/fxcm_data_downloader.py \
    --pairs EURUSD GBPUSD \
    --timeframes M1 \
    --start-year 2020 \
    --end-year 2023
```

---

### 5.9 Resume Interrupted Download

If download was interrupted, simply run the same command again:

```bash
python scripts/fxcm_data_downloader.py
```

**What happens**:
- Script checks existing files
- Skips already downloaded files
- Continues from where it left off
- No data is re-downloaded unnecessarily

---

## 6. Understanding the Output

### 6.1 Console Output Explanation

```
============================================================
Processing: EURUSD
============================================================
```
Current currency pair being processed.

```
==================================================
Timeframe: M1
==================================================
```
Current timeframe being processed.

```
📥 Downloading EURUSD 2015 M1 data...
```
Starting to download a specific year's data.

```
  Week 01/52...
    ✅ 7180 records -> week_01.csv
```
- ✅ Success: Downloaded and saved
- Number of records downloaded
- Filename created

```
  Week 02/52... ⏭️  Already exists, skipped
```
- ⏭️ Skipped: File already exists locally

```
  Week 03/52...
    ⏭️  No data available
```
- ⏭️ No data: FXCM doesn't have data for this period (404 error)

---

### 6.2 Final Summary

```
============================================================
Download Summary
============================================================
Total Files Processed: 3328
  ✅ Downloaded: 2800
  ⏭️  Skipped (existing): 400
  ❌ Failed/Not Available: 128
Total Records Downloaded: 25,000,000
Time Elapsed: 3600.5 seconds
============================================================
```

**Interpretation**:
- **Total Files**: All files attempted
- **Downloaded**: Successfully downloaded new files
- **Skipped**: Files that already existed
- **Failed**: Files not available (404) or errors
- **Total Records**: Number of OHLC candles downloaded
- **Time Elapsed**: Duration in seconds

---

## 7. Directory Structure

### 7.1 Output Directory Layout

```
fxcm_data/
├── EURUSD/
│   ├── M1/
│   │   ├── 2015/
│   │   │   ├── week_01.csv
│   │   │   ├── week_02.csv
│   │   │   └── ...
│   │   │   └── week_52.csv
│   │   ├── 2016/
│   │   └── ...
│   └── D1/
│       ├── 2015.csv
│       ├── 2016.csv
│       └── ...
├── GBPUSD/
│   ├── M1/
│   └── D1/
├── USDJPY/
├── AUDUSD/
├── USDCAD/
└── USDCHF/
```

### 7.2 File Naming Conventions

**M1 Files**: `week_NN.csv` where NN is 01-52
- Example: `week_01.csv`, `week_15.csv`

**D1 Files**: `YYYY.csv` where YYYY is the year
- Example: `2015.csv`, `2020.csv`

### 7.3 CSV File Format

All CSV files have the same format:

```csv
DateTime,Open,High,Low,Close
2020-01-01 00:00:00,1.1234,1.1240,1.1230,1.1238
2020-01-01 00:01:00,1.1238,1.1245,1.1235,1.1242
...
```

**Columns**:
- **DateTime**: Timestamp in ISO 8601 format
- **Open**: Opening price
- **High**: Highest price in period
- **Low**: Lowest price in period
- **Close**: Closing price

**Note**: Volume column is not included (FXCM data doesn't provide it).

---

## 8. Log Files

### 8.1 Log Directory

All logs are saved to: `logs/`

### 8.2 Log File Types

#### Download Log
**Filename**: `fxcm_download_YYYYMMDD_HHMMSS.log`

**Contents**:
- Detailed download activity
- Success/failure for each file
- Error messages
- Retry attempts
- Timestamps for all operations

**Example**:
```
2025-10-05 12:00:00 - INFO - Log file: logs/fxcm_download_20251005_120000.log
2025-10-05 12:00:01 - INFO - ============================================================
2025-10-05 12:00:01 - INFO - FXCM Historical Data Downloader v2.0
...
2025-10-05 12:00:05 - DEBUG - ✅ Downloaded: https://...EURUSD/2020/1.csv.gz (7180 records)
...
```

---

#### Summary Report
**Filename**: `fxcm_download_summary_YYYYMMDD_HHMMSS.txt`

**Contents**:
- Configuration used
- Final statistics
- Completion time

**Example**:
```
============================================================
FXCM Data Download Summary Report
============================================================

Configuration:
  Currency Pairs: EURUSD, GBPUSD
  Timeframes: M1, D1
  Date Range: 2015 - 2025
  Output Directory: C:\...\fxcm_data
  Max Retries: 5

Results:
  Total Files Processed: 1000
  Downloaded: 850
  Skipped (existing): 100
  Failed/Not Available: 50
  Total Records: 5,000,000
  Time Elapsed: 3600.5 seconds

Completion Time: 2025-10-05 13:00:00
============================================================
```

---

## 9. Troubleshooting

### 9.1 Script Won't Run

**Problem**: `python: command not found`

**Solution**:
- Ensure Python is installed
- Check PATH environment variable
- Try `python3` instead of `python` (Linux/macOS)

---

**Problem**: `ModuleNotFoundError: No module named 'pandas'`

**Solution**:
```bash
pip install pandas requests
```

---

### 9.2 Network Errors

**Problem**: `Connection timeout` or `Network unreachable`

**Solutions**:
- Check internet connection
- Try again later
- Increase retry count: `--max-retries 10`
- Check firewall settings

---

### 9.3 Many 404 Errors

**Problem**: Many files showing "No data available"

**Explanation**: This is **normal**. FXCM doesn't have data for all weeks/years.

**Common gaps**:
- Week 1 and Week 53 often missing (year boundaries)
- Some historical periods may not have data
- Market holidays

**Solution**: No action needed. These are expected gaps.

---

### 9.4 Disk Full Error

**Problem**: `OSError: [Errno 28] No space left on device`

**Solutions**:
- Free up disk space
- Download specific pairs only: `--pairs EURUSD`
- Download specific timeframe: `--timeframes D1`
- Download specific date range: `--start-year 2020`

---

### 9.5 Slow Download Speed

**Problem**: Download is very slow

**Solutions**:
- Check internet connection speed
- Close other bandwidth-intensive applications
- Try downloading during off-peak hours
- Download fewer pairs/timeframes at once

---

### 9.6 Corrupted CSV Files

**Problem**: CSV file won't open or has errors

**Solutions**:
1. Delete the problematic file
2. Run script again (it will re-download)
3. Check log file for errors during download

---

## 10. FAQ

### Q1: How much disk space do I need?

**A**: Depends on what you download:
- **Full dataset** (all pairs, M1+D1, 2015-now): ~50-100 GB
- **Single pair** (M1+D1, 2015-now): ~8-15 GB
- **All pairs, D1 only** (2015-now): ~5-10 GB
- **Recent 3 years** (all pairs, M1+D1): ~15-30 GB

---

### Q2: How long does it take to download?

**A**: Varies by dataset size and connection:
- **Full dataset**: 2-4 hours
- **Single pair**: 20-40 minutes
- **D1 only (all pairs)**: 5-10 minutes
- **Recent 3 years**: 30-60 minutes

---

### Q3: Can I interrupt and resume?

**A**: Yes! The script automatically skips existing files. If interrupted:
1. Press Ctrl+C to stop
2. Run the same command again
3. It will continue from where it left off

---

### Q4: Why are some weeks missing?

**A**: FXCM doesn't have data for all periods. Common gaps:
- Week 1 (year start)
- Week 53 (year end)
- Market holidays
- Historical data limitations

This is normal and expected.

---

### Q5: Can I download data for other currency pairs?

**A**: Only the 6 supported pairs are available:
- EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF

These are the pairs provided by FXCM's public API.

---

### Q6: Can I get hourly (H1) data?

**A**: Not directly from this script. But you can:
1. Download M1 data
2. Use `scripts/convert_m1_to_multi_timeframes.py` to generate H1 from M1

---

### Q7: Is the data free?

**A**: Yes! FXCM provides this historical data for free via their public API.

---

### Q8: Can I use this for commercial purposes?

**A**: Check FXCM's terms of service for data usage. This script is MIT licensed, but the data has its own terms.

---

### Q9: What if I get HTTP 500 errors?

**A**: Server errors. The script will retry automatically. If persistent:
- Try again later
- FXCM's servers may be temporarily down

---

### Q10: Can I download multiple datasets in parallel?

**A**: Not recommended. Run one instance at a time to:
- Avoid overloading FXCM's servers
- Prevent file conflicts
- Ensure accurate logging

---

## 11. Best Practices

### 11.1 Start Small

When first using the script:
1. Test with one pair: `--pairs EURUSD`
2. Test with D1 only: `--timeframes D1`
3. Test with recent data: `--start-year 2023`
4. Once comfortable, download larger datasets

---

### 11.2 Use Batch File (Windows)

For convenience:
```batch
download_fxcm_data.bat
```

This handles:
- Virtual environment activation
- UTF-8 encoding
- Proper path handling

---

### 11.3 Monitor Logs

Check log files to:
- Verify downloads completed successfully
- Identify patterns in failed files
- Troubleshoot issues

---

### 11.4 Backup Data

After downloading:
- Backup the `fxcm_data/` directory
- Consider compressing for storage
- Keep logs for reference

---

### 11.5 Regular Updates

To keep data current:
```bash
# Run monthly or weekly
python scripts/fxcm_data_downloader.py --start-year 2025
```

Script automatically skips existing files.

---

### 11.6 Organize by Use Case

Create separate download configurations:

**For backtesting all strategies**:
```bash
# Download everything
python scripts/fxcm_data_downloader.py
```

**For specific strategy development**:
```bash
# Only EURUSD, recent data
python scripts/fxcm_data_downloader.py --pairs EURUSD --start-year 2020
```

**For quick analysis**:
```bash
# D1 only
python scripts/fxcm_data_downloader.py --timeframes D1
```

---

### 11.7 Error Recovery

If many errors occur:
1. Check internet connection
2. Review log file
3. Try downloading smaller chunks
4. Contact FXCM if API issues persist

---

### 11.8 Performance Optimization

For faster downloads:
- Use wired connection (vs WiFi)
- Download during off-peak hours
- Close other applications
- Download D1 first (smaller, faster)

---

## 12. Getting Help

### 12.1 Check Documentation

1. This manual
2. Requirements document
3. Design document
4. README file

### 12.2 Review Logs

Log files contain detailed error information.

### 12.3 Common Issues

Most issues are covered in [Troubleshooting](#9-troubleshooting) and [FAQ](#10-faq).

### 12.4 Contact

For issues not covered in documentation:
- Check GitHub repository
- Review FXCM API documentation
- Contact project maintainer

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-05  
**Status**: Final
