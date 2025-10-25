@echo off
chcp 65001

:: 获取批处理文件所在目录的完整路径
set "SCRIPT_DIR=%~dp0"

:: 定义虚拟环境路径（基于脚本目录的完整路径）
set "VENV_PATH=%SCRIPT_DIR%runtime\conda_env"

:: 检查虚拟环境是否存在
if not exist "%VENV_PATH%" (
    echo 错误：虚拟环境不存在于 %VENV_PATH%
    pause
    exit /b 1
)

:: 使用完整路径打开新命令行窗口
cmd /k "cd /d "%VENV_PATH%" && call "%VENV_PATH%\Scripts\activate.bat" && echo 虚拟环境已成功激活！"