import shutil
import os
import time

# 复制文件的函数
def copy_config_and_models(scripts_dir):
    """复制配置文件"""

    print('''
开始同步配置文件，此操作会强制覆盖掉音乐小智目录下的配置文件.
如果你不想文件被覆盖，请在一键包根目录下，新建一个名为 nosync.txt 文本文件，只需存在这个文件即可，不需要在文件中写入任何内容

注意：如果在一键包根目录下，新建了nosync.txt文件，那么在每次启动音乐小智服务端时，
都不会同步配置文件，若你忘记修改对应小智服务端的配置文件，可能会导致服务端运行异常.
建议你了解并熟悉后再考虑关闭启动后自动同步配置文件的功能
    ''')

    # 检查是否存在nosync.txt文件
    if os.path.exists(rf"{scripts_dir}\nosync.txt"):
        print("已跳过同步配置文件")
        return True
    try:
        # 检查目录是否存在
        if not os.path.exists(rf"{scripts_dir}\src\main\music-xiaozhi-server"):
            print("音乐小智目录不存在，已取消同步")
            return False
        # 检查配置文件是否存在
        if os.path.exists(rf"{scripts_dir}\src\main\music-xiaozhi-server\data"):
            print("正在同步配置文件到音乐小智目录……")
            shutil.rmtree(rf"{scripts_dir}\src\main\music-xiaozhi-server\data")
            print("已删除存在的配置文件")
            time.sleep(0.5)
            shutil.copytree(rf"{scripts_dir}\src\main\xiaozhi-server\data", rf"{scripts_dir}\src\main\music-xiaozhi-server\data")
            print("配置文件同步完成！")
        else:
            # 复制配置文件到音乐小智目录
            print("正在同步配置文件到音乐小智目录……")
            shutil.copytree(rf"{scripts_dir}\src\main\xiaozhi-server\data", rf"{scripts_dir}\src\main\music-xiaozhi-server\data")
            print("配置文件同步完成！")
        return True
    except Exception as e:
        print(f"❌ 复制文件失败: {e}")
        return False

if __name__ == "__main__":
    # 获取脚本所在目录
    scripts_dir = os.path.dirname(__file__)
    # 复制配置文件
    copy_config_and_models(scripts_dir)
