"""Pydantic schemas for the FastAPI backend."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Role(str, Enum):
    admin = "admin"
    user = "user"
    guest = "guest"


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int


class UserBase(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    role: Role = Role.user


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_locked: bool
    last_login_at: datetime | None
    created_at: datetime


class UserUpdate(BaseModel):
    email: str | None = None
    full_name: str | None = None
    role: Role | None = None
    is_active: bool | None = None


class FileNode(BaseModel):
    name: str
    type: str
    size_bytes: int | None = None
    permissions: str
    updated_at: datetime


class FileCreateRequest(BaseModel):
    path: str
    content: str | None = ""
    permissions: str = "644"


class FileUpdateRequest(BaseModel):
    content: str | None = None
    permissions: str | None = None


class SearchRequest(BaseModel):
    query: str
    path: str = "/"
    type: str | None = None
    limit: int = 20


class ProcessRead(BaseModel):
    pid: int
    app_id: str
    user_id: int
    status: str
    priority: int
    memory_mb: int
    cpu_percent: float
    started_at: datetime


class SettingRead(BaseModel):
    key: str
    value: str | int | float | bool
    value_type: str
    category: str


class SettingUpdate(BaseModel):
    key: str
    value: str | int | float | bool


class LogRead(BaseModel):
    id: int
    timestamp: datetime
    level: str
    category: str
    source: str
    message: str
    ip_address: str | None


class SystemStatus(BaseModel):
    uptime_seconds: float
    cpu_percent: float
    memory_total_mb: int
    memory_used_mb: int
    memory_free_mb: int
    process_count: int
    active_user_count: int
