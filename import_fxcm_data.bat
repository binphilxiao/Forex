@echo off
REM FXCM Data Importer - Windows Batch Launcher
REM Version: 2.0.0
REM Author: binphilxiao

echo.
echo ============================================================
echo FXCM Data Importer v2.0
echo ============================================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Run importer with default settings
python scripts\fxcm_importer.py %*

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo Import completed successfully!
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo Import failed with error code: %ERRORLEVEL%
    echo ============================================================
)

echo.
pause
