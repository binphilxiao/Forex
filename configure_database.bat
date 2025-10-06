@echo off
REM ============================================================================
REM ClickHouse Database Configuration Tool
REM ============================================================================
REM 
REM Description:
REM   Interactive wizard for configuring ClickHouse database connection
REM   Replaces view_clickhouse_tables.py with user-friendly interface
REM
REM Features:
REM   - Interactive prompts with defaults
REM   - Input validation
REM   - Connection testing
REM   - Secure password entry
REM   - Detailed logging
REM
REM Usage:
REM   configure_database.bat              - Run configuration wizard
REM   configure_database.bat test         - Test existing configuration
REM   configure_database.bat notest       - Configure without testing
REM
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo    ClickHouse Database Configurator v1.0
echo ============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Determine mode based on argument
set MODE=normal
if /i "%1"=="test" set MODE=test-only
if /i "%1"=="notest" set MODE=no-test

REM Run configurator based on mode
if "%MODE%"=="test-only" (
    echo Running in TEST-ONLY mode...
    echo.
    python scripts\clickhouse_configurator.py --test-only
) else if "%MODE%"=="no-test" (
    echo Running in NO-TEST mode...
    echo.
    python scripts\clickhouse_configurator.py --no-test
) else (
    echo Running interactive configuration wizard...
    echo.
    python scripts\clickhouse_configurator.py
)

REM Check exit code
if %errorlevel% equ 0 (
    echo.
    echo ============================================================================
    echo    Configuration completed successfully!
    echo ============================================================================
    echo.
    echo Configuration file: clickhouse_config.json
    echo Log files location: logs\
    echo.
    echo Next steps:
    echo   1. Review configuration: type clickhouse_config.json
    echo   2. Test connection: configure_database.bat test
    echo   3. Start using Forex tools: batch_import.bat
    echo.
) else (
    echo.
    echo ============================================================================
    echo    Configuration failed or was cancelled
    echo ============================================================================
    echo.
    echo Please check the error messages above and try again.
    echo For help, see: README_CLICKHOUSE_CONFIGURATOR.md
    echo.
)

pause
