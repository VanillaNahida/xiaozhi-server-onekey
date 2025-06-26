@echo off
chcp 65001 >nul

set "BATCH_DIR=%~dp0"
set "PYTHON_PATH=%BATCH_DIR%runtime\python.exe"
set "PATH=%BATCH_DIR%runtime\ffmpeg;%PATH%"
set "PATH=%BATCH_DIR%runtime\mysql\bin;%PATH%"
set "PATH=%BATCH_DIR%runtime\Redis;%PATH%"
set "PATH=%BATCH_DIR%runtime\nodejs;%PATH%"
set "PATH=%BATCH_DIR%runtime\jdk-21\bin;%PATH%"
cd /d "%BATCH_DIR%src\main\xiaozhi-server"
title 小智AI服务端
"%PYTHON_PATH%" app.py
pause