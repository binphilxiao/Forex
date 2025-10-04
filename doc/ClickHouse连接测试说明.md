# ClickHouse 数据库连接测试

## 📋 功能说明

这个工具用于测试ClickHouse数据库连接是否正常，支持：
- HTTP接口连接测试（推荐，无需额外依赖）
- Native Protocol连接测试（可选，需要安装驱动）
- 可配置的连接参数
- 详细的测试报告

## 🚀 快速开始

### 方法1: 使用批处理文件（推荐）

双击运行：
```
测试ClickHouse连接.bat
```

### 方法2: 命令行运行

```powershell
python scripts\test_clickhouse_connection.py
```

## ⚙️ 配置说明

### 配置文件位置

`config/clickhouse_config.json`

### 配置参数

```json
{
    "host": "192.168.2.168",      // ClickHouse服务器IP
    "port": 9000,                  // Native Protocol端口
    "http_port": 8123,             // HTTP接口端口
    "user": "default",             // 用户名
    "password": "yourStrongPassword", // 密码
    "database": "default"          // 默认数据库
}
```

### 端口说明

根据你的截图，ClickHouse开放了以下端口：
- **8123** - HTTP接口（推荐使用）
- **9000** - Native Protocol（需要clickhouse-driver）
- **9009** - 跨服务器复制端口

本脚本主要使用 **8123 (HTTP)** 和 **9000 (Native)** 端口。

## 📦 依赖安装

### 基本功能（仅HTTP测试）

只需要 `requests` 库：

```powershell
pip install requests
```

### 完整功能（包括Native测试）

```powershell
pip install requests clickhouse-driver
```

## 🧪 测试内容

脚本会执行以下测试：

### HTTP连接测试
1. ✅ 检查服务器响应
2. ✅ 查询ClickHouse版本
3. ✅ 查询服务器时间
4. ✅ 列出所有数据库

### Native连接测试（可选）
1. ✅ 建立Native连接
2. ✅ 查询ClickHouse版本
3. ✅ 查询服务器时间
4. ✅ 列出所有数据库
5. ✅ 创建测试表并插入数据

## 📊 测试输出示例

```
============================================================
ClickHouse 数据库连接测试工具 v1.0.0
============================================================

当前配置:
  服务器: 192.168.2.168
  HTTP端口: 8123
  Native端口: 9000
  用户: default
  数据库: default

============================================================
🔍 测试ClickHouse HTTP连接
============================================================
服务器: 192.168.2.168
端口: 8123 (HTTP)
用户: default
数据库: default

📡 测试1: 检查服务器响应...
✅ 服务器响应正常

📊 测试2: 查询ClickHouse版本...
✅ ClickHouse版本: 23.8.2.7

⏰ 测试3: 查询服务器时间...
✅ 服务器时间: 2025-10-04 15:30:45

📁 测试4: 列出所有数据库...
✅ 找到 5 个数据库:
   - default
   - system
   - INFORMATION_SCHEMA
   - information_schema
   - _temporary_and_external_tables

============================================================
🎉 所有测试通过！ClickHouse连接正常
============================================================
```

## 🔧 修改配置

### 方法1: 编辑配置文件

编辑 `config/clickhouse_config.json`：

```json
{
    "host": "你的服务器IP",
    "port": 9000,
    "http_port": 8123,
    "user": "你的用户名",
    "password": "你的密码",
    "database": "你的数据库"
}
```

### 方法2: 修改脚本默认值

编辑 `scripts/test_clickhouse_connection.py`，修改 `CLICKHOUSE_CONFIG` 字典：

```python
CLICKHOUSE_CONFIG = {
    "host": "你的服务器IP",
    "port": 9000,
    "http_port": 8123,
    "user": "你的用户名",
    "password": "你的密码",
    "database": "你的数据库"
}
```

## 🐛 故障排查

### 连接失败

如果连接失败，请检查：

1. **ClickHouse服务是否运行**
   ```bash
   # 在ClickHouse服务器上检查
   systemctl status clickhouse-server
   ```

2. **网络连接**
   ```powershell
   # 测试网络连通性
   ping 192.168.2.168
   
   # 测试端口是否开放
   Test-NetConnection -ComputerName 192.168.2.168 -Port 8123
   ```

3. **防火墙设置**
   - 确保防火墙允许8123和9000端口

4. **用户名和密码**
   - 验证用户名: `default`
   - 验证密码: `yourStrongPassword`

5. **ClickHouse配置**
   - 检查 `/etc/clickhouse-server/config.xml`
   - 确保监听正确的IP和端口

### 权限问题

如果表操作测试失败，可能是权限不足：

```sql
-- 在ClickHouse中授予权限
GRANT ALL ON *.* TO default;
```

## 💡 使用建议

1. **首次使用**
   - 先安装 `requests` 库
   - 修改配置文件中的连接参数
   - 运行测试脚本

2. **生产环境**
   - 使用配置文件管理连接参数
   - 不要在代码中硬编码密码
   - 使用专用用户账号，不要使用default

3. **定期测试**
   - 部署后测试连接
   - 维护时验证连接
   - 故障排查时快速诊断

## 📚 相关文档

- [ClickHouse官方文档](https://clickhouse.com/docs/)
- [ClickHouse HTTP接口](https://clickhouse.com/docs/en/interfaces/http/)
- [Python Driver](https://github.com/mymarilyn/clickhouse-driver)

## 🔗 端口参考

根据ClickHouse标准配置：

| 端口 | 协议 | 用途 |
|------|------|------|
| 8123 | HTTP | HTTP接口（推荐） |
| 9000 | TCP | Native Protocol |
| 9009 | TCP | 跨服务器复制 |
| 9004 | TCP | MySQL兼容协议 |
| 5432 | TCP | PostgreSQL兼容协议 |

---

**创建时间**: 2025-10-04  
**版本**: 1.0.0  
**作者**: AI Assistant
