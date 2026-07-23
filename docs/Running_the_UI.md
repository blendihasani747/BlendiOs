# BlendiOS — Running the Desktop UI

This guide explains how to launch the actual BlendiOS desktop environment (the PySide6 GUI).

> **⚠️ Important:** BlendiOS runs as a Python application on top of your existing OS. It is **not** a bootable kernel.

---

## Requirements

- Python 3.11+
- Dependencies installed from `pyproject.toml`
- A display / desktop session (not a headless server without X11/VNC)

---

## 1. Install Dependencies

From the project root:

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

---

## 2. Configure Environment

```bash
cp .env.example .env        # macOS / Linux
copy .env.example .env      # Windows
```

Edit `.env` and set a secret key:

```env
BLENDIOS_SECRET_KEY=your-random-secret-key
```

---

## 3. Initialize the Database

```bash
python scripts/seed_db.py
```

---

## 4. Launch the BlendiOS Desktop UI

This is the main command. It opens the full-screen desktop with taskbar, start menu, and apps.

```bash
python -m blendios
```

You will see:

- A full-screen **blue desktop**
- A **taskbar** at the bottom with the BlendiOS start button and clock
- Click **"BlendiOS"** to open the **Start Menu**
- Click **Terminal** or **Calculator** to launch an app
- Drag app windows by their title bar
- Use the **Shutdown** button in the Start Menu to exit

---

## 5. Optional: Run the API Server

In a second terminal:

```bash
source .venv/bin/activate
uvicorn blendios.api.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

---

## 6. Optional: Run the Streamlit Dashboard

In a third terminal:

```bash
source .venv/bin/activate
streamlit run dashboards/streamlit_dashboard.py
```

---

## What Is Implemented?

The current UI includes:

- ✅ Full-screen desktop shell
- ✅ Taskbar with Start button, app launchers, clock
- ✅ Start menu with installed apps list
- ✅ Window manager with draggable, resizable, closable windows
- ✅ Terminal app with working commands (`help`, `echo`, `whoami`, `date`, `uname`, `ps`, `clear`)
- ✅ Calculator app with basic arithmetic
- ✅ Kernel bootstrap and process creation on app launch

More apps and features will be added in later phases.

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'PySide6'`

Install dependencies:

```bash
pip install -e ".[dev]"
```

### `Could not initialize GLX / Platform plugin could not be loaded`

You are running on a headless system without a display. Either:

- Run BlendiOS on a machine with a desktop environment.
- Use a remote desktop / VNC.
- On Linux, use `xvfb-run` for testing:

```bash
xvfb-run python -m blendios
```

### App window does not appear

Check the terminal output for errors. Make sure the database is seeded and the virtual environment is activated.

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| Click Start button | Open Start Menu |
| Drag title bar | Move window |
| Click window | Focus window |
| Click ✕ on title bar | Close window |
| Shutdown button | Exit BlendiOS |
