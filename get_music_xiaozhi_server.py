import os
import sys
import time
import shutil
import zipfile
import requests
from io import BytesIO
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException

DEFAULT_ZIP_URL = "https://github.com/XuSenfeng/xiaozhi-esp32-server-music/archive/refs/heads/master.zip"

# 硬编码的代理地址
PROXY_URL = [
    "https://ghfast.top/https://github.com/XuSenfeng/xiaozhi-esp32-server-music/archive/refs/heads/master.zip",
    "https://gh.ddlc.top/https://github.com/XuSenfeng/xiaozhi-esp32-server-music/archive/refs/heads/master.zip",
    "https://slink.ltd/https://github.com/XuSenfeng/xiaozhi-esp32-server-music/archive/refs/heads/master.zip",
    "https://cors.isteed.cc/https://github.com/XuSenfeng/xiaozhi-esp32-server-music/archive/refs/heads/master.zip",
    "https://hub.gitmirror.com/https://github.com/XuSenfeng/xiaozhi-esp32-server-music/archive/refs/heads/master.zip",
    "https://sciproxy.com/https://github.com/XuSenfeng/xiaozhi-esp32-server-music/archive/refs/heads/master.zip",
    "https://ghproxy.net/https://github.com/XuSenfeng/xiaozhi-esp32-server-music/archive/refs/heads/master.zip",
    "https://gitclone.com/https://github.com/XuSenfeng/xiaozhi-esp32-server-music/archive/refs/heads/master.zip",
    "https://hub.incept.pw/https://github.com/XuSenfeng/xiaozhi-esp32-server-music/archive/refs/heads/master.zip",
    "https://github.moeyy.xyz/https://github.com/XuSenfeng/xiaozhi-esp32-server-music/archive/refs/heads/master.zip",
    "https://dl.ghpig.top/https://github.com/XuSenfeng/xiaozhi-esp32-server-music/archive/refs/heads/master.zip",
    "https://gh-proxy.com/https://github.com/XuSenfeng/xiaozhi-esp32-server-music/archive/refs/heads/master.zip",
    "https://hub.whtrys.space/https://github.com/XuSenfeng/xiaozhi-esp32-server-music/archive/refs/heads/master.zip",
    "https://gh-proxy.ygxz.in/https://github.com/XuSenfeng/xiaozhi-esp32-server-music/archive/refs/heads/master.zip",
    "https://ghproxy.net/https://github.com/XuSenfeng/xiaozhi-esp32-server-music/archive/refs/heads/master.zip"
]

def download_file_with_fallbacks(filename="master.zip", retries=5):
    """
    通过镜像源列表下载文件，支持失败自动切换和重试
    
    参数:
        filename: 保存的文件名
        retries: 每个地址的最大重试次数
        
    返回: 
        成功返回文件路径，失败返回None
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': '*/*'
    }
    
    # 确保目标目录存在
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename) or os.getcwd(), exist_ok=True)
    
    for idx, url in enumerate(PROXY_URL):
        print(f"尝试镜像源 #{idx+1}/{len(PROXY_URL)}: {url.split('//')[1].split('/')[0]}")
        
        # 每个地址尝试多次
        for attempt in range(1, retries + 1):
            try:
                start_time = time.time()
                response = requests.get(
                    url,
                    headers=headers,
                    stream=True,  # 流式下载大文件
                    timeout=(5, 15)  # 连接超时5秒，读取超时15秒
                )
                
                # 检查响应状态
                response.raise_for_status()
                
                # 获取文件大小
                total_size = int(response.headers.get('content-length', 0))
                print(f"文件大小: {total_size/(1024 * 1024):.2f} MB" if total_size > 0 else "文件大小: 未知")
                
                # 下载文件
                downloaded = 0
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress = downloaded / total_size * 100
                                print(f"\r下载进度: {progress:.1f}%", end='', flush=True)
                
                if total_size > 0:
                    print()
                print(f"✅ 下载成功! 耗时: {time.time()-start_time:.2f}秒")
                return os.path.abspath(filename)
                
            except RequestException as e:
                wait_time = min(5, attempt * 1.5)  # 指数退避等待
                print(f"尝试 #{attempt} 失败: {type(e).__name__}{f' - {str(e)}' if str(e) else ''}")
                if attempt < retries:
                    print(f"等待 {wait_time:.1f}秒后重试...")
                    time.sleep(wait_time)
                    
        print("-" * 60)
    
    print("❌ 所有镜像源均尝试失败")
    return None


def extract_repo(filename="master.zip", extract_dir="./"):
    """
    下载GitHub的ZIP文件并解压
    
    参数:
        zip_url: GitHub仓库的ZIP文件URL
        filename: 保存的文件名 (默认 master.zip)
        extract_dir: 解压目录 (默认当前目录)
    返回:
        解压后的完整目录路径
    """
    try:
        # 确保解压目录存在
        if not os.path.exists(extract_dir):
            os.makedirs(extract_dir, exist_ok=True)
            print(f"创建目录: {os.path.abspath(extract_dir)}")
        
        # 检查zip文件是否存在
        if os.path.exists(filename):
            print(f"已存在 {filename}，直接解压")
        else:
            # 下载zip
            print(f"下载 {filename}...")
            result = download_file_with_fallbacks(filename)
            if result:
                print(f"文件已保存至: {result}")
                if os.path.exists(result):
                    file_size = os.path.getsize(result)
                    print(f"文件大小: {file_size/(1024 * 1024):.2f} MB")
            else:
                print("下载失败，请检查网络或镜像源状态")
                sys.exit(1)

        # 解压ZIP文件
        print(f"解压 {filename} 到: {os.path.abspath(extract_dir)}")
        
        # 确保ZIP文件有效
        if zipfile.is_zipfile(filename):
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                # 获取顶层目录名
                first_dir = zip_ref.namelist()[0].split('/')[0] if zip_ref.namelist() else "repo"
                zip_ref.extractall(extract_dir)
            
            extracted_path = os.path.abspath(os.path.join(extract_dir, first_dir))
            print(f"解压完成! 文件位于: {extracted_path}")
            return extracted_path
        else:
            print(f"文件损坏或不是有效的ZIP文件: {filename}")
            os.remove(filename)
            sys.exit(1)
    
    except zipfile.BadZipFile:
        print(f"ZIP文件损坏，已自动删除 {filename}")
        if os.path.exists(filename):
            os.remove(filename)
        sys.exit(1)
    except Exception as e:
        print(f"解压过程中发生错误: {e}")
        sys.exit(1)

def main():
    """主函数"""
    # 下载并解压
    unpack_dir = extract_repo()
    
    if unpack_dir is None:
        print("解压失败，程序退出")
        sys.exit(1)
    
    print(f"解压成功，目录: {unpack_dir}")
    
    # 源文件路径
    source_path = os.path.join(unpack_dir, "main", "xiaozhi-server")
    # 目标路径
    target_path = os.path.abspath("./src/main/music-xiaozhi-server")
    
    print(f"开始复制: {source_path} → {target_path}")
    
    try:
        # 确保源路径存在
        if not os.path.exists(source_path):
            print(f"源目录不存在: {source_path}")
            raise FileNotFoundError(f"源目录不存在: {source_path}")
            
        # 如果目标路径已存在，先删除
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
            print(f"移除已存在的目标目录: {target_path}")
            
        # 确保目标目录的父目录存在
        parent_dir = os.path.dirname(target_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
            print(f"创建父目录: {parent_dir}")
        
        # 执行复制
        shutil.copytree(source_path, target_path)
        print(f"✅ 复制成功! 内容已保存到: {target_path}")
        
    except Exception as e:
        print(f"❌ 复制过程中发生错误: {e}")
    
    finally:
        # 清理临时文件
        try:
            if os.path.exists("master.zip"):
                os.remove("master.zip")
                print("已删除临时压缩文件")
            
            if unpack_dir and os.path.exists(unpack_dir):
                shutil.rmtree(unpack_dir)
                print(f"已删除临时解压目录: {unpack_dir}")
        except Exception as e:
            print(f"清理临时文件时出错: {e}")

if __name__ == "__main__":
    main()
