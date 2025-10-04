@echo off
chcp 65001 >nul
echo.
echo ================================================
echo    严格校验导入数据
echo    版本: 4.0 (详细模式)
echo ================================================
echo.

python scripts\comprehensive_check.py

if errorlevel 1 (
    echo.
    echo ❌ 校验失败！
    pause
) else (
    echo.
    echo ✅ 校验完成！
    pause
)
