#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FXCM M1 多时间周期数据转换器
===========================

这个脚本用于将FXCM的1分钟(M1)数据聚合生成多个时间周期的数据：
- M5 (5分钟)
- M15 (15分钟) 
- M30 (30分钟)
- H1 (60分钟/1小时)

功能特点:
- 读取M1数据并按不同时间窗口聚合
- 保持与原始数据相同的CSV格式
- 支持多个货币对的批量转换
- 生成详细的转换日志和统计报告
- 智能跳过已存在的文件
- 严格的数据验证和错误处理

聚合规则:
- Open: 时间窗口内第一个M1记录的开盘价
- High: 时间窗口内所有M1记录的最高价
- Low: 时间窗口内所有M1记录的最低价
- Close: 时间窗口内最后一个M1记录的收盘价

作者: AI Assistant
创建时间: 2025-10-03
版本: 1.0.2
"""

import sys
import io
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
import json

# 设置标准输出编码为UTF-8，避免Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class FXCMMultiTimeframeConverter:
    """FXCM M1多时间周期数据转换器"""
    
    def __init__(self):
        """初始化转换器"""
        self.base_path = Path(__file__).parent.parent / 'fxcm_data'
        self.instruments = ['EURUSD', 'USDCAD', 'GBPUSD', 'USDCHF', 'AUDUSD', 'USDJPY']
        self.start_year = 2015
        self.end_year = 2025
        
        # 支持的时间周期配置
        self.timeframes = {
            'M5': {'minutes': 5, 'folder': 'M5'},
            'M15': {'minutes': 15, 'folder': 'M15'},
            'M30': {'minutes': 30, 'folder': 'M30'},
            'H1': {'minutes': 60, 'folder': 'H1'}
        }
        
        # 设置日志
        self.setup_logging()
        
        # 统计信息
        self.stats = {
            'total_processed_files': 0,
            'total_skipped_files': 0,
            'total_input_rows': 0,
            'total_output_rows': 0,
            'processing_errors': 0,
            'by_instrument': {},
            'processing_time': 0
        }
    
    def setup_logging(self):
        """设置日志系统"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'm1_to_multi_timeframes_{timestamp}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"M1多时间周期转换开始 - 日志文件: {log_file}")
    
    def parse_datetime(self, dt_str):
        """解析日期时间字符串"""
        try:
            # 尝试常见的日期时间格式
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%Y/%m/%d %H:%M'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(dt_str, fmt)
                except ValueError:
                    continue
            
            # 如果都失败了，尝试pandas的通用解析
            return pd.to_datetime(dt_str)
            
        except Exception as e:
            raise ValueError(f"无法解析日期时间: {dt_str}, 错误: {e}")
    
    def round_to_timeframe(self, dt, minutes):
        """将时间舍入到指定分钟间隔的边界"""
        if minutes == 60:
            # 对于H1，舍入到整点
            return dt.replace(minute=0, second=0, microsecond=0)
        else:
            # 对于其他时间周期，舍入到对应的分钟边界
            rounded_minute = (dt.minute // minutes) * minutes
            return dt.replace(minute=rounded_minute, second=0, microsecond=0)
    
    def aggregate_to_timeframe(self, df, timeframe_minutes):
        """将1分钟数据聚合为指定时间周期数据"""
        if df.empty:
            return df
        
        try:
            # 解析DateTime列
            df['DateTime_parsed'] = df['DateTime'].apply(self.parse_datetime)
            
            # 将时间舍入到指定时间周期边界
            df['DateTime_rounded'] = df['DateTime_parsed'].apply(
                lambda dt: self.round_to_timeframe(dt, timeframe_minutes)
            )
            
            # 按指定时间窗口分组聚合
            grouped = df.groupby('DateTime_rounded')
            
            aggregated_data = []
            
            for time_window, group in grouped:
                # 按时间排序确保正确的OHLC计算
                group = group.sort_values('DateTime_parsed')
                
                # 计算OHLC数据
                ohlc_data = {
                    'DateTime': time_window.strftime('%Y-%m-%d %H:%M:%S'),
                    'Open': group['Open'].iloc[0],      # 第一个记录的开盘价
                    'High': group['High'].max(),        # 最高价
                    'Low': group['Low'].min(),          # 最低价
                    'Close': group['Close'].iloc[-1]    # 最后一个记录的收盘价
                }
                
                aggregated_data.append(ohlc_data)
            
            # 创建新的DataFrame
            result_df = pd.DataFrame(aggregated_data)
            
            # 按时间排序
            result_df['DateTime_sort'] = pd.to_datetime(result_df['DateTime'])
            result_df = result_df.sort_values('DateTime_sort')
            result_df = result_df.drop('DateTime_sort', axis=1)
            
            return result_df
            
        except Exception as e:
            self.logger.error(f"数据聚合错误: {e}")
            raise
    
    def process_m1_file(self, m1_file_path, output_file_path, timeframe_name, timeframe_minutes):
        """处理单个M1文件，生成对应时间周期的文件"""
        try:
            # 检查输出文件是否已存在
            if output_file_path.exists():
                self.logger.info(f"  ⏭️ {timeframe_name}文件已存在，跳过: {output_file_path.name}")
                self.stats['total_skipped_files'] += 1
                return True
            
            # 读取M1数据
            df_m1 = pd.read_csv(m1_file_path)
            
            if df_m1.empty:
                self.logger.warning(f"  ⚠️ M1文件为空: {m1_file_path.name}")
                return False
            
            # 验证必需的OHLC列
            required_columns = ['DateTime', 'Open', 'High', 'Low', 'Close']
            missing_columns = [col for col in required_columns if col not in df_m1.columns]
            
            if missing_columns:
                self.logger.error(f"  ❌ M1文件缺少必需列 {missing_columns}: {m1_file_path.name}")
                return False
            
            # 转换为指定时间周期数据
            df_aggregated = self.aggregate_to_timeframe(df_m1, timeframe_minutes)
            initial_rows = len(df_m1)
            
            if df_aggregated.empty:
                self.logger.warning(f"  ⚠️ {timeframe_name}聚合数据为空: {m1_file_path.name}")
                return False
            
            # 确保输出目录存在
            output_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存聚合数据
            df_aggregated.to_csv(output_file_path, index=False)
            
            # 更新统计
            self.stats['total_processed_files'] += 1
            self.stats['total_input_rows'] += initial_rows
            self.stats['total_output_rows'] += len(df_aggregated)
            
            compression_ratio = initial_rows / len(df_aggregated) if len(df_aggregated) > 0 else 0
            
            self.logger.info(f"  ✅ 转换完成: {m1_file_path.name} -> {output_file_path.name}")
            self.logger.info(f"      📊 数据行数: {initial_rows:,} -> {len(df_aggregated):,} (压缩比: {compression_ratio:.1f}:1)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"  ❌ 处理文件失败 {m1_file_path.name}: {e}")
            self.stats['processing_errors'] += 1
            return False
    
    def process_year(self, instrument, year):
        """处理单个货币对的某一年数据，生成所有时间周期"""
        self.logger.info(f"\n🔄 处理 {instrument} {year}年数据...")
        
        # M1输入路径
        m1_year_dir = self.base_path / instrument / 'M1' / str(year)
        
        if not m1_year_dir.exists():
            self.logger.warning(f"  ⚠️ M1数据目录不存在: {m1_year_dir}")
            return
        
        # 获取所有M1文件并排序
        m1_files = list(m1_year_dir.glob('*.csv'))
        if not m1_files:
            self.logger.warning(f"  ⚠️ {m1_year_dir}目录中没有找到CSV文件")
            return
        
        m1_files.sort()
        
        # 为每个时间周期处理文件
        for timeframe_name, config in self.timeframes.items():
            self.logger.info(f"\n  📈 生成{timeframe_name}数据...")
            
            output_year_dir = self.base_path / instrument / config['folder'] / str(year)
            
            # 处理每个M1文件
            for m1_file in m1_files:
                output_file = output_year_dir / m1_file.name
                self.process_m1_file(m1_file, output_file, timeframe_name, config['minutes'])
    
    def process_instrument(self, instrument):
        """处理单个货币对的所有年份数据"""
        self.logger.info(f"\n🏦 开始处理货币对: {instrument}")
        
        # 检查该货币对是否有M1数据
        instrument_m1_dir = self.base_path / instrument / 'M1'
        if not instrument_m1_dir.exists():
            self.logger.warning(f"  ⚠️ {instrument} M1数据目录不存在")
            return
        
        for year in range(self.start_year, self.end_year + 1):
            self.process_year(instrument, year)
    
    def generate_conversion_report(self):
        """生成转换报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # HTML报告
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FXCM M1到M5转换报告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.8em;
            font-weight: 300;
        }}
        .header p {{
            margin: 15px 0 0;
            opacity: 0.9;
            font-size: 1.2em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            padding: 40px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            border-left: 5px solid;
            transition: transform 0.3s ease;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-card.primary {{ border-left-color: #007bff; }}
        .stat-card.success {{ border-left-color: #28a745; }}
        .stat-card.info {{ border-left-color: #17a2b8; }}
        .stat-card.warning {{ border-left-color: #ffc107; }}
        .stat-card.danger {{ border-left-color: #dc3545; }}
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            margin: 0;
            color: #2c3e50;
        }}
        .stat-label {{
            color: #6c757d;
            margin: 10px 0 0;
            font-size: 1em;
            font-weight: 500;
        }}
        .section {{
            margin: 40px;
        }}
        .section h2 {{
            color: #2c3e50;
            border-bottom: 3px solid #6c5ce7;
            padding-bottom: 15px;
            font-size: 1.8em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            background: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        th {{
            background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 1.1em;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #dee2e6;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #e3f2fd;
        }}
        .conversion-ratio {{
            font-weight: bold;
            color: #17a2b8;
        }}
        .footer {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            text-align: center;
            padding: 30px;
            font-size: 1em;
        }}
        .summary-box {{
            background: linear-gradient(135deg, #00cec9 0%, #55efc4 100%);
            color: white;
            padding: 30px;
            margin: 20px 0;
            border-radius: 12px;
            text-align: center;
        }}
        .summary-box h3 {{
            margin: 0 0 15px 0;
            font-size: 1.5em;
        }}
        .summary-box p {{
            margin: 5px 0;
            font-size: 1.1em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔄 M1到M5转换报告</h1>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card primary">
                <div class="stat-number">{self.stats['total_m1_files_processed']}</div>
                <div class="stat-label">M1文件处理数</div>
            </div>
            <div class="stat-card success">
                <div class="stat-number">{self.stats['total_m5_files_generated']}</div>
                <div class="stat-label">M5文件生成数</div>
            </div>
            <div class="stat-card info">
                <div class="stat-number">{self.stats['total_m1_records']:,}</div>
                <div class="stat-label">M1记录总数</div>
            </div>
            <div class="stat-card info">
                <div class="stat-number">{self.stats['total_m5_records']:,}</div>
                <div class="stat-label">M5记录总数</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-number">{self.stats['total_skipped_files']}</div>
                <div class="stat-label">跳过文件数</div>
            </div>
            <div class="stat-card danger">
                <div class="stat-number">{self.stats['processing_errors']}</div>
                <div class="stat-label">处理错误数</div>
            </div>
        </div>
"""
        
        # 转换效率摘要
        if self.stats['total_m5_records'] > 0:
            compression_ratio = self.stats['total_m1_records'] / self.stats['total_m5_records']
            
            html_content += f"""
        <div class="summary-box">
            <h3>📊 转换效率摘要</h3>
            <p><strong>数据压缩比:</strong> {compression_ratio:.1f}:1</p>
            <p><strong>处理时间:</strong> {self.stats['processing_time']:.1f} 秒</p>
            <p><strong>平均处理速度:</strong> {self.stats['total_m1_files_processed']/max(self.stats['processing_time'], 1):.1f} 文件/秒</p>
        </div>
"""
        
        # 按货币对统计
        html_content += """
        <div class="section">
            <h2>📈 按货币对统计</h2>
            <table>
                <thead>
                    <tr>
                        <th>货币对</th>
                        <th>处理文件数</th>
                        <th>生成M5文件</th>
                        <th>M1记录数</th>
                        <th>M5记录数</th>
                        <th>压缩比</th>
                        <th>错误数</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for instrument, years_data in self.stats['by_instrument'].items():
            total_processed = sum(year_data['files_processed'] for year_data in years_data.values())
            total_generated = sum(year_data['files_generated'] for year_data in years_data.values())
            total_m1_records = sum(year_data['m1_records'] for year_data in years_data.values())
            total_m5_records = sum(year_data['m5_records'] for year_data in years_data.values())
            total_errors = sum(year_data['errors'] for year_data in years_data.values())
            
            compression_ratio = total_m1_records / total_m5_records if total_m5_records > 0 else 0
            
            html_content += f"""
                    <tr>
                        <td><strong>{instrument}</strong></td>
                        <td>{total_processed}</td>
                        <td>{total_generated}</td>
                        <td>{total_m1_records:,}</td>
                        <td>{total_m5_records:,}</td>
                        <td class="conversion-ratio">{compression_ratio:.1f}:1</td>
                        <td>{total_errors}</td>
                    </tr>
"""
        
        html_content += """
                </tbody>
            </table>
        </div>
"""
        
        # 结尾
        html_content += f"""
        <div class="footer">
            <p>FXCM M1到M5数据转换器 v1.0.0</p>
            <p>转换完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
        
        # 保存HTML报告
        html_file = Path(__file__).parent.parent / 'logs' / f'm1_to_m5_report_{timestamp}.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 生成JSON报告
        json_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'script_version': '1.0.0',
                'conversion_type': 'M1_to_M5',
                'instruments': self.instruments,
                'year_range': f'{self.start_year}-{self.end_year}'
            },
            'statistics': self.stats
        }
        
        json_file = Path(__file__).parent.parent / 'logs' / f'm1_to_m5_report_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"转换报告已生成:")
        self.logger.info(f"  HTML: {html_file.absolute()}")
        self.logger.info(f"  JSON: {json_file.absolute()}")
        
        return html_file, json_file
    
    def process_all(self):
        """处理所有货币对的M1多时间周期转换"""
        self.logger.info("\n" + "="*50)
        self.logger.info("� 开始FXCM M1多时间周期数据转换")
        self.logger.info("支持的时间周期: " + ", ".join(self.timeframes.keys()))
        self.logger.info("="*50)
        
        # 检查数据目录
        if not self.base_path.exists():
            self.logger.error(f"数据目录不存在: {self.base_path.absolute()}")
            print(f"❌ 错误: 数据目录不存在 - {self.base_path.absolute()}")
            print("请先运行 fxcm_data_downloader.py 下载M1数据")
            return
        
        import time
        start_time = time.time()
        
        try:
            # 处理每个货币对
            for instrument in self.instruments:
                self.process_instrument(instrument)
            
            self.logger.info("\n" + "="*50)
            self.logger.info("✅ M1多时间周期转换完成!")
            self.logger.info(f"📊 处理统计:")
            self.logger.info(f"   - 处理文件数: {self.stats['total_processed_files']:,}")
            self.logger.info(f"   - 跳过文件数: {self.stats['total_skipped_files']:,}")
            self.logger.info(f"   - 输入数据行: {self.stats['total_input_rows']:,}")
            self.logger.info(f"   - 输出数据行: {self.stats['total_output_rows']:,}")
            
            if self.stats['total_input_rows'] > 0:
                overall_compression = self.stats['total_input_rows'] / self.stats['total_output_rows']
                self.logger.info(f"   - 总体压缩比: {overall_compression:.1f}:1")
            
            # 计算处理时间
            processing_time = time.time() - start_time
            self.logger.info(f"⏱️ 总处理时间: {processing_time:.2f} 秒")
            self.logger.info("="*50)
            
        except Exception as e:
            self.logger.error(f"转换过程中发生错误: {e}")
            print(f"❌ 转换失败: {e}")

def main():
    """主函数"""
    converter = FXCMMultiTimeframeConverter()
    converter.process_all()

if __name__ == '__main__':
    main()