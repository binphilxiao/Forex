@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ============================================================
echo FXCM Historical Data Downloader v2.0
echo ============================================================
echo.

REM Check if virtual environment exists
if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found, using system Python
)

echo.
echo Starting FXCM data download...
echo.

REM Run the download script
python scripts\fxcm_data_downloader.py %*

echo.
echo ============================================================
echo Download process completed
echo ============================================================
echo.

pause
