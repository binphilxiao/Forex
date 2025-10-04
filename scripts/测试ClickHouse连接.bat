@echo off
chcp 65001 >nul
echo ========================================
echo ClickHouse 数据库连接测试
echo ========================================
echo.

python test\test_clickhouse_connection.py

echo.
pause
