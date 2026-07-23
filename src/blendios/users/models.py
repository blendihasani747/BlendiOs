"""User and security domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from blendios.constants import ROLE_USER


class Role(str, Enum):
    """Built-in user roles."""

    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


@dataclass
class User:
    """Represents a BlendiOS user account."""

    id: int
    username: str
    email: str | None
    full_name: str | None
    role: Role = Role.USER
    is_active: bool = True
    is_locked: bool = False
    failed_logins: int = 0
    last_login_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN

    @property
    def is_guest(self) -> bool:
        return self.role == Role.GUEST


@dataclass
class Session:
    """Represents an authenticated user session."""

    id: int
    user_id: int
    token: str
    refresh_token: str | None
    ip_address: str | None
    user_agent: str | None
    issued_at: datetime
    expires_at: datetime
    is_revoked: bool = False

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at


@dataclass(frozen=True)
class Permission:
    """A granular permission."""

    resource: str
    action: str

    def __str__(self) -> str:
        return f"{self.resource}:{self.action}"


# Built-in permissions
PERMISSIONS = {
    "user:create": Permission("user", "create"),
    "user:read": Permission("user", "read"),
    "user:update": Permission("user", "update"),
    "user:delete": Permission("user", "delete"),
    "file:create": Permission("file", "create"),
    "file:read": Permission("file", "read"),
    "file:update": Permission("file", "update"),
    "file:delete": Permission("file", "delete"),
    "app:install": Permission("app", "install"),
    "app:launch": Permission("app", "launch"),
    "app:uninstall": Permission("app", "uninstall"),
    "process:kill": Permission("process", "kill"),
    "system:shutdown": Permission("system", "shutdown"),
    "system:settings": Permission("system", "settings"),
    "log:read": Permission("log", "read"),
}

# Role permission mappings
ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.ADMIN: set(PERMISSIONS.keys()),
    Role.USER: {
        "file:create",
        "file:read",
        "file:update",
        "file:delete",
        "app:launch",
        "system:settings",
    },
    Role.GUEST: {
        "file:read",
        "app:launch",
    },
}
