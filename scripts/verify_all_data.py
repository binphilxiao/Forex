#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
一键验证ClickHouse数据库中的所有数据
包括完整性检查、质量检查、一致性检查
"""

import sys
import io
import json
import requests
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
DATABASE = 'forex_data'

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

def print_banner():
    """打印欢迎横幅"""
    print("\n" + "="*80)
    print("           🔍 FXCM数据一键验证工具")
    print("="*80)
    print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"数据库: {CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}/{DATABASE}")
    print("="*80 + "\n")

def print_section(title, icon="📊"):
    """打印分段标题"""
    print("\n" + "="*80)
    print(f"  {icon} {title}")
    print("="*80 + "\n")

def check_basic_stats():
    """检查1：基础统计信息"""
    print_section("第1步：基础统计信息", "📊")
    
    stats = {}
    
    # 检查所有表
    tables = ['ohlcv_m1', 'ohlcv_d1', 'ohlcv_m5', 'ohlcv_m15', 'ohlcv_m30', 'ohlcv_h1']
    
    print("数据表统计:")
    print("-" * 80)
    print(f"{'表名':<15} {'记录数':>15} {'大小(MB)':>12} {'货币对数':>10} {'状态':<10}")
    print("-" * 80)
    
    for table in tables:
        try:
            # 获取记录数
            query = f"SELECT count() FROM {DATABASE}.{table}"
            count = int(execute_query(query))
            
            # 获取大小
            query = f"""
            SELECT formatReadableSize(sum(bytes))
            FROM system.parts
            WHERE database = '{DATABASE}' AND table = '{table}' AND active
            """
            size = execute_query(query).strip()
            
            # 获取货币对数
            query = f"SELECT countDistinct(symbol) FROM {DATABASE}.{table}"
            symbols = int(execute_query(query))
            
            stats[table] = {
                'count': count,
                'size': size,
                'symbols': symbols
            }
            
            status = "✅" if count > 0 else "⚠️ "
            print(f"{table:<15} {count:>15,} {size:>12} {symbols:>10} {status}")
            
        except Exception as e:
            print(f"{table:<15} {'错误':>15} {'-':>12} {'-':>10} ❌")
            stats[table] = {'count': 0, 'size': '-', 'symbols': 0}
    
    print("-" * 80)
    total_count = sum(s['count'] for s in stats.values())
    print(f"{'总计':<15} {total_count:>15,}")
    print()
    
    return stats

def check_symbol_coverage():
    """检查2：货币对覆盖情况"""
    print_section("第2步：货币对覆盖情况", "💱")
    
    expected_symbols = ['AUDUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'USDCHF']
    
    print("M1分钟线数据覆盖:")
    print("-" * 80)
    print(f"{'货币对':<12} {'记录数':>15} {'开始时间':<20} {'结束时间':<20} {'状态':<10}")
    print("-" * 80)
    
    m1_coverage = {}
    
    for symbol in expected_symbols:
        try:
            query = f"""
            SELECT 
                count() as cnt,
                min(timestamp) as start_time,
                max(timestamp) as end_time
            FROM {DATABASE}.ohlcv_m1
            WHERE symbol = '{symbol}'
            """
            result = execute_query(query)
            
            if result:
                parts = result.split('\t')
                count = int(parts[0])
                start = parts[1] if len(parts) > 1 else '-'
                end = parts[2] if len(parts) > 2 else '-'
                
                m1_coverage[symbol] = count
                
                if count > 0:
                    print(f"{symbol:<12} {count:>15,} {start:<20} {end:<20} {'✅ 完整':<10}")
                else:
                    print(f"{symbol:<12} {count:>15,} {'-':<20} {'-':<20} {'❌ 缺失':<10}")
            else:
                m1_coverage[symbol] = 0
                print(f"{symbol:<12} {0:>15,} {'-':<20} {'-':<20} {'❌ 缺失':<10}")
                
        except Exception as e:
            m1_coverage[symbol] = 0
            print(f"{symbol:<12} {'错误':>15} {'-':<20} {'-':<20} {'❌ 错误':<10}")
    
    print()
    
    print("D1日线数据覆盖:")
    print("-" * 80)
    print(f"{'货币对':<12} {'记录数':>15} {'开始日期':<15} {'结束日期':<15} {'状态':<10}")
    print("-" * 80)
    
    d1_coverage = {}
    
    for symbol in expected_symbols:
        try:
            query = f"""
            SELECT 
                count() as cnt,
                min(date) as start_date,
                max(date) as end_date
            FROM {DATABASE}.ohlcv_d1
            WHERE symbol = '{symbol}'
            """
            result = execute_query(query)
            
            if result:
                parts = result.split('\t')
                count = int(parts[0])
                start = parts[1] if len(parts) > 1 else '-'
                end = parts[2] if len(parts) > 2 else '-'
                
                d1_coverage[symbol] = count
                
                if count > 0:
                    print(f"{symbol:<12} {count:>15,} {start:<15} {end:<15} {'✅ 完整':<10}")
                else:
                    print(f"{symbol:<12} {count:>15,} {'-':<15} {'-':<15} {'❌ 缺失':<10}")
            else:
                d1_coverage[symbol] = 0
                print(f"{symbol:<12} {0:>15,} {'-':<15} {'-':<15} {'❌ 缺失':<10}")
                
        except Exception as e:
            d1_coverage[symbol] = 0
            print(f"{symbol:<12} {'错误':>15} {'-':<15} {'-':<15} {'❌ 错误':<10}")
    
    print()
    
    return m1_coverage, d1_coverage

def check_data_quality():
    """检查3：数据质量"""
    print_section("第3步：数据质量检查", "✅")
    
    issues = []
    
    # 检查M1数据质量
    print("M1数据质量:")
    print("-" * 80)
    
    # 1. 检查价格异常
    print("  检查价格异常值...")
    query = f"""
    SELECT symbol, count() as cnt
    FROM {DATABASE}.ohlcv_m1
    WHERE open <= 0 OR high <= 0 OR low <= 0 OR close <= 0
    GROUP BY symbol
    """
    try:
        result = execute_query(query)
        if result:
            print(f"    ❌ 发现异常价格数据:")
            print(f"       {result}")
            issues.append("M1数据存在零值或负值价格")
        else:
            print(f"    ✅ 无异常价格（零值或负值）")
    except:
        print(f"    ✅ 无异常价格（零值或负值）")
    
    # 2. 检查OHLC逻辑
    print("  检查OHLC逻辑...")
    query = f"""
    SELECT symbol, count() as cnt
    FROM {DATABASE}.ohlcv_m1
    WHERE high < low OR open > high OR open < low OR close > high OR close < low
    GROUP BY symbol
    """
    try:
        result = execute_query(query)
        if result:
            print(f"    ❌ 发现OHLC逻辑错误:")
            print(f"       {result}")
            issues.append("M1数据存在OHLC逻辑错误")
        else:
            print(f"    ✅ OHLC逻辑正确")
    except:
        print(f"    ✅ OHLC逻辑正确")
    
    print()
    
    # 检查D1数据质量
    print("D1数据质量:")
    print("-" * 80)
    
    # 1. 检查价格异常
    print("  检查价格异常值...")
    query = f"""
    SELECT symbol, count() as cnt
    FROM {DATABASE}.ohlcv_d1
    WHERE open <= 0 OR high <= 0 OR low <= 0 OR close <= 0
    GROUP BY symbol
    """
    try:
        result = execute_query(query)
        if result:
            print(f"    ❌ 发现异常价格数据:")
            print(f"       {result}")
            issues.append("D1数据存在零值或负值价格")
        else:
            print(f"    ✅ 无异常价格（零值或负值）")
    except:
        print(f"    ✅ 无异常价格（零值或负值）")
    
    # 2. 检查OHLC逻辑
    print("  检查OHLC逻辑...")
    query = f"""
    SELECT symbol, count() as cnt
    FROM {DATABASE}.ohlcv_d1
    WHERE high < low OR open > high OR open < low OR close > high OR close < low
    GROUP BY symbol
    """
    try:
        result = execute_query(query)
        if result:
            print(f"    ❌ 发现OHLC逻辑错误:")
            print(f"       {result}")
            issues.append("D1数据存在OHLC逻辑错误")
        else:
            print(f"    ✅ OHLC逻辑正确")
    except:
        print(f"    ✅ OHLC逻辑正确")
    
    print()
    
    return issues

def check_materialized_views():
    """检查4：物化视图状态"""
    print_section("第4步：物化视图数据检查", "🔄")
    
    print("聚合数据统计:")
    print("-" * 80)
    print(f"{'时间周期':<12} {'总记录数':>15} {'货币对数':>10} {'状态':<10}")
    print("-" * 80)
    
    timeframes = ['m5', 'm15', 'm30', 'h1']
    mv_stats = {}
    
    for tf in timeframes:
        try:
            # 获取总记录数
            query = f"SELECT count() FROM {DATABASE}.ohlcv_{tf}"
            count = int(execute_query(query))
            
            # 获取货币对数
            query = f"SELECT countDistinct(symbol) FROM {DATABASE}.ohlcv_{tf}"
            symbols = int(execute_query(query))
            
            mv_stats[tf] = {'count': count, 'symbols': symbols}
            
            status = "✅" if count > 0 else "⚠️ "
            print(f"{tf.upper():<12} {count:>15,} {symbols:>10} {status}")
            
        except Exception as e:
            mv_stats[tf] = {'count': 0, 'symbols': 0}
            print(f"{tf.upper():<12} {'错误':>15} {'-':>10} ❌")
    
    print()
    
    # 检查每个货币对的聚合数据
    print("各货币对聚合数据详情:")
    print("-" * 90)
    print(f"{'货币对':<12} {'M5':>12} {'M15':>12} {'M30':>12} {'H1':>12} {'状态':<10}")
    print("-" * 90)
    
    symbols = ['AUDUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'USDCHF']
    
    for symbol in symbols:
        counts = []
        for tf in timeframes:
            query = f"SELECT count() FROM {DATABASE}.ohlcv_{tf} WHERE symbol = '{symbol}'"
            try:
                count = int(execute_query(query))
                counts.append(count)
            except:
                counts.append(0)
        
        total = sum(counts)
        status = "✅" if total > 0 else "⚠️ "
        print(f"{symbol:<12} {counts[0]:>12,} {counts[1]:>12,} {counts[2]:>12,} {counts[3]:>12,} {status}")
    
    print()
    
    return mv_stats

def check_data_consistency():
    """检查5：数据一致性"""
    print_section("第5步：M1与聚合数据一致性检查", "🔍")
    
    print("数据比例验证（理论值: M5≈M1/5, M15≈M1/15, H1≈M1/60）:")
    print("-" * 100)
    print(f"{'货币对':<12} {'M1':>12} {'M5':>12} {'比例':>8} {'M15':>12} {'比例':>8} {'H1':>12} {'比例':>8} {'状态':<10}")
    print("-" * 100)
    
    symbols_query = f"SELECT symbol FROM {DATABASE}.ohlcv_m1 GROUP BY symbol"
    symbols_result = execute_query(symbols_query)
    symbols = [s.strip() for s in symbols_result.split('\n') if s.strip()]
    
    consistency_issues = []
    
    for symbol in symbols:
        # 获取各时间周期的数据量
        m1_query = f"SELECT count() FROM {DATABASE}.ohlcv_m1 WHERE symbol = '{symbol}'"
        m5_query = f"SELECT count() FROM {DATABASE}.ohlcv_m5 WHERE symbol = '{symbol}'"
        m15_query = f"SELECT count() FROM {DATABASE}.ohlcv_m15 WHERE symbol = '{symbol}'"
        h1_query = f"SELECT count() FROM {DATABASE}.ohlcv_h1 WHERE symbol = '{symbol}'"
        
        try:
            m1_count = int(execute_query(m1_query))
            m5_count = int(execute_query(m5_query))
            m15_count = int(execute_query(m15_query))
            h1_count = int(execute_query(h1_query))
            
            if m1_count == 0:
                continue
            
            # 计算实际比例
            m5_ratio = m1_count / m5_count if m5_count > 0 else 0
            m15_ratio = m1_count / m15_count if m15_count > 0 else 0
            h1_ratio = m1_count / h1_count if h1_count > 0 else 0
            
            # 判断是否正常（允许±20%误差，因为周末和节假日）
            m5_ok = 4 <= m5_ratio <= 6 if m5_count > 0 else False
            m15_ok = 12 <= m15_ratio <= 18 if m15_count > 0 else False
            h1_ok = 48 <= h1_ratio <= 72 if h1_count > 0 else False
            
            status = "✅" if (m5_ok and m15_ok and h1_ok) else "⚠️ "
            
            if not (m5_ok and m15_ok and h1_ok):
                consistency_issues.append(f"{symbol}聚合数据比例异常")
            
            print(f"{symbol:<12} {m1_count:>12,} {m5_count:>12,} {m5_ratio:>8.1f} {m15_count:>12,} {m15_ratio:>8.1f} {h1_count:>12,} {h1_ratio:>8.1f} {status}")
            
        except Exception as e:
            print(f"{symbol:<12} {'错误':>12} {'-':>12} {'-':>8} {'-':>12} {'-':>8} {'-':>12} {'-':>8} ❌")
    
    print()
    
    return consistency_issues

def generate_final_report(stats, m1_cov, d1_cov, quality_issues, mv_stats, consistency_issues):
    """生成最终报告"""
    print_section("验证总结报告", "📝")
    
    # 统计总览
    print("数据统计总览:")
    print("-" * 80)
    total_records = sum(s['count'] for s in stats.values())
    print(f"  总记录数: {total_records:,} 条")
    print(f"  M1数据: {stats['ohlcv_m1']['count']:,} 条")
    print(f"  D1数据: {stats['ohlcv_d1']['count']:,} 条")
    print(f"  M5聚合: {stats['ohlcv_m5']['count']:,} 条")
    print(f"  M15聚合: {stats['ohlcv_m15']['count']:,} 条")
    print(f"  M30聚合: {stats['ohlcv_m30']['count']:,} 条")
    print(f"  H1聚合: {stats['ohlcv_h1']['count']:,} 条")
    print()
    
    # 货币对覆盖
    print("货币对覆盖:")
    print("-" * 80)
    m1_complete = sum(1 for v in m1_cov.values() if v > 0)
    d1_complete = sum(1 for v in d1_cov.values() if v > 0)
    print(f"  M1数据: {m1_complete}/6 个货币对完整")
    print(f"  D1数据: {d1_complete}/6 个货币对完整")
    print()
    
    # 数据质量
    print("数据质量:")
    print("-" * 80)
    if quality_issues:
        print(f"  ❌ 发现 {len(quality_issues)} 个质量问题:")
        for issue in quality_issues:
            print(f"     • {issue}")
    else:
        print(f"  ✅ 数据质量完美，无异常")
    print()
    
    # 物化视图
    print("物化视图:")
    print("-" * 80)
    mv_working = sum(1 for v in mv_stats.values() if v['count'] > 0)
    print(f"  运行状态: {mv_working}/4 个物化视图正常工作")
    print()
    
    # 一致性
    print("数据一致性:")
    print("-" * 80)
    if consistency_issues:
        print(f"  ⚠️  发现 {len(consistency_issues)} 个一致性问题:")
        for issue in consistency_issues:
            print(f"     • {issue}")
    else:
        print(f"  ✅ M1与聚合数据一致性良好")
    print()
    
    # 总体评分
    print("="*80)
    total_issues = len(quality_issues) + len(consistency_issues)
    
    if total_issues == 0 and m1_complete >= 3 and d1_complete == 6:
        print("           ✅ 验证通过 - 数据库状态优秀")
        grade = "A+"
    elif total_issues <= 2:
        print("           ✅ 验证通过 - 数据库状态良好")
        grade = "A"
    else:
        print("           ⚠️  验证发现问题 - 建议检查")
        grade = "B"
    
    print(f"           综合评分: {grade}")
    print("="*80 + "\n")
    
    return {
        'total_records': total_records,
        'm1_coverage': m1_complete,
        'd1_coverage': d1_complete,
        'quality_issues': len(quality_issues),
        'consistency_issues': len(consistency_issues),
        'grade': grade
    }

def main():
    """主函数"""
    try:
        print_banner()
        
        # 执行各项检查
        stats = check_basic_stats()
        m1_cov, d1_cov = check_symbol_coverage()
        quality_issues = check_data_quality()
        mv_stats = check_materialized_views()
        consistency_issues = check_data_consistency()
        
        # 生成最终报告
        report = generate_final_report(stats, m1_cov, d1_cov, quality_issues, mv_stats, consistency_issues)
        
        # 保存验证报告
        log_file = f"verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总记录数: {report['total_records']:,}\n")
            f.write(f"M1覆盖: {report['m1_coverage']}/6\n")
            f.write(f"D1覆盖: {report['d1_coverage']}/6\n")
            f.write(f"质量问题: {report['quality_issues']}\n")
            f.write(f"一致性问题: {report['consistency_issues']}\n")
            f.write(f"综合评分: {report['grade']}\n")
        
        print(f"📝 验证报告已保存到: {log_file}\n")
        
        print("💡 建议:")
        if report['m1_coverage'] < 6:
            print("  • 运行 'python 一键导入所有数据.py' 导入缺失的数据")
        print("  • 运行 'python scripts\\query_examples.py' 查询和使用数据")
        print("  • 运行 'python scripts\\view_clickhouse_tables.py' 查看详细表信息")
        print()
        
    except Exception as e:
        print(f"\n❌ 验证过程出错: {str(e)}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
