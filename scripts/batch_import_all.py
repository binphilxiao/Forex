#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
一键导入所有FXCM数据到ClickHouse
包括所有货币对的M1和D1数据
支持快速模式（检查首尾记录）和HTML报告生成
"""

import sys
import io
import os
import json
import time
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# 解决Windows控制台UTF-8编码问题
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 导入自定义的导入器
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
from fxcm_importer import FXCMDataImporter
from generate_import_report import generate_html_report

def print_banner():
    """打印欢迎横幅"""
    print("\n" + "="*80)
    print("           🚀 FXCM数据一键导入工具")
    print("="*80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

def print_section(title):
    """打印分段标题"""
    print("\n" + "-"*80)
    print(f"  {title}")
    print("-"*80 + "\n")

def scan_data_files():
    """扫描所有待导入的数据文件"""
    data_root = Path('fxcm_data')
    
    if not data_root.exists():
        print("❌ 错误: fxcm_data文件夹不存在！")
        return None
    
    file_groups = {
        'M1': [],
        'D1': []
    }
    
    # 所有支持的货币对
    symbols = ['AUDUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'USDCHF']
    
    for symbol in symbols:
        symbol_path = data_root / symbol
        if not symbol_path.exists():
            continue
        
        # 扫描D1文件
        d1_path = symbol_path / 'D1'
        if d1_path.exists():
            for csv_file in sorted(d1_path.glob('*.csv')):
                file_groups['D1'].append({
                    'symbol': symbol,
                    'path': csv_file,
                    'timeframe': 'D1'
                })
        
        # 扫描M1文件
        m1_path = symbol_path / 'M1'
        if m1_path.exists():
            for year_folder in sorted(m1_path.iterdir()):
                if year_folder.is_dir():
                    for csv_file in sorted(year_folder.glob('*.csv')):
                        file_groups['M1'].append({
                            'symbol': symbol,
                            'path': csv_file,
                            'timeframe': 'M1'
                        })
    
    return file_groups

def import_files(importer, files, timeframe):
    """导入一组文件"""
    total_files = len(files)
    success_count = 0
    skip_count = 0
    error_count = 0
    total_inserted = 0
    total_skipped = 0
    
    # 详细的文件导入记录（用于生成报告）
    file_details = []
    
    print(f"📁 发现 {total_files} 个{timeframe}文件待导入\n")
    
    start_time = time.time()
    
    for idx, file_info in enumerate(files, 1):
        symbol = file_info['symbol']
        csv_path = file_info['path']
        
        # 显示进度
        progress_bar = "█" * (idx * 40 // total_files)
        progress_bar += "░" * (40 - len(progress_bar))
        percent = (idx * 100) // total_files
        
        print(f"[{idx}/{total_files}] [{progress_bar}] {percent}%")
        print(f"  📄 文件: {symbol}/{csv_path.parent.name}/{csv_path.name}")
        
        file_record = {
            'symbol': symbol,
            'timeframe': timeframe,
            'file_path': str(csv_path),
            'file_name': csv_path.name,
            'status': 'unknown',
            'inserted': 0,
            'skipped': 0,
            'error': None
        }
        
        try:
            # 记录导入前的统计
            old_inserted = importer.stats['inserted_rows']
            old_skipped = importer.stats['skipped_rows']
            
            # 导入文件（使用快速模式：只检查首尾记录）
            importer.import_csv_file(str(csv_path), symbol, timeframe, check_mode='fast')
            
            # 计算本次导入的增量
            inserted = importer.stats['inserted_rows'] - old_inserted
            skipped = importer.stats['skipped_rows'] - old_skipped
            
            file_record['inserted'] = inserted
            file_record['skipped'] = skipped
            
            if inserted > 0:
                success_count += 1
                total_inserted += inserted
                file_record['status'] = 'inserted'
                print(f"  ✅ 成功插入 {inserted:,} 条新记录")
            
            if skipped > 0:
                skip_count += 1
                total_skipped += skipped
                if inserted == 0:
                    file_record['status'] = 'skipped'
                print(f"  ⏭️  跳过 {skipped:,} 条已存在的数据")
            
            if inserted == 0 and skipped == 0:
                file_record['status'] = 'empty'
                print(f"  ℹ️  文件为空或无有效数据")
            
        except Exception as e:
            error_count += 1
            file_record['status'] = 'error'
            file_record['error'] = str(e)
            print(f"  ❌ 导入失败: {str(e)}")
        
        file_details.append(file_record)
        
        # 每10个文件显示一次统计
        if idx % 10 == 0 or idx == total_files:
            elapsed = time.time() - start_time
            avg_time = elapsed / idx
            remaining = avg_time * (total_files - idx)
            
            print(f"\n  ⏱️  进度统计:")
            print(f"     已处理: {idx}/{total_files} 文件")
            print(f"     成功: {success_count} | 跳过: {skip_count} | 错误: {error_count}")
            print(f"     新插入: {total_inserted:,} 条 | 已跳过: {total_skipped:,} 条")
            print(f"     已用时: {elapsed:.1f}秒 | 预计剩余: {remaining:.1f}秒")
            print()
    
    return {
        'total_files': total_files,
        'success_count': success_count,
        'skip_count': skip_count,
        'error_count': error_count,
        'total_inserted': total_inserted,
        'total_skipped': total_skipped,
        'elapsed_time': time.time() - start_time,
        'file_details': file_details
    }

def print_summary(d1_result, m1_result):
    """打印总结报告"""
    print("\n" + "="*80)
    print("           📊 导入完成 - 总结报告")
    print("="*80 + "\n")
    
    print("【D1日线数据】")
    print("-"*80)
    print(f"  文件总数:   {d1_result['total_files']:,}")
    print(f"  成功导入:   {d1_result['success_count']:,}")
    print(f"  跳过(已存在): {d1_result['skip_count']:,}")
    print(f"  失败:       {d1_result['error_count']:,}")
    print(f"  新增记录:   {d1_result['total_inserted']:,} 条")
    print(f"  跳过记录:   {d1_result['total_skipped']:,} 条")
    print(f"  耗时:       {d1_result['elapsed_time']:.2f} 秒")
    
    print("\n【M1分钟线数据】")
    print("-"*80)
    print(f"  文件总数:   {m1_result['total_files']:,}")
    print(f"  成功导入:   {m1_result['success_count']:,}")
    print(f"  跳过(已存在): {m1_result['skip_count']:,}")
    print(f"  失败:       {m1_result['error_count']:,}")
    print(f"  新增记录:   {m1_result['total_inserted']:,} 条")
    print(f"  跳过记录:   {m1_result['total_skipped']:,} 条")
    print(f"  耗时:       {m1_result['elapsed_time']:.2f} 秒")
    
    print("\n【总计】")
    print("-"*80)
    total_files = d1_result['total_files'] + m1_result['total_files']
    total_inserted = d1_result['total_inserted'] + m1_result['total_inserted']
    total_skipped = d1_result['total_skipped'] + m1_result['total_skipped']
    total_time = d1_result['elapsed_time'] + m1_result['elapsed_time']
    
    print(f"  文件总数:   {total_files:,}")
    print(f"  新增记录:   {total_inserted:,} 条")
    print(f"  跳过记录:   {total_skipped:,} 条")
    print(f"  总耗时:     {total_time:.2f} 秒 ({total_time/60:.1f} 分钟)")
    
    if total_inserted > 0:
        print(f"  导入速度:   {total_inserted/total_time:.0f} 条/秒")
    
    print("\n" + "="*80)
    
    if d1_result['error_count'] + m1_result['error_count'] == 0:
        print("           ✅ 所有数据导入成功！")
    else:
        print(f"           ⚠️  有 {d1_result['error_count'] + m1_result['error_count']} 个文件导入失败")
    
    print("="*80 + "\n")
    
    print("💡 提示:")
    print("  • 物化视图会自动生成M5/M15/M30/H1聚合数据")
    print("  • 运行 'python scripts\\view_clickhouse_tables.py' 查看数据库状态")
    print("  • 运行 'python scripts\\verify_data_consistency.py' 验证数据一致性")
    print()
    
    # 生成HTML报告
    try:
        report_file = generate_html_report(d1_result, m1_result)
        print(f"📄 HTML报告已生成: {report_file.absolute()}")
        print(f"   在浏览器中打开查看详细报告\n")
    except Exception as e:
        print(f"⚠️  HTML报告生成失败: {str(e)}\n")

def main():
    """主函数"""
    try:
        # 检查命令行参数
        skip_confirm = '--yes' in sys.argv or '-y' in sys.argv
        
        print_banner()
        
        # 读取配置
        print("📋 读取配置文件...")
        with open('config/clickhouse_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"   ✅ 连接到 {config['host']}:{config['http_port']}\n")
        
        # 扫描文件
        print("🔍 扫描数据文件...")
        file_groups = scan_data_files()
        
        if file_groups is None:
            return
        
        d1_files = file_groups['D1']
        m1_files = file_groups['M1']
        
        print(f"   ✅ 发现 {len(d1_files)} 个D1文件")
        print(f"   ✅ 发现 {len(m1_files)} 个M1文件")
        
        total_files = len(d1_files) + len(m1_files)
        print(f"\n   📊 总计: {total_files} 个文件待导入\n")
        
        if total_files == 0:
            print("❌ 没有找到任何数据文件！")
            return
        
        # 确认导入
        if not skip_confirm:
            print("⚠️  准备开始导入，这可能需要较长时间...")
            response = input("   是否继续？(y/n): ").strip().lower()
            
            if response != 'y':
                print("\n❌ 用户取消导入\n")
                return
        else:
            print("⚠️  自动模式：跳过确认，开始导入...\n")
        
        # 创建导入器
        importer = FXCMDataImporter('config/clickhouse_config.json')
        
        # 导入D1数据
        print_section("📈 第1步：导入D1日线数据")
        d1_result = import_files(importer, d1_files, 'D1')
        
        # 导入M1数据
        print_section("📊 第2步：导入M1分钟线数据")
        m1_result = import_files(importer, m1_files, 'M1')
        
        # 打印总结
        print_summary(d1_result, m1_result)
        
        # 保存日志
        log_file = f"import_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"导入完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"D1文件: {d1_result['total_files']}, 新增: {d1_result['total_inserted']}\n")
            f.write(f"M1文件: {m1_result['total_files']}, 新增: {m1_result['total_inserted']}\n")
        
        print(f"📝 导入日志已保存到: {log_file}\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断导入\n")
    except Exception as e:
        print(f"\n❌ 导入过程出错: {str(e)}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
