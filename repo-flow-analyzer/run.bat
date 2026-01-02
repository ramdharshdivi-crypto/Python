@echo off
REM Enterprise Spring Boot Repository Analyzer
REM Windows batch script to run the analyzer

setlocal enabledelayedexpansion

echo.
echo ===================================================
echo  Enterprise Spring Boot Repository Analyzer
echo ===================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    echo Visit: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Get the repository path
if "%~1"=="" (
    echo Usage: run.bat <repository_path> [output_dir]
    echo.
    echo Examples:
    echo   run.bat C:\path\to\spring-boot-project
    echo   run.bat C:\path\to\repo my-analysis
    echo.
    set /p repo_path="Enter repository path: "
) else (
    set repo_path=%~1
)

if not exist "!repo_path!" (
    echo Error: Repository path does not exist: !repo_path!
    pause
    exit /b 1
)

REM Get output directory
if "%~2"=="" (
    set output_dir=repo-analysis-output
) else (
    set output_dir=%~2
)

echo.
echo Repository: !repo_path!
echo Output Dir: !output_dir!
echo.
echo Starting analysis...
echo.

REM Run the analyzer
python main.py --repo "!repo_path!" --out "!output_dir!"

if errorlevel 1 (
    echo.
    echo Error: Analysis failed
    pause
    exit /b 1
)

echo.
echo Analysis complete! Results saved to:
echo !repo_path!\!output_dir!
echo.
pause
exit /b 0
