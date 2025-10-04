# 📚 FXCM 数据处理系统 - 文档中心

> 这里包含了项目的所有详细文档

## 📖 文档导航

### 核心文档

#### 1. [README.md](./README.md) 📘
**项目总览和完整说明**
- 项目介绍和功能特点
- 详细的安装和使用说明
- 数据结构和文件组织
- 完整的版本历史

#### 2. [WEB_GUIDE.md](./WEB_GUIDE.md) 🌐
**Web界面详细使用指南**
- Flask Web界面完整说明
- 功能特性详解
- 使用流程和最佳实践
- 故障排除指南

### 开发文档

#### 3. [REQUIREMENTS.md](./REQUIREMENTS.md) 📋
**需求规格文档**
- 功能需求 (FR)
- 非功能需求 (NFR)
- 数据需求 (DR)
- 项目里程碑

#### 4. [CHANGELOG.md](./CHANGELOG.md) 📜
**版本更新历史**
- 详细的版本变更记录
- 新增功能、Bug修复、改进说明
- 版本时间线

### 发布说明

#### 5. [v4.1.0_RELEASE_NOTES.md](./v4.1.0_RELEASE_NOTES.md) 🎉
**v4.1.0 版本发布说明**
- 数据分析可视化集成
- 自动打开HTML报告
- 技术实现细节

#### 6. [v4.1.1_FIX_NOTES.md](./v4.1.1_FIX_NOTES.md) 🔧
**v4.1.1 修复说明**
- 脚本文件名修正
- 终端输出问题修复
- 详细的技术分析

### 维护文档

#### 7. [CLEANUP_NOTES.md](./CLEANUP_NOTES.md) 🧹
**代码清理说明**
- Tkinter GUI 移除记录
- 项目结构简化
- 清理统计和影响

#### 8. [ENCODING_FIX.md](./ENCODING_FIX.md) 🔤
**编码问题修复文档**
- Windows UTF-8 编码问题
- 修复方案和技术细节

---

## 🎯 快速查找

### 我是新用户
👉 先看 [../QUICKSTART.md](../QUICKSTART.md)  
👉 再看 [README.md](./README.md)

### 我要使用Web界面
👉 查看 [WEB_GUIDE.md](./WEB_GUIDE.md)

### 我遇到了问题
👉 查看 [WEB_GUIDE.md](./WEB_GUIDE.md) 的故障排除部分  
👉 查看 [v4.1.1_FIX_NOTES.md](./v4.1.1_FIX_NOTES.md)

### 我想了解版本历史
👉 查看 [CHANGELOG.md](./CHANGELOG.md)

### 我是开发者
👉 查看 [REQUIREMENTS.md](./REQUIREMENTS.md)  
👉 查看所有发布说明文档

---

## 📂 文档组织原则

```
Forex/
├── QUICKSTART.md          ⭐ 根目录：仅快速开始指南
│
└── doc/                   📚 所有详细文档都在这里
    ├── README.md          项目总览
    ├── WEB_GUIDE.md       Web界面指南
    ├── REQUIREMENTS.md    需求文档
    ├── CHANGELOG.md       版本历史
    ├── v4.x.x_*.md        发布说明
    ├── CLEANUP_NOTES.md   维护记录
    └── ENCODING_FIX.md    技术说明
```

---

## 🔄 文档更新原则

1. **根目录** - 只保留 `QUICKSTART.md` 快速开始指南
2. **doc文件夹** - 所有其他文档都归档在这里
3. **版本发布** - 重要版本的发布说明保留为独立文件
4. **技术文档** - 特定技术问题的修复说明独立存档

---

**文档版本**: v4.1.2  
**最后更新**: 2025-01-04
