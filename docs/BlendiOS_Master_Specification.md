# BlendiOS — Master Project Specification

**Version:** 1.0.0  
**Status:** Draft / Blueprint  
**Date:** 2026-07-02  
**Classification:** Internal Engineering Document  
**Target Audience:** Software Architects, Senior Engineers, Tech Leads, Contributors

---

## 0. Executive Summary

**BlendiOS** is a large-scale, Python-based desktop operating system *environment* that runs as an application layer on top of an existing host operating system (Linux, macOS, or Windows). It is **not** a bootable kernel. Instead, it simulates the user experience, architecture, and services of a desktop OS by providing:

- A multi-user login and session subsystem.
- A virtual file system with permissions, encryption, trash, and compression.
- A process and memory manager with pluggable scheduling algorithms.
- A window manager, desktop shell, taskbar, widgets, and notifications.
- A suite of internal productivity and system applications.
- A FastAPI-based REST backend for cross-component communication.
- A Streamlit monitoring dashboard.
- A dynamic plugin and theming engine.

**Design goals:**

1. **Modularity:** Every subsystem is independently testable, replaceable, and versioned.
2. **Scalability:** The architecture supports 20,000–50,000+ lines of Python without tangled dependencies.
3. **Educational Value:** The project serves as a teaching platform for OS concepts, GUI development, API design, database modeling, security, and system integration.
4. **Professional Quality:** Production-ready patterns (dependency injection, layered architecture, event buses, async I/O, type hints, CI/CD, logging, exception handling).

---

## 1. Vision & Scope

### 1.1 Purpose

BlendiOS exists to demonstrate how a desktop operating environment can be modeled entirely in Python. It bridges the gap between academic operating-system theory and modern application development by exposing real engineering concerns:

- Authentication, authorization, and audit logging.
- Resource scheduling and memory allocation simulation.
- GUI window composition and event handling.
- Persistent state management with SQLite.
- REST API design and security.
- Plugin-driven extensibility.
- Data visualization and analytics dashboards.

### 1.2 Learning Goals

By building and extending BlendiOS, engineers will learn to:

- Design layered architectures with clear separation of concerns.
- Implement scheduler algorithms (FIFO, Round Robin, Priority, SJF).
- Model memory allocation, paging, and RAM monitoring.
- Build a PySide6 desktop shell with a custom window manager.
- Secure a multi-user system using bcrypt, sessions, permissions, and encryption.
- Create RESTful APIs with FastAPI, JWT/OAuth2, and dependency injection.
- Build analytical dashboards with Streamlit, Pandas, Plotly, and Matplotlib.
- Write testable, typed Python using Pydantic models and dataclasses.
- Develop a dynamic plugin loader using Python importlib and entry points.
- Manage themes and UI customization through a declarative engine.

### 1.3 Target Scale

| Metric | Target |
|---|---|
| Total Python LOC | 20,000–50,000+ |
| Modules / Packages | 60–100+ |
| Internal Applications | 10+ |
| Database Tables | 10+ |
| REST Endpoints | 30+ |
| Plugin Extension Points | 4+ |
| Themes | 6 built-in + unlimited custom |
| Unit/Integration Tests | 500+ |

### 1.4 6–12 Month Roadmap (High-Level)

| Quarter | Focus |
|---|---|
| **Q1 (Months 1–3)** | Foundation: architecture, kernel, user/security, VFS, SQLite, PySide6 shell. |
| **Q2 (Months 4–6)** | Desktop environment, terminal, file explorer, settings, calculator, notes. |
| **Q3 (Months 7–9)** | Task manager, scheduler/memory simulation, browser, media player, paint, app store. |
| **Q4 (Months 10–12)** | FastAPI backend, Streamlit dashboard, plugin system, themes, testing, optimization, documentation. |

---

## 2. Folder Architecture

```
BlendiOS/
├── README.md                       # Project overview and quick-start
├── pyproject.toml                  # Dependencies, build metadata, scripts
├── .env.example                    # Environment variable template
├── .gitignore
├── Makefile                        # Standard tasks (test, lint, run, docs)
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
│       │   ├── base_scheduler.py
│       │   ├── fifo.py
│       │   ├── round_robin.py
│       │   ├── priority.py
│       │   └── shortest_job_first.py
│       │
│       ├── memory/                 # Memory simulation
│       │   ├── __init__.py
│       │   ├── memory_manager.py
│       │   ├── allocator.py
│       │   ├── ram_monitor.py
│       │   └── models.py
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

### 2.1 Module Responsibility Matrix

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

---

## 3. Core System Modules

### 3.1 Kernel (`src/blendios/kernel/`)

The **Kernel** is the central controller of BlendiOS. It does *not* interact with real hardware; it simulates operating-system primitives and coordinates all subsystems through an event bus.

#### 3.1.1 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Kernel                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Process      │  │ Memory       │  │ Service          │  │
│  │ Manager      │◄─┤ Manager      │◄─┤ Manager          │  │
│  └──────┬───────┘  └──────────────┘  └────────┬─────────┘  │
│         │                                      │            │
│  ┌──────▼───────┐  ┌──────────────┐  ┌────────▼─────────┐  │
│  │ Scheduler    │  │ Crash        │  │ Event Bus        │  │
│  │ (pluggable)  │  │ Handler      │  │ (pub/sub)        │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### 3.1.2 Key Classes

| Class | Responsibility |
|---|---|
| `Kernel` | Singleton facade. Initializes all managers and exposes system-level operations. |
| `ProcessManager` | Creates, terminates, suspends, resumes, and queries processes. Maintains the process table. |
| `Scheduler` | Abstract base; concrete implementations select the next process to run. |
| `MemoryManager` | Tracks simulated RAM allocation, deallocation, and page usage. |
| `ServiceManager` | Registers and supervises long-running background services. |
| `CrashHandler` | Captures exceptions, logs them, restarts failed services, and notifies the user. |
| `EventBus` | Async publish/subscribe messaging between kernel, apps, and UI. |

#### 3.1.3 Kernel Event Flow

1. **Startup:** `Kernel.bootstrap()` initializes database, loads users, mounts VFS, starts services, and launches the desktop shell.
2. **App Launch:** App requests process creation → `ProcessManager.create_process()` → scheduler enqueues process → event published to desktop.
3. **Scheduling:** A background tick (e.g., 100 ms) triggers the scheduler to update the active process.
4. **Memory Allocation:** Each process declares requested memory; `MemoryManager` simulates allocation and raises `OutOfMemoryError` if limits are exceeded.
5. **Crash:** Uncaught exceptions in processes/services are routed to `CrashHandler`, which logs, attempts restart, and notifies the UI.

---

### 3.2 Desktop Environment (`src/blendios/desktop/`)

The **Desktop Environment** is the graphical shell users interact with. It is built on PySide6 and communicates with the kernel and apps through the event bus and API client.

#### 3.2.1 Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      Desktop Shell                              │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────────────┐ │
│  │ Wallpaper   │  │ Taskbar     │  │ Notification Center    │ │
│  └─────────────┘  └──────┬──────┘  └────────────────────────┘ │
│                          │                                     │
│  ┌─────────────┐  ┌──────▼──────┐  ┌────────────────────────┐ │
│  │ Start Menu  │  │ Widgets     │  │ Global Search          │ │
│  └─────────────┘  └─────────────┘  └────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐│
│  │ Virtual Desktops Manager                                  ││
│  └───────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────┘
```

#### 3.2.2 Key Classes

| Class | Responsibility |
|---|---|
| `DesktopShell` | Main PySide6 `QMainWindow`. Hosts the desktop surface, taskbar, and shortcuts. |
| `Taskbar` | Shows open apps, clock, system tray, start button, and quick-launch icons. |
| `StartMenu` | Categorized app launcher with search and power options. |
| `NotificationCenter` | Displays toasts, history, andDo not disturb toggle. |
| `WidgetEngine` | Renders desktop widgets (clock, CPU/RAM meters, weather, notes). |
| `GlobalSearch` | Indexes apps, files, settings, and commands; provides fuzzy search. |
| `VirtualDesktops` | Manages multiple virtual desktops and window placement. |

---

### 3.3 Window Manager (`src/blendios/window_manager/`)

The **Window Manager** controls application window geometry, focus, stacking order, snap assist, and animations. Each app window is a `QWidget` wrapped in a `ManagedWindow`.

#### 3.3.1 Architecture

```
App Window ──► ManagedWindow ──► WindowManager ──► Desktop Shell
                  │
                  ├─ Decorators (title bar, buttons)
                  ├─ SnapManager (edges, zones)
                  ├─ AnimationEngine (move, fade, resize)
                  └─ Focus / Z-Order registry
```

#### 3.3.2 Key Classes

| Class | Responsibility |
|---|---|
| `WindowManager` | Singleton. Tracks all windows, assigns IDs, routes focus and geometry changes. |
| `ManagedWindow` | Wrapper around an app `QWidget`. Adds custom chrome, resize grips, and title bar. |
| `WindowDecorator` | Custom title bar with minimize, maximize, close, and context menu. |
| `SnapManager` | Handles drag-to-snap (left/right half, quarters, maximize), hotkey tiling, and snap zones. |
| `AnimationEngine` | PySide6 animation framework for open/close, minimize, snap, and focus transitions. |

#### 3.3.3 Window Lifecycle

1. App requests a window via `WindowManager.create_window(app, content_widget)`.
2. A `ManagedWindow` is constructed with decorators and registered in the z-order list.
3. Window appears with an open animation and receives focus.
4. User interactions (move, resize, snap) are handled by the manager.
5. On close, the window triggers an animation, unregisters from the manager, and notifies the kernel to terminate the process.

---

## 4. User System & Security

### 4.1 Authentication

- **Local login** via username + password.
- **bcrypt** used for password hashing with a configurable work factor (default 12).
- **Sessions** stored in SQLite with session ID, user ID, IP, user agent, issued at, and expiry.
- **API authentication** via OAuth2 Password Bearer tokens issued on login.
- **Token refresh** and **logout invalidation** supported.

### 4.2 Authorization

- Role-Based Access Control (RBAC) with three built-in roles:
  - **Admin:** Full system access, user management, logs, settings.
  - **User:** Standard access to files, apps, and personal settings.
  - **Guest:** Ephemeral session, restricted file access, no persistence.
- Permissions are granular: `file:read`, `file:write`, `user:create`, `app:install`, `system:shutdown`, etc.

### 4.3 Security Stack

| Concern | Implementation |
|---|---|
| Password hashing | `bcrypt.hashpw(password, bcrypt.gensalt(rounds=12))` |
| Session tokens | Cryptographically random 32-byte tokens, base64-encoded |
| File encryption | Fernet (AES-128-CBC + HMAC) from `cryptography` library |
| At-rest sensitive data | Encrypted with user-derived keys or system key |
| File permissions | Unix-style `rwx` for owner/group/others mapped to VFS nodes |
| Audit logging | Every login, permission change, file access, and system event logged |
| Rate limiting | Configurable per-endpoint (default 5 failed login attempts / 15 min) |
| Input validation | Pydantic models on all API and CLI inputs |

### 4.4 Key Classes

| Class | Responsibility |
|---|---|
| `AuthService` | Verifies credentials, issues/invalidates sessions, enforces rate limits. |
| `SessionManager` | Creates, validates, refreshes, and revokes sessions. |
| `RoleManager` | Defines roles and resolves permission sets. |
| `PermissionService` | Checks whether a user/session has a required permission. |
| `EncryptionService` | Symmetric encryption/decryption for files and secrets. |
| `AuditLogger` | Writes security and operational events to the `logs` table. |

---

## 5. Virtual File System (VFS)

### 5.1 Overview

BlendiOS provides a **Virtual File System** stored under a configurable host directory (e.g., `~/.blendios/vfs/`). It supports folders, files, metadata, permissions, compression, encryption, trash, and restore.

### 5.2 Folder Structure

```
~/.blendios/vfs/
├── system/
│   ├── apps/                 # Installed app metadata
│   ├── settings/             # Global system settings JSON
│   ├── logs/                 # Rotated log files
│   └── themes/               # Custom themes
│
├── users/
│   ├── admin/
│   │   ├── home/
│   │   │   ├── Documents/
│   │   │   ├── Downloads/
│   │   │   ├── Music/
│   │   │   ├── Pictures/
│   │   │   ├── Videos/
│   │   │   └── Desktop/
│   │   ├── .trash/           # User-specific trash
│   │   └── .config/          # User settings and caches
│   │
│   └── <username>/
│       └── ...
│
└── shared/                   # Shared public folder
```

### 5.3 Operations

| Operation | Description |
|---|---|
| `create_file(path, content)` | Creates a file node with metadata and permissions. |
| `create_folder(path)` | Creates a folder node. |
| `read(path)` | Reads file contents; enforces read permissions. |
| `write(path, content)` | Writes file contents; enforces write permissions. |
| `delete(path)` | Moves node to `.trash/` instead of permanent deletion. |
| `copy(src, dst)` | Copies a node recursively with optional metadata. |
| `move(src, dst)` | Moves/renames a node. |
| `list(path)` | Lists children of a folder. |
| `search(query, filters)` | Fuzzy search by name, type, size, date. |
| `compress(paths, archive_name)` | Creates ZIP/TAR archives. |
| `decompress(archive, dst)` | Extracts archives. |
| `encrypt(path)` | Encrypts file contents using Fernet. |
| `decrypt(path)` | Decrypts file contents if key is available. |
| `trash(path)` | Moves to `.trash/` with original path recorded. |
| `restore(trash_path)` | Restores item to original or chosen path. |
| `empty_trash()` | Permanently deletes trashed items. |

### 5.4 Key Classes

| Class | Responsibility |
|---|---|
| `VirtualFileSystem` | Main API for VFS operations and mount management. |
| `FSNode` | Abstract base for all file system nodes (id, name, parent, permissions, timestamps). |
| `Folder(FSNode)` | Container node with children. |
| `File(FSNode)` | Leaf node with binary content and MIME type. |
| `SearchEngine` | Indexes nodes and supports full-text/fuzzy search. |
| `CompressionService` | ZIP/TAR compression and extraction. |
| `TrashManager` | Moves nodes to trash and manages retention. |
| `RestoreManager` | Restores trashed nodes to original locations. |

---

## 6. Terminal Emulator

### 6.1 Overview

The terminal is both an app (`apps/terminal/`) and a command interpreter (`cli/`). It exposes a shell-like interface inside a PySide6 widget.

### 6.2 Supported Commands

| Command | Description |
|---|---|
| `help [cmd]` | Show command list or detailed help. |
| `ls [-la] [path]` | List directory contents. |
| `cd <path>` | Change current directory. |
| `mkdir <name>` | Create directory. |
| `touch <name>` | Create empty file. |
| `rm [-rf] <path>` | Remove file or folder (moves to trash by default). |
| `cp <src> <dst>` | Copy file/folder. |
| `mv <src> <dst>` | Move/rename file/folder. |
| `tree [path]` | Display directory tree. |
| `grep <pattern> <path>` | Search text within files. |
| `find <path> -name <pattern>` | Find files matching pattern. |
| `whoami` | Display current user. |
| `install <app>` | Install an app from the app store. |
| `update [app]` | Update installed app(s). |
| `shutdown` | Shut down BlendiOS. |
| `reboot` | Restart BlendiOS. |
| `ps` | List running processes. |
| `kill <pid>` | Terminate a process. |
| `top` | Display resource usage. |
| `clear` | Clear terminal screen. |
| `echo <text>` | Print text. |
| `cat <file>` | Display file contents. |
| `chmod <mode> <path>` | Change file permissions. |
| `chown <user> <path>` | Change file owner. |
| `df` | Show disk usage. |
| `free` | Show memory usage. |
| `netstat` | Show active network/API connections. |

### 6.3 Command Parsing Architecture

```
Input String
    │
    ▼
Lexer ──► Tokens
    │
    ▼
Parser ──► Command AST (command, args, flags)
    │
    ▼
Command Router ──► Registered Command Handler
    │
    ▼
Execute via Kernel / VFS / App Store / etc.
    │
    ▼
Output / Error String
```

#### 6.3.1 Components

| Component | Responsibility |
|---|---|
| `Lexer` | Splits raw input into tokens, respecting quotes and escapes. |
| `Parser` | Validates syntax and builds a `CommandInvocation` object. |
| `CommandRegistry` | Maps command names to handler classes/functions. |
| `CommandContext` | Holds current user, working directory, session, and environment variables. |
| `CommandExecutor` | Runs the handler, captures stdout/stderr, and returns the result. |

#### 6.3.2 Extensibility

Plugins can register new terminal commands via the plugin hook `register_commands(registry)`. The terminal dynamically reloads available commands on plugin load/unload.

---

## 7. Applications Layer

### 7.1 App Architecture

All internal apps inherit from `BaseApp` and communicate with the kernel through a well-defined `AppContext`.

```
┌──────────────────────────────────────────────────────────────┐
│                         App                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │ BaseApp     │  │ AppWindow   │  │ AppContext           │ │
│  │ (lifecycle) │  │ (PySide6)   │  │ (kernel, vfs, api)   │ │
│  └──────┬──────┘  └─────────────┘  └──────────────────────┘ │
│         │                                                    │
│         ▼                                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Kernel  ◄──►  VFS  ◄──►  API Client  ◄──►  FastAPI     │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### 7.2 Internal Applications

| App | Responsibility |
|---|---|
| **File Explorer** | Browse VFS, preview files, manage folders, drag-and-drop, context menus. |
| **Terminal** | Command interpreter and shell UI. |
| **Settings** | System and user preferences: display, network, users, themes, security. |
| **Calculator** | Standard and scientific calculator with history. |
| **Notes** | Rich-text notes with save/load, search, and tagging. |
| **Browser** | Lightweight web browser using PySide6 `QWebEngineView` + `requests`/`bs4` helpers. |
| **Media Player** | Audio/video playback with playlist support. |
| **Paint** | Basic raster drawing with brushes, shapes, colors, and save/export. |
| **Task Manager** | View running processes, CPU/RAM usage, start/stop apps/services. |
| **App Store** | Browse, install, update, and uninstall internal apps and plugins. |

### 7.3 App Communication Flow

1. **Launch:** Desktop shell calls `Kernel.launch_app(app_id)`.
2. **Process:** Kernel creates a process entry and invokes `AppRegistry.create_instance(app_id, context)`.
3. **Window:** App creates its main `QWidget` and registers it with `WindowManager`.
4. **Runtime:** App uses `AppContext` to call VFS, send API requests, or publish kernel events.
5. **Termination:** On close, app calls `AppContext.shutdown()`, kernel terminates the process, and the window manager removes the window.

---

## 8. Scheduler & Memory Manager

### 8.1 Scheduler Subsystem

The kernel uses a pluggable scheduler to decide which ready process runs next.

#### 8.1.1 Implemented Algorithms

| Algorithm | Description |
|---|---|
| **FIFO (FCFS)** | First-in-first-out non-preemptive queue. |
| **Round Robin** | Time-sliced preemptive scheduling with configurable quantum. |
| **Priority** | Preemptive/non-preemptive scheduling by priority; lower number = higher priority. |
| **Shortest Job First (SJF)** | Non-preemptive scheduling by estimated burst time. |

#### 8.1.2 Scheduler Class Hierarchy

```
BaseScheduler (abstract)
    ├── FIFOScheduler
    ├── RoundRobinScheduler
    ├── PriorityScheduler
    └── ShortestJobFirstScheduler
```

#### 8.1.3 Key Metrics

Each scheduler reports:

- Average waiting time
- Average turnaround time
- CPU utilization
- Throughput
- Context switches

---

### 8.2 Memory Manager

The memory manager simulates RAM allocation for processes.

#### 8.2.1 Features

- Configurable total RAM (default 4 GB simulated).
- Allocation strategies: first-fit, best-fit, worst-fit.
- Page table simulation with frame allocation.
- Memory usage monitoring per process.
- Swap file simulation when RAM is exhausted.
- Garbage collection of terminated process memory.

#### 8.2.2 Key Classes

| Class | Responsibility |
|---|---|
| `MemoryManager` | Tracks total, used, and free memory. |
| `Allocator` | Implements allocation strategies and defragmentation. |
| `RAMMonitor` | Streams memory statistics to the UI/dashboard. |
| `PageTable` | Simulates virtual-to-physical page mapping. |
| `MemoryBlock` | Represents an allocated or free memory region. |

---

## 9. FastAPI Backend

### 9.1 Overview

The FastAPI backend exposes BlendiOS services over HTTP. It is used by:

- Internal apps (REST client).
- The Streamlit dashboard.
- External scripts and CI/CD.
- Future mobile/web companion interfaces.

### 9.2 Base URL

```
http://localhost:8000/api/v1
```

### 9.3 Authentication

OAuth2 Password Bearer flow:

```
POST /api/v1/auth/login   → access_token + refresh_token
POST /api/v1/auth/refresh → new access_token
POST /api/v1/auth/logout  → revoke token
```

### 9.4 Endpoint Reference

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/auth/login` | Authenticate and receive tokens. | No |
| POST | `/auth/logout` | Invalidate session/token. | Yes |
| POST | `/auth/register` | Register a new user (Admin only). | Yes |
| GET | `/users` | List users. | Admin |
| GET | `/users/me` | Current user profile. | Yes |
| GET | `/users/{id}` | Get user details. | Admin |
| PUT | `/users/{id}` | Update user. | Admin/Self |
| DELETE | `/users/{id}` | Delete user. | Admin |
| GET | `/files` | List files in a directory. | Yes |
| POST | `/files` | Create a file. | Yes |
| GET | `/files/{path}` | Read file metadata/content. | Yes |
| PUT | `/files/{path}` | Update file content. | Yes |
| DELETE | `/files/{path}` | Move file to trash. | Yes |
| POST | `/files/search` | Search files. | Yes |
| POST | `/files/compress` | Compress files. | Yes |
| POST | `/files/decompress` | Decompress archive. | Yes |
| GET | `/apps` | List installed apps. | Yes |
| POST | `/apps/{id}/launch` | Launch an app. | Yes |
| DELETE | `/apps/{id}` | Uninstall app. | Admin |
| GET | `/processes` | List running processes. | Yes |
| GET | `/processes/{pid}` | Process details. | Yes |
| POST | `/processes/{pid}/kill` | Kill a process. | Admin/Owner |
| GET | `/settings` | Get settings. | Yes |
| PUT | `/settings` | Update settings. | Yes/Admin |
| GET | `/logs` | Query system logs. | Admin |
| GET | `/system/status` | CPU/RAM/storage status. | Yes |
| POST | `/system/shutdown` | Shutdown BlendiOS. | Admin |

### 9.5 Architecture

```
FastAPI App
    ├── dependencies.py   # DB session, current user, permissions
    ├── security.py       # Token creation/validation
    └── routers/
        ├── auth.py
        ├── users.py
        ├── files.py
        ├── apps.py
        ├── processes.py
        ├── settings.py
        └── logs.py
```

---

## 10. SQLite Database Design

### 10.1 Schema Overview

BlendiOS uses a single SQLite database (`~/.blendos/system/blendios.db`) with the following tables:

- `users`
- `sessions`
- `files`
- `folders`
- `settings`
- `processes`
- `logs`
- `installed_apps`
- `themes`

### 10.2 Schema SQL

See `docs/Database_Schema.sql` for the complete, executable schema including indexes and foreign keys.

### 10.3 Key Tables Summary

| Table | Purpose |
|---|---|
| `users` | User accounts with hashed passwords, roles, and status. |
| `sessions` | Active and expired login sessions/tokens. |
| `files` | Virtual file metadata, content reference, owner, permissions. |
| `folders` | Virtual folder metadata and hierarchy. |
| `settings` | Key-value system and user settings. |
| `processes` | Running and historical process records. |
| `logs` | Audit and system event logs. |
| `installed_apps` | Installed applications and plugins. |
| `themes` | Installed theme definitions. |

---

## 11. Streamlit Dashboard

### 11.1 Overview

The Streamlit dashboard (`dashboards/streamlit_dashboard.py`) provides real-time and historical analytics about BlendiOS.

### 11.2 Dashboard Pages

| Page | Widgets |
|---|---|
| **Overview** | CPU/RAM/storage gauges, active users, uptime. |
| **Performance** | Time-series CPU and RAM graphs (Plotly/Matplotlib). |
| **Storage** | Storage breakdown by user/folder/type. |
| **Users** | Active users table, login statistics, session list. |
| **Apps** | Installed apps grid, launch counts, version info. |
| **Logs** | Filterable log viewer with severity colors. |
| **Security** | Failed login attempts, permission changes, audit trail. |

### 11.3 Data Flow

```
Streamlit Dashboard
    │
    ▼
FastAPI REST API
    │
    ▼
Kernel / Database / VFS
```

The dashboard polls the `/system/status`, `/processes`, `/users`, and `/logs` endpoints every few seconds to refresh graphs.

---

## 12. Plugin System

### 12.1 Overview

BlendiOS supports dynamic plugins loaded at runtime from `~/.blendios/plugins/` or installed via the App Store. Plugins can extend apps, widgets, terminal commands, and themes.

### 12.2 Plugin Structure

```
MyPlugin/
├── plugin.json          # Metadata: id, name, version, author, entrypoints
├── __init__.py
├── app.py               # Optional: app implementation
├── widget.py            # Optional: widget implementation
├── commands.py          # Optional: terminal commands
└── theme/
    └── my_theme.json
```

### 12.3 Extension Points

| Extension Point | Hook |
|---|---|
| Apps | `register_apps(registry)` |
| Widgets | `register_widgets(registry)` |
| Terminal Commands | `register_commands(registry)` |
| Themes | `register_themes(registry)` |
| Services | `register_services(manager)` |
| API Routes | `register_routers(app)` |

### 12.4 Security

- Plugins are loaded in a restricted sandbox.
- Import of unsafe modules (`os.system`, `subprocess`, etc.) is audited.
- Plugin signatures/ checksums are verified before loading (optional).
- Plugins run with the permissions of the installing user.

### 12.5 Key Classes

| Class | Responsibility |
|---|---|
| `PluginLoader` | Discovers, validates, and imports plugins. |
| `PluginRegistry` | Maintains the list of active plugins and their hooks. |
| `PluginSandbox` | Restricted execution environment for plugin code. |
| `IPlugin` | Abstract interface all plugins must implement. |

---

## 13. Themes System

### 13.1 Overview

The theme engine provides a centralized way to style all PySide6 widgets. Themes are JSON files defining colors, fonts, spacing, and border radii.

### 13.2 Built-in Themes

| Theme | Description |
|---|---|
| **Dark** | Default dark mode with high contrast. |
| **Light** | Clean light mode. |
| **Blue** | Dark blue accent palette. |
| **Green** | Nature-inspired green accent palette. |
| **Purple** | Vibrant purple accent palette. |
| **High Contrast** | Accessibility-focused theme. |

### 13.3 Theme File Format

```json
{
  "id": "dark",
  "name": "Dark",
  "palette": {
    "window": "#1e1e1e",
    "window_text": "#ffffff",
    "base": "#252526",
    "alternate_base": "#2d2d30",
    "accent": "#0078d4",
    "button": "#3c3c3c",
    "button_text": "#ffffff",
    "border": "#5a5a5a",
    "error": "#f44336",
    "warning": "#ff9800",
    "success": "#4caf50"
  },
  "fonts": {
    "default": {"family": "Segoe UI", "size": 10},
    "monospace": {"family": "Consolas", "size": 10}
  },
  "spacing": {
    "small": 4,
    "medium": 8,
    "large": 16
  }
}
```

### 13.4 Theme Engine Architecture

| Component | Responsibility |
|---|---|
| `ThemeEngine` | Loads active theme, applies it globally, and notifies widgets. |
| `ThemeLoader` | Reads theme JSON files and validates against schema. |
| `Palette` | Converts theme JSON into PySide6 `QPalette`. |
| `StyleSheetBuilder` | Generates QSS from theme definitions. |

---

## 14. Development Roadmap

### Phase 1 — Login + Desktop Shell

**Duration:** 4–6 weeks  
**Deliverables:**

- Project scaffolding and CI/CD.
- SQLite schema and repositories.
- User authentication and session management.
- Basic PySide6 desktop shell (wallpaper + taskbar).
- Theme engine with Dark/Light themes.

### Phase 2 — File Explorer + Terminal

**Duration:** 4–6 weeks  
**Deliverables:**

- Virtual file system with CRUD, permissions, trash, and restore.
- File Explorer app.
- Terminal emulator with core commands.
- Command parser and registry.

### Phase 3 — Users + Security Hardening

**Duration:** 3–4 weeks  
**Deliverables:**

- Roles (Admin, User, Guest) and permissions.
- File encryption and bcrypt password hashing.
- Audit logging and security event log.
- Session expiration and rate limiting.

### Phase 4 — Task Manager + Scheduler + Memory

**Duration:** 4–6 weeks  
**Deliverables:**

- Process manager and service manager.
- Four scheduling algorithms.
- Simulated memory manager with allocation strategies.
- Task Manager app.
- Notifications and crash handler.

### Phase 5 — Applications Expansion

**Duration:** 6–8 weeks  
**Deliverables:**

- Settings, Calculator, Notes apps.
- Browser, Media Player, Paint apps.
- App Store and app installer.
- Widget engine (clock, CPU/RAM meters).
- Global search and virtual desktops.

### Phase 6 — FastAPI + Streamlit Dashboard

**Duration:** 4–6 weeks  
**Deliverables:**

- FastAPI backend with all routers.
- OAuth2 authentication and permissions.
- REST API client in apps.
- Streamlit dashboard with real-time graphs.

### Phase 7 — Plugins + Optimization + Testing

**Duration:** 4–6 weeks  
**Deliverables:**

- Dynamic plugin loader and sandbox.
- Plugin extension points (apps, widgets, commands, themes).
- Comprehensive unit, integration, and E2E tests.
- Performance optimization and profiling.
- Final documentation and release packaging.

### 14.1 Total Estimated Timeline

| Phase | Weeks | Cumulative |
|---|---|---|
| Phase 1 | 4–6 | 4–6 |
| Phase 2 | 4–6 | 8–12 |
| Phase 3 | 3–4 | 11–16 |
| Phase 4 | 4–6 | 15–22 |
| Phase 5 | 6–8 | 21–30 |
| Phase 6 | 4–6 | 25–36 |
| Phase 7 | 4–6 | 29–42 |

**Total:** approximately **7–10 months** for a small team of 2–4 engineers, or **6–12 months** with documentation and polish.

---

## 15. Engineering Standards

### 15.1 Code Quality

- **Type hints** throughout (`typing`, `Pydantic`).
- **Docstrings** for all public modules, classes, and methods (Google style).
- **Linting:** `ruff`, `mypy`, `black`.
- **Testing:** `pytest` with fixtures, mocks, and parametrized tests.
- **Logging:** `structlog` or standard `logging` with structured JSON logs.

### 15.2 Dependency Rules

- `kernel/` may depend on `common/`, `database/`, `users/`.
- `desktop/` may depend on `kernel/`, `window_manager/`, `themes/`, `common/`.
- `apps/` may depend on `kernel/`, `filesystem/`, `api/`, `themes/`, `common/`.
- `api/` may depend on `kernel/`, `users/`, `filesystem/`, `database/`, `common/`.
- No circular dependencies; enforced by `importlinter` or custom checks.

### 15.3 Configuration Management

All environment-specific values use `python-dotenv` and `pydantic-settings`:

```bash
# .env
BLENDIOS_DB_PATH=~/.blendios/system/blendios.db
BLENDIOS_VFS_PATH=~/.blendios/vfs
BLENDIOS_API_HOST=127.0.0.1
BLENDIOS_API_PORT=8000
BLENDIOS_SECRET_KEY=change-me-in-production
BLENDIOS_BCRYPT_ROUNDS=12
BLENDIOS_LOG_LEVEL=INFO
```

---

## 16. Conclusion

BlendiOS is an ambitious but achievable Python project that demonstrates enterprise-grade software architecture through the lens of a desktop operating environment. By following the modular, layered design in this specification, the project can scale to 20,000–50,000+ lines while remaining maintainable, testable, and educational.

This master specification serves as the living blueprint for all implementation, testing, and documentation efforts.

---

**Document Owner:** BlendiOS Architecture Team  
**Next Review Date:** 2026-08-02  
**Approval:** [Pending]
