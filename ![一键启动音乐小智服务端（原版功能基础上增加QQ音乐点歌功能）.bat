@echo off
chcp 65001 >nul

title 小智AI音乐服务端
set "BATCH_DIR=%~dp0"

REM 检测音乐小智目录是否存在
if not exist "%BATCH_DIR%src\main\music-xiaozhi-server\" (
    echo ⚠️ 未找到音乐小智服务端目录
    echo 正在尝试自动初始化...
    "%BATCH_DIR%runtime\conda_env\python.exe" "%BATCH_DIR%\scripts\init_music_xiaozhi_server.py"
    echo.
    echo 初始化完成，请重新运行本脚本
    pause
    exit /b 1
)

set "PYTHON_PATH=%BATCH_DIR%runtime\conda_env\python.exe"
set "PATH=%BATCH_DIR%runtime\ffmpeg;%PATH%"
set "PATH=%BATCH_DIR%runtime\mysql\bin;%PATH%"
set "PATH=%BATCH_DIR%runtime\Redis;%PATH%"
set "PATH=%BATCH_DIR%runtime\nodejs;%PATH%"
set "PATH=%BATCH_DIR%runtime\jdk-21\bin;%PATH%"

"%PYTHON_PATH%" "%BATCH_DIR%\scripts\sync_config.py" 
timeout /t 5
cls
"%PYTHON_PATH%" "%BATCH_DIR%\scripts\check_update.py" --use_music_server true
timeout /t 5