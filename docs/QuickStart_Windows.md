# BlendiOS — Quick Start Guide for Windows

This guide walks you through setting up BlendiOS on **Windows 10/11** using **PowerShell** (recommended) or Command Prompt (`cmd.exe`).

> **⚠️ Important:** BlendiOS is a desktop environment built in Python that runs on top of Windows. It is **not** a bootable operating system kernel.

---

## ✅ Prerequisites

1. **Python 3.11 or newer** installed and added to your system `PATH`.
   - Download from [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
   - During installation, check **"Add Python to PATH"**.
2. **Git for Windows** (optional, for cloning).
   - Download from [https://git-scm.com/download/win](https://git-scm.com/download/win)
3. A C++ compiler may be required for some native packages (e.g., PySide6 usually provides wheels, but if you build packages from source, install **Microsoft C++ Build Tools**).

---

## 1. Open PowerShell

Press `Win + X` and select **Terminal (Admin)** or **Windows PowerShell**.

> If PowerShell scripts fail later, you may need to allow script execution:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Choose **Y** when prompted.

---

## 2. Navigate to the BlendiOS Folder

If you cloned or extracted BlendiOS to `C:\Projects\BlendiOS`, run:

```powershell
cd C:\Projects\BlendiOS
```

---

## 3. Create a Virtual Environment

```powershell
python -m venv .venv
```

This creates a local Python environment inside the project folder.

---

## 4. Activate the Virtual Environment

### PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Command Prompt (cmd.exe)

```cmd
.venv\Scripts\activate.bat
```

When activated, your prompt will show `(.venv)` at the beginning.

To deactivate later, run:

```powershell
deactivate
```

---

## 5. Install Dependencies

With the virtual environment active, install BlendiOS in editable mode:

```powershell
pip install -e ".[dev]"
```

This installs all runtime and development dependencies listed in `pyproject.toml`.

> This step may take a few minutes because of PySide6, Pandas, NumPy, and Plotly.

---

## 6. Configure Environment Variables

Copy the example environment file:

### PowerShell

```powershell
copy .env.example .env
```

### Command Prompt

```cmd
copy .env.example .env
```

Edit `.env` with Notepad or your preferred editor. At minimum, change:

```env
BLENDIOS_SECRET_KEY=your-very-long-random-secret-key-here
```

Generate a secure key with:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Then paste the output into `.env`.

---

## 7. Initialize the SQLite Database

Run the database seed script:

```powershell
python scripts\seed_db.py
```

You should see output like:

```text
Database initialized at: C:\Users\<YourName>\.blendios\system\blendios.db
```

---

## 8. Run the BlendiOS Desktop UI

This is the main command — it opens the actual OS desktop environment:

```powershell
python -m blendios
```

You should see:

- A full-screen **blue desktop**
- A **taskbar** at the bottom with the BlendiOS start button and clock
- Click **"BlendiOS"** to open the **Start Menu**
- Launch **Terminal** or **Calculator** from the Start Menu or taskbar
- Drag windows by their title bar, close them with the ✕ button
- Use the **Shutdown** button in the Start Menu to exit

For more details, see [`Running_the_UI.md`](Running_the_UI.md).

---

## 9. Run the FastAPI Backend (Optional)

In a **second terminal window**, activate the virtual environment and run:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn blendios.api.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000/api/v1
```

Open the interactive docs at:

```text
http://127.0.0.1:8000/docs
```

---

## 10. Run the Streamlit Dashboard (Optional)

In a **third terminal window**, activate the virtual environment and run:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run dashboards\streamlit_dashboard.py
```

Streamlit will open automatically in your default browser.

---

## 11. Run Tests

```powershell
pytest tests\ -q
```

To run with coverage:

```powershell
pytest tests\ -q --cov=src\blendios --cov-report=term-missing
```

---

## 12. Useful Windows Commands

| Task | Command |
|---|---|
| Format code | `black src tests dashboards` |
| Lint code | `ruff check src tests dashboards` |
| Type check | `mypy src` |
| Seed database | `python scripts\seed_db.py` |
| Run desktop | `python -m blendios` |
| Run API | `uvicorn blendios.api.main:app --reload` |
| Run dashboard | `streamlit run dashboards\streamlit_dashboard.py` |

---

## 🛠️ Troubleshooting

### "Running scripts is disabled on this system"

Run PowerShell as Administrator or set the execution policy for your user:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Python was not found"

Reinstall Python and make sure **"Add Python to PATH"** is checked, or use the Python Launcher:

```powershell
py -3.11 -m venv .venv
```

### PySide6 / Qt platform errors

Make sure you are running BlendiOS on a machine with a display (not over SSH without X forwarding). On Windows, this should work normally.

### SQLite database is locked

Close any open database viewers and ensure only one BlendiOS process is accessing `~\.blendios\system\blendios.db`.

---

## 📚 Next Steps

- Read the full specification: [`docs/BlendiOS_Master_Specification.md`](BlendiOS_Master_Specification.md)
- Explore the architecture: [`docs/Architecture_Diagram.md`](Architecture_Diagram.md)
- Review the API: [`docs/API_Specification.md`](API_Specification.md)
- Inspect the database schema: [`docs/Database_Schema.sql`](Database_Schema.sql)
