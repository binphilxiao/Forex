# FXCM 外汇数据管理系统

<div align="center">

**一站式外汇历史数据下载、导入、验证和分析解决方案**

![Version](https://img.shields.io/badge/version-5.0.6-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20MacOS-lightgrey.svg)

</div>

---

## 📋 项目简介

FXCM 外汇数据管理系统是一个功能完整的数据处理平台，提供从数据下载、数据库导入、数据验证到可视化分析的全流程解决方案。

### 🎯 核心功能

- **📥 数据下载** - 自动下载FXCM历史数据（2015-2025，10年数据）
- **💾 数据库导入** - 快速导入ClickHouse数据库（10-20倍速度提升）
- **✅ 数据验证** - 多级数据质量检查（A+评分系统）
- **� 一致性验证** - CSV与数据库数据一致性验证（双模式）
- **�📊 可视化报告** - 精美的HTML报告（数据完整性、导入统计、一致性）
- **🌐 Web界面** - 现代化的Flask Web管理界面
- **⚡ 智能检查** - 快速模式和详细模式双重验证

---

## ✨ v5.0.6 最新更新

### � 文档重组
- **文档分类整理** - 所有文档移至 `doc/` 目录并分类
- **快速开始指南** - 全新的 `QUICKSTART.md` 5分钟上手
- **文档索引** - `doc/README.md` 提供完整文档导航
- **精简根目录** - 仅保留 README.md, QUICKSTART.md, requirements.txt

### 🗑️ 项目精简
- **删除冗余脚本** - 移除 `rebuild_clickhouse_tables.py` 等危险操作
- **核心脚本减至9个** - 专注核心功能，提高可维护性
- **文档分类**: 
  - `doc/guides/` - 使用指南
  - `doc/reference/` - 参考文档
  - `doc/development/` - 开发文档

### �🔧 统一配置管理
- **集中配置** - 所有脚本从 `config/clickhouse_config.json` 读取配置
- **一次配置，全局使用** - 运行配置器后，所有脚本自动使用配置
- **配置优先级** - 命令行参数 > 配置文件 > 默认值
- **6个脚本使用配置** - 数据库和数据处理脚本全覆盖

### 🎯 配置器工具
```powershell
# 首次使用：配置数据库连接
python scripts\clickhouse_configurator.py

# 之后所有脚本自动使用配置
python scripts\fxcm_importer.py          # 自动读取配置
python scripts\m1_timeframe_converter.py # 自动读取配置
python scripts\verify_data_consistency.py # 自动读取配置
```

---

## ✨ v5.0.3 功能特性

### 💎 FXCM数据导入器 v2.0
- **双重验证模式** - 快速模式（50K records/sec）和全面模式（10K records/sec）
- **智能去重检测** - 自动跳过已导入文件
- **配置文件支持** - 自动读取ClickHouse配置，无需手动输入密码
- **超高性能** - 实测161K records/sec，超出目标3倍

### 🔍 数据一致性验证工具
- **双模式验证** - 快速模式（默认）和详细模式
- **HTML可视化报告** - 精美的渐变设计报告界面
- **终端彩色输出** - 实时进度和彩色状态标记
- **验证结果** - 98.7%一致性（3,290/3,332文件）

---

## ✨ v5.0.0 重大更新

### 🚀 性能提升
- **快速导入模式** - 仅检查首尾记录，速度提升10-20倍（3分钟 vs 30-60分钟）
- **智能跳过** - 自动识别已导入数据，避免重复处理
- **批量处理** - 一次性处理3,332个文件，导入2650万条记录

### 📊 HTML报告系统
- **导入报告** - 自动生成精美的导入统计报告
- **完整性报告** - 数据完整性可视化分析
- **进度追踪** - 按货币对分类的详细统计
- **状态标记** - 四种状态一目了然（✅已导入/⏭️已跳过/❌错误/ℹ️空文件）

### 🔧 双模式检查
- **快速模式（默认）** - 只检查文件首尾记录，适合日常导入
- **详细模式** - 逐条验证每个记录，适合问题排查

### 📁 项目结构优化
- **统一脚本管理** - 所有Python脚本集中在`scripts/`目录
- **测试脚本分离** - 测试代码独立在`scripts/test/`
- **文档完善** - 详细的使用指南和索引文档

---

## 🚀 快速开始

### 方式一：使用批处理启动器（推荐）

Windows用户可直接双击运行：

```
verify_consistency.bat  # 数据一致性验证
start_web_ui.bat       # 启动Web界面
```

### 方式二：Python命令行

```powershell
# 1. 批量导入数据（快速模式 + HTML报告）
python scripts\batch_import_all.py

# 2. 验证数据质量
python scripts\verify_all_data.py

# 3. 详细校验（交互式）
python scripts\comprehensive_check.py

# 4. 数据一致性验证（CSV vs ClickHouse）
python scripts\verify_data_consistency.py

# 5. 启动Web界面
python scripts\start_web.py
```

### 方式三：Web界面操作

```powershell
# 启动Web服务
start_web_ui.bat

# 浏览器访问
http://localhost:5000
```

Web界面支持：
- 📥 下载FXCM数据
- 💾 导入到ClickHouse
- 📊 数据完整性分析
- ⚙️ 灵活的配置选项

---

## 🌟 功能特点

### 1. 数据下载

- **多货币对** - 支持EURUSD、GBPUSD、USDJPY、AUDUSD、USDCAD、USDCHF
- **多时间周期** - M1、M5、M15、M30、H1、D1
- **长时间跨度** - 2015-2025年（10年历史数据）
- **智能跳过** - 自动检测已存在文件
- **失败重试** - 404错误自动重试5次
- **详细日志** - 每次运行独立时间戳日志

### 2. ClickHouse数据库导入

#### ⚡ 快速模式（默认）
- **速度提升** - 10-20倍性能提升（3分钟 vs 30-60分钟）
- **智能检查** - 只验证文件首尾记录
- **自动跳过** - 数据完整则跳过整个文件
- **HTML报告** - 自动生成导入统计报告

#### 🔍 详细模式
- **逐条验证** - 检查每个记录是否存在
- **精确定位** - 找出具体的缺失数据
- **问题修复** - 适合修复特定数据问题
- **交互选择** - 可选择特定文件检查

### 3. 数据验证

#### 五级质量检查
1. **完整性检查** - 验证所有预期文件是否存在
2. **时间连续性** - 检查数据时间戳连续性
3. **价格合理性** - 验证OHLC价格关系
4. **数据量统计** - 统计各货币对记录数
5. **质量评分** - A+到F的评分系统

#### 验证报告
- 📊 HTML可视化报告
- 📝 详细的文本报告
- 🏆 A+评分系统
- 📈 数据质量趋势

### 4. 可视化报告

#### 导入报告（import_report_*.html）
- 总体统计（文件数、记录数、耗时、速度）
- 按货币对分类统计
- D1/M1数据详情
- 状态标记和进度条
- 模式说明

#### 完整性报告（fxcm_data_report_*.html）
- 文件完整率统计
- 按年/周热力图矩阵
- 缺失数据详细列表
- 货币对对比分析

---

## 📁 项目结构

```
Forex/
├── 📄 启动器（根目录）
│   ├── start_web_ui.bat           # Web界面
│   └── README.md                   # 本文档
│
├── 📂 scripts/（Python脚本）
│   ├── 🔧 核心功能
│   │   ├── batch_import_all.py          # 批量导入（快速模式）
│   │   ├── verify_all_data.py           # 数据验证
│   │   ├── comprehensive_check.py       # 详细校验
│   │   ├── import_fxcm_to_clickhouse.py # 导入核心类
│   │   └── generate_import_report.py    # HTML报告生成
│   │
│   ├── 💾 数据库工具
│   │   ├── create_clickhouse_tables.py  # 创建表
│   │   ├── rebuild_clickhouse_tables.py # 重建表
│   │   └── view_clickhouse_tables.py    # 查看表
│   │
│   ├── 📥 数据工具
  │   │   ├── fxcm_data_downloader.py      # 数据下载器v2.0
│   │   ├── convert_m1_to_multi_timeframes.py # 时间周期转换
│   │   └── check_data_completeness.py   # 数据完整性检查
│   │
│   ├── 🌐 Web界面
│   │   ├── flask_app.py                 # Flask应用
│   │   └── start_web.py                 # Web启动器
│   │
│   └── 🧪 test/（测试脚本）
│       ├── test_clickhouse_connection.py
│       ├── query_examples.py
│       └── demo_setup.py
│
├── 📂 config/（配置文件）
│   ├── clickhouse_config.json      # ClickHouse配置
│   └── download_config.json        # 下载配置
│
├── 📂 doc/（文档）
│   ├── HTML_REPORT_GUIDE.md        # HTML报告指南
│   ├── DATABASE_SCHEMA.md          # 数据库结构
│   └── 导入模式说明.md
│
├── 📂 logs/（日志和报告）
│   ├── import_report_*.html        # 导入报告
│   ├── fxcm_data_report_*.html    # 完整性报告
│   ├── import_log_*.txt           # 导入日志
│   └── verification_report_*.txt   # 验证报告
│
├── 📂 fxcm_data/（原始数据）
│   ├── EURUSD/
│   │   ├── M1/  # 分钟数据
│   │   └── D1/  # 日线数据
│   ├── GBPUSD/
│   └── ...
│
└── 📂 templates/（Web模板）
    └── index.html

```

---
```

## 💻 环境要求

### 系统要求
- **操作系统** - Windows / Linux / MacOS
- **Python** - 3.7 或更高版本
- **内存** - 建议 8GB 以上
- **磁盘空间** - 约 50GB（完整10年数据）

### Python依赖

```
pandas>=1.3.0
requests>=2.25.0
flask>=2.0.0
clickhouse-driver>=0.2.0
```

### ClickHouse数据库

- **版本** - ClickHouse 21.0 或更高
- **推荐配置** - 独立服务器或Docker部署
- **连接方式** - HTTP接口（默认8123端口）

---

## 🔧 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/binphilxiao/Forex.git
cd Forex
```

### 2. 创建虚拟环境（推荐）

```powershell
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```powershell
pip install -r requirements.txt
```

### 4. 配置ClickHouse

编辑 `config/clickhouse_config.json`:

```json
{
  "host": "localhost",
  "http_port": 8123,
  "native_port": 9000,
  "database": "forex_data",
  "user": "default",
  "password": ""
}
```

### 5. 创建数据库表

```powershell
python scripts\create_clickhouse_tables.py
```

### 6. 开始使用

```powershell
# 方式一：Python脚本（推荐）
python scripts\fxcm_importer.py

# 方式二：Web界面
start_web_ui.bat
```

---

所有 CSV 文件包含以下列：

| 列名 | 说明 |
|------|------|
| DateTime | 时间戳（格式：YYYY-MM-DD HH:MM:SS） |
| Open | 开盘价 |
| High | 最高价 |
| Low | 最低价 |
| Close | 收盘价 |

**注意**：
- 数据源自 FXCM 的 Bid（买入）价格，列名已从 `BidOpen`, `BidHigh`, `BidLow`, `BidClose` 重命名为标准 OHLC 格式
- 不包含 Volume 列，仅保留 OHLC 价格数据
- 所有时间周期的数据格式保持一致

## 日志系统

### 日志文件

- **位置**：`logs/download_YYYYMMDD_HHMMSS.log`
- **命名规则**：每次运行生成独立的时间戳日志文件
- **内容**：记录下载成功的文件和最终失败的 404 错误（经过 5 次重试）

### 日志级别

- `INFO`：正常的下载操作
  - `✅ 下载成功`：成功下载并保存文件
  - `❌ 404错误（重试5次后）`：重试 5 次后仍然失败的下载

### 示例日志

```
2025-10-03 11:05:07,421 - INFO - 日志文件: logs\download_20251003_110507.log
2025-10-03 11:05:10,731 - INFO - ❌ 404错误（重试5次后）: https://candledata.fxcorporate.com/m1/EURUSD/2019/1.csv.gz
2025-10-03 11:05:13,961 - INFO - ✅ 下载成功: https://candledata.fxcorporate.com/m1/EURUSD/2023/27.csv.gz (0 条记录)
```

## 数据源说明

### API 端点

脚本从 FXCM 公开 API 下载数据：

- **M1 数据**：`https://candledata.fxcorporate.com/m1/{货币对}/{年份}/{周数}.csv.gz`
- **D1 数据**：`https://candledata.fxcorporate.com/D1/{货币对}/{年份}.csv.gz`

### 数据可用性

⚠️ **重要提示**：

1. **不是所有周次的数据都存在**
   - 第 1 周和第 53 周经常返回 404（年份边界问题）
   - 某些历史时期的数据可能缺失
   
2. **最近年份可能不完整**
   - 当前年份（2025）的数据可能尚未完全发布
   - 2022-2025 年的某些货币对数据可能缺失

3. **数据更新**
   - FXCM 会定期更新历史数据
   - 建议定期运行脚本以获取最新数据

## 错误处理

### 404 错误

脚本对 404 错误（数据不存在）实施 5 次重试机制：

1. 第一次请求失败后，等待 0.5 秒
2. 重试最多 5 次
3. 如果 5 次都失败，记录到日志并跳过

### 其他错误

- **网络错误**：同样会重试 5 次
- **解析错误**：记录错误并跳过该文件
- **磁盘错误**：脚本会自动创建所需的目录结构

## 性能优化

### 跳过已存在文件

脚本会检查文件是否已存在：

```python
if output_path.exists():
    print(f"  Week {week}/52... ⏭️ 已存在，跳过")
    return True
```

这大大减少了重复运行的时间。

### 下载速度

- 单个文件下载时间：约 0.5-2 秒
- 完整下载（所有货币对，10年数据）：约 2-4 小时（首次运行）
- 增量更新：几分钟内完成

## 常见问题

### Q1: 为什么有些周的数据显示 404 错误？

**A**: 这是正常现象。FXCM 并非所有周次都有数据，特别是：
- 每年的第 1 周和第 53 周
- 市场休市期间
- 历史数据缺失期

脚本会自动跳过这些不存在的数据。

### Q2: 如何只下载特定货币对的数据？

**A**: 修改脚本中的 `INSTRUMENTS` 列表：

```python
INSTRUMENTS = ['EURUSD']  # 只下载 EURUSD
```

### Q3: 可以下载其他时间周期吗（如 H1, H4）？

**A**: 
- **已支持**：M1、M5、M15、M30、H1、D1
- **M5、M15、M30、H1** 通过 `convert_m1_to_multi_timeframes.py` 从M1数据转换生成
- **H4、H8、D1** 等其他周期需要从现有数据进一步转换或通过其他API获取

### Q4: 下载的数据包含 Ask 价格吗？

**A**: 不包含。数据仅包含 Bid（买入）价格。如需 Ask 价格，需要查阅 FXCM 的其他数据源。

### Q5: 如何验证下载的数据是否完整？

**A**: 可以检查日志文件中的 404 错误数量，以及与预期的数据文件进行对比。正常情况下，每年应有约 45-50 周的 M1 数据。

### Q6: 多时间周期转换需要多长时间？

**A**: 
- **单个货币对单年**：约2-5分钟
- **全部6个货币对10年数据**：约2-4小时
- **转换速度**：取决于原始M1数据的大小和系统性能
- **建议**：可以先转换部分数据测试效果

### Q7: 转换后的数据质量如何保证？

**A**: 
- **严格时间对齐**：所有时间周期都对齐到标准边界
- **标准OHLC聚合**：使用行业标准的开高低收聚合方法
- **数据完整性检查**：转换过程中验证数据连续性
- **压缩比验证**：实时显示压缩比确保转换正确性

### Q8: 可以只转换特定时间周期吗？

**A**: 可以修改 `convert_m1_to_multi_timeframes.py` 中的 `timeframes` 配置，选择需要的时间周期：

```python
self.timeframes = {
    'M5': {'minutes': 5},     # 只转换M5
    # 'M15': {'minutes': 15}, # 注释掉不需要的
    # 'M30': {'minutes': 30},
    # 'H1': {'minutes': 60}
}
```

## 数据完整性检查

### 数据检查脚本：check_data_completeness.py

除了数据下载功能，项目还提供了一个完整的数据完整性检查工具：

```powershell
python check_data_completeness.py
```

### 检查功能特点

- ✅ **全面扫描**：检查所有货币对的M1、M5、M15、M30、H1和D1数据完整性
- ✅ **统计分析**：计算文件大小、记录数量和完整率
- ✅ **可视化报告**：生成现代化的HTML可视化报告
- ✅ **多时间周期热力图**：各个时间周期数据按年/周的完整性矩阵
- ✅ **缺失分析**：详细列出所有缺失的数据文件
- ✅ **JSON导出**：提供机器可读的详细数据报告

### 生成的报告文件

所有报告文件都会生成到 `logs/` 目录中：

- `logs/fxcm_data_report_YYYYMMDD_HHMMSS.html` - 可视化HTML报告
- `logs/fxcm_data_report_YYYYMMDD_HHMMSS.json` - 详细JSON数据报告
- `logs/data_check_YYYYMMDD_HHMMSS.log` - 检查过程日志

### 报告内容

1. **总体统计**：文件数量、完整率、总记录数、数据大小
2. **货币对分析**：每个货币对的详细统计和完整度
3. **时间完整性**：M1数据的年/周热力图矩阵
4. **缺失列表**：所有缺失数据的详细路径

## M1多时间周期数据转换

### 数据转换脚本：convert_m1_to_multi_timeframes.py

项目提供了将1分钟(M1)数据转换为多个高级时间周期数据的功能：

```powershell
python convert_m1_to_multi_timeframes.py
```

### 支持的时间周期

- **M5**：5分钟数据（5:1压缩比）
- **M15**：15分钟数据（15:1压缩比）
- **M30**：30分钟数据（30:1压缩比）
- **H1**：60分钟数据（60:1压缩比）

### 转换功能特点

- ✅ **多时间周期**：一次转换生成M5、M15、M30、H1四个时间周期
- ✅ **精确聚合**：严格按照时间窗口边界聚合OHLC数据
- ✅ **格式保持**：生成的数据保持与M1数据完全相同的列格式（不含Volume）
- ✅ **批量转换**：支持所有货币对和年份的批量转换
- ✅ **跳过重复**：自动跳过已存在的文件，支持增量转换
- ✅ **详细日志**：记录转换过程、压缩比和统计信息
- ✅ **时间对齐**：严格按照时间边界对齐（如5分钟边界：00:00, 00:05, 00:10...）

### 聚合规则

所有时间周期的聚合都遵循标准的OHLC规则：

- **Open (开盘价)**：时间窗口内第一个M1记录的开盘价
- **High (最高价)**：时间窗口内所有M1记录的最高价
- **Low (最低价)**：时间窗口内所有M1记录的最低价  
- **Close (收盘价)**：时间窗口内最后一个M1记录的收盘价

### 时间边界对齐

- **M5**：对齐到5分钟边界（00:00, 00:05, 00:10, 00:15...）
- **M15**：对齐到15分钟边界（00:00, 00:15, 00:30, 00:45）
- **M30**：对齐到30分钟边界（00:00, 00:30）
- **H1**：对齐到小时边界（00:00, 01:00, 02:00...）

### 生成的多时间周期数据结构

```
fxcm_data/
├── EURUSD/
│   ├── M1/          # 原始1分钟数据
│   ├── M5/          # 生成的5分钟数据
│   │   ├── 2015/
│   │   │   ├── week_01.csv
│   │   │   ├── week_02.csv
│   │   │   └── ...
│   │   ├── 2016/
│   │   └── ...
│   ├── M15/         # 生成的15分钟数据
│   ├── M30/         # 生成的30分钟数据
│   └── H1/          # 生成的60分钟数据
└── ...
```

### 转换报告

转换完成后会在 `logs/` 目录生成详细报告：

- `logs/multi_timeframe_conversion_YYYYMMDD_HHMMSS.log` - 转换过程日志
- 实时显示转换进度、压缩比和统计信息

### 压缩效率

- **M5数据压缩比**：约 5:1 (每5个M1记录生成1个M5记录)
- **M15数据压缩比**：约 15:1 (每15个M1记录生成1个M15记录)
- **M30数据压缩比**：约 30:1 (每30个M1记录生成1个M30记录)
- **H1数据压缩比**：约 60:1 (每60个M1记录生成1个H1记录)
- **文件大小减少**：根据时间周期不同，节省80%-98%的存储空间
- **处理速度**：平均每秒处理数十个文件，单个货币对年度数据几分钟内完成

## 脚本架构

### 主要类：FXCMDataDownloader

```python
class FXCMDataDownloader:
    def __init__(self):
        # 初始化日志系统和路径
        
    def download_week_data(self, instrument, year, week, timeframe='m1', max_retries=5):
        # 下载单周的 M1 数据
        
    def download_daily_data(self, instrument, year, max_retries=5):
        # 下载单年的 D1 数据
        
    def download_all_data(self):
        # 主循环：遍历所有货币对、时间周期和年份
```

### 主要类：FXCMDataChecker

```python
class FXCMDataChecker:
    def __init__(self):
        # 初始化检查器和日志系统
        
    def check_weekly_data(self, instrument, year, timeframe):
        # 检查周数据完整性（M1、M5、M15、M30、H1）
        
    def check_yearly_data(self, instrument, timeframe):
        # 检查年度数据完整性（D1）
        
    def analyze_data_completeness(self):
        # 分析所有数据完整性
        
    def generate_html_report(self):
        # 生成HTML可视化报告
        
    def generate_json_report(self):
        # 生成JSON数据报告
```

### 主要类：FXCMMultiTimeframeConverter

```python
class FXCMMultiTimeframeConverter:
    def __init__(self):
        # 初始化转换器和时间周期配置
        
    def parse_datetime(self, dt_str):
        # 解析datetime字符串
        
    def round_to_timeframe(self, dt, minutes):
        # 将时间对齐到时间周期边界
        
    def aggregate_to_timeframe(self, df_m1, timeframe_minutes):
        # 聚合M1数据到指定时间周期
        
    def process_m1_file(self, m1_file, output_file, timeframe_name, timeframe_minutes):
        # 处理单个M1文件转换
        
    def process_instrument(self, instrument):
        # 处理单个货币对的所有转换
        
    def process_all(self):
        # 处理所有货币对的多时间周期转换
```

### 工作流程

#### 数据下载流程
1. **初始化**：创建日志文件和数据目录
2. **循环货币对**：遍历 `INSTRUMENTS` 列表
3. **循环时间周期**：处理 M1 和 D1
4. **循环年份**：从 `START_YEAR` 到 `END_YEAR`
5. **下载数据**：
   - M1：每周一个文件（1-52 周）
   - D1：每年一个文件
6. **保存数据**：解压并保存为 CSV
7. **记录日志**：记录成功和失败的操作

#### 数据检查流程
1. **扫描文件**：检查所有预期的数据文件
2. **统计分析**：计算文件大小和记录数量
3. **完整性分析**：计算缺失率和完整率
4. **生成报告**：创建HTML和JSON格式报告
5. **保存结果**：将报告保存到logs目录

## Web界面 (推荐使用)

### Flask Web界面 v4.1 🎉

项目提供了**现代化、功能强大**的Web界面，支持灵活配置下载选项！

```powershell
# 方法1: 双击启动（Windows）
双击 "启动Web界面.bat"

# 方法2: Python启动脚本
python start_web.py

# 方法3: 直接运行
python flask_app.py
```

### 界面功能特点

#### 🎯 灵活的下载配置
- ✅ **外汇对多选** - 自由选择要下载的货币对（EUR/USD, GBP/USD, USD/JPY等）
- ✅ **年份范围设置** - 灵活设置起始年份和终止年份（2015-2025）
- ✅ **失败重试开关** - 可选择是否启用下载失败重试
- ✅ **重试次数控制** - 自定义重试次数（1-10次）
- ✅ **配置持久化** - 配置自动保存到JSON文件

#### 🎮 强大的任务管理
- ✅ **数据下载管理** - 可视化选择货币对和年份范围
- ✅ **多时间周期转换** - 一键转换M5/M15/M30/H1数据
- ✅ **数据完整性分析** - 生成详细的分析报告
- ✅ **实时进度显示** - 动态进度条和状态更新
- ✅ **任务停止功能** - 随时停止正在运行的任务
- ✅ **终端日志输出** - 所有日志实时显示在终端窗口

#### 💡 用户友好体验
- ✅ **自动打开浏览器** - 启动后自动打开Web界面
- ✅ **响应式设计** - 支持桌面和移动设备访问
- ✅ **现代化UI** - 渐变紫色主题，简洁美观
- ✅ **局域网访问** - 支持手机等设备远程访问

### 配置示例

启动下载任务前，可以灵活配置：

1. **选择外汇对**：
   - EUR/USD ✅
   - GBP/USD ✅
   - USD/JPY ✅
   - AUD/USD ☐
   - USD/CAD ☐
   - USD/CHF ☐

2. **设置年份范围**：
   - 起始年份：2018
   - 终止年份：2021

3. **配置重试机制**：
   - 启用重试：✅
   - 重试次数：5

终端会显示配置信息：
```
📋 下载配置:
   外汇对: EURUSD, GBPUSD, USDJPY
   年份范围: 2018 - 2021
   失败重试: 是
   重试次数: 5

============================================================
FXCM 历史数据下载器
============================================================
货币对: EURUSD, GBPUSD, USDJPY
时间周期: M1, D1
年份范围: 2018 - 2021
失败重试: 是
重试次数: 5
保存路径: C:\Users\...\Forex\fxcm_data
============================================================
```

### 访问方式

启动后可通过以下地址访问：

- **本机访问**: http://localhost:5000
- **局域网访问**: http://[你的IP]:5000
- 支持手机、平板等设备访问

**详细使用指南**: 请查看 [`WEB_GUIDE.md`](WEB_GUIDE.md)

---

## 📝 更新日志

### v5.0.0 (2025-10-04) 🎉 重大版本发布

#### 🚀 核心功能升级
- **快速导入模式** - 10-20倍速度提升（3分钟 vs 30-60分钟）
  - 只检查CSV文件首尾记录是否存在
  - 智能跳过已完整导入的文件
  - 适合日常批量导入操作

- **详细校验模式** - 精确数据验证
  - 逐条验证每个记录
  - 交互式文件选择
  - 适合问题定位和修复

#### 📊 HTML报告系统
- **自动生成导入报告** - `import_report_*.html`
  - 总体统计（文件数、记录数、速度）
  - 按货币对分类统计
  - 详细的文件导入明细
  - 可视化进度条和状态标记

- **数据完整性报告** - `fxcm_data_report_*.html`
  - 文件完整率分析
  - 按年/周热力图矩阵
  - 缺失数据详细列表
  - 货币对对比分析

#### 📁 项目结构重构
- **Python脚本统一管理** - 所有.py文件移至`scripts/`
  - 核心功能脚本
  - 数据库工具脚本
  - Web界面脚本
  - 测试脚本（`scripts/test/`）

- **配置文件独立** - 配置集中在`config/`目录
  - ClickHouse配置
  - 下载配置
  - 易于管理和版本控制

- **文档完善** - 详细的使用指南
  - `PROJECT_STRUCTURE.md` - 项目结构说明
  - `SCRIPT_INDEX.md` - 脚本索引和快速查找
  - `HTML_REPORT_GUIDE.md` - HTML报告使用指南
  - `CHANGELOG_FILE_RENAME.md` - 完整更新日志

#### 🎯 用户体验优化
- **便捷启动器** - 根目录批处理文件
  - `start_web_ui.bat` - 一键启动Web界面

- **智能模式切换**
  - 日常使用：快速模式（默认）
  - 问题排查：详细模式（按需）
  - 自动选择最优方案

#### 📈 性能数据
- **处理速度**: 3分钟导入3,332个文件
- **数据量**: 26,500,000条记录
- **数据质量**: A+评分
- **存储优化**: 智能跳过减少90%处理时间

#### 🔧 技术改进
- 新增 `generate_import_report.py` - HTML报告生成器
- 优化 `batch_import_all.py` - 集成报告功能
- 改进 `import_fxcm_to_clickhouse.py` - 双模式支持
- 完善错误处理和日志系统

---

### v4.2.5 (2025-10-04) 🔧
- 🐛 **修复报告重复打开问题** - 数据分析完成后报告只打开一次
- 🎯 **职责分离优化** - check_data_completeness.py 只负责生成报告，flask_app.py 负责打开
- ✅ **改进代码结构** - 避免多层重复执行副作用操作

### v4.2.4 (2025-10-04) 🎨
- 🔕 **移除打开报告提示** - 报告生成后静默打开，无弹窗干扰
- 🏷️ **简化网页标题** - 移除标题中的版本号，避免版本不同步
- 📂 **确认日志路径规范** - 所有日志文件统一写入根目录 logs/ 文件夹
- 💡 **优化用户体验** - "最好的提示就是没有提示"

### v4.2.3 (2025-10-04) 🌐
- ✨ **数据分析报告自动打开** - 分析完成后自动在浏览器打开HTML报告
- 📊 **可视化报告增强** - 生成 fxcm_data_report_*.html 可视化报告
- 🚀 **智能报告管理** - Flask自动查找并打开最新生成的报告
- 📝 **报告命名规范** - 使用时间戳命名 (YYYYMMDD_HHMMSS)

### v4.2.2 (2025-10-04) 🔧
- 🐛 **修复双开浏览器窗口** - 启动Web界面时只打开一次浏览器
- 🎯 **职责分离** - start_web.py 负责启动，flask_app.py 只负责服务
- ✅ **代码优化** - 移除 flask_app.py 中的重复浏览器启动代码

### v4.2.1 (2025-10-04) 📝
- 🔧 **版本号统一** - 修正所有版本号为 v4.2.0
- ✅ **移除停止确认** - 停止任务时不再弹出确认对话框
- 🎯 **用户体验优化** - 减少不必要的交互确认

### v4.2.0 (2025-10-04) 🚀
- 🔕 **移除任务启动确认** - 启动任务时不再弹出确认对话框
- ✅ **简化操作流程** - 点击按钮直接执行，无额外确认步骤
- 🎨 **界面优化** - 移除所有 JavaScript alert/confirm 对话框

### v4.1.9 (2025-10-04) 📊
- 🔇 **禁用Flask访问日志** - 减少终端输出噪音
- ✅ **日志级别优化** - werkzeug 日志级别设为 ERROR
- 🎯 **终端输出清爽** - 只显示重要信息

### v4.1.8 (2025-10-04) ⚙️
- 🔧 **默认配置优化** - 年份范围 2015-2025，重试次数 5
- ✅ **配置持久化改进** - download_config.json 默认值更新
- 📝 **用户友好** - 开箱即用的合理默认配置

### v4.1.7 (2025-10-04) 🔧
- 🐛 **修复Flask模板路径** - 显式设置 template_folder 和 static_folder
- ✅ **路径问题解决** - 确保Flask能正确找到模板和静态文件
- 🎯 **稳定性提升** - 解决文件重组后的路径引用问题

### v4.1.6 (2025-10-04) 🔧
- 🐛 **修复所有脚本路径引用** - 使用 Path(__file__).parent.parent
- ✅ **路径统一** - 所有脚本正确引用项目根目录
- 📂 **支持重组后的结构** - 适配 scripts/ 目录结构

### v4.1.5 (2025-10-04) 📁
- 📂 **创建config文件夹** - 新增独立配置目录
- 🔧 **配置文件迁移** - download_config.json 移至 config/
- ✅ **更新路径引用** - 所有脚本更新配置文件路径

### v4.1.4 (2025-10-04) 📁
- 📂 **Scripts重组** - 所有Python脚本移至 scripts/ 目录
- ✅ **批处理文件更新** - 更新所有.bat文件的脚本路径
- 🎯 **项目结构优化** - 代码和文档分离更清晰

### v4.1.3 (2025-10-04) 📚
- 📂 **文档重组** - 创建 doc/ 目录集中管理文档
- ✅ **文档迁移** - 所有.md文件移至 doc/
- 📝 **项目整洁** - 根目录只保留核心文件

### v4.1.2 (2025-10-04) 🎨
- 🗑️ **移除Tkinter GUI** - 删除图形界面相关代码
- ✅ **专注Web界面** - 统一使用Flask Web界面
- 🎯 **简化项目** - 减少维护负担

### v4.0.0 (2025-10-04) 🎉
- 🎨 **增强下载配置** - 全新的灵活配置系统
- ✅ **外汇对多选** - 支持自由选择要下载的货币对
- ✅ **年份范围设置** - 可自定义起始年份和终止年份
- ✅ **失败重试控制** - 可选择是否启用重试及重试次数（1-10次）
- ✅ **配置持久化** - 配置自动保存到download_config.json
- ✅ **配置读取优化** - 下载脚本自动读取并应用配置
- ✅ **停止任务功能** - 新增任务停止功能，可随时中断任务
- ✅ **Web界面优化** - 移除网页日志显示，改为终端实时输出
- ✅ **自动打开浏览器** - 启动后自动打开Web界面
- 🔧 **修复脚本文件名** - 更正分析脚本文件名引用
- 📚 **文档全面更新** - 更新README和WEB_GUIDE文档

### v3.0.x (2025-10-04)
- 🌐 **Flask Web界面** - 从Streamlit切换到Flask框架
- ✅ **现代化设计** - 渐变紫色主题，响应式布局
- ✅ **移除日志面板** - 简化界面，日志仅在终端显示
- ✅ **停止功能实现** - 真正可用的任务停止功能
- ✅ **缓存优化** - 解决浏览器缓存问题
- 🔧 **多个修复** - 进度条算法、响应头、路由优化

### v1.0.4 (2025-10-04)
- 🐛 **修复Streamlit多线程问题** - 解决ScriptRunContext警告
- ✅ **改进错误处理** - 增强子进程调用的错误信息

### v1.0.3 (2025-10-04)
- 🐛 **Web界面按钮修复** - 解决按钮禁用问题

### v1.0.2 (2025-10-04)
- 🌐 **Web可视化界面** - 新增基于Streamlit的界面

### v1.0.1 (2025-10-03)
- 🚀 **多时间周期转换** - 新增 `convert_m1_to_multi_timeframes.py` 脚本
- ✅ **四个新时间周期** - 支持 M5、M15、M30、H1 数据转换
- ✅ **精确时间对齐** - 严格按照时间边界对齐聚合数据
- ✅ **批量转换能力** - 一次性转换所有货币对和年份的数据
- ✅ **数据格式优化** - 移除 Volume 列，保持纯 OHLC 格式
- ✅ **压缩比显示** - 实时显示各时间周期的压缩比统计
- ✅ **增量转换支持** - 自动跳过已存在文件，支持断点续传
- ✅ **数据完整性检查升级** - `check_data_completeness.py` 支持所有时间周期
- ✅ **多时间周期热力图** - HTML报告中包含所有时间周期的完整性矩阵
- 📚 **文档全面更新** - 更新 README.md 包含完整的多时间周期说明

### v1.0.0 (2025-10-03)
- ✅ **初始版本发布** - 项目正式上线
- ✅ **多货币对支持** - 支持 6 大主流货币对（EURUSD, USDCAD, GBPUSD, USDCHF, AUDUSD, USDJPY）
- ✅ **双时间周期** - 支持 M1（1分钟）和 D1（日线）数据下载
- ✅ **长时间跨度** - 覆盖 2015-2025 年共 10 年历史数据
- ✅ **智能重试机制** - 对 404 和网络错误实现 5 次自动重试
- ✅ **完整日志系统** - 时间戳日志文件，记录所有下载操作
- ✅ **文件跳过优化** - 自动检测已存在文件，避免重复下载
- ✅ **规范化数据结构** - 标准 OHLC 格式，层级目录组织
- ✅ **Git 版本控制** - 创建 .gitignore，排除数据文件，仅版本控制代码
- 🏷️ **Git 标签** - 创建 v1.0.0 版本标签

---

## 📚 文档索引

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 项目结构详解
- [SCRIPT_INDEX.md](SCRIPT_INDEX.md) - 脚本索引和快速查找
- [doc/HTML_REPORT_GUIDE.md](doc/HTML_REPORT_GUIDE.md) - HTML报告使用指南
- [CHANGELOG_FILE_RENAME.md](CHANGELOG_FILE_RENAME.md) - 完整更新日志
- [doc/DATABASE_SCHEMA.md](doc/DATABASE_SCHEMA.md) - 数据库结构说明
- [QUICKSTART.md](QUICKSTART.md) - 快速开始指南

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

### 如何贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 报告问题

使用 [GitHub Issues](https://github.com/binphilxiao/Forex/issues) 报告问题

---

## 📜 许可证

本项目采用 MIT 许可证。

**数据来源**: 数据来自 FXCM 公开 API，仅供学习研究使用。数据版权归 FXCM 所有。

---

## 💬 联系方式

- **作者**: binphilxiao
- **GitHub**: [@binphilxiao](https://github.com/binphilxiao)
- **问题反馈**: 通过 GitHub Issues

---

## 🌟 致谢

感谢以下开源项目：

- [ClickHouse](https://clickhouse.com/) - 高性能列式数据库
- [Flask](https://flask.palletsprojects.com/) - 轻量级Web框架
- [Pandas](https://pandas.pydata.org/) - 数据分析库
- [FXCM](https://www.fxcm.com/) - 提供历史数据API

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个Star！⭐**

Made with ❤️ by binphilxiao

**最后更新**: 2025年10月5日 | **版本**: v5.0.1

</div>
