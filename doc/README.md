# 📚 项目文档索引

本文件夹包含FXCM Forex数据管理系统的核心技术文档。

---

## 📂 文档结构

```
doc/
├── README.md                                    # 本文件 - 文档索引
├── CHANGELOG.md                                 # 项目更新日志
├── 日志文件路径检查.md                           # 日志系统配置说明
│
├── requirement/                                 # 需求文档
│   ├── fxcm_downloader_requirements.md          # FXCM下载器需求规格
│   └── data_consistency_verification_requirements.md  # 数据一致性验证需求
│
├── design/                                      # 设计文档
│   ├── fxcm_downloader_design.md                # FXCM下载器架构设计
│   └── data_consistency_verification_design.md  # 数据一致性验证设计
│
└── manual/                                      # 用户手册
    ├── fxcm_downloader_manual.md                # FXCM下载器用户手册
    └── data_consistency_verification_manual.md  # 数据一致性验证手册
```

---

## 🎯 快速导航

### 核心文档

| 文档 | 说明 | 推荐度 |
|-----|------|--------|
| [CHANGELOG.md](CHANGELOG.md) | **项目变更历史** - 记录所有版本更新 | ⭐⭐⭐⭐⭐ |
| [日志文件路径检查.md](日志文件路径检查.md) | **日志系统说明** - 日志配置和位置 | ⭐⭐⭐⭐ |

---

### 📋 FXCM数据下载器文档

#### 概述
FXCM数据下载器v2.0是一个功能强大的历史数据获取工具，支持命令行参数、自动重试、跳过已存在文件等特性。

#### 相关文档

| 文档类型 | 文件名 | 主要内容 |
|---------|--------|---------|
| **需求规格** | [requirement/fxcm_downloader_requirements.md](requirement/fxcm_downloader_requirements.md) | • 功能需求 (FR-1 ~ FR-12)<br>• 非功能需求 (NFR-1 ~ NFR-10)<br>• 用户故事和验收标准 |
| **架构设计** | [design/fxcm_downloader_design.md](design/fxcm_downloader_design.md) | • 系统架构图<br>• 类设计详解<br>• API集成方案<br>• 数据结构设计 |
| **用户手册** | [manual/fxcm_downloader_manual.md](manual/fxcm_downloader_manual.md) | • 安装指南<br>• 命令行参数说明<br>• 9+ 使用示例<br>• 重试机制说明<br>• 故障排查 (6个常见问题)<br>• 常见问题 (10个FAQ) |

#### 快速开始
```bash
# 查看帮助
python scripts/fxcm_data_downloader.py --help

# 默认下载（所有货币对，2015-现在）
python scripts/fxcm_data_downloader.py

# 自定义下载
python scripts/fxcm_data_downloader.py --pairs EURUSD GBPUSD --timeframes M1 --start-year 2020
```

---

### 🔍 数据一致性验证工具文档

#### 概述
数据一致性验证工具用于检查CSV文件与ClickHouse数据库之间的数据一致性，支持快速模式和详细模式。

#### 相关文档

| 文档类型 | 文件名 | 主要内容 |
|---------|--------|---------|
| **需求规格** | [requirement/data_consistency_verification_requirements.md](requirement/data_consistency_verification_requirements.md) | • 功能需求 (FR-1 ~ FR-12)<br>• 非功能需求 (NFR-1 ~ NFR-10)<br>• 验证策略和标准 |
| **架构设计** | [design/data_consistency_verification_design.md](design/data_consistency_verification_design.md) | • 双模式验证架构<br>• 数据库查询优化<br>• HTML报告生成<br>• 性能优化方案 |
| **用户手册** | [manual/data_consistency_verification_manual.md](manual/data_consistency_verification_manual.md) | • 快速模式 vs 详细模式<br>• HTML报告解读<br>• 常见问题处理<br>• 最佳实践 |

#### 快速开始
```bash
# 快速模式验证（推荐）
python scripts/verify_data_consistency.py

# 详细模式验证（逐条检查）
python scripts/verify_data_consistency.py --mode detailed

# 使用批处理文件
verify_consistency.bat
```

---

## 📊 文档更新说明

### 最近清理（2025-10-05）

删除了以下过时文档：
- ❌ 旧版本发布说明 (v4.x系列)
- ❌ 项目重组笔记
- ❌ 临时修复说明
- ❌ 重复的索引文件
- ❌ 过时的Web界面指南
- ❌ 早期的ClickHouse设计文档

### 保留的核心文档

保留了最重要和最新的文档：
- ✅ **CHANGELOG.md** - 完整的版本历史
- ✅ **FXCM下载器完整文档** (需求/设计/手册)
- ✅ **数据一致性验证完整文档** (需求/设计/手册)
- ✅ **日志系统配置文档**

---

## 🔗 相关资源

### 项目根目录文档

| 文档 | 位置 | 说明 |
|-----|------|-----|
| 主README | `../README.md` | 项目总览和快速开始 |
| FXCM下载器README | `../README_FXCM_DOWNLOADER.md` | 下载器功能介绍 |
| 脚本索引 | `../SCRIPT_INDEX.md` | 所有Python脚本的使用指南 |
| 项目结构 | `../PROJECT_STRUCTURE.md` | 完整的项目目录结构 |

### 在线资源

- 📘 **FXCM API**: https://candledata.fxcorporate.com/
- 📗 **ClickHouse文档**: https://clickhouse.com/docs/
- 📕 **Pandas文档**: https://pandas.pydata.org/docs/

---

## 💡 文档使用建议

### 新用户
1. 先阅读根目录的 `README.md` 了解项目概况
2. 查看 `SCRIPT_INDEX.md` 熟悉可用脚本
3. 根据需求查阅对应的用户手册 (manual/)

### 开发者
1. 阅读 `CHANGELOG.md` 了解项目演进
2. 查阅设计文档 (design/) 了解架构
3. 参考需求文档 (requirement/) 理解功能目标

### 维护者
1. 更新 `CHANGELOG.md` 记录每次变更
2. 保持设计文档与代码同步
3. 及时更新用户手册中的示例

---

## 📝 文档贡献指南

### 文档规范

1. **Markdown格式**: 所有文档使用Markdown格式
2. **UTF-8编码**: 确保中文正确显示
3. **清晰标题**: 使用层级标题组织内容
4. **代码示例**: 使用代码块并注明语言
5. **表格整理**: 复杂信息用表格展示

### 更新流程

1. 修改文档内容
2. 更新本索引文件（如有新增/删除）
3. 提交Git变更并注明文档变更
4. 在CHANGELOG.md中记录（重要更新）

---

**最后更新**: 2025-10-05  
**文档版本**: v5.0.2  
**文件总数**: 8个核心文档  
**维护者**: binphilxiao
