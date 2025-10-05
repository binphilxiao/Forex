# Data Consistency Verification Tool - Requirements Document

**Project:** FXCM Data Management System  
**Component:** Data Consistency Verification Tool  
**Version:** 1.0.0  
**Date:** 2025-10-05  
**Author:** FXCM Data Team

---

## 1. Overview

### 1.1 Purpose
This document defines the functional and non-functional requirements for the FXCM Data Consistency Verification Tool, which verifies the integrity and consistency between local CSV data files and the ClickHouse database.

### 1.2 Scope
The tool will:
- Compare local CSV files with database records
- Support multiple verification modes
- Generate visual reports
- Provide structured output for programmatic use

---

## 2. Functional Requirements

### 2.1 Data Verification

#### FR-1: Symbol Selection
- **Requirement:** The system SHALL allow users to select specific currency pairs for verification
- **Default Behavior:** If no symbols are specified, verify all 6 supported pairs:
  - AUDUSD
  - EURUSD
  - GBPUSD
  - USDJPY
  - USDCAD
  - USDCHF
- **Priority:** HIGH
- **Acceptance Criteria:**
  - User can specify one or more symbols via command-line arguments
  - System validates symbol names against supported list
  - Invalid symbols are rejected with clear error messages

#### FR-2: Timeframe Selection
- **Requirement:** The system SHALL support verification of different timeframe data
- **Supported Timeframes:**
  - M1 (1-minute data)
  - D1 (daily data)
- **Default Behavior:** Verify both M1 and D1 data if not specified
- **Priority:** HIGH
- **Acceptance Criteria:**
  - User can select one or both timeframes
  - M1 and D1 data are processed independently
  - Results are segregated by timeframe

#### FR-3: Date Range Selection
- **Requirement:** The system SHALL allow users to specify a date range for verification
- **Default Behavior:** Verify data from 2015 to current year
- **Parameters:**
  - Start year (inclusive)
  - End year (inclusive)
- **Priority:** HIGH
- **Acceptance Criteria:**
  - User can specify custom start and end years
  - System validates year range (start <= end)
  - Years outside available data range generate warnings, not errors

### 2.2 Verification Modes

#### FR-4: Fast Verification Mode
- **Requirement:** The system SHALL support a fast verification mode
- **Behavior:**
  - Check only the first and last records of each CSV file
  - If both records exist in database with matching values, mark as consistent
  - If only one record exists or neither exists, mark accordingly
- **Use Case:** Quick overview of data completeness
- **Priority:** HIGH
- **Performance Target:** < 5 minutes for all data
- **Acceptance Criteria:**
  - Reads only first and last lines from each CSV
  - Executes only 1 database query per file
  - Completes full scan within performance target

#### FR-5: Comprehensive Verification Mode
- **Requirement:** The system SHALL support a comprehensive verification mode
- **Behavior:**
  - Check every record in CSV file against database
  - Compare all OHLCV values (Open, High, Low, Close, Volume)
  - Report detailed statistics (matched, missing, mismatched)
- **Use Case:** Detailed data quality audit
- **Priority:** MEDIUM
- **Performance Note:** May take significantly longer than fast mode
- **Acceptance Criteria:**
  - Verifies 100% of records in each file
  - Detects value mismatches with configurable tolerance (0.00001)
  - Provides detailed mismatch statistics

#### FR-6: Default Verification Mode
- **Requirement:** Fast mode SHALL be the default
- **Rationale:** Provides quick feedback for most common use cases
- **Priority:** LOW
- **Acceptance Criteria:**
  - Script runs in fast mode when no mode parameter specified
  - User can override with explicit mode selection

### 2.3 Data Status Classification

#### FR-7: Status Categories
- **Requirement:** The system SHALL classify each file into one of three status categories
- **Categories:**

1. **No Data (RED)**
   - CSV file does not exist, OR
   - CSV file is empty, OR
   - No matching records found in database
   
2. **Inconsistent (YELLOW)**
   - CSV file exists and has data, AND
   - Some but not all records match database, OR
   - Record values differ from database
   
3. **Consistent (GREEN)**
   - CSV file exists and has data, AND
   - All required records exist in database with matching values

- **Priority:** HIGH
- **Acceptance Criteria:**
  - Each verified file receives exactly one status
  - Status determination logic is clearly documented
  - Edge cases (empty files, corrupt data) are handled

### 2.4 Database Configuration

#### FR-8: Configurable Database Connection
- **Requirement:** The system SHALL support configurable database connections
- **Configuration Parameters:**
  - Host (default: 192.168.2.168)
  - HTTP Port (default: 8123)
  - Native Port (default: 9000)
  - Native Protocol Port (default: 9009)
  - Username (default: default)
  - Password
  - Database name (default: default)
- **Configuration Source:** JSON configuration file
- **Priority:** HIGH
- **Acceptance Criteria:**
  - Configuration loaded from external JSON file
  - Missing configuration values use documented defaults
  - Invalid configuration generates clear error messages
  - Connection failures are caught and reported

### 2.5 Report Generation

#### FR-9: HTML Report
- **Requirement:** The system SHALL generate an HTML report visualizing verification results
- **Report Features:**
  - Color-coded visualization (green/yellow/red)
  - Organized by symbol, timeframe, year, and week
  - Summary statistics (counts by status)
  - Metadata (timestamp, mode, configuration)
  - Responsive design for various screen sizes
- **Report Location:** logs/ directory
- **Naming Convention:** consistency_report_YYYYMMDD_HHMMSS.html
- **Priority:** HIGH
- **Acceptance Criteria:**
  - HTML file is valid and renders in modern browsers
  - All verification results are included
  - Colors match terminal output conventions
  - Report auto-opens in default browser (optional)

#### FR-10: Terminal Report
- **Requirement:** The system SHALL display a real-time report in the terminal
- **Display Features:**
  - Color-coded status indicators (ANSI colors)
  - Progress indicators during verification
  - Per-file status lines
  - Summary statistics at end
- **Color Scheme:**
  - Green (✅): Consistent
  - Yellow (⚠️): Inconsistent
  - Red (❌): No Data
- **Priority:** HIGH
- **Acceptance Criteria:**
  - Terminal output is readable and well-formatted
  - Colors work on Windows and Unix terminals
  - Progress updates appear in real-time
  - Summary matches HTML report statistics

#### FR-11: Report Storage
- **Requirement:** All reports SHALL be saved in the logs/ directory
- **File Management:**
  - Create logs/ directory if it doesn't exist
  - Use timestamp-based filenames to avoid overwrites
  - No automatic cleanup of old reports
- **Priority:** MEDIUM
- **Acceptance Criteria:**
  - Reports persist after script completion
  - Filenames are sortable by date
  - Directory creation is automatic

### 2.6 Programmatic Interface

#### FR-12: Structured Return Data
- **Requirement:** The system SHALL return verification results as structured data
- **Data Structure:** List of dictionaries, each containing:
  - `symbol`: Currency pair (string)
  - `timeframe`: 'M1' or 'D1' (string)
  - `year`: Year number (integer)
  - `week`: Week number for M1, 0 for D1 (integer)
  - `file`: Full path to CSV file (string)
  - `status`: Status category (string: 'no_data', 'inconsistent', 'consistent')
  - `details`: Additional information (dictionary)
- **Use Case:** Integration with other scripts, automated testing
- **Priority:** MEDIUM
- **Acceptance Criteria:**
  - Return value is a Python list
  - Each element follows documented schema
  - Data is JSON-serializable
  - Empty list returned if no files found

---

## 3. Non-Functional Requirements

### 3.1 Performance

#### NFR-1: Fast Mode Performance
- **Requirement:** Fast mode SHALL complete verification of all data within 5 minutes
- **Context:** Approximately 300+ files across all symbols and timeframes
- **Priority:** HIGH

#### NFR-2: Memory Efficiency
- **Requirement:** The system SHALL not load entire datasets into memory
- **Approach:** Stream processing, file-by-file verification
- **Priority:** MEDIUM

#### NFR-3: Database Load
- **Requirement:** The system SHALL minimize database load
- **Approach:** Batch queries, efficient SQL, connection reuse
- **Priority:** MEDIUM

### 3.2 Usability

#### NFR-4: Command-Line Interface
- **Requirement:** The system SHALL provide an intuitive CLI
- **Features:**
  - Clear help documentation (--help)
  - Sensible defaults
  - Meaningful error messages
  - Examples in help text
- **Priority:** HIGH

#### NFR-5: Windows Batch File
- **Requirement:** A Windows .bat file SHALL be provided for easy execution
- **Features:**
  - Double-click execution
  - Basic parameter support
  - Clear console output
- **Priority:** HIGH

#### NFR-6: Documentation
- **Requirement:** Comprehensive documentation SHALL be provided
- **Required Documents:**
  - Requirements specification (this document)
  - Design documentation
  - User manual with examples
- **Priority:** HIGH

### 3.3 Reliability

#### NFR-7: Error Handling
- **Requirement:** The system SHALL handle errors gracefully
- **Error Categories:**
  - Configuration errors
  - Database connection errors
  - File I/O errors
  - Data parsing errors
- **Behavior:** Log errors, continue processing remaining files when possible
- **Priority:** HIGH

#### NFR-8: Data Integrity
- **Requirement:** The system SHALL NOT modify any data
- **Behavior:** Read-only operations on CSV files and database
- **Priority:** CRITICAL

### 3.4 Compatibility

#### NFR-9: Platform Support
- **Primary Platform:** Windows 10/11
- **Secondary Platform:** Linux (Ubuntu/CentOS)
- **Python Version:** 3.7+
- **Priority:** HIGH

#### NFR-10: Database Compatibility
- **Requirement:** Support ClickHouse 20.x and later
- **Communication:** HTTP interface (port 8123)
- **Priority:** HIGH

---

## 4. Dependencies

### 4.1 External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.7+ | Runtime environment |
| pandas | Latest | CSV file processing |
| requests | Latest | HTTP communication with ClickHouse |
| ClickHouse | 20.x+ | Database system |

### 4.2 Internal Dependencies

| Component | Purpose |
|-----------|---------|
| config/clickhouse_config.json | Database configuration |
| fxcm_data/ | CSV data files |
| logs/ | Report output directory |

---

## 5. User Stories

### US-1: Quick Health Check
**As a** data administrator  
**I want to** quickly verify all data is in the database  
**So that** I can confirm daily imports were successful

**Acceptance Criteria:**
- Run script without parameters
- Get results within 5 minutes
- See clear summary of any issues

### US-2: Deep Dive Investigation
**As a** data quality analyst  
**I want to** perform detailed verification of specific data  
**So that** I can investigate reported discrepancies

**Acceptance Criteria:**
- Select specific symbol and date range
- Use comprehensive mode
- Get detailed mismatch information

### US-3: Visual Report Review
**As a** project manager  
**I want to** view a visual report of data completeness  
**So that** I can assess overall data quality at a glance

**Acceptance Criteria:**
- HTML report auto-opens in browser
- Color-coded calendar view
- Clear summary statistics

### US-4: Automated Integration
**As a** DevOps engineer  
**I want to** integrate verification into automated pipelines  
**So that** data quality is continuously monitored

**Acceptance Criteria:**
- Script returns structured data
- Exit code indicates success/failure
- Results are programmatically accessible

---

## 6. Success Criteria

The tool is considered successful if:

1. ✅ All functional requirements (FR-1 through FR-12) are implemented
2. ✅ Performance targets are met (NFR-1)
3. ✅ Complete documentation suite is provided (NFR-6)
4. ✅ Tool successfully verifies 100% of existing data files
5. ✅ HTML and terminal reports are accurate and readable
6. ✅ No data corruption or modification occurs during verification
7. ✅ All automated tests pass

---

## 7. Future Enhancements (Out of Scope for v1.0)

The following features are documented for potential future versions:

- **FE-1:** Email notification of verification results
- **FE-2:** Automatic remediation (re-import missing/inconsistent data)
- **FE-3:** Trend analysis across multiple verification runs
- **FE-4:** Web-based dashboard for historical results
- **FE-5:** Multi-threaded/parallel verification for improved performance
- **FE-6:** Support for additional data sources beyond CSV
- **FE-7:** Detailed value-level diff reports (showing exact differences)
- **FE-8:** Integration with monitoring systems (Prometheus, Grafana)

---

## 8. Glossary

| Term | Definition |
|------|------------|
| Consistency | State where CSV file data exactly matches database records |
| Fast Mode | Verification method checking only first and last records |
| Comprehensive Mode | Verification method checking all records |
| OHLCV | Open, High, Low, Close, Volume - standard candlestick data |
| M1 | 1-minute timeframe data |
| D1 | Daily timeframe data |
| Status | Classification of verification result (no_data, inconsistent, consistent) |

---

## 9. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-10-05 | FXCM Data Team | Initial requirements document |

---

**Document Status:** APPROVED  
**Next Review Date:** 2025-11-05
