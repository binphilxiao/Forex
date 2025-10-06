# FXCM Data Downloader v2.0

<div align="center">

**Download Historical Forex Data from FXCM's Public API**

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-2.0.0-orange.svg)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Documentation](#-documentation)
- [Installation](#-installation)
- [Usage Examples](#-usage-examples)
- [Directory Structure](#-directory-structure)
- [Testing](#-testing)
- [Changelog](#-changelog)
- [License](#-license)

---

## 🎯 Overview

The FXCM Data Downloader is a robust Python script designed to download historical forex data from FXCM's public API. It provides a simple yet powerful command-line interface for downloading years of forex data across multiple currency pairs and timeframes.

### Key Capabilities

- **Multiple Currency Pairs**: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF
- **Multiple Timeframes**: M1 (1-minute candles), D1 (daily candles)
- **Wide Date Range**: 2015 to present (10+ years of historical data)
- **Smart Resume**: Automatically skips existing files
- **Comprehensive Logging**: Detailed logs for every operation
- **Error Handling**: Robust retry mechanism with configurable attempts

---

## ✨ Features

### Core Features

✅ **Flexible Download Options**
- Select specific currency pairs or download all
- Choose M1, D1, or both timeframes
- Specify custom date ranges

✅ **Intelligent File Management**
- Organized directory structure
- Automatic skip of existing files
- Resume capability after interruption

✅ **Robust Error Handling**
- Configurable retry mechanism (default: 5 attempts)
- Graceful handling of 404 errors
- Network error recovery

✅ **Comprehensive Logging**
- Timestamped log files
- Detailed download statistics
- Summary reports

✅ **Easy to Use**
- Simple command-line interface
- Windows batch file included
- Sensible defaults (zero configuration needed)

---

## 🚀 Quick Start

### Windows

```batch
# Double-click or run in Command Prompt
download_fxcm_data.bat
```

### Linux/macOS

```bash
python3 scripts/fxcm_data_downloader.py
```

### Default Behavior

By default, the script downloads:
- All 6 currency pairs
- Both M1 and D1 timeframes
- Data from 2015 to current year
- Saves to `fxcm_data/` directory
- Logs to `logs/` directory

---

## 📚 Documentation

Comprehensive documentation is available:

| Document | Description | Link |
|----------|-------------|------|
| **Requirements** | Detailed functional and non-functional requirements | [fxcm_downloader_requirements.md](doc/requirement/fxcm_downloader_requirements.md) |
| **Design** | System architecture, class design, and technical details | [fxcm_downloader_design.md](doc/design/fxcm_downloader_design.md) |
| **User Manual** | Complete usage guide with examples and troubleshooting | [fxcm_downloader_manual.md](doc/manual/fxcm_downloader_manual.md) |
| **Test Suite** | Automated testing documentation | See [Testing](#-testing) section |

---

## 💻 Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Stable internet connection
- 50-100 GB free disk space (for full dataset)

### Install Dependencies

```bash
pip install pandas requests
```

### Verify Installation

```bash
python scripts/fxcm_data_downloader.py --help
```

---

## 📖 Usage Examples

### Example 1: Download All Data (Default)

```bash
python scripts/fxcm_data_downloader.py
```

Downloads all pairs, all timeframes, from 2015 to now.

---

### Example 2: Download Specific Currency Pair

```bash
python scripts/fxcm_data_downloader.py --pairs EURUSD
```

Downloads only EURUSD data.

---

### Example 3: Download Multiple Pairs

```bash
python scripts/fxcm_data_downloader.py --pairs EURUSD GBPUSD USDJPY
```

---

### Example 4: Download Only M1 Data

```bash
python scripts/fxcm_data_downloader.py --timeframes M1
```

Downloads minute-level data only.

---

### Example 5: Download Only D1 Data

```bash
python scripts/fxcm_data_downloader.py --timeframes D1
```

Downloads daily data only (much faster, smaller size).

---

### Example 6: Download Recent Data

```bash
python scripts/fxcm_data_downloader.py --start-year 2020
```

Downloads data from 2020 onwards only.

---

### Example 7: Download Specific Date Range

```bash
python scripts/fxcm_data_downloader.py --start-year 2018 --end-year 2023
```

Downloads data from 2018 to 2023.

---

### Example 8: Custom Retry Attempts

```bash
# Network unstable - retry 10 times
python scripts/fxcm_data_downloader.py --max-retries 10

# Quick test - no retry
python scripts/fxcm_data_downloader.py --pairs EURUSD --timeframes D1 --start-year 2024 --max-retries 1
```

**Retry mechanism:**
- Automatically retries failed downloads
- Default: 5 retry attempts
- 0.5 second delay between retries
- See [Retry Mechanism Guide](doc/fxcm_downloader_retry_mechanism.md) for details

---

### Example 9: Complex Configuration

```bash
python scripts/fxcm_data_downloader.py \
    --pairs EURUSD GBPUSD \
    --timeframes M1 \
    --start-year 2020 \
    --end-year 2023 \
    --max-retries 3
```

Downloads EURUSD and GBPUSD, M1 only, from 2020 to 2023, with 3 retry attempts.

---

### Example 10: Resume Interrupted Download

Simply run the same command again:

```bash
python scripts/fxcm_data_downloader.py
```

The script automatically skips existing files and continues.

---

## 📁 Directory Structure

### Project Structure

```
Forex/
├── scripts/
│   ├── fxcm_data_downloader.py    # Main script
│   └── test/
│       └── test_fxcm_downloader.py # Test suite
├── doc/
│   ├── requirement/
│   │   └── fxcm_downloader_requirements.md
│   ├── design/
│   │   └── fxcm_downloader_design.md
│   └── manual/
│       └── fxcm_downloader_manual.md
├── fxcm_data/                     # Downloaded data (auto-created)
├── logs/                          # Log files (auto-created)
├── download_fxcm_data.bat         # Windows launcher
└── README_FXCM_DOWNLOADER.md      # This file
```

### Downloaded Data Structure

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
└── ...
```

### CSV File Format

All CSV files have the same structure:

```csv
DateTime,Open,High,Low,Close
2020-01-01 00:00:00,1.1234,1.1240,1.1230,1.1238
2020-01-01 00:01:00,1.1238,1.1245,1.1235,1.1242
...
```

**Columns**:
- **DateTime**: ISO 8601 timestamp (YYYY-MM-DD HH:MM:SS)
- **Open**: Opening price
- **High**: Highest price in the period
- **Low**: Lowest price in the period
- **Close**: Closing price

**Note**: Volume data is not included (not provided by FXCM).

---

## 🧪 Testing

### Run Test Suite

```bash
python scripts/test/test_fxcm_downloader.py
```

### Test Coverage

The test suite includes:

1. **Initialization Tests**: Verify proper setup
2. **Configuration Tests**: Check available pairs and timeframes
3. **Download Tests**: Test M1 and D1 downloads
4. **Error Handling Tests**: Verify invalid input handling
5. **Directory Tests**: Check proper file structure creation
6. **Statistics Tests**: Verify accurate tracking
7. **Logging Tests**: Ensure proper log file creation
8. **Skip Logic Tests**: Verify existing file detection

### Test Results

All tests should pass. Example output:

```
test_01_initialization ... ok
test_02_available_pairs ... ok
test_03_available_timeframes ... ok
...
test_13_skip_existing_files ... ok

======================================================================
Test Summary
======================================================================
Tests run: 13
Successes: 13
Failures: 0
Errors: 0
======================================================================
```

---

## 📊 Command-Line Options

```
usage: fxcm_data_downloader.py [-h] 
                               [--pairs {EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD,USDCHF} ...]
                               [--timeframes {M1,D1} ...]
                               [--start-year START_YEAR]
                               [--end-year END_YEAR]
                               [--max-retries MAX_RETRIES]

options:
  -h, --help            Show help message and exit
  
  --pairs {EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD,USDCHF} ...
                        Currency pairs to download (default: all)
  
  --timeframes {M1,D1} ...
                        Timeframes to download (default: M1 D1)
  
  --start-year START_YEAR
                        Start year (default: 2015)
  
  --end-year END_YEAR   End year (default: current year)
  
  --max-retries MAX_RETRIES
                        Maximum retry attempts (default: 5)
```

---

## 📝 Log Files

### Log Types

#### Download Log
**Location**: `logs/fxcm_download_YYYYMMDD_HHMMSS.log`

Contains:
- Detailed download activity
- Success/failure for each file
- Error messages
- Retry attempts

#### Summary Report
**Location**: `logs/fxcm_download_summary_YYYYMMDD_HHMMSS.txt`

Contains:
- Configuration used
- Final statistics
- Completion time

---

## ⚡ Performance

### Download Times (Approximate)

| Dataset | Size | Time |
|---------|------|------|
| Full dataset (all pairs, M1+D1, 2015-now) | 50-100 GB | 2-4 hours |
| Single pair (M1+D1, 2015-now) | 8-15 GB | 20-40 minutes |
| All pairs, D1 only (2015-now) | 5-10 GB | 5-10 minutes |
| Recent 3 years (all pairs, M1+D1) | 15-30 GB | 30-60 minutes |

*Times vary based on internet connection speed*

---

## 🔧 Troubleshooting

### Common Issues

#### Issue: Module not found
```bash
# Solution
pip install pandas requests
```

#### Issue: Many 404 errors
This is normal. FXCM doesn't have data for all weeks/years.

#### Issue: Slow download
- Check internet connection
- Try downloading during off-peak hours
- Download specific pairs/timeframes only

#### Issue: Disk full
- Free up space
- Download specific subsets: `--pairs EURUSD --timeframes D1`

### Get Help

1. Check [User Manual](doc/manual/fxcm_downloader_manual.md) - Comprehensive troubleshooting guide
2. Review log files in `logs/` directory
3. Check GitHub issues

---

## 📋 Changelog

### Version 2.0.0 (2025-10-05)

**New Features**:
- Complete rewrite of original `download_fxcm_candles.py`
- Command-line argument support
- Flexible currency pair selection
- Flexible timeframe selection
- Custom date range selection
- Comprehensive logging system
- Summary report generation
- Windows batch file launcher

**Improvements**:
- Better error handling
- Retry mechanism
- Skip existing files
- Organized code structure
- Type hints
- Comprehensive documentation

**Documentation**:
- Requirements specification
- Design documentation
- User manual
- Test suite
- This README

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Support for additional currency pairs
- Support for additional timeframes (H1, H4, W1, MN1)
- Progress bars for downloads
- Parallel downloads
- GUI interface
- Scheduled downloads

---

## 📜 License

This project is licensed under the MIT License.

**Data License**: Check FXCM's terms of service for data usage policies.

---

## 🌟 Acknowledgments

- **FXCM** for providing free historical forex data via public API
- **pandas** for CSV processing
- **requests** for HTTP functionality

---

## 📧 Contact

**Author**: binphilxiao  
**Project**: FXCM Data Downloader v2.0  
**Date**: 2025-10-05

---

## 🔗 Quick Links

- [Requirements Documentation](doc/requirement/fxcm_downloader_requirements.md)
- [Design Documentation](doc/design/fxcm_downloader_design.md)
- [User Manual](doc/manual/fxcm_downloader_manual.md)
- [Test Suite](scripts/test/test_fxcm_downloader.py)

---

<div align="center">

**⭐ If this project helps you, please give it a star! ⭐**

Made with ❤️ for the forex trading community

**Last Updated**: 2025-10-05 | **Version**: 2.0.0

</div>
