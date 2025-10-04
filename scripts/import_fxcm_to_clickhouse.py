#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FXCM数据导入ClickHouse脚本
功能：
1. 批量导入M1和D1数据
2. 自动查重，跳过已存在的相同数据
3. 数据冲突时提供选择：保留旧数据或使用新数据
4. 支持断点续传
5. 详细的导入日志
"""

import os
import sys
import json
import pandas as pd
import requests
from datetime import datetime
from pathlib import Path
import time

# 设置标准输出编码为UTF-8（仅在直接运行时）
if __name__ == '__main__' and sys.platform == 'win32':
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class FXCMDataImporter:
    def __init__(self, config_path='config/clickhouse_config.json'):
        """初始化导入器"""
        self.config = self._load_config(config_path)
        self.base_url = f"http://{self.config['host']}:{self.config['http_port']}"
        self.auth = (self.config['user'], self.config['password'])
        
        # 统计信息
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'total_rows': 0,
            'inserted_rows': 0,
            'skipped_rows': 0,
            'updated_rows': 0,
            'error_rows': 0,
            'conflicts': 0
        }
        
        # 冲突处理策略：'skip'（跳过）, 'overwrite'（覆盖）, 'ask'（询问）
        self.conflict_strategy = 'ask'
        
    def _load_config(self, config_path):
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def execute_query(self, query, data=None):
        """执行ClickHouse查询"""
        try:
            if data:
                response = requests.post(
                    self.base_url,
                    auth=self.auth,
                    params={'query': query},
                    data=data.encode('utf-8') if isinstance(data, str) else data,
                    timeout=300
                )
            else:
                response = requests.post(
                    self.base_url,
                    auth=self.auth,
                    data=query.encode('utf-8'),
                    timeout=300
                )
            
            if response.status_code == 200:
                return True, response.text.strip()
            else:
                return False, response.text
                
        except Exception as e:
            return False, str(e)
    
    def check_file_boundaries(self, symbol, timeframe, first_time, last_time):
        """快速检查：只检查文件的首尾记录是否存在
        
        返回:
            'complete': 首尾都存在，文件可能完整
            'partial': 只有部分存在，需要详细检查
            'missing': 完全不存在，需要导入
        """
        if timeframe == 'M1':
            table = 'ohlcv_m1'
            time_field = 'timestamp'
        else:
            table = 'ohlcv_d1'
            time_field = 'date'
        
        # 检查首尾记录
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
                return 'complete'  # 首尾都存在
            elif count == 1:
                return 'partial'  # 只有部分存在
            else:
                return 'missing'  # 完全不存在
        return 'missing'
    
    def check_existing_data(self, symbol, timeframe, start_time, end_time):
        """检查指定时间范围内是否已有数据（详细模式）"""
        if timeframe == 'M1':
            table = 'ohlcv_m1'
            time_field = 'timestamp'
        else:  # D1
            table = 'ohlcv_d1'
            time_field = 'date'
        
        query = f"""
        SELECT {time_field}, open, high, low, close
        FROM forex_data.{table}
        WHERE symbol = '{symbol}'
          AND {time_field} >= '{start_time}'
          AND {time_field} <= '{end_time}'
        ORDER BY {time_field}
        FORMAT TabSeparated
        """
        
        success, result = self.execute_query(query)
        if success and result:
            # 解析结果为字典 {timestamp: (open, high, low, close)}
            existing_data = {}
            for line in result.split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    timestamp = parts[0]
                    ohlc = tuple(float(x) for x in parts[1:5])
                    existing_data[timestamp] = ohlc
            return existing_data
        return {}
    
    def compare_rows(self, new_row, old_ohlc):
        """比较新旧数据是否一致"""
        new_ohlc = (
            float(new_row['open']),
            float(new_row['high']),
            float(new_row['low']),
            float(new_row['close'])
        )
        
        # 使用小数点后5位精度比较（考虑浮点数误差）
        tolerance = 1e-5
        for i in range(4):
            if abs(new_ohlc[i] - old_ohlc[i]) > tolerance:
                return False
        return True
    
    def handle_conflict(self, symbol, timestamp, new_row, old_ohlc):
        """处理数据冲突"""
        self.stats['conflicts'] += 1
        
        if self.conflict_strategy == 'skip':
            return 'skip'
        elif self.conflict_strategy == 'overwrite':
            return 'overwrite'
        else:  # ask
            print(f"\n⚠️  数据冲突：{symbol} @ {timestamp}")
            print(f"   旧数据 OHLC: {old_ohlc}")
            print(f"   新数据 OHLC: ({new_row['open']}, {new_row['high']}, {new_row['low']}, {new_row['close']})")
            
            while True:
                choice = input("   选择操作 [s]跳过 / [o]覆盖 / [a]全部跳过 / [A]全部覆盖: ").lower()
                if choice == 's':
                    return 'skip'
                elif choice == 'o':
                    return 'overwrite'
                elif choice == 'a':
                    self.conflict_strategy = 'skip'
                    return 'skip'
                elif choice == 'A':
                    self.conflict_strategy = 'overwrite'
                    return 'overwrite'
                else:
                    print("   无效选择，请重新输入")
    
    def delete_existing_data(self, symbol, timeframe, timestamps):
        """删除已存在的数据（用于覆盖）"""
        if not timestamps:
            return True
        
        if timeframe == 'M1':
            table = 'ohlcv_m1'
            time_field = 'timestamp'
        else:
            table = 'ohlcv_d1'
            time_field = 'date'
        
        # 构建删除条件
        timestamp_list = "', '".join(timestamps)
        query = f"""
        ALTER TABLE forex_data.{table}
        DELETE WHERE symbol = '{symbol}'
          AND {time_field} IN ('{timestamp_list}')
        """
        
        success, result = self.execute_query(query)
        return success
    
    def import_csv_file(self, csv_path, symbol, timeframe, check_mode='fast'):
        """导入单个CSV文件
        
        参数:
            csv_path: CSV文件路径
            symbol: 货币对符号
            timeframe: 时间周期 (M1/D1)
            check_mode: 检查模式
                - 'fast': 快速模式，只检查首尾记录（默认）
                - 'comprehensive': 详细模式，检查所有记录
        """
        try:
            # 读取CSV文件
            df = pd.read_csv(csv_path)
            
            if df.empty:
                print(f"   ⚠️  文件为空，跳过")
                return
            
            # 添加symbol列
            df['symbol'] = symbol
            
            # 重命名列
            column_mapping = {
                'DateTime': 'timestamp' if timeframe == 'M1' else 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close'
            }
            df.rename(columns=column_mapping, inplace=True)
            
            # 对于D1数据，需要将DateTime转换为Date类型（只保留日期部分）
            if timeframe == 'D1':
                df['date'] = pd.to_datetime(df['date']).dt.date
            
            # 根据检查模式选择不同的检查策略
            time_field = 'timestamp' if timeframe == 'M1' else 'date'
            start_time = df[time_field].min()
            end_time = df[time_field].max()
            
            if check_mode == 'fast':
                # 快速模式：只检查首尾记录
                first_time = df[time_field].iloc[0]
                last_time = df[time_field].iloc[-1]
                boundary_status = self.check_file_boundaries(symbol, timeframe, first_time, last_time)
                
                if boundary_status == 'complete':
                    # 首尾都存在，假设文件完整，直接跳过
                    self.stats['skipped_rows'] += len(df)
                    print(f"   ⏭️  跳过 {len(df)} 条已存在的数据 (快速检测)")
                    return
                elif boundary_status == 'missing':
                    # 完全不存在，直接批量插入
                    self._batch_insert(df, timeframe)
                    self.stats['inserted_rows'] += len(df)
                    print(f"   ✅ 插入 {len(df)} 条新数据")
                    return
                else:
                    # 部分存在，切换到详细模式
                    print(f"   🔍 检测到部分数据，切换到详细检查模式...")
                    check_mode = 'comprehensive'
            
            # 详细模式：检查所有记录
            existing_data = self.check_existing_data(symbol, timeframe, start_time, end_time)
            
            if not existing_data:
                # 没有重复数据，直接批量插入
                self._batch_insert(df, timeframe)
                self.stats['inserted_rows'] += len(df)
                print(f"   ✅ 插入 {len(df)} 条新数据")
            else:
                # 有重复数据，需要逐行检查
                new_rows = []
                overwrite_timestamps = []
                
                for _, row in df.iterrows():
                    timestamp_str = str(row[time_field])
                    
                    if timestamp_str in existing_data:
                        # 数据已存在，检查是否一致
                        old_ohlc = existing_data[timestamp_str]
                        
                        if self.compare_rows(row, old_ohlc):
                            # 数据一致，跳过
                            self.stats['skipped_rows'] += 1
                        else:
                            # 数据冲突，询问处理方式
                            action = self.handle_conflict(symbol, timestamp_str, row, old_ohlc)
                            
                            if action == 'overwrite':
                                overwrite_timestamps.append(timestamp_str)
                                new_rows.append(row)
                                self.stats['updated_rows'] += 1
                            else:  # skip
                                self.stats['skipped_rows'] += 1
                    else:
                        # 新数据
                        new_rows.append(row)
                        self.stats['inserted_rows'] += 1
                
                # 删除需要覆盖的旧数据
                if overwrite_timestamps:
                    print(f"   🔄 覆盖 {len(overwrite_timestamps)} 条旧数据")
                    self.delete_existing_data(symbol, timeframe, overwrite_timestamps)
                
                # 批量插入新数据和更新数据
                if new_rows:
                    new_df = pd.DataFrame(new_rows)
                    self._batch_insert(new_df, timeframe)
                    print(f"   ✅ 插入/更新 {len(new_rows)} 条数据，跳过 {len(df) - len(new_rows)} 条")
                else:
                    print(f"   ⏭️  跳过 {len(df)} 条已存在的数据")
            
            self.stats['total_rows'] += len(df)
            
        except Exception as e:
            print(f"   ❌ 错误: {str(e)}")
            self.stats['error_rows'] += len(df) if 'df' in locals() else 0
    
    def _batch_insert(self, df, timeframe):
        """批量插入数据"""
        if timeframe == 'M1':
            table = 'ohlcv_m1'
            time_field = 'timestamp'
        else:
            table = 'ohlcv_d1'
            time_field = 'date'
        
        # 选择需要的列
        columns = ['symbol', time_field, 'open', 'high', 'low', 'close']
        df_insert = df[columns].copy()
        
        # 转换为CSV格式（不含表头）
        csv_data = df_insert.to_csv(index=False, header=False)
        
        # 插入数据
        query = f"INSERT INTO forex_data.{table} ({', '.join(columns)}) FORMAT CSV"
        success, result = self.execute_query(query, csv_data)
        
        if not success:
            raise Exception(f"插入失败: {result}")
    
    def scan_fxcm_data_folder(self, base_path='fxcm_data'):
        """扫描fxcm_data文件夹，获取所有CSV文件"""
        files_to_import = {
            'M1': [],
            'D1': []
        }
        
        base_path = Path(base_path)
        
        # 遍历所有货币对文件夹
        for symbol_folder in base_path.iterdir():
            if not symbol_folder.is_dir():
                continue
            
            symbol = symbol_folder.name
            
            # M1数据（按周组织）
            m1_folder = symbol_folder / 'M1'
            if m1_folder.exists():
                for year_folder in sorted(m1_folder.iterdir()):
                    if not year_folder.is_dir():
                        continue
                    for week_file in sorted(year_folder.glob('week_*.csv')):
                        files_to_import['M1'].append({
                            'path': week_file,
                            'symbol': symbol,
                            'year': year_folder.name
                        })
            
            # D1数据（按年组织）
            d1_folder = symbol_folder / 'D1'
            if d1_folder.exists():
                for year_file in sorted(d1_folder.glob('*.csv')):
                    files_to_import['D1'].append({
                        'path': year_file,
                        'symbol': symbol,
                        'year': year_file.stem
                    })
        
        return files_to_import
    
    def import_all_data(self, base_path='fxcm_data', timeframes=['M1', 'D1']):
        """导入所有数据"""
        print("\n" + "="*80)
        print("          FXCM数据导入ClickHouse")
        print("="*80 + "\n")
        
        # 扫描文件
        print("📁 扫描数据文件...")
        files_to_import = self.scan_fxcm_data_folder(base_path)
        
        for tf in timeframes:
            if tf in files_to_import:
                count = len(files_to_import[tf])
                print(f"   {tf}: 找到 {count} 个文件")
                self.stats['total_files'] += count
        
        if self.stats['total_files'] == 0:
            print("❌ 没有找到任何CSV文件")
            return
        
        print(f"\n📊 总计: {self.stats['total_files']} 个文件待导入\n")
        
        # 确认导入
        confirm = input("是否开始导入？[y/N]: ").lower()
        if confirm != 'y':
            print("❌ 已取消导入")
            return
        
        print("\n" + "-"*80)
        print("开始导入数据...")
        print("-"*80 + "\n")
        
        start_time = time.time()
        
        # 导入数据
        for timeframe in timeframes:
            if timeframe not in files_to_import:
                continue
            
            print(f"\n📊 导入 {timeframe} 数据...")
            print("-"*60)
            
            for file_info in files_to_import[timeframe]:
                csv_path = file_info['path']
                symbol = file_info['symbol']
                
                print(f"\n   处理: {symbol} - {csv_path.name}")
                
                self.import_csv_file(csv_path, symbol, timeframe)
                self.stats['processed_files'] += 1
                
                # 显示进度
                progress = (self.stats['processed_files'] / self.stats['total_files']) * 100
                print(f"   进度: {self.stats['processed_files']}/{self.stats['total_files']} ({progress:.1f}%)")
        
        # 显示统计信息
        elapsed_time = time.time() - start_time
        
        print("\n" + "="*80)
        print("✅ 导入完成！")
        print("="*80 + "\n")
        
        print("📊 导入统计:")
        print(f"   文件总数: {self.stats['total_files']}")
        print(f"   已处理: {self.stats['processed_files']}")
        print(f"   数据总行数: {self.stats['total_rows']}")
        print(f"   新插入: {self.stats['inserted_rows']}")
        print(f"   已跳过（重复）: {self.stats['skipped_rows']}")
        print(f"   已更新（覆盖）: {self.stats['updated_rows']}")
        print(f"   冲突次数: {self.stats['conflicts']}")
        print(f"   错误: {self.stats['error_rows']}")
        print(f"   耗时: {elapsed_time:.2f} 秒")
        print()
    
    def import_specific_symbol(self, symbol, timeframe, base_path='fxcm_data'):
        """导入指定货币对的数据"""
        print(f"\n📊 导入 {symbol} 的 {timeframe} 数据...")
        
        base_path = Path(base_path)
        symbol_folder = base_path / symbol
        
        if not symbol_folder.exists():
            print(f"❌ 找不到货币对文件夹: {symbol}")
            return
        
        if timeframe == 'M1':
            m1_folder = symbol_folder / 'M1'
            if not m1_folder.exists():
                print(f"❌ 找不到M1数据文件夹")
                return
            
            for year_folder in sorted(m1_folder.iterdir()):
                if not year_folder.is_dir():
                    continue
                print(f"\n   处理年份: {year_folder.name}")
                for week_file in sorted(year_folder.glob('week_*.csv')):
                    print(f"      {week_file.name}")
                    self.import_csv_file(week_file, symbol, 'M1')
        
        elif timeframe == 'D1':
            d1_folder = symbol_folder / 'D1'
            if not d1_folder.exists():
                print(f"❌ 找不到D1数据文件夹")
                return
            
            for year_file in sorted(d1_folder.glob('*.csv')):
                print(f"   {year_file.name}")
                self.import_csv_file(year_file, symbol, 'D1')

def main():
    """主函数"""
    importer = FXCMDataImporter()
    
    print("\n" + "="*80)
    print("          FXCM数据导入工具")
    print("="*80 + "\n")
    print("选择导入模式:")
    print("  1. 导入所有数据（M1 + D1）")
    print("  2. 仅导入M1数据")
    print("  3. 仅导入D1数据")
    print("  4. 导入指定货币对")
    print()
    
    choice = input("请选择 [1-4]: ").strip()
    
    if choice == '1':
        importer.import_all_data(timeframes=['M1', 'D1'])
    elif choice == '2':
        importer.import_all_data(timeframes=['M1'])
    elif choice == '3':
        importer.import_all_data(timeframes=['D1'])
    elif choice == '4':
        symbol = input("输入货币对（如EURUSD）: ").strip().upper()
        timeframe = input("输入时间框架（M1或D1）: ").strip().upper()
        if timeframe in ['M1', 'D1']:
            importer.import_specific_symbol(symbol, timeframe)
        else:
            print("❌ 无效的时间框架")
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
