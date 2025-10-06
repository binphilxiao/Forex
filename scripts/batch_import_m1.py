# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, 'scripts')
from fxcm_importer import FXCMDataImporter

print("\n" + "="*80)
print("          Batch Import M1 Data to ClickHouse")
print("="*80 + "\n")

importer = FXCMDataImporter()
importer.conflict_strategy = 'skip'  # Auto skip duplicates

print("Starting M1 data import...")
print("Strategy: Auto skip duplicates")
print("-"*80 + "\n")

importer.import_all_data(timeframes=['M1'])
