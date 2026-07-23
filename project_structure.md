# BlendiOS — Project Structure

This document mirrors the actual project layout and explains the responsibility of each module.

```
BlendiOS/
├── README.md                       # Project overview and quick-start
├── pyproject.toml                  # Dependencies, build metadata, scripts
├── .env.example                    # Environment variable template
├── .gitignore
├── Makefile                        # Standard tasks (test, lint, run, docs)
├── project_structure.md            # This file
│
├── config/
│   ├── app.json                    # Global application configuration
│   ├── logging.yaml                # Logging configuration
│   ├── themes.json                 # Theme registry
│   └── security.yaml               # Security policies and limits
│
├── docs/                           # Architecture and API documentation
│   ├── BlendiOS_Master_Specification.md
│   ├── Architecture_Diagram.md
│   ├── API_Specification.md
│   └── Database_Schema.sql
│
├── assets/                         # Static resources
│   ├── icons/
│   ├── themes/
│   └── wallpapers/
│
├── scripts/                        # Automation and setup scripts
│   ├── setup_dev.sh
│   ├── seed_db.py
│   └── run_tests.sh
│
├── src/
│   └── blendios/                   # Main Python package
│       ├── __init__.py
│       ├── main.py                 # Entry point
│       ├── constants.py            # Global constants
│       ├── exceptions.py           # Domain exceptions
│       │
│       ├── kernel/                 # Core OS simulation layer
│       │   ├── __init__.py
│       │   ├── process_manager.py
│       │   ├── scheduler.py
│       │   ├── memory_manager.py
│       │   ├── service_manager.py
│       │   ├── crash_handler.py
│       │   ├── event_bus.py
│       │   └── models.py
│       │
│       ├── desktop/                # Desktop shell UI
│       │   ├── __init__.py
│       │   ├── desktop_shell.py
│       │   ├── taskbar.py
│       │   ├── start_menu.py
│       │   ├── notification_center.py
│       │   ├── widget_engine.py
│       │   ├── search.py
│       │   ├── virtual_desktops.py
│       │   └── models.py
│       │
│       ├── window_manager/         # Windowing logic
│       │   ├── __init__.py
│       │   ├── window_manager.py
│       │   ├── window.py
│       │   ├── decorators.py
│       │   ├── animations.py
│       │   ├── snap_manager.py
│       │   └── models.py
│       │
│       ├── users/                  # User and security subsystem
│       │   ├── __init__.py
│       │   ├── auth_service.py
│       │   ├── user_repository.py
│       │   ├── session_manager.py
│       │   ├── permission_service.py
│       │   ├── role_manager.py
│       │   ├── encryption.py
│       │   ├── audit_logger.py
│       │   └── models.py
│       │
│       ├── filesystem/             # Virtual file system
│       │   ├── __init__.py
│       │   ├── vfs.py
│       │   ├── node.py
│       │   ├── folder.py
│       │   ├── file.py
│       │   ├── search_engine.py
│       │   ├── compression.py
│       │   ├── trash_manager.py
│       │   ├── restore_manager.py
│       │   └── models.py
│       │
│       ├── apps/                   # Internal applications
│       │   ├── __init__.py
│       │   ├── base_app.py
│       │   ├── app_registry.py
│       │   ├── file_explorer/
│       │   ├── terminal/
│       │   ├── settings/
│       │   ├── calculator/
│       │   ├── notes/
│       │   ├── browser/
│       │   ├── media_player/
│       │   ├── paint/
│       │   ├── task_manager/
│       │   └── app_store/
│       │
│       ├── api/                    # FastAPI backend
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── dependencies.py
│       │   ├── security.py
│       │   ├── routers/
│       │   │   ├── auth.py
│       │   │   ├── users.py
│       │   │   ├── files.py
│       │   │   ├── apps.py
│       │   │   ├── processes.py
│       │   │   ├── settings.py
│       │   │   └── logs.py
│       │   └── schemas.py
│       │
│       ├── database/               # Persistence layer
│       │   ├── __init__.py
│       │   ├── connection.py
│       │   ├── migrations/
│       │   ├── repositories/
│       │   └── unit_of_work.py
│       │
│       ├── scheduler/              # Process scheduling algorithms
│       │   ├── __init__.py
│       │   └── (re-exports kernel.scheduler)
│       │
│       ├── memory/                 # Memory simulation
│       │   ├── __init__.py
│       │   └── (re-exports kernel.memory_manager)
│       │
│       ├── plugins/                # Plugin engine
│       │   ├── __init__.py
│       │   ├── loader.py
│       │   ├── registry.py
│       │   ├── interfaces.py
│       │   ├── hooks.py
│       │   └── sandbox.py
│       │
│       ├── themes/                 # Theming engine
│       │   ├── __init__.py
│       │   ├── theme_engine.py
│       │   ├── theme_loader.py
│       │   ├── palette.py
│       │   └── default_themes/
│       │
│       ├── services/               # Shared background services
│       │   ├── __init__.py
│       │   ├── heartbeat.py
│       │   ├── updater.py
│       │   └── backup.py
│       │
│       ├── common/                 # Shared utilities
│       │   ├── __init__.py
│       │   ├── validators.py
│       │   ├── singleton.py
│       │   ├── paths.py
│       │   ├── events.py
│       │   └── mixins.py
│       │
│       └── cli/                    # Command-line utilities
│           ├── __init__.py
│           └── blendios_cli.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   ├── conftest.py
│   └── fixtures/
│
└── dashboards/
    └── streamlit_dashboard.py
```

## Module Responsibility Matrix

| Module | Responsibility |
|---|---|
| `kernel/` | Simulates OS kernel services: process lifecycle, scheduling, memory accounting, service orchestration, crash handling, and inter-process events. |
| `desktop/` | Renders the desktop shell: wallpaper, taskbar, start menu, notifications, widgets, global search, and virtual desktops. |
| `window_manager/` | Manages application windows: creation, movement, resizing, snapping, z-order, minimize/maximize, focus, and animations. |
| `users/` | Authentication, authorization, roles, sessions, password hashing, encryption, file permissions, and audit logging. |
| `filesystem/` | Virtual file system implementation: nodes, folders, files, CRUD, search, compression, encryption, trash, and restore. |
| `apps/` | Internal applications. Each app is a self-contained package inheriting from `BaseApp`. |
| `api/` | FastAPI REST backend exposing system services to apps, dashboard, and external clients. |
| `database/` | SQLite connection management, migrations, repositories, and unit-of-work pattern. |
| `scheduler/` | Pluggable CPU scheduling algorithms used by the kernel process manager. |
| `memory/` | Simulated memory allocation, paging/segmentation helpers, and RAM monitoring. |
| `plugins/` | Dynamic plugin discovery, loading, sandboxing, and hook registration. |
| `themes/` | Theme engine, palette management, and built-in/custom theme loading. |
| `services/` | Long-running background services (heartbeat, updater, backup). |
| `common/` | Shared utilities, base classes, validators, and event helpers. |
| `cli/` | Administrative command-line interface for BlendiOS. |
| `dashboards/` | Streamlit monitoring and analytics dashboard. |
| `tests/` | Unit, integration, and end-to-end tests with fixtures. |
