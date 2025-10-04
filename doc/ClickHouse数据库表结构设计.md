# ClickHouse外汇数据库表结构设计文档

## 📊 数据库架构概述

本设计采用**原始数据存储 + 物化视图自动聚合**的架构，实现高效的多时间框架数据管理。

---

## 🗄️ 数据库名称

```sql
forex_data
```

- **引擎**: Atomic
- **用途**: 存储外汇OHLCV历史数据
- **支持货币对**: EURUSD, GBPUSD, USDJPY, USDCAD, USDCHF, AUDUSD等

---

## 📋 表结构设计

### 1. M1原始数据表 (`ohlcv_m1`)

**用途**: 存储1分钟级别的原始K线数据

**表结构**:
```sql
CREATE TABLE forex_data.ohlcv_m1 (
    symbol      String      -- 交易对符号 (EURUSD, GBPUSD等)
    timestamp   DateTime    -- K线开盘时间 (UTC)
    open        Float64     -- 开盘价
    high        Float64     -- 最高价
    low         Float64     -- 最低价
    close       Float64     -- 收盘价
    volume      UInt64      -- 成交量
    created_at  DateTime    -- 数据入库时间 (自动生成)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)      -- 按年月分区
ORDER BY (symbol, timestamp)          -- 排序键
PRIMARY KEY (symbol, timestamp)       -- 主键
```

**索引策略**:
- 主键索引: `(symbol, timestamp)` - 支持快速按货币对和时间查询
- 分区: 按年月分区，便于数据管理和删除

**数据示例**:
```
symbol   | timestamp           | open    | high    | low     | close   | volume
---------|---------------------|---------|---------|---------|---------|--------
EURUSD   | 2025-01-01 00:00:00 | 1.1050  | 1.1052  | 1.1048  | 1.1051  | 1500
EURUSD   | 2025-01-01 00:01:00 | 1.1051  | 1.1053  | 1.1050  | 1.1052  | 1200
```

---

### 2. D1原始数据表 (`ohlcv_d1`)

**用途**: 存储日线级别的原始K线数据

**表结构**:
```sql
CREATE TABLE forex_data.ohlcv_d1 (
    symbol      String      -- 交易对符号
    date        Date        -- K线日期
    open        Float64     -- 开盘价
    high        Float64     -- 最高价
    low         Float64     -- 最低价
    close       Float64     -- 收盘价
    volume      UInt64      -- 成交量
    created_at  DateTime    -- 数据入库时间
)
ENGINE = MergeTree()
PARTITION BY toYYYY(date)             -- 按年分区
ORDER BY (symbol, date)               -- 排序键
PRIMARY KEY (symbol, date)            -- 主键
```

**索引策略**:
- 主键索引: `(symbol, date)` - 支持快速按货币对和日期查询
- 分区: 按年分区

---

### 3. M5聚合表 (`ohlcv_m5`)

**用途**: 存储5分钟K线数据（由M1自动聚合生成）

**表结构**:
```sql
CREATE TABLE forex_data.ohlcv_m5 (
    symbol      String
    timestamp   DateTime
    open        Float64
    high        Float64
    low         Float64
    close       Float64
    volume      UInt64
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (symbol, timestamp)
```

**物化视图** (`ohlcv_m5_mv`):
```sql
CREATE MATERIALIZED VIEW forex_data.ohlcv_m5_mv
TO forex_data.ohlcv_m5
AS
SELECT
    symbol,
    toStartOfInterval(timestamp, INTERVAL 5 MINUTE) AS timestamp,
    argMin(open, timestamp) AS open,      -- 5分钟内第一个open
    max(high) AS high,                     -- 5分钟内最高价
    min(low) AS low,                       -- 5分钟内最低价
    argMax(close, timestamp) AS close,     -- 5分钟内最后一个close
    sum(volume) AS volume                  -- 5分钟内总成交量
FROM forex_data.ohlcv_m1
GROUP BY symbol, timestamp
```

**自动触发**: 每次向`ohlcv_m1`插入数据时，自动触发聚合并写入`ohlcv_m5`

---

### 4. M15聚合表 (`ohlcv_m15`)

**用途**: 存储15分钟K线数据（由M1自动聚合生成）

**聚合逻辑**: 与M5类似，使用`INTERVAL 15 MINUTE`

---

### 5. M30聚合表 (`ohlcv_m30`)

**用途**: 存储30分钟K线数据（由M1自动聚合生成）

**聚合逻辑**: 与M5类似，使用`INTERVAL 30 MINUTE`

---

### 6. H1聚合表 (`ohlcv_h1`)

**用途**: 存储1小时K线数据（由M1自动聚合生成）

**表结构**:
```sql
CREATE TABLE forex_data.ohlcv_h1 (
    symbol      String
    timestamp   DateTime
    open        Float64
    high        Float64
    low         Float64
    close       Float64
    volume      UInt64
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (symbol, timestamp)
```

**物化视图**:
```sql
CREATE MATERIALIZED VIEW forex_data.ohlcv_h1_mv
TO forex_data.ohlcv_h1
AS
SELECT
    symbol,
    toStartOfHour(timestamp) AS timestamp,
    argMin(open, timestamp) AS open,
    max(high) AS high,
    min(low) AS low,
    argMax(close, timestamp) AS close,
    sum(volume) AS volume
FROM forex_data.ohlcv_m1
GROUP BY symbol, timestamp
```

---

## 🔄 数据流程图

```
原始数据导入:
┌─────────────┐
│  CSV文件    │
│  (M1/D1)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ ohlcv_m1    │ ← 1分钟原始数据
└──────┬──────┘
       │
       ├──────────┐ 物化视图自动聚合
       │          │
       ▼          ▼
┌──────────┐  ┌──────────┐
│ohlcv_m5  │  │ohlcv_m15 │
└──────────┘  └──────────┘
       │          │
       ▼          ▼
┌──────────┐  ┌──────────┐
│ohlcv_m30 │  │ohlcv_h1  │
└──────────┘  └──────────┘
```

---

## 📥 数据导入方式

### 方式1: 使用ClickHouse HTTP接口

```python
import requests
import pandas as pd

# 读取CSV
df = pd.read_csv('EURUSD_M1_2025_week_01.csv')

# 准备数据
data = df.to_csv(index=False, header=False)

# 插入数据
url = "http://192.168.2.168:8123"
query = "INSERT INTO forex_data.ohlcv_m1 FORMAT CSV"

response = requests.post(url, params={'query': query}, data=data)
```

### 方式2: 使用clickhouse-driver

```python
from clickhouse_driver import Client

client = Client(host='192.168.2.168', port=9000)

# 批量插入
data = [
    ('EURUSD', '2025-01-01 00:00:00', 1.1050, 1.1052, 1.1048, 1.1051, 1500),
    ('EURUSD', '2025-01-01 00:01:00', 1.1051, 1.1053, 1.1050, 1.1052, 1200),
]

client.execute(
    'INSERT INTO forex_data.ohlcv_m1 (symbol, timestamp, open, high, low, close, volume) VALUES',
    data
)
```

---

## 🔍 常用查询示例

### 1. 查询EURUSD的M5数据
```sql
SELECT * 
FROM forex_data.ohlcv_m5 
WHERE symbol = 'EURUSD' 
  AND timestamp >= '2025-01-01 00:00:00'
  AND timestamp < '2025-01-02 00:00:00'
ORDER BY timestamp
LIMIT 100
```

### 2. 查询多个货币对的最新价格
```sql
SELECT 
    symbol,
    max(timestamp) AS last_time,
    argMax(close, timestamp) AS last_price
FROM forex_data.ohlcv_m1
WHERE symbol IN ('EURUSD', 'GBPUSD', 'USDJPY')
GROUP BY symbol
```

### 3. 查询某货币对的日K线数据
```sql
SELECT * 
FROM forex_data.ohlcv_d1 
WHERE symbol = 'EURUSD' 
  AND date >= '2025-01-01'
ORDER BY date DESC
LIMIT 30
```

### 4. 查询某时间段的数据统计
```sql
SELECT 
    symbol,
    count() AS count,
    min(timestamp) AS start_time,
    max(timestamp) AS end_time
FROM forex_data.ohlcv_m1
WHERE timestamp >= '2025-01-01'
GROUP BY symbol
ORDER BY symbol
```

---

## ⚡ 性能优化建议

### 1. 分区策略
- M1数据按月分区，单月数据量约4000万条（6个货币对）
- D1数据按年分区，单年数据量约2000条

### 2. 索引优化
- 主键 `(symbol, timestamp)` 支持最常见的查询模式
- 避免在查询中使用 `SELECT *`，指定具体字段

### 3. 批量插入
- 使用批量插入而非单条插入
- 建议批次大小: 10000-100000条

### 4. 物化视图刷新
- 物化视图是实时触发的，无需手动刷新
- 如需重建历史数据，可以先删除物化视图，再重新创建

---

## 🛠️ 维护操作

### 删除旧数据分区
```sql
-- 删除2020年的M1数据
ALTER TABLE forex_data.ohlcv_m1 DROP PARTITION '202001'
```

### 优化表
```sql
OPTIMIZE TABLE forex_data.ohlcv_m1 FINAL
```

### 查看表大小
```sql
SELECT 
    table,
    formatReadableSize(sum(bytes)) AS size
FROM system.parts
WHERE database = 'forex_data'
  AND active
GROUP BY table
ORDER BY sum(bytes) DESC
```

---

## 📊 数据容量估算

假设6个货币对，10年历史数据：

| 时间框架 | 每天条数 | 年数据量 | 10年数据量 | 估计大小 |
|---------|---------|---------|-----------|---------|
| M1      | 1440×6  | 315万   | 3150万    | ~2GB    |
| M5      | 288×6   | 63万    | 630万     | ~400MB  |
| M15     | 96×6    | 21万    | 210万     | ~150MB  |
| M30     | 48×6    | 10.5万  | 105万     | ~80MB   |
| H1      | 24×6    | 5.2万   | 52万      | ~40MB   |
| D1      | 6       | 2190    | 21900     | ~2MB    |
| **总计** |         |         | **4168万** | **~2.7GB** |

---

## ✅ 创建步骤

1. 确保ClickHouse服务器运行正常
2. 检查配置文件 `config/clickhouse_config.json`
3. 运行建表脚本: `python scripts/create_clickhouse_tables.py`
4. 验证表创建: `SHOW TABLES FROM forex_data`

---

## 📝 注意事项

1. **时区**: 所有时间戳使用UTC时区
2. **精度**: 价格使用Float64，保证精度
3. **物化视图**: 只对新插入的数据生效，已有数据需要手动填充
4. **备份**: 定期备份数据库
5. **监控**: 监控表大小和查询性能

---

**创建日期**: 2025-10-04  
**版本**: 1.0  
**作者**: FXCM数据管理系统
