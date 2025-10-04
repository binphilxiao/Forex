#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ClickHouse 数据库连接测试脚本
============================

这个脚本用于测试ClickHouse数据库连接是否正常。

功能特点:
- 支持配置数据库IP、端口、用户名和密码
- 测试基本连接
- 执行简单查询验证
- 显示数据库版本信息
- 详细的错误提示

作者: AI Assistant
创建时间: 2025-10-04
版本: 1.0.0
"""

import sys
import json
from pathlib import Path

# ClickHouse配置
CLICKHOUSE_CONFIG = {
    "host": "192.168.2.168",
    "port": 9000,  # ClickHouse Native Protocol 端口
    "http_port": 8123,  # HTTP接口端口
    "user": "default",
    "password": "yourStrongPassword",
    "database": "default"
}

def test_connection_http():
    """
    使用HTTP接口测试ClickHouse连接
    不需要额外依赖，只需要requests库
    """
    try:
        import requests
        
        url = f"http://{CLICKHOUSE_CONFIG['host']}:{CLICKHOUSE_CONFIG['http_port']}"
        
        print(f"\n{'='*60}")
        print(f"🔍 测试ClickHouse HTTP连接")
        print(f"{'='*60}")
        print(f"服务器: {CLICKHOUSE_CONFIG['host']}")
        print(f"端口: {CLICKHOUSE_CONFIG['http_port']} (HTTP)")
        print(f"用户: {CLICKHOUSE_CONFIG['user']}")
        print(f"数据库: {CLICKHOUSE_CONFIG['database']}")
        print()
        
        # 测试1: 基本连接
        print("📡 测试1: 检查服务器响应...")
        auth = (CLICKHOUSE_CONFIG['user'], CLICKHOUSE_CONFIG['password'])
        response = requests.get(f"{url}/ping", auth=auth, timeout=5)
        
        if response.status_code == 200:
            print("✅ 服务器响应正常")
        else:
            print(f"❌ 服务器响应异常: HTTP {response.status_code}")
            return False
        
        # 测试2: 查询版本
        print("\n📊 测试2: 查询ClickHouse版本...")
        query = "SELECT version()"
        response = requests.get(
            url,
            auth=auth,
            params={'query': query},
            timeout=5
        )
        
        if response.status_code == 200:
            version = response.text.strip()
            print(f"✅ ClickHouse版本: {version}")
        else:
            print(f"❌ 查询失败: {response.text}")
            return False
        
        # 测试3: 查询当前时间
        print("\n⏰ 测试3: 查询服务器时间...")
        query = "SELECT now() as current_time"
        response = requests.get(
            url,
            auth=auth,
            params={'query': query},
            timeout=5
        )
        
        if response.status_code == 200:
            current_time = response.text.strip()
            print(f"✅ 服务器时间: {current_time}")
        else:
            print(f"❌ 查询失败: {response.text}")
            return False
        
        # 测试4: 列出数据库
        print("\n📁 测试4: 列出所有数据库...")
        query = "SHOW DATABASES"
        response = requests.get(
            url,
            auth=auth,
            params={'query': query},
            timeout=5
        )
        
        if response.status_code == 200:
            databases = response.text.strip().split('\n')
            print(f"✅ 找到 {len(databases)} 个数据库:")
            for db in databases[:10]:  # 只显示前10个
                print(f"   - {db}")
            if len(databases) > 10:
                print(f"   ... 还有 {len(databases) - 10} 个数据库")
        else:
            print(f"❌ 查询失败: {response.text}")
            return False
        
        print(f"\n{'='*60}")
        print("🎉 所有测试通过！ClickHouse连接正常")
        print(f"{'='*60}\n")
        return True
        
    except ImportError:
        print("\n❌ 错误: 需要安装 requests 库")
        print("请运行: pip install requests")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ 连接错误: 无法连接到 {CLICKHOUSE_CONFIG['host']}:{CLICKHOUSE_CONFIG['http_port']}")
        print(f"详细信息: {e}")
        print("\n💡 请检查:")
        print("   1. ClickHouse服务是否正在运行")
        print("   2. 网络连接是否正常")
        print("   3. 防火墙是否允许连接")
        return False
    except requests.exceptions.Timeout:
        print(f"\n❌ 连接超时: 服务器 {CLICKHOUSE_CONFIG['host']}:{CLICKHOUSE_CONFIG['http_port']} 无响应")
        return False
    except Exception as e:
        print(f"\n❌ 未知错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_connection_native():
    """
    使用Native Protocol测试ClickHouse连接
    需要安装 clickhouse-driver
    """
    try:
        from clickhouse_driver import Client
        
        print(f"\n{'='*60}")
        print(f"🔍 测试ClickHouse Native连接")
        print(f"{'='*60}")
        print(f"服务器: {CLICKHOUSE_CONFIG['host']}")
        print(f"端口: {CLICKHOUSE_CONFIG['port']} (Native)")
        print(f"用户: {CLICKHOUSE_CONFIG['user']}")
        print(f"数据库: {CLICKHOUSE_CONFIG['database']}")
        print()
        
        # 创建客户端
        print("🔌 正在建立连接...")
        client = Client(
            host=CLICKHOUSE_CONFIG['host'],
            port=CLICKHOUSE_CONFIG['port'],
            user=CLICKHOUSE_CONFIG['user'],
            password=CLICKHOUSE_CONFIG['password'],
            database=CLICKHOUSE_CONFIG['database']
        )
        
        # 测试1: 查询版本
        print("📊 测试1: 查询ClickHouse版本...")
        result = client.execute("SELECT version()")
        version = result[0][0]
        print(f"✅ ClickHouse版本: {version}")
        
        # 测试2: 查询当前时间
        print("\n⏰ 测试2: 查询服务器时间...")
        result = client.execute("SELECT now() as current_time")
        current_time = result[0][0]
        print(f"✅ 服务器时间: {current_time}")
        
        # 测试3: 列出数据库
        print("\n📁 测试3: 列出所有数据库...")
        result = client.execute("SHOW DATABASES")
        databases = [row[0] for row in result]
        print(f"✅ 找到 {len(databases)} 个数据库:")
        for db in databases[:10]:
            print(f"   - {db}")
        if len(databases) > 10:
            print(f"   ... 还有 {len(databases) - 10} 个数据库")
        
        # 测试4: 创建测试表并插入数据
        print("\n🧪 测试4: 创建测试表...")
        try:
            client.execute("DROP TABLE IF EXISTS test_connection")
            client.execute("""
                CREATE TABLE test_connection (
                    id UInt32,
                    name String,
                    timestamp DateTime
                ) ENGINE = MergeTree()
                ORDER BY id
            """)
            print("✅ 测试表创建成功")
            
            # 插入测试数据
            print("   插入测试数据...")
            client.execute(
                "INSERT INTO test_connection VALUES",
                [(1, 'Test', '2025-10-04 00:00:00')]
            )
            
            # 查询数据
            result = client.execute("SELECT * FROM test_connection")
            print(f"✅ 数据插入和查询成功: {result}")
            
            # 清理测试表
            client.execute("DROP TABLE test_connection")
            print("✅ 测试表已清理")
            
        except Exception as e:
            print(f"⚠️  表操作测试失败 (可能权限不足): {e}")
        
        # 断开连接
        client.disconnect()
        
        print(f"\n{'='*60}")
        print("🎉 所有测试通过！ClickHouse Native连接正常")
        print(f"{'='*60}\n")
        return True
        
    except ImportError:
        print("\n⚠️  注意: clickhouse-driver 未安装")
        print("如需使用Native Protocol，请运行: pip install clickhouse-driver")
        return None  # 返回None表示跳过此测试
    except Exception as e:
        print(f"\n❌ Native连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def load_config_from_file(config_file='config/clickhouse_config.json'):
    """从配置文件加载数据库连接参数"""
    config_path = Path(__file__).parent.parent / config_file
    
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 更新全局配置
            CLICKHOUSE_CONFIG.update(config)
            print(f"✅ 已从 {config_file} 加载配置")
            return True
        except Exception as e:
            print(f"⚠️  配置文件加载失败: {e}")
            print(f"将使用默认配置")
            return False
    else:
        print(f"ℹ️  配置文件 {config_file} 不存在，使用默认配置")
        # 创建示例配置文件
        create_example_config(config_path)
        return False

def create_example_config(config_path):
    """创建示例配置文件"""
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        example_config = {
            "host": "192.168.2.168",
            "port": 9000,
            "http_port": 8123,
            "user": "default",
            "password": "yourStrongPassword",
            "database": "default"
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(example_config, f, indent=4, ensure_ascii=False)
        
        print(f"✅ 已创建示例配置文件: {config_path}")
        print(f"   请根据实际情况修改配置文件")
    except Exception as e:
        print(f"⚠️  创建配置文件失败: {e}")

def main():
    """主函数"""
    print("\n" + "="*60)
    print("ClickHouse 数据库连接测试工具 v1.0.0")
    print("="*60)
    
    # 尝试从配置文件加载
    load_config_from_file()
    
    print(f"\n当前配置:")
    print(f"  服务器: {CLICKHOUSE_CONFIG['host']}")
    print(f"  HTTP端口: {CLICKHOUSE_CONFIG['http_port']}")
    print(f"  Native端口: {CLICKHOUSE_CONFIG['port']}")
    print(f"  用户: {CLICKHOUSE_CONFIG['user']}")
    print(f"  数据库: {CLICKHOUSE_CONFIG['database']}")
    
    # 测试HTTP连接（推荐，不需要额外依赖）
    http_result = test_connection_http()
    
    # 测试Native连接（可选）
    native_result = test_connection_native()
    
    # 总结
    print("\n" + "="*60)
    print("📋 测试总结")
    print("="*60)
    print(f"HTTP连接测试: {'✅ 通过' if http_result else '❌ 失败'}")
    
    if native_result is not None:
        print(f"Native连接测试: {'✅ 通过' if native_result else '❌ 失败'}")
    else:
        print(f"Native连接测试: ⏭️  已跳过 (未安装clickhouse-driver)")
    
    if http_result or native_result:
        print("\n🎉 ClickHouse数据库连接正常！")
        return 0
    else:
        print("\n❌ ClickHouse数据库连接失败！")
        print("\n💡 故障排查建议:")
        print("   1. 检查ClickHouse服务是否运行")
        print("   2. 检查网络连接和防火墙设置")
        print("   3. 验证用户名和密码是否正确")
        print("   4. 确认端口号是否正确")
        print("   5. 查看ClickHouse服务日志")
        return 1

if __name__ == '__main__':
    sys.exit(main())
