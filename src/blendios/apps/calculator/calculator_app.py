"""Calculator application for BlendiOS."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from blendios.apps.base_app import AppContext, BaseApp


class CalculatorWidget(QWidget):
    """Calculator UI widget."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("surface")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.display = QLineEdit("0")
        self.display.setReadOnly(True)
        self.display.setStyleSheet(
            "background-color: #2d2d30; color: white; border: none; padding: 12px; font-size: 24px;"
        )
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.display)

        buttons = [
            ["C", "±", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "−"],
            ["1", "2", "3", "+"],
            ["0", ".", "="],
        ]

        grid = QGridLayout()
        grid.setSpacing(8)

        for row, row_buttons in enumerate(buttons):
            for col, text in enumerate(row_buttons):
                btn = QPushButton(text)
                btn.setMinimumSize(64, 48)
                if text in "0123456789.":
                    btn.setStyleSheet(
                        "background-color: #3c3c3c; color: white; border: none; font-size: 16px;"
                    )
                elif text == "=":
                    btn.setStyleSheet(
                        "background-color: #0078d4; color: white; border: none; font-size: 16px;"
                    )
                else:
                    btn.setStyleSheet(
                        "background-color: #505050; color: white; border: none; font-size: 16px;"
                    )

                # 0 spans two columns
                if text == "0":
                    grid.addWidget(btn, row + 1, col, 1, 2)
                elif row == 4 and col > 0:
                    # . and = shift one column to the right because 0 spans two
                    grid.addWidget(btn, row + 1, col + 1)
                else:
                    grid.addWidget(btn, row + 1, col)

                btn.clicked.connect(lambda checked, t=text: self._on_button(t))

        layout.addLayout(grid)

        self._current = "0"
        self._operator: str | None = None
        self._operand: float | None = None
        self._reset_next = False

    def _on_button(self, text: str) -> None:
        if text in "0123456789":
            if self._current == "0" or self._reset_next:
                self._current = text
                self._reset_next = False
            else:
                self._current += text
        elif text == ".":
            if "." not in self._current:
                self._current += "."
        elif text in "+-×÷":
            self._operand = float(self._current)
            self._operator = text
            self._reset_next = True
        elif text == "=":
            self._calculate()
        elif text == "C":
            self._current = "0"
            self._operator = None
            self._operand = None
        elif text == "±":
            value = float(self._current)
            self._current = str(-value)
        elif text == "%":
            value = float(self._current)
            self._current = str(value / 100)

        self.display.setText(self._current)

    def _calculate(self) -> None:
        if self._operator is None or self._operand is None:
            return
        try:
            right = float(self._current)
            if self._operator == "+":
                result = self._operand + right
            elif self._operator == "−":
                result = self._operand - right
            elif self._operator == "×":
                result = self._operand * right
            elif self._operator == "÷":
                result = self._operand / right if right != 0 else float("inf")
            else:
                return

            result_str = str(result)
            if "." in result_str:
                result_str = result_str.rstrip("0").rstrip(".")
            self._current = result_str
            self._operator = None
            self._operand = None
            self._reset_next = True
        except ValueError:
            self._current = "Error"


class CalculatorApp(BaseApp):
    """Calculator application."""

    app_id = "calculator"
    name = "Calculator"
    version = "0.1.0"
    icon = "icons/calculator.png"
    category = "utilities"

    def build_ui(self) -> QWidget:
        return CalculatorWidget()

    def on_launch(self) -> None:
        pass
