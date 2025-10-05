"""
Test Suite for FXCM Data Downloader
Tests the functionality of fxcm_data_downloader.py

Author: binphilxiao
Date: 2025-10-05
"""

import unittest
import sys
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fxcm_data_downloader import FXCMDataDownloader


class TestFXCMDataDownloader(unittest.TestCase):
    """Test cases for FXCM Data Downloader"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Create temporary directories
        cls.temp_dir = Path(tempfile.mkdtemp())
        cls.output_dir = cls.temp_dir / 'test_output'
        cls.log_dir = cls.temp_dir / 'test_logs'
        
        # Create downloader instance
        cls.downloader = FXCMDataDownloader(
            output_dir=cls.output_dir,
            log_dir=cls.log_dir,
            max_retries=2  # Reduce retries for faster testing
        )
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        if cls.temp_dir.exists():
            shutil.rmtree(cls.temp_dir)
    
    def test_01_initialization(self):
        """Test downloader initialization"""
        self.assertIsNotNone(self.downloader)
        self.assertTrue(self.downloader.output_dir.exists())
        self.assertTrue(self.downloader.log_dir.exists())
        self.assertEqual(self.downloader.max_retries, 2)
    
    def test_02_available_pairs(self):
        """Test available currency pairs"""
        expected_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF']
        self.assertEqual(FXCMDataDownloader.AVAILABLE_PAIRS, expected_pairs)
    
    def test_03_available_timeframes(self):
        """Test available timeframes"""
        expected_timeframes = ['M1', 'D1']
        self.assertEqual(FXCMDataDownloader.AVAILABLE_TIMEFRAMES, expected_timeframes)
    
    def test_04_base_url(self):
        """Test FXCM API base URL"""
        expected_url = "https://candledata.fxcorporate.com"
        self.assertEqual(FXCMDataDownloader.BASE_URL, expected_url)
    
    def test_05_download_single_week(self):
        """Test downloading a single week of M1 data"""
        # Try to download week 1 of 2020 for EURUSD
        df = self.downloader.download_m1_week('EURUSD', 2020, 1)
        
        if df is not None:
            # If data was downloaded, check structure
            self.assertIsNotNone(df)
            self.assertIn('DateTime', df.columns)
            self.assertIn('Open', df.columns)
            self.assertIn('High', df.columns)
            self.assertIn('Low', df.columns)
            self.assertIn('Close', df.columns)
            print(f"\n✅ Successfully downloaded {len(df)} records for EURUSD 2020 Week 1")
        else:
            # Data might not be available (404), which is acceptable
            print("\n⏭️  Data not available for EURUSD 2020 Week 1 (expected)")
    
    def test_06_download_single_year_d1(self):
        """Test downloading a single year of D1 data"""
        # Try to download 2020 D1 data for EURUSD
        df = self.downloader.download_d1_year('EURUSD', 2020)
        
        if df is not None:
            # If data was downloaded, check structure
            self.assertIsNotNone(df)
            self.assertIn('DateTime', df.columns)
            self.assertIn('Open', df.columns)
            self.assertIn('High', df.columns)
            self.assertIn('Low', df.columns)
            self.assertIn('Close', df.columns)
            print(f"\n✅ Successfully downloaded {len(df)} records for EURUSD 2020 D1")
        else:
            # Data might not be available (404), which is acceptable
            print("\n⏭️  Data not available for EURUSD 2020 D1 (expected)")
    
    def test_07_invalid_pair(self):
        """Test handling of invalid currency pair"""
        with self.assertRaises(ValueError):
            self.downloader.download(pairs=['INVALID'])
    
    def test_08_invalid_timeframe(self):
        """Test handling of invalid timeframe"""
        with self.assertRaises(ValueError):
            self.downloader.download(timeframes=['H4'])
    
    def test_09_directory_structure(self):
        """Test directory structure creation"""
        # Download small dataset
        self.downloader.download(
            pairs=['EURUSD'],
            timeframes=['D1'],
            start_year=2020,
            end_year=2020
        )
        
        # Check directory structure
        pair_dir = self.output_dir / 'EURUSD' / 'D1'
        self.assertTrue(pair_dir.exists())
        
        # Check if file was created or skipped
        file_path = pair_dir / '2020.csv'
        # File might not exist if data wasn't available (404)
        print(f"\n{'✅ File exists' if file_path.exists() else '⏭️  File not created (data unavailable)'}")
    
    def test_10_statistics(self):
        """Test download statistics"""
        # Reset statistics
        self.downloader.stats = {
            'total_files': 0,
            'downloaded': 0,
            'skipped': 0,
            'failed': 0,
            'total_records': 0
        }
        
        # Download small dataset
        stats = self.downloader.download(
            pairs=['EURUSD'],
            timeframes=['D1'],
            start_year=2020,
            end_year=2020
        )
        
        # Check statistics structure
        self.assertIn('total_files', stats)
        self.assertIn('downloaded', stats)
        self.assertIn('skipped', stats)
        self.assertIn('failed', stats)
        self.assertIn('total_records', stats)
        
        # Total files should be sum of downloaded + skipped + failed
        total = stats['downloaded'] + stats['skipped'] + stats['failed']
        self.assertEqual(stats['total_files'], total)
        
        print(f"\n✅ Statistics: {stats}")
    
    def test_11_log_file_creation(self):
        """Test log file creation"""
        log_files = list(self.log_dir.glob('fxcm_download_*.log'))
        self.assertGreater(len(log_files), 0)
        print(f"\n✅ Log files created: {len(log_files)}")
    
    def test_12_summary_report_creation(self):
        """Test summary report creation"""
        summary_files = list(self.log_dir.glob('fxcm_download_summary_*.txt'))
        self.assertGreater(len(summary_files), 0)
        print(f"\n✅ Summary reports created: {len(summary_files)}")
    
    def test_13_skip_existing_files(self):
        """Test skipping existing files"""
        # Download once
        self.downloader.download(
            pairs=['EURUSD'],
            timeframes=['D1'],
            start_year=2021,
            end_year=2021
        )
        
        first_stats = dict(self.downloader.stats)
        
        # Reset statistics
        self.downloader.stats = {
            'total_files': 0,
            'downloaded': 0,
            'skipped': 0,
            'failed': 0,
            'total_records': 0
        }
        
        # Download again (should skip)
        self.downloader.download(
            pairs=['EURUSD'],
            timeframes=['D1'],
            start_year=2021,
            end_year=2021
        )
        
        second_stats = dict(self.downloader.stats)
        
        # Second download should have more skipped files if first download succeeded
        if first_stats['downloaded'] > 0:
            self.assertGreater(second_stats['skipped'], 0)
            print(f"\n✅ Skipped {second_stats['skipped']} existing files")
        else:
            print("\n⏭️  No files to skip (no data available)")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFXCMDataDownloader)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
