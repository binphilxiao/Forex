# Forex Data Management System - Project Structure

## 📁 Root Directory

```
Forex/
├── 📄 Root Files (根目录 - 启动脚本)
│   ├── batch_import.bat            # 批量导入启动器
│   ├── verify_data.bat             # 数据验证启动器
│   ├── comprehensive_check.bat     # 严格校验启动器
│   ├── start_web_ui.bat            # Web界面启动器
│   ├── README.md                   # 项目说明
│   ├── QUICKSTART.md               # 快速开始指南
│   ├── PROJECT_STRUCTURE.md        # 项目结构文档
│   ├── CHANGELOG_FILE_RENAME.md    # 文件重命名日志
│   ├── requirements.txt            # Python依赖
│   └── .gitignore                  # Git忽略配置
│
├── 📂 config/                      # 配置文件
│   └── clickhouse_config.json      # ClickHouse数据库配置
│
├── 📂 scripts/                     # Python脚本库
│   ├── 🔧 Core Scripts (核心功能)
│   │   ├── import_fxcm_to_clickhouse.py  # 数据导入核心类
│   │   ├── batch_import_all.py           # 批量导入所有数据
│   │   ├── verify_all_data.py            # 数据质量验证
│   │   ├── comprehensive_check.py        # 严格校验导入
│   │   ├── batch_import_m1.py            # M1数据批量导入
│   │   └── direct_import_m1.py           # M1数据直接导入
│   │
│   ├── 💾 Database Tools (数据库工具)
│   │   ├── create_clickhouse_tables.py   # 创建数据库表
│   │   ├── rebuild_clickhouse_tables.py  # 重建数据库表
│   │   ├── view_clickhouse_tables.py     # 查看数据库表
│   │   ├── verify_data_quality.py        # 数据质量验证
│   │   └── check_data_completeness.py    # 数据完整性检查
│   │
│   ├── 🌐 Web Interface (Web界面)
│   │   ├── flask_app.py                  # Flask主应用
│   │   ├── fxcm_web_interface.py         # Web界面
│   │   ├── fxcm_web_interface_simple.py  # 简化Web界面
│   │   ├── run_web_interface.py          # Web启动器
│   │   └── start_web.py                  # Web启动脚本
│   │
│   ├── 📥 Data Tools (数据工具)
│   │   ├── download_fxcm_candles.py      # 下载FXCM数据
│   │   └── convert_m1_to_multi_timeframes.py  # 时间周期转换
│   │
│   └── 🧪 test/ (测试脚本)
│       ├── test_clickhouse_connection.py # 连接测试
│       ├── test_output.py                # 输出测试
│       ├── query_examples.py             # 查询示例
│       └── demo_setup.py                 # 演示设置
│
├── 📂 doc/                         # 文档目录
│   ├── 导入模式说明.md             # 快速/详细模式说明
│   ├── 一键脚本使用指南.md         # 使用指南
│   └── DATABASE_SCHEMA.md          # 数据库结构文档
│
├── 📂 templates/                   # Web界面模板
│   └── (HTML模板文件)
│
├── 📂 fxcm_data/                   # FXCM原始数据
│   ├── AUDUSD/
│   │   ├── D1/                     # 日线数据
│   │   └── M1/                     # 分钟数据
│   ├── EURUSD/
│   ├── GBPUSD/
│   ├── USDJPY/
│   ├── USDCAD/
│   └── USDCHF/
│
├── 📂 logs/                        # 日志文件
│   ├── import_log_*.txt            # 导入日志
│   ├── verification_report_*.txt   # 验证报告
│   └── download_*.log              # 下载日志
│
└── 📂 .venv/                       # Python虚拟环境 (gitignore)
```

---

## 🚀 Quick Start Scripts

### 1. 快速批量导入 (Fast Batch Import)
```bash
# Windows
batch_import.bat

# 或直接运行
python scripts\batch_import_all.py
```
- **功能**: 使用快速模式导入所有数据
- **速度**: ~3分钟 (3332个文件)
- **模式**: 只检查首尾记录

### 2. 数据质量验证 (Data Verification)
```bash
# Windows
verify_data.bat

# 或直接运行
python scripts\verify_all_data.py
```
- **功能**: 全面检查数据质量
- **速度**: ~1分钟
- **输出**: A+评分报告

### 3. 严格校验导入 (Comprehensive Check)
```bash
# Windows
comprehensive_check.bat

# 或直接运行
python scripts\comprehensive_check.py
```
- **功能**: 逐条验证每个记录
- **适用**: 修复特定数据问题
- **模式**: 交互式选择文件

### 4. Web界面 (Web UI)
```bash
start_web_ui.bat
```
- **功能**: 启动数据查询Web界面
- **端口**: http://localhost:5000

---

## 📂 Directory Details

### `/config/` - 配置文件
- `clickhouse_config.json`: 数据库连接配置

### `/scripts/` - 核心脚本
所有Python脚本统一放在此目录，按功能分类：

- **核心类**: `import_fxcm_to_clickhouse.py`
  - `FXCMDataImporter`: 数据导入主类
  - 支持快速/详细两种检查模式
  
- **批量导入工具**:
  - `batch_import_all.py`: 全部数据快速导入
  - `batch_import_m1.py`: M1数据批量导入
  - `direct_import_m1.py`: M1数据直接导入
  
- **验证工具**:
  - `verify_all_data.py`: 数据质量全面验证
  - `comprehensive_check.py`: 严格校验导入
  - `check_data_completeness.py`: 数据完整性检查
  - `verify_data_quality.py`: 数据质量验证

- **数据库工具**:
  - `create_clickhouse_tables.py`: 创建数据库表
  - `rebuild_clickhouse_tables.py`: 重建数据库表
  - `view_clickhouse_tables.py`: 查看数据库表

- **Web界面**:
  - `flask_app.py`: Flask主应用
  - `fxcm_web_interface.py`: 完整Web界面
  - `fxcm_web_interface_simple.py`: 简化Web界面
  - `run_web_interface.py`: Web启动器
  - `start_web.py`: Web启动脚本

- **数据工具**:
  - `download_fxcm_candles.py`: 下载FXCM数据
  - `convert_m1_to_multi_timeframes.py`: 时间周期转换

### `/scripts/test/` - 测试脚本
测试和示例脚本，不参与生产环境：
  - `test_clickhouse_connection.py`: 连接测试
  - `test_output.py`: 输出测试
  - `query_examples.py`: 查询示例
  - `demo_setup.py`: 演示设置

### `/doc/` - 文档
- `导入模式说明.md`: 快速vs详细模式对比
- `一键脚本使用指南.md`: 详细使用说明
- `DATABASE_SCHEMA.md`: 数据库结构

### `/fxcm_data/` - 原始数据
- 6个货币对的CSV文件
- 按货币对/时间周期/年份组织

### `/logs/` - 日志输出
- 所有导入/验证日志
- 自动生成时间戳

---

## 🔧 File Naming Convention

### 主脚本命名规则:
- `batch_*.py`: 批量处理脚本
- `verify_*.py`: 验证检查脚本
- `comprehensive_*.py`: 详细/深度处理脚本
- `start_*.bat`: 启动脚本

### 日志文件命名:
- `import_log_YYYYMMDD_HHMMSS.txt`
- `verification_report_YYYYMMDD_HHMMSS.txt`
- `comprehensive_check_YYYYMMDD_HHMMSS.txt`

---

## 📊 Data Flow

```
CSV Files (fxcm_data/)
    ↓
batch_import_all.py (快速模式)
    ↓
ClickHouse Database
    ↓
verify_all_data.py (质量检查)
    ↓
comprehensive_check.py (问题修复)
```

---

## 🎯 Best Practices

### 日常维护流程:
1. `batch_import.bat` - 导入新数据 (~3分钟)
2. `verify_data.bat` - 验证质量 (~1分钟)
3. 如发现问题: `comprehensive_check.bat`

### 文件管理:
- ✅ 所有Python脚本统一放在 `/scripts/`
- ✅ 测试脚本放在 `/scripts/test/`
- ✅ 启动器（.bat）放在根目录（方便运行）
- ✅ 日志自动保存到 `/logs/`
- ✅ 配置文件集中在 `/config/`
- ✅ 文档放在 `/doc/`

### 脚本调用规范:
```bash
# 从根目录运行启动器
batch_import.bat

# 或直接调用Python脚本
python scripts\batch_import_all.py

# 测试脚本
python scripts\test\test_clickhouse_connection.py
```

---

## 📝 Version History

- **v4.1.0** (2025-10-04)
  - 📁 **重大重构**: 所有Python脚本移至 `/scripts/`
  - 🧪 测试脚本单独放在 `/scripts/test/`
  - 🚀 根目录保留启动器（.bat文件）
  - 📋 更新所有批处理文件路径
  - 📚 完善项目结构文档

- **v4.0.0** (2025-10-04)
  - ✨ 文件重命名为英文
  - 📁 优化文件夹结构
  - ⚡ 快速导入模式 (10-20倍速度提升)
  - 🔍 严格校验工具
  - 📊 完善文档体系
