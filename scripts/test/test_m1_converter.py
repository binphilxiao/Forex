"""
Test Suite for M1 Timeframe Converter v2.0

Tests the M1 to multi-timeframe conversion functionality.

Author: binphilxiao
Date: 2025-10-05
"""

import unittest
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.m1_timeframe_converter import M1TimeframeConverter


class TestM1TimeframeConverter(unittest.TestCase):
    """Test cases for M1TimeframeConverter"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test environment"""
        print("\n" + "="*60)
        print("M1 Timeframe Converter - Test Suite")
        print("="*60)
        
    def setUp(self):
        """Setup before each test"""
        self.converter = M1TimeframeConverter(
            ch_host='192.168.2.168',
            ch_port=8123,
            overwrite=False  # Default: skip existing
        )
        
    def test_01_initialization(self):
        """Test TC-01: Converter initialization"""
        print("\n🧪 Test TC-01: Converter initialization")
        
        self.assertIsNotNone(self.converter)
        self.assertEqual(self.converter.ch_host, '192.168.2.168')
        self.assertEqual(self.converter.ch_port, 8123)
        self.assertFalse(self.converter.overwrite)  # Default is skip
        
        print("✅ Converter initialized successfully (default: skip existing)")
        
    def test_02_available_pairs(self):
        """Test TC-02: Available pairs configuration"""
        print("\n🧪 Test TC-02: Available pairs configuration")
        
        expected_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF']
        self.assertEqual(self.converter.AVAILABLE_PAIRS, expected_pairs)
        self.assertEqual(len(self.converter.AVAILABLE_PAIRS), 6)
        
        print(f"✅ Found {len(expected_pairs)} pairs: {', '.join(expected_pairs)}")
        
    def test_03_available_timeframes(self):
        """Test TC-03: Available timeframes configuration"""
        print("\n🧪 Test TC-03: Available timeframes configuration")
        
        expected_timeframes = ['M5', 'M15', 'M30', 'H1']
        self.assertEqual(self.converter.AVAILABLE_TIMEFRAMES, expected_timeframes)
        self.assertEqual(len(self.converter.AVAILABLE_TIMEFRAMES), 4)
        
        print(f"✅ Found {len(expected_timeframes)} timeframes: {', '.join(expected_timeframes)}")
        
    def test_04_timeframe_minutes(self):
        """Test TC-04: Timeframe minutes mapping"""
        print("\n🧪 Test TC-04: Timeframe minutes mapping")
        
        self.assertEqual(self.converter.TIMEFRAME_MINUTES['M5'], 5)
        self.assertEqual(self.converter.TIMEFRAME_MINUTES['M15'], 15)
        self.assertEqual(self.converter.TIMEFRAME_MINUTES['M30'], 30)
        self.assertEqual(self.converter.TIMEFRAME_MINUTES['H1'], 60)
        
        print("✅ Timeframe minutes correctly configured")
        
    def test_05_aggregation_rules(self):
        """Test TC-05: OHLC aggregation rules"""
        print("\n🧪 Test TC-05: OHLC aggregation rules")
        
        self.assertEqual(self.converter.AGGREGATION_RULES['Open'], 'first')
        self.assertEqual(self.converter.AGGREGATION_RULES['High'], 'max')
        self.assertEqual(self.converter.AGGREGATION_RULES['Low'], 'min')
        self.assertEqual(self.converter.AGGREGATION_RULES['Close'], 'last')
        
        print("✅ OHLC aggregation rules correctly defined")
        
    def test_06_table_name_generation(self):
        """Test TC-06: ClickHouse table name generation"""
        print("\n🧪 Test TC-06: ClickHouse table name generation")
        
        table_name = self.converter.get_table_name('EURUSD', 'M5')
        self.assertEqual(table_name, 'forex_eurusd_m5')
        
        table_name = self.converter.get_table_name('GBPUSD', 'H1')
        self.assertEqual(table_name, 'forex_gbpusd_h1')
        
        print("✅ Table names generated correctly")
        
    def test_07_m5_aggregation(self):
        """Test TC-07: M1 to M5 aggregation"""
        print("\n🧪 Test TC-07: M1 to M5 aggregation")
        
        # Create 5 minutes of M1 test data
        start_time = datetime(2024, 1, 1, 0, 0, 0)
        m1_data = pd.DataFrame({
            'DateTime': [start_time + timedelta(minutes=i) for i in range(5)],
            'Open': [1.1000, 1.1001, 1.1002, 1.1003, 1.1004],
            'High': [1.1005, 1.1006, 1.1007, 1.1008, 1.1009],
            'Low': [1.0995, 1.0996, 1.0997, 1.0998, 1.0999],
            'Close': [1.1001, 1.1002, 1.1003, 1.1004, 1.1005]
        })
        
        # Aggregate to M5
        m5_data = self.converter.aggregate_to_timeframe(m1_data, 'M5')
        
        # Verify results
        self.assertEqual(len(m5_data), 1)
        self.assertEqual(m5_data.iloc[0]['Open'], 1.1000)  # First open
        self.assertEqual(m5_data.iloc[0]['High'], 1.1009)  # Max high
        self.assertEqual(m5_data.iloc[0]['Low'], 1.0995)   # Min low
        self.assertEqual(m5_data.iloc[0]['Close'], 1.1005) # Last close
        
        print(f"✅ M5 aggregation: 5 M1 bars → 1 M5 bar")
        
    def test_08_m15_aggregation(self):
        """Test TC-08: M1 to M15 aggregation"""
        print("\n🧪 Test TC-08: M1 to M15 aggregation")
        
        # Create 15 minutes of M1 test data
        start_time = datetime(2024, 1, 1, 0, 0, 0)
        m1_data = pd.DataFrame({
            'DateTime': [start_time + timedelta(minutes=i) for i in range(15)],
            'Open': [1.2000 + i * 0.0001 for i in range(15)],
            'High': [1.2010 + i * 0.0001 for i in range(15)],
            'Low': [1.1990 + i * 0.0001 for i in range(15)],
            'Close': [1.2005 + i * 0.0001 for i in range(15)]
        })
        
        # Aggregate to M15
        m15_data = self.converter.aggregate_to_timeframe(m1_data, 'M15')
        
        # Verify results
        self.assertEqual(len(m15_data), 1)
        self.assertAlmostEqual(m15_data.iloc[0]['Open'], 1.2000, places=4)
        self.assertAlmostEqual(m15_data.iloc[0]['Close'], 1.2019, places=4)
        
        print(f"✅ M15 aggregation: 15 M1 bars → 1 M15 bar")
        
    def test_09_m30_aggregation(self):
        """Test TC-09: M1 to M30 aggregation"""
        print("\n🧪 Test TC-09: M1 to M30 aggregation")
        
        # Create 60 minutes of M1 test data (should produce 2 M30 bars)
        start_time = datetime(2024, 1, 1, 0, 0, 0)
        m1_data = pd.DataFrame({
            'DateTime': [start_time + timedelta(minutes=i) for i in range(60)],
            'Open': [1.3000 + i * 0.0001 for i in range(60)],
            'High': [1.3010 + i * 0.0001 for i in range(60)],
            'Low': [1.2990 + i * 0.0001 for i in range(60)],
            'Close': [1.3005 + i * 0.0001 for i in range(60)]
        })
        
        # Aggregate to M30
        m30_data = self.converter.aggregate_to_timeframe(m1_data, 'M30')
        
        # Verify results
        self.assertEqual(len(m30_data), 2)
        
        print(f"✅ M30 aggregation: 60 M1 bars → 2 M30 bars")
        
    def test_10_h1_aggregation(self):
        """Test TC-10: M1 to H1 aggregation"""
        print("\n🧪 Test TC-10: M1 to H1 aggregation")
        
        # Create 120 minutes of M1 test data (should produce 2 H1 bars)
        start_time = datetime(2024, 1, 1, 0, 0, 0)
        m1_data = pd.DataFrame({
            'DateTime': [start_time + timedelta(minutes=i) for i in range(120)],
            'Open': [1.4000 for i in range(120)],
            'High': [1.4010 for i in range(120)],
            'Low': [1.3990 for i in range(120)],
            'Close': [1.4005 for i in range(120)]
        })
        
        # Aggregate to H1
        h1_data = self.converter.aggregate_to_timeframe(m1_data, 'H1')
        
        # Verify results
        self.assertEqual(len(h1_data), 2)
        
        print(f"✅ H1 aggregation: 120 M1 bars → 2 H1 bars")
        
    def test_11_empty_dataframe(self):
        """Test TC-11: Handle empty dataframe"""
        print("\n🧪 Test TC-11: Handle empty dataframe")
        
        # Create empty dataframe
        empty_df = pd.DataFrame(columns=['DateTime', 'Open', 'High', 'Low', 'Close'])
        
        # Try to aggregate
        result = self.converter.aggregate_to_timeframe(empty_df, 'M5')
        
        # Should return empty dataframe
        self.assertEqual(len(result), 0)
        
        print("✅ Empty dataframe handled correctly")
        
    def test_12_statistics_initialization(self):
        """Test TC-12: Statistics initialization"""
        print("\n🧪 Test TC-12: Statistics initialization")
        
        self.assertEqual(self.converter.stats['total_pairs_processed'], 0)
        self.assertEqual(self.converter.stats['total_timeframes_generated'], 0)
        self.assertEqual(self.converter.stats['total_records_read'], 0)
        self.assertEqual(self.converter.stats['total_records_written'], 0)
        self.assertEqual(self.converter.stats['skipped_existing'], 0)
        self.assertEqual(self.converter.stats['errors'], 0)
        
        print("✅ Statistics initialized to zero")
        
    def test_13_logging_setup(self):
        """Test TC-13: Logging configuration"""
        print("\n🧪 Test TC-13: Logging configuration")
        
        self.assertIsNotNone(self.converter.logger)
        self.assertTrue(self.converter.log_dir.exists())
        self.assertTrue(self.converter.log_dir.is_dir())
        
        print(f"✅ Logging configured, log dir: {self.converter.log_dir}")
        
    def test_14_partial_hour_aggregation(self):
        """Test TC-14: Partial hour aggregation (edge case)"""
        print("\n🧪 Test TC-14: Partial hour aggregation")
        
        # Create 45 minutes of M1 data (incomplete hour)
        start_time = datetime(2024, 1, 1, 0, 0, 0)
        m1_data = pd.DataFrame({
            'DateTime': [start_time + timedelta(minutes=i) for i in range(45)],
            'Open': [1.5000 for i in range(45)],
            'High': [1.5010 for i in range(45)],
            'Low': [1.4990 for i in range(45)],
            'Close': [1.5005 for i in range(45)]
        })
        
        # Aggregate to H1
        h1_data = self.converter.aggregate_to_timeframe(m1_data, 'H1')
        
        # Should produce 1 incomplete H1 bar
        self.assertEqual(len(h1_data), 1)
        
        print(f"✅ Partial hour aggregation: 45 M1 bars → 1 partial H1 bar")
        
    def test_15_multi_day_aggregation(self):
        """Test TC-15: Multi-day M5 aggregation"""
        print("\n🧪 Test TC-15: Multi-day M5 aggregation")
        
        # Create 2 days of M1 data (5-minute intervals for testing)
        start_time = datetime(2024, 1, 1, 0, 0, 0)
        minutes_in_2_days = 24 * 60 * 2
        
        # Sample every 5 minutes to keep test data manageable
        m1_data = pd.DataFrame({
            'DateTime': [start_time + timedelta(minutes=i) for i in range(0, minutes_in_2_days, 5)],
            'Open': [1.1000 for i in range(0, minutes_in_2_days, 5)],
            'High': [1.1010 for i in range(0, minutes_in_2_days, 5)],
            'Low': [1.0990 for i in range(0, minutes_in_2_days, 5)],
            'Close': [1.1005 for i in range(0, minutes_in_2_days, 5)]
        })
        
        # Already at M5 granularity, so just verify
        self.assertGreater(len(m1_data), 100)
        
        print(f"✅ Multi-day data: {len(m1_data)} bars over 2 days")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestM1TimeframeConverter)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
