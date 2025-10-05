# FXCM Data Downloader Requirements Specification

**Project**: FXCM Historical Data Downloader v2.0  
**Author**: binphilxiao  
**Date**: 2025-10-05  
**Version**: 2.0.0

---

## 1. Overview

### 1.1 Purpose
The FXCM Data Downloader is a Python script designed to download historical forex data from FXCM's public API and save it to local CSV files for analysis and backtesting purposes.

### 1.2 Scope
This document outlines the functional and non-functional requirements for the FXCM Data Downloader v2.0.

---

## 2. Functional Requirements

### FR-1: Data Download Capability
**Priority**: High  
**Description**: The system shall download historical forex data from FXCM's public API.

**Acceptance Criteria**:
- Successfully connect to FXCM API endpoint
- Download data in gzip-compressed CSV format
- Decompress and parse CSV data
- Save data to local files

### FR-2: Currency Pair Selection
**Priority**: High  
**Description**: The system shall support downloading data for multiple currency pairs.

**Supported Pairs**:
- EURUSD (Euro / US Dollar)
- GBPUSD (British Pound / US Dollar)
- USDJPY (US Dollar / Japanese Yen)
- AUDUSD (Australian Dollar / US Dollar)
- USDCAD (US Dollar / Canadian Dollar)
- USDCHF (US Dollar / Swiss Franc)

**Acceptance Criteria**:
- Default: Download all 6 currency pairs
- Allow user to specify specific pairs via command-line argument
- Validate user-specified pairs against supported list

### FR-3: Timeframe Selection
**Priority**: High  
**Description**: The system shall support downloading data for different timeframes.

**Supported Timeframes**:
- **M1**: 1-minute candles (weekly files)
- **D1**: Daily candles (yearly files)

**Acceptance Criteria**:
- Default: Download both M1 and D1 data
- Allow user to specify timeframes via command-line argument
- Validate user-specified timeframes against supported list

### FR-4: Date Range Selection
**Priority**: High  
**Description**: The system shall allow users to specify date ranges for downloading data.

**Acceptance Criteria**:
- Default start year: 2015
- Default end year: Current year
- Allow user to specify custom start and end years
- Validate that start year is not greater than end year

### FR-5: Directory Structure
**Priority**: High  
**Description**: The system shall organize downloaded data in a hierarchical directory structure.

**Directory Structure**:
```
fxcm_data/
├── {PAIR}/                     # e.g., EURUSD/
│   ├── M1/                     # M1 timeframe
│   │   ├── {YEAR}/             # e.g., 2015/
│   │   │   ├── week_01.csv
│   │   │   ├── week_02.csv
│   │   │   └── ...
│   │   │   └── week_52.csv
│   │   └── ...
│   └── D1/                     # D1 timeframe
│       ├── 2015.csv
│       ├── 2016.csv
│       └── ...
└── ...
```

**Acceptance Criteria**:
- Create directory structure automatically
- M1 data: Organized by pair/timeframe/year/week
- D1 data: Organized by pair/timeframe/year
- Use consistent naming conventions

### FR-6: Skip Existing Files
**Priority**: High  
**Description**: The system shall skip downloading files that already exist locally.

**Acceptance Criteria**:
- Check for file existence before downloading
- Log skipped files
- Display skip status in console output
- Update statistics accordingly

### FR-7: Retry Mechanism
**Priority**: High  
**Description**: The system shall retry failed downloads with configurable attempts.

**Acceptance Criteria**:
- Default retry count: 5 attempts
- Configurable via command-line argument
- Delay between retries: 0.5 seconds
- Log retry attempts
- Handle 404 errors (data not available) gracefully

### FR-8: Logging System
**Priority**: High  
**Description**: The system shall maintain detailed logs of download operations.

**Log Requirements**:
- Timestamp-based log filenames: `fxcm_download_YYYYMMDD_HHMMSS.log`
- Log location: `logs/` directory
- Log levels: DEBUG, INFO, WARNING, ERROR
- Dual output: File and console

**Log Contents**:
- Download start/end times
- Successful downloads with record counts
- Skipped files (existing)
- Failed downloads (404, errors)
- Retry attempts
- Summary statistics

**Acceptance Criteria**:
- Create log directory automatically
- Generate unique log file per run
- Capture all download events
- Include timestamps for all entries

### FR-9: Summary Report
**Priority**: Medium  
**Description**: The system shall generate a summary report after download completion.

**Report Contents**:
- Configuration (pairs, timeframes, date range)
- Total files processed
- Files downloaded
- Files skipped (existing)
- Files failed/not available
- Total records downloaded
- Time elapsed

**Acceptance Criteria**:
- Save report to `logs/` directory
- Filename format: `fxcm_download_summary_YYYYMMDD_HHMMSS.txt`
- Display summary in console
- Include in log file

### FR-10: Data Normalization
**Priority**: High  
**Description**: The system shall normalize downloaded CSV data to a standard format.

**Standard Format**:
```
DateTime, Open, High, Low, Close
```

**Acceptance Criteria**:
- Handle FXCM format with Bid prefix (BidOpen, BidHigh, BidLow, BidClose)
- Handle standard format (Open, High, Low, Close)
- Convert DateTime to pandas datetime format
- Remove Volume column (if present)
- Maintain only OHLC columns

### FR-11: Command-Line Interface
**Priority**: Medium  
**Description**: The system shall provide a command-line interface for configuration.

**Arguments**:
- `--pairs`: Specify currency pairs
- `--timeframes`: Specify timeframes (M1, D1)
- `--start-year`: Specify start year
- `--end-year`: Specify end year
- `--max-retries`: Specify maximum retry attempts

**Acceptance Criteria**:
- Support all specified arguments
- Provide help text (`--help`)
- Show usage examples
- Validate argument values
- Use sensible defaults

### FR-12: Batch File Launcher (Windows)
**Priority**: Medium  
**Description**: Provide a Windows batch file for easy script execution.

**Acceptance Criteria**:
- UTF-8 encoding support
- Activate virtual environment (if exists)
- Pass command-line arguments through
- Display status messages
- Pause on completion

---

## 3. Non-Functional Requirements

### NFR-1: Performance
**Description**: The system shall download data efficiently.

**Requirements**:
- Rate limiting: 0.1 second delay between requests
- Connection timeout: 30 seconds
- Efficient gzip decompression
- Minimal memory footprint

**Acceptance Criteria**:
- Download full dataset (6 pairs, 10 years, M1+D1) in reasonable time
- Memory usage stays within acceptable limits
- No significant performance degradation over time

### NFR-2: Reliability
**Description**: The system shall handle errors gracefully.

**Requirements**:
- Retry failed downloads (5 attempts)
- Handle network errors
- Handle HTTP errors (404, 500, etc.)
- Handle malformed CSV data
- Continue on individual file failure

**Acceptance Criteria**:
- Script doesn't crash on single file failure
- All errors are logged
- User receives meaningful error messages

### NFR-3: Usability
**Description**: The system shall be easy to use.

**Requirements**:
- Simple command-line interface
- Clear console output
- Progress indicators
- Helpful error messages
- Documentation and examples

**Acceptance Criteria**:
- Users can run with default settings (zero configuration)
- Command-line help is comprehensive
- Output is clear and informative

### NFR-4: Maintainability
**Description**: The system shall be easy to maintain and extend.

**Requirements**:
- Clean, documented code
- Modular design
- Consistent naming conventions
- Type hints
- Comprehensive docstrings

**Acceptance Criteria**:
- Code follows PEP 8 style guide
- All functions have docstrings
- Type hints on all function signatures
- Easy to add new currency pairs or timeframes

### NFR-5: Compatibility
**Description**: The system shall work across different platforms.

**Requirements**:
- Python 3.7+
- Windows, Linux, macOS support
- UTF-8 encoding handling

**Acceptance Criteria**:
- Runs on Python 3.7 and later
- No platform-specific code (except batch file)
- Proper Unicode/UTF-8 handling

### NFR-6: Data Integrity
**Description**: Downloaded data shall be accurate and complete.

**Requirements**:
- Verify gzip decompression
- Validate CSV structure
- Maintain OHLC relationships (High >= Open, Close, Low <= Open, Close)
- Preserve datetime precision

**Acceptance Criteria**:
- Downloaded data matches FXCM source
- No data corruption during download/save
- CSV files are valid and parseable

### NFR-7: Testability
**Description**: The system shall be testable.

**Requirements**:
- Unit tests for core functionality
- Test data download
- Test directory structure creation
- Test error handling
- Test skip logic

**Acceptance Criteria**:
- Comprehensive test suite
- All tests pass
- Test coverage > 80%

### NFR-8: Documentation
**Description**: The system shall be well-documented.

**Documentation Required**:
- Requirements specification (this document)
- Design documentation
- User manual
- API documentation (docstrings)
- README file

**Acceptance Criteria**:
- All documents exist and are up-to-date
- Documents are clear and comprehensive
- Code examples are provided

### NFR-9: Logging
**Description**: Logging shall be comprehensive and useful.

**Requirements**:
- Separate log files per run
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- Both file and console output
- Timestamp all entries

**Acceptance Criteria**:
- Logs contain sufficient detail for troubleshooting
- Logs are rotated (one per run)
- Console output is user-friendly

### NFR-10: Resource Management
**Description**: The system shall manage resources properly.

**Requirements**:
- Close HTTP connections
- Release file handles
- Clean up temporary data
- Graceful shutdown

**Acceptance Criteria**:
- No resource leaks
- Proper cleanup on exit
- Handles interrupt signals (Ctrl+C) gracefully

---

## 4. User Stories

### US-1: Download All Data
**As a** forex trader  
**I want to** download all available historical data  
**So that** I can backtest my trading strategies

**Acceptance Criteria**:
- Run script with no arguments
- Download all 6 pairs, both timeframes, 2015-now
- Skip existing files
- Complete successfully with summary

### US-2: Download Specific Pair
**As a** forex analyst  
**I want to** download data for a specific currency pair  
**So that** I can focus on my area of interest

**Acceptance Criteria**:
- Specify pair with `--pairs EURUSD`
- Download only EURUSD data
- Skip other pairs

### US-3: Download Recent Data
**As a** day trader  
**I want to** download only recent data  
**So that** I can save time and storage space

**Acceptance Criteria**:
- Specify date range: `--start-year 2020`
- Download only 2020-now
- Skip older years

### US-4: Resume Failed Download
**As a** user with intermittent connection  
**I want to** resume a partially completed download  
**So that** I don't lose progress

**Acceptance Criteria**:
- Re-run script after interruption
- Skip existing files
- Continue downloading missing files
- Complete successfully

### US-5: Verify Downloaded Data
**As a** quality-conscious user  
**I want to** review download logs  
**So that** I can verify data integrity

**Acceptance Criteria**:
- Access log file in `logs/` directory
- View detailed download status for each file
- Check summary report
- Identify any failed downloads

---

## 5. Constraints

### 5.1 Technical Constraints
- Must use FXCM's public API endpoint
- Limited to available currency pairs and timeframes
- Subject to FXCM's data availability (some periods may be missing)
- Network dependent (requires internet connection)

### 5.2 Data Constraints
- M1 data: Weekly granularity (52 files per year)
- D1 data: Yearly granularity (1 file per year)
- Historical data may not be complete for all periods
- 404 errors indicate data unavailability (expected for some weeks/years)

### 5.3 Performance Constraints
- Rate limiting required to avoid overloading FXCM servers
- Large datasets may take hours to download
- Disk space required: Approximately 50-100 GB for full dataset

---

## 6. Assumptions

1. FXCM's public API remains accessible and stable
2. Data format (gzip-compressed CSV) remains consistent
3. Users have sufficient disk space for downloads
4. Users have reliable internet connection
5. Python 3.7+ is installed and available

---

## 7. Dependencies

### 7.1 Python Libraries
- `pandas`: CSV parsing and data manipulation
- `requests`: HTTP client for API calls
- `gzip`: Decompress downloaded files
- `logging`: Logging framework
- `argparse`: Command-line argument parsing
- `pathlib`: File system operations

### 7.2 External Services
- FXCM Public API: `https://candledata.fxcorporate.com`

---

## 8. Success Criteria

The FXCM Data Downloader v2.0 shall be considered successful if:

1. ✅ Downloads data for all 6 supported currency pairs
2. ✅ Supports both M1 and D1 timeframes
3. ✅ Creates proper directory structure automatically
4. ✅ Skips existing files correctly
5. ✅ Handles errors gracefully with retry mechanism
6. ✅ Generates comprehensive logs
7. ✅ Provides clear console output
8. ✅ Includes working batch file for Windows
9. ✅ All tests pass
10. ✅ Documentation is complete and accurate

---

## 9. Future Enhancements (Out of Scope for v2.0)

- Support for additional timeframes (H1, H4, etc.)
- Support for additional currency pairs
- GUI interface
- Progress bar for individual downloads
- Parallel downloads
- Data validation against database
- Automatic data updates (scheduled downloads)
- Email notifications on completion/failure

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-05  
**Status**: Final
