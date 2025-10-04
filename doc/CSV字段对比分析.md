# CSV文件与数据库表字段对比分析

## 📊 字段对比

### CSV文件结构（FXCM数据）

#### M1数据示例
```csv
DateTime,Open,High,Low,Close
2015-01-04 22:00:00,1.19552,1.19552,1.19355,1.19404
2015-01-04 22:01:00,1.19404,1.19404,1.18986,1.191
```

#### D1数据示例
```csv
DateTime,Open,High,Low,Close
2015-01-01 22:00:00,1.20992,1.20992,1.19981,1.19995
2015-01-03 22:00:00,1.19995,1.20055,1.19502,1.19552
```

**CSV字段列表**:
1. `DateTime` - 日期时间
2. `Open` - 开盘价
3. `High` - 最高价
4. `Low` - 最低价
5. `Close` - 收盘价

⚠️ **注意**: FXCM的CSV文件**没有Volume（成交量）字段**！

---

### 数据库表结构（ClickHouse）

#### ohlcv_m1表
```sql
CREATE TABLE forex_data.ohlcv_m1 (
    symbol      String,      -- 交易对符号（CSV中没有）
    timestamp   DateTime,    -- 对应CSV的DateTime
    open        Float64,     -- 对应CSV的Open
    high        Float64,     -- 对应CSV的High
    low         Float64,     -- 对应CSV的Low
    close       Float64,     -- 对应CSV的Close
    volume      UInt64,      -- CSV中没有！需要设默认值
    created_at  DateTime     -- 自动生成
)
```

---

## ❌ 问题分析

### 问题1: Volume字段缺失

**现状**:
- CSV文件: ❌ 没有 `Volume` 字段
- 数据库表: ✅ 有 `volume UInt64` 字段

**影响**:
- 直接导入CSV会因为字段数量不匹配而失败
- 外汇现货交易通常不记录成交量（与期货/股票不同）

**解决方案**:

#### 方案A: 修改表结构，volume设为可选（推荐）
```sql
-- 删除现有表
DROP TABLE IF EXISTS forex_data.ohlcv_m1;
DROP TABLE IF EXISTS forex_data.ohlcv_d1;

-- 重建表，volume设为Nullable或默认值0
CREATE TABLE forex_data.ohlcv_m1 (
    symbol      String,
    timestamp   DateTime,
    open        Float64,
    high        Float64,
    low         Float64,
    close       Float64,
    volume      UInt64 DEFAULT 0,  -- 默认值为0
    created_at  DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (symbol, timestamp);
```

#### 方案B: 导入时手动指定volume=0
```python
# 读取CSV时添加volume列
df = pd.read_csv('EURUSD_M1.csv')
df['symbol'] = 'EURUSD'
df['volume'] = 0  # 添加默认volume
df.rename(columns={'DateTime': 'timestamp', 'Open': 'open', 
                   'High': 'high', 'Low': 'low', 'Close': 'close'}, inplace=True)
```

---

## ✅ 字段映射方案

### 完整映射关系

| CSV字段 | 数据库字段 | 处理方式 | 备注 |
|---------|-----------|---------|------|
| (无) | `symbol` | 手动添加 | 从文件路径提取，如"EURUSD" |
| `DateTime` | `timestamp` | 直接映射 | 2015-01-04 22:00:00 |
| `Open` | `open` | 直接映射 | 1.19552 |
| `High` | `high` | 直接映射 | 1.19552 |
| `Low` | `low` | 直接映射 | 1.19355 |
| `Close` | `close` | 直接映射 | 1.19404 |
| (无) | `volume` | **默认值0** | ⚠️ CSV中没有 |
| (无) | `created_at` | 自动生成 | now() |

---

## 🔧 推荐修改方案

### 修改表结构（推荐）

**原因**:
1. FXCM外汇现货数据本身就没有成交量
2. Volume字段对外汇分析意义不大
3. 设置默认值0比每次导入时手动添加更简洁

**修改后的建表脚本**:

```sql
-- M1表（修改后）
CREATE TABLE forex_data.ohlcv_m1 (
    symbol      String COMMENT '交易对符号',
    timestamp   DateTime COMMENT 'K线时间',
    open        Float64 COMMENT '开盘价',
    high        Float64 COMMENT '最高价',
    low         Float64 COMMENT '最低价',
    close       Float64 COMMENT '收盘价',
    volume      UInt64 DEFAULT 0 COMMENT '成交量（外汇现货无此数据，默认0）',
    created_at  DateTime DEFAULT now() COMMENT '入库时间'
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (symbol, timestamp)
PRIMARY KEY (symbol, timestamp);

-- D1表（修改后）
CREATE TABLE forex_data.ohlcv_d1 (
    symbol      String COMMENT '交易对符号',
    date        Date COMMENT 'K线日期',
    open        Float64 COMMENT '开盘价',
    high        Float64 COMMENT '最高价',
    low         Float64 COMMENT '最低价',
    close       Float64 COMMENT '收盘价',
    volume      UInt64 DEFAULT 0 COMMENT '成交量（外汇现货无此数据，默认0）',
    created_at  DateTime DEFAULT now() COMMENT '入库时间'
)
ENGINE = MergeTree()
PARTITION BY toYear(date)
ORDER BY (symbol, date)
PRIMARY KEY (symbol, date);
```

---

## 📥 数据导入示例

### Python导入脚本

```python
import pandas as pd
import requests

# 读取CSV
df = pd.read_csv('fxcm_data/EURUSD/M1/2015/week_01.csv')

# 添加必要字段
df['symbol'] = 'EURUSD'  # 从文件路径提取
df['volume'] = 0         # 外汇无成交量，设为0

# 重命名列
df.rename(columns={
    'DateTime': 'timestamp',
    'Open': 'open',
    'High': 'high',
    'Low': 'low',
    'Close': 'close'
}, inplace=True)

# 调整列顺序
df = df[['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume']]

# 转换为CSV格式（不含表头）
csv_data = df.to_csv(index=False, header=False)

# 插入ClickHouse
url = "http://192.168.2.168:8123"
query = "INSERT INTO forex_data.ohlcv_m1 (symbol, timestamp, open, high, low, close, volume) FORMAT CSV"

response = requests.post(url, params={'query': query}, data=csv_data.encode('utf-8'))
```

---

## 🎯 结论与建议

### ✅ 需要做的修改

1. **重建数据库表**
   - 为 `volume` 字段添加 `DEFAULT 0`
   - 为 `created_at` 字段添加 `DEFAULT now()`

2. **更新建表脚本**
   - 修改 `scripts/create_clickhouse_tables.py`
   - 添加默认值说明

3. **创建数据导入脚本**
   - 自动从文件路径提取 `symbol`
   - 自动添加 `volume = 0`
   - 字段名转换（DateTime → timestamp等）

### 📋 下一步行动

1. ✅ 已完成：分析CSV和表结构差异
2. ⏭️ 待办：修改建表脚本，添加默认值
3. ⏭️ 待办：创建数据导入脚本
4. ⏭️ 待办：测试导入流程

---

**文档版本**: 1.0  
**创建日期**: 2025-10-04  
**状态**: 发现问题，需要修改表结构
