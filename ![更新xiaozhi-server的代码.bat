@echo off
chcp 65001 >nul

set "PYTHON_PATH=%BATCH_DIR%runtime\python.exe"
title 小智AI服务端更新脚本
"%PYTHON_PATH%" "runtime\Scripts\updater.py"