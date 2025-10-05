@echo off
chcp 65001 > nul
REM ====================================================================
REM FXCM Data Consistency Verification Tool
REM ====================================================================
REM This batch file runs the data consistency verification script
REM 
REM Usage:
REM   verify_consistency.bat              - Check all data (fast mode)
REM   verify_consistency.bat comprehensive - Use comprehensive mode
REM
REM Author: FXCM Data Team
REM Version: 1.0.0
REM ====================================================================

cd /d "%~dp0"

echo.
echo ====================================================================
echo   FXCM Data Consistency Verification Tool
echo ====================================================================
echo.

REM Check if comprehensive mode is requested
if "%1"=="comprehensive" (
    echo Mode: COMPREHENSIVE (checking all records - this may take a while)
    echo.
    python scripts\verify_data_consistency.py --mode comprehensive
) else if "%1"=="help" (
    python scripts\verify_data_consistency.py --help
) else (
    echo Mode: FAST (checking file boundaries only)
    echo.
    python scripts\verify_data_consistency.py %*
)

echo.
echo ====================================================================
echo   Verification Complete
echo ====================================================================
echo.
pause
