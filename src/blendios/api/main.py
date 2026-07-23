"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from blendios.api.routers import apps, auth, files, logs, processes, settings, users
from blendios.constants import API_PREFIX


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup: initialize kernel, database, services
    yield
    # Shutdown: cleanup resources


app = FastAPI(
    title="BlendiOS API",
    description="REST API for the BlendiOS desktop environment.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth.router, prefix=f"{API_PREFIX}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{API_PREFIX}/users", tags=["users"])
app.include_router(files.router, prefix=f"{API_PREFIX}/files", tags=["files"])
app.include_router(apps.router, prefix=f"{API_PREFIX}/apps", tags=["apps"])
app.include_router(processes.router, prefix=f"{API_PREFIX}/processes", tags=["processes"])
app.include_router(settings.router, prefix=f"{API_PREFIX}/settings", tags=["settings"])
app.include_router(logs.router, prefix=f"{API_PREFIX}/logs", tags=["logs"])


@app.get(f"{API_PREFIX}/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "BlendiOS API"}


def main() -> None:
    import uvicorn

    uvicorn.run("blendios.api.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
