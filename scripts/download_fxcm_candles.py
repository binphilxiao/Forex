"""
FXCM Historical Candle Data Downloader
下载FXCM公开的历史蜡烛图数据

使用方法：
python download_fxcm_candles.py

数据源：https://candledata.fxcorporate.com/
"""

import os
import sys
import io
import json
import requests
import gzip
import pandas as pd
from datetime import datetime, timedelta
import time
from pathlib import Path
import logging

# 设置标准输出编码为UTF-8，避免Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 读取配置文件（如果存在）
config_file = Path(__file__).parent.parent / 'config' / 'download_config.json'
if config_file.exists():
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    INSTRUMENTS = config.get('pairs', ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF'])
    START_YEAR = config.get('start_year', 2015)
    END_YEAR = config.get('end_year', 2021)
    RETRY_ENABLED = config.get('retry_enabled', True)
    MAX_RETRIES = config.get('retry_times', 3) if RETRY_ENABLED else 1
else:
    # 默认配置
    INSTRUMENTS = ['EURUSD', 'USDCAD', 'GBPUSD', 'USDCHF', 'AUDUSD', 'USDJPY']
    START_YEAR = 2015
    END_YEAR = 2021
    RETRY_ENABLED = True
    MAX_RETRIES = 3

TIMEFRAMES = {
    'M1': 1,      # 1分钟
    'D1': 1440    # 1天
}

# 数据保存路径
OUTPUT_DIR = Path('fxcm_data')
LOG_DIR = Path('logs')

class FXCMDataDownloader:
    def __init__(self):
        self.base_url = "https://candledata.fxcorporate.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 设置日志
        LOG_DIR.mkdir(exist_ok=True)
        # 使用时间戳创建日志文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = LOG_DIR / f'download_{timestamp}.log'
        
        # 配置日志格式
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"日志文件: {log_file}")
    
    def download_week_data(self, instrument, year, week, timeframe='m1', max_retries=5):
        """下载单周的分钟级数据（m1），支持重试"""
        url = f"{self.base_url}/{timeframe}/{instrument}/{year}/{week}.csv.gz"
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    # 解压gzip数据
                    decompressed = gzip.decompress(response.content)
                    # 转换为DataFrame
                    from io import StringIO
                    df = pd.read_csv(StringIO(decompressed.decode('utf-8')))
                    
                    # 检查并重命名列（FXCM格式可能有不同的列名）
                    if 'DateTime' in df.columns or 'Datetime' in df.columns:
                        # 统一列名
                        df.columns = df.columns.str.lower()
                        if 'bidopen' in df.columns:
                            df = df.rename(columns={
                                'datetime': 'DateTime',
                                'bidopen': 'Open',
                                'bidhigh': 'High',
                                'bidlow': 'Low',
                                'bidclose': 'Close'
                            })
                        else:
                            df = df.rename(columns={'datetime': 'DateTime'})
                            df.columns = [col.capitalize() for col in df.columns]
                        
                        df['DateTime'] = pd.to_datetime(df['DateTime'])
                        # 只保留需要的列
                        cols_to_keep = ['DateTime', 'Open', 'High', 'Low', 'Close']
                        if 'Volume' in df.columns:
                            cols_to_keep.append('Volume')
                        df = df[cols_to_keep]
                        
                        # 记录成功下载
                        self.logger.info(f"✅ 下载成功: {url} ({len(df)} 条记录)")
                        return df
                    else:
                        print(f"  ⚠️ 未知的CSV格式，列名: {df.columns.tolist()}")
                        self.logger.warning(f"未知CSV格式: {url} - 列名: {df.columns.tolist()}")
                        return None
                        
                elif response.status_code == 404:
                    # 404错误重试
                    if attempt < max_retries - 1:
                        time.sleep(0.5)  # 等待0.5秒后重试
                        continue
                    else:
                        # 最后一次重试仍失败，记录404错误
                        self.logger.info(f"❌ 404错误（重试{max_retries}次后）: {url}")
                        return None
                else:
                    print(f"  ⚠️ HTTP {response.status_code}: {url}")
                    self.logger.warning(f"HTTP {response.status_code}: {url}")
                    return None
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # 等待0.5秒后重试
                    continue
                else:
                    print(f"  ❌ 下载失败 {url}: {e}")
                    self.logger.error(f"下载失败（重试{max_retries}次后）: {url} - 错误: {e}")
                    return None
        
        return None
    
    def download_daily_data(self, instrument, year, max_retries=5):
        """下载整年的日线数据（D1），支持重试"""
        url = f"{self.base_url}/D1/{instrument}/{year}.csv.gz"
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    # 解压gzip数据
                    decompressed = gzip.decompress(response.content)
                    # 转换为DataFrame
                    from io import StringIO
                    df = pd.read_csv(StringIO(decompressed.decode('utf-8')))
                    
                    # 检查并重命名列
                    if 'DateTime' in df.columns or 'Datetime' in df.columns:
                        df.columns = df.columns.str.lower()
                        if 'bidopen' in df.columns:
                            df = df.rename(columns={
                                'datetime': 'DateTime',
                                'bidopen': 'Open',
                                'bidhigh': 'High',
                                'bidlow': 'Low',
                                'bidclose': 'Close'
                            })
                        else:
                            df = df.rename(columns={'datetime': 'DateTime'})
                            df.columns = [col.capitalize() for col in df.columns]
                        
                        df['DateTime'] = pd.to_datetime(df['DateTime'])
                        # 只保留需要的列
                        cols_to_keep = ['DateTime', 'Open', 'High', 'Low', 'Close']
                        if 'Volume' in df.columns:
                            cols_to_keep.append('Volume')
                        df = df[cols_to_keep]
                        
                        # 记录成功下载
                        self.logger.info(f"✅ 下载成功: {url} ({len(df)} 条记录)")
                        return df
                    else:
                        print(f"  ⚠️ 未知的CSV格式，列名: {df.columns.tolist()}")
                        self.logger.warning(f"未知CSV格式: {url} - 列名: {df.columns.tolist()}")
                        return None
                        
                elif response.status_code == 404:
                    # 404错误重试
                    if attempt < max_retries - 1:
                        time.sleep(0.5)  # 等待0.5秒后重试
                        continue
                    else:
                        # 最后一次重试仍失败，记录404错误
                        self.logger.info(f"❌ 404错误（重试{max_retries}次后）: {url}")
                        return None
                else:
                    print(f"  ⚠️ HTTP {response.status_code}: {url}")
                    self.logger.warning(f"HTTP {response.status_code}: {url}")
                    return None
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # 等待0.5秒后重试
                    continue
                else:
                    print(f"  ❌ 下载失败 {url}: {e}")
                    self.logger.error(f"下载失败（重试{max_retries}次后）: {url} - 错误: {e}")
                    return None
        
        return None
    
    def download_all_data(self):
        """下载所有货币对和时间周期的数据"""
        print("="*60)
        print("FXCM 历史数据下载器")
        print("="*60)
        print(f"货币对: {', '.join(INSTRUMENTS)}")
        print(f"时间周期: {', '.join(TIMEFRAMES.keys())}")
        print(f"年份范围: {START_YEAR} - {END_YEAR}")
        print(f"失败重试: {'是' if RETRY_ENABLED else '否'}")
        if RETRY_ENABLED:
            print(f"重试次数: {MAX_RETRIES}")
        print(f"保存路径: {OUTPUT_DIR.absolute()}")
        print("="*60)
        
        # 创建输出目录
        OUTPUT_DIR.mkdir(exist_ok=True)
        
        for instrument in INSTRUMENTS:
            print(f"\n{'='*60}")
            print(f"处理货币对: {instrument}")
            print(f"{'='*60}")
            
            # 创建货币对目录
            instrument_dir = OUTPUT_DIR / instrument
            instrument_dir.mkdir(exist_ok=True)
            
            # 处理每个时间周期
            for tf_name in TIMEFRAMES.keys():
                print(f"\n{'='*50}")
                print(f"处理时间周期: {tf_name}")
                print(f"{'='*50}")
                
                if tf_name == 'M1':
                    # 下载M1数据（按周下载并分别保存）
                    for year in range(START_YEAR, END_YEAR + 1):
                        # 创建目录结构: EURUSD/M1/2019/
                        year_dir = instrument_dir / tf_name / str(year)
                        year_dir.mkdir(parents=True, exist_ok=True)
                        
                        print(f"\n📥 下载 {instrument} {year}年 M1 数据...")
                        
                        for week in range(1, 53):
                            # 检查文件是否已存在
                            filename = year_dir / f"week_{week:02d}.csv"
                            if filename.exists():
                                print(f"  Week {week}/52... ⏭️ 已存在，跳过")
                                continue
                            
                            print(f"  Week {week}/52...", end=' ')
                            df = self.download_week_data(instrument, year, week, timeframe='m1', max_retries=MAX_RETRIES)
                            
                            if df is not None and not df.empty:
                                # 保存到: EURUSD/M1/2019/week_01.csv
                                df.to_csv(filename, index=False)
                                print(f"✅ {len(df)} 条记录 -> {filename.name}")
                            else:
                                print("⏭️ 跳过")
                            
                            time.sleep(0.1)
                
                elif tf_name == 'D1':
                    # 下载D1数据（按年下载）
                    # 创建目录结构: EURUSD/D1/
                    tf_dir = instrument_dir / tf_name
                    tf_dir.mkdir(parents=True, exist_ok=True)
                    
                    for year in range(START_YEAR, END_YEAR + 1):
                        # 检查文件是否已存在
                        filename = tf_dir / f"{year}.csv"
                        if filename.exists():
                            print(f"\n📥 下载 {instrument} {year}年 D1 数据... ⏭️ 已存在，跳过")
                            continue
                        
                        print(f"\n📥 下载 {instrument} {year}年 D1 数据...", end=' ')
                        year_data = self.download_daily_data(instrument, year)
                        
                        if year_data is not None and not year_data.empty:
                            # 保存到: EURUSD/D1/2019.csv
                            year_data.to_csv(filename, index=False)
                            print(f"✅ {len(year_data)} 条记录 -> {filename.name}")
                        else:
                            print("⏭️ 跳过")
                        
                        time.sleep(0.1)
        
        print(f"\n{'='*60}")
        print("✅ 所有数据下载完成！")
        print(f"{'='*60}")

def main():
    downloader = FXCMDataDownloader()
    downloader.download_all_data()

if __name__ == "__main__":
    main()
