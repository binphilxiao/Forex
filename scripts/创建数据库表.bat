@echo off
chcp 65001 >nul
echo ========================================
echo ClickHouse 数据库表结构创建
echo ========================================
echo.

cd ..
python scripts\create_clickhouse_tables.py

echo.
pause
