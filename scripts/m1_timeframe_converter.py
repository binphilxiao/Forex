"""
M1 Timeframe Converter v2.0
Convert M1 forex data to multiple timeframes (M5, M15, M30, H1)

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
from datetime import datetime
from typing import List, Optional, Dict
import clickhouse_connect
from clickhouse_connect.driver.client import Client

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class M1TimeframeConverter:
    """
    M1 to Multi-Timeframe Converter
    
    Converts 1-minute forex data to higher timeframes (M5, M15, M30, H1)
    and stores the aggregated data in ClickHouse database.
    
    Attributes:
        AVAILABLE_PAIRS (list): List of supported currency pairs
        AVAILABLE_TIMEFRAMES (list): List of supported output timeframes
        AGGREGATION_RULES (dict): Rules for OHLC aggregation
    """
    
    # Available currency pairs
    AVAILABLE_PAIRS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF']
    
    # Available output timeframes
    AVAILABLE_TIMEFRAMES = ['M5', 'M15', 'M30', 'H1']
    
    # Timeframe configurations (in minutes)
    TIMEFRAME_MINUTES = {
        'M5': 5,
        'M15': 15,
        'M30': 30,
        'H1': 60
    }
    
    # OHLC aggregation rules
    AGGREGATION_RULES = {
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last'
    }
    
    def __init__(self,
                 ch_host: str = '192.168.2.168',
                 ch_port: int = 8123,
                 ch_user: str = 'default',
                 ch_password: str = '',
                 overwrite: bool = True):
        """
        Initialize M1 Timeframe Converter
        
        Args:
            ch_host (str): ClickHouse server hostname/IP
            ch_port (int): ClickHouse HTTP port (default: 8123)
            ch_user (str): ClickHouse username
            ch_password (str): ClickHouse password
            overwrite (bool): Whether to overwrite existing data
        """
        # ClickHouse connection parameters
        self.ch_host = ch_host
        self.ch_port = ch_port
        self.ch_user = ch_user
        self.ch_password = ch_password
        
        # Processing options
        self.overwrite = overwrite
        
        # ClickHouse client
        self.client: Optional[Client] = None
        
        # Statistics
        self.stats = {
            'total_pairs_processed': 0,
            'total_timeframes_generated': 0,
            'total_records_read': 0,
            'total_records_written': 0,
            'skipped_existing': 0,
            'errors': 0,
            'processing_time': 0
        }
        
        # Project paths
        self.project_root = Path(__file__).parent.parent
        self.log_dir = self.project_root / 'logs'
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging configuration"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.log_dir / f'm1_converter_{timestamp}.log'
        
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
        
    def connect_clickhouse(self):
        """Establish connection to ClickHouse"""
        try:
            self.client = clickhouse_connect.get_client(
                host=self.ch_host,
                port=self.ch_port,
                username=self.ch_user,
                password=self.ch_password
            )
            self.logger.info(f"✅ Connected to ClickHouse at {self.ch_host}:{self.ch_port}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to ClickHouse: {e}")
            return False
            
    def disconnect_clickhouse(self):
        """Close ClickHouse connection"""
        if self.client:
            self.client.close()
            self.logger.info("ClickHouse connection closed")
            
    def get_table_name(self, pair: str, timeframe: str) -> str:
        """
        Get ClickHouse table name for pair and timeframe
        
        Args:
            pair (str): Currency pair
            timeframe (str): Timeframe (M5, M15, M30, H1)
            
        Returns:
            str: Table name
        """
        return f"forex_{pair.lower()}_{timeframe.lower()}"
        
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in ClickHouse"""
        try:
            result = self.client.command(
                f"EXISTS TABLE {table_name}"
            )
            return result == 1
        except Exception as e:
            self.logger.error(f"Error checking table existence: {e}")
            return False
            
    def get_existing_data_range(self, table_name: str, year: int) -> Optional[Dict]:
        """
        Get date range of existing data for a specific year
        
        Args:
            table_name (str): Table name
            year (int): Year to check
            
        Returns:
            dict: {'min_date': datetime, 'max_date': datetime, 'count': int} or None
        """
        try:
            query = f"""
            SELECT 
                min(DateTime) as min_date,
                max(DateTime) as max_date,
                count() as count
            FROM {table_name}
            WHERE toYear(DateTime) = {year}
            """
            result = self.client.query(query)
            if result.result_rows:
                row = result.result_rows[0]
                if row[2] > 0:  # count > 0
                    return {
                        'min_date': row[0],
                        'max_date': row[1],
                        'count': row[2]
                    }
            return None
        except Exception as e:
            self.logger.warning(f"Table {table_name} may not exist yet: {e}")
            return None
            
    def read_m1_data(self, pair: str, year: int) -> Optional[pd.DataFrame]:
        """
        Read M1 data from ClickHouse for a specific year
        
        Args:
            pair (str): Currency pair
            year (int): Year to read
            
        Returns:
            pd.DataFrame: M1 data or None if failed
        """
        try:
            table_name = f"forex_{pair.lower()}_m1"
            
            query = f"""
            SELECT 
                DateTime,
                Open,
                High,
                Low,
                Close
            FROM {table_name}
            WHERE toYear(DateTime) = {year}
            ORDER BY DateTime
            """
            
            result = self.client.query_df(query)
            
            if len(result) == 0:
                self.logger.warning(f"No M1 data found for {pair} {year}")
                return None
                
            # Ensure DateTime is datetime type
            result['DateTime'] = pd.to_datetime(result['DateTime'])
            
            self.logger.info(f"  📥 Read {len(result):,} M1 records for {pair} {year}")
            return result
            
        except Exception as e:
            self.logger.error(f"  ❌ Error reading M1 data for {pair} {year}: {e}")
            return None
            
    def aggregate_to_timeframe(self, 
                               df: pd.DataFrame, 
                               timeframe: str) -> pd.DataFrame:
        """
        Aggregate M1 data to specified timeframe
        
        Args:
            df (pd.DataFrame): M1 data with columns [DateTime, Open, High, Low, Close]
            timeframe (str): Target timeframe (M5, M15, M30, H1)
            
        Returns:
            pd.DataFrame: Aggregated data
        """
        # Handle empty dataframe
        if len(df) == 0:
            return pd.DataFrame(columns=['DateTime', 'Open', 'High', 'Low', 'Close'])
        
        minutes = self.TIMEFRAME_MINUTES[timeframe]
        
        # Set DateTime as index for resampling
        df = df.set_index('DateTime')
        
        # Resample and aggregate (using 'min' instead of deprecated 'T')
        aggregated = df.resample(f'{minutes}min').agg(self.AGGREGATION_RULES)
        
        # Remove rows with NaN (periods with no data)
        aggregated = aggregated.dropna()
        
        # Reset index to make DateTime a column again
        aggregated = aggregated.reset_index()
        
        return aggregated
        
    def write_to_clickhouse(self, 
                            df: pd.DataFrame, 
                            pair: str, 
                            timeframe: str) -> bool:
        """
        Write aggregated data to ClickHouse
        
        Args:
            df (pd.DataFrame): Aggregated data
            pair (str): Currency pair
            timeframe (str): Timeframe
            
        Returns:
            bool: Success status
        """
        try:
            table_name = self.get_table_name(pair, timeframe)
            
            # Create table if not exists
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name}
            (
                DateTime DateTime,
                Open Float64,
                High Float64,
                Low Float64,
                Close Float64
            )
            ENGINE = MergeTree()
            ORDER BY DateTime
            """
            
            self.client.command(create_table_sql)
            
            # Insert data
            self.client.insert_df(table_name, df)
            
            self.logger.info(f"  ✅ Wrote {len(df):,} records to {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"  ❌ Error writing to ClickHouse: {e}")
            return False
            
    def convert_pair_year_timeframe(self,
                                    pair: str,
                                    year: int,
                                    timeframe: str) -> bool:
        """
        Convert M1 data for one pair, year, and timeframe
        
        Args:
            pair (str): Currency pair
            year (int): Year to process
            timeframe (str): Target timeframe
            
        Returns:
            bool: Success status
        """
        table_name = self.get_table_name(pair, timeframe)
        
        # Check if data already exists
        if not self.overwrite:
            existing = self.get_existing_data_range(table_name, year)
            if existing and existing['count'] > 0:
                self.logger.info(f"  ⏭️  Skipping {pair} {year} {timeframe} - "
                               f"{existing['count']} records already exist")
                self.stats['skipped_existing'] += 1
                return True
                
        # Read M1 data
        m1_data = self.read_m1_data(pair, year)
        if m1_data is None or len(m1_data) == 0:
            return False
            
        self.stats['total_records_read'] += len(m1_data)
        
        # Aggregate to target timeframe
        aggregated = self.aggregate_to_timeframe(m1_data, timeframe)
        
        if len(aggregated) == 0:
            self.logger.warning(f"  ⚠️  No data after aggregation for {pair} {year} {timeframe}")
            return False
            
        # Write to ClickHouse
        success = self.write_to_clickhouse(aggregated, pair, timeframe)
        
        if success:
            self.stats['total_records_written'] += len(aggregated)
            self.stats['total_timeframes_generated'] += 1
            
        return success
        
    def convert(self,
               pairs: Optional[List[str]] = None,
               timeframes: Optional[List[str]] = None,
               start_year: int = 2015,
               end_year: Optional[int] = None) -> bool:
        """
        Main conversion method
        
        Args:
            pairs (list): List of currency pairs (default: all)
            timeframes (list): List of timeframes to generate (default: all)
            start_year (int): Start year
            end_year (int): End year (default: current year)
            
        Returns:
            bool: Overall success status
        """
        start_time = datetime.now()
        
        # Set defaults
        if pairs is None:
            pairs = self.AVAILABLE_PAIRS
        if timeframes is None:
            timeframes = self.AVAILABLE_TIMEFRAMES
        if end_year is None:
            end_year = datetime.now().year
            
        # Connect to ClickHouse
        if not self.connect_clickhouse():
            return False
            
        try:
            self._print_header(pairs, timeframes, start_year, end_year)
            
            # Process each pair
            for pair in pairs:
                self.logger.info(f"\n{'='*60}")
                self.logger.info(f"Processing: {pair}")
                self.logger.info(f"{'='*60}")
                
                # Process each year
                for year in range(start_year, end_year + 1):
                    self.logger.info(f"\n📅 Year: {year}")
                    
                    # Process each timeframe
                    for timeframe in timeframes:
                        self.logger.info(f"\n⏱️  Timeframe: {timeframe}")
                        
                        success = self.convert_pair_year_timeframe(pair, year, timeframe)
                        
                        if not success:
                            self.stats['errors'] += 1
                            
                self.stats['total_pairs_processed'] += 1
                
            # Print summary
            end_time = datetime.now()
            self.stats['processing_time'] = (end_time - start_time).total_seconds()
            self._print_summary()
            self._save_report(start_time, end_time)
            
            return True
            
        finally:
            self.disconnect_clickhouse()
            
    def _print_header(self, pairs, timeframes, start_year, end_year):
        """Print conversion header"""
        self.logger.info("="*60)
        self.logger.info("M1 to Multi-Timeframe Converter v2.0")
        self.logger.info("="*60)
        self.logger.info(f"Currency Pairs: {', '.join(pairs)}")
        self.logger.info(f"Timeframes: {', '.join(timeframes)}")
        self.logger.info(f"Year Range: {start_year} - {end_year}")
        self.logger.info(f"ClickHouse: {self.ch_host}:{self.ch_port}")
        self.logger.info(f"Overwrite Mode: {'Yes' if self.overwrite else 'No (Skip existing)'}")
        self.logger.info("="*60)
        
    def _print_summary(self):
        """Print conversion summary"""
        self.logger.info("\n" + "="*60)
        self.logger.info("Conversion Summary")
        self.logger.info("="*60)
        self.logger.info(f"Pairs Processed: {self.stats['total_pairs_processed']}")
        self.logger.info(f"Timeframes Generated: {self.stats['total_timeframes_generated']}")
        self.logger.info(f"Records Read (M1): {self.stats['total_records_read']:,}")
        self.logger.info(f"Records Written: {self.stats['total_records_written']:,}")
        self.logger.info(f"Skipped (existing): {self.stats['skipped_existing']}")
        self.logger.info(f"Errors: {self.stats['errors']}")
        self.logger.info(f"Processing Time: {self.stats['processing_time']:.1f} seconds")
        self.logger.info("="*60)
        self.logger.info("✅ Conversion completed!")
        
    def _save_report(self, start_time, end_time):
        """Save conversion report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.log_dir / f'm1_converter_report_{timestamp}.txt'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("M1 to Multi-Timeframe Conversion Report\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {self.stats['processing_time']:.1f} seconds\n\n")
            
            f.write("Statistics:\n")
            f.write(f"  Pairs Processed: {self.stats['total_pairs_processed']}\n")
            f.write(f"  Timeframes Generated: {self.stats['total_timeframes_generated']}\n")
            f.write(f"  Records Read (M1): {self.stats['total_records_read']:,}\n")
            f.write(f"  Records Written: {self.stats['total_records_written']:,}\n")
            f.write(f"  Skipped (existing): {self.stats['skipped_existing']}\n")
            f.write(f"  Errors: {self.stats['errors']}\n\n")
            
            f.write("="*60 + "\n")
            
        self.logger.info(f"📊 Report saved: {report_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='M1 to Multi-Timeframe Converter v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all pairs, all timeframes, 2015-now
  python m1_timeframe_converter.py
  
  # Convert specific pair
  python m1_timeframe_converter.py --pairs EURUSD
  
  # Convert multiple pairs
  python m1_timeframe_converter.py --pairs EURUSD GBPUSD USDJPY
  
  # Convert specific timeframes
  python m1_timeframe_converter.py --timeframes M5 M15
  
  # Convert specific year range
  python m1_timeframe_converter.py --start-year 2020 --end-year 2023
  
  # Skip existing data (don't overwrite)
  python m1_timeframe_converter.py --skip-existing
  
  # Custom ClickHouse connection
  python m1_timeframe_converter.py --ch-host 192.168.1.100 --ch-port 8123
        """
    )
    
    parser.add_argument(
        '--pairs',
        nargs='+',
        choices=M1TimeframeConverter.AVAILABLE_PAIRS,
        help='Currency pairs to convert (default: all)'
    )
    
    parser.add_argument(
        '--timeframes',
        nargs='+',
        choices=M1TimeframeConverter.AVAILABLE_TIMEFRAMES,
        help='Timeframes to generate (default: M5 M15 M30 H1)'
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
        help='End year (default: current year)'
    )
    
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        help='Skip existing data instead of overwriting (default: overwrite)'
    )
    
    parser.add_argument(
        '--ch-host',
        default='192.168.2.168',
        help='ClickHouse host (default: 192.168.2.168)'
    )
    
    parser.add_argument(
        '--ch-port',
        type=int,
        default=8123,
        help='ClickHouse HTTP port (default: 8123)'
    )
    
    parser.add_argument(
        '--ch-user',
        default='default',
        help='ClickHouse username (default: default)'
    )
    
    parser.add_argument(
        '--ch-password',
        default='',
        help='ClickHouse password (default: empty)'
    )
    
    args = parser.parse_args()
    
    # Create converter
    converter = M1TimeframeConverter(
        ch_host=args.ch_host,
        ch_port=args.ch_port,
        ch_user=args.ch_user,
        ch_password=args.ch_password,
        overwrite=not args.skip_existing
    )
    
    # Run conversion
    try:
        success = converter.convert(
            pairs=args.pairs,
            timeframes=args.timeframes,
            start_year=args.start_year,
            end_year=args.end_year
        )
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
