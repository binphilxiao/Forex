# 🚀 FXCM 数据处理系统 - 快速开始

> **版本**: v4.2.0 | **更新**: 2025-10-04

## ⚡ 核心命令

### 数据库操作（推荐）
```bash
# 1. 创建表结构（首次使用）
python scripts\create_clickhouse_tables.py

# 2. 导入所有数据
python 一键导入所有数据.py

# 3. 验证数据质量
python 一键验证所有数据.py

# 4. 查询示例
python scripts\query_examples.py

# 5. 查看表信息
python scripts\view_clickhouse_tables.py
```

### Web界面（可选）
```powershell
# 双击即可启动
启动Web界面.bat

# 或命令行启动
python scripts/start_web.py

# 浏览器访问
http://localhost:5000
```

---

## 📋 数据库快速开始

### 1️⃣ 准备工作
- ✅ ClickHouse服务器运行中（192.168.2.168:8123）
- ✅ 配置文件正确（`config/clickhouse_config.json`）
- ✅ CSV文件在 `fxcm_data/` 文件夹

### 2️⃣ 导入数据
```bash
python 一键导入所有数据.py
# 预计时间：30-60分钟
# 自动导入所有M1和D1数据
# 实时显示进度和日志
```

### 3️⃣ 验证数据
```bash
python 一键验证所有数据.py
# 预计时间：10-30秒
# 全面检查数据质量
# 自动生成评分报告
```

---

## 🎯 主要功能

### ClickHouse数据库（推荐）
| 功能 | 命令 | 时间 |
|------|------|------|
| 📥 导入数据 | `python 一键导入所有数据.py` | 30-60分钟 |
| ✅ 验证数据 | `python 一键验证所有数据.py` | 10-30秒 |
| 🔍 查询数据 | `python scripts\query_examples.py` | 毫秒级 |
| 📊 查看表 | `python scripts\view_clickhouse_tables.py` | 即时 |

### Web界面（可选）
| 功能 | 说明 | 时间 |
|------|------|------|
| 📥 下载数据 | 从FXCM下载M1/D1原始数据 | 2-4小时 |
| 🔄 转换数据 | M1转换为M5/M15/M30/H1 | 1-3小时 |
| 📊 分析数据 | 生成完整性报告和可视化 | 5-10分钟 |

---

## 📊 数据库状态（当前）

```
总记录数: 26,569,070 条
├── M1:  20,126,872 条 (6货币对: AUDUSD/EURUSD/GBPUSD/USDJPY/USDCAD/USDCHF)
├── D1:     12,971 条 (6货币对)
├── M5:  4,058,445 条 (物化视图自动生成)
├── M15: 1,354,303 条 (物化视图自动生成)
├── M30:   677,591 条 (物化视图自动生成)
└── H1:    338,888 条 (物化视图自动生成)

数据质量评分: A+
物化视图: 4/4 正常工作
```

---

## 📦 系统要求

```bash
# Python 版本
Python 3.7+

# 依赖安装
pip install flask pandas requests

# 存储空间
全量数据约 50GB
```

---

## 🌐 访问方式

- **本机**: http://localhost:5000
- **局域网**: http://[你的IP]:5000
- **手机/平板**: 支持移动设备访问

### 查看本机IP
```powershell
# Windows
ipconfig | findstr IPv4

# Linux/Mac
ifconfig | grep inet
```

---

## 📚 详细文档

完整文档请查看 **[doc](./doc/)** 文件夹：

### 数据库相关
- **[一键脚本使用指南.md](./doc/一键脚本使用指南.md)** ⭐ 导入验证脚本详细说明
- **[数据库表结构设计.md](./doc/数据库表结构设计.md)** - ClickHouse表结构
- **[数据导入使用指南.md](./doc/数据导入使用指南.md)** - 数据导入详细说明
- **[数据验证报告.md](./doc/数据验证报告.md)** - 数据质量验证报告

### Web界面相关
- **[README.md](./doc/README.md)** - 完整项目说明
- **[WEB_GUIDE.md](./doc/WEB_GUIDE.md)** - Web界面详细指南
- **[CHANGELOG.md](./doc/CHANGELOG.md)** - 版本更新历史
- **[REQUIREMENTS.md](./doc/REQUIREMENTS.md)** - 需求文档

---

## ⏱️ 时间预估

| 操作 | 时间 | 说明 |
|------|------|------|
| 创建表结构 | 5秒 | 首次使用执行一次 |
| 导入D1数据 | 3-5秒 | 42个文件 |
| 导入M1数据 | 30-60分钟 | 3290个文件 |
| 验证数据 | 10-30秒 | 全面质量检查 |
| 查询数据 | 毫秒级 | ClickHouse高性能 |

---

## ⚠️ 常见问题

### 数据库相关

#### Q: 导入时提示"连接失败"？
A: 检查ClickHouse服务器是否运行，配置是否正确

#### Q: 导入很慢怎么办？
A: 正常现象，M1数据量大（2千万条），预计30-60分钟

#### Q: 某个文件导入失败？
A: 单个文件失败不影响其他文件，查看错误信息处理

#### Q: 如何重新导入？
A: 直接运行导入脚本，已存在的数据会自动跳过

#### Q: 验证评分低怎么办？
A: 查看验证报告中的详细问题，根据建议处理

### Web界面相关

#### Q: 终端没有输出？
A: 这是正常的，请确保运行了 `python scripts/start_web.py`

#### Q: 下载很多404错误？
A: 正常现象，某些周次的数据FXCM不提供

#### Q: 如何停止任务？
A: 点击Web界面的 "⏹ 停止任务" 按钮

#### Q: 报告在哪里？
A: 分析完成后自动打开，也可在 `logs/` 文件夹查看

---

## 🆘 获取帮助

### 数据库问题
1. 查看 [doc/一键脚本使用指南.md](./doc/一键脚本使用指南.md) ⭐
2. 查看 [doc/数据导入使用指南.md](./doc/数据导入使用指南.md)
3. 运行验证脚本查看详细问题
4. 查看导入/验证日志文件

### Web界面问题
1. 查看 [doc/README.md](./doc/README.md) 完整文档
2. 查看 [doc/WEB_GUIDE.md](./doc/WEB_GUIDE.md) 使用指南
3. 查看终端输出的错误信息
4. 提交 GitHub Issue

---

## 🎉 开始你的数据之旅！

### 使用ClickHouse数据库（推荐）
```bash
# 1. 创建表结构
python scripts\create_clickhouse_tables.py

# 2. 导入数据
python 一键导入所有数据.py

# 3. 验证数据
python 一键验证所有数据.py

# 4. 查询数据
python scripts\query_examples.py
```

### 使用Web界面
```bash
python scripts/start_web.py
# 访问 http://localhost:5000
```

**现在就开始使用吧！** 🚀
