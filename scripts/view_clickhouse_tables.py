#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查看ClickHouse数据库表结构和统计信息
"""

import requests
import json
from datetime import datetime

class ClickHouseTableViewer:
    def __init__(self, config_path='config/clickhouse_config.json'):
        """初始化数据库连接"""
        self.config = self._load_config(config_path)
        self.base_url = f"http://{self.config['host']}:{self.config['http_port']}"
        self.auth = (self.config['user'], self.config['password'])
        
    def _load_config(self, config_path):
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def execute_query(self, query):
        """执行查询并返回结果"""
        try:
            response = requests.post(
                self.base_url,
                auth=self.auth,
                data=query.encode('utf-8'),
                timeout=30
            )
            
            if response.status_code == 200:
                return response.text.strip()
            else:
                return f"错误: {response.text}"
                
        except Exception as e:
            return f"异常: {str(e)}"
    
    def show_databases(self):
        """显示所有数据库"""
        print("\n📊 数据库列表:")
        print("-" * 50)
        result = self.execute_query("SHOW DATABASES")
        for db in result.split('\n'):
            print(f"   • {db}")
    
    def show_tables(self):
        """显示forex_data数据库中的所有表"""
        print("\n📋 forex_data 数据库表列表:")
        print("-" * 50)
        result = self.execute_query("SHOW TABLES FROM forex_data")
        tables = result.split('\n')
        
        # 分类显示
        data_tables = [t for t in tables if not t.endswith('_mv')]
        views = [t for t in tables if t.endswith('_mv')]
        
        print("\n   数据表:")
        for table in data_tables:
            print(f"   ├─ {table}")
        
        print("\n   物化视图:")
        for view in views:
            print(f"   ├─ {view}")
    
    def show_table_structure(self, table_name):
        """显示表结构"""
        print(f"\n📐 表结构: {table_name}")
        print("-" * 70)
        query = f"DESCRIBE TABLE forex_data.{table_name}"
        result = self.execute_query(query)
        
        print(f"{'字段名':<15} {'类型':<20} {'说明'}")
        print("-" * 70)
        for line in result.split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    print(f"{parts[0]:<15} {parts[1]:<20}")
    
    def show_table_stats(self):
        """显示表统计信息"""
        print("\n📊 表数据统计:")
        print("-" * 80)
        
        query = """
        SELECT 
            table,
            formatReadableSize(sum(bytes)) AS size,
            sum(rows) AS rows,
            count() AS parts
        FROM system.parts
        WHERE database = 'forex_data'
          AND active
        GROUP BY table
        ORDER BY table
        """
        
        result = self.execute_query(query)
        
        print(f"{'表名':<15} {'大小':<15} {'行数':<15} {'分区数'}")
        print("-" * 80)
        for line in result.split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 4:
                    print(f"{parts[0]:<15} {parts[1]:<15} {parts[2]:<15} {parts[3]}")
    
    def show_data_sample(self, table_name, limit=5):
        """显示表数据样本"""
        print(f"\n📄 表数据样本: {table_name} (前{limit}条)")
        print("-" * 100)
        
        query = f"SELECT * FROM forex_data.{table_name} LIMIT {limit} FORMAT PrettyCompact"
        result = self.execute_query(query)
        print(result)
    
    def show_symbol_stats(self):
        """显示各货币对数据统计"""
        print("\n💱 货币对数据统计:")
        print("-" * 80)
        
        query = """
        SELECT 
            symbol,
            count() AS m1_count,
            min(timestamp) AS first_time,
            max(timestamp) AS last_time
        FROM forex_data.ohlcv_m1
        GROUP BY symbol
        ORDER BY symbol
        """
        
        result = self.execute_query(query)
        
        print(f"{'货币对':<10} {'M1数据量':<15} {'开始时间':<20} {'结束时间'}")
        print("-" * 80)
        for line in result.split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 4:
                    print(f"{parts[0]:<10} {parts[1]:<15} {parts[2]:<20} {parts[3]}")
    
    def show_all_info(self):
        """显示所有信息"""
        print("\n" + "="*80)
        print("          ClickHouse 外汇数据库信息查看")
        print("="*80)
        
        # 1. 数据库列表
        self.show_databases()
        
        # 2. 表列表
        self.show_tables()
        
        # 3. 表统计
        self.show_table_stats()
        
        # 4. M1表结构
        self.show_table_structure('ohlcv_m1')
        
        # 5. 货币对统计
        self.show_symbol_stats()
        
        print("\n" + "="*80)
        print("✅ 信息查看完成")
        print("="*80 + "\n")

def main():
    """主函数"""
    try:
        viewer = ClickHouseTableViewer()
        viewer.show_all_info()
        
    except FileNotFoundError:
        print("❌ 错误: 找不到配置文件 config/clickhouse_config.json")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")

if __name__ == "__main__":
    main()
