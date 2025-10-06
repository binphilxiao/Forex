# Python脚本索引

## 📍 快速查找

所有Python脚本已统一放在 `scripts/` 目录下。

---

## 🚀 核心功能脚本 (scripts/)

### 验证工具
| 脚本 | 功能 | 运行方式 |
|-----|------|---------|
| `verify_data_consistency.py` | **CSV与数据库一致性检查（双模式+HTML报告）** | `verify_consistency.bat` 或 `python scripts\verify_data_consistency.py` |

### 数据库管理
| 脚本 | 功能 | 运行方式 |
|-----|------|---------|
| `clickhouse_configurator.py` | **数据库配置工具** - 交互式配置数据库连接，自动测试连接，保存到config/ | `python scripts\clickhouse_configurator.py` |
| `create_clickhouse_tables.py` | 创建数据库表 | `python scripts\create_clickhouse_tables.py` |
| `rebuild_clickhouse_tables.py` | 重建数据库表（删除并重建） | `python scripts\rebuild_clickhouse_tables.py` |
| `view_clickhouse_tables.py` | 查看数据库表信息 | `python scripts\view_clickhouse_tables.py` |

### Web界面
| 脚本 | 功能 | 运行方式 |
|-----|------|---------|
| `start_web.py` | Web服务启动脚本（主要） | `start_web_ui.bat` |
| `flask_app.py` | Flask主应用 | `python scripts\flask_app.py` |
| `fxcm_web_interface.py` | Web界面（完整版） | `python scripts\fxcm_web_interface.py` |
| `fxcm_web_interface_simple.py` | Web界面（简化版） | `python scripts\fxcm_web_interface_simple.py` |
| `run_web_interface.py` | Web启动器（备用） | `python scripts\run_web_interface.py` |

### 数据工具 (v2.0系列)
| 脚本 | 功能 | 运行方式 |
|-----|------|---------|
| `fxcm_data_downloader.py` | **FXCM数据下载器v2.0** - 命令行参数，灵活配置，自动重试 | `download_fxcm_data.bat` 或 `python scripts\fxcm_data_downloader.py` |
| `fxcm_importer.py` | **FXCM数据导入器v2.0** ⭐ - 双验证模式(快速/全面)，智能去重，自动配置，161K records/sec | `import_fxcm_data.bat` 或 `python scripts\fxcm_importer.py` |
| `m1_timeframe_converter.py` | **M1时间框架转换器v2.0** - 双模式(本地CSV/数据库SQL)，M1转M5/M15/M30/H1，ClickHouse可选 | `convert_m1_to_multi_timeframes.bat` 或 `python scripts\m1_timeframe_converter.py` |

### 辅助工具
| 脚本 | 功能 | 运行方式 |
|-----|------|---------|
| `generate_import_report.py` | HTML报告生成器 | 被其他脚本调用 |

---

## 🎯 常用操作快捷方式

### 日常维护流程
```powershell
# 1. 下载新数据
download_fxcm_data.bat

# 2. 导入数据
python scripts\fxcm_importer.py

# 3. 验证数据一致性
verify_consistency.bat

# 4. 启动Web界面查看数据
start_web_ui.bat
```

### 数据库管理
```powershell
# 配置数据库连接（首次使用）
python scripts\clickhouse_configurator.py

# 创建数据库表
python scripts\create_clickhouse_tables.py

# 查看数据库表信息
python scripts\view_clickhouse_tables.py

# 重建数据库（慎用！会删除所有数据）
python scripts\rebuild_clickhouse_tables.py
```

### 高级用法
```powershell
# 自定义导入参数
python scripts\fxcm_importer.py --pairs EURUSD GBPUSD --timeframes M1 --start-year 2024

# 使用全面验证模式
python scripts\fxcm_importer.py --check-mode comprehensive

# 转换M1到其他时间框架
python scripts\m1_timeframe_converter.py --pairs EURUSD --timeframes M5 M15
```

---

## 📋 脚本分类统计

- **核心功能脚本**: 13个
  - 验证工具: 1个
  - 数据库管理: 4个 (含配置工具)
  - Web界面: 5个
  - 数据工具v2.0: 3个
  - 辅助工具: 1个

**总计**: 13个Python脚本

---

## 🔍 按功能快速查找

### 我想...下载数据
- **下载FXCM数据**: `download_fxcm_data.bat`
  - 支持命令行参数
  - 自动重试失败的下载
  - 跳过已存在文件

### 我想...导入数据
- **手动导入**: `python scripts\fxcm_importer.py`
  - 支持自定义参数
  - 可选择货币对、时间框架、年份范围

### 我想...转换数据
- **M1转其他时间框架**: `convert_m1_to_multi_timeframes.bat`
  - 支持M5/M15/M30/H1
  - 双模式：本地CSV或数据库SQL

### 我想...验证数据
- **一致性验证**: `verify_consistency.bat`
  - CSV与数据库对比
  - 双模式验证
  - 生成HTML报告

### 我想...查看数据
- **Web界面（推荐）**: `start_web_ui.bat`
  - 现代化界面
  - 可视化图表
  - 实时查询
- **命令行查看**: `python scripts\view_clickhouse_tables.py`
  - 快速统计信息
  - 表结构查看

### 我想...管理数据库
- **配置数据库连接**: `python scripts\clickhouse_configurator.py` ⭐ - 交互式配置，保存到config/
- **创建表**: `python scripts\create_clickhouse_tables.py`
- **重建表**: `python scripts\rebuild_clickhouse_tables.py`

---

## 📚 v2.0工具链特性

### 🚀 FXCM数据下载器 v2.0
- ✅ 命令行参数支持
- ✅ 自动重试机制
- ✅ 跳过已存在文件
- ✅ 详细日志记录

### 💎 FXCM数据导入器 v2.0 ⭐
- ✅ **双验证模式**：快速(50K/s) | 全面(10K/s)
- ✅ **智能去重**：自动跳过已导入
- ✅ **自动配置**：读取config文件
- ✅ **超高性能**：实测161K records/sec

### 🔄 M1时间框架转换器 v2.0
- ✅ **双模式**：本地CSV | 数据库SQL
- ✅ **多时间框架**：M5/M15/M30/H1
- ✅ **ClickHouse可选**：无强制依赖

### 🔍 数据一致性验证工具
- ✅ **双验证模式**：快速 | 详细
- ✅ **HTML报告**：精美可视化

---

## 🎨 批处理启动器

| 批处理文件 | 对应脚本 | 功能 |
|-----------|---------|------|
| `download_fxcm_data.bat` | fxcm_data_downloader.py | 下载FXCM数据 |
| `import_fxcm_data.bat` | fxcm_importer.py | 导入数据（推荐） |
| `convert_m1_to_multi_timeframes.bat` | m1_timeframe_converter.py | 转换M1时间框架 |
| `verify_consistency.bat` | verify_data_consistency.py | 验证数据一致性 |
| `start_web_ui.bat` | start_web.py | 启动Web界面 |

---

**最后更新**: 2025-10-06  
**版本**: v5.0.4  
**核心改进**: 
- ✨ 全新v2.0工具链（下载、导入、转换）
- 🗑️ 删除所有测试脚本，精简项目结构
- 📊 保留13个核心功能脚本
- ⚡ 161K records/sec 超高性能导入
- 🔧 统一配置管理 - 所有脚本从`config/clickhouse_config.json`读取配置
- 🎯 一次配置，全局使用

