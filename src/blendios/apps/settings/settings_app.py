"""Settings application for BlendiOS."""

from __future__ import annotations

import platform
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from blendios.apps.base_app import BaseApp
from blendios.desktop.settings_store import SettingsStore


class SettingsCard(QFrame):
    """Reusable settings card container."""

    def __init__(self, title: str, subtitle: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("surface")

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        heading = QLabel(title)
        heading.setStyleSheet("font-size: 15px; font-weight: 600;")
        root.addWidget(heading)

        if subtitle:
            sub = QLabel(subtitle)
            sub.setObjectName("caption")
            sub.setWordWrap(True)
            root.addWidget(sub)

        self.content = QVBoxLayout()
        self.content.setContentsMargins(0, 0, 0, 0)
        self.content.setSpacing(10)
        root.addLayout(self.content)


class SettingsPage(QWidget):
    """Scrollable settings page with section cards."""

    def __init__(self, title: str, subtitle: str) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        root.addWidget(scroll, 1)

        host = QWidget()
        scroll.setWidget(host)

        self.layout = QVBoxLayout(host)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(14)

        heading = QLabel(title)
        heading.setStyleSheet("font-size: 24px; font-weight: 700;")
        self.layout.addWidget(heading)

        subheading = QLabel(subtitle)
        subheading.setObjectName("caption")
        self.layout.addWidget(subheading)

    def add_card(self, card: SettingsCard) -> None:
        self.layout.addWidget(card)

    def finish(self) -> None:
        self.layout.addStretch(1)


class SettingsWidget(QWidget):
    """Card-based settings experience with persistent controls."""

    def __init__(self) -> None:
        super().__init__()
        self.store = SettingsStore()
        self.settings = self.store.load()

        root = QHBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("surface")
        self.sidebar.setFixedWidth(230)
        root.addWidget(self.sidebar)

        self.pages = QStackedWidget()
        root.addWidget(self.pages, 1)

        self._build_pages()
        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

    def _build_pages(self) -> None:
        self._add_page("Appearance", self._build_appearance_page())
        self._add_page("Wallpaper", self._build_wallpaper_page())
        self._add_page("Display", self._build_display_page())
        self._add_page("Sound", self._build_sound_page())
        self._add_page("Notifications", self._build_notifications_page())
        self._add_page("Language & Region", self._build_language_page())
        self._add_page("Date & Time", self._build_datetime_page())
        self._add_page("Keyboard", self._build_keyboard_page())
        self._add_page("Mouse & Touchpad", self._build_mouse_page())
        self._add_page("Storage", self._build_storage_page())
        self._add_page("Accounts", self._build_accounts_page())
        self._add_page("Security & Privacy", self._build_security_page())
        self._add_page("Network & Internet", self._build_network_page())
        self._add_page("Updates", self._build_updates_page())
        self._add_page("Developer Mode", self._build_developer_page())
        self._add_page("About", self._build_about_page())

    def _add_page(self, title: str, page: QWidget) -> None:
        self.sidebar.addItem(QListWidgetItem(title))
        self.pages.addWidget(page)

    def _build_appearance_page(self) -> QWidget:
        page = SettingsPage("Appearance", "Shape the look and feel of your desktop.")

        card_theme = SettingsCard("Theme & Layout", "Core desktop visual system")
        form = QFormLayout()

        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["dark", "light", "blue", "green", "purple"])
        self.theme_selector.setCurrentText(self.settings.theme)

        self.taskbar_position = QComboBox()
        self.taskbar_position.addItems(["bottom", "top", "left", "right"])
        self.taskbar_position.setCurrentText(self.settings.taskbar_position)

        self.animation_speed = QComboBox()
        self.animation_speed.addItems(["off", "slow", "normal", "fast"])
        self.animation_speed.setCurrentText(self.settings.animation_speed)

        form.addRow("Theme", self.theme_selector)
        form.addRow("Taskbar Position", self.taskbar_position)
        form.addRow("Animation Speed", self.animation_speed)
        card_theme.content.addLayout(form)

        apply = QPushButton("Apply Appearance")
        apply.clicked.connect(self._save_appearance)
        card_theme.content.addWidget(apply)

        page.add_card(card_theme)
        page.finish()
        return page

    def _build_wallpaper_page(self) -> QWidget:
        page = SettingsPage("Wallpaper", "Select wallpapers and slideshow behavior.")
        card = SettingsCard("Wallpaper System", "Category, slideshow and interval")
        form = QFormLayout()

        self.wallpaper_category = QComboBox()
        self.wallpaper_category.addItems(["Nature", "Abstract", "Dark", "Light", "Minimal", "Custom"])
        self.wallpaper_category.setCurrentText(self.settings.wallpaper_category)

        self.slideshow_toggle = QCheckBox("Enable Wallpaper Slideshow")
        self.slideshow_toggle.setChecked(self.settings.wallpaper_slideshow)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 3600)
        self.interval_spin.setValue(self.settings.wallpaper_interval_sec)
        self.interval_spin.setSuffix(" sec")

        form.addRow("Category", self.wallpaper_category)
        form.addRow("Interval", self.interval_spin)
        card.content.addWidget(self.slideshow_toggle)
        card.content.addLayout(form)

        apply = QPushButton("Apply Wallpaper")
        apply.clicked.connect(self._save_wallpaper)
        card.content.addWidget(apply)

        page.add_card(card)
        page.finish()
        return page

    def _build_display_page(self) -> QWidget:
        page = SettingsPage("Display", "Screen brightness, night mode and scaling.")
        card = SettingsCard("Screen Controls")

        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(self.settings.brightness)

        self.night_mode_toggle = QCheckBox("Night Mode")
        self.night_mode_toggle.setChecked(self.settings.night_mode_enabled)

        card.content.addWidget(QLabel("Brightness"))
        card.content.addWidget(self.brightness_slider)
        card.content.addWidget(self.night_mode_toggle)

        apply = QPushButton("Apply Display")
        apply.clicked.connect(self._save_display)
        card.content.addWidget(apply)

        page.add_card(card)
        page.finish()
        return page

    def _build_sound_page(self) -> QWidget:
        page = SettingsPage("Sound", "Output and system sound levels.")
        card = SettingsCard("Audio")

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.settings.volume)

        card.content.addWidget(QLabel("Master Volume"))
        card.content.addWidget(self.volume_slider)

        apply = QPushButton("Apply Sound")
        apply.clicked.connect(self._save_sound)
        card.content.addWidget(apply)

        page.add_card(card)
        page.finish()
        return page

    def _build_notifications_page(self) -> QWidget:
        page = SettingsPage("Notifications", "Global notifications and taskbar behavior.")
        card = SettingsCard("Notification Preferences")

        self.notifications_toggle = QCheckBox("Enable Notifications")
        self.notifications_toggle.setChecked(self.settings.notifications_enabled)

        self.taskbar_autohide_toggle = QCheckBox("Taskbar Auto-hide")
        self.taskbar_autohide_toggle.setChecked(self.settings.taskbar_auto_hide)

        card.content.addWidget(self.notifications_toggle)
        card.content.addWidget(self.taskbar_autohide_toggle)

        apply = QPushButton("Apply Notification Settings")
        apply.clicked.connect(self._save_notifications)
        card.content.addWidget(apply)

        page.add_card(card)
        page.finish()
        return page

    def _simple_info_page(self, title: str, subtitle: str, lines: list[str]) -> QWidget:
        page = SettingsPage(title, subtitle)
        card = SettingsCard(title)
        for line in lines:
            card.content.addWidget(QLabel(line))
        page.add_card(card)
        page.finish()
        return page

    def _build_language_page(self) -> QWidget:
        return self._simple_info_page(
            "Language & Region",
            "Regional formatting and language controls.",
            ["Language: English", "Date format: YYYY-MM-DD", "Time format: 24-hour", "Timezone: UTC"],
        )

    def _build_datetime_page(self) -> QWidget:
        return self._simple_info_page(
            "Date & Time",
            "Clock synchronization and formats.",
            ["Auto Sync: Enabled", "Clock format: HH:mm"],
        )

    def _build_keyboard_page(self) -> QWidget:
        return self._simple_info_page(
            "Keyboard",
            "Input and shortcut behavior.",
            ["Input language: EN-US", "Key repeat: normal"],
        )

    def _build_mouse_page(self) -> QWidget:
        return self._simple_info_page(
            "Mouse & Touchpad",
            "Pointer movement and click settings.",
            ["Pointer speed: 10", "Double-click speed: 400 ms"],
        )

    def _build_storage_page(self) -> QWidget:
        return self._simple_info_page(
            "Storage",
            "Storage allocation and cleanup actions.",
            ["Used: 18.6 GB / 64.0 GB", "Apps: 7.8 GB", "Files: 8.9 GB", "Cache: 1.9 GB"],
        )

    def _build_accounts_page(self) -> QWidget:
        return self._simple_info_page(
            "Accounts",
            "User management and sign-in options.",
            ["Current user: BlendiOS User", "Guest mode: disabled"],
        )

    def _build_security_page(self) -> QWidget:
        page = SettingsPage("Security & Privacy", "Lock password and encryption settings.")
        card = SettingsCard("Lock & Encryption")
        form = QFormLayout()

        self.lock_password_input = QLineEdit(self.settings.lock_password)
        self.lock_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.encryption_toggle = QCheckBox("Enable File Encryption")
        self.encryption_toggle.setChecked(self.settings.security_encryption_enabled)

        form.addRow("Lock Password", self.lock_password_input)
        card.content.addLayout(form)
        card.content.addWidget(self.encryption_toggle)

        apply = QPushButton("Apply Security")
        apply.clicked.connect(self._save_security)
        card.content.addWidget(apply)

        page.add_card(card)
        page.finish()
        return page

    def _build_network_page(self) -> QWidget:
        page = SettingsPage("Network & Internet", "Connectivity and proxy controls.")
        card = SettingsCard("Network Controls")
        form = QFormLayout()

        self.proxy_input = QLineEdit(self.settings.proxy_url)
        self.proxy_input.setPlaceholderText("http://proxy:port")

        self.wifi_toggle = QCheckBox("Enable Wi-Fi")
        self.wifi_toggle.setChecked(self.settings.wifi_enabled)

        self.bluetooth_toggle = QCheckBox("Enable Bluetooth")
        self.bluetooth_toggle.setChecked(self.settings.bluetooth_enabled)

        form.addRow("Proxy", self.proxy_input)
        card.content.addLayout(form)
        card.content.addWidget(self.wifi_toggle)
        card.content.addWidget(self.bluetooth_toggle)

        apply = QPushButton("Apply Network")
        apply.clicked.connect(self._save_network)
        card.content.addWidget(apply)

        page.add_card(card)
        page.finish()
        return page

    def _build_updates_page(self) -> QWidget:
        return self._simple_info_page(
            "Updates",
            "System update channel and history.",
            ["Auto Updates: Enabled", "Last check: Not available"],
        )

    def _build_developer_page(self) -> QWidget:
        return self._simple_info_page(
            "Developer Mode",
            "Developer and debugging toggles.",
            ["Terminal access: Enabled", "API server: Disabled"],
        )

    def _build_about_page(self) -> QWidget:
        page = SettingsPage("About", "System information and runtime details.")
        card = SettingsCard("BlendiOS")
        card.content.addWidget(QLabel("Version: 0.3.0"))
        card.content.addWidget(QLabel(f"Python: {sys.version.split()[0]}"))
        card.content.addWidget(QLabel(f"Platform: {platform.platform()}"))
        card.content.addWidget(QLabel("License: MIT"))
        page.add_card(card)
        page.finish()
        return page

    def _save_appearance(self) -> None:
        self.settings = self.store.update(
            theme=self.theme_selector.currentText(),
            taskbar_position=self.taskbar_position.currentText(),
            animation_speed=self.animation_speed.currentText(),
        )

    def _save_wallpaper(self) -> None:
        self.settings = self.store.update(
            wallpaper_category=self.wallpaper_category.currentText(),
            wallpaper_slideshow=self.slideshow_toggle.isChecked(),
            wallpaper_interval_sec=self.interval_spin.value(),
        )

    def _save_notifications(self) -> None:
        self.settings = self.store.update(
            notifications_enabled=self.notifications_toggle.isChecked(),
            taskbar_auto_hide=self.taskbar_autohide_toggle.isChecked(),
        )

    def _save_display(self) -> None:
        self.settings = self.store.update(
            brightness=self.brightness_slider.value(),
            night_mode_enabled=self.night_mode_toggle.isChecked(),
        )

    def _save_sound(self) -> None:
        self.settings = self.store.update(volume=self.volume_slider.value())

    def _save_security(self) -> None:
        self.settings = self.store.update(
            lock_password=self.lock_password_input.text().strip() or "blendios",
            security_encryption_enabled=self.encryption_toggle.isChecked(),
        )

    def _save_network(self) -> None:
        self.settings = self.store.update(
            wifi_enabled=self.wifi_toggle.isChecked(),
            bluetooth_enabled=self.bluetooth_toggle.isChecked(),
            proxy_url=self.proxy_input.text().strip(),
        )


class SettingsApp(BaseApp):
    """Settings application."""

    app_id = "settings"
    name = "Settings"
    version = "0.3.0"
    icon = "icons/settings.png"
    category = "system"

    def build_ui(self) -> QWidget:
        return SettingsWidget()

    def on_launch(self) -> None:
        pass
