import re
import json
import os
import requests
import subprocess
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta

# GitHub仓库信息
GITHUB_REPO_OWNER = "VanillaNahida"
GITHUB_REPO_NAME = "xiaozhi-server-onekey"
# 本地存储文件路径，用于记录用户查看状态
STATE_FILE = "./runtime/release_check_state.json"

# GitHubReleaseChecker类 - 用于显示GitHub更新信息
class GitHubReleaseChecker:
    def __init__(self):
        global popup_result
        # 重置全局结果变量
        popup_result = False
        # 初始化最新release数据为空字典
        self.latest_release = {}
        
        # 创建主窗口
        self.root = tk.Tk()
        # 设置初始通用标题
        self.root.title(f"小智AI服务端一键包 - 正在获取更新信息...")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        # 设置窗口置顶显示
        self.root.attributes('-topmost', True)
        
        # 创建大字体按钮样式
        self.style = ttk.Style()
        self.style.configure("LargeFont.TButton", font=('黑体', 13))
        
        # 初始化窗口组件
        self.create_widgets()
        
        # 居中显示窗口
        self.center_window()
        
        # 获取GitHub最新Release信息
        self.fetch_latest_release()
        
        # 启动主循环
        self.root.mainloop()
    
    def create_widgets(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建滚动文本框
        self.text_frame = ttk.Frame(self.main_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.text_widget = scrolledtext.ScrolledText(self.text_frame, wrap=tk.WORD, 
                                                   font=('Microsoft YaHei', 13),
                                                   width=80, height=25)
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # 绑定鼠标事件来检测链接
        self.text_widget.bind('<Button-1>', self.on_text_click)
        self.text_widget.bind('<Motion>', self.on_text_motion)
        
        self.text_widget.config(state=tk.DISABLED)
        
        # 创建底部按钮和复选框区域
        self.bottom_frame = ttk.Frame(self.main_frame)
        self.bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 创建左侧占位
        ttk.Frame(self.bottom_frame, width=20).pack(side=tk.LEFT)
        
        # 创建复选框 - 今日内不再提示
        self.no_today_var = tk.BooleanVar(value=False)
        self.no_today_checkbox = ttk.Checkbutton(self.bottom_frame, 
                                               text="今日内不再提示", 
                                               variable=self.no_today_var)
        self.no_today_checkbox.pack(side=tk.LEFT, padx=10, pady=10)
        
        # 创建中间占位使按钮居中
        ttk.Frame(self.bottom_frame).pack(side=tk.LEFT, expand=True)
        
        # 创建立即更新按钮
        self.update_now_button = ttk.Button(self.bottom_frame, text="立即更新", 
                                          command=self.on_update_now, padding=(0, 10),
                                          style="LargeFont.TButton", width=10)
        self.update_now_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        # 创建暂不更新按钮
        self.skip_update_button = ttk.Button(self.bottom_frame, text="暂不更新", 
                                           command=self.on_skip_update, padding=(0, 10),
                                           style="LargeFont.TButton", width=10)
        self.skip_update_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        # 创建右侧占位
        ttk.Frame(self.bottom_frame, width=20).pack(side=tk.LEFT)
    
    def fetch_latest_release(self):
        try:
            # 构建GitHub API URL
            url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases/latest"
            
            # 发送请求获取最新release信息
            response = requests.get(url)
            response.raise_for_status()  # 检查请求是否成功
            
            # 解析JSON响应
            release_data = response.json()
            
            # 保存最新release数据
            self.latest_release = release_data
            
            # 更新窗口标题，显示tag名称
            if 'tag_name' in release_data:
                self.root.title(f"小智AI服务端一键包 - 发现新版本！{release_data['tag_name']}")
                # 刷新窗口以确保标题更新立即生效
                self.root.update_idletasks()
            
            # 格式化release信息
            release_text = self.format_release_info(release_data)
            
            # 显示信息
            self.display_release_info(release_text)
            
        except requests.exceptions.RequestException as e:
            # 处理请求异常
            error_message = f"获取信息失败:\n{e}"
            # 更新窗口标题，显示错误信息
            self.root.title(f"小智AI服务端一键包 - 获取更新信息失败！")
            # 刷新窗口以确保标题更新立即生效
            self.root.update_idletasks()

            self.display_release_info(error_message)
        except Exception as e:
            # 处理其他异常
            error_message = f"程序运行出错:\n{str(e)}"
            self.display_release_info(error_message)
    
    def format_release_info(self, release_data):
        # 提取并格式化release信息
        tag_name = release_data.get("tag_name", "未知版本")
        name = release_data.get("name", "无标题")
        body = release_data.get("body", "无更新说明")
        published_at = release_data.get("published_at", "")
        html_url = release_data.get("html_url", "")
        
        # 格式化发布日期
        if published_at:
            # 将ISO格式时间转换为可读格式
            published_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            # 转换为本地时间
            local_date = published_date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            local_date = "未知"
        
        # 构建完整的发布信息文本
        release_info = f"【新版本发布】{name}\n"
        release_info += f"版本号: {tag_name}\n"
        release_info += f"发布时间: {local_date}\n"
        if html_url:
            release_info += f"查看详情: {html_url}\n\n"
        release_info += "【更新内容】\n"
        release_info += body
        
        return release_info
    
    def tag_links(self):
        # 查找所有URL并添加标签
        url_pattern = r'https?://\S+'
        text = self.text_widget.get(1.0, tk.END)
        
        # 搜索所有URL
        for match in re.finditer(url_pattern, text):
            start_pos = match.start()
            end_pos = match.end()
            
            # 计算文本框中的位置
            start_line, start_char = self.get_line_char(start_pos, text)
            end_line, end_char = self.get_line_char(end_pos, text)
            
            # 为链接添加标签
            start_index = f"{start_line}.{start_char}"
            end_index = f"{end_line}.{end_char}"
            
            self.text_widget.tag_add("link", start_index, end_index)
        
        # 配置链接标签的样式
        self.text_widget.tag_config("link", foreground="blue", underline=True)
    
    def get_line_char(self, pos, text):
        # 计算给定字符位置对应的行和列
        lines = text[:pos].split('\n')
        line = len(lines)
        char = len(lines[-1])
        return line, char
    
    def on_text_click(self, event):
        # 获取点击位置的所有标签
        tags = self.text_widget.tag_names(f"@{event.x},{event.y}")
        
        # 如果点击了链接
        if "link" in tags:
            # 获取光标位置
            index = self.text_widget.index(f"@{event.x},{event.y}")
            
            # 查找该位置所在的整个链接文本
            # 获取所有link标签的范围
            ranges = list(self.text_widget.tag_ranges("link"))
            for i in range(0, len(ranges), 2):
                start = ranges[i]
                end = ranges[i+1]
                if self.text_widget.compare(index, ">=", start) and self.text_widget.compare(index, "<", end):
                    url = self.text_widget.get(start, end)
                    # 打开链接
                    webbrowser.open_new(url)
                    break
    
    def on_text_motion(self, event):
        # 检查鼠标是否悬停在链接上并更改光标
        try:
            tags = self.text_widget.tag_names(f"@{event.x},{event.y}")
            if "link" in tags:
                self.text_widget.config(cursor="hand2")
            else:
                self.text_widget.config(cursor="xterm")
        except tk.TclError:
            # 鼠标移出文本区域时忽略错误
            self.text_widget.config(cursor="xterm")
    
    def display_release_info(self, text):
        # 在文本框中显示发布信息
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, text)
        # 标记链接
        self.tag_links()
        self.text_widget.config(state=tk.DISABLED)
        # 滚动到顶部
        self.text_widget.see(1.0)
    
    def on_confirm(self):
        # 处理确认按钮点击事件（兼容旧代码）
        self.on_skip_update()
        
    def on_update_now(self):
        global popup_result
        # 处理立即更新按钮点击事件，设置结果为True表示选择了立即更新
        popup_result = True

        # 获取项目根目录并构建路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        python_exe = os.path.join(project_root, "runtime", "conda_env", "python.exe")
        update_script = os.path.join(project_root, "scripts", "update_onekey_pack.py")
        
        # 启动更新脚本
        cmd = rf'start "小智AI服务端更新脚本" "{python_exe}" "{update_script}"'
        subprocess.Popen(cmd, cwd=os.path.join(project_root, "scripts"), shell=True)
        
        # 如果勾选了今日内不再提示，保存状态
        if self.no_today_var.get():
            self.save_state()
        
        # 关闭窗口
        self.root.destroy()
        
    def on_skip_update(self):
        global popup_result
        # 处理暂不更新按钮点击事件
        # 设置结果为False表示选择了暂不更新
        popup_result = False
        # 如果勾选了今日内不再提示，保存状态
        if self.no_today_var.get():
            self.save_state()
        
        # 关闭窗口
        self.root.destroy()
    
    def center_window(self):
        # 计算窗口居中位置
        self.root.update_idletasks()  # 确保获取到正确的窗口尺寸
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 计算居中位置
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # 设置窗口位置
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    @property
    def result(self):
        # 返回全局结果变量的值
        global popup_result
        return popup_result
    
    @property
    def result(self):
        # 返回全局结果变量的值
        global popup_result
        return popup_result
    
    @property
    def result(self):
        # 返回全局结果变量的值
        global popup_result
        return popup_result
    
    def save_state(self):
        # 保存用户查看状态
        try:
            state = {
                "last_view_date": datetime.now().isoformat()
            }
            
            # 写入状态文件
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f)
        except Exception:
            # 忽略保存错误
            pass

# 全局变量 - 用于存储弹窗的结果状态
popup_result = False

# PopupWindow类 - 用于显示必看说明
class PopupWindow:
    def __init__(self, root):
        global popup_result
        # 重置全局结果变量
        popup_result = False
        
        # 主窗口设置
        self.root = root
        self.root.title("小智AI一键包 By：香草味的纳西妲喵 - 必看说明")
        self.root.geometry("1280x870")
        self.root.resizable(False, False)
        
        # 创建大字体按钮样式
        self.style = ttk.Style()
        self.style.configure("LargeFont.TButton", font=('黑体', 12))
        
        # 窗口居中显示
        self.center_window()
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 倒计时相关变量初始化
        self.countdown_seconds = 3
        self.countdown_active = True
        
        # 初始化其他组件
        self.create_widgets()
        
    def create_widgets(self):
        # 创建只读文本框
        self.text_frame = ttk.Frame(self.main_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        
        # 创建垂直滚动条
        self.scrollbar = ttk.Scrollbar(self.text_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建Text组件并关联滚动条
        self.text_widget = tk.Text(self.text_frame, wrap=tk.WORD, font=('Microsoft YaHei', 18),
                                  bg=self.root.cget('bg'), bd=0, highlightthickness=0,
                                  yscrollcommand=self.scrollbar.set)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 配置滚动条控制文本框
        self.scrollbar.config(command=self.text_widget.yview)
        
        # 设置为只读
        self.text_widget.config(state=tk.DISABLED)
        
        # 添加示例文本和链接
        self.add_text_with_links(self.get_readme_content())
        
        # 绑定鼠标事件来检测链接
        self.text_widget.bind('<Button-1>', self.on_text_click)
        self.text_widget.bind('<Motion>', self.on_text_motion)
        
        # 创建按钮框架 - 确保在文本框下方有足够空间
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=(20, 20))
        
        # 创建内部框架来居中按钮
        self.inner_button_frame = ttk.Frame(self.button_frame)
        self.inner_button_frame.pack(fill=tk.X, expand=True)
        
        # 创建左侧占位
        ttk.Label(self.inner_button_frame).pack(side=tk.LEFT, expand=True)
        
        # 创建确认按钮并绑定事件 - 初始禁用状态，增加高度和字体大小
        self.confirm_button = ttk.Button(self.inner_button_frame, text=f"请看提示({self.countdown_seconds}s)", 
                                        width=18, command=self.on_confirm, state=tk.DISABLED, padding=(0, 10), 
                                        style="LargeFont.TButton")
        self.confirm_button.pack(side=tk.LEFT, padx=20)
        
        # 启动倒计时
        self.start_countdown()
        
        # 创建取消按钮并绑定事件，增加高度和字体大小以保持一致性
        self.cancel_button = ttk.Button(self.inner_button_frame, text="取消", width=15, command=self.on_cancel, padding=(0, 10), 
                                       style="LargeFont.TButton")
        self.cancel_button.pack(side=tk.LEFT, padx=20)
        
        # 创建右侧占位
        ttk.Label(self.inner_button_frame).pack(side=tk.RIGHT, expand=True)
    
    def get_readme_content(self):
        # 读取必看说明.txt文件内容
        try:
            with open("必看说明.txt", "r", encoding="utf-8") as file:
                return file.read()
        except Exception:
            return "无法读取必看说明文件，请确保文件存在且格式正确。"
    
    def add_text_with_links(self, text):
        # 启用文本框进行编辑
        self.text_widget.config(state=tk.NORMAL)
        
        # 清空现有内容
        self.text_widget.delete(1.0, tk.END)
        
        # 插入文本
        self.text_widget.insert(tk.END, text)
        
        # 查找并标记链接
        self.tag_links()
        
        # 再次设置为只读
        self.text_widget.config(state=tk.DISABLED)
    
    def tag_links(self):
        # 查找所有URL并添加标签
        url_pattern = r'https?://\S+'
        text = self.text_widget.get(1.0, tk.END)
        
        # 搜索所有URL
        for match in re.finditer(url_pattern, text):
            start_pos = match.start()
            end_pos = match.end()
            
            # 计算文本框中的位置
            start_line, start_char = self.get_line_char(start_pos, text)
            end_line, end_char = self.get_line_char(end_pos, text)
            
            # 为链接添加标签
            start_index = f"{start_line}.{start_char}"
            end_index = f"{end_line}.{end_char}"
            
            self.text_widget.tag_add("link", start_index, end_index)
        
        # 配置链接标签的样式
        self.text_widget.tag_config("link", foreground="blue", underline=True)
    
    def get_line_char(self, pos, text):
        # 计算给定字符位置对应的行和列
        lines = text[:pos].split('\n')
        line = len(lines)
        char = len(lines[-1])
        return line, char
    
    def on_text_click(self, event):
        # 获取点击位置的所有标签
        tags = self.text_widget.tag_names(f"@{event.x},{event.y}")
        
        # 如果点击了链接
        if "link" in tags:
            # 获取光标位置
            index = self.text_widget.index(f"@{event.x},{event.y}")
            
            # 查找该位置所在的整个链接文本
            # 获取所有link标签的范围
            ranges = list(self.text_widget.tag_ranges("link"))
            for i in range(0, len(ranges), 2):
                start = ranges[i]
                end = ranges[i+1]
                if self.text_widget.compare(index, ">=", start) and self.text_widget.compare(index, "<", end):
                    url = self.text_widget.get(start, end)
                    # 打开链接
                    webbrowser.open_new(url)
                    break
    
    def on_text_motion(self, event):
        # 检查鼠标是否悬停在链接上并更改光标
        try:
            tags = self.text_widget.tag_names(f"@{event.x},{event.y}")
            if "link" in tags:
                self.text_widget.config(cursor="hand2")
            else:
                self.text_widget.config(cursor="xterm")
        except tk.TclError:
            # 鼠标移出文本区域时忽略错误
            self.text_widget.config(cursor="xterm")
    
    def on_confirm(self):
        global popup_result
        # 确认按钮功能 - 检查是否滚动到底部
        if not self.is_scrolled_to_bottom():
            # 如果没有滚动到底部，显示警告
            self.show_warning()
            return
        
        with open("./runtime/.is_first_run", "w") as f:
            f.write("yes") 
        
        # 设置全局结果为True表示确认
        popup_result = True
        self.root.destroy()
        return True
    
    def is_scrolled_to_bottom(self):
        # 检查文本是否已滚动到底部
        # 获取当前视图的顶部和底部位置
        view_top, view_bottom = self.text_widget.yview()
        # 如果视图底部接近1.0（文本末尾），则认为已滚动到底部
        # 使用0.98作为阈值，允许有少量误差
        return view_bottom >= 0.98
    
    def show_warning(self):
        # 显示警告弹窗
        messagebox.showwarning("警告", "请先阅读完本提示信息！\n看到这个提示说明你没完全阅读完。（滚动条不在最底下）")
    
    def on_cancel(self):
        global popup_result
        # 取消按钮功能
        # 设置全局结果为False表示取消
        popup_result = False
        self.root.destroy()
        return False
        
    def start_countdown(self):
        # 启动倒计时功能
        if self.countdown_active and self.countdown_seconds > 0:
            # 更新按钮文本
            self.confirm_button.config(text=f"请看上方提示({self.countdown_seconds}s)")
            # 减少倒计时秒数
            self.countdown_seconds -= 1
            # 1秒后再次调用自身
            self.root.after(1000, self.start_countdown)
        elif self.countdown_seconds == 0:
            # 倒计时结束，启用按钮
            self.on_countdown_complete()
    
    def on_countdown_complete(self):
        # 倒计时结束时调用，更新按钮状态
        self.countdown_active = False
        self.confirm_button.config(text="已阅读并确认", state=tk.NORMAL)
    
    def center_window(self):
        # 计算窗口居中位置
        self.root.update_idletasks()  # 确保获取到正确的窗口尺寸
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 计算居中位置
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # 设置窗口位置
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    @property
    def result(self):
        # 返回全局结果变量的值
        global popup_result
        return popup_result

# 公共函数 - 用于显示GitHub更新信息
def show_github_release():
    """显示GitHub更新信息弹窗并返回用户选择结果
    
    Returns:
        bool: True表示用户选择了立即更新，False表示用户选择了暂不更新
    """
    global popup_result
    # 重置结果变量
    popup_result = False
    # 检查是否应该显示更新提示
    if should_show_update():
        app = GitHubReleaseChecker()
    # 返回用户选择结果
    return popup_result

# 公共函数 - 用于显示必看说明弹窗
def first_run():
    """显示必看说明弹窗"""
    root = tk.Tk()
    app = PopupWindow(root)
    root.mainloop()
    return app.result

# 辅助函数 - 检查是否应该显示更新提示
def should_show_update():
    """检查是否应该显示更新提示"""
    try:
        # 如果状态文件不存在，则显示更新
        if not os.path.exists(STATE_FILE):
            return True
        
        # 读取状态文件
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        
        # 获取上次查看时间
        last_view_date = datetime.fromisoformat(state.get("last_view_date", ""))
        
        # 检查是否超过一天
        now = datetime.now()
        one_day_ago = now - timedelta(days=1)
        
        # 如果上次查看时间在一天前，则显示更新
        return last_view_date < one_day_ago
    
    except Exception:
        # 任何错误都显示更新
        return True

# 如果直接运行此文件，则作为示例
if __name__ == "__main__":
    # 显示更新提示弹窗
    show_github_release()