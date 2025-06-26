import os
import shutil
from tqdm import tqdm

def copy_file_with_progress(src, dst, chunk_size=1024 * 1024):
    """复制文件并显示进度条"""
    try:
        total_size = os.path.getsize(src)  # 获取文件总大小
        with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
            # 初始化进度条
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"复制 {os.path.basename(src)}") as pbar:
                while True:
                    chunk = fsrc.read(chunk_size)  # 分块读取（默认1MB）
                    if not chunk:
                        break
                    fdst.write(chunk)
                    pbar.update(len(chunk))  # 更新进度条
        print(f"✅ 文件复制成功: {src} → {dst}")
    except Exception as e:
        print(f"❌ 复制失败: {e}")

# 复制文件的函数
def copy_config_and_models():
    """复制配置文件和模型文件"""
    try:
        # 检查配置文件是否存在
        if os.path.exists(rf"{scripts_dir}\src\main\music-xiaozhi-server\data"):
            print("配置文件已存在，跳过复制")
        else:
            # 复制配置文件到音乐小智目录
            print("开始复制配置文件到音乐小智目录")
            shutil.copytree(rf"{scripts_dir}\src\main\xiaozhi-server\data", rf"{scripts_dir}\src\main\music-xiaozhi-server\data")
            print("配置文件复制完成！")

        if os.path.exists(rf"{scripts_dir}\src\main\music-xiaozhi-server\models\SenseVoiceSmall\model.pt"):
            print("语音识别模型文件已存在，跳过复制")
        else:
            # 复制语音识别模型文件到音乐小智目录
            print("开始复制语音识别模型文件到音乐小智目录，可能需要较长时间，请耐心等待~")
            copy_file_with_progress(rf"{scripts_dir}\src\main\xiaozhi-server\models\SenseVoiceSmall\model.pt", rf"{scripts_dir}\src\main\music-xiaozhi-server\models\SenseVoiceSmall\model.pt")
            print("语音识别模型文件复制完成！")
        return True
    except Exception as e:
        print(f"❌ 复制模型文件失败: {e}")
        return False

if __name__ == "__main__":
    # 获取脚本所在目录
    scripts_dir = os.path.dirname(__file__)

    # 检查是否存在小智服务器文件夹
    if not os.path.exists(rf"{scripts_dir}\src\main\music-xiaozhi-server"):
        while True:
            choice = input("你还没有下载音乐小智服务器，是否去下载？（Y/n）（回车确认，输入n取消）").strip().lower()
            
            if choice in ['y', 'yes', '']:
                print("下载音乐小智服务器")
                # 导入模块下载小智的代码
                from get_music_xiaozhi_server import main
                main()
                print("下载音乐小智服务端DLC成功！")
                # 复制模型文件和配置文件
                copy_config_and_models()
                break
            elif choice in ['n', 'no']:
                print("取消下载")
                break
            else:
                print("无效输入，请输入 Y(是) 或 n(否)")
    else:
        print("你似乎已经下载过音乐小智服务端了，请回到一键包根目录，尝试启动音乐小智服务端吧！")


