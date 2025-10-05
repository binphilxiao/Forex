# Data Consistency Verification Tool - User Manual

**Project:** FXCM Data Management System  
**Component:** Data Consistency Verification Tool  
**Version:** 1.0.0  
**Date:** 2025-10-05  
**Author:** FXCM Data Team

---

## Table of Contents

1. [Quick Start](#1-quick-start)
2. [Installation](#2-installation)
3. [Basic Usage](#3-basic-usage)
4. [Advanced Usage](#4-advanced-usage)
5. [Understanding Reports](#5-understanding-reports)
6. [Verification Modes](#6-verification-modes)
7. [Command-Line Options](#7-command-line-options)
8. [Use Cases](#8-use-cases)
9. [Troubleshooting](#9-troubleshooting)
10. [Best Practices](#10-best-practices)
11. [FAQ](#11-faq)

---

## 1. Quick Start

### 1.1 Windows Users (Easiest)

Double-click the batch file:
```
verify_consistency.bat
```

That's it! The tool will:
- ✅ Check all currency pairs (EURUSD, GBPUSD, USDJPY, USDCAD, USDCHF, AUDUSD)
- ✅ Check both M1 and D1 data
- ✅ Check data from 2015 to present
- ✅ Use fast mode (5 minutes)
- ✅ Generate an HTML report
- ✅ Open the report in your browser

### 1.2 Command Line Users

```bash
cd C:\Users\abing\OneDrive\Desktop\Forex
python scripts\verify_data_consistency.py
```

### 1.3 What to Expect

**Terminal Output:**
```
================================================================================
  🔍 FXCM Data Consistency Verification
================================================================================
Mode: FAST
Symbols: AUDUSD, EURUSD, GBPUSD, USDJPY, USDCAD, USDCHF
Timeframes: M1, D1
Period: 2015 - 2025
================================================================================

📊 Checking EURUSD M1...
  ✅ EURUSD M1 2015 Week-01           CONSISTENT
  ✅ EURUSD M1 2015 Week-02           CONSISTENT
  ⚠️  EURUSD M1 2015 Week-03           INCONSISTENT
  ...
```

**HTML Report:**
- Automatically opens in your default browser
- Color-coded calendar view
- Summary statistics
- Saved in `logs/consistency_report_[timestamp].html`

---

## 2. Installation

### 2.1 Prerequisites

- **Python:** Version 3.7 or higher
- **Operating System:** Windows 10/11, Linux, or macOS
- **Network Access:** Connection to ClickHouse database
- **Disk Space:** 10 MB for script, 100 MB for reports

### 2.2 Check Python Version

```bash
python --version
```

Expected output: `Python 3.7.x` or higher

### 2.3 Install Dependencies

```bash
pip install pandas requests
```

Or using requirements file (if available):
```bash
pip install -r requirements.txt
```

### 2.4 Verify Installation

Run the test suite:
```bash
python scripts\test\test_verify_consistency.py
```

Expected output:
```
✅ PASSED - Basic Functionality
✅ PASSED - Fast Mode Verification
...
Total: 5/5 tests passed (100.0%)
```

### 2.5 Configure Database Connection

Edit `config/clickhouse_config.json`:

```json
{
    "host": "192.168.2.168",
    "http_port": 8123,
    "port": 9000,
    "native_port": 9009,
    "user": "default",
    "password": "yourStrongPassword",
    "database": "default"
}
```

**Important:** Keep this file secure - it contains your database password!

---

## 3. Basic Usage

### 3.1 Check All Data (Default)

```bash
python scripts\verify_data_consistency.py
```

This checks:
- All 6 currency pairs
- Both M1 and D1 timeframes
- Years 2015 to current year
- Fast mode (boundary checks only)

**Time:** ~5 minutes  
**Output:** Terminal + HTML report

### 3.2 Check Specific Symbol

```bash
python scripts\verify_data_consistency.py --symbols EURUSD
```

Only checks EURUSD data.

### 3.3 Check Multiple Symbols

```bash
python scripts\verify_data_consistency.py --symbols EURUSD GBPUSD USDJPY
```

### 3.4 Check Specific Timeframe

```bash
# Only M1 data
python scripts\verify_data_consistency.py --timeframes M1

# Only D1 data
python scripts\verify_data_consistency.py --timeframes D1
```

### 3.5 Check Specific Year Range

```bash
# Only 2020-2023
python scripts\verify_data_consistency.py --start-year 2020 --end-year 2023

# Only 2025
python scripts\verify_data_consistency.py --start-year 2025 --end-year 2025
```

### 3.6 Comprehensive Mode

```bash
python scripts\verify_data_consistency.py --mode comprehensive
```

**Warning:** This is much slower (hours instead of minutes) but more accurate.

---

## 4. Advanced Usage

### 4.1 Combine Multiple Options

```bash
# Check EURUSD M1 data for 2024 in comprehensive mode
python scripts\verify_data_consistency.py \
    --symbols EURUSD \
    --timeframes M1 \
    --start-year 2024 \
    --end-year 2024 \
    --mode comprehensive
```

### 4.2 Custom Configuration File

```bash
python scripts\verify_data_consistency.py --config path/to/custom_config.json
```

### 4.3 Custom Output Path

```bash
python scripts\verify_data_consistency.py --output my_custom_report.html
```

### 4.4 Skip HTML Report

```bash
python scripts\verify_data_consistency.py --no-html
```

Only shows terminal output, no HTML file generated.

### 4.5 Programmatic Usage (Python)

```python
from scripts.verify_data_consistency import DataConsistencyChecker

# Create checker
checker = DataConsistencyChecker(mode='fast')

# Run verification
results = checker.verify_data(
    symbols=['EURUSD', 'GBPUSD'],
    timeframes=['M1'],
    start_year=2024,
    end_year=2024
)

# Process results
for result in results:
    print(f"{result['symbol']} {result['year']} Week {result['week']}: {result['status']}")

# Generate report
checker.generate_html_report('my_report.html')
```

---

## 5. Understanding Reports

### 5.1 Terminal Report

#### Status Indicators

| Icon | Color | Status | Meaning |
|------|-------|--------|---------|
| ✅ | Green | CONSISTENT | CSV data matches database perfectly |
| ⚠️ | Yellow | INCONSISTENT | CSV exists but data doesn't match DB |
| ❌ | Red | NO DATA | CSV file missing or not in database |

#### Example Terminal Output

```
📊 Checking EURUSD M1...
  ✅ EURUSD M1 2015 Week-01           CONSISTENT
  ✅ EURUSD M1 2015 Week-02           CONSISTENT
  ⚠️  EURUSD M1 2015 Week-03           INCONSISTENT
  ❌ EURUSD M1 2015 Week-04           NO DATA
```

#### Summary Statistics

```
================================================================================
  📋 Verification Summary
================================================================================
Total files checked: 300
✅ Consistent:    250 ( 83.3%)  ← Good! Most data is correct
⚠️  Inconsistent:   30 ( 10.0%)  ← Needs investigation
❌ No data:        20 (  6.7%)  ← Missing files or not imported
================================================================================
```

### 5.2 HTML Report

#### Header Section

Shows:
- Report title
- Generation timestamp
- Verification mode used

#### Statistics Boxes

Four color-coded boxes showing:
1. **Consistent** (green) - Files that match perfectly
2. **Inconsistent** (yellow) - Files with data mismatches
3. **No Data** (red) - Missing or empty files
4. **Total Files** (blue) - Total files checked

#### Symbol Sections

Each currency pair has its own section with:

**M1 Data:**
- Year-by-year view
- 52 cells representing weeks
- Hover over cell to see details

**D1 Data:**
- Year-by-year view
- One cell per year (full year file)

#### Color Legend

At the bottom of the report:
- 🟢 Green = Consistent
- 🟡 Yellow = Inconsistent
- 🔴 Red = No Data

#### Interactive Features

- **Hover:** Shows tooltip with file details
- **Visual Scanning:** Quickly spot problem areas (red/yellow)
- **Week Numbers:** Click to see which weeks have issues

### 5.3 Report Location

Reports are saved in:
```
logs/consistency_report_YYYYMMDD_HHMMSS.html
```

Example:
```
logs/consistency_report_20251005_143022.html
```

The timestamp ensures each report has a unique name.

---

## 6. Verification Modes

### 6.1 Fast Mode (Default)

**How it works:**
1. Read first line of CSV file
2. Read last line of CSV file
3. Check if both timestamps exist in database
4. If both exist → CONSISTENT
5. If only one exists → INCONSISTENT
6. If neither exists → NO DATA

**Advantages:**
- ⚡ Very fast (~5 minutes for all data)
- 💾 Low memory usage
- 🎯 Good for daily health checks

**Limitations:**
- ❌ Doesn't check middle records
- ❌ Might miss data gaps
- ❌ Assumes if boundaries exist, middle is correct

**Best for:**
- Daily/weekly routine checks
- Quick health assessment
- After bulk imports

**Example:**
```bash
python scripts\verify_data_consistency.py
# or
python scripts\verify_data_consistency.py --mode fast
```

### 6.2 Comprehensive Mode

**How it works:**
1. Read entire CSV file
2. Query all corresponding records from database
3. Compare every single record
4. Check all values (open, high, low, close, volume)
5. Report detailed statistics

**Advantages:**
- ✅ 100% accurate
- 📊 Detailed mismatch information
- 🔍 Finds all inconsistencies

**Limitations:**
- 🐌 Very slow (~3-5 hours for all data)
- 💾 High memory usage
- 🌐 Heavy network usage

**Best for:**
- Detailed investigations
- Before critical operations
- After suspected data corruption
- Compliance audits

**Example:**
```bash
python scripts\verify_data_consistency.py --mode comprehensive
# or
verify_consistency.bat comprehensive
```

### 6.3 Mode Comparison

| Aspect | Fast Mode | Comprehensive Mode |
|--------|-----------|-------------------|
| Time (all data) | ~5 minutes | ~3-5 hours |
| Memory | ~200 MB | ~500 MB |
| Network | ~1.5 MB | ~15 GB |
| Accuracy | ~95% | 100% |
| Records checked | 2 per file | All records |
| Best use | Daily checks | Deep audits |

### 6.4 Choosing the Right Mode

**Use Fast Mode when:**
- ✅ You need quick feedback
- ✅ Checking recently imported data
- ✅ Running automated daily checks
- ✅ Database is remote (slow network)

**Use Comprehensive Mode when:**
- ✅ Investigating specific issues
- ✅ After manual data modifications
- ✅ Quarterly/annual audits
- ✅ Compliance requirements
- ✅ Fast mode shows inconsistencies

---

## 7. Command-Line Options

### 7.1 Complete Option List

```bash
python scripts\verify_data_consistency.py [OPTIONS]
```

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--symbols` | | list | All 6 pairs | Currency pairs to check |
| `--timeframes` | | list | M1, D1 | Timeframes to check |
| `--start-year` | | int | 2015 | Start year (inclusive) |
| `--end-year` | | int | Current | End year (inclusive) |
| `--mode` | | choice | fast | Verification mode (fast/comprehensive) |
| `--config` | | path | config/clickhouse_config.json | Config file path |
| `--output` | | path | Auto | HTML report output path |
| `--no-html` | | flag | False | Skip HTML report generation |
| `--help` | `-h` | flag | | Show help message |

### 7.2 Option Details

#### --symbols

Specify one or more currency pairs:
```bash
--symbols EURUSD
--symbols EURUSD GBPUSD USDJPY
```

Valid symbols:
- AUDUSD
- EURUSD
- GBPUSD
- USDJPY
- USDCAD
- USDCHF

#### --timeframes

Specify one or both timeframes:
```bash
--timeframes M1
--timeframes D1
--timeframes M1 D1
```

#### --start-year / --end-year

Specify year range:
```bash
--start-year 2020 --end-year 2023
```

Notes:
- Both years are inclusive
- Start must be ≤ end
- Years outside available data generate warnings

#### --mode

Choose verification mode:
```bash
--mode fast          # Quick boundary checks
--mode comprehensive # Check all records
```

#### --config

Use custom configuration file:
```bash
--config /path/to/custom_config.json
```

Config file must contain:
```json
{
    "host": "hostname",
    "http_port": 8123,
    "user": "username",
    "password": "password",
    "database": "database_name"
}
```

#### --output

Specify custom output path:
```bash
--output reports/my_report.html
--output C:\Reports\verification_2024.html
```

#### --no-html

Skip HTML report generation:
```bash
--no-html
```

Useful for:
- Automated scripts that only need exit code
- Terminal-only environments
- Quick checks where report isn't needed

### 7.3 Help Command

```bash
python scripts\verify_data_consistency.py --help
```

Shows:
- All available options
- Usage examples
- Default values

---

## 8. Use Cases

### 8.1 Daily Health Check

**Scenario:** You want to verify yesterday's data import was successful.

**Solution:**
```bash
# Check only current year, fast mode
python scripts\verify_data_consistency.py \
    --start-year 2025 \
    --end-year 2025 \
    --mode fast
```

**Time:** ~1 minute  
**Expected:** All consistent (green)

### 8.2 After Bulk Import

**Scenario:** You just imported EURUSD M1 data for 2020-2023.

**Solution:**
```bash
python scripts\verify_data_consistency.py \
    --symbols EURUSD \
    --timeframes M1 \
    --start-year 2020 \
    --end-year 2023
```

**Time:** ~2 minutes  
**Expected:** Check import was successful

### 8.3 Investigating Issues

**Scenario:** Fast mode shows GBPUSD 2022 Week 15 is inconsistent.

**Solution:**
```bash
# Narrow down to specific data with comprehensive mode
python scripts\verify_data_consistency.py \
    --symbols GBPUSD \
    --timeframes M1 \
    --start-year 2022 \
    --end-year 2022 \
    --mode comprehensive
```

**Time:** ~30 minutes  
**Expected:** Detailed information about mismatches

### 8.4 Quarterly Audit

**Scenario:** Compliance requires quarterly data verification.

**Solution:**
```bash
# Full comprehensive check of all data
python scripts\verify_data_consistency.py --mode comprehensive
```

**Time:** ~3-5 hours  
**Expected:** Complete accuracy report for auditors

### 8.5 Pre-Migration Check

**Scenario:** Before migrating to new database server, verify all data.

**Solution:**
```bash
# Step 1: Check old server (comprehensive)
python scripts\verify_data_consistency.py --mode comprehensive

# Step 2: After migration, check new server
# (Edit config to point to new server)
python scripts\verify_data_consistency.py --mode comprehensive

# Step 3: Compare reports
```

**Time:** ~6-10 hours total  
**Expected:** Identical results = successful migration

### 8.6 Automated Monitoring

**Scenario:** Run nightly verification and email results.

**Solution:**
```python
# monitoring_script.py
from scripts.verify_data_consistency import DataConsistencyChecker
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Run verification
checker = DataConsistencyChecker(mode='fast')
results = checker.verify_data()

# Generate report
report_path = checker.generate_html_report()

# Check if any issues
issues = checker.stats['inconsistent'] + checker.stats['no_data']

if issues > 0:
    # Send alert email
    msg = MIMEMultipart()
    msg['Subject'] = f'⚠️ Data Consistency Alert: {issues} issues found'
    msg['From'] = 'monitoring@example.com'
    msg['To'] = 'admin@example.com'
    
    body = f"""
    Data consistency check found {issues} issues:
    - Inconsistent: {checker.stats['inconsistent']}
    - No data: {checker.stats['no_data']}
    
    Full report: {report_path}
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email (configure SMTP)
    # smtp.send_message(msg)
```

### 8.7 Specific Week Investigation

**Scenario:** User reports EURUSD 2024 Week 23 has bad data.

**Solution:**
```python
# investigate_week.py
from scripts.verify_data_consistency import DataConsistencyChecker
from pathlib import Path

checker = DataConsistencyChecker(mode='comprehensive')

# Verify specific file
csv_path = Path('fxcm_data/EURUSD/M1/2024/week_23.csv')
result = checker.verify_file(csv_path, 'EURUSD', 'M1')

print(f"Status: {result['status']}")
print(f"Details: {result['details']}")

if result['status'] == 'inconsistent':
    details = result['details']
    print(f"\nMismatch Analysis:")
    print(f"  Total records: {details['total']}")
    print(f"  Matched: {details['matched']}")
    print(f"  Missing in DB: {details['missing']}")
    print(f"  Value mismatches: {details['mismatched']}")
```

---

## 9. Troubleshooting

### 9.1 Common Errors

#### Error: "Config file not found"

**Cause:** Configuration file is missing or path is wrong.

**Solution:**
```bash
# Check if file exists
dir config\clickhouse_config.json

# If missing, create from template
copy config\clickhouse_config.json.template config\clickhouse_config.json

# Edit with your settings
notepad config\clickhouse_config.json
```

#### Error: "Database connection failed"

**Cause:** Cannot connect to ClickHouse server.

**Checklist:**
1. ✅ Is the server running?
   ```bash
   ping 192.168.2.168
   ```

2. ✅ Is the port correct?
   ```bash
   telnet 192.168.2.168 8123
   ```

3. ✅ Are credentials correct?
   - Check username/password in config
   - Try connecting with clickhouse-client

4. ✅ Is firewall blocking?
   - Check Windows Firewall
   - Check network firewall rules

#### Error: "No files found"

**Cause:** Script can't find CSV files.

**Solution:**
```bash
# Make sure you're in the right directory
cd C:\Users\abing\OneDrive\Desktop\Forex

# Check if data directory exists
dir fxcm_data

# Check if specific symbol exists
dir fxcm_data\EURUSD\M1\2015
```

#### Error: "Module not found: pandas"

**Cause:** Required Python packages not installed.

**Solution:**
```bash
pip install pandas requests
```

#### Error: "Permission denied" writing report

**Cause:** No write permission to logs directory.

**Solution:**
```bash
# Check if logs directory exists
mkdir logs

# Check permissions
# Right-click logs folder → Properties → Security
```

### 9.2 Performance Issues

#### Issue: Fast mode takes too long (>10 minutes)

**Possible causes:**
- Slow network to database
- Database server overloaded
- Too many files to check

**Solutions:**
1. Check specific symbol/year instead of all:
   ```bash
   python scripts\verify_data_consistency.py --symbols EURUSD --start-year 2024
   ```

2. Use database on local network

3. Run during off-peak hours

#### Issue: Out of memory error

**Possible causes:**
- Comprehensive mode on large dataset
- Too many files processed simultaneously
- Insufficient RAM

**Solutions:**
1. Use fast mode instead:
   ```bash
   python scripts\verify_data_consistency.py --mode fast
   ```

2. Check smaller chunks:
   ```bash
   python scripts\verify_data_consistency.py --start-year 2020 --end-year 2020
   python scripts\verify_data_consistency.py --start-year 2021 --end-year 2021
   ```

3. Close other applications

4. Upgrade RAM

### 9.3 Report Issues

#### Issue: HTML report doesn't open automatically

**Cause:** No default browser or security restrictions.

**Solution:**
Manually open report:
```bash
# Find latest report
dir logs\consistency_report_*.html /O-D

# Open in browser
start logs\consistency_report_20251005_143022.html
```

#### Issue: Colors not showing in terminal

**Cause:** Terminal doesn't support ANSI colors.

**Solution:**
- Windows: Use Windows Terminal or PowerShell
- Linux: Most terminals support colors
- Fallback: Use HTML report instead

### 9.4 Data Interpretation Issues

#### Question: Why does fast mode say "consistent" but I know there's missing data?

**Answer:** Fast mode only checks first and last records. If both exist, it assumes the file is complete. Use comprehensive mode to check all records:
```bash
python scripts\verify_data_consistency.py --mode comprehensive --symbols SYMBOL
```

#### Question: What does "inconsistent" actually mean?

**Answer:** It means:
- **Fast mode:** One or both boundary records are missing
- **Comprehensive mode:** Some records don't match or are missing

Check the HTML report details for more information.

---

## 10. Best Practices

### 10.1 Regular Verification Schedule

**Recommended schedule:**

| Frequency | Mode | Scope | Purpose |
|-----------|------|-------|---------|
| **Daily** | Fast | All data | Health check |
| **Weekly** | Fast | Previous week | Recent import verification |
| **Monthly** | Comprehensive | Current year | Detailed check |
| **Quarterly** | Comprehensive | All data | Full audit |

**Example cron job (Linux):**
```bash
# Daily at 2 AM
0 2 * * * cd /path/to/Forex && python scripts/verify_data_consistency.py

# Monthly comprehensive on 1st of month at 1 AM
0 1 1 * * cd /path/to/Forex && python scripts/verify_data_consistency.py --mode comprehensive
```

**Example Windows Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily, 2:00 AM
4. Action: Start a program
5. Program: `C:\path\to\verify_consistency.bat`

### 10.2 Report Management

**Storage:**
- Keep reports for at least 90 days
- Archive important reports separately
- Use meaningful names for custom reports:
  ```bash
  --output logs/audit_2024_Q1.html
  --output logs/migration_verification.html
  ```

**Review:**
- Always review the summary statistics
- Investigate any inconsistent or no_data results
- Track trends over time (are issues increasing?)

### 10.3 Configuration Management

**Security:**
- ✅ Protect config file (contains password)
- ✅ Don't commit passwords to git
- ✅ Use environment variables for sensitive data
- ✅ Restrict file permissions

**Version control:**
```bash
# .gitignore
config/clickhouse_config.json
logs/*.html

# Keep template
config/clickhouse_config.json.template
```

**Multiple environments:**
```bash
# Development
config/clickhouse_config_dev.json

# Production
config/clickhouse_config_prod.json

# Usage
python scripts\verify_data_consistency.py --config config\clickhouse_config_prod.json
```

### 10.4 Integration with Workflows

**After data import:**
```bash
# 1. Import data
python scripts\batch_import_all.py

# 2. Verify import
python scripts\verify_data_consistency.py --start-year 2025

# 3. If issues found, investigate
```

**Before critical operations:**
```bash
# Before database migration/upgrade
python scripts\verify_data_consistency.py --mode comprehensive

# Save report as baseline
# After operation, run again and compare
```

**Automated testing:**
```python
# test_data_integrity.py
from scripts.verify_data_consistency import DataConsistencyChecker

def test_data_integrity():
    checker = DataConsistencyChecker(mode='fast')
    results = checker.verify_data(start_year=2025)
    
    # Assert no issues
    assert checker.stats['inconsistent'] == 0, "Found inconsistent data"
    assert checker.stats['no_data'] == 0, "Found missing data"
```

---

## 11. FAQ

### Q1: How long does verification take?

**A:** 
- Fast mode (all data): ~5 minutes
- Fast mode (one symbol): ~1 minute
- Comprehensive mode (all data): ~3-5 hours
- Comprehensive mode (one year): ~30 minutes

### Q2: Does verification modify any data?

**A:** No! The tool is completely read-only. It never modifies CSV files or database records.

### Q3: Can I run verification while importing data?

**A:** Yes, but:
- Fast mode: Usually safe
- Comprehensive mode: May see inconsistencies for files being imported
- Best practice: Run verification after imports complete

### Q4: What's the difference between "inconsistent" and "no data"?

**A:**
- **No data (red):** CSV file doesn't exist OR no records in database
- **Inconsistent (yellow):** CSV exists, database has some data, but they don't match
- **Consistent (green):** Perfect match

### Q5: Why do I get different results with fast vs comprehensive mode?

**A:** Fast mode only checks first and last records. Comprehensive mode checks ALL records. If data in the middle is missing or wrong, only comprehensive mode will detect it.

### Q6: Can I check just one specific week?

**A:** Not directly via command line, but you can use Python API:
```python
from pathlib import Path
from scripts.verify_data_consistency import DataConsistencyChecker

checker = DataConsistencyChecker(mode='comprehensive')
result = checker.verify_file(
    Path('fxcm_data/EURUSD/M1/2024/week_23.csv'),
    'EURUSD',
    'M1'
)
print(result)
```

### Q7: What should I do if I find inconsistencies?

**A:**
1. Note which files are inconsistent (from HTML report)
2. Run comprehensive mode on those specific files
3. Check import logs for errors during those time periods
4. Re-import the affected files
5. Verify again to confirm fix

### Q8: Can I automate this to run every night?

**A:** Yes! Use Windows Task Scheduler (Windows) or cron (Linux):

**Windows:**
```bash
# Create batch file: nightly_check.bat
@echo off
cd C:\Users\abing\OneDrive\Desktop\Forex
python scripts\verify_data_consistency.py --start-year 2025
```
Then schedule via Task Scheduler.

**Linux:**
```bash
# Add to crontab
0 2 * * * cd /path/to/Forex && python scripts/verify_data_consistency.py
```

### Q9: The HTML report is huge. Can I make it smaller?

**A:** The report size depends on how much data you check. To reduce size:
- Check fewer years: `--start-year 2024`
- Check fewer symbols: `--symbols EURUSD GBPUSD`
- Check specific timeframe: `--timeframes M1`

### Q10: Can I compare two different databases?

**A:** Yes! Run verification twice with different configs:
```bash
# Check database 1
python scripts\verify_data_consistency.py \
    --config config\db1_config.json \
    --output logs\db1_report.html

# Check database 2
python scripts\verify_data_consistency.py \
    --config config\db2_config.json \
    --output logs\db2_report.html

# Compare the HTML reports
```

### Q11: What if my database is on a different port?

**A:** Edit the config file:
```json
{
    "host": "192.168.2.168",
    "http_port": 8888,  // Change this
    ...
}
```

### Q12: Can I export results to CSV/Excel?

**A:** Not directly, but you can use Python API:
```python
import pandas as pd
from scripts.verify_data_consistency import DataConsistencyChecker

checker = DataConsistencyChecker()
results = checker.verify_data()

# Convert to DataFrame
df = pd.DataFrame(results)

# Export to CSV
df.to_csv('verification_results.csv', index=False)

# Export to Excel
df.to_excel('verification_results.xlsx', index=False)
```

### Q13: Why is comprehensive mode so slow?

**A:** It checks EVERY record (millions of rows):
- Reads entire CSV files
- Queries large date ranges from database
- Compares each record individually

This is necessary for 100% accuracy but takes time.

### Q14: Can I speed up verification?

**A:** Several options:
1. Use fast mode (10-20x faster)
2. Check fewer symbols/years
3. Run database locally (reduce network latency)
4. Use SSD for CSV files
5. Future enhancement: Parallel processing (not yet implemented)

### Q15: What do I do if tests fail?

**A:** 
1. Check error message in test output
2. Verify database connection:
   ```bash
   python scripts\test\test_clickhouse_connection.py
   ```
3. Check if data files exist:
   ```bash
   dir fxcm_data\EURUSD\M1\2015
   ```
4. Check configuration is correct
5. Contact support if issue persists

---

## Appendix A: File Structure Reference

```
Forex/
├── config/
│   └── clickhouse_config.json          # Database configuration
├── fxcm_data/
│   ├── EURUSD/
│   │   ├── M1/
│   │   │   ├── 2015/
│   │   │   │   ├── week_01.csv
│   │   │   │   ├── week_02.csv
│   │   │   │   └── ...
│   │   │   └── 2016/ ...
│   │   └── D1/
│   │       ├── 2015.csv
│   │       ├── 2016.csv
│   │       └── ...
│   └── GBPUSD/ ...
├── logs/
│   └── consistency_report_*.html       # Generated reports
├── scripts/
│   ├── verify_data_consistency.py      # Main script
│   └── test/
│       └── test_verify_consistency.py  # Test suite
└── verify_consistency.bat              # Windows launcher
```

---

## Appendix B: Exit Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 0 | Success | Verification completed (doesn't mean all data is consistent) |
| 1 | Error | Script crashed or couldn't complete |

Note: The exit code indicates script success, not data consistency. Check the report/statistics to assess data quality.

---

## Appendix C: Support and Contact

**Documentation:**
- Requirements: `doc/requirement/data_consistency_verification_requirements.md`
- Design: `doc/design/data_consistency_verification_design.md`
- Manual: `doc/manual/data_consistency_verification_manual.md` (this file)

**Testing:**
- Test script: `scripts/test/test_verify_consistency.py`
- Run tests: `python scripts/test/test_verify_consistency.py`

**Issues:**
- Check logs for error messages
- Run test suite
- Review troubleshooting section (Section 9)

**Version:** 1.0.0  
**Last Updated:** 2025-10-05

---

**Happy Verifying! 🔍✅**
