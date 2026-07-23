"""File Explorer app for BlendiOS."""

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
import time
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from PySide6.QtCore import QDir, QPoint, Qt
from PySide6.QtGui import QAction, QWindow
from PySide6.QtWidgets import (
    QFileDialog,
    QFileSystemModel,
    QHBoxLayout,
    QInputDialog,
    QLineEdit,
    QListWidget,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from blendios.apps.base_app import BaseApp
from blendios.common.paths import blendios_downloads_dir
from blendios.constants import DEFAULT_DATA_DIR
from blendios.window_manager.window_manager import WindowManager


class FileExplorerWidget(QWidget):
    """Dual-pane file explorer with context actions."""

    def __init__(self) -> None:
        super().__init__()
        self._quick_access_paths = {
            "BlendiOS Downloads": blendios_downloads_dir(),
            "Desktop": Path.home() / "Desktop",
            "Documents": Path.home() / "Documents",
            "Downloads": Path.home() / "Downloads",
            "Pictures": Path.home() / "Pictures",
            "Music": Path.home() / "Music",
            "Videos": Path.home() / "Videos",
        }
        self._current_path = str(blendios_downloads_dir())

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        top = QHBoxLayout()
        root.addLayout(top)

        self.back_button = QPushButton("Back")
        self.up_button = QPushButton("Up")
        self.home_button = QPushButton("Home")
        self.path_bar = QLineEdit(self._current_path)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search in current folder")

        for widget in (
            self.back_button,
            self.up_button,
            self.home_button,
            self.path_bar,
            self.search_bar,
        ):
            stretch = 1 if widget is self.path_bar else 0
            top.addWidget(widget, stretch)

        self.splitter = QSplitter()
        root.addWidget(self.splitter, 1)

        self.quick_access = QListWidget()
        self.quick_access.addItems(list(self._quick_access_paths.keys()))
        self.quick_access.itemClicked.connect(self._jump_quick_access)
        self.splitter.addWidget(self.quick_access)

        self.model = QFileSystemModel(self)
        self.model.setRootPath(self._current_path)
        self.model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot | QDir.AllDirs)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self._current_path))
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        self.tree.doubleClicked.connect(self._open_selected)
        self.splitter.addWidget(self.tree)

        self.splitter.setStretchFactor(1, 1)

        self.back_button.clicked.connect(self._go_back)
        self.up_button.clicked.connect(self._go_up)
        self.home_button.clicked.connect(self._go_home)
        self.path_bar.returnPressed.connect(self._set_path_from_bar)
        self.search_bar.textChanged.connect(self._apply_search_filter)

        self._history: list[str] = [self._current_path]
        self._embedded_windows: list[tuple[QWidget, subprocess.Popen]] = []

    def _jump_quick_access(self, item) -> None:
        target = self._quick_access_paths.get(item.text())
        if target is None:
            return
        if target.exists():
            self._set_path(str(target))

    def _set_path_from_bar(self) -> None:
        self._set_path(self.path_bar.text().strip())

    def _set_path(self, path: str) -> None:
        target = Path(path).expanduser()
        if not target.exists() or not target.is_dir():
            QMessageBox.warning(self, "Invalid Path", f"Path does not exist:\n{path}")
            return
        self._current_path = str(target)
        self.path_bar.setText(self._current_path)
        self.tree.setRootIndex(self.model.index(self._current_path))
        if not self._history or self._history[-1] != self._current_path:
            self._history.append(self._current_path)

    def _go_back(self) -> None:
        if len(self._history) < 2:
            return
        self._history.pop()
        self._set_path(self._history[-1])

    def _go_up(self) -> None:
        parent = Path(self._current_path).parent
        self._set_path(str(parent))

    def _go_home(self) -> None:
        self._set_path(str(blendios_downloads_dir()))

    def _open_selected(self, index) -> None:
        path = self.model.filePath(index)
        selected = Path(path)
        if selected.is_dir():
            self._set_path(path)
            return
        self._open_with_host_os(path)

    def _show_context_menu(self, point: QPoint) -> None:
        index = self.tree.indexAt(point)
        path = self.model.filePath(index) if index.isValid() else self._current_path
        selected = Path(path)

        menu = QMenu(self)
        open_action = QAction("Open", self)
        rename_action = QAction("Rename", self)
        delete_action = QAction("Delete", self)
        new_folder_action = QAction("New Folder", self)
        extract_zip_action = QAction("Extract ZIP Here", self)

        open_action.triggered.connect(lambda: self._open_index(index))
        rename_action.triggered.connect(lambda: self._rename_path(path))
        delete_action.triggered.connect(lambda: self._delete_path(path))
        new_folder_action.triggered.connect(self._create_folder)
        extract_zip_action.triggered.connect(lambda: self._extract_zip_here(path))

        menu.addAction(open_action)
        menu.addAction(rename_action)
        menu.addAction(delete_action)
        menu.addSeparator()
        if selected.is_file() and selected.suffix.lower() == ".zip":
            menu.addAction(extract_zip_action)
        menu.addAction(new_folder_action)
        menu.exec(self.tree.viewport().mapToGlobal(point))

    def _open_index(self, index) -> None:
        if not index.isValid():
            return
        self._open_selected(index)

    def _open_with_host_os(self, path: str) -> None:
        target = Path(path)
        if not target.exists():
            QMessageBox.warning(self, "Open Failed", f"Path does not exist:\n{path}")
            return

        if self._is_probable_installer(target):
            choice = QMessageBox.warning(
                self,
                "Installer Warning",
                "This is an installer package. Running it installs on your main Windows system, not inside BlendiOS.\n\n"
                "Use a portable ZIP build if you want app files to stay in BlendiOS storage.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if choice != QMessageBox.StandardButton.Yes:
                return

        if self._is_vscode_executable(target):
            vscode_args = self._vscode_portable_args()
            if sys.platform.startswith("win") and self._launch_embedded_windows_executable(
                target,
                extra_args=vscode_args,
            ):
                return
            if self._launch_vscode_portable(target):
                return

        if sys.platform.startswith("win") and target.suffix.lower() == ".exe":
            if self._launch_embedded_windows_executable(target):
                return

        try:
            if sys.platform.startswith("win"):
                os.startfile(str(target))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(target)])
            else:
                subprocess.Popen(["xdg-open", str(target)])
        except Exception as exc:
            QMessageBox.warning(self, "Open Failed", str(exc))

    def _is_probable_installer(self, target: Path) -> bool:
        installer_suffixes = {".msi", ".msix", ".msixbundle"}
        if target.suffix.lower() in installer_suffixes:
            return True
        name = target.name.lower()
        return name.endswith(".exe") and any(token in name for token in ("setup", "installer", "install"))

    def _is_vscode_executable(self, target: Path) -> bool:
        return target.name.lower() in {"code.exe", "code-insiders.exe"}

    def _launch_vscode_portable(self, target: Path) -> bool:
        try:
            subprocess.Popen([str(target), *self._vscode_portable_args()], cwd=str(target.parent))
            QMessageBox.information(
                self,
                "VS Code Portable",
                "VS Code launched with BlendiOS-local profile and extensions directories.",
            )
            return True
        except Exception as exc:
            QMessageBox.warning(self, "VS Code Launch Failed", str(exc))
            return False

    def _vscode_portable_args(self) -> list[str]:
        profile_root = DEFAULT_DATA_DIR / "apps" / "vscode"
        user_data_dir = profile_root / "user-data"
        extensions_dir = profile_root / "extensions"
        user_data_dir.mkdir(parents=True, exist_ok=True)
        extensions_dir.mkdir(parents=True, exist_ok=True)
        return [
            "--new-window",
            "--user-data-dir",
            str(user_data_dir),
            "--extensions-dir",
            str(extensions_dir),
        ]

    def _launch_embedded_windows_executable(self, target: Path, extra_args: list[str] | None = None) -> bool:
        try:
            command = [str(target)]
            if extra_args:
                command.extend(extra_args)
            process = subprocess.Popen(command, cwd=str(target.parent))
        except Exception:
            return False

        hwnd = self._wait_for_main_window(process.pid, target.name.lower(), timeout_seconds=10.0)
        if hwnd is None:
            return False

        foreign_window = QWindow.fromWinId(hwnd)
        if foreign_window is None:
            return False

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        container = QWidget.createWindowContainer(foreign_window, content)
        container.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        layout.addWidget(container, 1)

        shell = self._desktop_shell()
        app_id = f"external::{target.stem.lower()}"
        if shell is not None and hasattr(shell, "taskbar"):
            shell.taskbar.register_app(app_id, target.stem)

        parent = shell if shell is not None else self.window()
        managed_window = WindowManager().create_window(
            title=target.stem,
            content=content,
            parent=parent,
            app_id=app_id,
        )
        managed_window.resize(1200, 800)
        self._force_embed_window(hwnd, int(container.winId()))
        managed_window.closed.connect(
            lambda _window_id, p=process, w=managed_window, a=app_id: self._on_embedded_window_closed(p, w, a)
        )
        if shell is not None and hasattr(shell, "taskbar"):
            shell.taskbar.set_running(app_id, True)

        self._embedded_windows.append((managed_window, process))
        return True

    def _desktop_shell(self) -> QWidget | None:
        host_window = self.window()
        parent = host_window.parentWidget() if host_window is not None else None
        return parent

    def _on_embedded_window_closed(self, process: subprocess.Popen, window: QWidget, app_id: str) -> None:
        self._embedded_windows = [entry for entry in self._embedded_windows if entry[0] is not window]
        shell = self._desktop_shell()
        if shell is not None and hasattr(shell, "taskbar"):
            shell.taskbar.set_running(app_id, False)
        if process.poll() is None:
            try:
                process.terminate()
            except Exception:
                return

    def _force_embed_window(self, hwnd: int, parent_hwnd: int) -> None:
        if not sys.platform.startswith("win"):
            return
        try:
            user32 = ctypes.windll.user32
            GWL_STYLE = -16
            WS_CHILD = 0x40000000
            WS_POPUP = 0x80000000
            style = user32.GetWindowLongW(hwnd, GWL_STYLE)
            style = (style | WS_CHILD) & ~WS_POPUP
            user32.SetWindowLongW(hwnd, GWL_STYLE, style)
            user32.SetParent(hwnd, parent_hwnd)
        except Exception:
            return

    def _wait_for_main_window(
        self,
        pid: int,
        executable_name: str | None,
        timeout_seconds: float = 8.0,
    ) -> int | None:
        if not sys.platform.startswith("win"):
            return None

        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            hwnd = self._find_main_window_for_process(pid, executable_name)
            if hwnd is not None:
                return hwnd
            time.sleep(0.15)
        return None

    def _find_main_window_for_process(self, pid: int, executable_name: str | None) -> int | None:
        if not sys.platform.startswith("win"):
            return None

        user32 = ctypes.windll.user32
        found: list[int] = []
        GW_OWNER = 4

        enum_proc_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def callback(hwnd, _lparam):
            window_pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
            current_pid = int(window_pid.value)
            if current_pid != pid:
                if executable_name is None:
                    return True
                process_name = self._get_process_name(current_pid)
                if process_name != executable_name:
                    return True
            if not user32.IsWindowVisible(hwnd):
                return True
            if user32.GetWindow(hwnd, GW_OWNER):
                return True
            found.append(int(hwnd))
            return False

        user32.EnumWindows(enum_proc_type(callback), 0)
        return found[0] if found else None

    def _get_process_name(self, pid: int) -> str | None:
        if not sys.platform.startswith("win"):
            return None
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return None
        try:
            buffer_size = ctypes.c_ulong(260)
            buffer = ctypes.create_unicode_buffer(260)
            ok = ctypes.windll.kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(buffer_size))
            if not ok:
                return None
            return Path(buffer.value).name.lower()
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)

    def _rename_path(self, path: str) -> None:
        source = Path(path)
        if not source.exists():
            return
        new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=source.name)
        if not ok or not new_name.strip():
            return
        target = source.parent / new_name.strip()
        try:
            source.rename(target)
            self.model.refresh()
        except OSError as exc:
            QMessageBox.warning(self, "Rename Failed", str(exc))

    def _delete_path(self, path: str) -> None:
        source = Path(path)
        if not source.exists():
            return
        if QMessageBox.question(self, "Delete", f"Delete {source.name}?") != QMessageBox.StandardButton.Yes:
            return
        try:
            if source.is_dir():
                source.rmdir()
            else:
                source.unlink()
            self.model.refresh()
        except OSError as exc:
            QMessageBox.warning(self, "Delete Failed", str(exc))

    def _create_folder(self) -> None:
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if not ok or not name.strip():
            return
        target = Path(self._current_path) / name.strip()
        try:
            target.mkdir(parents=False, exist_ok=False)
            self.model.refresh()
        except OSError as exc:
            QMessageBox.warning(self, "Create Folder Failed", str(exc))

    def _extract_zip_here(self, path: str) -> None:
        source = Path(path)
        if not source.exists() or source.suffix.lower() != ".zip":
            QMessageBox.warning(self, "Extract ZIP", "Select a valid .zip file.")
            return

        destination = source.parent / source.stem
        destination.mkdir(parents=True, exist_ok=True)
        try:
            with ZipFile(source, "r") as archive:
                archive.extractall(destination)
            self.model.refresh()
            QMessageBox.information(
                self,
                "Extract ZIP",
                f"Archive extracted to:\n{destination}",
            )
        except (BadZipFile, OSError) as exc:
            QMessageBox.warning(self, "Extract ZIP Failed", str(exc))

    def _apply_search_filter(self, query: str) -> None:
        q = query.strip().lower()
        for row in range(self.model.rowCount(self.model.index(self._current_path))):
            idx = self.model.index(row, 0, self.model.index(self._current_path))
            if not idx.isValid():
                continue
            name = self.model.fileName(idx).lower()
            hidden = bool(q) and q not in name
            self.tree.setRowHidden(row, self.model.index(self._current_path), hidden)


class FileExplorerApp(BaseApp):
    """File Explorer application."""

    app_id = "file_explorer"
    name = "File Explorer"
    version = "0.1.0"
    icon = "icons/file_explorer.png"
    category = "system"

    def build_ui(self) -> QWidget:
        return FileExplorerWidget()

    def on_launch(self) -> None:
        pass
