"""
FXCM Data Importer v2.0
Import FXCM forex data from CSV files to ClickHouse database

Author: binphilxiao
Date: 2025-10-05
Version: 2.0.0
License: MIT
"""

import sys
import io
import argparse
import pandas as pd
from pathlib import Path
import logging
import json
from datetime import datetime
from typing import List, Optional, Dict, Tuple

# Conditional import of ClickHouse
try:
    import clickhouse_connect
    from clickhouse_connect.driver.client import Client
    CLICKHOUSE_AVAILABLE = True
except ImportError:
    CLICKHOUSE_AVAILABLE = False
    clickhouse_connect = None
    Client = None

# Load default ClickHouse config if available
def load_clickhouse_config():
    """Load ClickHouse configuration from config file"""
    config_path = Path('config/clickhouse_config.json')
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class FXCMDataImporter:
    """
    FXCM Data Importer
    
    Import forex historical data from CSV files to ClickHouse database
    with intelligent duplicate detection and flexible validation modes.
    
    Attributes:
        AVAILABLE_PAIRS (list): Supported currency pairs
        AVAILABLE_TIMEFRAMES (list): Supported timeframes
    """
    
    # Available currency pairs
    AVAILABLE_PAIRS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF']
    
    # Available timeframes
    AVAILABLE_TIMEFRAMES = ['M1', 'D1']
    
    # Check modes
    CHECK_MODES = ['fast', 'comprehensive']
    
    def __init__(self,
                 ch_host: str = '192.168.2.168',
                 ch_http_port: int = 8123,
                 ch_user: str = 'default',
                 ch_password: str = '',
                 data_dir: str = 'fxcm_data',
                 log_dir: str = 'logs',
                 batch_size: int = 1000,
                 tolerance: float = 1e-5):
        """
        Initialize FXCM Data Importer
        
        Args:
            ch_host: ClickHouse host
            ch_http_port: ClickHouse HTTP port
            ch_user: ClickHouse username
            ch_password: ClickHouse password
            data_dir: Directory containing CSV files
            log_dir: Directory for log files
            batch_size: Number of records per batch insert
            tolerance: Tolerance for OHLC comparison
        """
        # ClickHouse connection parameters
        self.ch_host = ch_host
        self.ch_http_port = ch_http_port
        self.ch_user = ch_user
        self.ch_password = ch_password
        
        # Settings
        self.batch_size = batch_size
        self.tolerance = tolerance
        
        # ClickHouse client
        self.client = None
        
        # Statistics
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'skipped_files': 0,
            'total_records_read': 0,
            'records_imported': 0,
            'records_skipped': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None,
            'processing_time': 0
        }
        
        # Project paths
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / data_dir
        self.log_dir = self.project_root / log_dir
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging configuration"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.log_dir / f'fxcm_import_{timestamp}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Log file: {log_file}")
        self.report_file = self.log_dir / f'fxcm_import_report_{timestamp}.txt'
        
    def connect_clickhouse(self) -> bool:
        """Establish connection to ClickHouse"""
        if not CLICKHOUSE_AVAILABLE:
            self.logger.error("❌ ClickHouse module not available. Install with: pip install clickhouse-connect")
            return False
            
        try:
            self.client = clickhouse_connect.get_client(
                host=self.ch_host,
                port=self.ch_http_port,
                username=self.ch_user,
                password=self.ch_password
            )
            self.logger.info(f"✅ Connected to ClickHouse at {self.ch_host}:{self.ch_http_port}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to ClickHouse: {e}")
            return False
            
    def disconnect_clickhouse(self):
        """Close ClickHouse connection"""
        if self.client:
            self.client.close()
            self.logger.info("ClickHouse connection closed")
            
    def _get_table_name(self, timeframe: str) -> str:
        """Get ClickHouse table name for timeframe"""
        return f"forex_data.ohlcv_{timeframe.lower()}"
        
    def _get_csv_files(self, pair: str, timeframe: str, year: int) -> List[Path]:
        """Get list of CSV files to process"""
        files = []
        
        if timeframe == 'M1':
            # M1: fxcm_data/EURUSD/M1/2024/week_01.csv
            year_dir = self.data_dir / pair / 'M1' / str(year)
            if year_dir.exists():
                files = sorted(year_dir.glob('week_*.csv'))
        else:  # D1
            # D1: fxcm_data/EURUSD/D1/2024.csv
            d1_file = self.data_dir / pair / 'D1' / f'{year}.csv'
            if d1_file.exists():
                files = [d1_file]
                
        return files
        
    def _read_csv_file(self, file_path: Path, timeframe: str) -> Optional[pd.DataFrame]:
        """Read CSV file and prepare data"""
        try:
            df = pd.read_csv(file_path)
            
            if df.empty:
                self.logger.warning(f"  ⚠️  File is empty: {file_path.name}")
                return None
                
            # Rename columns to match DB schema
            column_mapping = {
                'DateTime': 'timestamp' if timeframe == 'M1' else 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close'
            }
            df.rename(columns=column_mapping, inplace=True)
            
            # Convert datetime/date
            if timeframe == 'M1':
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            else:  # D1
                df['date'] = pd.to_datetime(df['date']).dt.date
                
            return df
            
        except Exception as e:
            self.logger.error(f"  ❌ Error reading {file_path.name}: {e}")
            self.stats['errors'] += 1
            return None
            
    def _validate_fast(self, df: pd.DataFrame, pair: str, timeframe: str) -> bool:
        """
        Fast validation - check first and last records only
        
        Returns:
            True if file exists in DB (skip), False if needs import
        """
        try:
            table = self._get_table_name(timeframe)
            time_col = 'timestamp' if timeframe == 'M1' else 'date'
            
            # Get first and last records
            first_row = df.iloc[0]
            last_row = df.iloc[-1]
            
            first_time = first_row[time_col]
            last_time = last_row[time_col]
            
            # Query DB for these two records
            query = f"""
            SELECT {time_col}, open, high, low, close
            FROM {table}
            WHERE symbol = '{pair}'
              AND {time_col} IN ('{first_time}', '{last_time}')
            ORDER BY {time_col}
            """
            
            result = self.client.query(query)
            
            if result.row_count != 2:
                return False  # Not both records exist, need import
                
            # Compare OHLC values
            db_first = result.result_rows[0]
            db_last = result.result_rows[1]
            
            # First record comparison
            first_match = self._compare_ohlc(
                (first_row['open'], first_row['high'], first_row['low'], first_row['close']),
                (db_first[1], db_first[2], db_first[3], db_first[4])
            )
            
            # Last record comparison
            last_match = self._compare_ohlc(
                (last_row['open'], last_row['high'], last_row['low'], last_row['close']),
                (db_last[1], db_last[2], db_last[3], db_last[4])
            )
            
            return first_match and last_match
            
        except Exception as e:
            self.logger.error(f"  ❌ Fast validation error: {e}")
            return False
            
    def _validate_comprehensive(self, df: pd.DataFrame, pair: str, timeframe: str) -> pd.DataFrame:
        """
        Comprehensive validation - check all records
        
        Returns:
            DataFrame containing only new/modified records to import
        """
        try:
            table = self._get_table_name(timeframe)
            time_col = 'timestamp' if timeframe == 'M1' else 'date'
            
            # Get time range
            min_time = df[time_col].min()
            max_time = df[time_col].max()
            
            # Query existing data
            query = f"""
            SELECT {time_col}, open, high, low, close
            FROM {table}
            WHERE symbol = '{pair}'
              AND {time_col} >= '{min_time}'
              AND {time_col} <= '{max_time}'
            """
            
            result = self.client.query(query)
            
            # Build hash map of existing data
            existing_data = {}
            for row in result.result_rows:
                timestamp = row[0]
                ohlc = (row[1], row[2], row[3], row[4])
                existing_data[timestamp] = ohlc
                
            # Filter new/modified records
            new_records = []
            for idx, row in df.iterrows():
                ts = row[time_col]
                
                if ts not in existing_data:
                    # New record
                    new_records.append(row)
                else:
                    # Check if modified
                    csv_ohlc = (row['open'], row['high'], row['low'], row['close'])
                    db_ohlc = existing_data[ts]
                    
                    if not self._compare_ohlc(csv_ohlc, db_ohlc):
                        # Modified record
                        new_records.append(row)
                        
            return pd.DataFrame(new_records) if new_records else pd.DataFrame()
            
        except Exception as e:
            self.logger.error(f"  ❌ Comprehensive validation error: {e}")
            return df  # Import all on error
            
    def _compare_ohlc(self, csv_ohlc: tuple, db_ohlc: tuple) -> bool:
        """Compare OHLC values with tolerance"""
        for i in range(4):
            if abs(float(csv_ohlc[i]) - float(db_ohlc[i])) > self.tolerance:
                return False
        return True
        
    def _insert_batch(self, df: pd.DataFrame, pair: str, timeframe: str) -> int:
        """Insert data in batches"""
        if df.empty:
            return 0
            
        try:
            table = self._get_table_name(timeframe)
            time_col = 'timestamp' if timeframe == 'M1' else 'date'
            
            # Add symbol column
            df['symbol'] = pair
            df['volume'] = 0
            
            # Select columns in correct order
            columns = ['symbol', time_col, 'open', 'high', 'low', 'close', 'volume']
            df_insert = df[columns].copy()
            
            # Insert in batches
            total_inserted = 0
            for i in range(0, len(df_insert), self.batch_size):
                batch = df_insert.iloc[i:i + self.batch_size]
                
                try:
                    self.client.insert_df(table, batch)
                    total_inserted += len(batch)
                except Exception as e:
                    self.logger.error(f"  ❌ Batch insert error: {e}")
                    self.stats['errors'] += 1
                    
            return total_inserted
            
        except Exception as e:
            self.logger.error(f"  ❌ Insert error: {e}")
            self.stats['errors'] += 1
            return 0
            
    def _process_file(self, file_path: Path, pair: str, timeframe: str, check_mode: str) -> Tuple[int, int]:
        """
        Process a single CSV file
        
        Returns:
            (records_imported, records_skipped)
        """
        self.logger.info(f"  📄 Processing: {file_path.name}")
        
        # Read CSV
        df = self._read_csv_file(file_path, timeframe)
        if df is None:
            return (0, 0)
            
        records_total = len(df)
        self.stats['total_records_read'] += records_total
        
        # Validation
        if check_mode == 'fast':
            # Fast mode: check first/last only
            if self._validate_fast(df, pair, timeframe):
                self.logger.info(f"    ⏭️  Skipped: File exists in DB ({records_total:,} records)")
                self.stats['skipped_files'] += 1
                self.stats['records_skipped'] += records_total
                return (0, records_total)
            else:
                # Import entire file
                records_imported = self._insert_batch(df, pair, timeframe)
                self.logger.info(f"    ✅ Imported: {records_imported:,} records")
                self.stats['records_imported'] += records_imported
                return (records_imported, 0)
                
        else:  # comprehensive
            # Comprehensive mode: check all records
            new_df = self._validate_comprehensive(df, pair, timeframe)
            records_new = len(new_df)
            records_skipped = records_total - records_new
            
            if records_new > 0:
                records_imported = self._insert_batch(new_df, pair, timeframe)
                self.logger.info(f"    ✅ Imported: {records_imported:,} new/modified")
                self.logger.info(f"    ⏭️  Skipped: {records_skipped:,} existing")
                self.stats['records_imported'] += records_imported
                self.stats['records_skipped'] += records_skipped
                return (records_imported, records_skipped)
            else:
                self.logger.info(f"    ⏭️  Skipped: All {records_total:,} records exist in DB")
                self.stats['skipped_files'] += 1
                self.stats['records_skipped'] += records_total
                return (0, records_total)
                
    def import_data(self,
                    pairs: List[str],
                    timeframes: List[str],
                    start_year: int,
                    end_year: int,
                    check_mode: str = 'fast') -> bool:
        """
        Main import process
        
        Args:
            pairs: List of currency pairs
            timeframes: List of timeframes (M1/D1)
            start_year: Start year
            end_year: End year
            check_mode: 'fast' or 'comprehensive'
            
        Returns:
            True if successful
        """
        self.stats['start_time'] = datetime.now()
        
        # Print header
        self._print_header(pairs, timeframes, start_year, end_year, check_mode)
        
        # Connect to ClickHouse
        if not self.connect_clickhouse():
            return False
            
        try:
            # Process each combination
            for pair in pairs:
                self.logger.info(f"\n{'='*60}")
                self.logger.info(f"Processing: {pair}")
                self.logger.info(f"{'='*60}")
                
                for timeframe in timeframes:
                    self.logger.info(f"\n⏱️  Timeframe: {timeframe}")
                    
                    for year in range(start_year, end_year + 1):
                        self.logger.info(f"\n📅 Year: {year}")
                        
                        # Get CSV files
                        files = self._get_csv_files(pair, timeframe, year)
                        
                        if not files:
                            self.logger.warning(f"  ⚠️  No files found for {pair} {timeframe} {year}")
                            continue
                            
                        self.stats['total_files'] += len(files)
                        self.logger.info(f"  📊 Found {len(files)} files")
                        
                        # Process each file
                        for file_path in files:
                            self._process_file(file_path, pair, timeframe, check_mode)
                            self.stats['processed_files'] += 1
                            
            # Generate report
            self.stats['end_time'] = datetime.now()
            self.stats['processing_time'] = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            self._generate_report()
            
            return True
            
        except KeyboardInterrupt:
            self.logger.warning("\n\n⚠️  Import interrupted by user")
            return False
        except Exception as e:
            self.logger.error(f"\n\n❌ Import failed: {e}")
            return False
        finally:
            self.disconnect_clickhouse()
            
    def _print_header(self, pairs, timeframes, start_year, end_year, check_mode):
        """Print import configuration header"""
        header = f"""
{'='*60}
FXCM Data Importer v2.0
{'='*60}
Currency Pairs: {', '.join(pairs)}
Timeframes: {', '.join(timeframes)}
Year Range: {start_year} - {end_year}
Check Mode: {check_mode.capitalize()}
ClickHouse: {self.ch_host}:{self.ch_http_port}
Data Directory: {self.data_dir}
{'='*60}
"""
        self.logger.info(header)
        
    def _generate_report(self):
        """Generate import summary report"""
        summary = f"""
{'='*60}
Import Summary
{'='*60}

Statistics:
  Total Files Found: {self.stats['total_files']:,}
  Files Processed: {self.stats['processed_files']:,}
  Files Skipped (duplicate): {self.stats['skipped_files']:,}
  
  Total Records Read: {self.stats['total_records_read']:,}
  Records Imported: {self.stats['records_imported']:,}
  Records Skipped: {self.stats['records_skipped']:,}
  Errors: {self.stats['errors']}
  
Processing Time: {self.stats['processing_time']:.1f} seconds ({self.stats['processing_time']/60:.1f} minutes)
Average Speed: {self.stats['total_records_read']/self.stats['processing_time'] if self.stats['processing_time'] > 0 else 0:,.0f} records/second

Status: {'✅ Import completed successfully' if self.stats['errors'] == 0 else '⚠️  Import completed with errors'}
{'='*60}
"""
        
        self.logger.info(summary)
        
        # Save report to file
        with open(self.report_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        self.logger.info(f"\n📊 Report saved: {self.report_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='FXCM Data Importer v2.0 - Import forex data from CSV to ClickHouse',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import all data with fast mode (default)
  python fxcm_importer.py
  
  # Import specific pairs
  python fxcm_importer.py --pairs EURUSD GBPUSD
  
  # Import only M1 data for 2024
  python fxcm_importer.py --timeframes M1 --start-year 2024 --end-year 2024
  
  # Use comprehensive validation mode
  python fxcm_importer.py --check-mode comprehensive
  
  # Custom ClickHouse server
  python fxcm_importer.py --ch-host 192.168.1.100 --ch-http-port 8123
"""
    )
    
    # Currency pairs
    parser.add_argument(
        '--pairs',
        nargs='+',
        choices=FXCMDataImporter.AVAILABLE_PAIRS,
        default=FXCMDataImporter.AVAILABLE_PAIRS,
        help='Currency pairs to import (default: all)'
    )
    
    # Timeframes
    parser.add_argument(
        '--timeframes',
        nargs='+',
        choices=FXCMDataImporter.AVAILABLE_TIMEFRAMES,
        default=FXCMDataImporter.AVAILABLE_TIMEFRAMES,
        help='Timeframes to import (default: M1 D1)'
    )
    
    # Date range
    parser.add_argument(
        '--start-year',
        type=int,
        default=2015,
        help='Start year (default: 2015)'
    )
    
    parser.add_argument(
        '--end-year',
        type=int,
        default=datetime.now().year,
        help='End year (default: current year)'
    )
    
    # Check mode
    parser.add_argument(
        '--check-mode',
        choices=FXCMDataImporter.CHECK_MODES,
        default='fast',
        help='Validation mode: fast (check first/last) or comprehensive (check all) (default: fast)'
    )
    
    # Load default ClickHouse config
    ch_config = load_clickhouse_config()
    
    # ClickHouse connection
    parser.add_argument(
        '--ch-host',
        default=ch_config.get('host', '192.168.2.168'),
        help=f"ClickHouse host (default: {ch_config.get('host', '192.168.2.168')})"
    )
    
    parser.add_argument(
        '--ch-http-port',
        type=int,
        default=ch_config.get('http_port', 8123),
        help=f"ClickHouse HTTP port (default: {ch_config.get('http_port', 8123)})"
    )
    
    parser.add_argument(
        '--ch-user',
        default=ch_config.get('user', 'default'),
        help=f"ClickHouse username (default: {ch_config.get('user', 'default')})"
    )
    
    parser.add_argument(
        '--ch-password',
        default=ch_config.get('password', ''),
        help='ClickHouse password (default: from config file or empty)'
    )
    
    args = parser.parse_args()
    
    # Create importer
    importer = FXCMDataImporter(
        ch_host=args.ch_host,
        ch_http_port=args.ch_http_port,
        ch_user=args.ch_user,
        ch_password=args.ch_password
    )
    
    # Run import
    success = importer.import_data(
        pairs=args.pairs,
        timeframes=args.timeframes,
        start_year=args.start_year,
        end_year=args.end_year,
        check_mode=args.check_mode
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
