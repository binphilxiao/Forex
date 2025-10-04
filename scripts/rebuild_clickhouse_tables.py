#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重建ClickHouse数据库表（修复volume字段问题）
"""

import requests
import json

class ClickHouseTableRebuilder:
    def __init__(self, config_path='config/clickhouse_config.json'):
        """初始化数据库连接"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.base_url = f"http://{self.config['host']}:{self.config['http_port']}"
        self.auth = (self.config['user'], self.config['password'])
    
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
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description}")
                print(f"   错误: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ {description}")
            print(f"   异常: {str(e)}")
            return False
    
    def drop_all_tables(self):
        """删除所有表和物化视图"""
        print("\n🗑️  删除现有表和物化视图...")
        print("-" * 60)
        
        # 删除物化视图（必须先删除）
        views = ['ohlcv_m5_mv', 'ohlcv_m15_mv', 'ohlcv_m30_mv', 'ohlcv_h1_mv']
        for view in views:
            query = f"DROP TABLE IF EXISTS forex_data.{view}"
            self.execute_query(query, f"删除物化视图 {view}")
        
        # 删除数据表
        tables = ['ohlcv_m1', 'ohlcv_d1', 'ohlcv_m5', 'ohlcv_m15', 'ohlcv_m30', 'ohlcv_h1']
        for table in tables:
            query = f"DROP TABLE IF EXISTS forex_data.{table}"
            self.execute_query(query, f"删除表 {table}")
    
    def rebuild_tables(self):
        """重建所有表"""
        print("\n" + "="*70)
        print("          重建ClickHouse表结构（修复volume默认值）")
        print("="*70)
        
        # 1. 删除现有表
        self.drop_all_tables()
        
        # 2. 重新创建表
        print("\n🔨 重新创建表结构...")
        print("-" * 60)
        
        # 导入并运行建表脚本
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))
        
        from create_clickhouse_tables import ClickHouseTableCreator
        creator = ClickHouseTableCreator()
        
        # 创建数据库
        creator.create_database()
        
        # 创建表
        print("\n📊 创建原始数据表...")
        creator.create_m1_table()
        creator.create_d1_table()
        
        # 创建物化视图
        print("\n📊 创建物化视图...")
        creator.create_m5_materialized_view()
        creator.create_m15_materialized_view()
        creator.create_m30_materialized_view()
        creator.create_h1_materialized_view()
        
        # 显示创建的表
        print("\n" + "="*70)
        print("✅ 表结构重建完成！")
        print("="*70)
        
        creator.show_tables()
        
        print("\n💡 重要更新：")
        print("   • volume 字段现在有默认值 0")
        print("   • created_at 字段自动生成当前时间")
        print("   • 导入CSV时可以省略这两个字段")
        print()

def main():
    """主函数"""
    try:
        print("\n⚠️  警告：此操作将删除所有现有表和数据！")
        confirm = input("确定要继续吗？(输入 yes 确认): ")
        
        if confirm.lower() != 'yes':
            print("❌ 操作已取消")
            return
        
        rebuilder = ClickHouseTableRebuilder()
        rebuilder.rebuild_tables()
        
    except FileNotFoundError:
        print("❌ 错误: 找不到配置文件 config/clickhouse_config.json")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")

if __name__ == "__main__":
    main()
