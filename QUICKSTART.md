# 🚀 快速开始指南# 🚀 快速开始指南# 🚀 FXCM 数据处理系统 - 快速开始



> **版本**: v5.0.7 | **更新**: 2025-10-06



## ⚡ 5分钟快速上手> **版本**: v5.0.6 | **更新**: 2025-10-06> **版本**: v4.2.0 | **更新**: 2025-10-04



### 第一步：配置数据库连接

```powershell

# 运行配置向导（仅首次使用）## ⚡ 5分钟快速上手## ⚡ 核心命令

python scripts\clickhouse_configurator.py

```



### 第二步：创建数据库表### 第一步：配置数据库连接### 数据库操作（推荐）

```powershell

python scripts\create_clickhouse_tables.py```powershell```bash

```

# 运行配置向导（仅首次使用）# 1. 创建表结构（首次使用）

### 第三步：下载和导入数据

```powershellpython scripts\clickhouse_configurator.pypython scripts\create_clickhouse_tables.py

# 下载FXCM数据

download_fxcm_data.bat```



# 导入到数据库# 2. 导入所有数据

import_fxcm_data.bat

```### 第二步：创建数据库表python 一键导入所有数据.py



### 第四步：验证数据```powershell

```powershell

verify_consistency.batpython scripts\create_clickhouse_tables.py# 3. 验证数据质量

```

```python 一键验证所有数据.py

---



## 🎯 核心功能

### 第三步：下载和导入数据# 4. 查询示例

### 1. 数据库配置 ⭐

```powershell```powershellpython scripts\query_examples.py

# 交互式配置数据库连接

python scripts\clickhouse_configurator.py# 下载FXCM数据



# 配置保存到: config/clickhouse_config.jsondownload_fxcm_data.bat# 5. 查看表信息

# 所有脚本自动读取此配置

```python scripts\view_clickhouse_tables.py



### 2. 数据下载# 导入到数据库```

```powershell

# 一键下载（使用批处理）import_fxcm_data.bat

download_fxcm_data.bat

```### Web界面（可选）

# 或自定义下载

python scripts\fxcm_data_downloader.py --pairs EURUSD GBPUSD --timeframes M1 D1```powershell

```

### 第四步：验证数据# 双击即可启动

### 3. 数据导入

```powershell```powershell启动Web界面.bat

# 一键导入（使用批处理）

import_fxcm_data.batverify_consistency.bat



# 或自定义导入```# 或命令行启动

python scripts\fxcm_importer.py --pairs EURUSD --timeframes M1 --start-year 2024

```python scripts/start_web.py



### 4. 时间框架转换---

```powershell

# 一键转换（M1 → M5/M15/M30/H1）# 浏览器访问

convert_m1_to_multi_timeframes.bat

## 🎯 核心功能http://localhost:5000

# 或自定义转换

python scripts\m1_timeframe_converter.py --pairs EURUSD --timeframes M5 M15```

```

### 1. 数据库配置 ⭐

### 5. 数据验证

```powershell```powershell---

# 一键验证（CSV与数据库一致性）

verify_consistency.bat# 交互式配置数据库连接



# 或命令行验证python scripts\clickhouse_configurator.py## 📋 数据库快速开始

python scripts\verify_data_consistency.py

```



### 6. Web界面# 配置保存到: config/clickhouse_config.json### 1️⃣ 准备工作

```powershell

# 启动Web管理界面# 所有脚本自动读取此配置- ✅ ClickHouse服务器运行中（192.168.2.168:8123）

start_web_ui.bat

```- ✅ 配置文件正确（`config/clickhouse_config.json`）

# 浏览器访问

# http://localhost:5000- ✅ CSV文件在 `fxcm_data/` 文件夹

```

### 2. 数据下载

---

```powershell### 2️⃣ 导入数据

## 📖 核心脚本详细参数

# 一键下载（使用批处理）```bash

### 1️⃣ 数据下载器 (fxcm_data_downloader.py)

download_fxcm_data.batpython 一键导入所有数据.py

#### 基本参数

```powershell# 预计时间：30-60分钟

# 查看帮助

python scripts\fxcm_data_downloader.py --help# 或自定义下载# 自动导入所有M1和D1数据



# 下载所有数据（默认：所有货币对，M1+D1，2015至今）python scripts\fxcm_data_downloader.py --pairs EURUSD GBPUSD --timeframes M1 D1# 实时显示进度和日志

python scripts\fxcm_data_downloader.py

`````````



#### 参数说明

| 参数 | 说明 | 可选值 | 默认值 |

|------|------|--------|--------|### 3. 数据导入### 3️⃣ 验证数据

| `--pairs` | 货币对 | EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF | 全部 |

| `--timeframes` | 时间框架 | M1, D1 | M1 D1 |```powershell```bash

| `--start-year` | 起始年份 | 2015-2025 | 2015 |

| `--end-year` | 结束年份 | 2015-2025 | 当前年份 |# 一键导入（使用批处理）python 一键验证所有数据.py

| `--max-retries` | 最大重试次数 | 整数 | 5 |

import_fxcm_data.bat# 预计时间：10-30秒

#### 使用实例

```powershell# 全面检查数据质量

# 示例1：下载单个货币对

python scripts\fxcm_data_downloader.py --pairs EURUSD# 或自定义导入# 自动生成评分报告



# 示例2：下载多个货币对python scripts\fxcm_importer.py --pairs EURUSD --timeframes M1 --start-year 2024```

python scripts\fxcm_data_downloader.py --pairs EURUSD GBPUSD USDJPY

```

# 示例3：只下载M1数据

python scripts\fxcm_data_downloader.py --timeframes M1---



# 示例4：只下载D1数据### 4. 时间框架转换

python scripts\fxcm_data_downloader.py --timeframes D1

```powershell## 🎯 主要功能

# 示例5：下载特定年份范围

python scripts\fxcm_data_downloader.py --start-year 2020 --end-year 2023# 一键转换（M1 → M5/M15/M30/H1）



# 示例6：下载2024年EURUSD的M1数据convert_m1_to_multi_timeframes.bat### ClickHouse数据库（推荐）

python scripts\fxcm_data_downloader.py --pairs EURUSD --timeframes M1 --start-year 2024 --end-year 2024

| 功能 | 命令 | 时间 |

# 示例7：下载最近3年所有数据

python scripts\fxcm_data_downloader.py --start-year 2022# 或自定义转换|------|------|------|



# 示例8：组合参数 - EURUSD和GBPUSD的D1数据（2018-2023）python scripts\m1_timeframe_converter.py --pairs EURUSD --timeframes M5 M15| 📥 导入数据 | `python 一键导入所有数据.py` | 30-60分钟 |

python scripts\fxcm_data_downloader.py --pairs EURUSD GBPUSD --timeframes D1 --start-year 2018 --end-year 2023

```| ✅ 验证数据 | `python 一键验证所有数据.py` | 10-30秒 |

# 示例9：增加重试次数（网络不稳定时）

python scripts\fxcm_data_downloader.py --max-retries 10| 🔍 查询数据 | `python scripts\query_examples.py` | 毫秒级 |

```

### 5. 数据验证| 📊 查看表 | `python scripts\view_clickhouse_tables.py` | 即时 |

---

```powershell

### 2️⃣ 数据导入器 (fxcm_importer.py)

# 一键验证（CSV与数据库一致性）### Web界面（可选）

#### 基本参数

```powershellverify_consistency.bat| 功能 | 说明 | 时间 |

# 查看帮助

python scripts\fxcm_importer.py --help|------|------|------|



# 导入所有数据（默认：快速验证模式）# 或命令行验证| 📥 下载数据 | 从FXCM下载M1/D1原始数据 | 2-4小时 |

python scripts\fxcm_importer.py

```python scripts\verify_data_consistency.py| 🔄 转换数据 | M1转换为M5/M15/M30/H1 | 1-3小时 |



#### 参数说明```| 📊 分析数据 | 生成完整性报告和可视化 | 5-10分钟 |

| 参数 | 说明 | 可选值 | 默认值 |

|------|------|--------|--------|

| `--pairs` | 货币对 | EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF | 全部 |

| `--timeframes` | 时间框架 | M1, D1 | M1 D1 |### 6. Web界面---

| `--start-year` | 起始年份 | 2015-2025 | 2015 |

| `--end-year` | 结束年份 | 2015-2025 | 当前年份 |```powershell

| `--check-mode` | 验证模式 | fast, comprehensive | fast |

| `--ch-host` | ClickHouse主机 | IP地址 | 从配置文件读取 |# 启动Web管理界面## 📊 数据库状态（当前）

| `--ch-http-port` | HTTP端口 | 端口号 | 8123 |

| `--ch-user` | 用户名 | 字符串 | default |start_web_ui.bat

| `--ch-password` | 密码 | 字符串 | 从配置文件读取 |

```

#### 使用实例

```powershell# 浏览器访问总记录数: 26,569,070 条

# 示例1：导入单个货币对

python scripts\fxcm_importer.py --pairs EURUSD# http://localhost:5000├── M1:  20,126,872 条 (6货币对: AUDUSD/EURUSD/GBPUSD/USDJPY/USDCAD/USDCHF)



# 示例2：导入多个货币对```├── D1:     12,971 条 (6货币对)

python scripts\fxcm_importer.py --pairs EURUSD GBPUSD USDJPY

├── M5:  4,058,445 条 (物化视图自动生成)

# 示例3：只导入M1数据

python scripts\fxcm_importer.py --timeframes M1---├── M15: 1,354,303 条 (物化视图自动生成)



# 示例4：只导入D1数据├── M30:   677,591 条 (物化视图自动生成)

python scripts\fxcm_importer.py --timeframes D1

## 📊 支持的货币对和时间框架└── H1:    338,888 条 (物化视图自动生成)

# 示例5：导入2024年数据

python scripts\fxcm_importer.py --start-year 2024 --end-year 2024



# 示例6：使用全面验证模式（慢但更准确）### 货币对（6个）数据质量评分: A+

python scripts\fxcm_importer.py --check-mode comprehensive

- AUDUSD - 澳元/美元物化视图: 4/4 正常工作

# 示例7：快速模式导入EURUSD 2024年M1数据

python scripts\fxcm_importer.py --pairs EURUSD --timeframes M1 --start-year 2024- EURUSD - 欧元/美元```



# 示例8：连接自定义ClickHouse服务器- GBPUSD - 英镑/美元

python scripts\fxcm_importer.py --ch-host 192.168.1.100 --ch-http-port 8123

- USDJPY - 美元/日元---

# 示例9：完全自定义参数

python scripts\fxcm_importer.py ^- USDCAD - 美元/加元

    --pairs EURUSD GBPUSD ^

    --timeframes M1 ^- USDCHF - 美元/瑞郎## 📦 系统要求

    --start-year 2023 ^

    --check-mode fast ^

    --ch-host 192.168.2.168

### 时间框架（6个）```bash

# 示例10：导入最近1年数据（全面验证）

python scripts\fxcm_importer.py --start-year 2024 --check-mode comprehensive- **M1** - 1分钟（原始数据）# Python 版本

```

- **M5** - 5分钟（转换生成）Python 3.7+

---

- **M15** - 15分钟（转换生成）

### 3️⃣ 时间框架转换器 (m1_timeframe_converter.py)

- **M30** - 30分钟（转换生成）# 依赖安装

#### 基本参数

```powershell- **H1** - 1小时（转换生成）pip install flask pandas requests

# 查看帮助

python scripts\m1_timeframe_converter.py --help- **D1** - 日线（原始数据）



# 转换所有数据（默认：本地CSV模式，M5+M15+M30+H1）# 存储空间

python scripts\m1_timeframe_converter.py

```### 数据年份范围全量数据约 50GB



#### 参数说明- **2015 - 2025**（10年历史数据）```

| 参数 | 说明 | 可选值 | 默认值 |

|------|------|--------|--------|

| `--pairs` | 货币对 | EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF | 全部 |

| `--timeframes` | 目标时间框架 | M5, M15, M30, H1 | M5 M15 M30 H1 |------

| `--start-year` | 起始年份 | 2015-2025 | 2015 |

| `--end-year` | 结束年份 | 2015-2025 | 当前年份 |

| `--overwrite` | 覆盖已存在数据 | 无需值 | 跳过已存在 |

| `--mode` | 转换模式 | local, database | local |## 🔧 系统要求## 🌐 访问方式

| `--ch-host` | ClickHouse主机 | IP地址 | 从配置文件读取 |

| `--ch-port` | HTTP端口 | 端口号 | 8123 |

| `--ch-user` | 用户名 | 字符串 | default |

| `--ch-password` | 密码 | 字符串 | 从配置文件读取 |### 必需组件- **本机**: http://localhost:5000



#### 使用实例- **Python**: 3.8 或更高版本- **局域网**: http://[你的IP]:5000

```powershell

# 示例1：转换单个货币对- **ClickHouse**: 数据库服务器- **手机/平板**: 支持移动设备访问

python scripts\m1_timeframe_converter.py --pairs EURUSD

- **磁盘空间**: 至少 20GB 可用空间

# 示例2：转换多个货币对

python scripts\m1_timeframe_converter.py --pairs EURUSD GBPUSD USDJPY### 查看本机IP



# 示例3：只生成M5和M15### Python依赖```powershell

python scripts\m1_timeframe_converter.py --timeframes M5 M15

```powershell# Windows

# 示例4：只生成H1数据

python scripts\m1_timeframe_converter.py --timeframes H1# 安装所有依赖ipconfig | findstr IPv4



# 示例5：转换2024年数据pip install -r requirements.txt

python scripts\m1_timeframe_converter.py --start-year 2024 --end-year 2024

# Linux/Mac

# 示例6：覆盖已存在的文件（默认跳过）

python scripts\m1_timeframe_converter.py --overwrite# 或手动安装核心依赖ifconfig | grep inet



# 示例7：使用数据库模式（ClickHouse SQL转换）pip install flask pandas requests clickhouse-connect```

python scripts\m1_timeframe_converter.py --mode database

```

# 示例8：本地CSV模式转换EURUSD的M5数据

python scripts\m1_timeframe_converter.py --mode local --pairs EURUSD --timeframes M5---



# 示例9：数据库模式转换2023-2024年数据---

python scripts\m1_timeframe_converter.py --mode database --start-year 2023 --end-year 2024

## 📚 详细文档

# 示例10：连接自定义ClickHouse服务器（数据库模式）

python scripts\m1_timeframe_converter.py ^## 📁 项目结构

    --mode database ^

    --ch-host 192.168.1.100 ^完整文档请查看 **[doc](./doc/)** 文件夹：

    --ch-port 8123

```

# 示例11：完全自定义 - 本地模式转换特定数据并覆盖

python scripts\m1_timeframe_converter.py ^Forex/### 数据库相关

    --pairs EURUSD GBPUSD ^

    --timeframes M5 M30 ^├── README.md                      # 项目说明- **[一键脚本使用指南.md](./doc/一键脚本使用指南.md)** ⭐ 导入验证脚本详细说明

    --start-year 2024 ^

    --overwrite ^├── QUICKSTART.md                  # 快速开始（本文件）- **[数据库表结构设计.md](./doc/数据库表结构设计.md)** - ClickHouse表结构

    --mode local

```├── requirements.txt               # Python依赖- **[数据导入使用指南.md](./doc/数据导入使用指南.md)** - 数据导入详细说明



---├── config/                        # 配置文件目录- **[数据验证报告.md](./doc/数据验证报告.md)** - 数据质量验证报告



### 4️⃣ 数据一致性验证器 (verify_data_consistency.py)│   └── clickhouse_config.json     # 数据库配置



#### 基本参数├── scripts/                       # Python脚本目录### Web界面相关

```powershell

# 查看帮助│   ├── clickhouse_configurator.py # 数据库配置工具- **[README.md](./doc/README.md)** - 完整项目说明

python scripts\verify_data_consistency.py --help

│   ├── fxcm_data_downloader.py    # 数据下载器- **[WEB_GUIDE.md](./doc/WEB_GUIDE.md)** - Web界面详细指南

# 验证所有数据（默认：快速模式，生成HTML报告）

python scripts\verify_data_consistency.py│   ├── fxcm_importer.py           # 数据导入器- **[CHANGELOG.md](./doc/CHANGELOG.md)** - 版本更新历史

```

│   ├── m1_timeframe_converter.py  # 时间框架转换器- **[REQUIREMENTS.md](./doc/REQUIREMENTS.md)** - 需求文档

#### 参数说明

| 参数 | 说明 | 可选值 | 默认值 |│   └── ...                        # 其他脚本

|------|------|--------|--------|

| `--symbols` | 货币对 | EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF | 全部 |├── doc/                           # 文档目录---

| `--timeframes` | 时间框架 | M1, D1 | M1 D1 |

| `--start-year` | 起始年份 | 2015-2025 | 2015 |│   ├── guides/                    # 使用指南

| `--end-year` | 结束年份 | 2015-2025 | 当前年份 |

| `--mode` | 验证模式 | fast, comprehensive | fast |│   ├── reference/                 # 参考文档## ⏱️ 时间预估

| `--config` | 配置文件路径 | 文件路径 | config/clickhouse_config.json |

| `--output` | 输出文件路径 | 文件路径 | 自动生成时间戳 |│   └── development/               # 开发文档

| `--no-html` | 跳过HTML报告 | 无需值 | 生成HTML |

├── fxcm_data/                     # CSV数据目录| 操作 | 时间 | 说明 |

#### 使用实例

```powershell├── logs/                          # 日志文件目录|------|------|------|

# 示例1：验证单个货币对

python scripts\verify_data_consistency.py --symbols EURUSD└── templates/                     # Web模板目录| 创建表结构 | 5秒 | 首次使用执行一次 |



# 示例2：验证多个货币对```| 导入D1数据 | 3-5秒 | 42个文件 |

python scripts\verify_data_consistency.py --symbols EURUSD GBPUSD USDJPY

| 导入M1数据 | 30-60分钟 | 3290个文件 |

# 示例3：只验证M1数据

python scripts\verify_data_consistency.py --timeframes M1---| 验证数据 | 10-30秒 | 全面质量检查 |



# 示例4：只验证D1数据| 查询数据 | 毫秒级 | ClickHouse高性能 |

python scripts\verify_data_consistency.py --timeframes D1

## 💡 常用操作

# 示例5：验证2024年数据

python scripts\verify_data_consistency.py --start-year 2024 --end-year 2024---



# 示例6：使用全面验证模式（逐条记录验证）### 日常工作流程

python scripts\verify_data_consistency.py --mode comprehensive

```powershell## ⚠️ 常见问题

# 示例7：验证特定年份范围

python scripts\verify_data_consistency.py --start-year 2020 --end-year 2023# 1. 下载最新数据



# 示例8：指定自定义配置文件download_fxcm_data.bat### 数据库相关

python scripts\verify_data_consistency.py --config my_config.json



# 示例9：指定输出报告文件名

python scripts\verify_data_consistency.py --output logs\my_report.html# 2. 导入到数据库#### Q: 导入时提示"连接失败"？



# 示例10：不生成HTML报告（仅终端输出）import_fxcm_data.batA: 检查ClickHouse服务器是否运行，配置是否正确

python scripts\verify_data_consistency.py --no-html



# 示例11：快速验证EURUSD 2024年M1数据

python scripts\verify_data_consistency.py ^# 3. 验证数据质量#### Q: 导入很慢怎么办？

    --symbols EURUSD ^

    --timeframes M1 ^verify_consistency.batA: 正常现象，M1数据量大（2千万条），预计30-60分钟

    --start-year 2024 ^

    --mode fast



# 示例12：全面验证最近2年所有数据# 4. 启动Web界面查看#### Q: 某个文件导入失败？

python scripts\verify_data_consistency.py ^

    --start-year 2023 ^start_web_ui.batA: 单个文件失败不影响其他文件，查看错误信息处理

    --mode comprehensive

```

# 示例13：验证特定货币对并保存自定义报告

python scripts\verify_data_consistency.py ^#### Q: 如何重新导入？

    --symbols EURUSD GBPUSD ^

    --timeframes M1 D1 ^### 数据库管理A: 直接运行导入脚本，已存在的数据会自动跳过

    --start-year 2024 ^

    --output logs\eurusd_gbpusd_2024_report.html```powershell

```

# 配置连接（首次使用）#### Q: 验证评分低怎么办？

---

python scripts\clickhouse_configurator.pyA: 查看验证报告中的详细问题，根据建议处理

## 📊 支持的货币对和时间框架



### 货币对（6个）

- **EURUSD** - 欧元/美元# 创建表结构### Web界面相关

- **GBPUSD** - 英镑/美元

- **USDJPY** - 美元/日元python scripts\create_clickhouse_tables.py

- **AUDUSD** - 澳元/美元

- **USDCAD** - 美元/加元#### Q: 终端没有输出？

- **USDCHF** - 美元/瑞郎

# 查看数据库信息A: 这是正常的，请确保运行了 `python scripts/start_web.py`

### 时间框架

#### 原始数据（下载）python scripts\view_clickhouse_tables.py

- **M1** - 1分钟

- **D1** - 日线```#### Q: 下载很多404错误？



#### 转换生成A: 正常现象，某些周次的数据FXCM不提供

- **M5** - 5分钟

- **M15** - 15分钟### 高级用法

- **M30** - 30分钟

- **H1** - 1小时```powershell#### Q: 如何停止任务？



### 数据年份范围# 下载特定货币对和年份A: 点击Web界面的 "⏹ 停止任务" 按钮

- **2015 - 2025**（10年历史数据）

python scripts\fxcm_data_downloader.py --pairs EURUSD GBPUSD --years 2024 2025

---

#### Q: 报告在哪里？

## 🔧 系统要求

# 使用全面验证模式导入A: 分析完成后自动打开，也可在 `logs/` 文件夹查看

### 必需组件

- **Python**: 3.8 或更高版本python scripts\fxcm_importer.py --check-mode comprehensive

- **ClickHouse**: 数据库服务器

- **磁盘空间**: 至少 20GB 可用空间---



### Python依赖# 本地CSV模式转换（不需要ClickHouse）

```powershell

# 安装所有依赖python scripts\m1_timeframe_converter.py --mode local --pairs EURUSD## 🆘 获取帮助

pip install -r requirements.txt

```

# 或手动安装核心依赖

pip install flask pandas requests clickhouse-connect### 数据库问题

```

---1. 查看 [doc/一键脚本使用指南.md](./doc/一键脚本使用指南.md) ⭐

---

2. 查看 [doc/数据导入使用指南.md](./doc/数据导入使用指南.md)

## 💡 常用操作场景

## ⚠️ 常见问题3. 运行验证脚本查看详细问题

### 场景1：首次使用完整流程

```powershell4. 查看导入/验证日志文件

# 1. 配置数据库

python scripts\clickhouse_configurator.py### Q: 第一次使用，应该从哪里开始？



# 2. 创建表结构**A**: 按照本文档"5分钟快速上手"部分的步骤操作即可。### Web界面问题

python scripts\create_clickhouse_tables.py

1. 查看 [doc/README.md](./doc/README.md) 完整文档

# 3. 下载数据（所有货币对，2015至今）

python scripts\fxcm_data_downloader.py### Q: 配置文件在哪里？2. 查看 [doc/WEB_GUIDE.md](./doc/WEB_GUIDE.md) 使用指南



# 4. 导入数据（快速模式）**A**: `config/clickhouse_config.json`，使用 `clickhouse_configurator.py` 自动生成。3. 查看终端输出的错误信息

python scripts\fxcm_importer.py

4. 提交 GitHub Issue

# 5. 验证数据

python scripts\verify_data_consistency.py### Q: 数据下载很慢怎么办？



# 6. 转换时间框架**A**: 正常现象，10年M1数据量约15-20GB，需要2-4小时。可以先下载特定货币对和年份。---

python scripts\m1_timeframe_converter.py

```



### 场景2：只处理最近数据### Q: 导入失败怎么办？## 🎉 开始你的数据之旅！

```powershell

# 下载2024年数据**A**: 

python scripts\fxcm_data_downloader.py --start-year 2024

1. 检查ClickHouse服务是否运行### 使用ClickHouse数据库（推荐）

# 导入2024年数据

python scripts\fxcm_importer.py --start-year 20242. 检查配置文件是否正确```bash



# 验证2024年数据3. 查看错误日志：`logs/` 目录# 1. 创建表结构

python scripts\verify_data_consistency.py --start-year 2024

4. 使用 `--check-mode quick` 加快导入速度python scripts\create_clickhouse_tables.py

# 转换2024年数据

python scripts\m1_timeframe_converter.py --start-year 2024

```

### Q: Web界面无法访问？# 2. 导入数据

### 场景3：处理特定货币对

```powershell**A**: python 一键导入所有数据.py

# 完整流程：EURUSD和GBPUSD

python scripts\fxcm_data_downloader.py --pairs EURUSD GBPUSD1. 确认已运行 `start_web_ui.bat`

python scripts\fxcm_importer.py --pairs EURUSD GBPUSD

python scripts\verify_data_consistency.py --symbols EURUSD GBPUSD2. 检查端口5000是否被占用# 3. 验证数据

python scripts\m1_timeframe_converter.py --pairs EURUSD GBPUSD

```3. 尝试访问 `http://127.0.0.1:5000`python 一键验证所有数据.py



### 场景4：高质量数据验证

```powershell

# 使用全面验证模式导入### Q: 如何查看详细文档？# 4. 查询数据

python scripts\fxcm_importer.py --check-mode comprehensive

**A**: 查看 `doc/` 目录：python scripts\query_examples.py

# 使用全面模式验证一致性

python scripts\verify_data_consistency.py --mode comprehensive- **使用指南**: `doc/guides/````

```

- **参考文档**: `doc/reference/`

### 场景5：数据库模式转换（高性能）

```powershell- **完整文档**: `doc/README.md`### 使用Web界面

# 使用数据库SQL进行时间框架转换

python scripts\m1_timeframe_converter.py --mode database```bash

```

---python scripts/start_web.py

---

# 访问 http://localhost:5000

## ⚠️ 常见问题

## 📚 更多文档```

### Q: 第一次使用，应该从哪里开始？

**A**: 按照本文档"5分钟快速上手"部分的步骤操作即可。



### Q: 配置文件在哪里？- **[README.md](README.md)** - 完整项目说明**现在就开始使用吧！** 🚀

**A**: `config/clickhouse_config.json`，使用 `clickhouse_configurator.py` 自动生成。

- **[doc/README.md](doc/README.md)** - 详细文档索引

### Q: 如何查看脚本的所有参数？- **[doc/guides/](doc/guides/)** - 各工具使用指南

**A**: 使用 `--help` 参数，例如：- **[doc/reference/SCRIPT_INDEX.md](doc/reference/SCRIPT_INDEX.md)** - 脚本索引

```powershell- **[doc/CHANGELOG.md](doc/CHANGELOG.md)** - 版本更新历史

python scripts\fxcm_importer.py --help

```---



### Q: 数据下载很慢怎么办？## 🎉 开始使用

**A**: 正常现象，10年M1数据量约15-20GB，需要2-4小时。可以先下载特定货币对和年份。

```powershell

### Q: 导入失败怎么办？# 一键完成所有配置

**A**: python scripts\clickhouse_configurator.py

1. 检查ClickHouse服务是否运行

2. 检查配置文件是否正确# 开始下载和导入数据

3. 查看错误日志：`logs/` 目录download_fxcm_data.bat

4. 使用 `--check-mode fast` 加快导入速度import_fxcm_data.bat



### Q: Web界面无法访问？# 启动Web界面

**A**: start_web_ui.bat

1. 确认已运行 `start_web_ui.bat````

2. 检查端口5000是否被占用

3. 尝试访问 `http://127.0.0.1:5000`**祝您使用愉快！** 🚀



### Q: 如何查看详细文档？---

**A**: 查看 `doc/` 目录：

- **使用指南**: `doc/guides/`**需要帮助？** 查看 [doc/README.md](doc/README.md) 获取完整文档。

- **参考文档**: `doc/reference/`
- **完整文档**: `doc/README.md`

### Q: 快速模式和全面模式有什么区别？
**A**: 
- **快速模式** (fast): 只检查首尾记录，速度快（默认）
- **全面模式** (comprehensive): 逐条验证所有记录，更准确但较慢

### Q: 本地模式和数据库模式有什么区别？
**A**: 
- **本地模式** (local): 读取CSV文件转换，无需ClickHouse（默认）
- **数据库模式** (database): 使用ClickHouse SQL转换，速度更快但需要数据库

---

## 📚 更多文档

- **[README.md](README.md)** - 完整项目说明
- **[doc/README.md](doc/README.md)** - 详细文档索引
- **[doc/guides/](doc/guides/)** - 各工具使用指南
- **[doc/reference/SCRIPT_INDEX.md](doc/reference/SCRIPT_INDEX.md)** - 脚本索引
- **[doc/CHANGELOG.md](doc/CHANGELOG.md)** - 版本更新历史

---

## 🎉 开始使用

```powershell
# 一键完成所有配置
python scripts\clickhouse_configurator.py

# 开始下载和导入数据
download_fxcm_data.bat
import_fxcm_data.bat

# 启动Web界面
start_web_ui.bat
```

**祝您使用愉快！** 🚀

---

**需要帮助？** 查看 [doc/README.md](doc/README.md) 获取完整文档。
