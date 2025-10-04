#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FXCM 数据完整性检查器
====================

这个脚本用于检查已下载的FXCM历史数据的完整性，生成可视化报告。

功能特点:
- 扫描所有货币对的M1、M5、M15、M30、H1和D1数据
- 检查缺失的周/年数据
- 统计文件大小和记录数量
- 生成HTML可视化报告
- 提供数据质量分析
- 支持多时间周期数据检查

作者: AI Assistant
创建时间: 2025-10-03
版本: 1.0.2
"""

import sys
import io
import pandas as pd
from pathlib import Path
import json
from datetime import datetime, timedelta
import logging
from collections import defaultdict
import os

# 设置标准输出编码为UTF-8，避免Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class FXCMDataChecker:
    """FXCM数据完整性检查器"""
    
    def __init__(self):
        """初始化检查器"""
        self.base_path = Path(__file__).parent.parent / 'fxcm_data'
        self.instruments = ['EURUSD', 'USDCAD', 'GBPUSD', 'USDCHF', 'AUDUSD', 'USDJPY']
        self.timeframes = ['M1', 'M5', 'M15', 'M30', 'H1', 'D1']
        self.weekly_timeframes = ['M1', 'M5', 'M15', 'M30', 'H1']  # 按周存储的时间周期
        self.yearly_timeframes = ['D1']  # 按年存储的时间周期
        self.start_year = 2015
        self.end_year = 2025
        
        # 创建日志
        self.setup_logging()
        
        # 数据统计
        self.stats = {
            'total_files_expected': 0,
            'total_files_found': 0,
            'total_files_missing': 0,
            'total_records': 0,
            'total_size_mb': 0.0,
            'by_instrument': {},
            'by_timeframe': {},
            'missing_data': []
        }
        
    def setup_logging(self):
        """设置日志系统"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'data_check_{timestamp}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"数据检查开始 - 日志文件: {log_file}")
        
    def check_weekly_data(self, instrument, timeframe, year):
        """检查按周存储的时间周期数据完整性（M1, M5, M15, M30, H1）"""
        year_path = self.base_path / instrument / timeframe / str(year)
        
        found_weeks = []
        missing_weeks = []
        file_stats = []
        
        # 检查每周的数据 (1-52周)
        for week in range(1, 53):
            week_file = year_path / f'week_{week:02d}.csv'
            
            if week_file.exists():
                try:
                    # 读取文件统计信息
                    file_size = week_file.stat().st_size
                    
                    # 快速读取行数（不加载全部数据）
                    with open(week_file, 'r', encoding='utf-8') as f:
                        row_count = sum(1 for line in f) - 1  # 减去标题行
                    
                    found_weeks.append(week)
                    file_stats.append({
                        'week': week,
                        'size_bytes': file_size,
                        'size_mb': file_size / (1024 * 1024),
                        'records': row_count,
                        'file_path': str(week_file)
                    })
                    
                except Exception as e:
                    self.logger.warning(f"读取文件错误 {week_file}: {e}")
                    missing_weeks.append(week)
            else:
                missing_weeks.append(week)
        
        return {
            'found_weeks': found_weeks,
            'missing_weeks': missing_weeks,
            'file_stats': file_stats,
            'total_files': len(found_weeks),
            'missing_files': len(missing_weeks),
            'completeness_rate': len(found_weeks) / 52 * 100
        }
    
    def check_yearly_data(self, instrument, timeframe):
        """检查按年存储的时间周期数据完整性（D1）"""
        timeframe_path = self.base_path / instrument / timeframe
        
        found_years = []
        missing_years = []
        file_stats = []
        
        # 检查每年的数据
        for year in range(self.start_year, self.end_year + 1):
            year_file = timeframe_path / f'{year}.csv'
            
            if year_file.exists():
                try:
                    # 读取文件统计信息
                    file_size = year_file.stat().st_size
                    
                    # 快速读取行数
                    with open(year_file, 'r', encoding='utf-8') as f:
                        row_count = sum(1 for line in f) - 1  # 减去标题行
                    
                    found_years.append(year)
                    file_stats.append({
                        'year': year,
                        'size_bytes': file_size,
                        'size_mb': file_size / (1024 * 1024),
                        'records': row_count,
                        'file_path': str(year_file)
                    })
                    
                except Exception as e:
                    self.logger.warning(f"读取文件错误 {year_file}: {e}")
                    missing_years.append(year)
            else:
                missing_years.append(year)
        
        expected_years = list(range(self.start_year, self.end_year + 1))
        
        return {
            'found_years': found_years,
            'missing_years': missing_years,
            'file_stats': file_stats,
            'total_files': len(found_years),
            'missing_files': len(missing_years),
            'completeness_rate': len(found_years) / len(expected_years) * 100
        }
    
    def analyze_data_completeness(self):
        """分析所有数据的完整性"""
        self.logger.info("开始分析数据完整性...")
        
        for instrument in self.instruments:
            self.logger.info(f"检查货币对: {instrument}")
            
            # 为每个时间周期初始化统计数据
            instrument_stats = {
                'total_size_mb': 0.0,
                'total_records': 0,
                'total_files': 0,
                'missing_files': 0
            }
            
            # 为每个时间周期初始化数据结构
            for timeframe in self.timeframes:
                instrument_stats[timeframe] = {}
            
            # 检查按周存储的时间周期数据
            for timeframe in self.weekly_timeframes:
                self.logger.info(f"  检查 {timeframe} 数据...")
                
                timeframe_path = self.base_path / instrument / timeframe
                if not timeframe_path.exists():
                    self.logger.warning(f"  ⚠️ {timeframe} 目录不存在: {timeframe_path}")
                    continue
                
                for year in range(self.start_year, self.end_year + 1):
                    timeframe_result = self.check_weekly_data(instrument, timeframe, year)
                    instrument_stats[timeframe][year] = timeframe_result
                    
                    # 累计统计
                    for file_stat in timeframe_result['file_stats']:
                        instrument_stats['total_size_mb'] += file_stat['size_mb']
                        instrument_stats['total_records'] += file_stat['records']
                        instrument_stats['total_files'] += 1
                    
                    instrument_stats['missing_files'] += timeframe_result['missing_files']
                    
                    # 记录缺失数据
                    for missing_week in timeframe_result['missing_weeks']:
                        self.stats['missing_data'].append({
                            'instrument': instrument,
                            'timeframe': timeframe,
                            'year': year,
                            'week': missing_week,
                            'file_path': f"fxcm_data/{instrument}/{timeframe}/{year}/week_{missing_week:02d}.csv"
                        })
            
            # 检查按年存储的时间周期数据
            for timeframe in self.yearly_timeframes:
                self.logger.info(f"  检查 {timeframe} 数据...")
                
                timeframe_path = self.base_path / instrument / timeframe
                if not timeframe_path.exists():
                    self.logger.warning(f"  ⚠️ {timeframe} 目录不存在: {timeframe_path}")
                    continue
                
                timeframe_result = self.check_yearly_data(instrument, timeframe)
                instrument_stats[timeframe] = timeframe_result
                
                # 累计统计
                for file_stat in timeframe_result['file_stats']:
                    instrument_stats['total_size_mb'] += file_stat['size_mb']
                    instrument_stats['total_records'] += file_stat['records']
                    instrument_stats['total_files'] += 1
                
                instrument_stats['missing_files'] += timeframe_result['missing_files']
                
                # 记录缺失数据
                for missing_year in timeframe_result['missing_years']:
                    self.stats['missing_data'].append({
                        'instrument': instrument,
                        'timeframe': timeframe,
                        'year': missing_year,
                        'week': None,
                        'file_path': f"fxcm_data/{instrument}/{timeframe}/{missing_year}.csv"
                    })
            
            # 保存到总统计
            self.stats['by_instrument'][instrument] = instrument_stats
            self.stats['total_records'] += instrument_stats['total_records']
            self.stats['total_size_mb'] += instrument_stats['total_size_mb']
            self.stats['total_files_found'] += instrument_stats['total_files']
            self.stats['total_files_missing'] += instrument_stats['missing_files']
            
            self.logger.info(f"  ✅ {instrument}: {instrument_stats['total_files']} 文件, "
                           f"{instrument_stats['total_records']:,} 记录, "
                           f"{instrument_stats['total_size_mb']:.1f} MB")
        
        # 计算总期望文件数
        # 按周存储的时间周期: M1, M5, M15, M30, H1 = 5 × 6 instruments × 11 years × 52 weeks = 17160 files
        # 按年存储的时间周期: D1 = 1 × 6 instruments × 11 years = 66 files  
        # Total: 17226 files
        weekly_files = len(self.weekly_timeframes) * 6 * 11 * 52
        yearly_files = len(self.yearly_timeframes) * 6 * 11
        self.stats['total_files_expected'] = weekly_files + yearly_files
        
        self.logger.info(f"总计: {self.stats['total_files_found']}/{self.stats['total_files_expected']} 文件")
        self.logger.info(f"缺失: {self.stats['total_files_missing']} 文件")
        self.logger.info(f"总记录数: {self.stats['total_records']:,}")
        self.logger.info(f"总大小: {self.stats['total_size_mb']:.1f} MB")
    
    def generate_html_report(self):
        """生成HTML可视化报告"""
        self.logger.info("生成HTML报告...")
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FXCM 数据完整性报告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid;
        }}
        .stat-card.success {{ border-left-color: #28a745; }}
        .stat-card.warning {{ border-left-color: #ffc107; }}
        .stat-card.info {{ border-left-color: #17a2b8; }}
        .stat-card.danger {{ border-left-color: #dc3545; }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 0;
        }}
        .stat-label {{
            color: #6c757d;
            margin: 5px 0 0;
            font-size: 0.9em;
        }}
        .section {{
            margin: 30px;
        }}
        .section h2 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 500;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #dee2e6;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #e9ecef;
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 5px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }}
        .completeness-high {{ color: #28a745; font-weight: bold; }}
        .completeness-medium {{ color: #ffc107; font-weight: bold; }}
        .completeness-low {{ color: #dc3545; font-weight: bold; }}
        .missing-item {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 5px;
            padding: 8px;
            margin: 5px 0;
            font-family: monospace;
            font-size: 0.9em;
        }}
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 FXCM 多时间周期数据完整性报告</h1>
            <p>生成时间: {timestamp}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card success">
                <div class="stat-number">{self.stats['total_files_found']}</div>
                <div class="stat-label">已下载文件</div>
            </div>
            <div class="stat-card danger">
                <div class="stat-number">{self.stats['total_files_missing']}</div>
                <div class="stat-label">缺失文件</div>
            </div>
            <div class="stat-card info">
                <div class="stat-number">{self.stats['total_records']:,}</div>
                <div class="stat-label">总记录数</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-number">{self.stats['total_size_mb']:.1f}</div>
                <div class="stat-label">总大小 (MB)</div>
            </div>
        </div>
"""
        
        # 按货币对统计表格
        html_content += """
        <div class="section">
            <h2>📈 按货币对统计</h2>
            <table>
                <thead>
                    <tr>
                        <th>货币对</th>
                        <th>已下载文件</th>
                        <th>缺失文件</th>
                        <th>完整率</th>
                        <th>总记录数</th>
                        <th>总大小 (MB)</th>
                        <th>完整度</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for instrument, data in self.stats['by_instrument'].items():
            # 计算该货币对的期望文件数：5个按周时间周期 + 1个按年时间周期
            weekly_expected = len(self.weekly_timeframes) * 11 * 52  # 按周时间周期
            yearly_expected = len(self.yearly_timeframes) * 11        # 按年时间周期
            total_expected = weekly_expected + yearly_expected
            completeness = (data['total_files'] / total_expected) * 100
            
            completeness_class = 'completeness-high'
            if completeness < 90:
                completeness_class = 'completeness-medium'
            if completeness < 70:
                completeness_class = 'completeness-low'
            
            html_content += f"""
                    <tr>
                        <td><strong>{instrument}</strong></td>
                        <td>{data['total_files']}</td>
                        <td>{data['missing_files']}</td>
                        <td class="{completeness_class}">{completeness:.1f}%</td>
                        <td>{data['total_records']:,}</td>
                        <td>{data['total_size_mb']:.1f}</td>
                        <td>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {completeness}%"></div>
                            </div>
                        </td>
                    </tr>
"""
        
        html_content += """
                </tbody>
            </table>
        </div>
"""
        
        # 按周时间周期数据完整性热力图
        html_content += """
        <div class="section">
            <h2>📅 按周时间周期数据完整性矩阵 (按年/周)</h2>
            <p>绿色表示数据存在，红色表示数据缺失</p>
"""
        
        for instrument in self.instruments:
            for timeframe in self.weekly_timeframes:
                html_content += f"""
            <h3>{instrument} - {timeframe}数据</h3>
            <table style="font-size: 0.8em;">
                <thead>
                    <tr>
                        <th>年份</th>
"""
                
                # 表头：周数
                for week in range(1, 53):
                    html_content += f'<th style="width: 20px; text-align: center;">{week}</th>'
                
                html_content += """
                    </tr>
                </thead>
                <tbody>
"""
                
                # 每年的数据
                for year in range(self.start_year, self.end_year + 1):
                    html_content += f'<tr><td><strong>{year}</strong></td>'
                    
                    timeframe_data = self.stats['by_instrument'][instrument].get(timeframe, {}).get(year, {})
                    found_weeks = timeframe_data.get('found_weeks', [])
                    
                    for week in range(1, 53):
                        color = '#28a745' if week in found_weeks else '#dc3545'
                        title = f'{instrument} {timeframe} {year} Week {week}: {"✓" if week in found_weeks else "✗"}'
                        html_content += f'<td style="background-color: {color}; color: white; text-align: center; cursor: help;" title="{title}">{"✓" if week in found_weeks else "✗"}</td>'
                    
                    html_content += '</tr>'
                
                html_content += '</tbody></table><br>'
        
        html_content += '</div>'
        
        # 缺失数据列表
        if self.stats['missing_data']:
            html_content += """
        <div class="section">
            <h2>❌ 缺失数据详细列表</h2>
"""
            
            # 按货币对分组显示缺失数据
            missing_by_instrument = defaultdict(list)
            for item in self.stats['missing_data']:
                missing_by_instrument[item['instrument']].append(item)
            
            for instrument, missing_items in missing_by_instrument.items():
                html_content += f'<h3>{instrument}</h3>'
                
                # 按时间周期分组显示缺失数据
                for timeframe in self.timeframes:
                    tf_missing = [item for item in missing_items if item['timeframe'] == timeframe]
                    
                    if tf_missing:
                        html_content += f'<h4>{timeframe} 数据缺失 ({len(tf_missing)} 个文件)</h4>'
                        display_limit = 20 if timeframe in self.weekly_timeframes else len(tf_missing)
                        
                        for item in tf_missing[:display_limit]:
                            html_content += f'<div class="missing-item">{item["file_path"]}</div>'
                        
                        if len(tf_missing) > display_limit:
                            html_content += f'<p>... 还有 {len(tf_missing) - display_limit} 个缺失文件</p>'
        
        html_content += '</div>'
        
        # 结尾
        html_content += f"""
        <div class="footer">
            <p>FXCM 数据完整性检查器 v2.0.0 | 生成时间: {timestamp}</p>
            <p>数据路径: {self.base_path.absolute()}</p>
        </div>
    </div>
</body>
</html>
"""
        
        # 保存HTML文件到logs目录
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = Path(__file__).parent.parent / 'logs' / f'fxcm_data_report_{timestamp}.html'
        report_file.parent.mkdir(exist_ok=True)  # 确保logs目录存在
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML报告已生成: {report_file.absolute()}")
        return report_file
    
    def generate_json_report(self):
        """生成JSON格式的详细报告"""
        report_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'script_version': '2.0.0',
                'data_path': str(self.base_path.absolute()),
                'instruments': self.instruments,
                'timeframes': self.timeframes,
                'year_range': f'{self.start_year}-{self.end_year}'
            },
            'summary': self.stats,
            'detailed_analysis': self.stats['by_instrument']
        }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = Path(__file__).parent.parent / 'logs' / f'fxcm_data_report_{timestamp}.json'
        json_file.parent.mkdir(exist_ok=True)  # 确保logs目录存在
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"JSON报告已生成: {json_file.absolute()}")
        return json_file
    
    def run_analysis(self):
        """运行完整的数据分析"""
        start_time = datetime.now()
        
        # 检查数据目录是否存在
        if not self.base_path.exists():
            self.logger.error(f"数据目录不存在: {self.base_path.absolute()}")
            print(f"❌ 错误: 数据目录不存在 - {self.base_path.absolute()}")
            print("请先运行 download_fxcm_candles.py 下载数据")
            return
        
        print("🔍 开始检查FXCM数据完整性...")
        print(f"📁 数据目录: {self.base_path.absolute()}")
        print(f"💱 货币对: {', '.join(self.instruments)}")
        print(f"📊 时间周期: {', '.join(self.timeframes)}")
        print(f"📅 年份范围: {self.start_year}-{self.end_year}")
        print()
        
        try:
            # 分析数据完整性
            self.analyze_data_completeness()
            
            # 生成报告
            html_file = self.generate_html_report()
            json_file = self.generate_json_report()
            
            # 显示总结
            end_time = datetime.now()
            duration = end_time - start_time
            
            print()
            print("="*60)
            print("📋 数据完整性检查完成!")
            print("="*60)
            print(f"📊 总文件数: {self.stats['total_files_found']:,} / {self.stats['total_files_expected']:,}")
            print(f"❌ 缺失文件: {self.stats['total_files_missing']:,}")
            print(f"📈 完整率: {(self.stats['total_files_found']/self.stats['total_files_expected']*100):.1f}%")
            print(f"📝 总记录数: {self.stats['total_records']:,}")
            print(f"💾 总大小: {self.stats['total_size_mb']:.1f} MB")
            print(f"⏱️  检查耗时: {duration.total_seconds():.1f} 秒")
            print()
            print("📄 报告文件:")
            print(f"  🌐 HTML报告: {html_file.absolute()}")
            print(f"  📋 JSON报告: {json_file.absolute()}")
            print()
            print("💡 提示: 打开HTML报告文件查看详细的可视化分析")
            
            # 返回HTML文件路径
            return str(html_file.absolute())
            
        except Exception as e:
            self.logger.error(f"分析过程中出现错误: {e}")
            print(f"❌ 错误: {e}")
            return None

def main():
    """主函数"""
    print("FXCM 数据完整性检查器 v2.0.0")
    print("="*40)
    
    checker = FXCMDataChecker()
    report_path = checker.run_analysis()
    
    # 注意：不在这里打开报告，由调用方（如Flask）决定是否打开
    # 这样可以避免在Web界面调用时重复打开两次

if __name__ == '__main__':
    main()