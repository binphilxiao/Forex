@echo off
chcp 65001 >nul
echo.
echo ================================================
echo    批量导入所有数据
echo    版本: 4.0 (快速模式)
echo ================================================
echo.

python scripts\batch_import_all.py

if errorlevel 1 (
    echo.
    echo ❌ 导入失败！
    pause
) else (
    echo.
    echo ✅ 导入完成！
    pause
)
