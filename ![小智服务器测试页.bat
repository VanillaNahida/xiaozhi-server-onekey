@echo off
chcp 65001 >nul

title 小智AI服务端测试页Server Test Page
set "BATCH_DIR=%~dp0"
set "PYTHON_PATH=%BATCH_DIR%runtime\conda_env\python.exe"
"%PYTHON_PATH%" ".\scripts\start_test_server.py"