"""Server Health & Metrics API.

Run it with:
    uvicorn app.main:app --reload
"""

from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI, HTTPException

from app import system_info

# The only units we accept. FastAPI rejects anything else with a 422 error.
SizeUnit = Literal["B", "KB", "MB", "GB"]

AVAILABLE_METRICS = ["system", "cpu", "memory", "disk"]

app = FastAPI(
    title="Server Health & Metrics API",
    description="A small API that reports the health and resource usage of the server it runs on.",
    version="1.0.0",
)


@app.get("/")
def root():
    """Welcome message and a list of the endpoints you can call."""
    return {
        "message": "Welcome to the Server Health & Metrics API",
        "docs": "/docs",
        "endpoints": ["/health", "/metrics"] + [f"/metrics/{name}" for name in AVAILABLE_METRICS],
    }


@app.get("/health")
def health():
    """Liveness check. If this answers, the service is up."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/metrics")
def all_metrics(unit: SizeUnit = "GB"):
    """Every metric in one response."""
    return {
        "system": system_info.get_system_info(),
        "cpu": system_info.get_cpu_info(),
        "memory": system_info.get_memory_info(unit),
        "disk": system_info.get_disk_info(system_info.default_disk_path(), unit),
    }


@app.get("/metrics/system")
def system_metrics():
    """Hostname, operating system, Python version and uptime."""
    return system_info.get_system_info()


@app.get("/metrics/cpu")
def cpu_metrics():
    """CPU usage percentage and core counts."""
    return system_info.get_cpu_info()


@app.get("/metrics/memory")
def memory_metrics(unit: SizeUnit = "GB"):
    """RAM usage. Example: /metrics/memory?unit=MB"""
    return system_info.get_memory_info(unit)


@app.get("/metrics/disk")
def disk_metrics(path: str | None = None, unit: SizeUnit = "GB"):
    """Disk usage. Example: /metrics/disk?path=D:\\&unit=GB"""
    if path is None:
        path = system_info.default_disk_path()
    try:
        return system_info.get_disk_info(path, unit)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Path not found: {path}")


# This catch-all route MUST stay last, or it would swallow the routes above.
@app.get("/metrics/{metric_name}")
def unknown_metric(metric_name: str):
    """Catches any metric name not matched above and returns a helpful 404."""
    raise HTTPException(
        status_code=404,
        detail=f"Unknown metric '{metric_name}'. Available metrics: {AVAILABLE_METRICS}",
    )
