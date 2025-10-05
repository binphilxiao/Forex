# M1 Converter - Quick Reference Card

**Version:** 2.0.0  
**Date:** 2025-10-05

---

## 🚀 Quick Start

```bash
# Local mode (default) - CSV-based, no database needed
python scripts\m1_timeframe_converter.py

# Database mode - ClickHouse SQL, ultra-fast
python scripts\m1_timeframe_converter.py --mode database

# Specific parameters
python scripts\m1_timeframe_converter.py --pairs EURUSD --timeframes M5 --start-year 2024
```

---

## 📊 Conversion Modes Comparison

| Feature | Local Mode | Database Mode |
|---------|-----------|---------------|
| **Command** | `--mode local` | `--mode database` |
| **Default** | ✅ Yes | No |
| **Data Source** | CSV files | ClickHouse tables |
| **Aggregation** | pandas (Python) | SQL (ClickHouse) |
| **Output** | CSV files | ClickHouse tables |
| **Speed** | 1-2M M1/min | 10-50M M1/min |
| **ClickHouse Required** | ❌ No | ✅ Yes |
| **Network Needed** | ❌ No | ✅ Yes |
| **Offline Use** | ✅ Yes | ❌ No |
| **Memory Usage** | 500MB-1GB | <100MB |
| **Flexibility** | High | Medium |
| **Best For** | Dev, Testing | Production |

---

## 📁 Data Flow

### Local Mode (Default)
```
fxcm_data/EURUSD/M1/2024/week_*.csv
    ↓ Read CSV
    ↓ pandas.resample()
    ↓ Save CSV
fxcm_data/EURUSD/M5/2024/2024.csv
```

### Database Mode
```
ClickHouse: forex_eurusd_m1
    ↓ SQL: INSERT...SELECT...GROUP BY
ClickHouse: forex_eurusd_m5
```

---

## 🎯 Use Cases

### Use Local Mode If:
- ✅ Data volume < 10M M1 records
- ✅ Need offline processing
- ✅ Want CSV output
- ✅ Development/testing
- ✅ Custom calculations needed

### Use Database Mode If:
- ✅ Data volume > 10M M1 records
- ✅ Need maximum speed
- ✅ Production environment
- ✅ Have ClickHouse server
- ✅ Integration with DB systems

---

## 🔧 Parameters Cheat Sheet

| Parameter | Type | Default | Example |
|-----------|------|---------|---------|
| `--mode` | Choice | local | `--mode database` |
| `--pairs` | List | All 6 | `--pairs EURUSD GBPUSD` |
| `--timeframes` | List | All 4 | `--timeframes M5 H1` |
| `--start-year` | Int | 2015 | `--start-year 2024` |
| `--end-year` | Int | Current | `--end-year 2024` |
| `--overwrite` | Flag | False | `--overwrite` |
| `--ch-host` | String | 192.168.2.168 | `--ch-host localhost` |
| `--ch-port` | Int | 8123 | `--ch-port 8123` |

---

## 💡 Common Commands

```bash
# Convert all data with local mode (default)
python scripts\m1_timeframe_converter.py

# Convert EURUSD only, local mode
python scripts\m1_timeframe_converter.py --pairs EURUSD

# Convert 2024 data, database mode (fast)
python scripts\m1_timeframe_converter.py --mode database --start-year 2024 --end-year 2024

# Overwrite existing data
python scripts\m1_timeframe_converter.py --overwrite

# Skip existing data (incremental update)
python scripts\m1_timeframe_converter.py

# Generate only M5, local mode
python scripts\m1_timeframe_converter.py --timeframes M5

# High-speed production batch
python scripts\m1_timeframe_converter.py --mode database --overwrite

# Development test (fast)
python scripts\m1_timeframe_converter.py --mode local --pairs EURUSD --start-year 2024
```

---

## 📈 Performance Estimates

| Task | Local Mode | Database Mode |
|------|-----------|---------------|
| 1 year, 1 pair, 1 TF | 5-10 sec | 0.5-1 sec |
| 1 year, 1 pair, all TFs | 20-40 sec | 2-4 sec |
| 10 years, 1 pair, all TFs | 3-7 min | 20-40 sec |
| 10 years, 6 pairs, all TFs | 20-40 min | 2-4 min |

**Speed Factor:** Database mode is typically **10-20x faster**

---

## 🔍 Verification

```bash
# Run tests (15 test cases)
python scripts\test\test_m1_converter.py

# Check logs
cat logs\m1_converter_report_*.txt

# List generated files (local mode)
ls fxcm_data\EURUSD\M5\2024\

# Query database (database mode)
# In ClickHouse:
SELECT count() FROM forex_eurusd_m5 WHERE toYear(DateTime) = 2024;
```

---

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| **No module 'clickhouse_connect'** | `pip install clickhouse-connect` |
| **No module 'pandas'** | `pip install pandas` |
| **Connection refused** | Check ClickHouse is running: `curl http://192.168.2.168:8123` |
| **No CSV files found** | Download M1 data first: `python scripts\fxcm_data_downloader.py` |
| **Slow performance** | Use database mode or process year-by-year |

---

## 📚 Documentation

- **Full Manual:** `doc/manual/m1_converter_manual.md`
- **Mode Comparison:** `doc/manual/m1_converter_modes.md`
- **README:** `README_M1_CONVERTER.md`
- **Design Doc:** `doc/design/m1_converter_design.md`
- **Requirements:** `doc/requirement/m1_converter_requirements.md`

---

## 🎓 Examples Gallery

### Example 1: First-Time Setup (Local Mode)
```bash
# Step 1: Download M1 data
python scripts\fxcm_data_downloader.py

# Step 2: Convert to all timeframes (local, no DB needed)
python scripts\m1_timeframe_converter.py --mode local

# Step 3: Use CSV files
# Files in: fxcm_data/{pair}/{timeframe}/{year}/{year}.csv
```

### Example 2: Production High-Performance (Database Mode)
```bash
# Step 1: Ensure M1 data is in ClickHouse
# (import CSV to ClickHouse if needed)

# Step 2: Fast conversion
python scripts\m1_timeframe_converter.py --mode database

# Step 3: Query from ClickHouse
# SQL: SELECT * FROM forex_eurusd_m5 LIMIT 100
```

### Example 3: Incremental Daily Update (Local Mode)
```bash
# Daily at 00:05
python scripts\fxcm_data_downloader.py --start-year 2025 --end-year 2025
python scripts\m1_timeframe_converter.py --mode local --start-year 2025
```

### Example 4: Mixed Development + Production
```bash
# Development (local, EURUSD only)
python scripts\m1_timeframe_converter.py --mode local --pairs EURUSD

# Production (database, all pairs)
python scripts\m1_timeframe_converter.py --mode database
```

---

## 🔄 Workflow Patterns

### Pattern A: Pure Local (No Database)
```
Download M1 CSV → Convert (local mode) → Use CSV files
```
**Pros:** Simple, offline, flexible  
**Cons:** Slower for large data

### Pattern B: Pure Database (High Performance)
```
Download M1 CSV → Import to ClickHouse → Convert (database mode) → Query from ClickHouse
```
**Pros:** Ultra-fast, scalable  
**Cons:** Requires database

### Pattern C: Hybrid
```
Download M1 CSV → Keep both CSV and ClickHouse
Local mode for dev → Database mode for production
```
**Pros:** Flexibility + performance  
**Cons:** Double storage

---

## 📞 Support

- **Help:** `python scripts\m1_timeframe_converter.py --help`
- **Tests:** `python scripts\test\test_m1_converter.py`
- **Logs:** `logs/m1_converter_*.log`

---

**Quick Reference v2.0.0** | Last Updated: 2025-10-05 | Author: binphilxiao
