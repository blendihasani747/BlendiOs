"""Apps router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from blendios.api.routers.auth import oauth2_scheme

router = APIRouter()


@router.get("")
async def list_apps(token: str = Depends(oauth2_scheme)) -> dict[str, list[dict[str, str]]]:
    """List installed applications."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.post("/{app_id}/launch")
async def launch_app(
    app_id: str, token: str = Depends(oauth2_scheme)
) -> dict[str, str]:
    """Launch an application."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.delete("/{app_id}")
async def uninstall_app(
    app_id: str, token: str = Depends(oauth2_scheme)
) -> dict[str, str]:
    """Uninstall an application (admin only)."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
