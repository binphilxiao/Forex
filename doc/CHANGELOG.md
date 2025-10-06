# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [5.1.2] - 2025-10-06

### Documentation
- Added doc/reference/database_schema.md describing the ClickHouse schema, table metadata, and aggregation views.
- Linked the schema reference from the documentation hub for quick discovery.

---

## [5.1.0] - 2025-10-06

### Added
- Documentation hub (`doc/README.md`) with a cleaned table of contents.
- New reference set: `doc/overview/`, `doc/workflows/`, `doc/reference/`, and `doc/operations/`.

### Changed
- Rewrote `README.md` and `QUICKSTART.md` to deliver a concise, accurate pipeline walkthrough.
- Replaced corrupted legacy manuals with lean Markdown written in UTF-8.
- Updated documentation links across the project to match the new structure.

### Removed
- Deleted deprecated `doc/guides/`, `doc/manual/`, `doc/design/`, `doc/development/`, and `doc/requirement/` directories.
- Dropped obsolete Markdown files whose names were mangled by encoding issues.

### Tooling
- Refreshed `scripts/verify_docs.py` messaging (UTF-8, clearer output) to support the new layout.

---

## [5.0.7] - 2025-10-06

### Changed
- Reworked `QUICKSTART.md` with end-to-end walkthroughs and 47 command examples covering `fxcm_data_downloader.py`, `fxcm_importer.py`, `m1_timeframe_converter.py`, and `verify_data_consistency.py`.
- Synced `README.md` and `doc/reference/SCRIPT_INDEX.md` to list eight core scripts and the v5.0.7 metadata.

### Removed
- Removed `scripts/generate_import_report.py`; import health checks now live in the main workflow.

### Documentation
- Added detailed flag tables, usage scenarios, and FAQs to help new users execute download -> import -> convert -> verify pipelines without guesswork.

---

## [5.0.6] - 2025-10-06

### Added
- Added `doc/guides/`, `doc/reference/`, and `doc/development/` folders to organise manuals, design notes, and reference material.
- Added `doc/guides/CONFIG_USAGE.md` describing how every ClickHouse-aware script reads `config/clickhouse_config.json`.
- Added `scripts/verify_docs.py` to lint documentation structure and report broken links.

### Changed
- Moved all documentation into the new `doc/` hierarchy; the repository root now keeps only `README.md`, `QUICKSTART.md`, and `requirements.txt`.
- Refreshed `QUICKSTART.md` to match the new structure and emphasise the core workflow.
- Updated `README.md` and `doc/reference/SCRIPT_INDEX.md` to version 5.0.6 and to point at the relocated files.

### Removed
- Removed `scripts/rebuild_clickhouse_tables.py`; schema rebuilds are now guided through the configurator workflow.

---

## [5.0.5] - 2025-10-06

### Added
- Added an "Import to Database" action to the web UI with a `/api/start_import` endpoint that launches `fxcm_importer.py`.

### Changed
- Simplified the web interface stack to the Flask app (`start_web.py` plus `flask_app.py`) and aligned the toolbar flow with the download -> import -> convert -> verify lifecycle.
- Updated `README.md` and `doc/reference/SCRIPT_INDEX.md` to reflect the ten core scripts and the new web workflow.

### Removed
- Removed legacy Streamlit front-ends (`scripts/fxcm_web_interface.py`, `scripts/fxcm_web_interface_simple.py`) and the `scripts/run_web_interface.py` launcher.
- Deleted `batch_import.bat`, `comprehensive_check.bat`, and `verify_data.bat` in favour of direct script usage.

---

## [5.0.4] - 2025-10-06

### Added
- Added `scripts/clickhouse_configurator.py`, an interactive wizard for generating and validating ClickHouse connection settings, alongside full requirements, design, and user manuals.

### Changed
- Moved the ClickHouse configuration file to `config/clickhouse_config.json` and updated every consumer to load it from the shared location.
- Updated Windows console handling to force UTF-8 output so multi-language logs render correctly.
- Refreshed `doc/reference/SCRIPT_INDEX.md` and `README.md` to describe the new tooling and reduced script counts.

### Removed
- Removed legacy importer and verification wrappers (`scripts/import_fxcm_to_clickhouse.py`, `scripts/batch_import_all.py`, `scripts/batch_import_m1.py`, `scripts/direct_import_m1.py`, `scripts/verify_all_data.py`, `scripts/verify_data_quality.py`, `scripts/check_data_completeness.py`, `scripts/comprehensive_check.py`) in favour of `fxcm_importer.py` and `verify_data_consistency.py`.
- Removed the dedicated unit test harness for the configurator (`scripts/test/test_clickhouse_configurator.py`) after the wizard stabilised.

---

## [5.0.3] - 2025-10-05

### Added
- Introduced `scripts/fxcm_importer.py` v2.0 with fast and comprehensive validation modes, ClickHouse integration, and automatic configuration loading.
- Added `scripts/test/test_fxcm_importer.py`, Windows launcher `import_fxcm_data.bat`, and dedicated requirements, design, manual, and README documentation for the importer.

### Changed
- Updated `README.md` and `doc/reference/SCRIPT_INDEX.md` to highlight the new importer and adjust script counts.

### Testing
- Added 15 importer unit tests covering both validation tiers; all pass.

---

## [5.0.2] - 2025-10-05

### Added
- **Dual Conversion Modes** for M1 Timeframe Converter
  - Local mode (default): CSV-based processing using pandas
  - Database mode: ClickHouse SQL aggregation for high performance
  - `--mode` parameter to switch between modes
- **Conditional ClickHouse Import**
  - Local mode no longer requires ClickHouse installation
  - Only pandas needed for local CSV processing
  - Clear error messages when ClickHouse is unavailable
- **New Documentation**
  - `doc/manual/m1_converter_modes.md`: dual-mode comparison guide
  - `doc/manual/m1_converter_quick_reference.md`: quick reference card
  - Updated README and user manual with mode examples

### Changed
- M1 Timeframe Converter v2.0 now supports two conversion strategies
- Default mode changed to "local" (CSV-based) for better accessibility
- ClickHouse is now an optional dependency (only needed for database mode)

### Fixed
- Resolved `ModuleNotFoundError` when running local mode without ClickHouse
- Improved error handling for missing dependencies
- Better separation of concerns between local and database processing

### Performance
- Local mode: about 190,000 M1 records per second
- Database mode: roughly 10x faster than local mode (SQL aggregation)
- Tested: converted 369,856 M1 records to 74,205 M5 in 1.9 seconds (local mode)

### Testing
- All 15 unit tests passing
- Local mode verified without ClickHouse installation
- Database mode remains backward compatible

---

## [5.0.1] - 2025-10-03

### Added
- M1 Timeframe Converter v2.0 complete rewrite
  - Command-line interface with argparse
  - ClickHouse integration for data storage
  - Support for M5, M15, M30, and H1 timeframes
  - Batch processing for all six currency pairs
  - Comprehensive logging and reporting

### Changed
- Default behaviour: skip existing data (`--overwrite` flag to force)
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
  - Automatic retry on failure (three attempts)
  - Skip existing files option
  - Comprehensive logging
  - HTML and text reports

### Changed
- Reorganised project structure
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
- Web interface for data visualisation
- Batch processing tools
- Consistency checking between CSV and database

---

**Version Format**: MAJOR.MINOR.PATCH

- **MAJOR**: Incompatible API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)


