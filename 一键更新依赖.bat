@echo off
chcp 65001 >nul

cd %cd%\runtime\Scripts
title 一键更新依赖
echo 开始更新依赖……
pip install -r "../../src/main/xiaozhi-server/requirements.txt" -i https://mirrors.aliyun.com/pypi/simple/
echo 更新依赖成功！
pip install -r "../../src/main/music-xiaozhi-server/requirements.txt" -i https://mirrors.aliyun.com/pypi/simple/
echo 更新小智音乐服务依赖成功！
pause

