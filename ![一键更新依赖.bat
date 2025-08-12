@echo off
chcp 65001 >nul

set "BATCH_DIR=%~dp0"
cd "%BATCH_DIR%runtime\conda_env\Scripts"

title 一键更新依赖

echo 开始更新主服务依赖...
pip install -r "../../../src/main/xiaozhi-server/requirements.txt" -i https://mirrors.aliyun.com/pypi/simple/
cls
echo 主服务依赖更新成功！

REM 检测音乐服务目录（修正路径格式）
if exist "%BATCH_DIR%src\main\music-xiaozhi-server\" (
    echo 发现音乐服务端目录，开始更新音乐服务依赖...
    pip install -r "../../../src/main/music-xiaozhi-server/requirements.txt" -i https://mirrors.aliyun.com/pypi/simple/
    cls
    echo 音乐服务依赖更新成功！
) else (
    echo 未检测到音乐服务端目录，跳过依赖安装
)

echo 全部依赖更新完毕！
pause