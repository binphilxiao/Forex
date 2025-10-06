#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ClickHouse 物化视图设置脚本
==========================

这个脚本用于在 ClickHouse 中设置物化视图（Materialized Views），
实现从 M1 数据自动实时聚合生成 M5、M15、M30、H1 数据。

功能特点:
- 一次性设置，永久生效
- 自动实时聚合：新的 M1 数据插入后自动生成其他时间周期数据
- 使用 ClickHouse 原生聚合功能，性能极高
- 支持历史数据回填
- 彩色进度显示

工作原理:
1. 创建目标时间周期表（M5、M15、M30、H1）
2. 创建物化视图，监听 M1 表的插入操作
3. 新数据插入 M1 表时，物化视图自动触发聚合并插入到目标表
4. 可选：回填历史数据

作者: AI Assistant
创建时间: 2025-10-06
版本: 1.0.0
"""

import sys
import io
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

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


class ClickHouseMaterializedViewSetup:
    """ClickHouse 物化视图设置管理器"""
    
    # 时间周期配置
    TIMEFRAMES = {
        'M5': {'interval': '5 MINUTE', 'description': '5分钟'},
        'M15': {'interval': '15 MINUTE', 'description': '15分钟'},
        'M30': {'interval': '30 MINUTE', 'description': '30分钟'},
        'H1': {'interval': '1 HOUR', 'description': '1小时'}
    }
    
    # 货币对列表
    INSTRUMENTS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF']
    
    def __init__(self):
        """初始化设置管理器"""
        # 加载配置
        self.config = self.load_config()
        
        # 设置日志
        self.setup_logging()
        
        # ClickHouse 客户端
        self.client: Optional[Client] = None
        
        # 进度网格
        self.progress_grid = ProgressGrid("ClickHouse 物化视图设置进度")
        
        # 统计信息
        self.stats = {
            'tables_created': 0,
            'views_created': 0,
            'backfill_rows': 0,
            'errors': 0
        }
    
    def load_config(self) -> Dict:
        """加载 ClickHouse 配置"""
        config_path = Path(__file__).parent.parent / 'config' / 'clickhouse_config.json'
        
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def setup_logging(self):
        """设置日志系统"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'clickhouse_mv_setup_{timestamp}.log'
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"ClickHouse 物化视图设置开始 - 日志文件: {log_file}")
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
                database=self.config['database']
            )
            
            # 测试连接
            result = self.client.command('SELECT version()')
            print(f"✅ 连接成功! ClickHouse 版本: {result}\n")
            self.logger.info(f"连接到 ClickHouse 成功，版本: {result}")
            
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            self.logger.error(f"连接到 ClickHouse 失败: {e}")
            raise
    
    def create_timeframe_table(self, timeframe: str) -> bool:
        """创建时间周期表"""
        try:
            table_name = f'forex_data.ohlcv_{timeframe.lower()}'
            
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name}
            (
                symbol String,
                timestamp DateTime,
                open Float64,
                high Float64,
                low Float64,
                close Float64,
                volume UInt64
            )
            ENGINE = MergeTree()
            PARTITION BY toYYYYMM(timestamp)
            ORDER BY (symbol, timestamp)
            SETTINGS index_granularity = 8192
            """
            
            self.client.command(create_table_sql)
            self.logger.info(f"创建表 {table_name} 成功")
            return True
            
        except Exception as e:
            self.logger.error(f"创建表 {table_name} 失败: {e}")
            return False
    
    def create_materialized_view(self, timeframe: str) -> bool:
        """创建物化视图"""
        try:
            table_name = f'forex_data.ohlcv_{timeframe.lower()}'
            mv_name = f'forex_data.ohlcv_{timeframe.lower()}_mv'
            interval = self.TIMEFRAMES[timeframe]['interval']
            
            # 先删除已存在的物化视图
            drop_mv_sql = f"DROP VIEW IF EXISTS {mv_name}"
            self.client.command(drop_mv_sql)
            
            # 创建物化视图
            # 注意：在聚合查询中，argMin/argMax 第二个参数也必须是被聚合的列
            create_mv_sql = f"""
            CREATE MATERIALIZED VIEW {mv_name}
            TO {table_name}
            AS SELECT
                symbol,
                toStartOfInterval(timestamp, INTERVAL {interval}) as timestamp,
                anyLast(open) as open,
                max(high) as high,
                min(low) as low,
                anyLast(close) as close,
                sum(volume) as volume
            FROM forex_data.ohlcv_m1
            GROUP BY symbol, timestamp
            ORDER BY symbol, timestamp
            """
            
            self.client.command(create_mv_sql)
            self.logger.info(f"创建物化视图 {mv_name} 成功")
            return True
            
        except Exception as e:
            self.logger.error(f"创建物化视图 {mv_name} 失败: {e}")
            return False
    
    def backfill_historical_data(self, timeframe: str, instrument: str, year: int) -> int:
        """回填历史数据"""
        try:
            table_name = f'forex_data.ohlcv_{timeframe.lower()}'
            interval = self.TIMEFRAMES[timeframe]['interval']
            
            insert_sql = f"""
            INSERT INTO {table_name}
            SELECT
                symbol,
                toStartOfInterval(timestamp, INTERVAL {interval}) as timestamp,
                anyLast(open) as open,
                max(high) as high,
                min(low) as low,
                anyLast(close) as close,
                sum(volume) as volume
            FROM forex_data.ohlcv_m1
            WHERE symbol = '{instrument}'
              AND toYear(timestamp) = {year}
            GROUP BY symbol, timestamp
            ORDER BY timestamp
            """
            
            result = self.client.command(insert_sql)
            
            # 获取插入的行数
            count_sql = f"""
            SELECT count(*) 
            FROM {table_name} 
            WHERE symbol = '{instrument}' AND toYear(timestamp) = {year}
            """
            rows = self.client.command(count_sql)
            
            self.logger.debug(f"回填 {instrument} {year} {timeframe} 数据: {rows} 行")
            return rows
            
        except Exception as e:
            self.logger.error(f"回填 {instrument} {year} {timeframe} 数据失败: {e}")
            return 0
    
    def get_available_years(self, instrument: str) -> List[int]:
        """获取某个货币对的可用年份"""
        try:
            query = f"""
            SELECT DISTINCT toYear(timestamp) as year
            FROM forex_data.ohlcv_m1
            WHERE symbol = '{instrument}'
            ORDER BY year
            """
            result = self.client.query(query)
            return [row[0] for row in result.result_rows]
        except Exception as e:
            self.logger.error(f"获取 {instrument} 可用年份失败: {e}")
            return []
    
    def setup_all(self, backfill: bool = True):
        """设置所有物化视图"""
        print("=" * 80)
        print("🚀 开始设置 ClickHouse 物化视图")
        print("=" * 80)
        print()
        
        # 连接到 ClickHouse
        self.connect()
        
        # 1. 创建时间周期表和物化视图
        print("📊 创建表和物化视图...")
        print()
        
        for timeframe, config in self.TIMEFRAMES.items():
            desc = config['description']
            print(f"⏱️  {timeframe} ({desc})")
            
            # 创建表
            if self.create_timeframe_table(timeframe):
                print(f"  ✅ 表创建成功")
                self.stats['tables_created'] += 1
            else:
                print(f"  ❌ 表创建失败")
                self.stats['errors'] += 1
                continue
            
            # 创建物化视图
            if self.create_materialized_view(timeframe):
                print(f"  ✅ 物化视图创建成功")
                self.stats['views_created'] += 1
            else:
                print(f"  ❌ 物化视图创建失败")
                self.stats['errors'] += 1
            
            print()
        
        # 2. 回填历史数据（可选）
        if backfill:
            print("\n" + "=" * 80)
            print("📥 回填历史数据...")
            print("=" * 80)
            print()
            
            for instrument in self.INSTRUMENTS:
                # 获取可用年份
                years = self.get_available_years(instrument)
                
                if not years:
                    print(f"⚠️  {instrument}: 没有可用数据")
                    continue
                
                print(f"💱 {instrument} ({len(years)} 年)")
                
                for timeframe in self.TIMEFRAMES.keys():
                    # 初始化进度网格
                    self.progress_grid.initialize_grid(instrument, timeframe, 'backfill', len(years))
                    
                    year_index = 0
                    for year in years:
                        rows = self.backfill_historical_data(timeframe, instrument, year)
                        
                        if rows > 0:
                            self.progress_grid.update_status(
                                instrument, timeframe, 'backfill', year_index, ProgressStatus.SUCCESS
                            )
                            self.stats['backfill_rows'] += rows
                        else:
                            self.progress_grid.update_status(
                                instrument, timeframe, 'backfill', year_index, ProgressStatus.SKIPPED
                            )
                        
                        self.progress_grid.display_line(
                            instrument, timeframe, 'backfill', 
                            f"{instrument} {timeframe} 回填"
                        )
                        year_index += 1
                    
                    self.progress_grid.newline()
                
                print()
        
        # 3. 显示汇总
        print("\n" + "=" * 80)
        print("📊 设置完成汇总")
        print("=" * 80)
        print(f"✅ 创建表数量: {self.stats['tables_created']}")
        print(f"✅ 创建物化视图数量: {self.stats['views_created']}")
        if backfill:
            print(f"✅ 回填数据行数: {self.stats['backfill_rows']:,}")
        print(f"❌ 错误数量: {self.stats['errors']}")
        print()
        
        # 4. 显示使用说明
        print("=" * 80)
        print("📖 使用说明")
        print("=" * 80)
        print()
        print("✨ 物化视图已设置完成！")
        print()
        print("🔄 自动聚合规则:")
        print("   - 当新的 M1 数据插入到 fxcm_m1 表时")
        print("   - 物化视图会自动触发聚合")
        print("   - 自动生成 M5、M15、M30、H1 数据")
        print("   - 无需运行任何额外脚本！")
        print()
        print("📊 数据表:")
        print("   - fxcm_m1  (源数据)")
        print("   - fxcm_m5  (自动聚合)")
        print("   - fxcm_m15 (自动聚合)")
        print("   - fxcm_m30 (自动聚合)")
        print("   - fxcm_h1  (自动聚合)")
        print()
        print("🔍 验证数据:")
        print("   SELECT instrument, count(*) as rows")
        print("   FROM fxcm_m5")
        print("   GROUP BY instrument")
        print("   ORDER BY instrument;")
        print()
        print("=" * 80)
        print()
    
    def verify_setup(self):
        """验证物化视图设置"""
        print("\n" + "=" * 80)
        print("🔍 验证物化视图设置")
        print("=" * 80)
        print()
        
        self.connect()
        
        # 检查表是否存在
        for timeframe in self.TIMEFRAMES.keys():
            table_name = f'forex_data.ohlcv_{timeframe.lower()}'
            mv_name = f'{table_name}_mv'
            
            # 检查表
            table_exists_sql = f"EXISTS TABLE {table_name}"
            table_exists = self.client.command(table_exists_sql)
            
            # 检查物化视图
            mv_exists_sql = f"EXISTS VIEW {mv_name}"
            mv_exists = self.client.command(mv_exists_sql)
            
            # 获取行数
            if table_exists:
                count_sql = f"SELECT count(*) FROM {table_name}"
                row_count = self.client.command(count_sql)
            else:
                row_count = 0
            
            # 显示结果
            table_status = "✅" if table_exists else "❌"
            mv_status = "✅" if mv_exists else "❌"
            
            print(f"{timeframe}:")
            print(f"  表 {table_name}: {table_status}")
            print(f"  视图 {mv_name}: {mv_status}")
            print(f"  数据行数: {row_count:,}")
            print()
    
    def cleanup(self):
        """清理：删除所有物化视图和表"""
        print("\n" + "=" * 80)
        print("🗑️  清理物化视图和表")
        print("=" * 80)
        print()
        
        response = input("⚠️  确定要删除所有物化视图和表吗？(yes/no): ")
        if response.lower() != 'yes':
            print("❌ 操作已取消")
            return
        
        self.connect()
        
        for timeframe in self.TIMEFRAMES.keys():
            table_name = f'forex_data.ohlcv_{timeframe.lower()}'
            mv_name = f'{table_name}_mv'
            
            try:
                # 删除物化视图
                self.client.command(f"DROP VIEW IF EXISTS {mv_name}")
                print(f"✅ 删除物化视图: {mv_name}")
                
                # 删除表
                self.client.command(f"DROP TABLE IF EXISTS {table_name}")
                print(f"✅ 删除表: {table_name}")
                
            except Exception as e:
                print(f"❌ 删除失败: {e}")
        
        print("\n✅ 清理完成")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='ClickHouse 物化视图设置脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--mode',
        choices=['setup', 'verify', 'cleanup'],
        default='setup',
        help='运行模式: setup(设置), verify(验证), cleanup(清理)'
    )
    
    parser.add_argument(
        '--no-backfill',
        action='store_true',
        help='不回填历史数据（仅创建表和视图）'
    )
    
    args = parser.parse_args()
    
    try:
        manager = ClickHouseMaterializedViewSetup()
        
        if args.mode == 'setup':
            manager.setup_all(backfill=not args.no_backfill)
        elif args.mode == 'verify':
            manager.verify_setup()
        elif args.mode == 'cleanup':
            manager.cleanup()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
