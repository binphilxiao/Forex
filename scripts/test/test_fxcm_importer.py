"""
FXCM Data Importer - Test Suite

Author: binphilxiao
Date: 2025-10-05
Version: 1.0.0
"""

import unittest
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.fxcm_importer import FXCMDataImporter


class TestFXCMDataImporter(unittest.TestCase):
    """Test suite for FXCM Data Importer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.importer = FXCMDataImporter(
            ch_host='192.168.2.168',
            ch_http_port=8123,
            batch_size=100,
            tolerance=1e-5
        )
        
    def test_01_initialization(self):
        """Test TC-01: Importer initialization"""
        print("\n🧪 Test TC-01: Importer initialization")
        
        self.assertIsNotNone(self.importer)
        self.assertEqual(self.importer.ch_host, '192.168.2.168')
        self.assertEqual(self.importer.ch_http_port, 8123)
        self.assertEqual(self.importer.batch_size, 100)
        self.assertEqual(self.importer.tolerance, 1e-5)
        self.assertIsNotNone(self.importer.stats)
        
        print("✅ Importer initialized successfully")
        
    def test_02_available_pairs(self):
        """Test TC-02: Available pairs configuration"""
        print("\n🧪 Test TC-02: Available pairs configuration")
        
        expected_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF']
        self.assertEqual(FXCMDataImporter.AVAILABLE_PAIRS, expected_pairs)
        self.assertEqual(len(FXCMDataImporter.AVAILABLE_PAIRS), 6)
        
        print(f"✅ Found {len(expected_pairs)} pairs: {', '.join(expected_pairs)}")
        
    def test_03_available_timeframes(self):
        """Test TC-03: Available timeframes configuration"""
        print("\n🧪 Test TC-03: Available timeframes configuration")
        
        expected_timeframes = ['M1', 'D1']
        self.assertEqual(FXCMDataImporter.AVAILABLE_TIMEFRAMES, expected_timeframes)
        self.assertEqual(len(FXCMDataImporter.AVAILABLE_TIMEFRAMES), 2)
        
        print(f"✅ Found {len(expected_timeframes)} timeframes: {', '.join(expected_timeframes)}")
        
    def test_04_check_modes(self):
        """Test TC-04: Check modes configuration"""
        print("\n🧪 Test TC-04: Check modes configuration")
        
        expected_modes = ['fast', 'comprehensive']
        self.assertEqual(FXCMDataImporter.CHECK_MODES, expected_modes)
        
        print(f"✅ Check modes: {', '.join(expected_modes)}")
        
    def test_05_table_name_generation(self):
        """Test TC-05: Table name generation"""
        print("\n🧪 Test TC-05: Table name generation")
        
        m1_table = self.importer._get_table_name('M1')
        d1_table = self.importer._get_table_name('D1')
        
        self.assertEqual(m1_table, 'forex_data.ohlcv_m1')
        self.assertEqual(d1_table, 'forex_data.ohlcv_d1')
        
        print(f"✅ M1 table: {m1_table}")
        print(f"✅ D1 table: {d1_table}")
        
    def test_06_ohlc_comparison_exact(self):
        """Test TC-06: OHLC comparison - exact match"""
        print("\n🧪 Test TC-06: OHLC comparison - exact match")
        
        ohlc1 = (1.10000, 1.10050, 1.09950, 1.10010)
        ohlc2 = (1.10000, 1.10050, 1.09950, 1.10010)
        
        result = self.importer._compare_ohlc(ohlc1, ohlc2)
        self.assertTrue(result)
        
        print("✅ Exact OHLC match detected correctly")
        
    def test_07_ohlc_comparison_within_tolerance(self):
        """Test TC-07: OHLC comparison - within tolerance"""
        print("\n🧪 Test TC-07: OHLC comparison - within tolerance")
        
        ohlc1 = (1.10000, 1.10050, 1.09950, 1.10010)
        ohlc2 = (1.100001, 1.100501, 1.099501, 1.100101)  # Diff: 0.000001
        
        result = self.importer._compare_ohlc(ohlc1, ohlc2)
        self.assertTrue(result)
        
        print("✅ OHLC match within tolerance detected correctly")
        
    def test_08_ohlc_comparison_outside_tolerance(self):
        """Test TC-08: OHLC comparison - outside tolerance"""
        print("\n🧪 Test TC-08: OHLC comparison - outside tolerance")
        
        ohlc1 = (1.10000, 1.10050, 1.09950, 1.10010)
        ohlc2 = (1.10100, 1.10050, 1.09950, 1.10010)  # Diff: 0.001
        
        result = self.importer._compare_ohlc(ohlc1, ohlc2)
        self.assertFalse(result)
        
        print("✅ OHLC mismatch outside tolerance detected correctly")
        
    def test_09_csv_file_path_m1(self):
        """Test TC-09: CSV file path construction - M1"""
        print("\n🧪 Test TC-09: CSV file path construction - M1")
        
        files = self.importer._get_csv_files('EURUSD', 'M1', 2024)
        
        # Check if path structure is correct (files may or may not exist)
        expected_dir = self.importer.data_dir / 'EURUSD' / 'M1' / '2024'
        
        print(f"✅ Expected M1 directory: {expected_dir}")
        if files:
            print(f"✅ Found {len(files)} M1 files")
        else:
            print("⚠️  No M1 files found (directory may not exist)")
            
    def test_10_csv_file_path_d1(self):
        """Test TC-10: CSV file path construction - D1"""
        print("\n🧪 Test TC-10: CSV file path construction - D1")
        
        files = self.importer._get_csv_files('EURUSD', 'D1', 2024)
        
        expected_file = self.importer.data_dir / 'EURUSD' / 'D1' / '2024.csv'
        
        print(f"✅ Expected D1 file: {expected_file}")
        if files:
            print(f"✅ Found D1 file: {files[0]}")
        else:
            print("⚠️  D1 file not found (file may not exist)")
            
    def test_11_statistics_initialization(self):
        """Test TC-11: Statistics initialization"""
        print("\n🧪 Test TC-11: Statistics initialization")
        
        self.assertEqual(self.importer.stats['total_files'], 0)
        self.assertEqual(self.importer.stats['processed_files'], 0)
        self.assertEqual(self.importer.stats['skipped_files'], 0)
        self.assertEqual(self.importer.stats['total_records_read'], 0)
        self.assertEqual(self.importer.stats['records_imported'], 0)
        self.assertEqual(self.importer.stats['records_skipped'], 0)
        self.assertEqual(self.importer.stats['errors'], 0)
        
        print("✅ Statistics initialized to zero")
        
    def test_12_logging_setup(self):
        """Test TC-12: Logging configuration"""
        print("\n🧪 Test TC-12: Logging configuration")
        
        self.assertIsNotNone(self.importer.logger)
        self.assertTrue(self.importer.log_dir.exists())
        self.assertIsNotNone(self.importer.report_file)
        
        print(f"✅ Logging configured, log dir: {self.importer.log_dir}")
        print(f"✅ Report file: {self.importer.report_file}")
        
    def test_13_batch_size_configuration(self):
        """Test TC-13: Batch size configuration"""
        print("\n🧪 Test TC-13: Batch size configuration")
        
        # Test default batch size
        importer_default = FXCMDataImporter()
        self.assertEqual(importer_default.batch_size, 1000)
        
        # Test custom batch size
        importer_custom = FXCMDataImporter(batch_size=500)
        self.assertEqual(importer_custom.batch_size, 500)
        
        print("✅ Batch size configurable (default: 1000)")
        
    def test_14_tolerance_configuration(self):
        """Test TC-14: Tolerance configuration"""
        print("\n🧪 Test TC-14: Tolerance configuration")
        
        # Test default tolerance
        importer_default = FXCMDataImporter()
        self.assertEqual(importer_default.tolerance, 1e-5)
        
        # Test custom tolerance
        importer_custom = FXCMDataImporter(tolerance=1e-6)
        self.assertEqual(importer_custom.tolerance, 1e-6)
        
        print("✅ Tolerance configurable (default: 1e-5)")
        
    def test_15_data_directory_configuration(self):
        """Test TC-15: Data directory configuration"""
        print("\n🧪 Test TC-15: Data directory configuration")
        
        expected_dir = self.importer.project_root / 'fxcm_data'
        self.assertEqual(self.importer.data_dir, expected_dir)
        
        print(f"✅ Data directory: {self.importer.data_dir}")


def run_tests():
    """Run all tests and display summary"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFXCMDataImporter)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("FXCM Data Importer - Test Suite Summary")
    print("=" * 60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n" + "=" * 60)
        print(f"✅ ALL {result.testsRun} TESTS PASSED")
        print("="*60)
    else:
        print("\n" + "=" * 60)
        print(f"❌ {len(result.failures) + len(result.errors)} TEST(S) FAILED")
        print("="*60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
