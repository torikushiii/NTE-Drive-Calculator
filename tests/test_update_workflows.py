# 覆盖英文分支发行版检查与安装包下载行为。

import os
import tempfile
import unittest
import urllib.error
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialog, QLabel, QMessageBox, QPushButton, QTextBrowser, QWidget



class UpdateWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_public_project_links_and_group_notice(self):
        from src.app.constants import (
            BILIBILI_HOME_URL,
            DISCORD_GROUP_URL,
            GITHUB_HOME_URL,
            GITHUB_LATEST_RELEASE_URL,
            GROUP_CHAT_DEVELOPER_HINT,
            GROUP_CHAT_DISCORD_HINT,
            QQ_GROUP_NUMBER,
            SUPPORT_US_URL,
        )
        from src.ui.controllers import update_controller

        opened = []
        window = SimpleNamespace(_open_url=opened.append)
        update_controller._open_update_homepage(window)
        update_controller._open_bilibili_homepage(window)
        update_controller._open_project_homepage(window)
        update_controller._open_support_homepage(window)
        update_controller._open_discord_group(window)

        self.assertEqual(
            [
                GITHUB_LATEST_RELEASE_URL,
                BILIBILI_HOME_URL,
                GITHUB_HOME_URL,
                SUPPORT_US_URL,
                DISCORD_GROUP_URL,
            ],
            opened,
        )
        self.assertEqual(
            "https://github.com/torikushiii/NTE-Drive-Calculator-English/releases",
            GITHUB_LATEST_RELEASE_URL,
        )
        self.assertEqual("https://afdian.com/a/hxwd94666", SUPPORT_US_URL)
        self.assertEqual("1029030672", QQ_GROUP_NUMBER)
        self.assertEqual("若想加入开发群，请先入本群私聊群主", GROUP_CHAT_DEVELOPER_HINT)
        self.assertEqual("获取开发动态，也可在这里交流。", GROUP_CHAT_DISCORD_HINT)
        self.assertEqual("https://discord.gg/P3ZvMN7Hwj", DISCORD_GROUP_URL)

    def test_update_dialog_reuses_about_page_group_notice(self):
        from src.features.settings import updates
        from src.ui.controllers import update_controller

        opened = []

        class Window(QWidget):
            def _open_discord_group(self):
                opened.append("discord")

            def _show_group_chat_notice(self):
                return update_controller._show_group_chat_notice(self)

            @staticmethod
            def _current_style_sheet():
                return ""

            @staticmethod
            def _show_netdisk_download_dialog(_links):
                return None

            @staticmethod
            def _start_update_download():
                return None

        window = Window()
        captured = []

        def capture_dialog(dialog):
            captured.append(dialog)
            return 0

        with patch.object(QDialog, "exec", capture_dialog):
            group_dialog = update_controller._show_group_chat_notice(window)
            updates.show_update_dialog(
                window,
                "",
                {"latest": "2.4.0", "message": "测试更新说明"},
                "2.3.0",
            )

        self.assertEqual(2, len(captured))
        group_text = [label.text() for label in group_dialog.findChildren(QLabel)]
        self.assertNotIn("加入群聊", group_text)
        self.assertIn("1029030672", group_text)
        self.assertIn("若想加入开发群，请先入本群私聊群主", group_text)
        self.assertIn("获取开发动态，也可在这里交流。", group_text)
        self.assertNotIn("关闭", [button.text() for button in group_dialog.findChildren(QPushButton)])
        copy_button = next(
            button for button in group_dialog.findChildren(QPushButton)
            if button.text() == "复制群号"
        )
        copy_button.click()
        self.assertEqual("1029030672", QApplication.clipboard().text())
        self.assertEqual("已复制", copy_button.text())
        update_dialog = captured[1]
        update_group = next(
            button for button in update_dialog.findChildren(QPushButton)
            if button.text() == "加入群聊"
        )
        with patch.object(QDialog, "exec", capture_dialog):
            update_group.click()
        self.assertEqual(3, len(captured))
        self.assertEqual("加入群聊", captured[2].windowTitle())
        notes = update_dialog.findChild(QTextBrowser, "updateReleaseNotes")
        self.assertGreaterEqual(notes.minimumHeight(), 140)
        self.assertLessEqual(notes.minimumHeight(), 300)
        for dialog in (group_dialog, captured[2]):
            discord = next(
                button
                for button in dialog.findChildren(QPushButton)
                if button.text() == "加入 Discord"
            )
            discord.click()
        self.assertEqual(["discord", "discord"], opened)

    def test_netdisk_dialog_uses_channel_cards_without_footer(self):
        from src.ui.controllers import update_controller

        opened = []

        class Window(QWidget):
            def _open_url(self, url):
                opened.append(url)

            @staticmethod
            def _current_style_sheet():
                return ""

        links = (
            ("夸克网盘", "https://pan.quark.cn/s/item"),
            ("百度网盘", "https://pan.baidu.com/s/item"),
            ("迅雷网盘", "https://pan.xunlei.com/s/item"),
        )
        window = Window()
        with patch.object(QDialog, "exec", return_value=0):
            dialog = update_controller._show_netdisk_download_dialog(window, links)

        texts = [label.text() for label in dialog.findChildren(QLabel)]
        self.assertNotIn("选择下载网盘", texts)
        self.assertNotIn("选择一个渠道，随后在浏览器中完成下载。", texts)
        for name, url in links:
            self.assertIn(name, texts)
            self.assertNotIn(url, texts)
        self.assertNotIn("下载地址不再铺满弹窗，按钮与渠道一一对应。", texts)
        buttons = dialog.findChildren(QPushButton)
        self.assertNotIn("取消", [button.text() for button in buttons])
        self.assertEqual(3, len(buttons))
        for name, _url in links:
            button = next(button for button in buttons if button.accessibleName() == f"打开{name}")
            self.assertEqual("打开网盘", button.text())
            button.click()
        self.assertEqual([url for _name, url in links], opened)

    def test_update_download_failure_link_opens_the_project_page(self):
        from src.app.constants import GITHUB_RELEASES_URL
        from src.ui.controllers import update_controller

        link_text = update_controller._update_project_link_text("尝试下载")

        self.assertIn("GitHub English releases", link_text)
        self.assertIn(f'href="{GITHUB_RELEASES_URL}"', link_text)
        self.assertNotIn("mirrorchyan", link_text)

    def test_update_download_only_allows_current_or_newer_release(self):
        from src.ui.controllers import update_controller

        self.assertTrue(
            update_controller._update_download_version_is_available("v2.1.0", "v2.1.0")
        )
        self.assertTrue(
            update_controller._update_download_version_is_available("v2.1.1", "v2.1.0")
        )
        self.assertFalse(
            update_controller._update_download_version_is_available("v2.0.9", "v2.1.0")
        )

    def test_update_older_version_download_requires_explicit_choice(self):
        from src.ui.controllers import update_controller

        class Window(QWidget):
            def __init__(self):
                super().__init__()
                self._update_status = QLabel()
                self._update_download_btn = QPushButton()
                self.downloads = []

            def _start_update_installer_download(self, url):
                self.downloads.append(url)

        window = Window()
        info = {"latest": "2.2.0", "url": "https://example.invalid/setup.exe"}
        with patch.object(update_controller, "APP_VERSION", "2.3.0"), \
                patch.object(update_controller, "log_event"), \
                patch.object(update_controller, "_confirm_update_older_version_download", return_value=False) as confirm:
            window._update_download_btn.setEnabled(False)
            update_controller._on_update_download_ready(window, info)
            confirm.assert_called_once_with(window, "2.3.0", "2.2.0")
            self.assertEqual([], window.downloads)
            self.assertTrue(window._update_download_btn.isEnabled())
            self.assertEqual("已取消较旧版本下载。", window._update_status.text())

        with patch.object(update_controller, "APP_VERSION", "2.3.0"), \
                patch.object(update_controller, "log_event"), \
                patch.object(update_controller, "_confirm_update_older_version_download", return_value=True):
            window._update_download_btn.setEnabled(False)
            update_controller._on_update_download_ready(window, info)
            self.assertEqual([info["url"]], window.downloads)
            self.assertFalse(window._update_download_btn.isEnabled())

        with patch.object(update_controller, "APP_VERSION", "2.3.0"), \
                patch.object(update_controller, "log_event"), \
                patch.object(update_controller, "_confirm_update_older_version_download") as confirm:
            update_controller._on_update_download_ready(
                window, {"latest": "2.3.0", "url": "https://example.invalid/current.exe"},
            )
            confirm.assert_not_called()
            self.assertEqual("https://example.invalid/current.exe", window.downloads[-1])
        window.deleteLater()

    def test_update_older_version_dialog_has_download_and_default_cancel(self):
        from src.ui.controllers import update_controller

        owner = QWidget()
        choices = []

        def choose(dialog):
            buttons = {button.text(): button for button in dialog.buttons()}
            self.assertEqual({"下载", "取消"}, set(buttons))
            self.assertEqual(QMessageBox.Icon.Warning, dialog.icon())
            self.assertIs(dialog.defaultButton(), buttons["取消"])
            self.assertIs(dialog.escapeButton(), buttons["取消"])
            self.assertIn("2.3.0", dialog.informativeText())
            self.assertIn("2.2.0", dialog.informativeText())
            buttons[choices.pop(0)].click()

        choices.extend(("取消", "下载"))
        with patch.object(QMessageBox, "exec", choose), patch.object(QApplication, "beep"):
            self.assertFalse(update_controller._confirm_update_older_version_download(
                owner, "2.3.0", "2.2.0",
            ))
            self.assertTrue(update_controller._confirm_update_older_version_download(
                owner, "2.3.0", "2.2.0",
            ))
        owner.deleteLater()

    def test_update_check_default_timeout_is_short(self):
        from src.features.settings import updates

        seen_timeouts = []
        original_urlopen = updates.urllib.request.urlopen

        def fake_urlopen(_request, **kwargs):
            seen_timeouts.append(kwargs.get("timeout"))
            raise urllib.error.URLError("network unavailable")

        updates.urllib.request.urlopen = fake_urlopen
        try:
            updates.fetch_update_info(
                "https://example.invalid/latest",
                "1.1.0",
            )
        finally:
            updates.urllib.request.urlopen = original_urlopen

        self.assertTrue(seen_timeouts)
        self.assertTrue(all(timeout <= 5 for timeout in seen_timeouts))

    def test_startup_update_error_updates_status_without_prompt(self):
        import src.ui.app as app_module

        class Label:
            def __init__(self):
                self.text = ""

            def setText(self, text):
                self.text = text

        class Window:
            def __init__(self):
                self._update_check_manual = False
                self._update_status = Label()
                self.prompts = []

            def _show_update_failure_netdisk_prompt(self, detail=""):
                self.prompts.append(detail)

        window = Window()
        app_module.MainWindow._on_update_error(window, "timeout")

        self.assertIn("GitHub", window._update_status.text)
        self.assertEqual([], window.prompts)

    def test_update_network_failure_returns_user_facing_result(self):
        from src.features.settings import updates

        original_urlopen = updates.urllib.request.urlopen
        updates.urllib.request.urlopen = lambda *_args, **_kwargs: (_ for _ in ()).throw(
            urllib.error.URLError(OSError(10061, "connection refused"))
        )
        try:
            info = updates.fetch_update_info(
                "https://example.invalid/latest",
                "1.1.0",
                timeout=1,
            )
        finally:
            updates.urllib.request.urlopen = original_urlopen

        self.assertFalse(info["has_release"])
        self.assertFalse(info["newer"])
        self.assertEqual("", info["url"])
        self.assertEqual(updates.UPDATE_FAILURE_MESSAGE, info["message"])
        self.assertNotIn("Traceback", info["message"])

    def test_non_github_response_returns_user_facing_result(self):
        from src.features.settings import updates

        original_urlopen = updates.urllib.request.urlopen

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return '{"code":4001,"msg":"CDK 无效"}'.encode("utf-8")

        updates.urllib.request.urlopen = lambda *_args, **_kwargs: Response()
        try:
            info = updates.fetch_update_info(
                "https://example.invalid/latest",
                "1.1.0",
                timeout=1,
            )
        finally:
            updates.urllib.request.urlopen = original_urlopen

        self.assertFalse(info["has_release"])
        self.assertTrue(info["error"])
        self.assertEqual(updates.UPDATE_FAILURE_MESSAGE, info["message"])

    def test_github_response_includes_version_notes_and_download_url(self):
        from src.features.settings import updates

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return (
                    '[{"tag_name":"v2.1.0-english.1","prerelease":true,'
                    '"body":"修复配装页面","assets":[{'
                    '"name":"NTE_Drive_Calc_English_Setup_2.1.0-english.1.exe",'
                    '"state":"uploaded","browser_download_url":'
                    '"https://github.com/torikushiii/NTE-Drive-Calculator-English/'
                    'releases/download/v2.1.0-english.1/setup.exe"}]}]'
                ).encode("utf-8")

        original_urlopen = updates.urllib.request.urlopen
        requested_urls = []

        def fake_urlopen(request, **_kwargs):
            url = request.full_url if hasattr(request, "full_url") else str(request)
            requested_urls.append(url)
            return Response()

        updates.urllib.request.urlopen = fake_urlopen
        try:
            info = updates.fetch_update_info(
                "https://api.github.com/repos/torikushiii/NTE-Drive-Calculator-English/releases",
                "2.0.0",
                timeout=1,
            )
        finally:
            updates.urllib.request.urlopen = original_urlopen

        self.assertTrue(info["has_release"])
        self.assertTrue(info["newer"])
        self.assertEqual("2.1.0-english.1", info["latest"])
        self.assertIn("NTE-Drive-Calculator-English/releases/download/", info["url"])
        self.assertEqual("修复配装页面", info["message"])
        self.assertEqual(
            "https://api.github.com/repos/torikushiii/NTE-Drive-Calculator-English/releases",
            requested_urls[0],
        )

    def test_update_installer_download_writes_valid_exe_and_reports_progress(self):
        from src.features.settings import updates

        class Response:
            headers = {"Content-Length": "8"}

            def __init__(self):
                self._blocks = [b"MZtest", b"ok", b""]

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self, _size):
                return self._blocks.pop(0)

        original_urlopen = updates.urllib.request.urlopen
        updates.urllib.request.urlopen = lambda *_args, **_kwargs: Response()
        updates_progress = []
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                result = updates.download_update_installer(
                    "https://download.example/NTE-Drive-Calc.exe",
                    destination_dir=temp_dir,
                    progress_callback=lambda current, total: updates_progress.append((current, total)),
                )
                installer = Path(result["path"])
                self.assertEqual(b"MZtestok", installer.read_bytes())
                self.assertEqual(8, result["downloaded"])
        finally:
            updates.urllib.request.urlopen = original_urlopen

        self.assertEqual((0, 8), updates_progress[0])
        self.assertEqual((8, 8), updates_progress[-1])

    def test_update_installer_download_removes_partial_file_when_cancelled(self):
        from src.features.settings import updates

        class Response:
            headers = {"Content-Length": "16"}

            def __init__(self):
                self._blocks = [b"MZfirst", b"second", b""]

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self, _size):
                return self._blocks.pop(0)

        original_urlopen = updates.urllib.request.urlopen
        updates.urllib.request.urlopen = lambda *_args, **_kwargs: Response()
        cancelled = {"value": False}
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                with self.assertRaises(updates.UpdateDownloadCancelled):
                    updates.download_update_installer(
                        "https://download.example/NTE-Drive-Calc.exe",
                        destination_dir=temp_dir,
                        progress_callback=lambda *_args: cancelled.__setitem__("value", True),
                        cancel_check=lambda: cancelled["value"],
                    )
                self.assertEqual([], list(Path(temp_dir).iterdir()))
        finally:
            updates.urllib.request.urlopen = original_urlopen

    def test_update_check_uses_the_fork_and_keeps_the_specific_release_link(self):
        from src.ui.controllers import update_controller

        captured = {}
        original_fetch = update_controller.fetch_update_info

        def fake_fetch(api_url, version):
            captured.update(api_url=api_url, version=version)
            return {"has_release": True, "latest": "2.3.1-english.2", "release_url": "https://example.invalid/tag"}

        class Window:
            pass

        update_controller.fetch_update_info = fake_fetch
        try:
            info = update_controller._fetch_update_info(Window())
        finally:
            update_controller.fetch_update_info = original_fetch

        self.assertIn("api.github.com/repos/torikushiii/NTE-Drive-Calculator-English/releases", captured["api_url"])
        self.assertEqual("https://example.invalid/tag", info["release_url"])





if __name__ == "__main__":

    unittest.main()
