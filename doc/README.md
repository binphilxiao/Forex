# 📚 FXCM 外汇数据管理系统 - 完整文档# 📚 项目文档索引



> **版本**: v5.0.6 | **更新**: 2025-10-06本文件夹包含FXCM Forex数据管理系统的核心技术文档。



## 📖 文档导航---



### 🚀 快速开始## 📂 文档结构

- **[根目录/QUICKSTART.md](../QUICKSTART.md)** - 5分钟快速上手指南

- **[根目录/README.md](../README.md)** - 项目完整说明```

doc/

---├── README.md                                    # 本文件 - 文档索引

├── CHANGELOG.md                                 # 项目更新日志

## 📁 文档分类├── 日志文件路径检查.md                           # 日志系统配置说明

│

### 1. 使用指南 (guides/)├── requirement/                                 # 需求文档

│   ├── fxcm_downloader_requirements.md          # FXCM下载器需求规格

#### 工具使用手册│   └── data_consistency_verification_requirements.md  # 数据一致性验证需求

- **[CONFIG_USAGE.md](guides/CONFIG_USAGE.md)** - 配置文件使用说明 ⭐│

- **[CLICKHOUSE_CONFIGURATOR.md](guides/CLICKHOUSE_CONFIGURATOR.md)** - 数据库配置工具├── design/                                      # 设计文档

- **[FXCM_DOWNLOADER.md](guides/FXCM_DOWNLOADER.md)** - 数据下载器使用指南│   ├── fxcm_downloader_design.md                # FXCM下载器架构设计

- **[FXCM_IMPORTER.md](guides/FXCM_IMPORTER.md)** - 数据导入器使用指南│   └── data_consistency_verification_design.md  # 数据一致性验证设计

- **[M1_CONVERTER.md](guides/M1_CONVERTER.md)** - M1时间框架转换器指南│

└── manual/                                      # 用户手册

#### 详细手册 (manual/)    ├── fxcm_downloader_manual.md                # FXCM下载器用户手册

- **[fxcm_downloader_manual.md](manual/fxcm_downloader_manual.md)** - 下载器详细手册    └── data_consistency_verification_manual.md  # 数据一致性验证手册

- **[fxcm_importer_manual.md](manual/fxcm_importer_manual.md)** - 导入器详细手册```

- **[m1_converter_manual.md](manual/m1_converter_manual.md)** - 转换器详细手册

- **[m1_converter_modes.md](manual/m1_converter_modes.md)** - 转换器模式说明---

- **[m1_converter_quick_reference.md](manual/m1_converter_quick_reference.md)** - 转换器快速参考

## 🎯 快速导航

---

### 核心文档

### 2. 参考文档 (reference/)

| 文档 | 说明 | 推荐度 |

- **[SCRIPT_INDEX.md](reference/SCRIPT_INDEX.md)** - 所有脚本索引和分类 ⭐|-----|------|--------|

- **[PROJECT_STRUCTURE.md](reference/PROJECT_STRUCTURE.md)** - 项目结构说明| [CHANGELOG.md](CHANGELOG.md) | **项目变更历史** - 记录所有版本更新 | ⭐⭐⭐⭐⭐ |

| [日志文件路径检查.md](日志文件路径检查.md) | **日志系统说明** - 日志配置和位置 | ⭐⭐⭐⭐ |

---

---

### 3. 开发文档 (development/)

### 📋 FXCM数据下载器文档

- **[GIT_COMMIT_GUIDE.md](development/GIT_COMMIT_GUIDE.md)** - Git提交规范

- **[CHANGELOG_FILE_RENAME.md](development/CHANGELOG_FILE_RENAME.md)** - 文件重命名历史#### 概述

FXCM数据下载器v2.0是一个功能强大的历史数据获取工具，支持命令行参数、自动重试、跳过已存在文件等特性。

---

#### 相关文档

### 4. 变更日志

| 文档类型 | 文件名 | 主要内容 |

- **[CHANGELOG.md](CHANGELOG.md)** - 版本更新历史 📝|---------|--------|---------|

| **需求规格** | [requirement/fxcm_downloader_requirements.md](requirement/fxcm_downloader_requirements.md) | • 功能需求 (FR-1 ~ FR-12)<br>• 非功能需求 (NFR-1 ~ NFR-10)<br>• 用户故事和验收标准 |

---| **架构设计** | [design/fxcm_downloader_design.md](design/fxcm_downloader_design.md) | • 系统架构图<br>• 类设计详解<br>• API集成方案<br>• 数据结构设计 |

| **用户手册** | [manual/fxcm_downloader_manual.md](manual/fxcm_downloader_manual.md) | • 安装指南<br>• 命令行参数说明<br>• 9+ 使用示例<br>• 重试机制说明<br>• 故障排查 (6个常见问题)<br>• 常见问题 (10个FAQ) |

### 5. 设计文档 (design/)

#### 快速开始

- 数据库表结构设计```bash

- 系统架构设计# 查看帮助

- 性能优化方案python scripts/fxcm_data_downloader.py --help



---# 默认下载（所有货币对，2015-现在）

python scripts/fxcm_data_downloader.py

### 6. 需求文档 (requirement/)

# 自定义下载

- 功能需求说明python scripts/fxcm_data_downloader.py --pairs EURUSD GBPUSD --timeframes M1 --start-year 2020

- 技术需求规格```



------



## 🎯 按使用场景查找文档### 🔍 数据一致性验证工具文档



### 我是新用户，如何开始？#### 概述

1. **[../QUICKSTART.md](../QUICKSTART.md)** - 快速开始指南数据一致性验证工具用于检查CSV文件与ClickHouse数据库之间的数据一致性，支持快速模式和详细模式。

2. **[guides/CONFIG_USAGE.md](guides/CONFIG_USAGE.md)** - 配置数据库连接

3. **[reference/SCRIPT_INDEX.md](reference/SCRIPT_INDEX.md)** - 了解所有可用脚本#### 相关文档



### 我想下载数据| 文档类型 | 文件名 | 主要内容 |

- **[guides/FXCM_DOWNLOADER.md](guides/FXCM_DOWNLOADER.md)** - 下载器使用指南|---------|--------|---------|

- **[manual/fxcm_downloader_manual.md](manual/fxcm_downloader_manual.md)** - 详细手册| **需求规格** | [requirement/data_consistency_verification_requirements.md](requirement/data_consistency_verification_requirements.md) | • 功能需求 (FR-1 ~ FR-12)<br>• 非功能需求 (NFR-1 ~ NFR-10)<br>• 验证策略和标准 |

| **架构设计** | [design/data_consistency_verification_design.md](design/data_consistency_verification_design.md) | • 双模式验证架构<br>• 数据库查询优化<br>• HTML报告生成<br>• 性能优化方案 |

### 我想导入数据到数据库| **用户手册** | [manual/data_consistency_verification_manual.md](manual/data_consistency_verification_manual.md) | • 快速模式 vs 详细模式<br>• HTML报告解读<br>• 常见问题处理<br>• 最佳实践 |

- **[guides/FXCM_IMPORTER.md](guides/FXCM_IMPORTER.md)** - 导入器使用指南

- **[manual/fxcm_importer_manual.md](manual/fxcm_importer_manual.md)** - 详细手册#### 快速开始

```bash

### 我想转换时间框架# 快速模式验证（推荐）

- **[guides/M1_CONVERTER.md](guides/M1_CONVERTER.md)** - 转换器使用指南python scripts/verify_data_consistency.py

- **[manual/m1_converter_manual.md](manual/m1_converter_manual.md)** - 详细手册

- **[manual/m1_converter_modes.md](manual/m1_converter_modes.md)** - 模式说明# 详细模式验证（逐条检查）

python scripts/verify_data_consistency.py --mode detailed

### 我想了解所有脚本功能

- **[reference/SCRIPT_INDEX.md](reference/SCRIPT_INDEX.md)** - 完整脚本索引# 使用批处理文件

verify_consistency.bat

### 我想配置数据库连接```

- **[guides/CONFIG_USAGE.md](guides/CONFIG_USAGE.md)** - 配置文件使用说明

- **[guides/CLICKHOUSE_CONFIGURATOR.md](guides/CLICKHOUSE_CONFIGURATOR.md)** - 配置工具指南---



### 我是开发者，想贡献代码## 📊 文档更新说明

- **[development/GIT_COMMIT_GUIDE.md](development/GIT_COMMIT_GUIDE.md)** - Git提交规范

- **[reference/PROJECT_STRUCTURE.md](reference/PROJECT_STRUCTURE.md)** - 项目结构### 最近清理（2025-10-05）

- **[CHANGELOG.md](CHANGELOG.md)** - 版本历史

删除了以下过时文档：

---- ❌ 旧版本发布说明 (v4.x系列)

- ❌ 项目重组笔记

## 📊 文档统计- ❌ 临时修复说明

- ❌ 重复的索引文件

### 使用指南- ❌ 过时的Web界面指南

- 工具手册: 5个- ❌ 早期的ClickHouse设计文档

- 详细手册: 5个

- **总计**: 10个文档### 保留的核心文档



### 参考文档保留了最重要和最新的文档：

- 脚本索引: 1个- ✅ **CHANGELOG.md** - 完整的版本历史

- 项目结构: 1个- ✅ **FXCM下载器完整文档** (需求/设计/手册)

- **总计**: 2个文档- ✅ **数据一致性验证完整文档** (需求/设计/手册)

- ✅ **日志系统配置文档**

### 开发文档

- Git规范: 1个---

- 变更历史: 1个

- **总计**: 2个文档## 🔗 相关资源



### 其他文档### 项目根目录文档

- 变更日志: 1个

- 设计文档: 若干| 文档 | 位置 | 说明 |

- 需求文档: 若干|-----|------|-----|

| 主README | `../README.md` | 项目总览和快速开始 |

---| FXCM下载器README | `../README_FXCM_DOWNLOADER.md` | 下载器功能介绍 |

| 脚本索引 | `../SCRIPT_INDEX.md` | 所有Python脚本的使用指南 |

## 🔍 文档搜索提示| 项目结构 | `../PROJECT_STRUCTURE.md` | 完整的项目目录结构 |



### 常见关键词### 在线资源

- **配置** → `guides/CONFIG_USAGE.md`

- **下载** → `guides/FXCM_DOWNLOADER.md`- 📘 **FXCM API**: https://candledata.fxcorporate.com/

- **导入** → `guides/FXCM_IMPORTER.md`- 📗 **ClickHouse文档**: https://clickhouse.com/docs/

- **转换** → `guides/M1_CONVERTER.md`- 📕 **Pandas文档**: https://pandas.pydata.org/docs/

- **脚本** → `reference/SCRIPT_INDEX.md`

- **项目结构** → `reference/PROJECT_STRUCTURE.md`---



---## 💡 文档使用建议



## 📝 文档维护### 新用户

1. 先阅读根目录的 `README.md` 了解项目概况

### 文档版本2. 查看 `SCRIPT_INDEX.md` 熟悉可用脚本

所有文档应包含版本号和更新日期：3. 根据需求查阅对应的用户手册 (manual/)

```markdown

> **版本**: v5.0.6 | **更新**: 2025-10-06### 开发者

```1. 阅读 `CHANGELOG.md` 了解项目演进

2. 查阅设计文档 (design/) 了解架构

### 文档链接检查3. 参考需求文档 (requirement/) 理解功能目标

定期检查文档中的链接是否有效，确保所有引用的文件都存在。

### 维护者

### 文档更新原则1. 更新 `CHANGELOG.md` 记录每次变更

1. 功能变更时同步更新相关文档2. 保持设计文档与代码同步

2. 保持文档简洁明了3. 及时更新用户手册中的示例

3. 提供足够的示例代码

4. 及时更新版本号---



---## 📝 文档贡献指南



## 🆘 需要帮助？### 文档规范



### 快速获取帮助1. **Markdown格式**: 所有文档使用Markdown格式

1. 查看 **[../QUICKSTART.md](../QUICKSTART.md)** 快速开始2. **UTF-8编码**: 确保中文正确显示

2. 查看 **[reference/SCRIPT_INDEX.md](reference/SCRIPT_INDEX.md)** 脚本索引3. **清晰标题**: 使用层级标题组织内容

3. 查看对应工具的使用指南4. **代码示例**: 使用代码块并注明语言

4. 查看详细手册获取更多信息5. **表格整理**: 复杂信息用表格展示



### 联系方式### 更新流程

- GitHub Issues

- 项目文档反馈1. 修改文档内容

2. 更新本索引文件（如有新增/删除）

---3. 提交Git变更并注明文档变更

4. 在CHANGELOG.md中记录（重要更新）

**祝您使用愉快！** 📚

---

**最后更新**: 2025-10-05  
**文档版本**: v5.0.2  
**文件总数**: 8个核心文档  
**维护者**: binphilxiao
