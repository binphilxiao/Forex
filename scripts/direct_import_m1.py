# -*- coding: utf-8 -*-
"""
Direct M1 Data Import - No User Confirmation Required
"""
import sys
from pathlib import Path
sys.path.insert(0, 'scripts')
from import_fxcm_to_clickhouse import FXCMDataImporter
import time

print("\n" + "="*80)
print("          M1 Data Import to ClickHouse (Auto Mode)")
print("="*80 + "\n")

# Initialize importer
importer = FXCMDataImporter()
importer.conflict_strategy = 'skip'  # Auto skip duplicates, no asking

# Scan files
print("Scanning fxcm_data folder...")
files_to_import = importer.scan_fxcm_data_folder('fxcm_data')

m1_files = files_to_import.get('M1', [])
print(f"Found {len(m1_files)} M1 files to import\n")

if not m1_files:
    print("No M1 files found!")
    sys.exit(1)

print("="*80)
print("Starting import (Auto mode - skips duplicates automatically)")
print("="*80 + "\n")

start_time = time.time()

# Import M1 data
for i, file_info in enumerate(m1_files, 1):
    csv_path = file_info['path']
    symbol = file_info['symbol']
    year = file_info['year']
    
    print(f"[{i}/{len(m1_files)}] Processing: {symbol}/{year}/{csv_path.name}")
    
    try:
        importer.import_csv_file(csv_path, symbol, 'M1')
        importer.stats['processed_files'] += 1
        
        # Show progress every 10 files
        if i % 10 == 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining = (len(m1_files) - i) * avg_time
            print(f"  Progress: {i}/{len(m1_files)} ({i/len(m1_files)*100:.1f}%)")
            print(f"  Elapsed: {elapsed/60:.1f}min, Estimated remaining: {remaining/60:.1f}min\n")
    
    except Exception as e:
        print(f"  ERROR: {str(e)}\n")
        continue

# Print final statistics
elapsed_time = time.time() - start_time

print("\n" + "="*80)
print("Import Completed!")
print("="*80 + "\n")

print("Statistics:")
print(f"  Total files: {len(m1_files)}")
print(f"  Processed: {importer.stats['processed_files']}")
print(f"  Total rows: {importer.stats['total_rows']:,}")
print(f"  Inserted: {importer.stats['inserted_rows']:,}")
print(f"  Skipped (duplicates): {importer.stats['skipped_rows']:,}")
print(f"  Updated: {importer.stats['updated_rows']:,}")
print(f"  Errors: {importer.stats['error_rows']:,}")
print(f"  Time: {elapsed_time/60:.2f} minutes")
print()
