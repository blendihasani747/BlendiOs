"""Logs router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from blendios.api.routers.auth import oauth2_scheme
from blendios.api.schemas import LogRead

router = APIRouter()


@router.get("", response_model=list[LogRead])
async def query_logs(
    level: str | None = None,
    category: str | None = None,
    limit: int = 50,
    offset: int = 0,
    token: str = Depends(oauth2_scheme),
) -> list[LogRead]:
    """Query system logs (admin only)."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
