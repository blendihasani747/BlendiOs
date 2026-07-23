"""Settings router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from blendios.api.routers.auth import oauth2_scheme
from blendios.api.schemas import SettingRead, SettingUpdate

router = APIRouter()


@router.get("", response_model=list[SettingRead])
async def get_settings(
    category: str | None = None, token: str = Depends(oauth2_scheme)
) -> list[SettingRead]:
    """Get system/user settings."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.put("")
async def update_settings(
    updates: list[SettingUpdate], token: str = Depends(oauth2_scheme)
) -> list[SettingRead]:
    """Update settings."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
