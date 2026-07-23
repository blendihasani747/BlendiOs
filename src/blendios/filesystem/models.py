"""Virtual file system domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class NodeType(str, Enum):
    """Type of VFS node."""

    FILE = "file"
    FOLDER = "folder"


@dataclass
class FSNode:
    """Base class for virtual file system nodes."""

    id: int
    name: str
    path: str
    parent_id: int | None
    owner_id: int
    group_id: int | None
    permissions: str
    node_type: NodeType
    is_encrypted: bool = False
    is_compressed: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)

    def can_read(self, user_id: int, is_admin: bool = False) -> bool:
        """Check read permission (simplified Unix-style)."""
        if is_admin or user_id == self.owner_id:
            return int(self.permissions[0]) >= 4
        return int(self.permissions[2]) >= 4

    def can_write(self, user_id: int, is_admin: bool = False) -> bool:
        """Check write permission."""
        if is_admin or user_id == self.owner_id:
            return int(self.permissions[0]) >= 6
        return int(self.permissions[2]) >= 6

    def can_execute(self, user_id: int, is_admin: bool = False) -> bool:
        """Check execute permission."""
        if is_admin or user_id == self.owner_id:
            return int(self.permissions[0]) % 2 == 1
        return int(self.permissions[2]) % 2 == 1


@dataclass
class File(FSNode):
    """A virtual file."""

    size_bytes: int = 0
    mime_type: str = "application/octet-stream"
    content_ref: str | None = None
    checksum: str | None = None

    def __post_init__(self) -> None:
        self.node_type = NodeType.FILE


@dataclass
class Folder(FSNode):
    """A virtual folder."""

    children: list[FSNode] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.node_type = NodeType.FOLDER
