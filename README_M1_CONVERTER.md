# M1 Timeframe Converter v2.0

**Convert 1-minute forex data to higher timeframes with ClickHouse integration**

---

## 🎯 Overview

The M1 Timeframe Converter is a professional-grade Python tool that aggregates 1-minute (M1) forex market data into higher timeframes (M5, M15, M30, H1) and stores the results in ClickHouse database.

### Key Features

✅ **Multi-Timeframe Support**
- M5 (5 minutes)
- M15 (15 minutes)
- M30 (30 minutes)
- H1 (1 hour)

✅ **6 Major Currency Pairs**
- EURUSD, GBPUSD, USDJPY
- AUDUSD, USDCAD, USDCHF

✅ **ClickHouse Integration**
- Fast database storage
- Efficient batch processing
- Auto-table creation

✅ **Dual Conversion Modes**
- Local mode: CSV-based processing (default)
- Database mode: ClickHouse SQL aggregation

✅ **Flexible CLI**
- Selective pair/timeframe conversion
- Custom date ranges
- Skip or overwrite modes

✅ **Comprehensive Logging**
- Detailed progress tracking
- Summary reports
- Error handling

---

## 📊 Quick Start

### Using Windows Batch File (Easiest)

```cmd
convert_m1_to_multi_timeframes.bat
```

### Using Command Line

```bash
# Convert all data (default)
python scripts\m1_timeframe_converter.py

# Convert specific pair
python scripts\m1_timeframe_converter.py --pairs EURUSD

# Convert specific timeframes
python scripts\m1_timeframe_converter.py --timeframes M5 H1

# Convert specific year range
python scripts\m1_timeframe_converter.py --start-year 2020 --end-year 2024

# Skip existing data (faster)
python scripts\m1_timeframe_converter.py

# Use local mode (CSV-based, default)
python scripts\m1_timeframe_converter.py --mode local

# Use database mode (ClickHouse SQL, ultra-fast)
python scripts\m1_timeframe_converter.py --mode database
```

---

## 📋 Installation

### Prerequisites

- **Python 3.7+**
- **ClickHouse** database server
- **M1 data** loaded in ClickHouse

### Install Dependencies

```bash
pip install pandas clickhouse-connect
```

### Verify Installation

```bash
python scripts\m1_timeframe_converter.py --help
```

---

## 💡 Usage Examples

### Example 1: Convert All Data

```bash
python scripts\m1_timeframe_converter.py
```

**Output:**
- 6 pairs × 4 timeframes = 24 datasets
- Years: 2015 to current year
- Mode: Overwrite existing data

### Example 2: Convert Recent Years Only

```bash
python scripts\m1_timeframe_converter.py --start-year 2022 --end-year 2024
```

**Output:**
- All pairs, all timeframes
- Only years 2022-2024

### Example 3: Incremental Update

```bash
python scripts\m1_timeframe_converter.py
```

**Output:**
- Default mode: Skip existing data
- Only processes new/missing data
- Much faster for updates

### Example 4: Force Overwrite

```bash
python scripts\m1_timeframe_converter.py --overwrite
```

**Output:**
- Overwrites all existing data
- Ensures latest M1 data is used
- Takes longer but guarantees freshness

### Example 4: Specific Pair and Timeframe

```bash
python scripts\m1_timeframe_converter.py --pairs EURUSD --timeframes M5
```

**Output:**
- Only EURUSD M5 data
- All years

### Example 5: Custom ClickHouse Server

```bash
python scripts\m1_timeframe_converter.py --ch-host 192.168.1.100 --ch-port 8123
```

**Output:**
- Connects to custom server
- All other settings default

---

## 📂 Output

### Console Output

```
============================================================
M1 to Multi-Timeframe Converter v2.0
============================================================
Currency Pairs: EURUSD, GBPUSD
Timeframes: M5, M15, M30, H1
Year Range: 2015 - 2025
============================================================

Processing: EURUSD
  📥 Read 525,600 M1 records for EURUSD 2024
  ✅ Wrote 105,120 records to forex_eurusd_m5
  
============================================================
Conversion Summary
============================================================
Pairs Processed: 6
Timeframes Generated: 24
Records Read (M1): 23,357,603
Records Written: 4,671,521
Processing Time: 1247.5 seconds
✅ Conversion completed!
```

### Log Files

**Location:** `logs/`

- **Log:** `m1_converter_20251005_143015.log`
- **Report:** `m1_converter_report_20251005_143015.txt`

### ClickHouse Tables

**Pattern:** `forex_{pair}_{timeframe}`

**Examples:**
- `forex_eurusd_m5`
- `forex_eurusd_m15`
- `forex_eurusd_m30`
- `forex_eurusd_h1`

---

## 🔧 Command-Line Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--mode` | Str | local | Conversion mode: 'local' or 'database' |
| `--pairs` | List | All 6 | Currency pairs to convert |
| `--timeframes` | List | All 4 | Timeframes to generate |
| `--start-year` | Int | 2015 | Start year |
| `--end-year` | Int | Current | End year |
| `--overwrite` | Flag | False | Overwrite existing data (default: skip) |
| `--ch-host` | Str | 192.168.2.168 | ClickHouse host |
| `--ch-port` | Int | 8123 | ClickHouse HTTP port |
| `--ch-user` | Str | default | Username |
| `--ch-password` | Str | (empty) | Password |

---

## 📚 Documentation

### Core Documentation

1. **[Requirements Specification](doc/requirement/m1_converter_requirements.md)**
   - Functional requirements (FR-1 to FR-12)
   - Non-functional requirements (NFR-1 to NFR-10)
   - User stories and acceptance criteria
   - Success criteria and constraints

2. **[Design Specification](doc/design/m1_converter_design.md)**
   - System architecture
   - Class design and methods
   - Database schema
   - Data flow and algorithms
   - Performance optimization

3. **[User Manual](doc/manual/m1_converter_manual.md)**
   - Installation guide
   - Quick start tutorial
   - Command-line reference
   - Usage examples
   - Troubleshooting and FAQ

### Additional Resources

- **Conversion Modes Guide:** `doc/manual/m1_converter_modes.md`
- **Test Suite:** `scripts/test/test_m1_converter.py`
- **Windows Launcher:** `convert_m1_to_multi_timeframes.bat`
- **Log Directory:** `logs/`

---

## 🧪 Testing

### Run All Tests

```bash
python scripts\test\test_m1_converter.py
```

### Test Coverage

**15 Test Cases:**
- ✅ TC-01: Converter initialization
- ✅ TC-02: Available pairs configuration
- ✅ TC-03: Available timeframes configuration
- ✅ TC-04: Timeframe minutes mapping
- ✅ TC-05: OHLC aggregation rules
- ✅ TC-06: Table name generation
- ✅ TC-07: M5 aggregation logic
- ✅ TC-08: M15 aggregation logic
- ✅ TC-09: M30 aggregation logic
- ✅ TC-10: H1 aggregation logic
- ✅ TC-11: Empty dataframe handling
- ✅ TC-12: Statistics initialization
- ✅ TC-13: Logging configuration
- ✅ TC-14: Partial hour aggregation
- ✅ TC-15: Multi-day aggregation

---

## 📈 Performance

### Benchmarks

| Metric | Performance |
|--------|-------------|
| **M1 Read** | 1-2 million records/min |
| **Aggregation** | 2-5 million records/min |
| **ClickHouse Write** | 500K-1M records/min |
| **Overall** | ~1-2 million M1 records/min |

### Processing Time Estimates

| Dataset | Estimated Time |
|---------|----------------|
| Single pair, 1 year, 1 TF | 1-5 seconds |
| Single pair, 10 years, all TFs | 1-5 minutes |
| All pairs, 10 years, all TFs | 10-30 minutes |

---

## 🔍 How It Works

### OHLC Aggregation Algorithm

For each timeframe period (e.g., 5 minutes for M5):

1. **Open**: First M1 open in period
2. **High**: Maximum M1 high in period
3. **Low**: Minimum M1 low in period
4. **Close**: Last M1 close in period

### Example: M1 to M5

**Input (5 M1 bars):**
```
00:00  Open=1.1000  High=1.1005  Low=1.0995  Close=1.1001
00:01  Open=1.1001  High=1.1006  Low=1.0996  Close=1.1002
00:02  Open=1.1002  High=1.1007  Low=1.0997  Close=1.1003
00:03  Open=1.1003  High=1.1008  Low=1.0998  Close=1.1004
00:04  Open=1.1004  High=1.1009  Low=1.0999  Close=1.1005
```

**Output (1 M5 bar):**
```
00:00  Open=1.1000  High=1.1009  Low=1.0995  Close=1.1005
       ↑            ↑            ↑            ↑
       First        Max          Min          Last
```

---

## 🛠️ Troubleshooting

### Common Issues

#### ClickHouse Connection Failed
```bash
# Check if ClickHouse is running
curl http://192.168.2.168:8123
# Should return "Ok."
```

#### No M1 Data Found
```sql
-- Verify M1 table exists
SELECT count() FROM forex_eurusd_m1 WHERE toYear(DateTime) = 2024;
```

#### Python Module Not Found
```bash
pip install pandas clickhouse-connect
```

### Getting Help

```bash
python scripts\m1_timeframe_converter.py --help
```

---

## 🚀 Best Practices

### Recommended Workflow

1. **Initial Setup:**
   ```bash
   # Download M1 data first
   python scripts\fxcm_data_downloader.py
   
   # Then convert to all timeframes
   python scripts\m1_timeframe_converter.py
   ```

2. **Regular Updates:**
   ```bash
   # Download new M1 data
   python scripts\fxcm_data_downloader.py --start-year 2025
   
   # Convert only new data
   python scripts\m1_timeframe_converter.py --start-year 2025 --skip-existing
   ```

3. **Verification:**
   ```bash
   # Run tests
   python scripts\test\test_m1_converter.py
   
   # Check reports
   type logs\m1_converter_report_*.txt
   ```

### Performance Tips

✅ Process year by year for large datasets  
✅ Use `--skip-existing` for incremental updates  
✅ Run during off-hours to avoid network congestion  
✅ Monitor disk space before large conversions  

### Data Quality Tips

✅ Always convert from M1 (don't aggregate M5 to M15)  
✅ Verify M1 data first before converting  
✅ Use overwrite mode after M1 data updates  
✅ Check for gaps in time series  

---

## 📊 Project Structure

```
Forex/
├── scripts/
│   ├── m1_timeframe_converter.py     # Main converter script
│   └── test/
│       └── test_m1_converter.py      # Test suite
│
├── convert_m1_to_multi_timeframes.bat  # Windows launcher
│
├── doc/
│   ├── requirement/
│   │   └── m1_converter_requirements.md  # Requirements spec
│   ├── design/
│   │   └── m1_converter_design.md       # Design spec
│   └── manual/
│       └── m1_converter_manual.md       # User manual
│
├── logs/                               # Output directory
│   ├── m1_converter_*.log             # Log files
│   └── m1_converter_report_*.txt      # Reports
│
└── README_M1_CONVERTER.md             # This file
```

---

## 🔮 Future Enhancements

### Planned Features (Phase 2)

- ⏭️ Parallel processing of multiple pairs
- ⏭️ Resume capability after interruption
- ⏭️ Data validation and quality checks
- ⏭️ Progress bar (tqdm)
- ⏭️ Email notifications
- ⏭️ Web-based monitoring dashboard
- ⏭️ Support for D1 (daily) timeframe
- ⏭️ CSV/PostgreSQL data sources

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|  
| 2.0.0 | 2025-10-05 | Complete rewrite with ClickHouse integration + dual conversion modes |
| 1.0.2 | Previous | Legacy version (CSV-based) |---

## 👤 Author

**binphilxiao**  
Date: 2025-10-05

---

## 📄 License

MIT License

---

## 🙏 Related Tools

- **[FXCM Data Downloader](README_FXCM_DOWNLOADER.md)**: Download M1 source data
- **Data Consistency Checker**: Verify data integrity

---

## 📞 Support

For issues, questions, or suggestions:

1. Check the [User Manual](doc/manual/m1_converter_manual.md)
2. Review [Troubleshooting](doc/manual/m1_converter_manual.md#7-troubleshooting)
3. Check [FAQ](doc/manual/m1_converter_manual.md#8-faq)
4. Review log files in `logs/` directory

---

**M1 Timeframe Converter v2.0** - Professional forex data aggregation tool
