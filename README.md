<<<<<<< HEAD
# BlendiOs
=======
# BlendiOS

A large-scale, Python-based desktop operating system **environment** built with PySide6, FastAPI, Streamlit, and SQLite.

> **⚠️ Important:** BlendiOS is **not** a real bootable OS kernel. It is a desktop environment and OS simulation layer that runs on top of an existing host operating system (Linux, macOS, or Windows).

---

## 🎯 Vision

BlendiOS demonstrates how a desktop operating environment can be modeled entirely in Python. It bridges academic operating-system theory with modern application development by providing a modular, testable, and extensible architecture.

## 🏗️ Architecture Highlights

- **Kernel simulation:** process manager, scheduler, memory manager, service manager, crash handler.
- **Desktop shell:** taskbar, start menu, notifications, widgets, global search, virtual desktops.
- **Window manager:** move, resize, snap, z-order, animations.
- **Virtual file system:** CRUD, search, compression, encryption, trash, restore.
- **User & security:** bcrypt password hashing, sessions, RBAC, permissions, audit logs.
- **Terminal emulator:** command interpreter with extensible command registry.
- **Internal apps:** File Explorer, Terminal, Settings, Calculator, Notes, Browser, Media Player, Paint, Task Manager, App Store.
- **FastAPI backend:** RESTful API for apps, dashboard, and external clients.
- **Streamlit dashboard:** real-time CPU/RAM/storage graphs, user analytics, logs.
- **Plugin system:** dynamic loading of apps, widgets, commands, and themes.
- **Theme engine:** dark, light, blue, green, purple, high contrast, and custom themes.

## 📁 Project Structure

See [`docs/BlendiOS_Master_Specification.md`](docs/BlendiOS_Master_Specification.md) for the complete architecture and module responsibility matrix.

```
BlendiOS/
├── docs/                  # Architecture, API, and database documentation
├── src/blendios/          # Main Python package
├── tests/                 # Unit, integration, and E2E tests
├── dashboards/            # Streamlit monitoring dashboard
└── scripts/               # Setup and automation scripts
```

### Windows Quick Start

For Windows-specific instructions (PowerShell and Command Prompt), see [`docs/QuickStart_Windows.md`](docs/QuickStart_Windows.md).

You can also run the automated setup script:

```powershell
# PowerShell
.\scripts\setup_dev_windows.ps1
```

```cmd
:: Command Prompt
scripts\setup_dev_windows.bat
```

## 🚀 Quick Start (macOS / Linux)

### 1. Clone and create a virtual environment

```bash
cd BlendiOS
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -e ".[dev]"
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

### 4. Initialize the database

```bash
python scripts/seed_db.py
```

### 5. Run the BlendiOS desktop UI

```bash
python -m blendios
```

This opens the full-screen desktop environment with taskbar, start menu, and apps.
For detailed UI launch instructions and troubleshooting, see [`docs/Running_the_UI.md`](docs/Running_the_UI.md).

### 6. Run the FastAPI backend (optional)

```bash
uvicorn blendios.api.main:app --reload
```

### 7. Run the Streamlit dashboard (optional)

```bash
streamlit run dashboards/streamlit_dashboard.py
```

## 🧪 Running Tests

```bash
pytest tests/ -q
```

## 🛠️ Tech Stack

- Python 3.11+
- PySide6 (GUI)
- FastAPI (REST backend)
- Streamlit (dashboard)
- SQLite (persistence)
- Pydantic (data validation)
- Pandas / NumPy / Plotly / Matplotlib (analytics)
- Requests / BeautifulSoup (browser/network tools)
- bcrypt (password hashing)
- python-dotenv (configuration)

## 📄 Documentation

- [Master Specification](docs/BlendiOS_Master_Specification.md)
- [Architecture Diagrams](docs/Architecture_Diagram.md)
- [API Specification](docs/API_Specification.md)
- [Database Schema](docs/Database_Schema.sql)
- [Running the Desktop UI](docs/Running_the_UI.md)
- [Windows Quick Start](docs/QuickStart_Windows.md)

## 📜 License

MIT License.

## 🤝 Contributing

Contributions are welcome. Please open an issue or pull request and follow the engineering standards described in the master specification.
>>>>>>> 054469b (Initial commit)
