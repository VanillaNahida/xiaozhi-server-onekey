# coding=UTF-8
# 本更新脚本以GPL v3.0开源
import os
import sys
import time
import wave
import shutil
import pyaudio
import requests
import threading
import subprocess
from datetime import datetime
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# 没用的功能
def get_windows_version():
    # 获取Windows版本信息
    version_info = sys.getwindowsversion()
    build_number = version_info.build  # 系统构建版本号

    if build_number >= 22000:
        return "Windows 11"
    elif build_number >= 10240:  # Windows 10 首个正式版本号
        return "Windows 10"
    else:
        return f"旧版 Windows (Build {build_number})"
    
def is_windows_11():
    try:
        result = get_windows_version()
        if result == "Windows 10":
            return False
        elif result == "Windows 11":
            return True
        else:
            return False
    except OSError as e:
        print(e)

def print_gradient_text(text, start_color, end_color):
    """
    在终端打印彩色渐变文字
    
    参数:
    text: 要打印的文字
    start_color: 起始颜色 (R, G, B) 元组, 范围0-255
    end_color: 结束颜色 (R, G, B) 元组, 范围0-255
    """
    r1, g1, b1 = start_color
    r2, g2, b2 = end_color
    
    gradient_text = []
    for i, char in enumerate(text):
        # 计算当前字符的颜色插值
        ratio = i / (len(text) - 1) if len(text) > 1 else 0
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        
        # 使用ANSI转义序列设置颜色
        gradient_text.append(f"\033[38;2;{r};{g};{b}m{char}")
    
    # 组合所有字符并重置颜色
    print(''.join(gradient_text) + '\033[0m')

def print_logo():
    """打印logo"""
    # 打印logo
    text = r"""    
    小智AI服务端一键包更新脚本 Ver 1.5.0
    脚本作者：哔哩哔哩 @香草味的纳西妲喵
    GitHub: @VanillaNahida
 __      __            _  _  _            _   _         _      _      _        
 \ \    / /           (_)| || |          | \ | |       | |    (_)    | |       
  \ \  / /__ _  _ __   _ | || |  __ _    |  \| |  __ _ | |__   _   __| |  __ _ 
   \ \/ // _` || '_ \ | || || | / _` |   | . ` | / _` || '_ \ | | / _` | / _` |
    \  /| (_| || | | || || || || (_| |   | |\  || (_| || | | || || (_| || (_| |
     \/  \__,_||_| |_||_||_||_| \__,_|   |_| \_| \__,_||_| |_||_| \__,_| \__,_|   

    感谢使用本脚本！
"""
    if is_windows_11():
        print_gradient_text(text, (240, 230, 50), (90, 180, 0))
    else:
        print(text)
    # 初始化输出
    text = """
脚本开源地址：https://github.com/VanillaNahida/xiaozhi-server-onekey/
"""
    if is_windows_11():
        print_gradient_text(text, (150, 240, 200), (20, 160, 40))
    else:
        print(text)

def play_audio_async(file_path):
    """使用线程实现非阻塞播放"""
    def _play():
        # 打开wav文件
        wf = wave.open(file_path, 'rb')
        
        # 初始化pyaudio
        p = pyaudio.PyAudio()
        
        # 打开音频流
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        
        # 读取数据并播放
        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)
        
        # 停止和关闭流
        stream.stop_stream()
        stream.close()
        
        # 关闭pyaudio
        p.terminate()
    
    # 创建守护线程（daemon=True 确保主线程退出时自动终止）
    thread = threading.Thread(target=_play, daemon=True)
    thread.start()
    return thread

# 常量
DEFAULT_REPO_URL = "https://github.com/VanillaNahida/xiaozhi-server-onekey.git"

def get_github_proxy_urls():
    """返回GitHub镜像代理地址列表"""
    return [
        "https://ghfast.top",
        "https://github.acmsz.top",
        "https://gh.b52m.cn",
        "https://gh.nxnow.top",
        "https://gh.ddlc.top",
        "https://slink.ltd",
        "https://cors.isteed.cc",
        "https://hub.gitmirror.com",
        "https://sciproxy.com",
        "https://ghproxy.net",
        "https://gitclone.com",
        "https://hub.incept.pw",
        "https://github.moeyy.xyz",
        "https://dl.ghpig.top",
        "https://gh-proxy.com",
        "https://hub.whtrys.space",
        "https://gh-proxy.ygxz.in",
        "https://ghproxy.net"
    ]

def run_git_command(git_path, args):
    """执行 Git 命令并实时显示输出"""
    process = subprocess.Popen(
        [git_path] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    output_lines = []
    print(f"\n执行命令: git {' '.join(args)}")
    print("-" * 60)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            cleaned = output.strip()
            print(cleaned)
            output_lines.append(cleaned)
    print("-" * 60)
    return process.poll(), '\n'.join(output_lines)
    
def pull_with_proxy(git_path):
    """使用代理更新代码（传参Git所在位置）"""
    # 获取脚本所在目录的上级目录
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 获取代理地址列表
    proxy_list = get_github_proxy_urls()
    for proxy in proxy_list:
        # 拼接代理地址
        new_url = f"{proxy.rstrip('/')}/{DEFAULT_REPO_URL}"
        print(f"\n开始更新一键包，使用代理地址：{new_url}")
        run_git_command(git_path, ["remote", "set-url", "origin", new_url])
        # 更新代码
        code, output = run_git_command(git_path, ["pull"])
        if code == 0:
            # 成功提示音
            if os.path.exists(f'{script_dir}/scripts/assets/success.wav'): play_audio_async(f'{script_dir}/scripts/assets/success.wav')
            print("\n✅ 一键包更新成功！" if "Already up" not in output else "\n🎉 恭喜，你本地的代码已经是最新版本！")
            break
        else:
            print("\n❌ 更新失败，正在切换代理地址重试！")
            if os.path.exists(f'{script_dir}/scripts/assets/failed.wav'): play_audio_async(f'{script_dir}/scripts/assets/failed.wav')

def get_pull_mode():
    """选择更新模式"""
    print("\n请选择更新方式：")
    print("1. 普通更新（推荐，保留本地修改）")
    print("2. 强制更新（覆盖所有修改）")
    while True:
        choice = input("请输入选项（1/2）（留空默认为1）: ").strip() or '1'
        if choice in ('1', '2'):
            return 'normal' if choice == '1' else 'force'
        print("输入无效，请重新输入！")

def main():
    os.system("cls")
    print_logo()
    # # 初始化路径
    # script_dir = os.path.dirname(os.path.abspath(__file__))

    # 初始化路径，获取脚本所在目录的上级目录
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 切换目录
    os.chdir(script_dir)
    git_path = os.path.join(script_dir, "runtime", "git-2.48.1", "cmd", "git.exe")
    base_dir = script_dir
    print(f"当前脚本目录：{base_dir}")

    # 环境检查
    if not os.path.exists(git_path):
        print(f"[ERROR] 未找到Git程序：{git_path}")
        input("按 Enter 退出...")
        return

    try:
        os.chdir(base_dir)
    except Exception as e:
        print(f"[ERROR] 目录切换失败：{str(e)}")
        input("按 Enter 退出...")
        return

    # 代理设置流程
    use_proxy = input("\n是否设置GitHub代理？（留空或输入非y为不设置，若需要进行强制更新操作，请输入N并按下回车）(y/n): ").lower() == 'y'

    try:
        # 询问是否使用代理
        if use_proxy:
            # 使用代理更新代码
            pull_with_proxy(git_path)
        else:
            reset = input("是否重置为默认地址？(若需要进行强制更新操作，请输入N并按下回车) (y/n): ").lower() == 'y'
            if reset:
                print(f"\n重置为默认地址：{DEFAULT_REPO_URL}")
                run_git_command(git_path, ["remote", "set-url", "origin", DEFAULT_REPO_URL])
            else:
                print("输入非y, 已取消重置操作")

            # 更新操作
            pull_mode = get_pull_mode()
            
            if pull_mode == 'normal':
                code, output = run_git_command(git_path, ["pull"])
                if code == 0:
                    # 成功提示音
                    if os.path.exists(f'{script_dir}/scripts/assets/success.wav'): play_audio_async(f'{script_dir}/scripts/assets/success.wav')
                    print("\n✅ 一键包更新成功！" if "Already up" not in output else "\n🎉 恭喜，你的一键包已经是最新版本！")

                else:
                    print("\n❌ 更新失败，请检查日志")
                    if os.path.exists(f'{script_dir}/scripts/assets/failed.wav'): play_audio_async(f'{script_dir}/scripts/assets/failed.wav')
            else:
                print("\n警告⚠️： 强制更新将覆盖所有本地修改！")
                if input("你确认要强制更新吗？请输入“确认强制更新”确认操作：") == "确认强制更新":
                    print("\n正在强制同步...")
                    run_git_command(git_path, ["fetch", "origin"])
                    run_git_command(git_path, ["fetch", "--all"])
                    run_git_command(git_path, ["reset", "--hard", "origin/main"])
                    if os.path.exists(f'{script_dir}/scripts/assets/success.wav'): play_audio_async(f'{script_dir}/scripts/assets/success.wav')
                    print("\n🎉 强制更新成功！")
                else:
                    print("\n⛔ 输入无效，已取消强制更新操作")

    finally:
        # 显示最终远程地址
        print("\n重置为默认远程地址")
        run_git_command(git_path, ["remote", "set-url", "origin", DEFAULT_REPO_URL])
        print("\n当前远程地址：")
        run_git_command(git_path, ["remote", "-v"])

    print("\n操作完成！")
    
    # 执行一键更新依赖.bat
    print("\n开始更新依赖...")
    batch_file = os.path.join(base_dir, "![一键更新依赖.bat")
    if os.path.exists(batch_file):
        print(f"执行依赖更新脚本: {batch_file}")
        try:
            subprocess.run(batch_file, shell=True)
        except Exception as e:
            print(f"执行依赖更新脚本失败: {str(e)}")
    else:
        print(f"未找到依赖更新脚本: {batch_file}")
    
    time.sleep(2)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(f'{script_dir}/assets/sound.wav'): play_audio_async(f'{script_dir}/assets/sound.wav')
    main()
