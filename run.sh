#!/usr/bin/env bash
# Quick launcher for BlendiOS desktop UI on macOS / Linux

set -e

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Run: python3 -m venv .venv && source .venv/bin/activate && pip install -e \".[dev]\""
    exit 1
fi

source .venv/bin/activate
python -m blendios
