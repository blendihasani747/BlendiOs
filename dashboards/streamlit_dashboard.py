"""Streamlit monitoring dashboard for BlendiOS."""

from __future__ import annotations

import time
from datetime import datetime

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_BASE = "http://localhost:8000/api/v1"


def fetch_status(token: str) -> dict:
    """Fetch system status from the FastAPI backend."""
    try:
        response = requests.get(
            f"{API_BASE}/system/status",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(f"Failed to fetch status: {exc}")
        return {}


def fetch_processes(token: str) -> list[dict]:
    """Fetch running processes."""
    try:
        response = requests.get(
            f"{API_BASE}/processes",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []


def fetch_logs(token: str, limit: int = 100) -> list[dict]:
    """Fetch recent logs."""
    try:
        response = requests.get(
            f"{API_BASE}/logs",
            headers={"Authorization": f"Bearer {token}"},
            params={"limit": limit},
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []


def render_overview(status: dict) -> None:
    """Render overview KPIs."""
    st.header("System Overview")
    cols = st.columns(4)
    cols[0].metric("CPU %", f"{status.get('cpu_percent', 0):.1f}%")
    cols[1].metric("RAM Used", f"{status.get('memory_used_mb', 0)} MB")
    cols[2].metric("Processes", status.get("process_count", 0))
    cols[3].metric("Active Users", status.get("active_user_count", 0))


def render_memory_chart(status: dict) -> None:
    """Render a donut chart for memory usage."""
    st.subheader("Memory Usage")
    labels = ["Used", "Free"]
    values = [status.get("memory_used_mb", 0), status.get("memory_free_mb", 0)]
    fig = px.pie(names=labels, values=values, hole=0.4)
    st.plotly_chart(fig, use_container_width=True)


def render_process_table(processes: list[dict]) -> None:
    """Render running processes as a table."""
    st.subheader("Running Processes")
    if not processes:
        st.info("No processes available")
        return
    df = pd.DataFrame(processes)
    st.dataframe(df, use_container_width=True)


def render_logs(logs: list[dict]) -> None:
    """Render recent logs."""
    st.subheader("Recent Logs")
    if not logs:
        st.info("No logs available")
        return
    df = pd.DataFrame(logs)
    st.dataframe(df, use_container_width=True)


def main() -> None:
    """Main Streamlit entry point."""
    st.set_page_config(page_title="BlendiOS Dashboard", layout="wide")
    st.title("BlendiOS Monitoring Dashboard")
    st.caption(f"Last updated: {datetime.utcnow().isoformat()} UTC")

    token = st.sidebar.text_input("API Token", type="password")
    if not token:
        st.warning("Please enter a valid API token in the sidebar.")
        return

    auto_refresh = st.sidebar.checkbox("Auto-refresh every 5 seconds", value=True)

    status = fetch_status(token)
    processes = fetch_processes(token)
    logs = fetch_logs(token)

    render_overview(status)

    col1, col2 = st.columns(2)
    with col1:
        render_memory_chart(status)
    with col2:
        render_process_table(processes)

    render_logs(logs)

    if auto_refresh:
        time.sleep(5)
        st.rerun()


if __name__ == "__main__":
    main()
