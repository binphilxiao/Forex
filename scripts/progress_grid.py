#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Progress Grid Display Module
============================

提供彩色进度网格显示功能，用于实时显示数据处理状态。

使用Unicode彩色方块展示进度：
- 🟩 绿色：成功处理/新数据写入/数据一致
- 🟦 蓝色：文件已存在所以跳过
- 🟨 黄色：数据有警告或只部分验证通过/不一致
- 🟥 红色：下载/导入失败或文件缺失/没有数据

Author: FXCM Data Team
Version: 1.0.0
Date: 2025-10-06
"""

import sys
from typing import Dict, List, Optional
from enum import Enum


class ProgressStatus(Enum):
    """进度状态枚举"""
    SUCCESS = "success"          # 绿色：成功处理/新数据写入/数据一致
    SKIPPED = "skipped"          # 蓝色：文件已存在所以跳过
    WARNING = "warning"          # 黄色：数据有警告或只部分验证通过/不一致
    ERROR = "error"              # 红色：下载/导入失败或文件缺失/没有数据
    PENDING = "pending"          # 灰色：待处理


class ProgressGrid:
    """
    进度网格显示器
    
    使用彩色方块实时显示处理进度
    """
    
    # Unicode彩色方块
    SYMBOLS = {
        ProgressStatus.SUCCESS: '🟩',
        ProgressStatus.SKIPPED: '🟦',
        ProgressStatus.WARNING: '🟨',
        ProgressStatus.ERROR: '🟥',
        ProgressStatus.PENDING: '⬜'
    }
    
    # 终端颜色代码（用于日志文件）
    COLORS = {
        ProgressStatus.SUCCESS: '\033[92m',    # 绿色
        ProgressStatus.SKIPPED: '\033[94m',    # 蓝色
        ProgressStatus.WARNING: '\033[93m',    # 黄色
        ProgressStatus.ERROR: '\033[91m',      # 红色
        ProgressStatus.PENDING: '\033[90m',    # 灰色
        'RESET': '\033[0m'
    }
    
    # 状态描述
    STATUS_DESCRIPTIONS = {
        ProgressStatus.SUCCESS: '成功/一致',
        ProgressStatus.SKIPPED: '已跳过',
        ProgressStatus.WARNING: '警告/不一致',
        ProgressStatus.ERROR: '失败/无数据',
        ProgressStatus.PENDING: '待处理'
    }
    
    def __init__(self, title: str = "处理进度"):
        """
        初始化进度网格显示器
        
        Args:
            title: 显示标题
        """
        self.title = title
        self.grids = {}  # {symbol: {timeframe: {year: [status_list]}}}
        self.current_line = None  # 当前显示的行
        
    def initialize_grid(self, 
                        symbol: str, 
                        timeframe: str, 
                        year: int, 
                        total_items: int):
        """
        初始化一个网格
        
        Args:
            symbol: 货币对符号
            timeframe: 时间周期
            year: 年份
            total_items: 总项目数（周数或文件数）
        """
        if symbol not in self.grids:
            self.grids[symbol] = {}
        if timeframe not in self.grids[symbol]:
            self.grids[symbol][timeframe] = {}
        
        # 初始化为待处理状态
        self.grids[symbol][timeframe][year] = [ProgressStatus.PENDING] * total_items
    
    def update_status(self, 
                     symbol: str, 
                     timeframe: str, 
                     year: int, 
                     item_index: int, 
                     status: ProgressStatus):
        """
        更新单个项目的状态
        
        Args:
            symbol: 货币对符号
            timeframe: 时间周期
            year: 年份
            item_index: 项目索引（从0开始）
            status: 新状态
        """
        if (symbol in self.grids and 
            timeframe in self.grids[symbol] and 
            year in self.grids[symbol][timeframe] and
            0 <= item_index < len(self.grids[symbol][timeframe][year])):
            
            self.grids[symbol][timeframe][year][item_index] = status
    
    def display_line(self, 
                    symbol: str, 
                    timeframe: str, 
                    year: int, 
                    label: Optional[str] = None):
        """
        显示一行进度（实时更新同一行）
        
        Args:
            symbol: 货币对符号
            timeframe: 时间周期
            year: 年份
            label: 自定义标签（默认为"symbol timeframe year"）
        """
        if (symbol not in self.grids or 
            timeframe not in self.grids[symbol] or 
            year not in self.grids[symbol][timeframe]):
            return
        
        # 生成标签
        if label is None:
            label = f"{symbol} {timeframe} {year}"
        
        # 生成进度方块
        statuses = self.grids[symbol][timeframe][year]
        progress_symbols = ''.join([self.SYMBOLS[s] for s in statuses])
        
        # 清除当前行并显示新内容
        line = f"\r{label:25s}: {progress_symbols}"
        sys.stdout.write(line)
        sys.stdout.flush()
        self.current_line = line
    
    def newline(self):
        """换行（确认当前行的显示）"""
        if self.current_line:
            print()  # 输出换行
            self.current_line = None
    
    def display_all(self):
        """显示所有网格（用于最终展示）"""
        print(f"\n{'='*80}")
        print(f"  {self.title}")
        print(f"{'='*80}\n")
        
        for symbol in sorted(self.grids.keys()):
            print(f"\n💱 {symbol}")
            print(f"{'-'*80}")
            
            for timeframe in sorted(self.grids[symbol].keys()):
                print(f"\n  📊 {timeframe} 数据:")
                
                for year in sorted(self.grids[symbol][timeframe].keys()):
                    statuses = self.grids[symbol][timeframe][year]
                    progress_symbols = ''.join([self.SYMBOLS[s] for s in statuses])
                    
                    label = f"    {year}"
                    print(f"{label:10s}: {progress_symbols}")
        
        print()
    
    def get_statistics(self) -> Dict[str, int]:
        """
        获取统计信息
        
        Returns:
            字典，包含各状态的数量
        """
        stats = {
            'success': 0,
            'skipped': 0,
            'warning': 0,
            'error': 0,
            'pending': 0,
            'total': 0
        }
        
        for symbol in self.grids:
            for timeframe in self.grids[symbol]:
                for year in self.grids[symbol][timeframe]:
                    for status in self.grids[symbol][timeframe][year]:
                        stats[status.value] += 1
                        stats['total'] += 1
        
        return stats
    
    def print_summary(self):
        """打印统计摘要"""
        stats = self.get_statistics()
        total = stats['total']
        
        if total == 0:
            return
        
        print(f"\n{'='*80}")
        print(f"  📊 统计摘要")
        print(f"{'='*80}")
        print(f"总计: {total}")
        print(f"{self.SYMBOLS[ProgressStatus.SUCCESS]} 成功/一致:     {stats['success']:5d} ({stats['success']/total*100:5.1f}%)")
        print(f"{self.SYMBOLS[ProgressStatus.SKIPPED]} 已跳过:        {stats['skipped']:5d} ({stats['skipped']/total*100:5.1f}%)")
        print(f"{self.SYMBOLS[ProgressStatus.WARNING]} 警告/不一致:  {stats['warning']:5d} ({stats['warning']/total*100:5.1f}%)")
        print(f"{self.SYMBOLS[ProgressStatus.ERROR]} 失败/无数据:  {stats['error']:5d} ({stats['error']/total*100:5.1f}%)")
        print(f"{'='*80}\n")
    
    def print_legend(self):
        """打印图例"""
        print(f"\n{'='*80}")
        print(f"  图例说明")
        print(f"{'='*80}")
        print(f"{self.SYMBOLS[ProgressStatus.SUCCESS]} 成功处理/新数据写入/数据一致")
        print(f"{self.SYMBOLS[ProgressStatus.SKIPPED]} 文件已存在所以跳过")
        print(f"{self.SYMBOLS[ProgressStatus.WARNING]} 数据有警告或只部分验证通过/不一致")
        print(f"{self.SYMBOLS[ProgressStatus.ERROR]} 下载/导入失败或文件缺失/没有数据")
        print(f"{'='*80}\n")


class YearWeekProgressGrid(ProgressGrid):
    """
    年份-周数进度网格（用于M1数据）
    
    专门处理按年份和周数组织的数据进度显示
    """
    
    def __init__(self, title: str = "M1 数据处理进度"):
        super().__init__(title)
    
    def initialize_year(self, symbol: str, year: int, weeks: int = 52):
        """
        初始化一年的周数网格
        
        Args:
            symbol: 货币对符号
            year: 年份
            weeks: 周数（默认52）
        """
        self.initialize_grid(symbol, 'M1', year, weeks)
    
    def update_week(self, 
                   symbol: str, 
                   year: int, 
                   week: int, 
                   status: ProgressStatus):
        """
        更新某一周的状态
        
        Args:
            symbol: 货币对符号
            year: 年份
            week: 周数（1-52）
            status: 状态
        """
        self.update_status(symbol, 'M1', year, week - 1, status)
    
    def display_year(self, symbol: str, year: int):
        """
        显示一年的进度
        
        Args:
            symbol: 货币对符号
            year: 年份
        """
        self.display_line(symbol, 'M1', year)


class YearFileProgressGrid(ProgressGrid):
    """
    年份文件进度网格（用于D1数据）
    
    专门处理按年份组织的单文件数据进度显示
    """
    
    def __init__(self, title: str = "D1 数据处理进度"):
        super().__init__(title)
    
    def initialize_years(self, symbol: str, years: List[int]):
        """
        初始化多个年份的网格
        
        Args:
            symbol: 货币对符号
            years: 年份列表
        """
        self.initialize_grid(symbol, 'D1', 0, len(years))
        self.year_index_map = {year: idx for idx, year in enumerate(years)}
        self.years = years
    
    def update_year(self, 
                   symbol: str, 
                   year: int, 
                   status: ProgressStatus):
        """
        更新某一年的状态
        
        Args:
            symbol: 货币对符号
            year: 年份
            status: 状态
        """
        if hasattr(self, 'year_index_map') and year in self.year_index_map:
            idx = self.year_index_map[year]
            self.update_status(symbol, 'D1', 0, idx, status)


def demo():
    """演示进度网格的使用"""
    import time
    import random
    
    print("\n" + "="*80)
    print("  进度网格显示演示")
    print("="*80 + "\n")
    
    # 显示图例
    grid = ProgressGrid()
    grid.print_legend()
    
    # M1数据演示
    print("\n【M1 数据处理演示】\n")
    m1_grid = YearWeekProgressGrid("M1 数据下载进度")
    
    symbol = "EURUSD"
    year = 2024
    weeks = 52
    
    m1_grid.initialize_year(symbol, year, weeks)
    
    # 模拟处理过程
    for week in range(1, weeks + 1):
        # 随机状态
        status_choice = random.choice([
            ProgressStatus.SUCCESS,
            ProgressStatus.SKIPPED,
            ProgressStatus.WARNING,
            ProgressStatus.ERROR
        ])
        
        m1_grid.update_week(symbol, year, week, status_choice)
        m1_grid.display_year(symbol, year)
        time.sleep(0.05)  # 模拟处理延迟
    
    m1_grid.newline()
    
    # D1数据演示
    print("\n【D1 数据处理演示】\n")
    d1_grid = YearFileProgressGrid("D1 数据导入进度")
    
    symbol = "GBPUSD"
    years = list(range(2015, 2025))
    
    d1_grid.initialize_years(symbol, years)
    
    # 模拟处理过程
    for year in years:
        status_choice = random.choice([
            ProgressStatus.SUCCESS,
            ProgressStatus.SKIPPED,
            ProgressStatus.WARNING,
            ProgressStatus.ERROR
        ])
        
        d1_grid.update_year(symbol, year, status_choice)
        d1_grid.display_line(symbol, 'D1', 0, f"{symbol} D1")
        time.sleep(0.2)
    
    d1_grid.newline()
    
    # 显示统计
    print("\n【M1 统计】")
    m1_grid.print_summary()
    
    print("\n【D1 统计】")
    d1_grid.print_summary()


if __name__ == '__main__':
    demo()
