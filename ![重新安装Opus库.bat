@echo off
chcp 65001
cls
set "BATCH_DIR=%~dp0"
set "PYTHON_PATH=%BATCH_DIR%runtime\conda_env\python.exe"
title 重装Opus lib向导
"%PYTHON_PATH%" "%BATCH_DIR%scripts\get_opus.py"
echo 将在10秒后自动关闭窗口...
timeout /t 10
