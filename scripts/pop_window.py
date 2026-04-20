import re
import json
import os
import requests
import subprocess
import webbrowser
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QTextEdit, QPushButton, QCheckBox, QMessageBox,
                               QFrame, QLabel, QScrollBar, QStyle)
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QDesktopServices, QTextCharFormat, QFont, QColor, QPalette, QCursor
from datetime import datetime, timedelta

GITHUB_REPO_OWNER = "VanillaNahida"
GITHUB_REPO_NAME = "xiaozhi-server-onekey"
STATE_FILE = "./runtime/release_check_state.json"

popup_result = False


class GitHubReleaseChecker(QWidget):
    def __init__(self):
        super().__init__()
        global popup_result
        popup_result = False
        self.latest_release = {}

        self.setWindowTitle(f"小智AI服务端一键包 - 正在获取更新信息...")
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.init_auto_scale()
        self.create_widgets()
        self.center_window()
        self.fetch_latest_release()

    def init_auto_scale(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        reference_width = 1920
        reference_height = 1080

        self.scale_factor = min(screen_width / reference_width, screen_height / reference_height)
        self.scale_factor = max(0.5, min(self.scale_factor, 1.5))

        base_width = int(900 * self.scale_factor)
        base_height = int(700 * self.scale_factor)
        self.setGeometry(0, 0, base_width, base_height)

    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(int(20 * self.scale_factor), int(20 * self.scale_factor),
                                      int(20 * self.scale_factor), int(20 * self.scale_factor))

        self.text_widget = QTextEdit()
        self.text_widget.setReadOnly(True)
        self.text_widget.setFont(QFont('Microsoft YaHei', int(13 * self.scale_factor)))
        main_layout.addWidget(self.text_widget, 1)

        bottom_frame = QFrame()
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(0, int(10 * self.scale_factor), 0, 0)

        bottom_layout.addWidget(QLabel())

        self.no_today_var = False
        self.no_today_checkbox = QCheckBox("今日内不再提示")
        self.no_today_checkbox.stateChanged.connect(lambda state: setattr(self, 'no_today_var', bool(state)))
        bottom_layout.addWidget(self.no_today_checkbox)

        bottom_layout.addStretch()

        update_btn = QPushButton("立即更新")
        update_btn.setFont(QFont('黑体', int(10 * self.scale_factor)))
        update_btn.setMinimumWidth(int(120 * self.scale_factor))
        update_btn.setMinimumHeight(int(40 * self.scale_factor))
        update_btn.clicked.connect(self.on_update_now)
        bottom_layout.addWidget(update_btn)

        skip_btn = QPushButton("暂不更新")
        skip_btn.setFont(QFont('黑体', int(10 * self.scale_factor)))
        skip_btn.setMinimumWidth(int(120 * self.scale_factor))
        skip_btn.setMinimumHeight(int(40 * self.scale_factor))
        skip_btn.clicked.connect(self.on_skip_update)
        bottom_layout.addWidget(skip_btn)

        bottom_layout.addWidget(QLabel())

        main_layout.addWidget(bottom_frame)

    def fetch_latest_release(self):
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases/latest"
            response = requests.get(url)
            response.raise_for_status()

            release_data = response.json()
            self.latest_release = release_data

            if 'tag_name' in release_data:
                self.setWindowTitle(f"小智AI服务端一键包 - 发现新版本！{release_data['tag_name']}")

            release_text = self.format_release_info(release_data)
            self.display_release_info(release_text)

        except requests.exceptions.RequestException as e:
            self.setWindowTitle(f"小智AI服务端一键包 - 获取更新信息失败！")
            self.display_release_info(f"获取信息失败:\n{e}")
        except Exception as e:
            self.display_release_info(f"程序运行出错:\n{str(e)}")

    def format_release_info(self, release_data):
        tag_name = release_data.get("tag_name", "未知版本")
        name = release_data.get("name", "无标题")
        body = release_data.get("body", "无更新说明")
        published_at = release_data.get("published_at", "")
        html_url = release_data.get("html_url", "")

        if published_at:
            published_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            local_date = published_date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            local_date = "未知"

        release_info = f"【新版本发布】{name}\n"
        release_info += f"版本号: {tag_name}\n"
        release_info += f"发布时间: {local_date}\n"
        if html_url:
            release_info += f"查看详情: <a href=\"{html_url}\">{html_url}</a>\n\n"
        release_info += "【更新内容】\n"
        release_info += body

        return release_info

    def display_release_info(self, text):
        html_text = text.replace('\n', '<br>')
        html_text = re.sub(r'(https?://\S+)', r'<a href="\1" style="color: blue; text-decoration: underline;">\1</a>', html_text)
        self.text_widget.setHtml(html_text)
        self.text_widget.scrollToAnchor('')

    def on_update_now(self):
        global popup_result
        popup_result = True

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        python_exe = os.path.join(project_root, "runtime", "conda_env", "python.exe")
        update_script = os.path.join(project_root, "scripts", "update_onekey_pack.py")

        cmd = rf'start "小智AI服务端更新脚本" "{python_exe}" "{update_script}"'
        subprocess.Popen(cmd, cwd=os.path.join(project_root, "scripts"), shell=True)

        if self.no_today_var:
            self.save_state()

        self.close()

    def on_skip_update(self):
        global popup_result
        popup_result = False

        if self.no_today_var:
            self.save_state()

        self.close()

    def center_window(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def save_state(self):
        try:
            state = {
                "last_view_date": datetime.now().isoformat()
            }
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f)
        except Exception:
            pass

    @property
    def result(self):
        global popup_result
        return popup_result


class PopupWindow(QWidget):
    def __init__(self, root=None):
        super().__init__()
        global popup_result
        popup_result = False

        self.setWindowTitle("小智AI一键包 By：香草味的纳西妲喵 - 必看说明")
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.countdown_seconds = 15
        self.countdown_active = True

        self.init_auto_scale()
        self.create_widgets()
        self.center_window()

        if root:
            root.destroy()

    def init_auto_scale(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        reference_width = 1920
        reference_height = 1080

        self.scale_factor = min(screen_width / reference_width, screen_height / reference_height)
        self.scale_factor = max(0.5, min(self.scale_factor, 1.5))

        base_width = int(1280 * self.scale_factor)
        base_height = int(870 * self.scale_factor)
        self.setFixedSize(base_width, base_height)

    def create_widgets(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(int(20 * self.scale_factor), int(20 * self.scale_factor),
                                      int(20 * self.scale_factor), int(20 * self.scale_factor))

        text_frame = QFrame()
        text_layout = QVBoxLayout(text_frame)
        text_layout.setContentsMargins(0, 0, 0, 0)

        self.text_widget = QTextEdit()
        self.text_widget.setReadOnly(True)
        self.text_widget.setFont(QFont('Microsoft YaHei', int(18 * self.scale_factor)))
        text_layout.addWidget(self.text_widget)

        main_layout.addWidget(text_frame, 1)

        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, int(20 * self.scale_factor), 0, 0)

        button_layout.addStretch()

        self.confirm_button = QPushButton(f"请看提示({self.countdown_seconds}s)")
        self.confirm_button.setFont(QFont('黑体', int(10 * self.scale_factor)))
        self.confirm_button.setMinimumWidth(int(180 * self.scale_factor))
        self.confirm_button.setMinimumHeight(int(40 * self.scale_factor))
        self.confirm_button.setEnabled(False)
        self.confirm_button.clicked.connect(self.on_confirm)
        button_layout.addWidget(self.confirm_button)

        cancel_button = QPushButton("取消")
        cancel_button.setFont(QFont('黑体', int(10 * self.scale_factor)))
        cancel_button.setMinimumWidth(int(150 * self.scale_factor))
        cancel_button.setMinimumHeight(int(40 * self.scale_factor))
        cancel_button.clicked.connect(self.on_cancel)
        button_layout.addWidget(cancel_button)

        button_layout.addStretch()

        main_layout.addWidget(button_frame)

        self.add_text_with_links(self.get_readme_content())
        self.start_countdown()

    def get_readme_content(self):
        try:
            with open("必看说明.txt", "r", encoding="utf-8") as file:
                return file.read()
        except Exception:
            return "无法读取必看说明文件，请确保文件存在且格式正确。"

    def add_text_with_links(self, text):
        escaped_text = (text
                       .replace('&', '&amp;')
                       .replace('<', '&lt;')
                       .replace('>', '&gt;'))
        escaped_text = re.sub(r'(https?://\S+)', r'<a href="\1" style="color: blue; text-decoration: underline;">\1</a>', escaped_text)
        escaped_text = escaped_text.replace('\n', '<br>')
        self.text_widget.setHtml(escaped_text)

    def on_confirm(self):
        global popup_result
        if not self.is_scrolled_to_bottom():
            self.show_warning()
            return

        with open("./runtime/.is_first_run", "w") as f:
            f.write("yes")

        popup_result = True
        self.close()
        return True

    def is_scrolled_to_bottom(self):
        scrollbar = self.text_widget.verticalScrollBar()
        return scrollbar.value() >= scrollbar.maximum() * 0.98

    def show_warning(self):
        QMessageBox.warning(self, "警告", "请先阅读完本提示信息！\n看到这个提示说明你没完全阅读完。（滚动条不在最底下）")

    def on_cancel(self):
        global popup_result
        popup_result = False
        self.close()
        return False

    def start_countdown(self):
        if self.countdown_active and self.countdown_seconds > 0:
            self.confirm_button.setText(f"请看上方提示({self.countdown_seconds}s)")
            self.countdown_seconds -= 1
            QTimer.singleShot(1000, self.start_countdown)
        elif self.countdown_seconds == 0:
            self.on_countdown_complete()

    def on_countdown_complete(self):
        self.countdown_active = False
        self.confirm_button.setText("已阅读并确认")
        self.confirm_button.setEnabled(True)

    def center_window(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    @property
    def result(self):
        global popup_result
        return popup_result


def show_github_release():
    global popup_result
    popup_result = False
    if should_show_update():
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        window = GitHubReleaseChecker()
        window.show()
        app.exec()
    return popup_result


def first_run():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    window = PopupWindow()
    window.show()
    app.exec()
    return window.result


def should_show_update():
    try:
        if not os.path.exists(STATE_FILE):
            return True

        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)

        last_view_date = datetime.fromisoformat(state.get("last_view_date", ""))
        now = datetime.now()
        one_day_ago = now - timedelta(days=1)

        return last_view_date < one_day_ago

    except Exception:
        return True


if __name__ == "__main__":
    show_github_release()
    # first_run()
