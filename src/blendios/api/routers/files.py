"""Files router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from blendios.api.routers.auth import oauth2_scheme
from blendios.api.schemas import FileCreateRequest, FileNode, FileUpdateRequest, SearchRequest

router = APIRouter()


@router.get("", response_model=list[FileNode])
async def list_files(
    path: str = "/", token: str = Depends(oauth2_scheme)
) -> list[FileNode]:
    """List files and folders in a directory."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.post("")
async def create_file(
    request: FileCreateRequest, token: str = Depends(oauth2_scheme)
) -> dict[str, str]:
    """Create a new file."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/{file_path:path}")
async def read_file(
    file_path: str, token: str = Depends(oauth2_scheme)
) -> dict[str, str]:
    """Read a file's metadata and content."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.put("/{file_path:path}")
async def update_file(
    file_path: str, request: FileUpdateRequest, token: str = Depends(oauth2_scheme)
) -> dict[str, str]:
    """Update a file."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.delete("/{file_path:path}")
async def delete_file(
    file_path: str, token: str = Depends(oauth2_scheme)
) -> dict[str, str]:
    """Move a file to trash."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.post("/search")
async def search_files(
    request: SearchRequest, token: str = Depends(oauth2_scheme)
) -> dict[str, list[dict[str, str]]]:
    """Search files and folders."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
