#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ClickHouse数据查询示例
展示如何查询和使用导入的外汇数据
"""

import sys
import io
import requests
import json
import pandas as pd
from datetime import datetime, timedelta

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
DATABASE = 'forex_data'

def execute_query(query):
    """执行ClickHouse查询并返回DataFrame"""
    url = f"http://{CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/"
    params = {
        'query': query,
        'user': CLICKHOUSE_USER,
        'password': CLICKHOUSE_PASSWORD
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        # 将TSV格式转换为DataFrame
        from io import StringIO
        return pd.read_csv(StringIO(response.text), sep='\t')
    else:
        raise Exception(f"查询失败: {response.text}")

def print_header(title):
    """打印标题"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def example1_latest_prices():
    """示例1：查询最新价格"""
    print_header("📊 示例1：查询各货币对最新价格")
    
    query = f"""
    SELECT 
        symbol,
        timestamp,
        open,
        high,
        low,
        close
    FROM {DATABASE}.ohlcv_m1
    WHERE (symbol, timestamp) IN (
        SELECT symbol, max(timestamp) as timestamp
        FROM {DATABASE}.ohlcv_m1
        GROUP BY symbol
    )
    ORDER BY symbol
    """
    
    df = execute_query(query)
    print(df.to_string(index=False))
    print()

def example2_daily_stats():
    """示例2：查询某个货币对的日统计"""
    print_header("📊 示例2：EURUSD近30天统计（使用H1数据）")
    
    query = f"""
    SELECT 
        toDate(timestamp) as date,
        min(low) as daily_low,
        max(high) as daily_high,
        argMin(open, timestamp) as open,
        argMax(close, timestamp) as close,
        round(max(high) - min(low), 5) as daily_range
    FROM {DATABASE}.ohlcv_h1
    WHERE symbol = 'EURUSD'
        AND timestamp >= today() - INTERVAL 30 DAY
    GROUP BY date
    ORDER BY date DESC
    LIMIT 10
    """
    
    df = execute_query(query)
    print(df.to_string(index=False))
    print()

def example3_volatility():
    """示例3：计算波动率"""
    print_header("📊 示例3：各货币对日均波动率（基于H1数据）")
    
    query = f"""
    SELECT 
        symbol,
        round(avg(high - low), 5) as avg_hourly_range,
        round(min(high - low), 5) as min_hourly_range,
        round(max(high - low), 5) as max_hourly_range,
        count() as sample_size
    FROM {DATABASE}.ohlcv_h1
    WHERE timestamp >= today() - INTERVAL 30 DAY
    GROUP BY symbol
    ORDER BY avg_hourly_range DESC
    """
    
    df = execute_query(query)
    print(df.to_string(index=False))
    print()

def example4_price_history():
    """示例4：查询特定时间段的价格历史"""
    print_header("📊 示例4：AUDUSD最近7天的日K线数据")
    
    query = f"""
    SELECT 
        date,
        open,
        high,
        low,
        close,
        round((close - open) / open * 100, 2) as change_pct
    FROM {DATABASE}.ohlcv_d1
    WHERE symbol = 'AUDUSD'
        AND date >= today() - INTERVAL 7 DAY
    ORDER BY date DESC
    """
    
    df = execute_query(query)
    print(df.to_string(index=False))
    print()

def example5_intraday_pattern():
    """示例5：分析日内模式"""
    print_header("📊 示例5：EURUSD各小时平均波动（基于最近30天数据）")
    
    query = f"""
    SELECT 
        toHour(timestamp) as hour,
        round(avg(high - low), 5) as avg_range,
        count() as samples
    FROM {DATABASE}.ohlcv_h1
    WHERE symbol = 'EURUSD'
        AND timestamp >= today() - INTERVAL 30 DAY
    GROUP BY hour
    ORDER BY hour
    """
    
    df = execute_query(query)
    print(df.to_string(index=False))
    print()

def example6_multi_timeframe():
    """示例6：多时间框架分析"""
    print_header("📊 示例6：GBPUSD多时间框架对比（最新数据）")
    
    # M5
    query_m5 = f"""
    SELECT timestamp, close
    FROM {DATABASE}.ohlcv_m5
    WHERE symbol = 'GBPUSD'
    ORDER BY timestamp DESC
    LIMIT 1
    """
    
    # M15
    query_m15 = f"""
    SELECT timestamp, close
    FROM {DATABASE}.ohlcv_m15
    WHERE symbol = 'GBPUSD'
    ORDER BY timestamp DESC
    LIMIT 1
    """
    
    # H1
    query_h1 = f"""
    SELECT timestamp, close
    FROM {DATABASE}.ohlcv_h1
    WHERE symbol = 'GBPUSD'
    ORDER BY timestamp DESC
    LIMIT 1
    """
    
    # D1
    query_d1 = f"""
    SELECT date, close
    FROM {DATABASE}.ohlcv_d1
    WHERE symbol = 'GBPUSD'
    ORDER BY date DESC
    LIMIT 1
    """
    
    print("M5最新:", execute_query(query_m5).to_string(index=False))
    print("\nM15最新:", execute_query(query_m15).to_string(index=False))
    print("\nH1最新:", execute_query(query_h1).to_string(index=False))
    print("\nD1最新:", execute_query(query_d1).to_string(index=False))
    print()

def example7_data_coverage():
    """示例7：数据覆盖情况"""
    print_header("📊 示例7：各货币对数据覆盖情况")
    
    query = f"""
    SELECT 
        symbol,
        min(timestamp) as first_record,
        max(timestamp) as last_record,
        dateDiff('day', min(timestamp), max(timestamp)) as total_days,
        count() as total_records,
        round(count() / dateDiff('day', min(timestamp), max(timestamp)) / 24 / 60, 2) as coverage_ratio
    FROM {DATABASE}.ohlcv_m1
    GROUP BY symbol
    ORDER BY symbol
    """
    
    df = execute_query(query)
    print(df.to_string(index=False))
    print("\n说明: coverage_ratio接近1表示数据完整（考虑周末和节假日，0.7-0.8为正常值）")
    print()

def example8_simple_strategy():
    """示例8：简单策略回测示例（移动平均交叉）"""
    print_header("📊 示例8：EURUSD简单移动平均（H1数据，最近100根K线）")
    
    query = f"""
    SELECT 
        timestamp,
        close,
        round(avg(close) OVER (ORDER BY timestamp ROWS BETWEEN 9 PRECEDING AND CURRENT ROW), 5) as ma10,
        round(avg(close) OVER (ORDER BY timestamp ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 5) as ma20
    FROM {DATABASE}.ohlcv_h1
    WHERE symbol = 'EURUSD'
    ORDER BY timestamp DESC
    LIMIT 10
    """
    
    df = execute_query(query)
    print(df.to_string(index=False))
    print("\n说明: 显示最近10根H1 K线的收盘价及其MA10、MA20")
    print()

def interactive_menu():
    """交互式菜单"""
    while True:
        print("\n" + "="*80)
        print("           🔍 ClickHouse外汇数据查询示例")
        print("="*80)
        print("\n请选择要运行的示例:")
        print("\n  1. 查询各货币对最新价格")
        print("  2. 查询EURUSD近期日统计")
        print("  3. 计算各货币对波动率")
        print("  4. 查询AUDUSD日K线数据")
        print("  5. 分析EURUSD日内模式")
        print("  6. 多时间框架对比")
        print("  7. 数据覆盖情况统计")
        print("  8. 移动平均计算示例")
        print("  9. 运行所有示例")
        print("  0. 退出")
        print("\n" + "="*80)
        
        choice = input("\n请输入选项 (0-9): ").strip()
        
        try:
            if choice == '1':
                example1_latest_prices()
            elif choice == '2':
                example2_daily_stats()
            elif choice == '3':
                example3_volatility()
            elif choice == '4':
                example4_price_history()
            elif choice == '5':
                example5_intraday_pattern()
            elif choice == '6':
                example6_multi_timeframe()
            elif choice == '7':
                example7_data_coverage()
            elif choice == '8':
                example8_simple_strategy()
            elif choice == '9':
                example1_latest_prices()
                example2_daily_stats()
                example3_volatility()
                example4_price_history()
                example5_intraday_pattern()
                example6_multi_timeframe()
                example7_data_coverage()
                example8_simple_strategy()
            elif choice == '0':
                print("\n再见！\n")
                break
            else:
                print("\n❌ 无效选项，请重新输入")
            
            input("\n按回车键继续...")
            
        except Exception as e:
            print(f"\n❌ 执行出错: {str(e)}")
            input("\n按回车键继续...")

if __name__ == "__main__":
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\n用户中断，退出程序。\n")
    except Exception as e:
        print(f"\n❌ 程序出错: {str(e)}")
        import traceback
        traceback.print_exc()
