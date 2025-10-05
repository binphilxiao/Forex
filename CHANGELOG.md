# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [5.0.2] - 2025-10-05

### Added
- **Dual Conversion Modes** for M1 Timeframe Converter
  - Local Mode (default): CSV-based processing using pandas
  - Database Mode: ClickHouse SQL aggregation for high performance
  - `--mode` parameter to switch between modes
- **Conditional ClickHouse Import**
  - Local mode no longer requires ClickHouse installation
  - Only pandas needed for local CSV processing
  - Clear error messages when ClickHouse unavailable
- **New Documentation**
  - `doc/manual/m1_converter_modes.md`: Comprehensive dual-mode comparison guide
  - `doc/manual/m1_converter_quick_reference.md`: Quick reference card
  - Updated README and user manual with mode examples

### Changed
- M1 Timeframe Converter v2.0 now supports two conversion strategies
- Default mode changed to 'local' (CSV-based) for better accessibility
- ClickHouse is now optional dependency (only needed for database mode)

### Fixed
- ModuleNotFoundError when running local mode without ClickHouse
- Improved error handling for missing dependencies
- Better separation of concerns between local and database processing

### Performance
- Local mode: ~190,000 M1 records/second
- Database mode: ~10x faster than local mode (SQL aggregation)
- Tested: 369,856 M1 → 74,205 M5 in 1.9 seconds (local mode)

### Testing
- All 15 unit tests passing
- Local mode verified without ClickHouse installation
- Database mode backward compatible

---

## [5.0.1] - 2025-10-03

### Added
- M1 Timeframe Converter v2.0 complete rewrite
  - Command-line interface with argparse
  - ClickHouse integration for data storage
  - Support for M5, M15, M30, H1 timeframes
  - Batch processing for all 6 currency pairs
  - Comprehensive logging and reporting

### Changed
- Default behavior: Skip existing data (--overwrite flag to force)
- Improved OHLC aggregation algorithm
- Enhanced error handling and retry logic

### Documentation
- Complete requirements specification
- Detailed design documentation
- User manual with examples
- 15 test cases with full coverage

---

## [5.0.0] - 2025-10-02

### Added
- FXCM Data Downloader v2.0
  - Command-line parameters for flexible configuration
  - Automatic retry on failure (3 attempts)
  - Skip existing files option
  - Comprehensive logging
  - HTML and text reports

### Changed
- Reorganized project structure
- All scripts moved to `scripts/` directory
- Tests moved to `scripts/test/` subdirectory

### Documentation
- Created `SCRIPT_INDEX.md` for easy script navigation
- Updated README files for all major components
- Added batch file launchers for common tasks

---

## [4.0.0] - Previous

### Features
- CSV data import to ClickHouse
- Data verification and quality checks
- Web interface for data visualization
- Batch processing tools
- Consistency checking between CSV and database

---

**Version Format**: MAJOR.MINOR.PATCH

- **MAJOR**: Incompatible API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)
