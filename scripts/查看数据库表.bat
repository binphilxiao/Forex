@echo off
chcp 65001 >nul
echo ========================================
echo 查看ClickHouse数据库表信息
echo ========================================
echo.

cd ..
python scripts\view_clickhouse_tables.py

echo.
pause
