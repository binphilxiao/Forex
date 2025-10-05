#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Script for Data Consistency Checker
=========================================

This script tests the verify_data_consistency module.

Author: FXCM Data Team
Version: 1.0.0
Date: 2025-10-05
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from verify_data_consistency import DataConsistencyChecker


def test_basic_functionality():
    """Test basic functionality of the consistency checker."""
    print("\n" + "="*80)
    print("  🧪 Test 1: Basic Functionality")
    print("="*80 + "\n")
    
    try:
        # Create checker instance
        checker = DataConsistencyChecker(mode='fast')
        print("✅ Checker instance created successfully")
        
        # Check configuration
        assert checker.config is not None, "Config should not be None"
        assert 'host' in checker.config, "Config should have 'host' key"
        print(f"✅ Configuration loaded: {checker.config['host']}")
        
        # Test query execution (simple test)
        success, result = checker.execute_query("SELECT 1 FORMAT TabSeparated")
        if success:
            print(f"✅ Database connection successful: {result}")
        else:
            print(f"⚠️  Database connection failed: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_fast_mode():
    """Test fast mode verification on a small dataset."""
    print("\n" + "="*80)
    print("  🧪 Test 2: Fast Mode Verification")
    print("="*80 + "\n")
    
    try:
        checker = DataConsistencyChecker(mode='fast')
        
        # Check only EURUSD M1 data for 2015
        results = checker.verify_data(
            symbols=['EURUSD'],
            timeframes=['M1'],
            start_year=2015,
            end_year=2015
        )
        
        print(f"\n✅ Verification completed")
        print(f"   Total results: {len(results)}")
        
        if len(results) > 0:
            # Show sample result
            sample = results[0]
            print(f"\n   Sample result:")
            print(f"   - Symbol: {sample['symbol']}")
            print(f"   - Timeframe: {sample['timeframe']}")
            print(f"   - Year: {sample['year']}")
            print(f"   - Week: {sample['week']}")
            print(f"   - Status: {sample['status']}")
        
        # Check statistics
        print(f"\n   Statistics:")
        print(f"   - Consistent: {checker.stats['consistent']}")
        print(f"   - Inconsistent: {checker.stats['inconsistent']}")
        print(f"   - No data: {checker.stats['no_data']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_comprehensive_mode():
    """Test comprehensive mode verification on a very small dataset."""
    print("\n" + "="*80)
    print("  🧪 Test 3: Comprehensive Mode Verification")
    print("="*80 + "\n")
    
    print("⚠️  Note: This test may take longer as it checks all records")
    
    try:
        checker = DataConsistencyChecker(mode='comprehensive')
        
        # Check only one week of EURUSD M1 data
        # We'll manually verify just one file
        data_root = Path('fxcm_data')
        test_file = data_root / 'EURUSD' / 'M1' / '2015' / 'week_01.csv'
        
        if not test_file.exists():
            print(f"⚠️  Test file not found: {test_file}")
            print("   Skipping comprehensive mode test")
            return True
        
        result = checker.verify_file(test_file, 'EURUSD', 'M1')
        
        print(f"✅ File verified: {test_file.name}")
        print(f"   Status: {result['status']}")
        print(f"   Details: {result['details']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_html_report_generation():
    """Test HTML report generation."""
    print("\n" + "="*80)
    print("  🧪 Test 4: HTML Report Generation")
    print("="*80 + "\n")
    
    try:
        checker = DataConsistencyChecker(mode='fast')
        
        # Verify small dataset
        results = checker.verify_data(
            symbols=['EURUSD'],
            timeframes=['M1'],
            start_year=2015,
            end_year=2015
        )
        
        # Generate HTML report
        report_path = checker.generate_html_report(
            output_path='logs/test_consistency_report.html'
        )
        
        # Check if file was created
        if Path(report_path).exists():
            file_size = Path(report_path).stat().st_size
            print(f"✅ HTML report generated successfully")
            print(f"   Path: {report_path}")
            print(f"   Size: {file_size:,} bytes")
            return True
        else:
            print(f"❌ HTML report file not found: {report_path}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_result_structure():
    """Test the structure of verification results."""
    print("\n" + "="*80)
    print("  🧪 Test 5: Result Structure Validation")
    print("="*80 + "\n")
    
    try:
        checker = DataConsistencyChecker(mode='fast')
        
        # Get one result
        results = checker.verify_data(
            symbols=['EURUSD'],
            timeframes=['D1'],
            start_year=2015,
            end_year=2015
        )
        
        if len(results) == 0:
            print("⚠️  No results to validate")
            return True
        
        # Check first result structure
        result = results[0]
        required_keys = ['symbol', 'timeframe', 'year', 'week', 'file', 'status', 'details']
        
        for key in required_keys:
            if key not in result:
                print(f"❌ Missing required key: {key}")
                return False
            print(f"✅ Key '{key}': {result[key]}")
        
        # Check status value
        valid_statuses = [
            checker.STATUS_NO_DATA,
            checker.STATUS_INCONSISTENT,
            checker.STATUS_CONSISTENT
        ]
        
        if result['status'] not in valid_statuses:
            print(f"❌ Invalid status: {result['status']}")
            return False
        
        print(f"\n✅ Result structure is valid")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*80)
    print("  🚀 FXCM Data Consistency Checker - Test Suite")
    print("="*80)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Fast Mode Verification", test_fast_mode),
        ("Comprehensive Mode Verification", test_comprehensive_mode),
        ("HTML Report Generation", test_html_report_generation),
        ("Result Structure Validation", test_result_structure),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*80)
    print("  📊 Test Summary")
    print("="*80 + "\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✅ PASSED" if passed_flag else "❌ FAILED"
        print(f"  {status:12s} - {test_name}")
    
    print("\n" + "-"*80)
    print(f"  Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*80 + "\n")
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
