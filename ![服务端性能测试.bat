@echo off
chcp 65001 >nul

set "BATCH_DIR=%~dp0"
set "PYTHON_PATH=%BATCH_DIR%runtime\conda_env\python.exe"
if not exist "%PYTHON_PATH%" (
    echo Error: Python not found at "%PYTHON_PATH%"
    pause
    exit /b 1
)
set "PATH=%BATCH_DIR%runtime\ffmpeg;%PATH%"
cd /d "%BATCH_DIR%src\main\xiaozhi-server"
"%PYTHON_PATH%" performance_test_tool.py
pause