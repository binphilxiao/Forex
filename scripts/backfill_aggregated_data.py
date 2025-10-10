#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ClickHouse M1 数据聚合回填工具
==============================

从 M1 数据聚合生成 M5、M15、M30、H1 时间周期数据

功能特点:
- 支持选择性回填（指定货币对、时间周期、时间段）
- 增量回填模式（只处理缺失的数据）
- 全量回填模式（重新聚合所有数据）
- 彩色进度显示
- 详细的统计报告

聚合规则:
- Open: 时间窗口内第一个值
- High: 时间窗口内最大值
- Low: 时间窗口内最小值
- Close: 时间窗口内最后一个值
- Volume: 时间窗口内总和

作者: AI Assistant
创建时间: 2025-10-10
版本: 1.0.0
"""

import sys
import io
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Optional, Tuple

# Import progress grid module
from progress_grid import ProgressGrid, ProgressStatus

# Conditional import of ClickHouse
try:
    import clickhouse_connect
    from clickhouse_connect.driver.client import Client
    CLICKHOUSE_AVAILABLE = True
except ImportError:
    CLICKHOUSE_AVAILABLE = False
    clickhouse_connect = None
    Client = None

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class ClickHouseAggregator:
    """ClickHouse 数据聚合回填器"""
    
    # 支持的时间周期配置
    TIMEFRAMES = {
        'M5': {'interval': '5 MINUTE', 'minutes': 5, 'description': '5分钟'},
        'M15': {'interval': '15 MINUTE', 'minutes': 15, 'description': '15分钟'},
        'M30': {'interval': '30 MINUTE', 'minutes': 30, 'description': '30分钟'},
        'H1': {'interval': '1 HOUR', 'minutes': 60, 'description': '1小时'}
    }
    
    # 支持的货币对
    SYMBOLS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF']
    
    def __init__(self, config_path: str = 'config/clickhouse_config.json'):
        """初始化聚合器"""
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.client: Optional[Client] = None
        
        # 设置日志
        self.setup_logging()
        
        # 进度网格
        self.progress_grid = ProgressGrid("M1 数据聚合回填进度")
        
        # 统计信息
        self.stats = {
            'total_processed': 0,
            'total_inserted': 0,
            'total_skipped': 0,
            'total_errors': 0,
            'by_symbol': {},
            'by_timeframe': {}
        }
    
    def load_config(self) -> Dict:
        """加载 ClickHouse 配置"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def setup_logging(self):
        """设置日志系统"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'aggregation_{timestamp}.log'
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"数据聚合开始 - 日志文件: {log_file}")
        print(f"📝 日志文件: {log_file}\n")
    
    def connect(self):
        """连接到 ClickHouse"""
        if not CLICKHOUSE_AVAILABLE:
            raise ImportError("clickhouse-connect 未安装。请运行: pip install clickhouse-connect")
        
        try:
            print(f"🔌 连接到 ClickHouse: {self.config['host']}:{self.config['http_port']}...")
            
            self.client = clickhouse_connect.get_client(
                host=self.config['host'],
                port=self.config['http_port'],
                username=self.config['user'],
                password=self.config['password'],
                database=self.config.get('database', 'default')
            )
            
            # 测试连接
            result = self.client.command('SELECT version()')
            print(f"✅ 连接成功! ClickHouse 版本: {result}\n")
            self.logger.info(f"连接到 ClickHouse 成功，版本: {result}")
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            self.logger.error(f"连接到 ClickHouse 失败: {e}")
            raise
    
    def get_available_date_range(self, symbol: str) -> Optional[Tuple[str, str]]:
        """获取指定货币对的可用日期范围"""
        try:
            query = f"""
            SELECT 
                formatDateTime(min(timestamp), '%Y-%m-%d %H:%i:%S') as min_date,
                formatDateTime(max(timestamp), '%Y-%m-%d %H:%i:%S') as max_date
            FROM forex_data.ohlcv_m1
            WHERE symbol = '{symbol}'
            """
            result = self.client.query(query)
            
            if result.row_count > 0:
                row = result.result_rows[0]
                if row[0] and row[1]:
                    return (row[0], row[1])
            
            return None
            
        except Exception as e:
            self.logger.error(f"获取 {symbol} 可用日期范围失败: {e}")
            return None
    
    def get_missing_periods(self, symbol: str, timeframe: str, 
                           start_date: str, end_date: str) -> List[Tuple[str, str]]:
        """获取缺失的时间段（用于增量回填）"""
        try:
            table = f'forex_data.ohlcv_{timeframe.lower()}'
            interval = self.TIMEFRAMES[timeframe]['interval']
            
            # 首先检查目标表是否为空
            count_query = f"SELECT count() FROM {table} WHERE symbol = '{symbol}'"
            existing_count = self.client.command(count_query)
            
            if existing_count == 0:
                # 目标表为空，返回整个时间段需要回填
                self.logger.info(f"{symbol} {timeframe} 表为空，需要全量回填")
                return [(start_date, end_date)]
            
            # 查询源数据的时间范围
            query = f"""
            WITH source AS (
                SELECT DISTINCT toStartOfInterval(timestamp, INTERVAL {interval}) as ts
                FROM forex_data.ohlcv_m1
                WHERE symbol = '{symbol}'
                  AND timestamp >= '{start_date}'
                  AND timestamp <= '{end_date}'
            ),
            target AS (
                SELECT DISTINCT timestamp as ts
                FROM {table}
                WHERE symbol = '{symbol}'
                  AND timestamp >= '{start_date}'
                  AND timestamp <= '{end_date}'
            )
            SELECT source.ts
            FROM source
            LEFT JOIN target ON source.ts = target.ts
            WHERE target.ts IS NULL
            ORDER BY source.ts
            LIMIT 10000
            """
            
            result = self.client.query(query)
            
            if result.row_count > 0:
                # 将缺失的时间点合并为连续的时间段
                missing_timestamps = [str(row[0]) for row in result.result_rows]
                
                if missing_timestamps:
                    # 简化：返回整个时间段
                    return [(missing_timestamps[0], missing_timestamps[-1])]
            
            return []
            
        except Exception as e:
            self.logger.error(f"获取 {symbol} {timeframe} 缺失时间段失败: {e}")
            return []
    
    def aggregate_and_insert(self, symbol: str, timeframe: str, 
                            start_date: str, end_date: str,
                            replace_existing: bool = False) -> int:
        """聚合并插入数据（自动分批处理以避免分区过多）"""
        try:
            table = f'forex_data.ohlcv_{timeframe.lower()}'
            interval = self.TIMEFRAMES[timeframe]['interval']
            
            # 解析日期
            start_dt = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
            
            # 分批处理，每次处理 3 个月
            batch_months = 3
            current_start = start_dt
            total_rows = 0
            
            while current_start < end_dt:
                # 计算当前批次的结束日期
                batch_end = current_start + relativedelta(months=batch_months)
                if batch_end > end_dt:
                    batch_end = end_dt
                
                batch_start_str = current_start.strftime('%Y-%m-%d %H:%M:%S')
                batch_end_str = batch_end.strftime('%Y-%m-%d %H:%M:%S')
                
                # 如果是替换模式，先删除现有数据
                if replace_existing:
                    delete_query = f"""
                    ALTER TABLE {table} 
                    DELETE WHERE symbol = '{symbol}'
                      AND timestamp >= '{batch_start_str}'
                      AND timestamp <= '{batch_end_str}'
                    """
                    self.client.command(delete_query)
                    self.logger.debug(f"删除 {symbol} {timeframe} 现有数据: {batch_start_str} 到 {batch_end_str}")
                
                # 聚合并插入数据
                insert_query = f"""
                INSERT INTO {table}
                SELECT
                    symbol,
                    toStartOfInterval(timestamp, INTERVAL {interval}) as timestamp,
                    anyLast(open) as open,
                    max(high) as high,
                    min(low) as low,
                    anyLast(close) as close,
                    sum(volume) as volume
                FROM forex_data.ohlcv_m1
                WHERE symbol = '{symbol}'
                  AND timestamp >= '{batch_start_str}'
                  AND timestamp <= '{batch_end_str}'
                GROUP BY symbol, timestamp
                ORDER BY timestamp
                """
                
                self.client.command(insert_query)
                
                # 查询本批次插入的行数
                count_query = f"""
                SELECT count(*)
                FROM {table}
                WHERE symbol = '{symbol}'
                  AND timestamp >= toStartOfInterval(toDateTime('{batch_start_str}'), INTERVAL {interval})
                  AND timestamp <= toStartOfInterval(toDateTime('{batch_end_str}'), INTERVAL {interval})
                """
                count_result = self.client.query(count_query)
                batch_rows = count_result.result_rows[0][0]
                total_rows += batch_rows
                
                self.logger.debug(f"聚合 {symbol} {timeframe} 批次: {batch_start_str} 到 {batch_end_str}, 插入 {batch_rows} 行")
                
                # 移动到下一个批次
                current_start = batch_end
            
            self.logger.debug(f"聚合 {symbol} {timeframe} 完成: {start_date} 到 {end_date}, 总计 {total_rows} 行")
            
            return total_rows
            
        except Exception as e:
            self.logger.error(f"聚合 {symbol} {timeframe} 数据失败: {e}")
            raise
    
    def process_symbol_timeframe(self, symbol: str, timeframe: str,
                                 start_date: Optional[str] = None,
                                 end_date: Optional[str] = None,
                                 incremental: bool = True) -> Dict:
        """处理单个货币对的单个时间周期"""
        result = {
            'symbol': symbol,
            'timeframe': timeframe,
            'rows_inserted': 0,
            'status': 'success'
        }
        
        try:
            # 获取可用日期范围
            date_range = self.get_available_date_range(symbol)
            
            if not date_range:
                result['status'] = 'no_data'
                return result
            
            # 确定实际的开始和结束日期
            actual_start = start_date if start_date else date_range[0]
            actual_end = end_date if end_date else date_range[1]
            
            self.logger.info(f"处理 {symbol} {timeframe}: {actual_start} 到 {actual_end}")
            
            if incremental:
                # 增量模式：只处理缺失的时间段
                missing_periods = self.get_missing_periods(symbol, timeframe, actual_start, actual_end)
                
                if not missing_periods:
                    result['status'] = 'up_to_date'
                    self.logger.info(f"{symbol} {timeframe} 数据已是最新")
                    return result
                
                # 处理每个缺失的时间段
                total_rows = 0
                for period_start, period_end in missing_periods:
                    rows = self.aggregate_and_insert(symbol, timeframe, period_start, period_end, False)
                    total_rows += rows
                
                result['rows_inserted'] = total_rows
                
            else:
                # 全量模式：删除并重新聚合所有数据
                rows = self.aggregate_and_insert(symbol, timeframe, actual_start, actual_end, True)
                result['rows_inserted'] = rows
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            self.logger.error(f"处理 {symbol} {timeframe} 失败: {e}")
        
        return result
    
    def backfill(self, symbols: Optional[List[str]] = None,
                timeframes: Optional[List[str]] = None,
                start_date: Optional[str] = None,
                end_date: Optional[str] = None,
                incremental: bool = True):
        """执行回填"""
        print("=" * 80)
        print("🔄 ClickHouse M1 数据聚合回填")
        print("=" * 80)
        print()
        
        # 默认值
        if symbols is None:
            symbols = self.SYMBOLS
        if timeframes is None:
            timeframes = list(self.TIMEFRAMES.keys())
        
        mode = "增量回填" if incremental else "全量回填"
        print(f"📊 回填模式: {mode}")
        print(f"💱 货币对: {', '.join(symbols)}")
        print(f"⏱️  时间周期: {', '.join(timeframes)}")
        if start_date:
            print(f"📅 开始日期: {start_date}")
        if end_date:
            print(f"📅 结束日期: {end_date}")
        print()
        
        # 连接到 ClickHouse
        self.connect()
        
        # 处理每个货币对和时间周期
        for symbol in symbols:
            print(f"\n💱 {symbol}")
            print("=" * 80)
            
            for timeframe in timeframes:
                desc = self.TIMEFRAMES[timeframe]['description']
                print(f"\n⏱️  {timeframe} ({desc})")
                
                try:
                    result = self.process_symbol_timeframe(
                        symbol, timeframe, start_date, end_date, incremental
                    )
                    
                    if result['status'] == 'success':
                        print(f"  ✅ 成功插入 {result['rows_inserted']:,} 行")
                        self.stats['total_inserted'] += result['rows_inserted']
                        self.stats['total_processed'] += 1
                        
                    elif result['status'] == 'up_to_date':
                        print(f"  ✅ 数据已是最新，无需回填")
                        self.stats['total_skipped'] += 1
                        
                    elif result['status'] == 'no_data':
                        print(f"  ⚠️  源数据不存在")
                        self.stats['total_skipped'] += 1
                        
                    elif result['status'] == 'error':
                        print(f"  ❌ 失败: {result.get('error', 'Unknown error')}")
                        self.stats['total_errors'] += 1
                    
                    # 更新统计
                    if symbol not in self.stats['by_symbol']:
                        self.stats['by_symbol'][symbol] = {'inserted': 0, 'errors': 0}
                    if timeframe not in self.stats['by_timeframe']:
                        self.stats['by_timeframe'][timeframe] = {'inserted': 0, 'errors': 0}
                    
                    if result['status'] == 'success':
                        self.stats['by_symbol'][symbol]['inserted'] += result['rows_inserted']
                        self.stats['by_timeframe'][timeframe]['inserted'] += result['rows_inserted']
                    elif result['status'] == 'error':
                        self.stats['by_symbol'][symbol]['errors'] += 1
                        self.stats['by_timeframe'][timeframe]['errors'] += 1
                    
                except Exception as e:
                    print(f"  ❌ 异常: {e}")
                    self.stats['total_errors'] += 1
        
        # 显示汇总
        self.print_summary()
    
    def print_summary(self):
        """打印统计汇总"""
        print("\n" + "=" * 80)
        print("📊 回填汇总")
        print("=" * 80)
        
        print(f"\n总体统计:")
        print(f"  处理成功: {self.stats['total_processed']}")
        print(f"  跳过: {self.stats['total_skipped']}")
        print(f"  错误: {self.stats['total_errors']}")
        print(f"  总插入行数: {self.stats['total_inserted']:,}")
        
        if self.stats['by_symbol']:
            print(f"\n按货币对统计:")
            for symbol, data in sorted(self.stats['by_symbol'].items()):
                print(f"  {symbol}: {data['inserted']:,} 行")
        
        if self.stats['by_timeframe']:
            print(f"\n按时间周期统计:")
            for tf, data in sorted(self.stats['by_timeframe'].items()):
                print(f"  {tf}: {data['inserted']:,} 行")
        
        print("\n" + "=" * 80)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='ClickHouse M1 数据聚合回填工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 增量回填所有货币对的所有时间周期
  python backfill_aggregated_data.py
  
  # 全量回填 EURUSD 的 M5 和 M15
  python backfill_aggregated_data.py --symbols EURUSD --timeframes M5 M15 --full
  
  # 回填指定时间段
  python backfill_aggregated_data.py --start-date "2024-01-01" --end-date "2024-12-31"
  
  # 只回填 M5 数据
  python backfill_aggregated_data.py --timeframes M5
        """
    )
    
    parser.add_argument(
        '--symbols',
        nargs='+',
        choices=ClickHouseAggregator.SYMBOLS,
        help='要处理的货币对（默认：所有）'
    )
    
    parser.add_argument(
        '--timeframes',
        nargs='+',
        choices=list(ClickHouseAggregator.TIMEFRAMES.keys()),
        help='要处理的时间周期（默认：所有）'
    )
    
    parser.add_argument(
        '--start-date',
        help='开始日期 (格式: YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS)'
    )
    
    parser.add_argument(
        '--end-date',
        help='结束日期 (格式: YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS)'
    )
    
    parser.add_argument(
        '--full',
        action='store_true',
        help='全量回填模式（删除现有数据并重新聚合）'
    )
    
    parser.add_argument(
        '--config',
        default='config/clickhouse_config.json',
        help='ClickHouse 配置文件路径'
    )
    
    args = parser.parse_args()
    
    try:
        aggregator = ClickHouseAggregator(config_path=args.config)
        aggregator.backfill(
            symbols=args.symbols,
            timeframes=args.timeframes,
            start_date=args.start_date,
            end_date=args.end_date,
            incremental=not args.full
        )
        
    except KeyboardInterrupt:
        print("\n\n⚠️  操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
