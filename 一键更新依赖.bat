@echo off
chcp 65001 >nul

cd %cd%\runtime\Scripts
title 一键更新依赖
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
echo 设置镜像源成功！开始更新依赖……
pip install -r "../../src/main/xiaozhi-server/requirements.txt"
echo 更新依赖成功！
pause

