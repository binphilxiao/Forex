@echo off
chcp 65001 >nul
echo ========================================
echo 重建ClickHouse数据库表
echo ========================================
echo.
echo 警告：此操作将删除所有现有表和数据！
echo.

cd ..
python scripts\rebuild_clickhouse_tables.py

echo.
pause
