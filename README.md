# FXCM 历史数据下载器

## 项目简介

这是一个用于自动下载 FXCM（福汇）历史外汇数据的 Python 脚本。该脚本可以批量下载多个货币对的分钟级（M1）和日线级（D1）蜡烛图数据，并自动组织存储到规范的文件夹结构中。

## 功能特点

- ✅ **多货币对支持**：支持 EURUSD, USDCAD, GBPUSD, USDCHF, AUDUSD, USDJPY 等主流货币对
- ✅ **多时间周期**：支持 M1（1分钟）和 D1（日线）两种时间周期
- ✅ **长时间跨度**：默认下载 2015-2025 年共 10 年的历史数据
- ✅ **智能跳过**：自动检测已存在的文件，避免重复下载
- ✅ **错误重试**：对于 404 错误自动重试 5 次，提高下载成功率
- ✅ **详细日志**：记录所有下载操作和错误信息，每次运行生成独立的时间戳日志文件
- ✅ **规范存储**：按照货币对/时间周期/年份的层级结构组织数据

## 环境要求

- Python 3.7+
- 依赖库：
  - `pandas` - 数据处理
  - `requests` - HTTP 请求
  - 标准库：`gzip`, `pathlib`, `logging`, `datetime`, `time`, `io`

## 安装步骤

1. **克隆或下载项目**
   ```bash
   git clone <repository_url>
   cd Forex
   ```

2. **创建虚拟环境**（推荐）
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **安装依赖**
   ```powershell
   pip install pandas requests
   ```

## 使用方法

### 基本使用

直接运行脚本即可开始下载：

```powershell
python download_fxcm_candles.py
```

### 自定义配置

如需修改下载参数，可编辑脚本中的配置变量：

```python
# 货币对列表
INSTRUMENTS = ['EURUSD', 'USDCAD', 'GBPUSD', 'USDCHF', 'AUDUSD', 'USDJPY']

# 时间周期（仅支持 'm1' 和 'D1'）
TIMEFRAMES = ['m1', 'D1']

# 年份范围
START_YEAR = 2015
END_YEAR = 2025
```

## 数据结构

### 目录组织

下载的数据会按照以下结构存储：

```
Forex/
├── fxcm_data/              # 数据根目录
│   ├── EURUSD/             # 货币对文件夹
│   │   ├── M1/             # 1分钟数据
│   │   │   ├── 2015/       # 年份文件夹
│   │   │   │   ├── week_01.csv
│   │   │   │   ├── week_02.csv
│   │   │   │   └── ...
│   │   │   ├── 2016/
│   │   │   └── ...
│   │   └── D1/             # 日线数据
│   │       ├── 2015.csv
│   │       ├── 2016.csv
│   │       └── ...
│   ├── USDCAD/
│   ├── GBPUSD/
│   └── ...
└── logs/                   # 日志文件夹
    ├── download_20251003_110507.log
    └── ...
```

### CSV 数据格式

所有 CSV 文件包含以下列：

| 列名 | 说明 |
|------|------|
| DateTime | 时间戳（格式：YYYY-MM-DD HH:MM:SS） |
| Open | 开盘价 |
| High | 最高价 |
| Low | 最低价 |
| Close | 收盘价 |
| Volume | 成交量 |

**注意**：数据源自 FXCM 的 Bid（买入）价格，列名已从 `BidOpen`, `BidHigh`, `BidLow`, `BidClose` 重命名为标准 OHLC 格式。

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

**A**: 目前脚本仅支持 M1 和 D1。FXCM API 的其他时间周期端点格式可能不同，需要额外的开发工作。

### Q4: 下载的数据包含 Ask 价格吗？

**A**: 不包含。数据仅包含 Bid（买入）价格。如需 Ask 价格，需要查阅 FXCM 的其他数据源。

### Q5: 如何验证下载的数据是否完整？

**A**: 可以检查日志文件中的 404 错误数量，以及与预期的数据文件进行对比。正常情况下，每年应有约 45-50 周的 M1 数据。

## 数据完整性检查

### 数据检查脚本：check_data_completeness.py

除了数据下载功能，项目还提供了一个完整的数据完整性检查工具：

```powershell
python check_data_completeness.py
```

### 检查功能特点

- ✅ **全面扫描**：检查所有货币对的M1和D1数据完整性
- ✅ **统计分析**：计算文件大小、记录数量和完整率
- ✅ **可视化报告**：生成现代化的HTML可视化报告
- ✅ **热力图矩阵**：M1数据按年/周的完整性热力图
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

## M1到M5数据转换

### 数据转换脚本：convert_m1_to_m5.py

项目提供了将1分钟(M1)数据转换为5分钟(M5)数据的功能：

```powershell
python convert_m1_to_m5.py
```

### 转换功能特点

- ✅ **精确聚合**：严格按照5分钟时间窗口聚合OHLC数据
- ✅ **格式保持**：生成的M5数据保持与M1数据完全相同的列格式
- ✅ **批量转换**：支持所有货币对和年份的批量转换
- ✅ **格式一致**：生成的M5数据与M1数据格式完全一致
- ✅ **跳过重复**：自动跳过已存在的M5文件，支持增量转换
- ✅ **详细日志**：记录转换过程和统计信息

### 聚合规则

M5数据聚合遵循标准的OHLC规则：

- **Open (开盘价)**：5分钟窗口内第一个M1记录的开盘价
- **High (最高价)**：5分钟窗口内所有M1记录的最高价
- **Low (最低价)**：5分钟窗口内所有M1记录的最低价  
- **Close (收盘价)**：5分钟窗口内最后一个M1记录的收盘价

### 生成的M5数据结构

```
fxcm_data/
├── EURUSD/
│   ├── M1/          # 原始1分钟数据
│   └── M5/          # 生成的5分钟数据
│       ├── 2015/
│       │   ├── week_01.csv
│       │   ├── week_02.csv
│       │   └── ...
│       ├── 2016/
│       └── ...
└── ...
```

### 转换报告

转换完成后会在 `logs/` 目录生成详细报告：

- `logs/m1_to_m5_report_YYYYMMDD_HHMMSS.html` - 可视化转换报告
- `logs/m1_to_m5_report_YYYYMMDD_HHMMSS.json` - 详细转换统计
- `logs/m1_to_m5_conversion_YYYYMMDD_HHMMSS.log` - 转换过程日志

### 压缩效率

- **数据压缩比**：约 5:1 (每5个M1记录生成1个M5记录)
- **文件大小减少**：约80%的存储空间节省
- **处理速度**：平均每秒处理数十个文件

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
        
    def check_m1_data(self, instrument, year):
        # 检查M1数据完整性（按周）
        
    def check_d1_data(self, instrument):
        # 检查D1数据完整性（按年）
        
    def analyze_data_completeness(self):
        # 分析所有数据完整性
        
    def generate_html_report(self):
        # 生成HTML可视化报告
        
    def generate_json_report(self):
        # 生成JSON数据报告
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

## 更新日志

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

## 许可证

本项目仅供学习和研究使用。数据版权归 FXCM 所有。

## 联系方式

如有问题或建议，请通过 GitHub Issues 反馈。

---

**最后更新**: 2025年10月3日
