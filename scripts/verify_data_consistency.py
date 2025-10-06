#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FXCM Data Consistency Verification Script
=========================================

This script verifies the consistency between local CSV files and ClickHouse database.

Features:
- Compare local CSV data with database records
- Support fast mode (check first/last records) and comprehensive mode (check all records)
- Generate HTML and terminal reports with color-coded status
- Configurable symbols, timeframes, and date ranges
- Return structured verification results

Author: FXCM Data Team
Version: 1.0.0
Date: 2025-10-05
"""

import os
import sys
import json
import pandas as pd
import requests
from datetime import datetime, timedelta
from pathlib import Path
import argparse
from collections import defaultdict
import time

# Import progress grid module
from progress_grid import ProgressGrid, ProgressStatus

# Fix Windows console UTF-8 encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class DataConsistencyChecker:
    """
    Main class for verifying data consistency between CSV files and ClickHouse database.
    
    Attributes:
        config (dict): ClickHouse configuration
        base_url (str): ClickHouse HTTP endpoint URL
        auth (tuple): Authentication credentials
        mode (str): Verification mode ('fast' or 'comprehensive')
        results (list): List of verification results
    """
    
    # Status constants
    STATUS_NO_DATA = 'no_data'
    STATUS_INCONSISTENT = 'inconsistent'
    STATUS_CONSISTENT = 'consistent'
    
    # Color codes for terminal output
    COLOR_RED = '\033[91m'
    COLOR_YELLOW = '\033[93m'
    COLOR_GREEN = '\033[92m'
    COLOR_BLUE = '\033[94m'
    COLOR_RESET = '\033[0m'
    
    def __init__(self, config_path='config/clickhouse_config.json', mode='fast'):
        """
        Initialize the consistency checker.
        
        Args:
            config_path (str): Path to ClickHouse configuration file
            mode (str): Verification mode - 'fast' or 'comprehensive'
        """
        self.config = self._load_config(config_path)
        self.base_url = f"http://{self.config['host']}:{self.config.get('http_port', 8123)}"
        self.auth = (self.config['user'], self.config['password'])
        self.mode = mode
        self.results = []
        
        # Statistics
        self.stats = {
            'total_files': 0,
            'no_data': 0,
            'inconsistent': 0,
            'consistent': 0,
            'errors': 0
        }
        
        # Progress grid for visual feedback
        self.progress_grid = ProgressGrid("数据一致性验证进度")
        
    def _load_config(self, config_path):
        """Load ClickHouse configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            # Set default ports if not specified
            config.setdefault('http_port', 8123)
            config.setdefault('port', 9000)
            config.setdefault('native_port', 9009)
            return config
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            sys.exit(1)
    
    def execute_query(self, query, timeout=60):
        """
        Execute a query on ClickHouse via HTTP.
        
        Args:
            query (str): SQL query to execute
            timeout (int): Request timeout in seconds
            
        Returns:
            tuple: (success: bool, result: str)
        """
        try:
            response = requests.post(
                self.base_url,
                auth=self.auth,
                data=query.encode('utf-8'),
                timeout=timeout
            )
            
            if response.status_code == 200:
                return True, response.text.strip()
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, str(e)
    
    def get_csv_boundaries(self, csv_path, timeframe):
        """
        Get first and last timestamp from CSV file.
        
        Args:
            csv_path (Path): Path to CSV file
            timeframe (str): 'M1' or 'D1'
            
        Returns:
            tuple: (first_timestamp, last_timestamp, total_rows) or (None, None, 0) on error
        """
        try:
            df = pd.read_csv(csv_path)
            if df.empty:
                return None, None, 0
            
            # Get timestamp column (first column)
            time_col = df.columns[0]
            first_time = df[time_col].iloc[0]
            last_time = df[time_col].iloc[-1]
            total_rows = len(df)
            
            return first_time, last_time, total_rows
            
        except Exception as e:
            print(f"❌ Error reading CSV {csv_path}: {e}")
            return None, None, 0
    
    def check_boundaries_in_db(self, symbol, timeframe, first_time, last_time):
        """
        Check if first and last timestamps exist in database (fast mode).
        
        Args:
            symbol (str): Currency pair symbol
            timeframe (str): 'M1' or 'D1'
            first_time (str): First timestamp from CSV
            last_time (str): Last timestamp from CSV
            
        Returns:
            str: 'both', 'partial', or 'none'
        """
        table = 'ohlcv_m1' if timeframe == 'M1' else 'ohlcv_d1'
        time_field = 'timestamp' if timeframe == 'M1' else 'date'
        
        query = f"""
        SELECT COUNT(*) as cnt
        FROM forex_data.{table}
        WHERE symbol = '{symbol}'
          AND {time_field} IN ('{first_time}', '{last_time}')
        FORMAT TabSeparated
        """
        
        success, result = self.execute_query(query)
        if success and result:
            count = int(result.strip())
            if count == 2:
                return 'both'
            elif count == 1:
                return 'partial'
            else:
                return 'none'
        return 'none'
    
    def check_comprehensive(self, csv_path, symbol, timeframe):
        """
        Comprehensive check: compare all records between CSV and database.
        
        Args:
            csv_path (Path): Path to CSV file
            symbol (str): Currency pair symbol
            timeframe (str): 'M1' or 'D1'
            
        Returns:
            dict: Comparison results with match statistics
        """
        try:
            # Read CSV
            df = pd.read_csv(csv_path)
            if df.empty:
                return {'status': 'no_data', 'total': 0, 'matched': 0, 'missing': 0}
            
            time_col = df.columns[0]
            first_time = df[time_col].iloc[0]
            last_time = df[time_col].iloc[-1]
            
            # Query database
            table = 'ohlcv_m1' if timeframe == 'M1' else 'ohlcv_d1'
            time_field = 'timestamp' if timeframe == 'M1' else 'date'
            
            query = f"""
            SELECT {time_field}, open, high, low, close, volume
            FROM forex_data.{table}
            WHERE symbol = '{symbol}'
              AND {time_field} >= '{first_time}'
              AND {time_field} <= '{last_time}'
            ORDER BY {time_field}
            FORMAT TabSeparated
            """
            
            success, result = self.execute_query(query, timeout=300)
            if not success:
                return {'status': 'error', 'error': result}
            
            if not result:
                return {'status': 'no_data', 'total': len(df), 'matched': 0, 'missing': len(df)}
            
            # Parse database results
            db_data = {}
            for line in result.split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    timestamp = parts[0]
                    values = [float(x) for x in parts[1:6]]
                    db_data[timestamp] = values
            
            # Compare records
            matched = 0
            missing = 0
            mismatched = 0
            
            for idx, row in df.iterrows():
                timestamp = str(row[time_col])
                # CSV columns: DateTime, Open, High, Low, Close
                csv_values = [float(row['Open']), float(row['High']), 
                             float(row['Low']), float(row['Close'])]
                
                if timestamp in db_data:
                    db_values = db_data[timestamp][:4]  # Only compare OHLC, skip volume
                    # Compare with small tolerance for floating point
                    if all(abs(a - b) < 0.00001 for a, b in zip(csv_values, db_values)):
                        matched += 1
                    else:
                        mismatched += 1
                else:
                    missing += 1
            
            total = len(df)
            if matched == total:
                status = self.STATUS_CONSISTENT
            elif matched == 0:
                status = self.STATUS_NO_DATA
            else:
                status = self.STATUS_INCONSISTENT
            
            return {
                'status': status,
                'total': total,
                'matched': matched,
                'missing': missing,
                'mismatched': mismatched
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def verify_file(self, csv_path, symbol, timeframe):
        """
        Verify a single CSV file against database.
        
        Args:
            csv_path (Path): Path to CSV file
            symbol (str): Currency pair symbol
            timeframe (str): 'M1' or 'D1'
            
        Returns:
            dict: Verification result
        """
        # Extract year and week from path
        if timeframe == 'M1':
            # Path like: fxcm_data/EURUSD/M1/2015/week_01.csv
            parts = csv_path.parts
            year = int(parts[-2])
            week = int(parts[-1].replace('week_', '').replace('.csv', ''))
        else:
            # Path like: fxcm_data/EURUSD/D1/2015.csv
            year = int(csv_path.stem)
            week = 0  # D1 doesn't have weeks
        
        result = {
            'symbol': symbol,
            'timeframe': timeframe,
            'year': year,
            'week': week,
            'file': str(csv_path),
            'status': self.STATUS_NO_DATA,
            'details': {}
        }
        
        # Get CSV boundaries
        first_time, last_time, total_rows = self.get_csv_boundaries(csv_path, timeframe)
        
        if first_time is None:
            result['status'] = self.STATUS_NO_DATA
            result['details'] = {'error': 'Failed to read CSV file'}
            return result
        
        result['details']['csv_rows'] = total_rows
        result['details']['first_time'] = first_time
        result['details']['last_time'] = last_time
        
        if self.mode == 'fast':
            # Fast mode: check only boundaries
            boundary_status = self.check_boundaries_in_db(symbol, timeframe, first_time, last_time)
            
            if boundary_status == 'both':
                result['status'] = self.STATUS_CONSISTENT
                result['details']['db_check'] = 'Both boundaries found'
            elif boundary_status == 'partial':
                result['status'] = self.STATUS_INCONSISTENT
                result['details']['db_check'] = 'Only partial boundaries found'
            else:
                result['status'] = self.STATUS_NO_DATA
                result['details']['db_check'] = 'No boundaries found'
                
        else:
            # Comprehensive mode: check all records
            comp_result = self.check_comprehensive(csv_path, symbol, timeframe)
            result['status'] = comp_result['status']
            result['details'].update(comp_result)
        
        return result
    
    def verify_data(self, symbols=None, timeframes=None, start_year=2015, end_year=None):
        """
        Main verification function.
        
        Args:
            symbols (list): List of symbols to check (default: all 6 pairs)
            timeframes (list): List of timeframes ['M1', 'D1'] (default: both)
            start_year (int): Start year (default: 2015)
            end_year (int): End year (default: current year)
            
        Returns:
            list: List of verification results
        """
        # Default values
        if symbols is None:
            symbols = ['AUDUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'USDCHF']
        if timeframes is None:
            timeframes = ['M1', 'D1']
        if end_year is None:
            end_year = datetime.now().year
        
        self.results = []
        data_root = Path('fxcm_data')
        
        if not data_root.exists():
            print(f"❌ Error: Data directory '{data_root}' does not exist!")
            return self.results
        
        print(f"\n{'='*80}")
        print(f"  🔍 FXCM Data Consistency Verification")
        print(f"{'='*80}")
        print(f"Mode: {self.mode.upper()}")
        print(f"Symbols: {', '.join(symbols)}")
        print(f"Timeframes: {', '.join(timeframes)}")
        print(f"Period: {start_year} - {end_year}")
        print(f"{'='*80}\n")
        
        total_files = 0
        
        for symbol in symbols:
            symbol_path = data_root / symbol
            if not symbol_path.exists():
                print(f"⚠️  Warning: Symbol directory '{symbol}' not found")
                continue
            
            for timeframe in timeframes:
                tf_path = symbol_path / timeframe
                if not tf_path.exists():
                    print(f"⚠️  Warning: Timeframe directory '{symbol}/{timeframe}' not found")
                    continue
                
                print(f"\n📊 Checking {symbol} {timeframe}...")
                
                if timeframe == 'M1':
                    # M1 data organized by year/week
                    for year in range(start_year, end_year + 1):
                        year_path = tf_path / str(year)
                        if not year_path.exists():
                            continue
                        
                        csv_files = sorted(year_path.glob('week_*.csv'))
                        if csv_files:
                            # Initialize progress grid for this year
                            self.progress_grid.initialize_grid(symbol, timeframe, year, 52)
                            
                        for csv_file in csv_files:
                            total_files += 1
                            result = self.verify_file(csv_file, symbol, timeframe)
                            self.results.append(result)
                            self._update_stats(result['status'])
                            
                            # Update progress grid
                            week = result['week']
                            status_map = {
                                self.STATUS_CONSISTENT: ProgressStatus.SUCCESS,
                                self.STATUS_INCONSISTENT: ProgressStatus.WARNING,
                                self.STATUS_NO_DATA: ProgressStatus.ERROR
                            }
                            self.progress_grid.update_status(symbol, timeframe, year, week - 1, status_map[result['status']])
                            self.progress_grid.display_line(symbol, timeframe, year)
                        
                        # Newline after each year
                        if csv_files:
                            self.progress_grid.newline()
                
                else:  # D1
                    # D1 data organized by year files
                    years_list = []
                    for year in range(start_year, end_year + 1):
                        csv_file = tf_path / f"{year}.csv"
                        if csv_file.exists():
                            years_list.append(year)
                    
                    if years_list:
                        # Initialize progress grid for D1 years
                        self.progress_grid.initialize_grid(symbol, timeframe, 0, len(years_list))
                        year_index = 0
                        
                        for year in range(start_year, end_year + 1):
                            csv_file = tf_path / f"{year}.csv"
                            if csv_file.exists():
                                total_files += 1
                                result = self.verify_file(csv_file, symbol, timeframe)
                                self.results.append(result)
                                self._update_stats(result['status'])
                                
                                # Update progress grid
                                status_map = {
                                    self.STATUS_CONSISTENT: ProgressStatus.SUCCESS,
                                    self.STATUS_INCONSISTENT: ProgressStatus.WARNING,
                                    self.STATUS_NO_DATA: ProgressStatus.ERROR
                                }
                                self.progress_grid.update_status(symbol, timeframe, 0, year_index, status_map[result['status']])
                                self.progress_grid.display_line(symbol, timeframe, 0, f"{symbol} {timeframe}")
                                year_index += 1
                        
                        # Newline after all D1 years
                        self.progress_grid.newline()
        
        self.stats['total_files'] = total_files
        
        # Display progress grid summary and legend
        self.progress_grid.print_legend()
        self.progress_grid.print_summary()
        
        self._print_summary()
        
        return self.results
    
    def _update_stats(self, status):
        """Update statistics counters."""
        if status == self.STATUS_NO_DATA:
            self.stats['no_data'] += 1
        elif status == self.STATUS_INCONSISTENT:
            self.stats['inconsistent'] += 1
        elif status == self.STATUS_CONSISTENT:
            self.stats['consistent'] += 1
    
    def _print_file_status(self, result):
        """Print status for a single file."""
        status = result['status']
        symbol = result['symbol']
        timeframe = result['timeframe']
        year = result['year']
        week = result['week']
        
        # Format identifier
        if timeframe == 'M1':
            identifier = f"{symbol} {timeframe} {year} Week-{week:02d}"
        else:
            identifier = f"{symbol} {timeframe} {year}"
        
        # Color-coded status
        if status == self.STATUS_CONSISTENT:
            color = self.COLOR_GREEN
            icon = '✅'
            status_text = 'CONSISTENT'
        elif status == self.STATUS_INCONSISTENT:
            color = self.COLOR_YELLOW
            icon = '⚠️ '
            status_text = 'INCONSISTENT'
        else:
            color = self.COLOR_RED
            icon = '❌'
            status_text = 'NO DATA'
        
        print(f"  {icon} {identifier:35s} {color}{status_text}{self.COLOR_RESET}")
    
    def _print_summary(self):
        """Print verification summary."""
        total = self.stats['total_files']
        
        print(f"\n{'='*80}")
        print(f"  📋 Verification Summary")
        print(f"{'='*80}")
        print(f"Total files checked: {total}")
        print(f"{self.COLOR_GREEN}✅ Consistent:    {self.stats['consistent']:5d} ({self.stats['consistent']/total*100:5.1f}%){self.COLOR_RESET}")
        print(f"{self.COLOR_YELLOW}⚠️  Inconsistent:  {self.stats['inconsistent']:5d} ({self.stats['inconsistent']/total*100:5.1f}%){self.COLOR_RESET}")
        print(f"{self.COLOR_RED}❌ No data:       {self.stats['no_data']:5d} ({self.stats['no_data']/total*100:5.1f}%){self.COLOR_RESET}")
        print(f"{'='*80}\n")
    
    def generate_html_report(self, output_path=None):
        """
        Generate HTML report with color-coded visualization.
        
        Args:
            output_path (str): Output file path (default: logs/consistency_report_[timestamp].html)
            
        Returns:
            str: Path to generated report
        """
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"logs/consistency_report_{timestamp}.html"
        
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Organize results by symbol and timeframe
        organized = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
        
        for result in self.results:
            symbol = result['symbol']
            timeframe = result['timeframe']
            year = result['year']
            week = result['week']
            organized[symbol][timeframe][year][week] = result
        
        # Generate HTML
        html = self._generate_html_content(organized)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"📄 HTML report generated: {output_path}")
        return output_path
    
    def _generate_html_content(self, organized):
        """Generate HTML content for the report."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FXCM Data Consistency Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background: #f8f9fa;
            border-bottom: 3px solid #667eea;
        }}
        
        .stat-box {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .stat-box .number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-box .label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
        }}
        
        .stat-consistent .number {{ color: #28a745; }}
        .stat-inconsistent .number {{ color: #ffc107; }}
        .stat-nodata .number {{ color: #dc3545; }}
        
        .content {{
            padding: 40px;
        }}
        
        .symbol-section {{
            margin-bottom: 40px;
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
        }}
        
        .symbol-header {{
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        .timeframe-section {{
            margin-bottom: 30px;
        }}
        
        .timeframe-title {{
            font-size: 1.3em;
            color: #555;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }}
        
        .timeframe-title::before {{
            content: '📊';
            margin-right: 10px;
        }}
        
        .year-grid {{
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 10px;
            margin-bottom: 15px;
        }}
        
        .year-label {{
            font-weight: bold;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border-radius: 5px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .week-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(35px, 1fr));
            gap: 5px;
        }}
        
        .week-cell {{
            width: 35px;
            height: 35px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 5px;
            font-size: 0.8em;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        
        .week-cell:hover {{
            transform: scale(1.1);
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        
        .status-consistent {{
            background: #28a745;
            color: white;
        }}
        
        .status-inconsistent {{
            background: #ffc107;
            color: #333;
        }}
        
        .status-nodata {{
            background: #dc3545;
            color: white;
        }}
        
        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 30px;
            padding: 20px;
            background: white;
            border-radius: 10px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .legend-box {{
            width: 30px;
            height: 30px;
            border-radius: 5px;
        }}
        
        .footer {{
            background: #333;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        
        .info-panel {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        
        .info-panel strong {{
            color: #1976d2;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 FXCM Data Consistency Report</h1>
            <div class="subtitle">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="stats">
            <div class="stat-box stat-consistent">
                <div class="number">{self.stats['consistent']}</div>
                <div class="label">Consistent</div>
            </div>
            <div class="stat-box stat-inconsistent">
                <div class="number">{self.stats['inconsistent']}</div>
                <div class="label">Inconsistent</div>
            </div>
            <div class="stat-box stat-nodata">
                <div class="number">{self.stats['no_data']}</div>
                <div class="label">No Data</div>
            </div>
            <div class="stat-box">
                <div class="number" style="color: #667eea;">{self.stats['total_files']}</div>
                <div class="label">Total Files</div>
            </div>
        </div>
        
        <div class="content">
            <div class="info-panel">
                <strong>Verification Mode:</strong> {self.mode.upper()}<br>
                <strong>Database:</strong> {self.config['host']}:{self.config.get('http_port', 8123)}
            </div>
"""
        
        # Generate content for each symbol
        for symbol in sorted(organized.keys()):
            html += f"""
            <div class="symbol-section">
                <div class="symbol-header">💱 {symbol}</div>
"""
            
            for timeframe in ['M1', 'D1']:
                if timeframe not in organized[symbol]:
                    continue
                
                html += f"""
                <div class="timeframe-section">
                    <div class="timeframe-title">{timeframe} Data</div>
"""
                
                years = sorted(organized[symbol][timeframe].keys())
                for year in years:
                    weeks = organized[symbol][timeframe][year]
                    
                    html += f"""
                    <div class="year-grid">
                        <div class="year-label">{year}</div>
                        <div class="week-grid">
"""
                    
                    if timeframe == 'M1':
                        # M1 has weeks 1-52
                        for week in range(1, 53):
                            if week in weeks:
                                result = weeks[week]
                                status = result['status']
                                status_class = f'status-{status.replace("_", "")}'
                                title = f"{symbol} {timeframe} {year} Week {week}: {status.upper()}"
                                html += f'<div class="week-cell {status_class}" title="{title}">{week}</div>\n'
                            else:
                                html += f'<div class="week-cell status-nodata" title="No file">-</div>\n'
                    else:
                        # D1 has only one entry per year (week 0)
                        if 0 in weeks:
                            result = weeks[0]
                            status = result['status']
                            status_class = f'status-{status.replace("_", "")}'
                            title = f"{symbol} {timeframe} {year}: {status.upper()}"
                            details = result['details']
                            info = f"CSV rows: {details.get('csv_rows', 'N/A')}"
                            html += f'<div class="week-cell {status_class}" title="{title}&#10;{info}" style="width: 100%;">Full Year</div>\n'
                    
                    html += """
                        </div>
                    </div>
"""
                
                html += """
                </div>
"""
            
            html += """
            </div>
"""
        
        html += f"""
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-box status-consistent"></div>
                    <span>Consistent (CSV matches DB)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-box status-inconsistent"></div>
                    <span>Inconsistent (Data mismatch)</span>
                </div>
                <div class="legend-item">
                    <div class="legend-box status-nodata"></div>
                    <span>No Data (CSV not found or empty)</span>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>FXCM Data Consistency Verification Tool v1.0.0</p>
            <p>© 2025 FXCM Data Team</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Verify FXCM data consistency between CSV files and ClickHouse database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check all symbols, all timeframes, default period (2015-now), fast mode
  python verify_data_consistency.py
  
  # Check specific symbol
  python verify_data_consistency.py --symbols EURUSD
  
  # Check multiple symbols
  python verify_data_consistency.py --symbols EURUSD GBPUSD USDJPY
  
  # Check only M1 data
  python verify_data_consistency.py --timeframes M1
  
  # Check specific year range
  python verify_data_consistency.py --start-year 2020 --end-year 2023
  
  # Use comprehensive mode (slower but more accurate)
  python verify_data_consistency.py --mode comprehensive
  
  # Specify custom config file
  python verify_data_consistency.py --config custom_config.json
  
  # Specify custom output file
  python verify_data_consistency.py --output my_report.html
"""
    )
    
    parser.add_argument(
        '--symbols',
        nargs='+',
        default=None,
        help='Currency pairs to check (default: all 6 pairs)'
    )
    
    parser.add_argument(
        '--timeframes',
        nargs='+',
        choices=['M1', 'D1'],
        default=None,
        help='Timeframes to check (default: M1 and D1)'
    )
    
    parser.add_argument(
        '--start-year',
        type=int,
        default=2015,
        help='Start year (default: 2015)'
    )
    
    parser.add_argument(
        '--end-year',
        type=int,
        default=None,
        help='End year (default: current year)'
    )
    
    parser.add_argument(
        '--mode',
        choices=['fast', 'comprehensive'],
        default='fast',
        help='Verification mode: fast (check boundaries) or comprehensive (check all records)'
    )
    
    parser.add_argument(
        '--config',
        default='config/clickhouse_config.json',
        help='Path to ClickHouse config file (default: config/clickhouse_config.json)'
    )
    
    parser.add_argument(
        '--output',
        default=None,
        help='Output HTML file path (default: logs/consistency_report_[timestamp].html)'
    )
    
    parser.add_argument(
        '--no-html',
        action='store_true',
        help='Skip HTML report generation'
    )
    
    args = parser.parse_args()
    
    # Create checker instance
    checker = DataConsistencyChecker(config_path=args.config, mode=args.mode)
    
    # Run verification
    results = checker.verify_data(
        symbols=args.symbols,
        timeframes=args.timeframes,
        start_year=args.start_year,
        end_year=args.end_year
    )
    
    # Generate HTML report
    if not args.no_html:
        report_path = checker.generate_html_report(output_path=args.output)
        
        # Try to open in browser
        try:
            import webbrowser
            abs_path = os.path.abspath(report_path)
            webbrowser.open(f'file://{abs_path}')
            print(f"🌐 Opening report in browser...")
        except:
            pass
    
    # Return results (for programmatic use)
    return results


if __name__ == '__main__':
    main()
