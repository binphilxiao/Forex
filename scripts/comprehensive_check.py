#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
严格校验导入工具 - 对指定文件进行详细的数据完整性检查

使用场景：
1. 怀疑某个文件数据不完整时
2. 需要精确验证某个时间段的数据时
3. 修复数据问题后需要重新导入时

模式：comprehensive - 检查CSV中的每一条记录是否都存在于数据库
"""

import sys
import os
import codecs
from pathlib import Path
from datetime import datetime

# 配置UTF-8输出
if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 添加scripts目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))
from import_fxcm_to_clickhouse import FXCMDataImporter


def print_section(title):
    """打印分节标题"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def scan_data_files():
    """扫描所有可用的数据文件"""
    data_files = {
        'M1': {},  # {货币对: {年份: [文件列表]}}
        'D1': {}   # {货币对: [文件列表]}
    }
    
    base_path = Path('fxcm_data')
    if not base_path.exists():
        print("❌ 错误: fxcm_data 目录不存在")
        return data_files
    
    # 扫描所有货币对
    for symbol_dir in base_path.iterdir():
        if not symbol_dir.is_dir():
            continue
        
        symbol = symbol_dir.name
        
        # 扫描D1数据
        d1_dir = symbol_dir / 'D1'
        if d1_dir.exists():
            d1_files = sorted(d1_dir.glob('*.csv'))
            if d1_files:
                data_files['D1'][symbol] = d1_files
        
        # 扫描M1数据
        m1_dir = symbol_dir / 'M1'
        if m1_dir.exists():
            year_files = {}
            for year_dir in sorted(m1_dir.iterdir()):
                if year_dir.is_dir():
                    year = year_dir.name
                    week_files = sorted(year_dir.glob('week_*.csv'))
                    if week_files:
                        year_files[year] = week_files
            if year_files:
                data_files['M1'][symbol] = year_files
    
    return data_files


def print_file_tree(data_files):
    """打印文件树"""
    print("\n📁 可用数据文件：\n")
    
    # D1数据
    if data_files['D1']:
        print("📊 D1日线数据：")
        for symbol, files in sorted(data_files['D1'].items()):
            print(f"  • {symbol}: {len(files)} 个文件")
        print()
    
    # M1数据
    if data_files['M1']:
        print("📈 M1分钟线数据：")
        for symbol, years in sorted(data_files['M1'].items()):
            total_weeks = sum(len(files) for files in years.values())
            print(f"  • {symbol}: {len(years)} 年份, 共 {total_weeks} 个周文件")
            for year, files in sorted(years.items()):
                print(f"    ├─ {year}: {len(files)} 周")
        print()


def select_file_for_check(data_files):
    """交互式选择要检查的文件"""
    
    # 1. 选择时间周期
    print_section("步骤 1: 选择时间周期")
    print("1. D1 日线数据")
    print("2. M1 分钟线数据")
    
    while True:
        choice = input("\n请选择 [1-2]: ").strip()
        if choice == '1':
            timeframe = 'D1'
            break
        elif choice == '2':
            timeframe = 'M1'
            break
        else:
            print("❌ 无效选择，请重新输入")
    
    # 2. 选择货币对
    print_section("步骤 2: 选择货币对")
    symbols = sorted(data_files[timeframe].keys())
    
    for i, symbol in enumerate(symbols, 1):
        if timeframe == 'D1':
            file_count = len(data_files[timeframe][symbol])
            print(f"{i}. {symbol} ({file_count} 个文件)")
        else:
            years = data_files[timeframe][symbol]
            week_count = sum(len(files) for files in years.values())
            print(f"{i}. {symbol} ({len(years)} 年份, {week_count} 周)")
    
    while True:
        choice = input(f"\n请选择 [1-{len(symbols)}]: ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(symbols):
                symbol = symbols[idx]
                break
        except ValueError:
            pass
        print("❌ 无效选择，请重新输入")
    
    # 3. 选择具体文件
    if timeframe == 'D1':
        print_section("步骤 3: 选择年份文件")
        files = data_files['D1'][symbol]
        
        for i, file_path in enumerate(files, 1):
            print(f"{i}. {file_path.name}")
        
        while True:
            choice = input(f"\n请选择 [1-{len(files)}] 或 [all] 全部: ").strip().lower()
            if choice == 'all':
                selected_files = files
                break
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(files):
                    selected_files = [files[idx]]
                    break
            except ValueError:
                pass
            print("❌ 无效选择，请重新输入")
    
    else:  # M1
        # 3a. 选择年份
        print_section("步骤 3: 选择年份")
        years = sorted(data_files['M1'][symbol].keys())
        
        for i, year in enumerate(years, 1):
            week_count = len(data_files['M1'][symbol][year])
            print(f"{i}. {year} ({week_count} 周)")
        
        while True:
            choice = input(f"\n请选择 [1-{len(years)}]: ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(years):
                    year = years[idx]
                    break
            except ValueError:
                pass
            print("❌ 无效选择，请重新输入")
        
        # 3b. 选择周文件
        print_section("步骤 4: 选择周文件")
        week_files = data_files['M1'][symbol][year]
        
        print(f"\n{year} 年共有 {len(week_files)} 个周文件")
        print("\n可以选择：")
        print("  • 单个周: 输入周数 (1-52)")
        print("  • 多个周: 输入周数范围，如 1-10")
        print("  • 全部周: 输入 all")
        
        while True:
            choice = input(f"\n请选择: ").strip().lower()
            
            if choice == 'all':
                selected_files = week_files
                break
            elif '-' in choice:
                try:
                    start, end = choice.split('-')
                    start_week = int(start)
                    end_week = int(end)
                    selected_files = [f for f in week_files 
                                     if start_week <= int(f.stem.split('_')[1]) <= end_week]
                    if selected_files:
                        break
                except ValueError:
                    pass
            else:
                try:
                    week_num = int(choice)
                    selected_files = [f for f in week_files 
                                     if int(f.stem.split('_')[1]) == week_num]
                    if selected_files:
                        break
                except ValueError:
                    pass
            
            print("❌ 无效选择，请重新输入")
    
    return {
        'symbol': symbol,
        'timeframe': timeframe,
        'files': selected_files
    }


def comprehensive_check_and_import(importer, selection):
    """使用详细模式检查并导入文件"""
    symbol = selection['symbol']
    timeframe = selection['timeframe']
    files = selection['files']
    
    print_section(f"🔍 严格校验模式 - {symbol} {timeframe}")
    print(f"\n将检查 {len(files)} 个文件的每一条记录")
    print("⚠️  这可能需要较长时间...\n")
    
    # 确认
    confirm = input("确认继续？[y/N]: ").strip().lower()
    if confirm != 'y':
        print("\n❌ 已取消")
        return
    
    # 开始处理
    print(f"\n{'='*80}")
    print("开始处理...\n")
    
    success_count = 0
    skip_count = 0
    error_count = 0
    total_inserted = 0
    total_skipped = 0
    
    for idx, file_path in enumerate(files, 1):
        print(f"[{idx}/{len(files)}] 📄 {file_path.name}")
        
        try:
            # 记录前的统计
            old_inserted = importer.stats['inserted_rows']
            old_skipped = importer.stats['skipped_rows']
            
            # 使用详细检查模式
            importer.import_csv_file(
                str(file_path), 
                symbol, 
                timeframe, 
                check_mode='comprehensive'  # 强制使用详细模式
            )
            
            # 计算本次增量
            inserted = importer.stats['inserted_rows'] - old_inserted
            skipped = importer.stats['skipped_rows'] - old_skipped
            
            if inserted > 0:
                success_count += 1
                total_inserted += inserted
            
            if skipped > 0:
                skip_count += 1
                total_skipped += skipped
            
        except Exception as e:
            error_count += 1
            print(f"  ❌ 错误: {str(e)}")
    
    # 打印总结
    print(f"\n{'='*80}")
    print("📊 检查完成 - 统计报告")
    print(f"{'='*80}\n")
    
    print(f"文件总数:     {len(files)}")
    print(f"成功导入:     {success_count}")
    print(f"完全跳过:     {skip_count}")
    print(f"错误:         {error_count}")
    print(f"\n新增记录:     {total_inserted:,} 条")
    print(f"跳过记录:     {total_skipped:,} 条")
    
    # 保存日志
    log_file = f"comprehensive_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"严格校验报告\n")
        f.write(f"{'='*80}\n")
        f.write(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"货币对: {symbol}\n")
        f.write(f"时间周期: {timeframe}\n")
        f.write(f"文件数量: {len(files)}\n")
        f.write(f"\n统计:\n")
        f.write(f"  新增记录: {total_inserted:,} 条\n")
        f.write(f"  跳过记录: {total_skipped:,} 条\n")
        f.write(f"  成功: {success_count}, 跳过: {skip_count}, 错误: {error_count}\n")
    
    print(f"\n📝 详细日志已保存到: {log_file}")


def main():
    """主函数"""
    print_section("🔍 严格校验导入工具")
    print("\n本工具使用 comprehensive 模式检查数据完整性")
    print("会逐条验证CSV文件中的每一条记录是否存在于数据库")
    
    # 扫描文件
    print("\n正在扫描数据文件...")
    data_files = scan_data_files()
    
    if not data_files['D1'] and not data_files['M1']:
        print("\n❌ 未找到任何数据文件")
        return
    
    # 显示文件树
    print_file_tree(data_files)
    
    # 选择要检查的文件
    selection = select_file_for_check(data_files)
    
    # 创建导入器
    importer = FXCMDataImporter('config/clickhouse_config.json')
    
    # 执行严格检查
    comprehensive_check_and_import(importer, selection)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断检查\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 错误: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
