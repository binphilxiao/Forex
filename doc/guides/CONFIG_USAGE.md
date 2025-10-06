# 配置文件使用说明

## 📋 配置文件位置

**主配置文件**: `config/clickhouse_config.json`

## 🔧 配置内容

```json
{
  "host": "192.168.2.168",
  "port": 9000,
  "http_port": 8123,
  "interserver_http_port": 9009,
  "user": "default",
  "password": "YourStrongPassword",
  "database": "forex"
}
```

## ✅ 使用此配置的脚本

### 数据库管理脚本（3个）
1. **clickhouse_configurator.py** - 配置生成器
   - 功能：交互式生成配置文件
   - 运行：`python scripts\clickhouse_configurator.py`
   - 输出：`config/clickhouse_config.json`

2. **create_clickhouse_tables.py** - 创建数据库表
   - 读取：`config/clickhouse_config.json`
   - 默认：`config_path='config/clickhouse_config.json'`

3. **view_clickhouse_tables.py** - 查看数据库信息
   - 读取：`config/clickhouse_config.json`
   - 默认：`config_path='config/clickhouse_config.json'`

### 数据处理脚本（3个）
4. **fxcm_importer.py** - 数据导入器
   - 读取：`config/clickhouse_config.json`
   - 用途：自动获取数据库连接参数

5. **m1_timeframe_converter.py** - 时间框架转换器
   - 读取：`config/clickhouse_config.json`
   - 用途：数据库模式转换时使用

6. **verify_data_consistency.py** - 一致性验证
   - 读取：`config/clickhouse_config.json`
   - 默认：`config_path='config/clickhouse_config.json'`

## 🎯 配置优先级

所有脚本遵循统一的配置优先级：

```
1. 命令行参数（最高优先级）
   ↓
2. 配置文件 (config/clickhouse_config.json)
   ↓
3. 硬编码默认值（最低优先级，仅作备选）
```

## 📝 使用示例

### 首次使用流程

```powershell
# 1. 生成配置文件
python scripts\clickhouse_configurator.py

# 2. 所有脚本自动使用配置
python scripts\create_clickhouse_tables.py
python scripts\fxcm_importer.py
python scripts\verify_data_consistency.py
```

### 使用自定义配置

```powershell
# 某些脚本支持指定配置文件路径
python scripts\create_clickhouse_tables.py --config custom_config.json
```

### 命令行参数覆盖

```powershell
# 命令行参数优先级最高，会覆盖配置文件
python scripts\fxcm_importer.py --ch-host 192.168.1.100 --ch-http-port 8124
```

## ✨ 优势

1. **一次配置，全局使用** - 只需运行一次配置器
2. **无硬编码** - 所有连接参数从配置文件读取
3. **灵活覆盖** - 支持命令行参数临时覆盖
4. **易于维护** - 修改配置文件即可更新所有脚本
5. **安全性** - 敏感信息（密码）集中管理

## 🔒 安全建议

- 不要将 `config/clickhouse_config.json` 提交到公共Git仓库
- 建议添加到 `.gitignore`
- 在生产环境使用强密码

## 📊 配置验证

```powershell
# 测试配置是否正确
python scripts\clickhouse_configurator.py --test-only
```

---

**最后更新**: 2025-10-06
**版本**: v5.0.6
