@echo off
chcp 65001 >nul
echo ========================================
echo FXCM数据导入ClickHouse
echo ========================================
echo.

cd ..
python scripts\import_fxcm_to_clickhouse.py

echo.
pause
