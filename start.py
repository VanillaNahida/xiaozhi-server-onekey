# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from tqdm import tqdm

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def print_banner():
    print("""
    ░██████╗░██╗░░░██╗███████╗██╗░░██╗░█████╗░
    ██╔════╝░╚██╗░██╔╝╚════██║██║░██╔╝██╔══██╗
    ╚█████╗░░░╚████╔╝░░░███╔═╝█████═╝░███████║
    ░╚═══██╗░░░╚██╔╝░░░██╔══╝░██╔═██╗░██╔══██║
    ██████╔╝░░░░██║░░░███████╗██║░╚██╗██║░░██║
    ╚═════╝░░░░░╚═╝░░░╚══════╝╚═╝░░╚═╝╚═╝░░╚═╝
    """)

def run_command(command, description, new_window=False):
    print(f"\n▶ {description}")
    try:
        if new_window:
            # 统一转换为命令列表
            if isinstance(command, str):
                cmd_list = [command]
            else:
                cmd_list = command
            
            # 处理带空格的路径
            processed_cmd = ' '.join([f'"{arg}"' if ' ' in arg else arg for arg in cmd_list])
            full_cmd = f'start cmd /k "{processed_cmd} & echo. & echo 命令执行完毕，按任意键退出... & pause>nul"'
            
            subprocess.run(
                full_cmd,
                shell=True,
                cwd=SCRIPT_DIR,
                check=True
            )
            return True
        else:
            # 原有逻辑保持不变
            result = subprocess.run(
                command,
                shell=True,
                cwd=SCRIPT_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8'
            )
            print(result.stdout)
            return result.returncode == 0
    except Exception as e:
        print(f"执行失败: {str(e)}")
        return False

def main_menu():
    while True:
        print_banner()
        print("\n主菜单：")
        print("1. 更新服务端代码")
        print("2. 更新依赖库")
        print("3. 安装音乐小智服务端DLC")
        print("4. 启动主服务端")
        print("5. 启动音乐服务端")
        print("6. 退出")
        
        choice = input("请输入选项 (1-5): ").strip()
        
        if choice == '1':
            run_command(
                [
                    os.path.join(SCRIPT_DIR, 'runtime', 'python.exe'),
                    os.path.join(SCRIPT_DIR, 'runtime', 'Scripts', 'updater.py')
                ],
                "正在更新代码...",
                new_window=True  # 添加此参数
            )
            os.system("cls")
        elif choice == '2':
            run_command(
                os.path.join(SCRIPT_DIR, '一键更新依赖.bat'),
                "正在更新依赖...",
                new_window=True
            )
            os.system("cls")
        elif choice == '4':
            run_command(
                os.path.join(SCRIPT_DIR, '一键启动小智服务端.bat'),
                "正在启动主服务端...",
                new_window=True
            )
            os.system("cls")
        elif choice == '5':
            run_command(
                os.path.join(SCRIPT_DIR, '一键启动音乐小智服务端.bat'),
                "正在启动音乐服务端...",
                new_window=True
            )
            os.system("cls")
        elif choice == '6':
            print("感谢使用！")
            sys.exit(0)
        else:
            print("无效输入，请重新选择")

if __name__ == "__main__":
    print("欢迎使用小智AI服务端控制台")
    print(f"当前工作目录: {SCRIPT_DIR}")
    main_menu()