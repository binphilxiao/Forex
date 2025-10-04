#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ClickHouse数据库表结构创建脚本
用于存储外汇OHLCV数据，支持多时间框架
"""

import requests
import json
import os
from datetime import datetime

class ClickHouseTableCreator:
    def __init__(self, config_path='config/clickhouse_config.json'):
        """初始化数据库连接配置"""
        self.config = self._load_config(config_path)
        self.base_url = f"http://{self.config['host']}:{self.config['http_port']}"
        self.auth = (self.config['user'], self.config['password'])
        
    def _load_config(self, config_path):
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def execute_query(self, query, description=""):
        """执行SQL查询"""
        try:
            response = requests.post(
                self.base_url,
                auth=self.auth,
                data=query.encode('utf-8'),
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ {description} - 成功")
                return True
            else:
                print(f"❌ {description} - 失败")
                print(f"   错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ {description} - 异常")
            print(f"   错误: {str(e)}")
            return False
    
    def create_database(self):
        """创建外汇数据库"""
        query = """
        CREATE DATABASE IF NOT EXISTS forex_data
        ENGINE = Atomic
        COMMENT '外汇历史数据库 - 存储FXCM多时间框架K线数据'
        """
        return self.execute_query(query, "创建数据库 forex_data")
    
    def create_m1_table(self):
        """创建M1（1分钟）原始数据表"""
        query = """
        CREATE TABLE IF NOT EXISTS forex_data.ohlcv_m1
        (
            symbol String COMMENT '交易对符号，如EURUSD',
            timestamp DateTime COMMENT 'K线开盘时间（UTC）',
            open Float64 COMMENT '开盘价',
            high Float64 COMMENT '最高价',
            low Float64 COMMENT '最低价',
            close Float64 COMMENT '收盘价',
            volume UInt64 DEFAULT 0 COMMENT '成交量（FXCM外汇数据无此字段，默认0）',
            created_at DateTime DEFAULT now() COMMENT '数据入库时间'
        )
        ENGINE = MergeTree()
        PARTITION BY toYYYYMM(timestamp)
        ORDER BY (symbol, timestamp)
        PRIMARY KEY (symbol, timestamp)
        SETTINGS index_granularity = 8192
        COMMENT 'M1分钟级原始K线数据表'
        """
        return self.execute_query(query, "创建表 ohlcv_m1 (1分钟数据)")
    
    def create_d1_table(self):
        """创建D1（日线）原始数据表"""
        query = """
        CREATE TABLE IF NOT EXISTS forex_data.ohlcv_d1
        (
            symbol String COMMENT '交易对符号',
            date Date COMMENT 'K线日期',
            open Float64 COMMENT '开盘价',
            high Float64 COMMENT '最高价',
            low Float64 COMMENT '最低价',
            close Float64 COMMENT '收盘价',
            volume UInt64 DEFAULT 0 COMMENT '成交量（FXCM外汇数据无此字段，默认0）',
            created_at DateTime DEFAULT now() COMMENT '数据入库时间'
        )
        ENGINE = MergeTree()
        PARTITION BY toYear(date)
        ORDER BY (symbol, date)
        PRIMARY KEY (symbol, date)
        SETTINGS index_granularity = 8192
        COMMENT 'D1日线级原始K线数据表'
        """
        return self.execute_query(query, "创建表 ohlcv_d1 (日线数据)")
    
    def create_m5_materialized_view(self):
        """创建M5（5分钟）物化视图"""
        # 先创建目标表
        target_table_query = """
        CREATE TABLE IF NOT EXISTS forex_data.ohlcv_m5
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
        PRIMARY KEY (symbol, timestamp)
        COMMENT 'M5 (5分钟) K线数据表 - 由M1自动聚合生成'
        """
        
        # 创建物化视图
        mv_query = """
        CREATE MATERIALIZED VIEW IF NOT EXISTS forex_data.ohlcv_m5_mv
        TO forex_data.ohlcv_m5
        AS
        SELECT
            symbol,
            toStartOfInterval(timestamp, INTERVAL 5 MINUTE) AS timestamp,
            argMin(open, timestamp) AS open,
            max(high) AS high,
            min(low) AS low,
            argMax(close, timestamp) AS close,
            sum(volume) AS volume
        FROM forex_data.ohlcv_m1
        GROUP BY symbol, timestamp
        """
        
        self.execute_query(target_table_query, "创建表 ohlcv_m5")
        return self.execute_query(mv_query, "创建物化视图 ohlcv_m5_mv (自动聚合)")
    
    def create_m15_materialized_view(self):
        """创建M15（15分钟）物化视图"""
        target_table_query = """
        CREATE TABLE IF NOT EXISTS forex_data.ohlcv_m15
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
        PRIMARY KEY (symbol, timestamp)
        COMMENT 'M15 (15分钟) K线数据表 - 由M1自动聚合生成'
        """
        
        mv_query = """
        CREATE MATERIALIZED VIEW IF NOT EXISTS forex_data.ohlcv_m15_mv
        TO forex_data.ohlcv_m15
        AS
        SELECT
            symbol,
            toStartOfInterval(timestamp, INTERVAL 15 MINUTE) AS timestamp,
            argMin(open, timestamp) AS open,
            max(high) AS high,
            min(low) AS low,
            argMax(close, timestamp) AS close,
            sum(volume) AS volume
        FROM forex_data.ohlcv_m1
        GROUP BY symbol, timestamp
        """
        
        self.execute_query(target_table_query, "创建表 ohlcv_m15")
        return self.execute_query(mv_query, "创建物化视图 ohlcv_m15_mv (自动聚合)")
    
    def create_m30_materialized_view(self):
        """创建M30（30分钟）物化视图"""
        target_table_query = """
        CREATE TABLE IF NOT EXISTS forex_data.ohlcv_m30
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
        PRIMARY KEY (symbol, timestamp)
        COMMENT 'M30 (30分钟) K线数据表 - 由M1自动聚合生成'
        """
        
        mv_query = """
        CREATE MATERIALIZED VIEW IF NOT EXISTS forex_data.ohlcv_m30_mv
        TO forex_data.ohlcv_m30
        AS
        SELECT
            symbol,
            toStartOfInterval(timestamp, INTERVAL 30 MINUTE) AS timestamp,
            argMin(open, timestamp) AS open,
            max(high) AS high,
            min(low) AS low,
            argMax(close, timestamp) AS close,
            sum(volume) AS volume
        FROM forex_data.ohlcv_m1
        GROUP BY symbol, timestamp
        """
        
        self.execute_query(target_table_query, "创建表 ohlcv_m30")
        return self.execute_query(mv_query, "创建物化视图 ohlcv_m30_mv (自动聚合)")
    
    def create_h1_materialized_view(self):
        """创建H1（1小时）物化视图"""
        target_table_query = """
        CREATE TABLE IF NOT EXISTS forex_data.ohlcv_h1
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
        PRIMARY KEY (symbol, timestamp)
        COMMENT 'H1 (1小时) K线数据表 - 由M1自动聚合生成'
        """
        
        mv_query = """
        CREATE MATERIALIZED VIEW IF NOT EXISTS forex_data.ohlcv_h1_mv
        TO forex_data.ohlcv_h1
        AS
        SELECT
            symbol,
            toStartOfHour(timestamp) AS timestamp,
            argMin(open, timestamp) AS open,
            max(high) AS high,
            min(low) AS low,
            argMax(close, timestamp) AS close,
            sum(volume) AS volume
        FROM forex_data.ohlcv_m1
        GROUP BY symbol, timestamp
        """
        
        self.execute_query(target_table_query, "创建表 ohlcv_h1")
        return self.execute_query(mv_query, "创建物化视图 ohlcv_h1_mv (自动聚合)")
    
    def create_all_tables(self):
        """创建所有表和物化视图"""
        print("\n" + "="*70)
        print("          ClickHouse 外汇数据库表结构创建")
        print("="*70 + "\n")
        
        # 1. 创建数据库
        print("📊 步骤 1/7: 创建数据库")
        self.create_database()
        
        # 2. 创建M1原始数据表
        print("\n📊 步骤 2/7: 创建M1原始数据表")
        self.create_m1_table()
        
        # 3. 创建D1原始数据表
        print("\n📊 步骤 3/7: 创建D1原始数据表")
        self.create_d1_table()
        
        # 4-7. 创建各时间框架物化视图
        print("\n📊 步骤 4/7: 创建M5物化视图")
        self.create_m5_materialized_view()
        
        print("\n📊 步骤 5/7: 创建M15物化视图")
        self.create_m15_materialized_view()
        
        print("\n📊 步骤 6/7: 创建M30物化视图")
        self.create_m30_materialized_view()
        
        print("\n📊 步骤 7/7: 创建H1物化视图")
        self.create_h1_materialized_view()
        
        print("\n" + "="*70)
        print("✅ 数据库表结构创建完成！")
        print("="*70)
        
        # 显示创建的表
        self.show_tables()
    
    def show_tables(self):
        """显示所有创建的表"""
        print("\n📋 已创建的表和视图：\n")
        
        query = "SHOW TABLES FROM forex_data"
        try:
            response = requests.post(
                self.base_url,
                auth=self.auth,
                data=query.encode('utf-8')
            )
            
            if response.status_code == 200:
                tables = response.text.strip().split('\n')
                for i, table in enumerate(tables, 1):
                    print(f"   {i}. {table}")
            else:
                print("   无法获取表列表")
                
        except Exception as e:
            print(f"   错误: {str(e)}")
        
        print()

def main():
    """主函数"""
    try:
        creator = ClickHouseTableCreator()
        creator.create_all_tables()
        
        print("\n💡 使用说明：")
        print("   1. 原始数据导入：")
        print("      - M1数据 → forex_data.ohlcv_m1")
        print("      - D1数据 → forex_data.ohlcv_d1")
        print()
        print("   2. 自动生成数据（物化视图自动触发）：")
        print("      - M5  (5分钟)  ← 自动从M1聚合")
        print("      - M15 (15分钟) ← 自动从M1聚合")
        print("      - M30 (30分钟) ← 自动从M1聚合")
        print("      - H1  (1小时)  ← 自动从M1聚合")
        print()
        print("   3. 数据查询示例：")
        print("      SELECT * FROM forex_data.ohlcv_m5 WHERE symbol='EURUSD' LIMIT 10")
        print()
        
    except FileNotFoundError:
        print("❌ 错误: 找不到配置文件 config/clickhouse_config.json")
        print("   请确保配置文件存在")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")

if __name__ == "__main__":
    main()
