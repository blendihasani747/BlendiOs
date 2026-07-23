"""Notes app for BlendiOS."""

from __future__ import annotations

import json
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from blendios.apps.base_app import BaseApp
from blendios.constants import DEFAULT_DATA_DIR


@dataclass(slots=True)
class NoteItem:
    """Serializable note model."""

    title: str
    content: str
    pinned: bool = False


class NotesRepository:
    """Simple JSON persistence for notes."""

    def __init__(self) -> None:
        self.path = DEFAULT_DATA_DIR / "system" / "notes.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[NoteItem]:
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return [NoteItem(**item) for item in raw]
        except (json.JSONDecodeError, OSError, TypeError):
            return []

    def save(self, notes: list[NoteItem]) -> None:
        payload = [asdict(item) for item in notes]
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


class NotesWidget(QWidget):
    """Searchable notes editor with auto-save."""

    def __init__(self) -> None:
        super().__init__()
        self.repo = NotesRepository()
        self.notes = self.repo.load()
        self.current_index = -1

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        header = QHBoxLayout()
        root.addLayout(header)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search notes")
        self.search.textChanged.connect(self._refresh_list)
        header.addWidget(self.search, 1)

        self.new_button = QPushButton("New")
        self.delete_button = QPushButton("Delete")
        self.pin_button = QPushButton("Pin")
        self.export_button = QPushButton("Export")

        for button in (self.new_button, self.delete_button, self.pin_button, self.export_button):
            header.addWidget(button)

        split = QHBoxLayout()
        root.addLayout(split, 1)

        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._select_note)
        split.addWidget(self.list_widget, 1)

        self.editor = QTextEdit()
        self.editor.textChanged.connect(self._autosave_current)
        split.addWidget(self.editor, 3)

        self.new_button.clicked.connect(self._create_note)
        self.delete_button.clicked.connect(self._delete_note)
        self.pin_button.clicked.connect(self._toggle_pin)
        self.export_button.clicked.connect(self._export_note)

        self._refresh_list()

    def _refresh_list(self) -> None:
        query = self.search.text().strip().lower()
        self.list_widget.clear()

        indexed = list(enumerate(self.notes))
        indexed.sort(key=lambda pair: (not pair[1].pinned, pair[1].title.lower()))

        for source_index, note in indexed:
            if query and query not in note.title.lower() and query not in note.content.lower():
                continue
            prefix = "[PIN] " if note.pinned else ""
            item = QListWidgetItem(f"{prefix}{note.title}")
            item.setData(Qt.ItemDataRole.UserRole, source_index)
            self.list_widget.addItem(item)

        if self.list_widget.count() > 0 and self.current_index < 0:
            self.list_widget.setCurrentRow(0)

    def _select_note(self, row: int) -> None:
        if row < 0:
            self.current_index = -1
            self.editor.clear()
            return
        item = self.list_widget.item(row)
        if item is None:
            return
        source_index = item.data(Qt.ItemDataRole.UserRole)
        if source_index is None:
            return
        self.current_index = int(source_index)
        self.editor.blockSignals(True)
        self.editor.setPlainText(self.notes[self.current_index].content)
        self.editor.blockSignals(False)

    def _create_note(self) -> None:
        title, ok = QInputDialog.getText(self, "New Note", "Title:")
        if not ok or not title.strip():
            return
        self.notes.append(NoteItem(title=title.strip(), content=""))
        self.repo.save(self.notes)
        self._refresh_list()

    def _delete_note(self) -> None:
        if self.current_index < 0:
            return
        if QMessageBox.question(self, "Delete Note", "Delete selected note?") != QMessageBox.StandardButton.Yes:
            return
        self.notes.pop(self.current_index)
        self.current_index = -1
        self.repo.save(self.notes)
        self._refresh_list()

    def _toggle_pin(self) -> None:
        if self.current_index < 0:
            return
        self.notes[self.current_index].pinned = not self.notes[self.current_index].pinned
        self.repo.save(self.notes)
        self._refresh_list()

    def _autosave_current(self) -> None:
        if self.current_index < 0:
            return
        self.notes[self.current_index].content = self.editor.toPlainText()
        self.repo.save(self.notes)

    def _export_note(self) -> None:
        if self.current_index < 0:
            return
        note = self.notes[self.current_index]
        safe_name = "".join(ch for ch in note.title if ch.isalnum() or ch in (" ", "-", "_"))
        safe_name = safe_name.strip() or "note"
        safe_target = DEFAULT_DATA_DIR / "system" / f"{safe_name}.txt"
        safe_target.write_text(note.content, encoding="utf-8")
        QMessageBox.information(self, "Exported", f"Saved to {safe_target}")


class NotesApp(BaseApp):
    """Notes application."""

    app_id = "notes"
    name = "Notes"
    version = "0.1.0"
    icon = "icons/notes.png"
    category = "productivity"

    def build_ui(self) -> QWidget:
        return NotesWidget()

    def on_launch(self) -> None:
        pass
