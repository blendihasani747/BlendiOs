"""Processes router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from blendios.api.routers.auth import oauth2_scheme
from blendios.api.schemas import ProcessRead

router = APIRouter()


@router.get("", response_model=list[ProcessRead])
async def list_processes(
    token: str = Depends(oauth2_scheme)
) -> list[ProcessRead]:
    """List running processes."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/{pid}", response_model=ProcessRead)
async def get_process(
    pid: int, token: str = Depends(oauth2_scheme)
) -> ProcessRead:
    """Get process details."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.post("/{pid}/kill")
async def kill_process(
    pid: int, token: str = Depends(oauth2_scheme)
) -> dict[str, str]:
    """Kill a process."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
