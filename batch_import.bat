@echo off
chcp 65001 >nul
echo.
echo ================================================
echo    FXCM数据批量导入 v2.0
echo    使用新版导入器 - 双验证模式
echo ================================================
echo.

python scripts\fxcm_importer.py

if errorlevel 1 (
    echo.
    echo ❌ 导入失败！
    pause
) else (
    echo.
    echo ✅ 导入完成！
    pause
)
