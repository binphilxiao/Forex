# M1 Timeframe Converter - User Manual

**Version:** 2.0.0  
**Author:** binphilxiao  
**Date:** 2025-10-05

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation](#2-installation)
3. [Quick Start](#3-quick-start)
4. [Command-Line Reference](#4-command-line-reference)
5. [Usage Examples](#5-usage-examples)
6. [Understanding Output](#6-understanding-output)
7. [Troubleshooting](#7-troubleshooting)
8. [FAQ](#8-faq)
9. [Best Practices](#9-best-practices)

---

## 1. Introduction

### 1.1 What is M1 Timeframe Converter?

The M1 Timeframe Converter is a powerful Python tool that converts 1-minute (M1) forex market data into higher timeframes:
- **M5**: 5-minute bars
- **M15**: 15-minute bars
- **M30**: 30-minute bars
- **H1**: 1-hour bars

### 1.2 Key Features

✅ **Multi-Timeframe Support**: Generate M5, M15, M30, and H1 from M1 data  
✅ **6 Currency Pairs**: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF  
✅ **ClickHouse Integration**: Fast database storage and retrieval  
✅ **Flexible CLI**: Command-line parameters for selective conversion  
✅ **Smart Processing**: Skip or overwrite existing data  
✅ **Detailed Reporting**: Comprehensive logs and statistics  
✅ **Windows Launcher**: Easy-to-use batch file  

### 1.3 Who Should Use This Tool?

- **Forex Traders**: Need multi-timeframe analysis for trading decisions
- **Quantitative Analysts**: Building and backtesting trading strategies
- **Data Engineers**: Managing forex data pipelines
- **Researchers**: Analyzing forex market behavior across timeframes

---

## 2. Installation

### 2.1 Prerequisites

**Required:**
- Python 3.7 or higher
- ClickHouse database server
- M1 forex data loaded in ClickHouse

**Check Python Version:**
```bash
python --version
# Should show Python 3.7.x or higher
```

### 2.2 Install Dependencies

```bash
pip install pandas clickhouse-connect
```

**Verify Installation:**
```bash
pip list | grep pandas
pip list | grep clickhouse-connect
```

### 2.3 Download the Tool

The tool is located in your forex project:
```
Forex/
├── scripts/
│   └── m1_timeframe_converter.py     # Main script
├── convert_m1_to_multi_timeframes.bat  # Windows launcher
└── logs/                               # Output directory
```

---

## 3. Quick Start

### 3.1 Using Windows Batch File (Easiest)

**Step 1:** Double-click `convert_m1_to_multi_timeframes.bat`

**Step 2:** The tool runs with default settings:
- All 6 currency pairs
- All 4 timeframes (M5, M15, M30, H1)
- All years (2015 to current year)
- Overwrite mode (replace existing data)

**Step 3:** Check the output in console and `logs/` folder

### 3.2 Using Command Line (Recommended)

**Open Terminal (Windows PowerShell/CMD):**

```bash
# Navigate to project directory
cd C:\Users\abing\OneDrive\Desktop\Forex

# Run with default settings
python scripts\m1_timeframe_converter.py

# Run with specific parameters
python scripts\m1_timeframe_converter.py --pairs EURUSD --timeframes M5 M15
```

### 3.3 First Run Checklist

Before your first run, verify:

☑ ClickHouse server is running  
☑ ClickHouse is accessible at 192.168.2.168:8123  
☑ M1 data exists in ClickHouse (e.g., `forex_eurusd_m1`)  
☑ You have write permissions to ClickHouse  
☑ Sufficient disk space for output data  

---

## 4. Command-Line Reference

### 4.1 Basic Syntax

```bash
python scripts\m1_timeframe_converter.py [OPTIONS]
```

### 4.2 Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--mode` | String | local | Conversion mode: 'local' or 'database' |
| `--pairs` | List | All 6 pairs | Currency pairs to convert |
| `--timeframes` | List | All 4 TFs | Timeframes to generate |
| `--start-year` | Integer | 2015 | Start year |
| `--end-year` | Integer | Current year | End year |
| `--skip-existing` | Flag | False | Skip existing data |
| `--ch-host` | String | 192.168.2.168 | ClickHouse host |
| `--ch-port` | Integer | 8123 | ClickHouse HTTP port |
| `--ch-user` | String | default | ClickHouse username |
| `--ch-password` | String | (empty) | ClickHouse password |

### 4.3 Available Currency Pairs

- `EURUSD` - Euro / US Dollar
- `GBPUSD` - British Pound / US Dollar
- `USDJPY` - US Dollar / Japanese Yen
- `AUDUSD` - Australian Dollar / US Dollar
- `USDCAD` - US Dollar / Canadian Dollar
- `USDCHF` - US Dollar / Swiss Franc

### 4.4 Available Timeframes

- `M5` - 5 minutes (5 M1 bars → 1 M5 bar)
- `M15` - 15 minutes (15 M1 bars → 1 M15 bar)
- `M30` - 30 minutes (30 M1 bars → 1 M30 bar)
- `H1` - 1 hour (60 M1 bars → 1 H1 bar)

### 4.5 Getting Help

```bash
python scripts\m1_timeframe_converter.py --help
```

---

## 5. Usage Examples

### 5.1 Example 1: Convert All Data (Default)

**Command:**
```bash
python scripts\m1_timeframe_converter.py
```

**What it does:**
- Converts all 6 currency pairs
- Generates all 4 timeframes (M5, M15, M30, H1)
- Processes all years (2015 to current year)
- Overwrites existing data

**Expected Output:**
```
============================================================
M1 to Multi-Timeframe Converter v2.0
============================================================
Currency Pairs: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF
Timeframes: M5, M15, M30, H1
Year Range: 2015 - 2025
...
✅ Conversion completed!
```

### 5.2 Example 2: Convert Single Pair

**Command:**
```bash
python scripts\m1_timeframe_converter.py --pairs EURUSD
```

**What it does:**
- Converts only EURUSD
- Generates all 4 timeframes
- Processes all years

**Use Case:** Quick update for a specific pair you're trading

### 5.3 Example 3: Convert Multiple Pairs

**Command:**
```bash
python scripts\m1_timeframe_converter.py --pairs EURUSD GBPUSD USDJPY
```

**What it does:**
- Converts 3 major pairs
- Generates all 4 timeframes
- Processes all years

**Use Case:** Focus on major currency pairs only

### 5.4 Example 4: Generate Specific Timeframes

**Command:**
```bash
python scripts\m1_timeframe_converter.py --timeframes M5 H1
```

**What it does:**
- Converts all 6 pairs
- Generates only M5 and H1 (skips M15, M30)
- Processes all years

**Use Case:** You only need M5 for scalping and H1 for trend analysis

### 5.5 Example 5: Convert Specific Year Range

**Command:**
```bash
python scripts\m1_timeframe_converter.py --start-year 2020 --end-year 2023
```

**What it does:**
- Converts all 6 pairs
- Generates all 4 timeframes
- Processes only years 2020-2023

**Use Case:** Recent market data analysis

### 5.6 Example 6: Convert Single Year

**Command:**
```bash
python scripts\m1_timeframe_converter.py --start-year 2024 --end-year 2024
```

**What it does:**
- Converts all 6 pairs
- Generates all 4 timeframes
- Processes only year 2024

**Use Case:** Update current year data after downloading new M1 data

### 5.7 Example 7: Skip Existing Data

**Command:**
```bash
python scripts\m1_timeframe_converter.py --skip-existing
```

**What it does:**
- Converts all 6 pairs
- Generates all 4 timeframes
- **Skips years that already have data** (doesn't overwrite)

**Use Case:** Incremental updates without re-processing everything

**Output Example:**
```
⏭️ Skipping EURUSD 2020 M5 - 105,120 records already exist
```

### 5.8 Example 8: Custom ClickHouse Server

**Command:**
```bash
python scripts\m1_timeframe_converter.py --ch-host 192.168.1.100 --ch-port 8123
```

**What it does:**
- Connects to ClickHouse at custom IP address
- Uses custom port

**Use Case:** Multiple ClickHouse servers or different environments

### 5.9 Example 9: Local Mode (CSV-based, Default)

**Command:**
```bash
python scripts\m1_timeframe_converter.py --mode local
```

**What it does:**
- Reads M1 data from CSV files in `fxcm_data/`
- Uses pandas for aggregation calculation
- Saves results to CSV files in `fxcm_data/`
- **Does NOT require ClickHouse connection**

**Use Case:** Local development, offline analysis, data backup

**Data Flow:**
```
fxcm_data/EURUSD/M1/2024/week_*.csv
  ↓ pandas read
  ↓ pandas resample aggregation
  ↓ pandas write
fxcm_data/EURUSD/M5/2024/2024.csv
```

### 5.10 Example 10: Database Mode (ClickHouse SQL)

**Command:**
```bash
python scripts\m1_timeframe_converter.py --mode database
```

**What it does:**
- Uses ClickHouse SQL for aggregation (**data never leaves database**)
- Ultra-fast processing (~10x faster than local mode)
- Requires ClickHouse connection

**Use Case:** Production environment, large-scale data, high-performance processing

**SQL Flow:**
```sql
INSERT INTO forex_eurusd_m5
SELECT 
    toStartOfInterval(DateTime, INTERVAL 5 MINUTE) as DateTime,
    argMin(Open, DateTime) as Open,
    max(High) as High,
    min(Low) as Low,
    argMax(Close, DateTime) as Close
FROM forex_eurusd_m1
WHERE toYear(DateTime) = 2024
GROUP BY DateTime
ORDER BY DateTime
```

### 5.11 Example 11: Combined Parameters with Mode

**Command:**
```bash
python scripts\m1_timeframe_converter.py ^
    --mode local ^
    --pairs EURUSD GBPUSD ^
    --timeframes M5 M15 ^
    --start-year 2022 ^
    --end-year 2024
```

**What it does:**
- **Local mode**: CSV → pandas → CSV
- Converts EURUSD and GBPUSD only
- Generates M5 and M15 only
- Processes years 2022-2024
- Default behavior: skip existing

**Use Case:** Targeted local update without database dependency

### 5.12 Example 12: Combined Database Mode

**Command:**  
```bash
python scripts\m1_timeframe_converter.py ^
    --mode database ^
    --pairs EURUSD ^
    --timeframes M5 ^
    --start-year 2024 ^
    --overwrite
```

**What it does:**
- **Database mode**: ClickHouse SQL aggregation
- EURUSD only
- M5 only  
- 2024 only
- Overwrite existing data

**Use Case:** High-speed production refresh

---

## 6. Understanding Output

### 6.1 Console Output - Local Mode

**Header:**
```
============================================================
M1 to Multi-Timeframe Converter v2.0
============================================================
Currency Pairs: EURUSD, GBPUSD
Timeframes: M5, M15
Year Range: 2020 - 2024
Conversion Mode: Local (CSV → pandas → CSV)
Data Directory: C:\Users\...\Forex\fxcm_data
============================================================
```

**Progress:**
```
Processing: EURUSD
  📅 Year: 2024
  🕑 Timeframe: M5
    📁 Read 525,600 M1 records from CSV for EURUSD 2024
    ✅ Wrote 105,120 records to fxcm_data\EURUSD\M5\2024\2024.csv
```

### 6.2 Console Output - Database Mode

**Header:**
```
============================================================
M1 to Multi-Timeframe Converter v2.0
============================================================
Currency Pairs: EURUSD, GBPUSD
Timeframes: M5, M15
Year Range: 2020 - 2024
Conversion Mode: Database (ClickHouse SQL)
ClickHouse: 192.168.2.168:8123
============================================================
```

**Progress:**
```
Processing: EURUSD
  📅 Year: 2024
  🕑 Timeframe: M5
    ✅ Generated 105,120 M5 records in ClickHouse for EURUSD 2024 (SQL aggregation)
```

### 5.9 Example 9: Combined Parameters

**Command:**
```bash
python scripts\m1_timeframe_converter.py ^
    --pairs EURUSD GBPUSD ^
    --timeframes M5 M15 ^
    --start-year 2022 ^
    --end-year 2024 ^
    --skip-existing
```

**What it does:**
- Converts EURUSD and GBPUSD only
- Generates M5 and M15 only
- Processes years 2022-2024
- Skips existing data

**Use Case:** Targeted, efficient update

---

## 6. Understanding Output

### 6.1 Console Output

**Header:**
```
============================================================
M1 to Multi-Timeframe Converter v2.0
============================================================
Currency Pairs: EURUSD, GBPUSD
Timeframes: M5, M15
Year Range: 2020 - 2024
ClickHouse: 192.168.2.168:8123
Overwrite Mode: Yes
============================================================
```

**Progress:**
```
============================================================
Processing: EURUSD
============================================================

📅 Year: 2024

⏱️  Timeframe: M5
  📥 Read 525,600 M1 records for EURUSD 2024
  ✅ Wrote 105,120 records to forex_eurusd_m5

⏱️  Timeframe: M15
  📥 Read 525,600 M1 records for EURUSD 2024
  ✅ Wrote 35,040 records to forex_eurusd_m15
```

**Summary:**
```
============================================================
Conversion Summary
============================================================
Pairs Processed: 2
Timeframes Generated: 8
Records Read (M1): 4,204,800
Records Written: 840,960
Skipped (existing): 0
Errors: 0
Processing Time: 127.3 seconds
============================================================
✅ Conversion completed!
```

### 6.2 Log Files

**Location:** `logs/m1_converter_YYYYMMDD_HHMMSS.log`

**Example:** `logs/m1_converter_20251005_143015.log`

**Content:**
```
2025-10-05 14:30:15 - INFO - Log file: logs/m1_converter_20251005_143015.log
2025-10-05 14:30:15 - INFO - ✅ Connected to ClickHouse at 192.168.2.168:8123
2025-10-05 14:30:16 - INFO - Processing: EURUSD
2025-10-05 14:30:17 - INFO -   📥 Read 525,600 M1 records for EURUSD 2024
2025-10-05 14:30:18 - INFO -   ✅ Wrote 105,120 records to forex_eurusd_m5
```

### 6.3 Report Files

**Location:** `logs/m1_converter_report_YYYYMMDD_HHMMSS.txt`

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

### 6.4 Understanding Statistics

| Statistic | Description | Example |
|-----------|-------------|---------|
| **Pairs Processed** | Number of currency pairs completed | 6 |
| **Timeframes Generated** | Number of timeframe datasets created | 24 (6 pairs × 4 TFs) |
| **Records Read (M1)** | Total M1 bars read from ClickHouse | 23,357,603 |
| **Records Written** | Total aggregated bars written | 4,671,521 |
| **Skipped** | Items skipped (skip mode only) | 0 |
| **Errors** | Number of errors encountered | 0 |
| **Processing Time** | Total duration in seconds | 4515.2 (1.25 hours) |

---

## 7. Troubleshooting

### 7.1 Common Issues

#### Issue 1: ClickHouse Connection Failed

**Error:**
```
❌ Failed to connect to ClickHouse: Connection refused
```

**Solution:**
1. Verify ClickHouse server is running
2. Check host IP: `ping 192.168.2.168`
3. Verify port: Default is 8123 for HTTP
4. Check firewall settings
5. Verify credentials (username/password)

**Test Connection:**
```bash
curl http://192.168.2.168:8123
# Should return "Ok."
```

#### Issue 2: No M1 Data Found

**Error:**
```
⚠️ No M1 data found for EURUSD 2024
```

**Solution:**
1. Verify M1 table exists: `forex_eurusd_m1`
2. Check if year has data:
   ```sql
   SELECT count() FROM forex_eurusd_m1 WHERE toYear(DateTime) = 2024
   ```
3. Download M1 data first using FXCM Data Downloader
4. Verify table name format is correct

#### Issue 3: Python Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'pandas'
```

**Solution:**
```bash
pip install pandas clickhouse-connect
```

#### Issue 4: Insufficient Disk Space

**Error:**
```
❌ Error writing to ClickHouse: No space left on device
```

**Solution:**
1. Check disk space: `df -h` (Linux) or Properties in Windows
2. Free up space by deleting old logs
3. Use `--skip-existing` to avoid re-processing
4. Process year by year instead of all at once

#### Issue 5: Slow Performance

**Symptom:** Processing takes too long

**Solutions:**
1. **Process fewer years at a time:**
   ```bash
   python scripts\m1_timeframe_converter.py --start-year 2024 --end-year 2024
   ```

2. **Process specific pairs:**
   ```bash
   python scripts\m1_timeframe_converter.py --pairs EURUSD
   ```

3. **Check network speed to ClickHouse server**

4. **Verify ClickHouse server has sufficient resources**

5. **Use --skip-existing for incremental updates**

#### Issue 6: Permission Denied

**Error:**
```
❌ Error writing to ClickHouse: Permission denied
```

**Solution:**
1. Verify ClickHouse user has write permissions
2. Check database/table permissions
3. Try with admin credentials
4. Verify firewall allows outbound connections

---

## 8. FAQ

### Q1: How long does it take to convert all data?

**A:** Depends on data volume and hardware:
- **Single pair, single year, single timeframe:** 1-5 seconds
- **Single pair, 10 years, all timeframes:** 1-5 minutes
- **All pairs, 10 years, all timeframes:** 10-30 minutes

**Benchmark:** ~1-2 million M1 records processed per minute

### Q2: Can I run this tool while downloading M1 data?

**A:** Yes, but not recommended. Best practice:
1. Download all M1 data first
2. Then convert to higher timeframes
3. This avoids incomplete data issues

### Q3: What happens if I stop the tool mid-process?

**A:** 
- Data already written is saved (per-year commits)
- You can re-run with `--skip-existing` to continue
- No data corruption (ClickHouse transactions)

### Q4: Should I use skip or overwrite mode?

**Overwrite Mode (default):**
- ✅ Ensures latest data (if M1 was updated)
- ✅ Fixes any previous errors
- ❌ Takes more time

**Skip Mode (`--skip-existing`):**
- ✅ Much faster for incremental updates
- ✅ Saves processing time
- ❌ Won't update if M1 data changed

**Recommendation:** 
- Use **overwrite** for first run or after M1 updates
- Use **skip** for regular maintenance

### Q5: How much disk space do I need?

**Estimation:**
- **M1 data (1 pair, 1 year):** ~100 MB
- **M5 data:** ~20 MB (5x smaller)
- **M15 data:** ~7 MB (15x smaller)
- **M30 data:** ~3.5 MB (30x smaller)
- **H1 data:** ~1.7 MB (60x smaller)

**Total for 6 pairs, 10 years:**
- M1: ~6 GB
- M5+M15+M30+H1: ~2 GB

**Recommendation:** Have at least 10 GB free space

### Q6: Can I add more currency pairs?

**A:** Yes, modify the code:

1. Edit `m1_timeframe_converter.py`:
   ```python
   AVAILABLE_PAIRS = ['EURUSD', 'GBPUSD', 'USDJPY', 
                      'AUDUSD', 'USDCAD', 'USDCHF',
                      'NZDUSD']  # Add new pair
   ```

2. Ensure M1 data exists for the new pair in ClickHouse

3. Re-run the converter

### Q7: Can I add more timeframes (e.g., H4, D1)?

**A:** Yes, modify the code:

```python
AVAILABLE_TIMEFRAMES = ['M5', 'M15', 'M30', 'H1', 'H4']
TIMEFRAME_MINUTES = {'M5': 5, 'M15': 15, 'M30': 30, 'H1': 60, 'H4': 240}
```

### Q8: How do I verify the converted data is correct?

**Manual Check:**
```sql
-- Check record count
SELECT count() FROM forex_eurusd_m5 WHERE toYear(DateTime) = 2024;

-- Check OHLC values
SELECT * FROM forex_eurusd_m5 LIMIT 10;

-- Verify no gaps
SELECT 
    DateTime,
    DateTime - lag(DateTime) OVER (ORDER BY DateTime) as gap
FROM forex_eurusd_m5
WHERE toYear(DateTime) = 2024
ORDER BY DateTime
LIMIT 100;
```

**Automated Check:**
Run the test suite:
```bash
python scripts\test\test_m1_converter.py
```

### Q9: Should I use local mode or database mode?

**A:** Choose based on your needs:

**Use Local Mode (--mode local) if:**
- ✅ You have CSV data in `fxcm_data/` folder
- ✅ You want offline processing (no database needed)
- ✅ You need flexibility for custom calculations
- ✅ Data volume is under 10 million M1 records
- ✅ Development/testing environment

**Use Database Mode (--mode database) if:**
- ✅ M1 data is already in ClickHouse
- ✅ You need maximum speed (~10x faster)
- ✅ Processing large datasets (100M+ records)
- ✅ Production environment
- ✅ Integration with other database systems

**Performance Comparison:**
| Dataset | Local Mode | Database Mode |
|---------|------------|---------------|
| 1 year, 1 pair, all TFs | ~45 sec | ~5 sec |
| 10 years, 1 pair, all TFs | ~5 min | ~30 sec |
| 10 years, 6 pairs, all TFs | ~30 min | ~3 min |

**See also:** `doc/manual/m1_converter_modes.md` for detailed comparison

### Q10: Can I mix local mode and database mode?

**A:** Yes, but not recommended:
- Local mode writes to CSV files
- Database mode writes to ClickHouse tables
- They are independent output paths

**Best practice:** Choose one mode and stick with it for consistency.

### Q11: Does local mode still need ClickHouse?

**A:** 
- **For conversion:** No! Local mode is completely independent.
- **For source data:** Only if you want to import M1 data to ClickHouse first.

**Typical workflows:**

**Pure Local Workflow (No ClickHouse needed):**
```bash
# 1. Download M1 CSV data
python scripts\fxcm_data_downloader.py

# 2. Convert using local mode
python scripts\m1_timeframe_converter.py --mode local

# 3. Use CSV files directly
# Files in: fxcm_data/EURUSD/M5/2024/2024.csv
```

**Database Workflow:**
```bash
# 1. Download M1 CSV data
python scripts\fxcm_data_downloader.py

# 2. Import to ClickHouse
python scripts\batch_import_m1.py

# 3. Convert using database mode
python scripts\m1_timeframe_converter.py --mode database

# 4. Query from ClickHouse
```

### Q12: What if I get errors for some years but not others?

**A:**
- The tool continues processing even if one year fails
- Check the log file for specific error messages
- Fix the issue (e.g., missing M1 data)
- Re-run with `--skip-existing` to process only failed years

---

## 9. Best Practices

### 9.1 Choosing the Right Conversion Mode

**For Development/Testing:**
```bash
# Use local mode (no database needed)
python scripts\m1_timeframe_converter.py --mode local --pairs EURUSD --start-year 2024
```

**For Production (Small-Medium Data):**
```bash
# Local mode is simpler and sufficient
python scripts\m1_timeframe_converter.py --mode local
```

**For Production (Large Data, High Performance):**
```bash
# Database mode for maximum speed
python scripts\m1_timeframe_converter.py --mode database
```

### 9.2 Recommended Workflows

**Workflow A: Pure Local Mode (No Database)**

Best for: Development, testing, offline analysis

```bash
# Step 1: Download M1 CSV data
python scripts\fxcm_data_downloader.py

# Step 2: Convert using local mode
python scripts\m1_timeframe_converter.py --mode local

# Step 3: Use CSV files
# Data in: fxcm_data/{pair}/{timeframe}/{year}/{year}.csv
```

**Workflow B: Database Mode (High Performance)**

Best for: Production, large-scale processing

```bash
# Step 1: Download M1 CSV data
python scripts\fxcm_data_downloader.py

# Step 2: Import to ClickHouse
python scripts\batch_import_m1.py

# Step 3: Convert using database mode
python scripts\m1_timeframe_converter.py --mode database

# Step 4: Query from ClickHouse or export to CSV
```

**Workflow C: Hybrid Approach**

Best for: Flexibility + performance

```bash
# Keep both CSV and database data
# Use local mode for development
python scripts\m1_timeframe_converter.py --mode local --pairs EURUSD

# Use database mode for production batch processing
python scripts\m1_timeframe_converter.py --mode database --start-year 2020
```

### 9.3 Recommended Workflow (Original - Deprecated)

**Step 1: Initial Setup**
```bash
# Download all M1 data first
python scripts\fxcm_data_downloader.py

# Then convert to all timeframes
python scripts\m1_timeframe_converter.py
```

**Step 2: Regular Updates**
```bash
# Download new M1 data
python scripts\fxcm_data_downloader.py --start-year 2025 --end-year 2025

# Convert only new data
python scripts\m1_timeframe_converter.py --start-year 2025 --end-year 2025
```

**Step 3: Verification**
```bash
# Run tests
python scripts\test\test_m1_converter.py

# Check logs
cat logs\m1_converter_report_*.txt
```

### 9.4 Performance Tips

✅ **Process year by year** for large datasets  
✅ **Use database mode** for data >10M M1 records  
✅ **Use local mode** for flexibility and offline processing  
✅ **Use `--skip-existing`** for incremental updates  
✅ **Monitor disk space** before large conversions  
✅ **Check logs** for errors after each run  

### 9.5 Data Quality Tips

✅ **Process year by year** for large datasets  
✅ **Use skip mode** for incremental updates  
✅ **Run during off-hours** to avoid network congestion  
✅ **Monitor disk space** before large conversions  
✅ **Check logs** for errors after each run  

### 9.3 Data Quality Tips

✅ **Always convert from M1** (don't aggregate M5 to M15)  
✅ **Verify M1 data first** before converting  
✅ **Use overwrite mode** after M1 data updates  
✅ **Check for gaps** in time series  
✅ **Validate OHLC relationships** (High >= Low)  

### 9.4 Maintenance Tips

✅ **Clean old logs** periodically (keep last 30 days)  
✅ **Monitor database size** in ClickHouse  
✅ **Backup data** before major conversions  
✅ **Update Python packages** regularly  
✅ **Test with small dataset** before full conversion  

### 9.5 Security Tips

✅ **Don't commit passwords** to version control  
✅ **Use environment variables** for credentials (future)  
✅ **Limit database permissions** (read M1, write timeframes only)  
✅ **Use secure network** for ClickHouse connections  
✅ **Regularly update dependencies** for security patches  

---

## 10. Support and Resources

### 10.1 Documentation

- **Requirements:** `doc/requirement/m1_converter_requirements.md`
- **Design:** `doc/design/m1_converter_design.md`
- **This Manual:** `doc/manual/m1_converter_manual.md`
- **README:** `README_M1_CONVERTER.md`

### 10.2 Testing

- **Test Suite:** `scripts/test/test_m1_converter.py`
- Run tests: `python scripts\test\test_m1_converter.py`

### 10.3 Logs

- **Log Directory:** `logs/`
- **Log Files:** `m1_converter_YYYYMMDD_HHMMSS.log`
- **Reports:** `m1_converter_report_YYYYMMDD_HHMMSS.txt`

### 10.4 Related Tools

- **FXCM Data Downloader:** Download M1 source data
- **Data Consistency Checker:** Verify data integrity

---

## Appendix A: OHLC Aggregation Examples

### Example 1: M1 to M5 Aggregation

**Input (5 M1 bars):**
```
2024-01-01 00:00:00  Open=1.1000  High=1.1005  Low=1.0995  Close=1.1001
2024-01-01 00:01:00  Open=1.1001  High=1.1006  Low=1.0996  Close=1.1002
2024-01-01 00:02:00  Open=1.1002  High=1.1007  Low=1.0997  Close=1.1003
2024-01-01 00:03:00  Open=1.1003  High=1.1008  Low=1.0998  Close=1.1004
2024-01-01 00:04:00  Open=1.1004  High=1.1009  Low=1.0999  Close=1.1005
```

**Output (1 M5 bar):**
```
2024-01-01 00:00:00  Open=1.1000  High=1.1009  Low=1.0995  Close=1.1005
                     ↑            ↑            ↑            ↑
                     First        Max          Min          Last
```

### Example 2: M1 to H1 Aggregation

**Input:** 60 M1 bars (00:00 to 00:59)

**Output:** 1 H1 bar
```
DateTime: 2024-01-01 00:00:00
Open: First M1 open (00:00)
High: Maximum of all 60 M1 highs
Low: Minimum of all 60 M1 lows
Close: Last M1 close (00:59)
```

---

## Appendix B: ClickHouse Table Structure

### M1 Source Table
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
ORDER BY DateTime;
```

### M5 Target Table
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
ORDER BY DateTime;
```

**Note:** Tables are created automatically by the converter.

---

## Appendix C: Sample Commands Cheat Sheet

```bash
# Convert all data (default)
python scripts\m1_timeframe_converter.py

# Convert single pair
python scripts\m1_timeframe_converter.py --pairs EURUSD

# Convert multiple pairs
python scripts\m1_timeframe_converter.py --pairs EURUSD GBPUSD

# Convert specific timeframes
python scripts\m1_timeframe_converter.py --timeframes M5 H1

# Convert specific years
python scripts\m1_timeframe_converter.py --start-year 2020 --end-year 2023

# Skip existing data
python scripts\m1_timeframe_converter.py --skip-existing

# Custom ClickHouse server
python scripts\m1_timeframe_converter.py --ch-host 192.168.1.100

# Combined parameters
python scripts\m1_timeframe_converter.py --pairs EURUSD --timeframes M5 --start-year 2024 --skip-existing

# Get help
python scripts\m1_timeframe_converter.py --help

# Run tests
python scripts\test\test_m1_converter.py
```

---

**Document Version:** 2.0.0  
**Last Updated:** 2025-10-05  
**Author:** binphilxiao
