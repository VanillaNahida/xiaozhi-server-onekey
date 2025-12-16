#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import urllib.request
import urllib.error
import ssl
from pathlib import Path

# 获取当前脚本所在目录的父目录作为基础路径
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
runtime_dir = os.path.join(base_dir, 'runtime')

# 定义运行命令函数
def run_command(command):
    """运行命令并返回结果"""
    try:
        print(f"执行命令: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("命令执行成功")
            if result.stdout:
                print(f"输出: \n{result.stdout}")
        else:
            print(f"命令执行失败: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"执行命令时出错: {e}")
        return False

# 定义卸载opuslib_next包函数
def uninstall_opuslib():
    """卸载opuslib_next包"""
    print("正在卸载 opuslib_next...")
    return run_command(f"{sys.executable} -m pip uninstall opuslib_next -y")

# 定义下载opus.dll函数
def download_opus_dll():
    """从指定链接下载opus.dll"""
    url = "https://drive.xcnahida.cn/f/d/jRSj/opus.dll"
    # 动态计算目标目录
    target_dir = Path(os.path.join(runtime_dir, 'conda_env'))
    
    # 确保目标目录存在
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / "opus.dll"
    
    # 下载文件
    
    try:
        print(f"正在从 {url} 下载 opus.dll...")
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        request.add_header('Referer', 'xcnahida.cn')
        with urllib.request.urlopen(request) as response:
            with open(target_file, 'wb') as f:
                f.write(response.read())
        print("opus.dll 下载成功")
        return True
    except Exception as e:
        print(f"下载失败！错误信息: {e}")
    return False

# 定义安装依赖函数
def install_requirements():
    """安装requirements.txt中的依赖"""
    # 动态计算requirements.txt路径
    requirements_path = os.path.join(base_dir, 'src', 'main', 'xiaozhi-server', 'requirements.txt')
    print(f"正在安装 {requirements_path} 中的依赖...")
    return run_command(f"{sys.executable} -m pip install -vv -r \"{requirements_path}\"")

# 定义主函数
def main():
    print("开始执行OPUS库的安装流程...")
    
    # 步骤1: 卸载opuslib_next
    if not uninstall_opuslib():
        print("警告: 卸载 opuslib_next 失败，但将继续执行后续步骤...")
    
    # 步骤2: 下载opus.dll
    if not download_opus_dll():
        print("错误: 下载 opus.dll 失败")
        return False
    
    # 步骤3: 安装依赖
    if not install_requirements():
        print("错误: 安装依赖失败")
        return False
    
    print("所有步骤已完成!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)