# FXCM数据下载器重试机制说明

## 📋 概述

`fxcm_data_downloader.py` 内置了智能重试机制，可以自动重试失败的下载请求，提高数据下载的成功率。

## ⚙️ 重试机制特性

### 1. 可配置的重试次数

通过命令行参数 `--max-retries` 控制最大重试次数：

```bash
# 默认重试5次
python scripts\fxcm_data_downloader.py

# 自定义重试3次
python scripts\fxcm_data_downloader.py --max-retries 3

# 不重试（仅尝试1次）
python scripts\fxcm_data_downloader.py --max-retries 1

# 重试10次（适合网络不稳定的环境）
python scripts\fxcm_data_downloader.py --max-retries 10
```

### 2. 重试策略

#### 适用场景：
- ✅ **网络超时**：连接超时或请求超时
- ✅ **临时性错误**：服务器临时不可用
- ✅ **404错误**：数据不存在时也会重试（某些时候数据可能延迟上传）

#### 不重试场景：
- ❌ **HTTP状态码非200/404**：其他HTTP错误（如403、500等）不重试
- ❌ **CSV格式错误**：数据格式无法识别时不重试

### 3. 重试延迟

每次重试之间会有 **0.5秒** 的延迟，避免频繁请求对服务器造成压力。

## 📊 重试日志

重试信息会记录在日志文件中，方便追踪：

```
2025-10-05 13:33:55 - INFO - Max Retries: 3
2025-10-05 13:33:58 - DEBUG - ❌ 404 Not Found (after 3 retries): https://candledata.fxcorporate.com/D1/EURUSD/2024.csv.gz
```

## 🎯 使用示例

### 示例1：下载EURUSD数据，重试3次

```bash
python scripts\fxcm_data_downloader.py --pairs EURUSD --max-retries 3
```

**输出显示：**
```
============================================================
FXCM Historical Data Downloader v2.0
============================================================
Currency Pairs: EURUSD
Timeframes: M1, D1
Date Range: 2015 - 2025
Output Directory: C:\Users\...\Forex\fxcm_data
Max Retries: 3
============================================================
```

### 示例2：网络不稳定环境，增加重试次数

```bash
python scripts\fxcm_data_downloader.py --max-retries 10
```

### 示例3：快速测试，不重试

```bash
python scripts\fxcm_data_downloader.py --pairs EURUSD --timeframes D1 --start-year 2024 --max-retries 1
```

## 💡 最佳实践

### 推荐配置

| 场景 | 推荐重试次数 | 说明 |
|-----|------------|-----|
| 🏠 **家庭网络（稳定）** | 3-5次 | 默认5次已足够 |
| 📶 **移动网络（不稳定）** | 8-10次 | 增加重试提高成功率 |
| 🏢 **企业网络（代理）** | 5-8次 | 代理可能导致间歇性失败 |
| ⚡ **测试环境** | 1-2次 | 快速失败，节省时间 |

### 性能影响

- **低重试次数（1-3次）**：更快失败，适合测试
- **中等重试次数（5-8次）**：平衡速度和可靠性，适合日常使用
- **高重试次数（10+次）**：最大化成功率，但可能增加总体下载时间

## 🔧 代码实现

### 内部实现

```python
def _download_with_retry(self, url: str) -> Optional[pd.DataFrame]:
    """下载数据并支持重试"""
    for attempt in range(self.max_retries):
        try:
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                # 成功下载
                return process_data(response)
            
            elif response.status_code == 404:
                # 404错误 - 重试
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)  # 延迟0.5秒
                    continue
                else:
                    # 最后一次重试失败
                    return None
        
        except Exception as e:
            # 网络错误 - 重试
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
                continue
            else:
                return None
    
    return None
```

### 初始化配置

```python
def __init__(self, max_retries: int = 5, retry_delay: float = 0.5):
    self.max_retries = max_retries      # 最大重试次数
    self.retry_delay = retry_delay      # 重试延迟（秒）
```

## 📈 重试统计

下载完成后，摘要报告会显示：

```
============================================================
Download Summary
============================================================
Total Files Processed: 100
  ✅ Downloaded: 95
  ⏭️  Skipped (existing): 3
  ❌ Failed/Not Available: 2    ← 重试后仍失败的文件数
Total Records Downloaded: 5,234,567
Time Elapsed: 1234.5 seconds
============================================================
```

**失败原因可能包括：**
- 数据真的不存在（如未来日期）
- 服务器永久性错误
- 网络彻底断开
- 达到最大重试次数后仍失败

## ⚠️ 注意事项

1. **重试次数不是越多越好**
   - 如果数据真的不存在，重试再多次也无济于事
   - 过多重试会延长总体下载时间

2. **日志文件会记录所有重试**
   - 可以通过日志文件分析失败原因
   - 日志位置：`logs/fxcm_download_YYYYMMDD_HHMMSS.log`

3. **组合使用其他参数**
   ```bash
   # 下载特定范围，自定义重试
   python scripts\fxcm_data_downloader.py \
       --pairs EURUSD GBPUSD \
       --timeframes M1 \
       --start-year 2020 \
       --end-year 2023 \
       --max-retries 5
   ```

## 🔍 故障排查

### 如果大量文件下载失败：

1. **检查网络连接**
   ```bash
   # 测试能否访问FXCM API
   curl https://candledata.fxcorporate.com/D1/EURUSD/2021.csv.gz
   ```

2. **查看日志文件**
   ```bash
   # 查看最新日志
   Get-Content logs\fxcm_download_*.log | Select-Object -Last 50
   ```

3. **增加重试次数**
   ```bash
   python scripts\fxcm_data_downloader.py --max-retries 10
   ```

4. **减少并发量**
   - 暂时下载单个货币对
   - 分批下载不同年份

---

**相关文档：**
- [FXCM下载器用户手册](manual/fxcm_downloader_manual.md)
- [FXCM下载器设计文档](design/fxcm_downloader_design.md)
- [主README](../README_FXCM_DOWNLOADER.md)

**最后更新**: 2025-10-05
**版本**: v2.0.0
