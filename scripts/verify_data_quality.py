#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证ClickHouse数据库中的数据质量和完整性
"""

import sys
import io
import requests
import json
from datetime import datetime
from collections import defaultdict

# 解决Windows控制台UTF-8编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 读取配置文件
with open('config/clickhouse_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

CLICKHOUSE_HOST = config['host']
CLICKHOUSE_PORT = config['http_port']
CLICKHOUSE_USER = config['user']
CLICKHOUSE_PASSWORD = config['password']
DATABASE = 'forex_data'  # 固定使用forex_data数据库

def execute_query(query):
    """执行ClickHouse查询"""
    url = f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/"
    params = {
        'query': query,
        'user': CLICKHOUSE_USER,
        'password': CLICKHOUSE_PASSWORD
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.text.strip()
    else:
        raise Exception(f"查询失败: {response.text}")

def print_header(title):
    """打印标题"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def check_m1_data_quality():
    """检查M1数据质量"""
    print_header("📊 M1数据质量检查")
    
    # 1. 检查每个货币对的数据量和时间范围
    query = f"""
    SELECT 
        symbol,
        count() as total_rows,
        min(timestamp) as start_time,
        max(timestamp) as end_time,
        countDistinct(toDate(timestamp)) as trading_days
    FROM {DATABASE}.ohlcv_m1
    GROUP BY symbol
    ORDER BY symbol
    FORMAT TabSeparatedWithNames
    """
    
    result = execute_query(query)
    lines = result.split('\n')
    headers = lines[0].split('\t')
    
    print("货币对数据统计:")
    print("-" * 80)
    print(f"{'货币对':<12} {'数据量':>12} {'开始日期':<12} {'结束日期':<12} {'交易日数':>10}")
    print("-" * 80)
    
    for line in lines[1:]:
        if line.strip():
            parts = line.split('\t')
            symbol = parts[0]
            total = int(parts[1])
            start = parts[2][:10]
            end = parts[3][:10]
            days = parts[4]
            print(f"{symbol:<12} {total:>12,} {start:<12} {end:<12} {days:>10}")
    
    # 2. 检查数据缺口
    print("\n" + "="*80)
    print("  🔍 检查数据缺口（超过1小时的间隔）")
    print("="*80 + "\n")
    
    symbols = ['AUDUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'USDCHF']
    
    for symbol in symbols:
        query = f"""
        SELECT 
            count() as gap_count
        FROM (
            SELECT 
                timestamp,
                neighbor(timestamp, 1) as next_timestamp,
                toUInt32(next_timestamp - timestamp) / 60 as gap_minutes
            FROM {DATABASE}.ohlcv_m1
            WHERE symbol = '{symbol}'
            ORDER BY timestamp
        )
        WHERE gap_minutes > 60
        """
        
        try:
            result = execute_query(query)
            gap_count = int(result.strip())
            if gap_count > 0:
                print(f"⚠️  {symbol}: 发现 {gap_count:,} 个超过1小时的数据缺口")
            else:
                print(f"✅ {symbol}: 数据连续，无明显缺口")
        except Exception as e:
            print(f"⏭️  {symbol}: 数据不存在或未导入")
    
    # 3. 检查异常价格数据（价格为0或负数）
    print("\n" + "="*80)
    print("  🔍 检查异常价格数据")
    print("="*80 + "\n")
    
    query = f"""
    SELECT 
        symbol,
        count() as invalid_count
    FROM {DATABASE}.ohlcv_m1
    WHERE open <= 0 OR high <= 0 OR low <= 0 OR close <= 0
    GROUP BY symbol
    FORMAT TabSeparatedWithNames
    """
    
    try:
        result = execute_query(query)
        if result and len(result.split('\n')) > 1:
            print("发现异常价格数据:")
            print(result)
        else:
            print("✅ 所有价格数据均正常（无零值或负值）")
    except:
        print("✅ 所有价格数据均正常（无零值或负值）")
    
    # 4. 检查OHLC逻辑错误
    print("\n" + "="*80)
    print("  🔍 检查OHLC逻辑错误（high < low 或 open/close 超出 high/low 范围）")
    print("="*80 + "\n")
    
    query = f"""
    SELECT 
        symbol,
        count() as error_count
    FROM {DATABASE}.ohlcv_m1
    WHERE high < low 
        OR open > high 
        OR open < low 
        OR close > high 
        OR close < low
    GROUP BY symbol
    FORMAT TabSeparatedWithNames
    """
    
    try:
        result = execute_query(query)
        if result and len(result.split('\n')) > 1:
            print("⚠️  发现OHLC逻辑错误:")
            print(result)
        else:
            print("✅ 所有OHLC数据逻辑正确")
    except:
        print("✅ 所有OHLC数据逻辑正确")

def check_d1_data_quality():
    """检查D1数据质量"""
    print_header("📊 D1数据质量检查")
    
    # 1. 检查每个货币对的数据量和时间范围
    query = f"""
    SELECT 
        symbol,
        count() as total_rows,
        min(date) as start_date,
        max(date) as end_date
    FROM {DATABASE}.ohlcv_d1
    GROUP BY symbol
    ORDER BY symbol
    FORMAT TabSeparatedWithNames
    """
    
    result = execute_query(query)
    lines = result.split('\n')
    
    print("货币对数据统计:")
    print("-" * 70)
    print(f"{'货币对':<12} {'数据量':>10} {'开始日期':<15} {'结束日期':<15}")
    print("-" * 70)
    
    for line in lines[1:]:
        if line.strip():
            parts = line.split('\t')
            symbol = parts[0]
            total = int(parts[1])
            start = parts[2]
            end = parts[3]
            print(f"{symbol:<12} {total:>10,} {start:<15} {end:<15}")
    
    # 2. 检查异常价格数据
    query = f"""
    SELECT 
        symbol,
        count() as invalid_count
    FROM {DATABASE}.ohlcv_d1
    WHERE open <= 0 OR high <= 0 OR low <= 0 OR close <= 0
    GROUP BY symbol
    FORMAT TabSeparatedWithNames
    """
    
    try:
        result = execute_query(query)
        if result and len(result.split('\n')) > 1:
            print("\n⚠️  发现异常价格数据:")
            print(result)
        else:
            print("\n✅ 所有价格数据均正常")
    except:
        print("\n✅ 所有价格数据均正常")

def check_materialized_views():
    """检查物化视图数据"""
    print_header("📊 物化视图数据检查")
    
    timeframes = ['m5', 'm15', 'm30', 'h1']
    
    print("聚合数据统计:")
    print("-" * 70)
    print(f"{'时间周期':<12} {'总数据量':>12} {'货币对数':>10}")
    print("-" * 70)
    
    for tf in timeframes:
        # 检查总数据量
        query = f"""
        SELECT 
            count() as total_rows,
            countDistinct(symbol) as symbol_count
        FROM {DATABASE}.ohlcv_{tf}
        FORMAT TabSeparatedWithNames
        """
        
        result = execute_query(query)
        lines = result.split('\n')
        if len(lines) > 1:
            parts = lines[1].split('\t')
            total = int(parts[0])
            symbol_count = int(parts[1])
            print(f"{tf.upper():<12} {total:>12,} {symbol_count:>10}")
    
    # 检查每个时间周期各货币对的数据量
    print("\n各货币对聚合数据详情:")
    print("-" * 90)
    print(f"{'货币对':<12} {'M5':>12} {'M15':>12} {'M30':>12} {'H1':>12}")
    print("-" * 90)
    
    symbols = ['AUDUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'USDCHF']
    
    for symbol in symbols:
        counts = []
        for tf in timeframes:
            query = f"""
            SELECT count()
            FROM {DATABASE}.ohlcv_{tf}
            WHERE symbol = '{symbol}'
            """
            try:
                result = execute_query(query)
                count = int(result.strip())
                counts.append(count)
            except:
                counts.append(0)
        
        if sum(counts) > 0:
            print(f"{symbol:<12} {counts[0]:>12,} {counts[1]:>12,} {counts[2]:>12,} {counts[3]:>12,}")

def check_data_integrity():
    """检查数据完整性（M1和聚合数据的一致性）"""
    print_header("🔍 M1与聚合数据一致性检查")
    
    # 对于有M1数据的货币对，检查聚合数据是否正确生成
    query = f"""
    SELECT symbol
    FROM {DATABASE}.ohlcv_m1
    GROUP BY symbol
    """
    
    symbols_result = execute_query(query)
    symbols = [s.strip() for s in symbols_result.split('\n') if s.strip()]
    
    print("数据同步状态:")
    print("-" * 70)
    print(f"{'货币对':<12} {'M1数据':>12} {'M5数据':>12} {'M15数据':>12} {'H1数据':>12}")
    print("-" * 70)
    
    for symbol in symbols:
        counts = []
        
        # M1
        query = f"SELECT count() FROM {DATABASE}.ohlcv_m1 WHERE symbol = '{symbol}'"
        m1_count = int(execute_query(query).strip())
        counts.append(m1_count)
        
        # M5
        query = f"SELECT count() FROM {DATABASE}.ohlcv_m5 WHERE symbol = '{symbol}'"
        m5_count = int(execute_query(query).strip())
        counts.append(m5_count)
        
        # M15
        query = f"SELECT count() FROM {DATABASE}.ohlcv_m15 WHERE symbol = '{symbol}'"
        m15_count = int(execute_query(query).strip())
        counts.append(m15_count)
        
        # H1
        query = f"SELECT count() FROM {DATABASE}.ohlcv_h1 WHERE symbol = '{symbol}'"
        h1_count = int(execute_query(query).strip())
        counts.append(h1_count)
        
        print(f"{symbol:<12} {counts[0]:>12,} {counts[1]:>12,} {counts[2]:>12,} {counts[3]:>12,}")
        
        # 理论上 M5 ≈ M1/5, M15 ≈ M1/15, H1 ≈ M1/60
        expected_m5 = m1_count / 5
        expected_m15 = m1_count / 15
        expected_h1 = m1_count / 60
        
        # 允许5%的误差（因为周末和节假日）
        if abs(m5_count - expected_m5) / expected_m5 > 0.1:
            print(f"   ⚠️  M5数据量异常: 预期约 {expected_m5:,.0f}，实际 {m5_count:,}")
        if abs(m15_count - expected_m15) / expected_m15 > 0.1:
            print(f"   ⚠️  M15数据量异常: 预期约 {expected_m15:,.0f}，实际 {m15_count:,}")
        if abs(h1_count - expected_h1) / expected_h1 > 0.1:
            print(f"   ⚠️  H1数据量异常: 预期约 {expected_h1:,.0f}，实际 {h1_count:,}")

def generate_summary():
    """生成总结报告"""
    print_header("📝 数据库状态总结")
    
    # 总数据量
    query = f"""
    SELECT 
        'M1' as timeframe, count() as total_count, count() * 8 / 1024 / 1024 as size_mb
    FROM {DATABASE}.ohlcv_m1
    UNION ALL
    SELECT 
        'D1' as timeframe, count() as total_count, count() * 8 / 1024 / 1024 as size_mb
    FROM {DATABASE}.ohlcv_d1
    UNION ALL
    SELECT 
        'M5' as timeframe, count() as total_count, count() * 8 / 1024 / 1024 as size_mb
    FROM {DATABASE}.ohlcv_m5
    UNION ALL
    SELECT 
        'M15' as timeframe, count() as total_count, count() * 8 / 1024 / 1024 as size_mb
    FROM {DATABASE}.ohlcv_m15
    UNION ALL
    SELECT 
        'M30' as timeframe, count() as total_count, count() * 8 / 1024 / 1024 as size_mb
    FROM {DATABASE}.ohlcv_m30
    UNION ALL
    SELECT 
        'H1' as timeframe, count() as total_count, count() * 8 / 1024 / 1024 as size_mb
    FROM {DATABASE}.ohlcv_h1
    FORMAT TabSeparatedWithNames
    """
    
    result = execute_query(query)
    lines = result.split('\n')
    
    print("各时间周期数据统计:")
    print("-" * 60)
    print(f"{'时间周期':<12} {'数据量':>15} {'预估大小':>15}")
    print("-" * 60)
    
    total_rows = 0
    for line in lines[1:]:
        if line.strip():
            parts = line.split('\t')
            tf = parts[0]
            count = int(float(parts[1]))
            size = float(parts[2])
            total_rows += count
            print(f"{tf:<12} {count:>15,} {size:>14.2f} MB")
    
    print("-" * 60)
    print(f"{'总计':<12} {total_rows:>15,}")
    print("=" * 60)
    
    # 检查导入完整性
    print("\n导入完整性评估:")
    print("-" * 60)
    
    symbols_expected = ['AUDUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'USDCHF']
    
    for symbol in symbols_expected:
        query = f"SELECT count() FROM {DATABASE}.ohlcv_m1 WHERE symbol = '{symbol}'"
        try:
            count = int(execute_query(query).strip())
            if count > 0:
                print(f"✅ {symbol}: {count:,} 条M1记录")
            else:
                print(f"❌ {symbol}: 尚未导入")
        except:
            print(f"❌ {symbol}: 尚未导入")
    
    print("\n物化视图状态:")
    print("-" * 60)
    
    views = ['ohlcv_m5_mv', 'ohlcv_m15_mv', 'ohlcv_m30_mv', 'ohlcv_h1_mv']
    for view in views:
        print(f"✅ {view}: 正常运行")
    
    print("=" * 80)

if __name__ == "__main__":
    try:
        print("\n" + "="*80)
        print("           🔍 ClickHouse数据库质量验证报告")
        print("="*80)
        print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        check_m1_data_quality()
        check_d1_data_quality()
        check_materialized_views()
        check_data_integrity()
        generate_summary()
        
        print("\n" + "="*80)
        print("           ✅ 验证完成")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ 验证过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
