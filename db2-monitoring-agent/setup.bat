@echo off
REM Setup script for DB2 Monitoring Agent (Windows)

echo ========================================
echo DB2 & Kubernetes Monitoring Agent Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ first
    exit /b 1
)

echo Step 1: Creating virtual environment...
uv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    exit /b 1
)

echo.
echo Step 2: Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Step 3: Installing dependencies...
uv pip install -r requirements.txt --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple --allow-insecure-host pypi.ci.artifacts.walmart.com
if errorlevel 1 (
    echo Error: Failed to install dependencies
    exit /b 1
)

echo.
echo Step 4: Creating config file from example...
if not exist config.yaml (
    copy config.example.yaml config.yaml
    echo Created config.yaml - PLEASE EDIT THIS FILE with your settings!
) else (
    echo config.yaml already exists, skipping...
)

echo.
echo ========================================
echo Setup Complete! 
echo ========================================
echo.
echo Next steps:
echo 1. Edit config.yaml with your DB2 and Kubernetes settings
echo 2. Run the monitoring agent:
echo    .venv\Scripts\activate
echo    python main.py
echo.
echo For help:
echo    python main.py --help
echo.
