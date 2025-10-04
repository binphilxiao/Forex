# 🚀 FXCM 数据处理系统 - 快速开始

> **版本**: v4.1.2 | **更新**: 2025-01-04

## ⚡ 30秒快速启动

### Windows 用户（推荐）
```powershell
# 双击即可启动
启动Web界面.bat
```

### 所有平台
```bash
# 启动Web服务器
python scripts/start_web.py

# 浏览器访问
http://localhost:5000
```

---

## 📋 三步开始使用

### 1️⃣ 配置下载选项
在Web界面中设置：
- ✅ 选择外汇对（EUR/USD, GBP/USD等）
- ✅ 设置年份范围（2015-2025）
- ✅ 配置重试选项

### 2️⃣ 下载数据
```
点击 "📥 下载数据" → 观察终端输出 → 等待完成
```

### 3️⃣ 转换和分析
```
点击 "🔄 转换数据" → 生成多时间周期数据
点击 "📊 分析数据" → 自动打开可视化报告
```

---

## 🎯 主要功能

| 功能 | 说明 | 时间 |
|------|------|------|
| 📥 下载数据 | 从FXCM下载M1/D1原始数据 | 2-4小时 |
| 🔄 转换数据 | M1转换为M5/M15/M30/H1 | 1-3小时 |
| 📊 分析数据 | 生成完整性报告和可视化 | 5-10分钟 |

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

- **[README.md](./doc/README.md)** - 完整项目说明
- **[WEB_GUIDE.md](./doc/WEB_GUIDE.md)** - Web界面详细指南
- **[CHANGELOG.md](./doc/CHANGELOG.md)** - 版本更新历史
- **[REQUIREMENTS.md](./doc/REQUIREMENTS.md)** - 需求文档

---

## ⚠️ 常见问题

### Q: 终端没有输出？
A: 这是正常的，请确保运行了 `python scripts/start_web.py`

### Q: 下载很多404错误？
A: 正常现象，某些周次的数据FXCM不提供

### Q: 如何停止任务？
A: 点击Web界面的 "⏹ 停止任务" 按钮

### Q: 报告在哪里？
A: 分析完成后自动打开，也可在 `logs/` 文件夹查看

---

## 🆘 获取帮助

1. 查看 [doc/README.md](./doc/README.md) 完整文档
2. 查看 [doc/WEB_GUIDE.md](./doc/WEB_GUIDE.md) 使用指南
3. 查看终端输出的错误信息
4. 提交 GitHub Issue

---

## 🎉 开始你的数据之旅！

```bash
python scripts/start_web.py
```

**现在就访问 http://localhost:5000 开始使用吧！** 🚀
