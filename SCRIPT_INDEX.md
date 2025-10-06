# Python脚本索引

## 📍### 批量导入工具
| 脚本 | 功能 | 运行方式 |
|-----|------|------|
| `batch_import_all.py` | 批量导入所有数据（快速模式 + HTML报告）✨使用v2.0导入器 | `batch_import.bat` 或 `python scripts\batch_import_all.py` |
| `batch_import_m1.py` | M1数据批量导入 ✨使用v2.0导入器 | `python scripts\batch_import_m1.py` |
| `direct_import_m1.py` | M1数据直接导入 ✨使用v2.0导入器 | `python scripts\direct_import_m1.py` |
### 验证工具
| 脚本 | 功能 | 运行方式 |
|-----|------|------|
| `verify_data_consistency.py` | **CSV与数据库一致性检查（双模式+HTML报告）** | `verify_consistency.bat` 或 `python scripts\verify_data_consistency.py` |on脚本已统### 数据工具
| 脚本 | 功能 | 运行方式 |
|-----|------|------|
| `fxcm_data_downloader.py` | **FXCM数据下载器v2.0** - 命令行参数，灵活配置，自动重试 | `download_fxcm_data.bat` 或 `python scripts\fxcm_data_downloader.py` |
| `fxcm_importer.py` | **FXCM数据导入器v2.0** - 双验证模式(快速/全面)，智能去重，自动配置 | `import_fxcm_data.bat` 或 `python scripts\fxcm_importer.py` |
| `m1_timeframe_converter.py` | **M1时间框架转换器v2.0** - 双模式(本地CSV/数据库SQL)，M1转M5/M15/M30/H1，ClickHouse可选 | `convert_m1_to_multi_timeframes.bat` 或 `python scripts\m1_timeframe_converter.py` |scripts/` | 脚本 | 功能 | 运行方式 |
|-----|------|------|
| `test_clickhouse_connection.py` | 测试数据库连接 | `python scripts\test\test_clickhouse_connection.py` |
| `test_verify_consistency.py` | **测试一致性检查工具（完整测试套件）** | `python scripts\test\test_verify_consistency.py` |
| `test_fxcm_downloader.py` | **测试FXCM下载器（13个测试用例）** | `python scripts\test\test_fxcm_downloader.py` |
| `test_fxcm_importer.py` | **测试FXCM导入器（15个测试用例）** | `python scripts\test\test_fxcm_importer.py` |
| `test_m1_converter.py` | **测试M1转换器（15个测试用例）** | `python scripts\test\test_m1_converter.py` |脚本在 `scripts/test/` 子目录中。

---

## 🚀 核心功能脚本 (scripts/)

### 批量导入工具
| 脚本 | 功能 | 运行方式 |
|-----|------|---------|
| `batch_import_all.py` | 批量导入所有数据（快速模式 + HTML报告） | `batch_import.bat` 或 `python scripts\batch_import_all.py` |
| `batch_import_m1.py` | M1数据批量导入 | `python scripts\batch_import_m1.py` |
| `direct_import_m1.py` | M1数据直接导入 | `python scripts\direct_import_m1.py` |

### 验证工具
| 脚本 | 功能 | 运行方式 |
|-----|------|---------|
| `verify_all_data.py` | 数据质量全面验证（A+评分） | `verify_data.bat` 或 `python scripts\verify_all_data.py` |
| `comprehensive_check.py` | 严格校验导入（详细模式） | `comprehensive_check.bat` 或 `python scripts\comprehensive_check.py` |
| `verify_data_consistency.py` | **CSV与数据库一致性检查（双模式+HTML报告）** | `verify_consistency.bat` 或 `python scripts\verify_data_consistency.py` |
| `verify_data_quality.py` | 数据质量验证 | `python scripts\verify_data_quality.py` |
| `check_data_completeness.py` | 数据完整性检查 | `python scripts\check_data_completeness.py` |

### 数据库管理
| 脚本 | 功能 | 运行方式 |
|-----|------|---------|
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

### 数据工具
| 脚本 | 功能 | 运行方式 |
|-----|------|---------|
| `fxcm_data_downloader.py` | **FXCM数据下载器v2.0** - 命令行参数，灵活配置，自动重试 | `download_fxcm_data.bat` 或 `python scripts\fxcm_data_downloader.py` |
| `m1_timeframe_converter.py` | **M1时间框架转换器v2.0** - 双模式(本地CSV/数据库SQL)，M1转M5/M15/M30/H1，ClickHouse可选 | `convert_m1_to_multi_timeframes.bat` 或 `python scripts\m1_timeframe_converter.py` |

### 核心模块
| 脚本 | 功能 | 说明 |
|-----|------|-----|
| `import_fxcm_to_clickhouse.py` | 数据导入核心类 | 被其他脚本导入使用 |

---

## 🧪 测试脚本 (scripts/test/)

| 脚本 | 功能 | 运行方式 |
|-----|------|---------|
| `test_clickhouse_connection.py` | 测试数据库连接 | `python scripts\test\test_clickhouse_connection.py` |
| `test_verify_consistency.py` | **测试一致性检查工具（完整测试套件）** | `python scripts\test\test_verify_consistency.py` |
| `test_fxcm_downloader.py` | **测试FXCM下载器（13个测试用例）** | `python scripts\test\test_fxcm_downloader.py` |
| `test_m1_converter.py` | **测试M1转换器（15个测试用例）** | `python scripts\test\test_m1_converter.py` |
| `test_output.py` | 测试输出格式 | `python scripts\test\test_output.py` |
| `query_examples.py` | SQL查询示例 | `python scripts\test\query_examples.py` |
| `demo_setup.py` | 演示环境设置 | `python scripts\test\demo_setup.py` |

---

## 🎯 常用操作快捷方式

### 日常维护流程
```powershell
# 1. 导入新数据
batch_import.bat

# 2. 验证数据一致性
verify_consistency.bat

# 3. 启动Web界面查看数据
start_web_ui.bat
```

### 数据库管理
```powershell
# 初次使用：创建数据库表
python scripts\create_clickhouse_tables.py

# 查看数据库表信息
python scripts\view_clickhouse_tables.py

# 重建数据库（慎用！会删除所有数据）
python scripts\rebuild_clickhouse_tables.py
```

### 测试连接
```powershell
# 测试ClickHouse连接
python scripts\test\test_clickhouse_connection.py
```

---

## 📋 脚本分类统计

- **核心功能脚本**: 14个
  - 批量导入: 3个
  - 验证工具: 1个 (verify_data_consistency.py)
  - 数据库管理: 3个
  - Web界面: 5个
  - 数据工具: 3个 (全部v2.0)

- **测试脚本**: 8个
  - 连接测试: 1个
  - 一致性测试: 1个
  - 下载器测试: 1个
  - 导入器测试: 1个
  - 转换器测试: 1个
  - 输出测试: 1个
  - 查询示例: 1个
  - 演示设置: 1个

**总计**: 22个Python脚本

---

## 🔍 按功能快速查找

### 我想...导入数据
- **新版导入器v2.0（推荐）**: `import_fxcm_data.bat` - 双验证模式，智能去重，161K records/sec
- **快速批量导入**: `batch_import.bat` - 自动生成HTML报告
- **导入M1数据**: `python scripts\batch_import_m1.py`

### 我想...验证数据
- **数据一致性验证（推荐）**: `verify_consistency.bat` - 双模式，HTML报告

### 我想...查看数据
- **Web界面查看**: `start_web_ui.bat` (推荐)
- **命令行查看**: `python scripts\view_clickhouse_tables.py`

### 我想...管理数据库
- **创建表**: `python scripts\create_clickhouse_tables.py`
- **重建表**: `python scripts\rebuild_clickhouse_tables.py`
- **测试连接**: `python scripts\test\test_clickhouse_connection.py`

### 我想...下载数据
- **下载FXCM数据**: `download_fxcm_data.bat` - 支持命令行参数，自动重试，跳过已存在文件
- **转换M1为多时间框架**: `convert_m1_to_multi_timeframes.bat` - 双模式：本地CSV(默认)或数据库SQL，M1→M5/M15/M30/H1

---

**最后更新**: 2025-10-05  
**版本**: v5.0.3  
**最新改进**: FXCM数据导入器v2.0 - 双验证模式 + 智能去重 + 161K records/sec性能
