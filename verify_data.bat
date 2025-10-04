@echo off
chcp 65001 >nul
echo.
echo ================================================
echo    验证所有数据
echo    版本: 4.0
echo ================================================
echo.

python scripts\verify_all_data.py

if errorlevel 1 (
    echo.
    echo ❌ 验证失败！
    pause
) else (
    echo.
    echo ✅ 验证完成！
    pause
)
