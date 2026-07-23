"""Terminal application for BlendiOS."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from blendios.apps.base_app import AppContext, BaseApp


class TerminalWidget(QWidget):
    """Terminal UI widget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: #1e1e1e; color: #cccccc;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 11))
        self.output.setStyleSheet("border: none;")
        layout.addWidget(self.output, 1)

        self.input = QLineEdit()
        self.input.setFont(QFont("Consolas", 11))
        self.input.setStyleSheet(
            "background-color: #1e1e1e; color: #cccccc; border: none; padding: 8px;"
        )
        self.input.setPlaceholderText("Enter command...")
        layout.addWidget(self.input)

        self.input.returnPressed.connect(self._execute_command)
        self.output.append("BlendiOS Terminal v0.1.0")
        self.output.append("Type 'help' for a list of commands.\n")

    def _execute_command(self) -> None:
        command = self.input.text().strip()
        if not command:
            return

        self.output.append(f"> {command}")
        response = self._handle_command(command)
        self.output.append(response)
        self.input.clear()

    def _handle_command(self, command: str) -> str:
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:]

        handlers = {
            "help": self._cmd_help,
            "echo": self._cmd_echo,
            "whoami": self._cmd_whoami,
            "clear": self._cmd_clear,
            "date": self._cmd_date,
            "uname": self._cmd_uname,
            "ps": self._cmd_ps,
        }

        handler = handlers.get(cmd)
        if handler:
            return handler(args)
        return f"{cmd}: command not found"

    def _cmd_help(self, args: list[str]) -> str:
        return (
            "Available commands:\n"
            "  help    Show this help message\n"
            "  echo    Print text\n"
            "  whoami  Show current user\n"
            "  date    Show current date and time\n"
            "  uname   Show system info\n"
            "  ps      List running processes\n"
            "  clear   Clear the terminal screen"
        )

    def _cmd_echo(self, args: list[str]) -> str:
        return " ".join(args)

    def _cmd_whoami(self, args: list[str]) -> str:
        return "user"

    def _cmd_date(self, args: list[str]) -> str:
        from datetime import datetime

        return datetime.now().isoformat()

    def _cmd_uname(self, args: list[str]) -> str:
        return "BlendiOS 0.1.0 (Python Desktop Environment)"

    def _cmd_ps(self, args: list[str]) -> str:
        return "PID  APP\n1    desktop_shell\n2    terminal"

    def _cmd_clear(self, args: list[str]) -> str:
        self.output.clear()
        return ""


class TerminalApp(BaseApp):
    """Terminal application."""

    app_id = "terminal"
    name = "Terminal"
    version = "0.1.0"
    icon = "icons/terminal.png"
    category = "system"

    def build_ui(self) -> QWidget:
        return TerminalWidget()

    def on_launch(self) -> None:
        pass
