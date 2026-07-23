"""Main desktop shell for BlendiOS."""

from __future__ import annotations

import logging
from datetime import datetime

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QRect, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QCloseEvent, QColor, QLinearGradient, QPainter, QPixmap, QRadialGradient
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGraphicsBlurEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSlider,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from blendios.apps.app_registry import AppRegistry
from blendios.desktop.icon_provider import get_app_icon
from blendios.desktop.notifications import NotificationManager
from blendios.desktop.settings_store import DesktopSettings, SettingsStore
from blendios.desktop.start_menu import StartMenu
from blendios.desktop.taskbar import Taskbar
from blendios.desktop.wallpaper_manager import WallpaperManager
from blendios.kernel.kernel import Kernel
from blendios.themes.theme_engine import ThemeEngine
from blendios.window_manager.window_manager import WindowManager

logger = logging.getLogger(__name__)


class DesktopWallpaper(QWidget):
    """Dynamic desktop wallpaper renderer with cached pixmaps."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._brush = "qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #121620, stop:1 #05070d)"
        self._image_path: str | None = None
        self._image_cache = QPixmap()
        self._parallax = QPoint(0, 0)
        self._apply_wallpaper()

    def set_wallpaper_brush(self, brush: str) -> None:
        self._brush = brush
        self._apply_wallpaper()

    def _apply_wallpaper(self) -> None:
        if self._brush.startswith("image:"):
            self._image_path = self._brush.removeprefix("image:")
            self._image_cache = QPixmap(self._image_path)
            self.setStyleSheet("background-color: #0f1218;")
            self.update()
            return

        self._image_path = None
        self._image_cache = QPixmap()
        self.setStyleSheet(f"background: {self._brush};")

    def set_parallax_offset(self, x_offset: int, y_offset: int) -> None:
        """Apply subtle wallpaper parallax offset."""
        self._parallax = QPoint(x_offset, y_offset)
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if not self._image_cache.isNull():
            scaled = self._image_cache.scaled(
                self.size() + QSize(40, 40),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (self.width() - scaled.width()) // 2 + self._parallax.x()
            y = (self.height() - scaled.height()) // 2 + self._parallax.y()
            painter.drawPixmap(x, y, scaled)

        # Premium atmosphere overlay to avoid flat wallpaper appearance.
        top_overlay = QLinearGradient(0, 0, 0, self.height())
        top_overlay.setColorAt(0.0, QColor(8, 12, 20, 120))
        top_overlay.setColorAt(0.45, QColor(8, 12, 20, 30))
        top_overlay.setColorAt(1.0, QColor(8, 12, 20, 150))
        painter.fillRect(self.rect(), top_overlay)

        radial = QRadialGradient(self.width() * 0.75, self.height() * 0.2, self.width() * 0.65)
        radial.setColorAt(0.0, QColor(102, 176, 255, 34))
        radial.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), radial)


class DesktopShortcutGrid(QListWidget):
    """Desktop app shortcuts with drag/snap/rename behavior."""

    launch_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("desktopShortcuts")
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setFlow(QListWidget.Flow.TopToBottom)
        self.setMovement(QListWidget.Movement.Snap)
        self.setWrapping(True)
        self.setSpacing(10)
        self.setIconSize(QSize(48, 48))
        self.setGridSize(QSize(132, 92))
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.setEditTriggers(QListWidget.EditTrigger.EditKeyPressed)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.itemDoubleClicked.connect(self._on_item_activated)
        self.itemActivated.connect(self._on_item_activated)
        self.setStyleSheet(
            "QListWidget { background: transparent; border: none; padding: 12px; }"
            "QListWidget::item { color: #f2f6ff; padding: 6px; border-radius: 10px; }"
            "QListWidget::item:selected { background: rgba(58, 134, 255, 0.30); }"
        )

    def set_apps(self, apps: list[dict]) -> None:
        self.clear()
        for app in sorted(apps, key=lambda item: item["name"].lower()):
            item = QListWidgetItem(app["name"])
            item.setIcon(get_app_icon(self.style(), app["app_id"]))
            item.setData(Qt.ItemDataRole.UserRole, app["app_id"])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled)
            self.addItem(item)

    def _on_item_activated(self, item: QListWidgetItem) -> None:
        app_id = item.data(Qt.ItemDataRole.UserRole)
        if app_id:
            self.launch_requested.emit(app_id)

    def _show_context_menu(self, pos: QPoint) -> None:
        item = self.itemAt(pos)
        if item is None:
            return

        menu = QMenu(self)
        open_action = QAction("Open", self)
        rename_action = QAction("Rename", self)

        open_action.triggered.connect(lambda: self._on_item_activated(item))
        rename_action.triggered.connect(lambda: self.editItem(item))

        menu.addAction(open_action)
        menu.addAction(rename_action)
        menu.exec(self.viewport().mapToGlobal(pos))

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        if event.key() == Qt.Key.Key_F2:
            item = self.currentItem()
            if item is not None:
                self.editItem(item)
                return
        super().keyPressEvent(event)


class QuickSettingsPanel(QFrame):
    """Slide-out quick settings panel."""

    open_settings_requested = Signal()
    lock_requested = Signal()
    wifi_toggled = Signal(bool)
    bluetooth_toggled = Signal(bool)
    night_mode_toggled = Signal(bool)
    brightness_changed = Signal(int)
    volume_changed = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("quickPanel")
        self.setFixedWidth(330)
        self.hide()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("Quick Settings")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(title)

        self.wifi_button = QPushButton("Wi-Fi")
        self.wifi_button.setCheckable(True)
        self.bluetooth_button = QPushButton("Bluetooth")
        self.bluetooth_button.setCheckable(True)
        self.night_mode_button = QPushButton("Night Mode")
        self.night_mode_button.setCheckable(True)

        layout.addWidget(self.wifi_button)
        layout.addWidget(self.bluetooth_button)
        layout.addWidget(self.night_mode_button)

        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)

        layout.addWidget(QLabel("Brightness"))
        layout.addWidget(self.brightness_slider)
        layout.addWidget(QLabel("Volume"))
        layout.addWidget(self.volume_slider)

        self.screenshot_button = QPushButton("Capture")
        self.settings_button = QPushButton("Settings")
        self.lock_button = QPushButton("Lock")
        layout.addWidget(self.screenshot_button)
        layout.addWidget(self.settings_button)
        layout.addWidget(self.lock_button)
        layout.addStretch(1)

        self.wifi_button.toggled.connect(self.wifi_toggled.emit)
        self.bluetooth_button.toggled.connect(self.bluetooth_toggled.emit)
        self.night_mode_button.toggled.connect(self.night_mode_toggled.emit)
        self.brightness_slider.valueChanged.connect(self.brightness_changed.emit)
        self.volume_slider.valueChanged.connect(self.volume_changed.emit)
        self.settings_button.clicked.connect(self.open_settings_requested.emit)
        self.lock_button.clicked.connect(self.lock_requested.emit)
        self.screenshot_button.clicked.connect(self._screenshot_placeholder)

    def apply_settings(self, settings: DesktopSettings) -> None:
        self.wifi_button.setChecked(settings.wifi_enabled)
        self.bluetooth_button.setChecked(settings.bluetooth_enabled)
        self.night_mode_button.setChecked(settings.night_mode_enabled)
        self.brightness_slider.setValue(settings.brightness)
        self.volume_slider.setValue(settings.volume)

    def toggle(self, host_rect: QRect) -> None:
        if self.isVisible():
            self.hide_animated(host_rect)
        else:
            self.show_animated(host_rect)

    def show_animated(self, host_rect: QRect) -> None:
        self.setGeometry(host_rect.width(), 72, self.width(), host_rect.height() - 144)
        self.show()
        self.raise_()

        target = QRect(host_rect.width() - self.width() - 12, 72, self.width(), host_rect.height() - 144)
        animation = QPropertyAnimation(self, b"geometry", self)
        animation.setDuration(220)
        animation.setStartValue(self.geometry())
        animation.setEndValue(target)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()

    def hide_animated(self, host_rect: QRect) -> None:
        end_rect = QRect(host_rect.width() + 8, 72, self.width(), host_rect.height() - 144)
        animation = QPropertyAnimation(self, b"geometry", self)
        animation.setDuration(200)
        animation.setStartValue(self.geometry())
        animation.setEndValue(end_rect)
        animation.setEasingCurve(QEasingCurve.Type.InCubic)
        animation.finished.connect(self.hide)
        animation.start()

    def _screenshot_placeholder(self) -> None:
        QMessageBox.information(self, "Screenshot", "Screenshot tool is queued for next implementation pass.")


class LockScreenOverlay(QFrame):
    """Lock screen with blur effect and password unlock."""

    unlock_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("lockOverlay")
        self.setStyleSheet("background: rgba(8, 12, 20, 0.72);")
        self.hide()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addStretch(1)

        self.clock = QLabel()
        self.clock.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clock.setStyleSheet("font-size: 56px; font-weight: 600; color: #f5f8ff;")
        layout.addWidget(self.clock)

        self.date = QLabel()
        self.date.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date.setStyleSheet("font-size: 16px; color: #d2ddf0;")
        layout.addWidget(self.date)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setFixedWidth(280)
        self.password.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.password.returnPressed.connect(self._emit_unlock)
        layout.addWidget(self.password, alignment=Qt.AlignmentFlag.AlignCenter)

        self.unlock_button = QPushButton("Unlock")
        self.unlock_button.setFixedWidth(200)
        self.unlock_button.clicked.connect(self._emit_unlock)
        layout.addWidget(self.unlock_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.message = QLabel("")
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message.setStyleSheet("color: #ffb4b4;")
        layout.addWidget(self.message)

        layout.addStretch(2)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_time)

    def show_lock(self, host_rect: QRect) -> None:
        self.setGeometry(host_rect)
        self.password.clear()
        self.message.clear()
        self._update_time()
        self._timer.start(1000)
        self.show()
        self.raise_()

    def hide_lock(self) -> None:
        self._timer.stop()
        self.hide()

    def _update_time(self) -> None:
        now = datetime.now()
        self.clock.setText(now.strftime("%H:%M"))
        self.date.setText(now.strftime("%A, %B %d, %Y"))

    def _emit_unlock(self) -> None:
        self.unlock_requested.emit(self.password.text())


class DesktopCanvas(QWidget):
    """Main desktop surface with wallpaper and shortcut layers."""

    desktop_context_requested = Signal(QPoint)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMouseTracking(True)
        self.layout = QStackedLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setStackingMode(QStackedLayout.StackingMode.StackAll)

        self.wallpaper = DesktopWallpaper(self)
        self.shortcuts = DesktopShortcutGrid(self)
        self.layout.addWidget(self.wallpaper)
        self.layout.addWidget(self.shortcuts)
        self.layout.setCurrentWidget(self.shortcuts)

    def contextMenuEvent(self, event) -> None:  # type: ignore[override]
        self.desktop_context_requested.emit(event.globalPos())
        event.accept()

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        # Subtle parallax creates depth while keeping UI legible.
        center_x = self.width() / 2 if self.width() else 1
        center_y = self.height() / 2 if self.height() else 1
        dx = (event.position().x() - center_x) / center_x
        dy = (event.position().y() - center_y) / center_y
        self.wallpaper.set_parallax_offset(int(dx * 10), int(dy * 8))
        super().mouseMoveEvent(event)


class DesktopShell(QMainWindow):
    """Main BlendiOS desktop window."""

    def __init__(self, kernel: Kernel | None = None) -> None:
        super().__init__()
        self.kernel = kernel or Kernel()
        self.window_manager = WindowManager()
        self.app_registry = AppRegistry()
        self.settings_store = SettingsStore()
        self.settings = self.settings_store.load()
        self.theme_engine = ThemeEngine()
        self.wallpaper_manager = WallpaperManager()

        self.setWindowTitle("BlendiOS")
        self.showFullScreen()

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.canvas = DesktopCanvas(self)
        self.layout.addWidget(self.canvas, 1)

        self.taskbar = Taskbar(self)
        self.layout.addWidget(self.taskbar)

        self.start_menu = StartMenu(self)
        self.notification_manager = NotificationManager(self)
        self.quick_panel = QuickSettingsPanel(self)
        self.lock_overlay = LockScreenOverlay(self)

        self._canvas_blur = QGraphicsBlurEffect(self.canvas)
        self._settings_signature = ""
        self._settings_watch_timer = QTimer(self)

        self._configure_theme()
        self._configure_wallpaper()
        self._wire_signals()
        self._register_apps()
        self._start_settings_watch()

        self.window_manager.set_callbacks(
            on_focus=self._on_window_focus,
            on_close=self._on_window_closed,
        )

        self.quick_panel.apply_settings(self.settings)
        self._apply_taskbar_position(self.settings.taskbar_position)

        self.notification_manager.push(
            app_id="system",
            title="Welcome to BlendiOS",
            message="Desktop shell initialized successfully.",
        )
        logger.info("Desktop shell initialized")

    def _wire_signals(self) -> None:
        self.canvas.desktop_context_requested.connect(self._show_desktop_context)
        self.canvas.shortcuts.launch_requested.connect(self._launch_app)

        self.taskbar.start_requested.connect(self._toggle_start_menu)
        self.taskbar.notifications_requested.connect(self.notification_manager.toggle_center)
        self.taskbar.quick_settings_requested.connect(self._show_quick_settings)
        self.taskbar.app_requested.connect(self._launch_app)

        self.start_menu.launch_requested.connect(self._launch_app)
        self.start_menu.shutdown_requested.connect(self.shutdown)
        self.start_menu.restart_requested.connect(self._restart_session)
        self.start_menu.lock_requested.connect(self._lock_screen)

        self.quick_panel.open_settings_requested.connect(lambda: self._launch_app("settings"))
        self.quick_panel.lock_requested.connect(self._lock_screen)
        self.quick_panel.wifi_toggled.connect(lambda value: self._update_setting("wifi_enabled", value))
        self.quick_panel.bluetooth_toggled.connect(
            lambda value: self._update_setting("bluetooth_enabled", value)
        )
        self.quick_panel.night_mode_toggled.connect(
            lambda value: self._update_setting("night_mode_enabled", value)
        )
        self.quick_panel.brightness_changed.connect(lambda value: self._update_setting("brightness", value))
        self.quick_panel.volume_changed.connect(lambda value: self._update_setting("volume", value))

        self.lock_overlay.unlock_requested.connect(self._handle_unlock_attempt)

    def _configure_theme(self) -> None:
        self.theme_engine.set_theme(self.settings.theme)
        app = QApplication.instance()
        if app:
            self.theme_engine.apply_to_application(app)

    def _configure_wallpaper(self) -> None:
        self.wallpaper_manager.wallpaper_changed.connect(self.canvas.wallpaper.set_wallpaper_brush)
        self.wallpaper_manager.set_category(self.settings.wallpaper_category)
        self.canvas.wallpaper.set_wallpaper_brush(self.wallpaper_manager.current_wallpaper())
        if self.settings.wallpaper_slideshow:
            self.wallpaper_manager.start_slideshow(self.settings.wallpaper_interval_sec)

    def _register_apps(self) -> None:
        apps = self.app_registry.list_apps()
        self.start_menu.set_apps(apps)
        self.canvas.shortcuts.set_apps(apps)
        for app in apps:
            self.taskbar.register_app(app["app_id"], app["name"])

    def _start_settings_watch(self) -> None:
        self._settings_signature = self._signature(self.settings)
        self._settings_watch_timer.timeout.connect(self._watch_settings)
        self._settings_watch_timer.start(1000)

    def _watch_settings(self) -> None:
        current = self.settings_store.load()
        signature = self._signature(current)
        if signature == self._settings_signature:
            return

        self.settings = current
        self._settings_signature = signature
        self._apply_runtime_settings(current)

    def _apply_runtime_settings(self, settings: DesktopSettings) -> None:
        self._set_theme(settings.theme, notify=False)
        self._apply_taskbar_position(settings.taskbar_position)

        self.wallpaper_manager.set_category(settings.wallpaper_category)
        if settings.wallpaper_slideshow:
            self.wallpaper_manager.start_slideshow(settings.wallpaper_interval_sec)
        else:
            self.wallpaper_manager.stop_slideshow()

        self.quick_panel.apply_settings(settings)

    def _signature(self, settings: DesktopSettings) -> str:
        return "|".join(
            [
                settings.theme,
                settings.taskbar_position,
                settings.animation_speed,
                settings.wallpaper_category,
                str(settings.wallpaper_slideshow),
                str(settings.wallpaper_interval_sec),
                str(settings.notifications_enabled),
                str(settings.wifi_enabled),
                str(settings.bluetooth_enabled),
                str(settings.night_mode_enabled),
                str(settings.brightness),
                str(settings.volume),
                settings.lock_password,
            ]
        )

    def _apply_taskbar_position(self, position: str) -> None:
        target = position if position in {"top", "bottom"} else "bottom"
        self.layout.removeWidget(self.taskbar)
        if target == "top":
            self.layout.insertWidget(0, self.taskbar)
        else:
            self.layout.addWidget(self.taskbar)

    def _toggle_start_menu(self) -> None:
        if self.start_menu.isVisible():
            self.start_menu.hide()
            return

        taskbar_top_left = self.taskbar.mapToGlobal(self.taskbar.rect().topLeft())
        if self.layout.indexOf(self.taskbar) == 0:
            pos = QPoint(taskbar_top_left.x() + 12, taskbar_top_left.y() + self.taskbar.height() + 8)
        else:
            pos = QPoint(
                taskbar_top_left.x() + 12,
                taskbar_top_left.y() - self.start_menu.height() - 8,
            )
        self.start_menu.show_animated(pos)

    def _show_desktop_context(self, global_pos: QPoint) -> None:
        menu = QMenu(self)

        next_wallpaper_action = QAction("Next Wallpaper", self)
        next_wallpaper_action.triggered.connect(self.wallpaper_manager.next_wallpaper)
        menu.addAction(next_wallpaper_action)

        wallpaper_menu = menu.addMenu("Wallpaper Category")
        for category in self.wallpaper_manager.categories():
            action = QAction(category, self)
            action.triggered.connect(
                lambda checked=False, c=category: self._set_wallpaper_category(c)
            )
            wallpaper_menu.addAction(action)

        image_wallpaper_action = QAction("Use Image Wallpaper...", self)
        image_wallpaper_action.triggered.connect(self._select_image_wallpaper)
        menu.addAction(image_wallpaper_action)

        menu.addSeparator()
        toggle_slideshow_action = QAction("Toggle Slideshow", self)
        toggle_slideshow_action.triggered.connect(self._toggle_wallpaper_slideshow)
        menu.addAction(toggle_slideshow_action)

        menu.exec(global_pos)

    def _select_image_wallpaper(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Wallpaper",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)",
        )
        if not file_path:
            return

        if not self.wallpaper_manager.add_custom_image(file_path):
            QMessageBox.warning(self, "Wallpaper", "Selected image could not be loaded.")
            return

        self._update_setting("wallpaper_category", "Custom")
        self.notification_manager.push("system", "Wallpaper", "Custom image wallpaper applied.")

    def _set_wallpaper_category(self, category: str) -> None:
        self.wallpaper_manager.set_category(category)
        self._update_setting("wallpaper_category", category)
        self.notification_manager.push("system", "Wallpaper", f"Category switched to {category}.")

    def _toggle_wallpaper_slideshow(self) -> None:
        enabled = not self.settings.wallpaper_slideshow
        if enabled:
            self.wallpaper_manager.start_slideshow(self.settings.wallpaper_interval_sec)
        else:
            self.wallpaper_manager.stop_slideshow()
        self._update_setting("wallpaper_slideshow", enabled)
        state = "enabled" if enabled else "disabled"
        self.notification_manager.push("system", "Wallpaper Slideshow", f"Slideshow {state}.")

    def _show_quick_settings(self) -> None:
        self.quick_panel.toggle(self.rect())

    def _set_theme(self, name: str, notify: bool = True) -> None:
        self.theme_engine.set_theme(name)
        app = QApplication.instance()
        if app:
            self.theme_engine.apply_to_application(app)
        self._update_setting("theme", name)
        if notify:
            self.notification_manager.push("system", "Theme", f"Theme changed to {name.title()}.")

    def _toggle_notifications(self) -> None:
        enabled = not self.settings.notifications_enabled
        self._update_setting("notifications_enabled", enabled)
        self.notification_manager.push(
            "system",
            "Notifications",
            f"Notifications {'enabled' if enabled else 'disabled'}.",
        )

    def _update_setting(self, key: str, value) -> None:
        self.settings = self.settings_store.update(**{key: value})
        self._settings_signature = self._signature(self.settings)

    def _launch_app(self, app_id: str) -> None:
        self.start_menu.hide()
        try:
            app = self.kernel.launch_app(app_id)
            window = self.window_manager.create_window(
                title=app.name,
                content=app.get_main_window(),
                parent=self,
                app_id=app_id,
            )
            window.closed.connect(lambda _: app.on_close())
            self.taskbar.set_running(app_id, True)
            self.taskbar.set_active_window_title(app.name)
            self.notification_manager.push(app_id, app.name, "App launched")
        except Exception as exc:  # pragma: no cover - UI safety net
            logger.exception("Failed to launch app %s", app_id)
            QMessageBox.critical(self, "Launch Error", f"Failed to launch {app_id}:\n{exc}")

    def _on_window_focus(self, window) -> None:
        title = window.title_bar.title_label.text()
        self.taskbar.set_active_window_title(title)

    def _on_window_closed(self, window) -> None:
        if window is None:
            return
        app_id = getattr(window, "app_id", None)
        if app_id:
            self.taskbar.set_running(app_id, False)

    def _restart_session(self) -> None:
        self.notification_manager.push("system", "Restart", "Session restart requested.")

    def _lock_screen(self) -> None:
        self.canvas.setGraphicsEffect(self._canvas_blur)
        self._canvas_blur.setBlurRadius(18)
        self.quick_panel.hide()
        self.start_menu.hide()
        self.lock_overlay.show_lock(self.rect())

    def _handle_unlock_attempt(self, password: str) -> None:
        expected = self.settings.lock_password or "blendios"
        if password == expected:
            self.lock_overlay.hide_lock()
            self.canvas.setGraphicsEffect(None)
            return
        self.lock_overlay.message.setText("Incorrect password")

    def shutdown(self) -> None:
        self.start_menu.hide()
        self.quick_panel.hide()
        self.wallpaper_manager.stop_slideshow()
        self.kernel.shutdown()
        self.close()

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if hasattr(self, "quick_panel") and self.quick_panel.isVisible():
            self.quick_panel.setGeometry(
                self.rect().width() - self.quick_panel.width() - 12,
                72,
                self.quick_panel.width(),
                self.rect().height() - 144,
            )
        if hasattr(self, "lock_overlay") and self.lock_overlay.isVisible():
            self.lock_overlay.setGeometry(self.rect())

    def closeEvent(self, event: QCloseEvent) -> None:  # type: ignore[override]
        self.wallpaper_manager.stop_slideshow()
        self._settings_watch_timer.stop()
        self.kernel.shutdown()
        event.accept()
