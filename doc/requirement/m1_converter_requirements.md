# M1 Timeframe Converter - Requirements Specification

**Version:** 2.0.0  
**Author:** binphilxiao  
**Date:** 2025-10-05  
**Status:** Approved

---

## 1. Overview

### 1.1 Purpose
The M1 Timeframe Converter is a Python-based tool designed to aggregate 1-minute (M1) forex market data into higher timeframes (M5, M15, M30, H1) and store the results in a ClickHouse database. This tool enables efficient generation of multi-timeframe datasets from granular M1 data for forex trading analysis and backtesting.

### 1.2 Scope
- Convert M1 forex data to M5, M15, M30, and H1 timeframes
- Support 6 major currency pairs (EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF)
- Store aggregated data in ClickHouse database
- Provide flexible command-line interface for selective conversion
- Generate detailed conversion reports and logs

### 1.3 Target Users
- Forex traders requiring multi-timeframe analysis
- Quantitative analysts building trading strategies
- Data engineers managing forex data pipelines
- Researchers analyzing forex market behavior

---

## 2. Functional Requirements

### FR-1: M1 Data Reading
**Priority:** High  
**Description:** The system shall read M1 data from ClickHouse database.

**Acceptance Criteria:**
- Read M1 data for specified currency pairs
- Filter data by year range
- Handle missing data gracefully
- Support large datasets (millions of records)
- Validate data format and completeness

### FR-2: Timeframe Aggregation
**Priority:** High  
**Description:** The system shall aggregate M1 data to higher timeframes using OHLC aggregation rules.

**Acceptance Criteria:**
- Support M5 (5-minute) aggregation
- Support M15 (15-minute) aggregation
- Support M30 (30-minute) aggregation
- Support H1 (1-hour) aggregation
- Apply correct OHLC aggregation:
  - **Open:** First M1 open in period
  - **High:** Maximum M1 high in period
  - **Low:** Minimum M1 low in period
  - **Close:** Last M1 close in period
- Preserve timestamp accuracy
- Handle partial periods correctly

### FR-3: ClickHouse Integration
**Priority:** High  
**Description:** The system shall integrate with ClickHouse database for data storage.

**Acceptance Criteria:**
- Connect to ClickHouse server via HTTP protocol
- Support configurable host, port, username, password
- Create tables automatically if they don't exist
- Use efficient table schema (MergeTree engine, DateTime ordering)
- Insert data in batches for performance
- Handle connection errors gracefully

### FR-4: Currency Pair Selection
**Priority:** High  
**Description:** The system shall allow users to select which currency pairs to convert.

**Acceptance Criteria:**
- Support command-line parameter `--pairs`
- Accept one or more pairs: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF
- Default: Process all 6 pairs
- Validate pair names
- Provide clear error messages for invalid pairs

### FR-5: Timeframe Selection
**Priority:** High  
**Description:** The system shall allow users to select which timeframes to generate.

**Acceptance Criteria:**
- Support command-line parameter `--timeframes`
- Accept one or more timeframes: M5, M15, M30, H1
- Default: Generate all 4 timeframes
- Validate timeframe names
- Provide clear error messages for invalid timeframes

### FR-6: Date Range Selection
**Priority:** High  
**Description:** The system shall allow users to specify date range for conversion.

**Acceptance Criteria:**
- Support `--start-year` parameter (default: 2015)
- Support `--end-year` parameter (default: current year)
- Validate year range (start <= end)
- Process data year by year
- Handle partial years correctly

### FR-7: Overwrite vs Skip Mode
**Priority:** High  
**Description:** The system shall support two modes for handling existing data.

**Acceptance Criteria:**
- **Overwrite mode (default):** Replace existing data
- **Skip mode:** Skip years with existing data
- Command-line flag `--skip-existing` to enable skip mode
- Check for existing data before processing
- Report skipped items in logs

### FR-8: Progress Reporting
**Priority:** Medium  
**Description:** The system shall provide real-time progress information.

**Acceptance Criteria:**
- Display current pair being processed
- Display current year being processed
- Display current timeframe being generated
- Show record counts (read/written)
- Display elapsed time
- Show completion percentage

### FR-9: Logging
**Priority:** High  
**Description:** The system shall maintain detailed logs of all operations.

**Acceptance Criteria:**
- Create timestamped log files in `logs/` directory
- Log file naming: `m1_converter_YYYYMMDD_HHMMSS.log`
- Log levels: INFO, WARNING, ERROR
- Include timestamps in log entries
- Log to both file and console
- UTF-8 encoding support

### FR-10: Report Generation
**Priority:** Medium  
**Description:** The system shall generate summary reports after conversion.

**Acceptance Criteria:**
- Create report file in `logs/` directory
- Report naming: `m1_converter_report_YYYYMMDD_HHMMSS.txt`
- Include conversion statistics:
  - Pairs processed
  - Timeframes generated
  - Records read (M1)
  - Records written
  - Skipped items
  - Errors encountered
  - Total processing time
- Include start/end timestamps
- UTF-8 encoding support

### FR-11: Error Handling
**Priority:** High  
**Description:** The system shall handle errors gracefully without data corruption.

**Acceptance Criteria:**
- Catch and log all exceptions
- Continue processing remaining items after error
- Track error count
- Provide meaningful error messages
- Clean up resources on failure
- Close database connections properly

### FR-12: Command-Line Interface
**Priority:** High  
**Description:** The system shall provide user-friendly command-line interface.

**Acceptance Criteria:**
- Use argparse for parameter parsing
- Provide help text (`--help`)
- Include usage examples in help
- Support both short and long parameter formats
- Provide default values for all parameters
- Validate parameter combinations

---

## 3. Non-Functional Requirements

### NFR-1: Performance
**Priority:** High  
**Description:** The system shall process data efficiently.

**Acceptance Criteria:**
- Process at least 1 million M1 records per minute
- Use batch inserts to ClickHouse (minimize round trips)
- Minimize memory usage via pandas chunking
- Support parallel processing where applicable

### NFR-2: Scalability
**Priority:** Medium  
**Description:** The system shall handle large datasets.

**Acceptance Criteria:**
- Process years of data (hundreds of millions of records)
- Handle multiple currency pairs concurrently
- Scale to additional pairs without code changes
- Support data growth over time

### NFR-3: Reliability
**Priority:** High  
**Description:** The system shall operate reliably.

**Acceptance Criteria:**
- Data integrity: No data loss during aggregation
- Accurate OHLC calculations
- Consistent timestamp handling
- Idempotent operations (safe to re-run)

### NFR-4: Maintainability
**Priority:** High  
**Description:** The system shall be easy to maintain and extend.

**Acceptance Criteria:**
- Clean, well-documented code
- Modular design (separation of concerns)
- Comprehensive test coverage
- Clear error messages
- Configuration via parameters (no hardcoded values)

### NFR-5: Usability
**Priority:** Medium  
**Description:** The system shall be easy to use.

**Acceptance Criteria:**
- Simple command-line syntax
- Sensible defaults
- Clear progress indicators
- Helpful error messages
- Windows batch file launcher

### NFR-6: Portability
**Priority:** Medium  
**Description:** The system shall run on multiple platforms.

**Acceptance Criteria:**
- Support Windows, Linux, macOS
- Python 3.7+ compatibility
- No platform-specific dependencies
- Handle path separators correctly

### NFR-7: Documentation
**Priority:** High  
**Description:** The system shall be well-documented.

**Acceptance Criteria:**
- Requirements specification (this document)
- Design documentation
- User manual
- API documentation (docstrings)
- Usage examples
- README file

### NFR-8: Testing
**Priority:** High  
**Description:** The system shall have comprehensive test coverage.

**Acceptance Criteria:**
- Unit tests for all core functions
- Test aggregation logic
- Test edge cases (empty data, partial periods)
- Test error handling
- Minimum 80% code coverage

### NFR-9: Security
**Priority:** Medium  
**Description:** The system shall handle credentials securely.

**Acceptance Criteria:**
- Support ClickHouse authentication
- No passwords in code or logs
- Use environment variables or parameters for credentials
- Secure database connections

### NFR-10: Monitoring
**Priority:** Low  
**Description:** The system shall provide monitoring capabilities.

**Acceptance Criteria:**
- Log all operations
- Track processing statistics
- Report errors and warnings
- Generate summary reports

---

## 4. Data Requirements

### DR-1: Input Data Format
**Source:** ClickHouse table `forex_{pair}_m1`  
**Schema:**
```
DateTime: DateTime
Open: Float64
High: Float64
Low: Float64
Close: Float64
```

### DR-2: Output Data Format
**Target:** ClickHouse table `forex_{pair}_{timeframe}`  
**Schema:**
```
DateTime: DateTime
Open: Float64
High: Float64
Low: Float64
Close: Float64
```

### DR-3: Supported Currency Pairs
- EURUSD
- GBPUSD
- USDJPY
- AUDUSD
- USDCAD
- USDCHF

### DR-4: Supported Timeframes
- M5: 5 minutes
- M15: 15 minutes
- M30: 30 minutes
- H1: 60 minutes

---

## 5. Interface Requirements

### IR-1: Command-Line Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--pairs` | list | All pairs | No | Currency pairs to convert |
| `--timeframes` | list | All TFs | No | Timeframes to generate |
| `--start-year` | int | 2015 | No | Start year |
| `--end-year` | int | Current year | No | End year |
| `--skip-existing` | flag | False | No | Skip existing data |
| `--ch-host` | str | 192.168.2.168 | No | ClickHouse host |
| `--ch-port` | int | 8123 | No | ClickHouse HTTP port |
| `--ch-user` | str | default | No | ClickHouse username |
| `--ch-password` | str | (empty) | No | ClickHouse password |

### IR-2: ClickHouse Database

**Connection:**
- Protocol: HTTP
- Default Host: 192.168.2.168
- Default Port: 8123
- Authentication: Username/password

**Tables:**
- Naming: `forex_{pair}_{timeframe}`
- Engine: MergeTree
- Ordering: DateTime
- Auto-creation: Yes

---

## 6. User Stories

### US-1: Convert All Data
**As a** forex analyst  
**I want to** convert all M1 data to all higher timeframes  
**So that** I have complete multi-timeframe datasets for analysis

**Acceptance:**
- Run: `python m1_timeframe_converter.py`
- All 6 pairs processed
- All 4 timeframes generated
- All years (2015-current) converted

### US-2: Convert Specific Pair
**As a** trader  
**I want to** convert only EURUSD data  
**So that** I can quickly analyze this pair

**Acceptance:**
- Run: `python m1_timeframe_converter.py --pairs EURUSD`
- Only EURUSD processed
- All timeframes generated
- Other pairs skipped

### US-3: Convert Recent Years
**As a** researcher  
**I want to** convert only recent years (2020-2023)  
**So that** I can focus on modern market behavior

**Acceptance:**
- Run: `python m1_timeframe_converter.py --start-year 2020 --end-year 2023`
- Only years 2020-2023 processed
- All pairs and timeframes included

### US-4: Skip Existing Data
**As a** data engineer  
**I want to** skip years that are already converted  
**So that** I don't waste time re-processing

**Acceptance:**
- Run: `python m1_timeframe_converter.py --skip-existing`
- Check for existing data before processing
- Skip years with complete data
- Log skipped items

### US-5: Generate Specific Timeframes
**As a** strategy developer  
**I want to** generate only H1 data  
**So that** I can test my hourly strategy

**Acceptance:**
- Run: `python m1_timeframe_converter.py --timeframes H1`
- Only H1 timeframe generated
- All pairs processed

---

## 7. Constraints

### C-1: Technical Constraints
- Python 3.7 or higher required
- ClickHouse database must be accessible
- M1 source data must exist
- Sufficient disk space for output data
- Network connectivity to ClickHouse server

### C-2: Data Constraints
- M1 data must be clean (no duplicates, proper OHLC values)
- DateTime must be continuous (1-minute intervals)
- All prices must be positive numbers
- Data must be ordered by DateTime

### C-3: Performance Constraints
- Processing time proportional to data volume
- Memory usage limited by available RAM
- Network bandwidth affects ClickHouse operations

---

## 8. Assumptions

1. M1 source data is already loaded in ClickHouse
2. ClickHouse server is running and accessible
3. User has appropriate database permissions
4. System has Python 3.7+ installed
5. Required Python packages are installed (pandas, clickhouse-connect)
6. Sufficient disk space for logs and reports

---

## 9. Dependencies

### Software Dependencies
- Python 3.7+
- pandas >= 1.3.0
- clickhouse-connect >= 0.6.0

### External Systems
- ClickHouse database server
- Network access to ClickHouse

### Data Dependencies
- M1 source data in ClickHouse tables

---

## 10. Success Criteria

The M1 Timeframe Converter v2.0 will be considered successful if:

1. ✅ All 6 currency pairs can be converted
2. ✅ All 4 timeframes (M5, M15, M30, H1) are generated correctly
3. ✅ OHLC aggregation is mathematically accurate
4. ✅ Command-line interface works as specified
5. ✅ ClickHouse integration is functional
6. ✅ Skip and overwrite modes work correctly
7. ✅ Logs and reports are generated
8. ✅ All tests pass
9. ✅ Documentation is complete
10. ✅ Performance meets requirements (>1M records/minute)

---

## 11. Future Enhancements

### Phase 2 (Future)
- Support for additional currency pairs
- Support for D1 (daily) timeframe generation
- Parallel processing of multiple pairs
- Resume capability after interruption
- Data validation and quality checks
- Web-based monitoring dashboard
- Email notifications on completion/errors
- Support for other data sources (CSV, PostgreSQL)

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-10-05 | binphilxiao | Initial requirements specification |
| 2.0.0 | 2025-10-05 | binphilxiao | Complete rewrite with ClickHouse integration |

---

**Approval:**  
☑ Requirements Approved  
☑ Ready for Design Phase
