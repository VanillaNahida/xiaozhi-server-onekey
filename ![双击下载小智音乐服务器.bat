@echo off
chcp 65001 >nul

set "BATCH_DIR=%~dp0"
set "PYTHON_PATH=%BATCH_DIR%runtime\conda_env\python.exe"
title 初始化小智音乐服务器
"%PYTHON_PATH%" init_music_xiaozhi_server.py
pause