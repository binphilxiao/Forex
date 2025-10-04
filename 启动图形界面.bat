@echo off
chcp 65001 >nul
echo.
echo ================================================
echo    FXCM 数据处理系统 - 图形界面
echo    版本: 2.0.0 (Tkinter)
echo ================================================
echo.
echo 正在启动图形界面...
echo.

python fxcm_gui.py

if errorlevel 1 (
    echo.
    echo ❌ 启动失败！
    echo.
    echo 可能原因:
    echo 1. Python未正确安装
    echo 2. 缺少必要的库
    echo.
    echo 请尝试: pip install pandas requests
    echo.
    pause
)
