"""Users router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from blendios.api.routers.auth import oauth2_scheme
from blendios.api.schemas import UserRead, UserUpdate

router = APIRouter()


@router.get("", response_model=list[UserRead])
async def list_users(token: str = Depends(oauth2_scheme)) -> list[UserRead]:
    """List all users (admin only)."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/me", response_model=UserRead)
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserRead:
    """Get the currently authenticated user."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int, token: str = Depends(oauth2_scheme)
) -> UserRead:
    """Get a user by ID."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int, update: UserUpdate, token: str = Depends(oauth2_scheme)
) -> UserRead:
    """Update a user."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.delete("/{user_id}")
async def delete_user(
    user_id: int, token: str = Depends(oauth2_scheme)
) -> dict[str, str]:
    """Delete a user."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
