# BlendiOS — Windows Development Setup Script
# Run this script in PowerShell from the project root directory.
# Example: .\scripts\setup_dev_windows.ps1

param(
    [switch]$SkipVenvCreate,
    [switch]$SkipDbSeed
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Test-CommandExists {
    param([string]$Command)
    return [bool](Get-Command $Command -ErrorAction SilentlyContinue)
}

# -----------------------------------------------------------------------------
# Verify Python
# -----------------------------------------------------------------------------
Write-Step "Checking Python installation..."
if (-not (Test-CommandExists "python")) {
    Write-Error "Python was not found. Please install Python 3.11+ and add it to your PATH."
    exit 1
}

$pythonVersion = python --version 2>&1
Write-Host "Found: $pythonVersion"

# -----------------------------------------------------------------------------
# Create virtual environment
# -----------------------------------------------------------------------------
if (-not $SkipVenvCreate) {
    Write-Step "Creating virtual environment..."
    if (Test-Path ".venv") {
        Write-Host "Virtual environment already exists. Skipping creation."
    } else {
        python -m venv .venv
        Write-Host "Virtual environment created at .\venv"
    }
}

# -----------------------------------------------------------------------------
# Activate virtual environment
# -----------------------------------------------------------------------------
Write-Step "Activating virtual environment..."
$venvActivate = ".\.venv\Scripts\Activate.ps1"
if (-not (Test-Path $venvActivate)) {
    Write-Error "Virtual environment activation script not found at $venvActivate"
    exit 1
}
& $venvActivate

# -----------------------------------------------------------------------------
# Upgrade pip and install dependencies
# -----------------------------------------------------------------------------
Write-Step "Upgrading pip..."
python -m pip install --upgrade pip

Write-Step "Installing BlendiOS and dependencies..."
pip install -e ".[dev]"

# -----------------------------------------------------------------------------
# Configure environment file
# -----------------------------------------------------------------------------
Write-Step "Configuring environment..."
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example"

    $secretKey = python -c "import secrets; print(secrets.token_hex(32))"
    $envContent = Get-Content ".env" -Raw
    $envContent = $envContent -replace "BLENDIOS_SECRET_KEY=change-me-in-production", "BLENDIOS_SECRET_KEY=$secretKey"
    Set-Content ".env" $envContent -NoNewline
    Write-Host "Generated a random BLENDIOS_SECRET_KEY in .env"
} else {
    Write-Host ".env already exists. Skipping."
}

# -----------------------------------------------------------------------------
# Seed database
# -----------------------------------------------------------------------------
if (-not $SkipDbSeed) {
    Write-Step "Initializing SQLite database..."
    python scripts\seed_db.py
}

# -----------------------------------------------------------------------------
# Done
# -----------------------------------------------------------------------------
Write-Step "Setup complete!"
Write-Host "You can now run BlendiOS with the following commands:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  python -m blendios"
Write-Host ""
Write-Host "To run the API server:"
Write-Host "  uvicorn blendios.api.main:app --reload"
Write-Host ""
Write-Host "To run the Streamlit dashboard:"
Write-Host "  streamlit run dashboards\streamlit_dashboard.py"
