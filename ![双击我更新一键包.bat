@echo off
chcp 65001 >nul

set "PYTHON_PATH=%BATCH_DIR%runtime\conda_env\python.exe"
title 小智AI服务端一键包更新脚本
"%PYTHON_PATH%" ".\update_onekey_pack.py"
echo 一键包更新完毕！
"%PYTHON_PATH%" ".\runtime\success.py"
echo 请按回车键退出...

pause