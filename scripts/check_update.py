import subprocess
import os
from typing import Tuple, List

# 获取脚本所在目录的上级目录
script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 内嵌Git客户端路径
git_path = os.path.join(script_dir, "runtime", "git-2.48.1", "cmd", "git.exe")

# Git路径
git_path = os.path.join(script_dir, "runtime", "git-2.48.1", "cmd", "git.exe")

def fetch_remote() -> bool:
    try:
        subprocess.run([git_path, 'fetch'], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError as e:
        print(f'远程仓库更新失败: {e.output.decode()}')
        return False

def get_branch_commits(branch_name: str) -> Tuple[List[str], List[str]]:
    try:
        local = subprocess.check_output(
            [git_path, 'log', '--pretty=format:%H', branch_name],
            text=True,
            encoding='utf-8',
            errors='ignore'
        ).splitlines()

        remote = subprocess.check_output(
            [git_path, 'log', '--pretty=format:%H', f'origin/{branch_name}'],
            text=True
        ).splitlines()

        return local, remote
    except subprocess.CalledProcessError as e:
        print(f'获取提交记录失败: {e.output.decode()}')
        return [], []

def format_commit_date(commit_date_str):
    """将Git提交日期格式转换为中文显示格式"""
    # 定义月份和星期的映射字典
    month_map = {
        'Jan': '1月', 'Feb': '2月', 'Mar': '3月', 'Apr': '4月',
        'May': '5月', 'Jun': '6月', 'Jul': '7月', 'Aug': '8月',
        'Sep': '9月', 'Oct': '10月', 'Nov': '11月', 'Dec': '12月'
    }
    weekday_map = {
        'Mon': '星期一', 'Tue': '星期二', 'Wed': '星期三',
        'Thu': '星期四', 'Fri': '星期五', 'Sat': '星期六', 'Sun': '星期日'
    }

    # 提取各部分日期时间信息
    weekday_en = commit_date_str[0]
    month_en = commit_date_str[1]
    day = commit_date_str[2]
    time = commit_date_str[3]
    year = commit_date_str[4]

    # 转换为中文格式
    weekday_zh = weekday_map.get(weekday_en, weekday_en)
    month_zh = month_map.get(month_en, month_en)

    # 按要求的格式重组
    formatted_date = f'{year}年{month_zh}{day}日 {weekday_zh} {time}'
    
    return formatted_date

def check_updates():
    print("检查更新中……")
    current_branch = subprocess.check_output(
        [git_path, 'rev-parse', '--abbrev-ref', 'HEAD'],
        text=True
    ).strip()

    if not fetch_remote():
        return

    local_commits, remote_commits = get_branch_commits(current_branch)

    if not remote_commits:
        print('远程分支不存在或无提交')
        return

    latest_remote = remote_commits[0]
    print(f'远程最新提交: {latest_remote}')

    if latest_remote not in local_commits:
        commit_range = f'{local_commits[0]}..{latest_remote}'
        # 计算新增的提交数量（远程有而本地没有的提交）
        new_commits = [commit for commit in remote_commits if commit not in local_commits]
        print(f'\n❗发现 {len(new_commits)} 个新提交：\n{"="*50}')
        # 获取详细提交信息
        log_output = subprocess.check_output(
            [git_path, 'log', commit_range, 
             '--pretty=format:Commit Hash: %C(yellow)%H%Creset %C(cyan)%Creset%n作者: %C(green)%an <%ae>%Creset%n提交信息：%n    %s%n分支信息: %C(auto)%d%Creset'],
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        # 获取提交日期
        commit_date_str = subprocess.check_output(
            [git_path, 'log', commit_range, '--pretty=format:%cd'],
            text=True,
            encoding='utf-8',
            errors='ignore'
        ).strip().rsplit()
        # 调用函数并打印结果
        formatted_date = format_commit_date(commit_date_str)
        print(f'\n\033[33m[提交详细信息]\033[0m\n提交日期: {formatted_date}\n{log_output}\n')
        print(f'{"="*50}\n建议关闭窗口后，运行更新脚本获取一键包最新版！')
    else:
        print('\n🎉 恭喜！你的本地一键包已是最新版本！')
        latest_commit = subprocess.check_output(
            [git_path, 'log', '-1', '--pretty=format:Commit Hash: %C(yellow)%H%Creset %C(cyan)%Creset%n作者: %C(green)%an <%ae>%Creset%n提交信息：%n    %s%n分支信息: %C(auto)%d%Creset'],
            text=True,
            encoding='utf-8',
            errors='ignore'
        )

        # 提交日期格式化
        commit_date_str = subprocess.check_output(
            [git_path, 'log', '-1', '--pretty=format:%cd'],
            text=True,
            encoding='utf-8',
            errors='ignore'
        ).strip().rsplit()

        # 调用函数并打印结果
        formatted_date = format_commit_date(commit_date_str)
        print(f'\n当前最新提交: \n提交日期: {formatted_date}\n{latest_commit}')
    
    print("\n检查完毕！正在启动小智AI服务端……")
        
if __name__ == '__main__':
    check_updates()
    
