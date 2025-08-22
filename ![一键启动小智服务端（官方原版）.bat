@echo off
chcp 65001 >nul

set "BATCH_DIR=%~dp0"
set "PYTHON_PATH=%BATCH_DIR%runtime\conda_env\python.exe"
title 小智AI服务端
"%PYTHON_PATH%" "%BATCH_DIR%\check_update.py"
set "PATH=%BATCH_DIR%runtime\ffmpeg;%PATH%"
set "PATH=%BATCH_DIR%runtime\mysql\bin;%PATH%"
set "PATH=%BATCH_DIR%runtime\Redis;%PATH%"
set "PATH=%BATCH_DIR%runtime\maven\bin;%PATH%"
set "PATH=%BATCH_DIR%runtime\jdk\bin;%PATH%"
cd /d "%BATCH_DIR%src\main\xiaozhi-server"
"%PYTHON_PATH%" app.py
pause