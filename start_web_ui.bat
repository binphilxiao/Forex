@echo off
chcp 65001 >nul
echo.
echo ================================================
echo    FXCM 数据处理系统 - Web界面
echo    版本: 3.0.0 (Flask)
echo ================================================
echo.
echo 正在启动Web服务器...
echo.

python scripts\start_web.py

if errorlevel 1 (
    echo.
    echo ❌ 启动失败！
    echo.
    echo 可能原因:
    echo 1. Python未正确安装
    echo 2. 缺少Flask库
    echo.
    echo 请尝试: pip install flask pandas requests
    echo.
    pause
)
