@echo off
chcp 65001 >nul

set "PYTHON_PATH=%BATCH_DIR%runtime\conda_env\python.exe"
title 小智AI服务端更新脚本
"%PYTHON_PATH%" ".\scripts\updater.py"

echo 开始更新主服务依赖...
pip install -r "./src/main/xiaozhi-server/requirements.txt" -i https://mirrors.aliyun.com/pypi/simple/
@REM cls
echo 主服务依赖更新成功！

REM 检测音乐服务目录（修正路径格式）
if exist "%BATCH_DIR%src\main\music-xiaozhi-server\" (
    echo 发现音乐服务端目录，开始更新音乐服务依赖...
    pip install -r "./src/main/music-xiaozhi-server/requirements.txt" -i https://mirrors.aliyun.com/pypi/simple/
    @REM cls
    echo 音乐服务依赖更新成功！
) else (
    echo 未检测到音乐服务端目录，跳过依赖安装
)

echo 全部依赖更新完毕！请按回车键退出...
pause