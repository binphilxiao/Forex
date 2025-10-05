@echo off
REM ============================================================================
REM M1 to Multi-Timeframe Converter Launcher
REM Version: 2.0.0
REM Author: binphilxiao
REM ============================================================================

cd /d "%~dp0"

echo ============================================================
echo M1 to Multi-Timeframe Converter v2.0
echo ============================================================
echo.

REM Run with default settings (all pairs, all timeframes, 2015-now)
python scripts\m1_timeframe_converter.py %*

echo.
echo ============================================================
echo Conversion completed!
echo Check logs folder for detailed reports
echo ============================================================
pause
