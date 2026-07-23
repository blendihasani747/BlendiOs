"""Built-in web browser for BlendiOS."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests
from PySide6.QtCore import QThread, QUrl, Qt, QObject, Signal, Slot
from PySide6.QtGui import QAction, QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLineEdit,
    QLabel,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from blendios.apps.base_app import BaseApp
from blendios.constants import DEFAULT_DATA_DIR
from blendios.common.paths import blendios_downloads_dir

try:
    from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
    from PySide6.QtWebEngineWidgets import QWebEngineView
except Exception:  # pragma: no cover - graceful fallback when webengine missing
    QWebEngineProfile = None
    QWebEnginePage = None
    QWebEngineSettings = None
    QWebEngineView = None


@dataclass(slots=True)
class BrowserTabState:
    """State holder for each browser tab."""

    home_url: str = "https://duckduckgo.com"


class DownloadWorker(QObject):
    """Background downloader to keep browser UI responsive."""

    progress = Signal(int)
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, url: str, destination: str) -> None:
        super().__init__()
        self.url = url
        self.destination = destination

    @Slot()
    def run(self) -> None:
        try:
            with requests.get(self.url, stream=True, timeout=45) as response:
                response.raise_for_status()
                total = int(response.headers.get("content-length", "0") or 0)
                downloaded = 0
                with open(self.destination, "wb") as output:
                    for chunk in response.iter_content(chunk_size=64 * 1024):
                        if not chunk:
                            continue
                        output.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            percent = max(0, min(100, int(downloaded * 100 / total)))
                            self.progress.emit(percent)
            self.progress.emit(100)
            self.finished.emit(self.destination)
        except Exception as exc:  # pragma: no cover - network and filesystem variability
            self.failed.emit(str(exc))


class BrowserWidget(QWidget):
    """Tabbed browser UI with basic navigation and bookmarks."""

    def __init__(self) -> None:
        super().__init__()
        self._profile: QWebEngineProfile | None = None
        self._active_downloads: list[object] = []
        self._pending_download_navigation = False
        self._browser_data_dir = DEFAULT_DATA_DIR / "browser"
        self._browser_data_dir.mkdir(parents=True, exist_ok=True)
        self._bookmarks: list[str] = [
            "https://duckduckgo.com",
            "https://docs.python.org/3/",
            "https://doc.qt.io/",
        ]
        self._incognito = False

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)
        root.addLayout(toolbar)

        self.back_button = QPushButton("Back")
        self.forward_button = QPushButton("Forward")
        self.refresh_button = QPushButton("Refresh")
        self.stop_button = QPushButton("Stop")
        self.home_button = QPushButton("Home")
        self.new_tab_button = QPushButton("+")
        self.bookmark_button = QToolButton()
        self.bookmark_button.setText("Bookmarks")
        self.bookmark_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.download_button = QPushButton("Download")
        self.incognito_button = QPushButton("Incognito Off")

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search term")
        self.url_bar.returnPressed.connect(self._load_from_url_bar)

        for widget in (
            self.back_button,
            self.forward_button,
            self.refresh_button,
            self.stop_button,
            self.home_button,
            self.url_bar,
            self.new_tab_button,
            self.bookmark_button,
            self.download_button,
            self.incognito_button,
        ):
            stretch = 1 if widget is self.url_bar else 0
            toolbar.addWidget(widget, stretch)

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setMaximumHeight(4)
        self.progress.hide()
        root.addWidget(self.progress)

        self.download_status = QLabel("")
        self.download_status.setObjectName("caption")
        root.addWidget(self.download_status)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tabs.currentChanged.connect(self._sync_url_bar)
        root.addWidget(self.tabs, 1)

        self.forward_button.clicked.connect(self._go_forward)
        self.refresh_button.clicked.connect(self._refresh)
        self.stop_button.clicked.connect(self._stop_loading)
        self.back_button.clicked.connect(self._go_back)
        self.home_button.clicked.connect(self._go_home)
        self.new_tab_button.clicked.connect(lambda: self._create_tab("https://duckduckgo.com"))
        self.download_button.clicked.connect(self._download_from_current_url)
        self.incognito_button.clicked.connect(self._toggle_incognito)

        find_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        find_shortcut.activated.connect(self._find_in_page)

        self._build_bookmark_menu()
        self._init_profile()
        self._create_tab("https://duckduckgo.com")
        self._download_thread: QThread | None = None
        self._download_worker: DownloadWorker | None = None

    def _init_profile(self) -> None:
        if QWebEngineProfile is None:
            return
        self._profile = QWebEngineProfile.defaultProfile()
        self._profile.setPersistentStoragePath(str(self._browser_data_dir / "storage"))
        self._profile.setCachePath(str(self._browser_data_dir / "cache"))
        self._profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        self._profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies
        )
        self._profile.setHttpCacheMaximumSize(128 * 1024 * 1024)

        download_signal = getattr(self._profile, "downloadRequested", None)
        if download_signal is not None:
            download_signal.connect(self._handle_profile_download_requested)

    def _build_bookmark_menu(self) -> None:
        menu = QMenu(self)
        for url in self._bookmarks:
            action = QAction(url, self)
            action.triggered.connect(lambda checked=False, u=url: self._create_tab(u))
            menu.addAction(action)
        self.bookmark_button.setMenu(menu)

    def _toggle_incognito(self) -> None:
        self._incognito = not self._incognito
        label = "Incognito On" if self._incognito else "Incognito Off"
        self.incognito_button.setText(label)

    def _create_tab(self, url: str) -> None:
        if QWebEngineView is None:
            placeholder = QWidget()
            layout = QVBoxLayout(placeholder)
            layout.addWidget(QPushButton("Qt WebEngine is unavailable in this environment."))
            self.tabs.addTab(placeholder, "Browser Unavailable")
            self.tabs.setCurrentWidget(placeholder)
            return

        view = QWebEngineView()
        if self._incognito and QWebEngineProfile is not None and QWebEnginePage is not None:
            profile = QWebEngineProfile(self)
            profile.setOffTheRecord(True)
            download_signal = getattr(profile, "downloadRequested", None)
            if download_signal is not None:
                download_signal.connect(self._handle_profile_download_requested)
            page = QWebEnginePage(profile, view)
            view.setPage(page)

        self._configure_web_view(view)

        view.setUrl(self._normalize_url(url))
        view.urlChanged.connect(lambda qurl, v=view: self._on_url_changed(v, qurl))
        view.loadProgress.connect(self._on_progress)
        view.loadFinished.connect(lambda ok, v=view: self._on_load_finished(v, ok))
        view.titleChanged.connect(lambda title, v=view: self._on_title_changed(v, title))
        view.iconChanged.connect(lambda icon, v=view: self._on_icon_changed(v, icon))
        view.page().newWindowRequested.connect(self._handle_new_window_request)

        index = self.tabs.addTab(view, "New Tab")
        self.tabs.setCurrentIndex(index)

    def _configure_web_view(self, view) -> None:
        if QWebEngineSettings is None:
            return
        settings = view.settings()
        self._set_web_attribute(settings, "JavascriptEnabled", True)
        self._set_web_attribute(settings, "LocalStorageEnabled", True)
        self._set_web_attribute(settings, "PluginsEnabled", True)
        self._set_web_attribute(settings, "FullScreenSupportEnabled", True)
        self._set_web_attribute(settings, "AutoLoadImages", True)
        self._set_web_attribute(settings, "ScrollAnimatorEnabled", True)

    def _set_web_attribute(self, settings, attribute_name: str, enabled: bool) -> None:
        if QWebEngineSettings is None:
            return
        web_attr = getattr(QWebEngineSettings.WebAttribute, attribute_name, None)
        if web_attr is None:
            return
        try:
            settings.setAttribute(web_attr, enabled)
        except Exception:
            # Some Qt builds expose a subset of WebAttributes.
            return

    def _current_view(self):
        widget = self.tabs.currentWidget()
        if widget is None or QWebEngineView is None or not isinstance(widget, QWebEngineView):
            return None
        return widget

    def _close_tab(self, index: int) -> None:
        if self.tabs.count() <= 1:
            return
        widget = self.tabs.widget(index)
        self.tabs.removeTab(index)
        if widget is not None:
            widget.deleteLater()

    def _load_from_url_bar(self) -> None:
        view = self._current_view()
        if view is None:
            return
        self.download_status.setText("Loading...")
        view.setUrl(self._normalize_url(self.url_bar.text().strip()))

    def _go_back(self) -> None:
        view = self._current_view()
        if view is not None:
            view.back()

    def _go_forward(self) -> None:
        view = self._current_view()
        if view is not None:
            view.forward()

    def _refresh(self) -> None:
        view = self._current_view()
        if view is not None:
            view.reload()

    def _stop_loading(self) -> None:
        view = self._current_view()
        if view is not None:
            view.stop()

    def _go_home(self) -> None:
        view = self._current_view()
        if view is None:
            return
        view.setUrl(QUrl("https://duckduckgo.com"))

    def _sync_url_bar(self) -> None:
        view = self._current_view()
        if view is not None:
            self.url_bar.setText(view.url().toString())

    def _on_url_changed(self, view, qurl: QUrl) -> None:
        if self._current_view() is view:
            self.url_bar.setText(qurl.toString())

    def _on_progress(self, value: int) -> None:
        self.progress.show()
        self.progress.setValue(value)
        if value >= 100:
            self.progress.hide()
            if self.download_status.text() == "Loading...":
                self.download_status.setText("")

    def _on_load_finished(self, view, ok: bool) -> None:
        if ok:
            self.download_status.setText("")
            return
        if self._pending_download_navigation:
            self._pending_download_navigation = False
            self.download_status.setText("Download started...")
            return
        self.download_status.setText("Failed to load page")

    def _on_title_changed(self, view, title: str) -> None:
        index = self.tabs.indexOf(view)
        if index >= 0:
            self.tabs.setTabText(index, title[:24] or "New Tab")

    def _on_icon_changed(self, view, icon: QIcon) -> None:
        index = self.tabs.indexOf(view)
        if index >= 0 and not icon.isNull():
            self.tabs.setTabIcon(index, icon)

    def _handle_new_window_request(self, request) -> None:
        url = request.requestedUrl().toString()
        if not url:
            self._create_tab("https://duckduckgo.com")
            return
        self._create_tab(url)

    def _find_in_page(self) -> None:
        view = self._current_view()
        if view is None:
            return
        text, ok = QInputDialog.getText(self, "Find in Page", "Search text:")
        if ok and text:
            view.findText(text)

    def _normalize_url(self, text: str) -> QUrl:
        if not text:
            return QUrl("https://duckduckgo.com")

        # Keep explicit schemes untouched (http, https, file, etc.).
        parsed = urlparse(text)
        if parsed.scheme:
            return QUrl(text)

        if " " in text and "." not in text:
            return QUrl(f"https://duckduckgo.com/?q={text.replace(' ', '+')}")

        # Local and development hosts usually run on plain HTTP.
        lowered = text.lower()
        if lowered.startswith("localhost") or lowered.startswith("127.") or lowered.startswith("192.168."):
            text = f"http://{text}"
        elif ":" in text and "/" not in text:
            text = f"http://{text}"
        else:
            text = f"https://{text}"
        return QUrl(text)

    def _download_from_current_url(self) -> None:
        if self._download_thread is not None:
            QMessageBox.information(self, "Download", "A download is already in progress.")
            return

        initial_url = self.url_bar.text().strip() or "https://"
        url, ok = QInputDialog.getText(self, "Download File", "File URL:", text=initial_url)
        if not ok or not url.strip():
            return

        normalized = self._normalize_url(url.strip()).toString()
        default_name = self._suggest_filename(normalized)
        downloads_dir = blendios_downloads_dir()

        target, _ = QFileDialog.getSaveFileName(
            self,
            "Save Download",
            str(downloads_dir / default_name),
            "All Files (*.*)",
        )
        if not target:
            return

        self.download_status.setText(f"Downloading to: {target}")
        self.progress.show()
        self.progress.setValue(0)

        self._download_thread = QThread(self)
        self._download_worker = DownloadWorker(normalized, target)
        self._download_worker.moveToThread(self._download_thread)

        self._download_thread.started.connect(self._download_worker.run)
        self._download_worker.progress.connect(self.progress.setValue)
        self._download_worker.finished.connect(self._on_download_finished)
        self._download_worker.failed.connect(self._on_download_failed)
        self._download_worker.finished.connect(self._cleanup_download_thread)
        self._download_worker.failed.connect(self._cleanup_download_thread)
        self._download_thread.start()

    def _suggest_filename(self, url: str) -> str:
        parsed = urlparse(url)
        candidate = Path(parsed.path).name.strip()
        if candidate:
            return candidate
        return "download.bin"

    def _on_download_finished(self, destination: str) -> None:
        self.progress.hide()
        self.download_status.setText(f"Downloaded: {destination}")
        QMessageBox.information(self, "Download Complete", f"Saved to:\n{destination}")

    def _on_download_failed(self, error: str) -> None:
        self.progress.hide()
        self.download_status.setText("Download failed")
        QMessageBox.warning(self, "Download Failed", error)

    def _cleanup_download_thread(self) -> None:
        if self._download_thread is not None:
            self._download_thread.quit()
            self._download_thread.wait(1500)
            self._download_thread = None
        self._download_worker = None

    def _handle_profile_download_requested(self, request) -> None:
        self._pending_download_navigation = True
        downloads_dir = blendios_downloads_dir()

        default_name = self._download_request_name(request)
        destination, _ = QFileDialog.getSaveFileName(
            self,
            "Save Download",
            str(downloads_dir / default_name),
            "All Files (*.*)",
        )

        if not destination:
            cancel = getattr(request, "cancel", None)
            if callable(cancel):
                cancel()
            return

        target = Path(destination)
        set_dir = getattr(request, "setDownloadDirectory", None)
        set_name = getattr(request, "setDownloadFileName", None)
        set_path = getattr(request, "setPath", None)

        if callable(set_dir) and callable(set_name):
            set_dir(str(target.parent))
            set_name(target.name)
        elif callable(set_path):
            set_path(str(target))

        accept = getattr(request, "accept", None)
        if callable(accept):
            accept()

        self._active_downloads.append(request)
        self.download_status.setText(f"Downloading: {target.name}")

        state_changed = getattr(request, "stateChanged", None)
        if state_changed is not None:
            state_changed.connect(lambda: self._on_profile_download_state_changed(request, target))

        finished = getattr(request, "finished", None)
        if finished is not None:
            finished.connect(lambda: self._on_profile_download_finished(request, target))

    def _download_request_name(self, request) -> str:
        get_name = getattr(request, "downloadFileName", None)
        if callable(get_name):
            name = get_name()
            if name:
                return name
        get_suggested = getattr(request, "suggestedFileName", None)
        if callable(get_suggested):
            name = get_suggested()
            if name:
                return name
        return "download.bin"

    def _on_profile_download_state_changed(self, request, target: Path) -> None:
        state_method = getattr(request, "state", None)
        if not callable(state_method):
            return
        state = state_method()
        state_name = getattr(state, "name", str(state)).lower()
        if "completed" in state_name:
            self.download_status.setText(f"Downloaded: {target.name}")
        elif "interrupted" in state_name or "cancelled" in state_name:
            reason_method = getattr(request, "interruptReasonString", None)
            reason = reason_method() if callable(reason_method) else "Download interrupted"
            self.download_status.setText(reason or "Download interrupted")

    def _on_profile_download_finished(self, request, target: Path) -> None:
        if request in self._active_downloads:
            self._active_downloads.remove(request)
        if target.exists():
            self.download_status.setText(f"Downloaded: {target}")
        elif not self.download_status.text():
            self.download_status.setText("Download finished")


class BrowserApp(BaseApp):
    """Browser application."""

    app_id = "browser"
    name = "Browser"
    version = "0.1.0"
    icon = "icons/browser.png"
    category = "internet"

    def build_ui(self) -> QWidget:
        return BrowserWidget()

    def on_launch(self) -> None:
        pass
