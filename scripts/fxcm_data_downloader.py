"""
FXCM Historical Data Downloader v2.0
Download historical forex data from FXCM's public API

Author: binphilxiao
Date: 2025-10-05
Version: 2.0.0
License: MIT
"""

import os
import sys
import io
import json
import argparse
import requests
import gzip
import pandas as pd
from datetime import datetime
import time
from pathlib import Path
import logging
from typing import Optional, List

# Import progress grid module
from progress_grid import ProgressGrid, ProgressStatus

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class FXCMDataDownloader:
    """
    FXCM Historical Data Downloader
    
    Downloads forex historical data from FXCM's public API and saves to local CSV files.
    Supports multiple currency pairs, timeframes (M1, D1), and date ranges.
    
    Attributes:
        AVAILABLE_PAIRS (list): List of supported currency pairs
        AVAILABLE_TIMEFRAMES (list): List of supported timeframes
        BASE_URL (str): FXCM API base URL
    """
    
    # Available currency pairs
    AVAILABLE_PAIRS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF']
    
    # Available timeframes
    AVAILABLE_TIMEFRAMES = ['M1', 'D1']
    
    # FXCM API base URL
    BASE_URL = "https://candledata.fxcorporate.com"
    
    def __init__(self, 
                 output_dir: Path = None,
                 log_dir: Path = None,
                 max_retries: int = 5,
                 retry_delay: float = 0.5):
        """
        Initialize FXCM Data Downloader
        
        Args:
            output_dir (Path): Directory to save downloaded data (default: fxcm_data/)
            log_dir (Path): Directory to save log files (default: logs/)
            max_retries (int): Maximum number of retry attempts for failed downloads
            retry_delay (float): Delay in seconds between retry attempts
        """
        # Set directories
        self.project_root = Path(__file__).parent.parent
        self.output_dir = output_dir or self.project_root / 'fxcm_data'
        self.log_dir = log_dir or self.project_root / 'logs'
        
        # Create directories
        self.output_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
        
        # Download settings
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Statistics
        self.stats = {
            'total_files': 0,
            'downloaded': 0,
            'skipped': 0,
            'failed': 0,
            'total_records': 0
        }
        
        # Setup logging
        self._setup_logging()
        
        # Progress grid for visual feedback
        self.progress_grid = ProgressGrid("FXCM 数据下载进度")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.log_dir / f'fxcm_download_{timestamp}.log'
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter('%(message)s')
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"Log file: {log_file}")
        self.log_file = log_file
    
    def _download_with_retry(self, url: str) -> Optional[pd.DataFrame]:
        """
        Download data from URL with retry mechanism
        
        Args:
            url (str): URL to download
            
        Returns:
            pd.DataFrame: DataFrame containing the downloaded data, or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    # Decompress gzip data
                    decompressed = gzip.decompress(response.content)
                    
                    # Parse CSV
                    from io import StringIO
                    df = pd.read_csv(StringIO(decompressed.decode('utf-8')))
                    
                    # Normalize column names
                    df = self._normalize_columns(df)
                    
                    if df is not None:
                        self.logger.debug(f"✅ Downloaded: {url} ({len(df)} records)")
                        return df
                    else:
                        self.logger.warning(f"⚠️ Unknown CSV format: {url}")
                        return None
                
                elif response.status_code == 404:
                    # 404 error - data doesn't exist
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        self.logger.debug(f"❌ 404 Not Found (after {self.max_retries} retries): {url}")
                        return None
                
                else:
                    self.logger.warning(f"⚠️ HTTP {response.status_code}: {url}")
                    return None
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    self.logger.error(f"❌ Download failed (after {self.max_retries} retries): {url} - {e}")
                    return None
        
        return None
    
    def _normalize_columns(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Normalize CSV column names to standard format
        
        Args:
            df (pd.DataFrame): Raw DataFrame from CSV
            
        Returns:
            pd.DataFrame: Normalized DataFrame with standard column names
        """
        # Convert all column names to lowercase for comparison
        df.columns = df.columns.str.lower()
        
        # Check for datetime column
        if 'datetime' not in df.columns:
            return None
        
        # Rename columns based on detected format
        if 'bidopen' in df.columns:
            # FXCM format with Bid prefix
            df = df.rename(columns={
                'datetime': 'DateTime',
                'bidopen': 'Open',
                'bidhigh': 'High',
                'bidlow': 'Low',
                'bidclose': 'Close'
            })
        else:
            # Standard format
            df = df.rename(columns={
                'datetime': 'DateTime',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close'
            })
        
        # Parse datetime
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        
        # Keep only required columns
        required_cols = ['DateTime', 'Open', 'High', 'Low', 'Close']
        df = df[required_cols]
        
        return df
    
    def download_m1_week(self, 
                        pair: str, 
                        year: int, 
                        week: int) -> Optional[pd.DataFrame]:
        """
        Download M1 data for a specific week
        
        Args:
            pair (str): Currency pair (e.g., 'EURUSD')
            year (int): Year (e.g., 2020)
            week (int): Week number (1-52)
            
        Returns:
            pd.DataFrame: DataFrame containing the weekly M1 data
        """
        url = f"{self.BASE_URL}/m1/{pair}/{year}/{week}.csv.gz"
        return self._download_with_retry(url)
    
    def download_d1_year(self, 
                        pair: str, 
                        year: int) -> Optional[pd.DataFrame]:
        """
        Download D1 data for a specific year
        
        Args:
            pair (str): Currency pair (e.g., 'EURUSD')
            year (int): Year (e.g., 2020)
            
        Returns:
            pd.DataFrame: DataFrame containing the yearly D1 data
        """
        url = f"{self.BASE_URL}/D1/{pair}/{year}.csv.gz"
        return self._download_with_retry(url)
    
    def download_pair_timeframe(self,
                               pair: str,
                               timeframe: str,
                               start_year: int,
                               end_year: int) -> dict:
        """
        Download all data for a specific pair and timeframe
        
        Args:
            pair (str): Currency pair
            timeframe (str): Timeframe ('M1' or 'D1')
            start_year (int): Start year
            end_year (int): End year (inclusive)
            
        Returns:
            dict: Dictionary with download statistics
        """
        stats = {'downloaded': 0, 'skipped': 0, 'failed': 0, 'records': 0}
        
        # Create directory structure
        pair_dir = self.output_dir / pair / timeframe
        
        if timeframe == 'M1':
            # M1: Download by week and save to year folders
            for year in range(start_year, end_year + 1):
                year_dir = pair_dir / str(year)
                year_dir.mkdir(parents=True, exist_ok=True)
                
                # Initialize progress grid for this year
                self.progress_grid.initialize_grid(pair, timeframe, year, 52)
                
                for week in range(1, 53):
                    self.stats['total_files'] += 1
                    
                    # Check if file exists
                    filename = year_dir / f"week_{week:02d}.csv"
                    if filename.exists():
                        self.logger.debug(f"  Week {week:02d}/52... ⏭️  Already exists, skipped")
                        stats['skipped'] += 1
                        self.stats['skipped'] += 1
                        # Update progress grid - skipped
                        self.progress_grid.update_status(pair, timeframe, year, week - 1, ProgressStatus.SKIPPED)
                    else:
                        # Download data
                        self.logger.debug(f"  Week {week:02d}/52...")
                        df = self.download_m1_week(pair, year, week)
                        
                        if df is not None and not df.empty:
                            # Save to CSV
                            df.to_csv(filename, index=False)
                            records = len(df)
                            stats['downloaded'] += 1
                            stats['records'] += records
                            self.stats['downloaded'] += 1
                            self.stats['total_records'] += records
                            self.logger.debug(f"    ✅ {records} records -> {filename.name}")
                            # Update progress grid - success
                            self.progress_grid.update_status(pair, timeframe, year, week - 1, ProgressStatus.SUCCESS)
                        else:
                            stats['failed'] += 1
                            self.stats['failed'] += 1
                            self.logger.debug(f"    ⏭️  No data available")
                            # Update progress grid - error
                            self.progress_grid.update_status(pair, timeframe, year, week - 1, ProgressStatus.ERROR)
                        
                        time.sleep(0.1)  # Rate limiting
                    
                    # Display progress line
                    self.progress_grid.display_line(pair, timeframe, year)
                
                # Newline after year
                self.progress_grid.newline()
        
        elif timeframe == 'D1':
            # D1: Download by year
            pair_dir.mkdir(parents=True, exist_ok=True)
            
            years_list = list(range(start_year, end_year + 1))
            # Initialize progress grid for D1 years
            self.progress_grid.initialize_grid(pair, timeframe, 0, len(years_list))
            year_index = 0
            
            for year in years_list:
                self.stats['total_files'] += 1
                
                # Check if file exists
                filename = pair_dir / f"{year}.csv"
                if filename.exists():
                    self.logger.debug(f"\n📥 Downloading {pair} {year} D1 data... ⏭️  Already exists, skipped")
                    stats['skipped'] += 1
                    self.stats['skipped'] += 1
                    # Update progress grid - skipped
                    self.progress_grid.update_status(pair, timeframe, 0, year_index, ProgressStatus.SKIPPED)
                else:
                    # Download data
                    self.logger.debug(f"\n📥 Downloading {pair} {year} D1 data...")
                    df = self.download_d1_year(pair, year)
                    
                    if df is not None and not df.empty:
                        # Save to CSV
                        df.to_csv(filename, index=False)
                        records = len(df)
                        stats['downloaded'] += 1
                        stats['records'] += records
                        self.stats['downloaded'] += 1
                        self.stats['total_records'] += records
                        self.logger.debug(f"  ✅ {records} records -> {filename.name}")
                        # Update progress grid - success
                        self.progress_grid.update_status(pair, timeframe, 0, year_index, ProgressStatus.SUCCESS)
                    else:
                        stats['failed'] += 1
                        self.stats['failed'] += 1
                        self.logger.debug(f"  ⏭️  No data available")
                        # Update progress grid - error
                        self.progress_grid.update_status(pair, timeframe, 0, year_index, ProgressStatus.ERROR)
                    
                    time.sleep(0.1)  # Rate limiting
                
                # Display progress line
                self.progress_grid.display_line(pair, timeframe, 0, f"{pair} {timeframe}")
                year_index += 1
            
            # Newline after all years
            self.progress_grid.newline()
        
        return stats
    
    def download(self,
                pairs: List[str] = None,
                timeframes: List[str] = None,
                start_year: int = 2015,
                end_year: int = None) -> dict:
        """
        Download FXCM historical data
        
        Args:
            pairs (list): List of currency pairs (default: all available pairs)
            timeframes (list): List of timeframes (default: ['M1', 'D1'])
            start_year (int): Start year (default: 2015)
            end_year (int): End year (default: current year)
            
        Returns:
            dict: Dictionary with download statistics
        """
        # Set defaults
        if pairs is None:
            pairs = self.AVAILABLE_PAIRS
        if timeframes is None:
            timeframes = ['M1', 'D1']
        if end_year is None:
            end_year = datetime.now().year
        
        # Validate inputs
        invalid_pairs = [p for p in pairs if p not in self.AVAILABLE_PAIRS]
        if invalid_pairs:
            raise ValueError(f"Invalid currency pairs: {invalid_pairs}")
        
        invalid_tfs = [tf for tf in timeframes if tf not in self.AVAILABLE_TIMEFRAMES]
        if invalid_tfs:
            raise ValueError(f"Invalid timeframes: {invalid_tfs}")
        
        # Print header
        self._print_header(pairs, timeframes, start_year, end_year)
        
        # Download data
        start_time = time.time()
        
        for pair in pairs:
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Processing: {pair}")
            self.logger.info(f"{'='*60}")
            
            for timeframe in timeframes:
                self.logger.info(f"\n{'='*50}")
                self.logger.info(f"Timeframe: {timeframe}")
                self.logger.info(f"{'='*50}")
                
                self.download_pair_timeframe(pair, timeframe, start_year, end_year)
        
        # Calculate elapsed time
        elapsed = time.time() - start_time
        
        # Display progress grid summary and legend
        self.progress_grid.print_legend()
        self.progress_grid.print_summary()
        
        # Print summary
        self._print_summary(elapsed)
        
        # Save summary to log
        self._save_summary_report(pairs, timeframes, start_year, end_year, elapsed)
        
        return self.stats
    
    def _print_header(self, pairs, timeframes, start_year, end_year):
        """Print download header"""
        self.logger.info("="*60)
        self.logger.info("FXCM Historical Data Downloader v2.0")
        self.logger.info("="*60)
        self.logger.info(f"Currency Pairs: {', '.join(pairs)}")
        self.logger.info(f"Timeframes: {', '.join(timeframes)}")
        self.logger.info(f"Date Range: {start_year} - {end_year}")
        self.logger.info(f"Output Directory: {self.output_dir.absolute()}")
        self.logger.info(f"Max Retries: {self.max_retries}")
        self.logger.info("="*60)
    
    def _print_summary(self, elapsed):
        """Print download summary"""
        self.logger.info("\n" + "="*60)
        self.logger.info("Download Summary")
        self.logger.info("="*60)
        self.logger.info(f"Total Files Processed: {self.stats['total_files']}")
        self.logger.info(f"  ✅ Downloaded: {self.stats['downloaded']}")
        self.logger.info(f"  ⏭️  Skipped (existing): {self.stats['skipped']}")
        self.logger.info(f"  ❌ Failed/Not Available: {self.stats['failed']}")
        self.logger.info(f"Total Records Downloaded: {self.stats['total_records']:,}")
        self.logger.info(f"Time Elapsed: {elapsed:.1f} seconds")
        self.logger.info("="*60)
        self.logger.info(f"✅ Download completed successfully!")
        self.logger.info(f"📄 Log file saved: {self.log_file}")
        self.logger.info("="*60)
    
    def _save_summary_report(self, pairs, timeframes, start_year, end_year, elapsed):
        """Save summary report to log directory"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.log_dir / f'fxcm_download_summary_{timestamp}.txt'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("FXCM Data Download Summary Report\n")
            f.write("="*60 + "\n\n")
            
            f.write("Configuration:\n")
            f.write(f"  Currency Pairs: {', '.join(pairs)}\n")
            f.write(f"  Timeframes: {', '.join(timeframes)}\n")
            f.write(f"  Date Range: {start_year} - {end_year}\n")
            f.write(f"  Output Directory: {self.output_dir.absolute()}\n")
            f.write(f"  Max Retries: {self.max_retries}\n\n")
            
            f.write("Results:\n")
            f.write(f"  Total Files Processed: {self.stats['total_files']}\n")
            f.write(f"  Downloaded: {self.stats['downloaded']}\n")
            f.write(f"  Skipped (existing): {self.stats['skipped']}\n")
            f.write(f"  Failed/Not Available: {self.stats['failed']}\n")
            f.write(f"  Total Records: {self.stats['total_records']:,}\n")
            f.write(f"  Time Elapsed: {elapsed:.1f} seconds\n\n")
            
            f.write(f"Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n")
        
        self.logger.info(f"📊 Summary report saved: {report_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='FXCM Historical Data Downloader v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all pairs, all timeframes, 2015-now
  python fxcm_data_downloader.py
  
  # Download specific pair
  python fxcm_data_downloader.py --pairs EURUSD
  
  # Download multiple pairs
  python fxcm_data_downloader.py --pairs EURUSD GBPUSD USDJPY
  
  # Download only M1 data
  python fxcm_data_downloader.py --timeframes M1
  
  # Download specific date range
  python fxcm_data_downloader.py --start-year 2020 --end-year 2023
  
  # Combine options
  python fxcm_data_downloader.py --pairs EURUSD --timeframes D1 --start-year 2018
        """
    )
    
    parser.add_argument(
        '--pairs',
        nargs='+',
        choices=FXCMDataDownloader.AVAILABLE_PAIRS,
        help='Currency pairs to download (default: all)'
    )
    
    parser.add_argument(
        '--timeframes',
        nargs='+',
        choices=FXCMDataDownloader.AVAILABLE_TIMEFRAMES,
        help='Timeframes to download (default: M1 D1)'
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
        '--max-retries',
        type=int,
        default=5,
        help='Maximum retry attempts for failed downloads (default: 5)'
    )
    
    args = parser.parse_args()
    
    # Create downloader
    downloader = FXCMDataDownloader(max_retries=args.max_retries)
    
    # Download data
    try:
        downloader.download(
            pairs=args.pairs,
            timeframes=args.timeframes,
            start_year=args.start_year,
            end_year=args.end_year
        )
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
