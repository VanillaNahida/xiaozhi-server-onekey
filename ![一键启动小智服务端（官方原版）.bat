@echo off
chcp 65001 >nul

title 小智AI服务端
set "BATCH_DIR=%~dp0"
set "PYTHON_PATH=%BATCH_DIR%runtime\conda_env\python.exe"
set "PATH=%BATCH_DIR%runtime\ffmpeg;%PATH%"
set "PATH=%BATCH_DIR%runtime\mysql\bin;%PATH%"
set "PATH=%BATCH_DIR%runtime\Redis;%PATH%"
set "PATH=%BATCH_DIR%runtime\maven\bin;%PATH%"
set "PATH=%BATCH_DIR%runtime\jdk\bin;%PATH%"

"%PYTHON_PATH%" "%BATCH_DIR%\scripts\check_update.py"
timeout /t 3
cls
cd /d "%BATCH_DIR%src\main\xiaozhi-server"
"%PYTHON_PATH%" app.py
pause