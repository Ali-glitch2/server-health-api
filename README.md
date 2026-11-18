# Server Health & Metrics API

A lightweight REST API built with **FastAPI** that reports the health and resource usage of the machine it runs on: CPU, memory, disk, network and uptime.

It works like a minimal version of monitoring agents such as Prometheus Node Exporter. Its `/health` endpoint follows the pattern used by Kubernetes liveness probes, load balancer health checks and Docker `HEALTHCHECK`.

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.165-009688?logo=fastapi&logoColor=white)

---

## Features

- **Health check** endpoint that reports `ok` or `degraded` based on memory pressure
- **System metrics**: hostname, OS, architecture, Python version, uptime
- **CPU, memory, disk and network** usage via [`psutil`](https://github.com/giampaolo/psutil)
- **Unit conversion** (`B`, `KB`, `MB`, `GB`) through query parameters
- **Input validation**: invalid values return a clear `422` error
- **Error handling**: unknown metrics and missing disk paths return `404` with a helpful message
- **Interactive API docs** generated automatically at `/docs` (Swagger UI) and `/redoc`
- **Cross-platform**: runs on Windows, Linux and macOS

## API endpoints

| Method | Endpoint | Description | Query parameters |
|--------|----------|-------------|------------------|
| GET | `/` | Welcome message and endpoint list | – |
| GET | `/health` | Service health (`ok` / `degraded`) | – |
| GET | `/metrics` | All metrics in one response | `unit` (default `GB`) |
| GET | `/metrics/system` | Hostname, OS, Python version, uptime | – |
| GET | `/metrics/cpu` | CPU usage % and core counts | – |
| GET | `/metrics/memory` | RAM total / used / available | `unit` (default `GB`) |
| GET | `/metrics/disk` | Disk usage for a drive | `path`, `unit` (default `GB`) |
| GET | `/metrics/network` | Bytes/packets sent and received, errors, drops | `unit` (default `MB`) |

### Example responses

`GET /health`
```json
{
  "status": "ok",
  "timestamp": "2026-11-18T21:10:25.430668+00:00",
  "checks": {
    "memory_usage_percent": 81.6,
    "memory_threshold_percent": 90.0
  }
}
```

`GET /metrics/memory?unit=MB`
```json
{
  "unit": "MB",
  "total": 16002.46,
  "used": 13934.84,
  "available": 2067.62,
  "usage_percent": 87.1
}
```

`GET /metrics/gpu` → **404**
```json
{
  "detail": "Unknown metric 'gpu'. Available metrics: ['system', 'cpu', 'memory', 'disk', 'network']"
}
```

## Project structure

```
server-health-api/
├── app/
│   ├── __init__.py       # Marks "app" as a Python package
│   ├── main.py           # FastAPI app: routes, validation, HTTP errors
│   └── system_info.py    # Collects system data with psutil (no web logic)
├── requirements.txt      # Pinned dependencies
├── .gitignore
└── README.md
```

The API layer (`main.py`) is kept separate from the data-collection layer (`system_info.py`), so each part can be changed or reused on its own.

## Getting started

### Prerequisites
- Python 3.10 or newer
- Git

### Installation

```bash
git clone https://github.com/Ali-glitch2/server-health-api.git
cd server-health-api

# Create and activate a virtual environment
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run the server

```bash
uvicorn app.main:app --reload
```

The API is now available at **http://127.0.0.1:8000**.

| URL | What you get |
|-----|--------------|
| http://127.0.0.1:8000/docs | Interactive Swagger UI |
| http://127.0.0.1:8000/redoc | ReDoc documentation |

## Testing with curl

```bash
curl http://127.0.0.1:8000/health
curl "http://127.0.0.1:8000/metrics/memory?unit=MB"
curl "http://127.0.0.1:8000/metrics/network?unit=GB"
curl -i http://127.0.0.1:8000/metrics/gpu          # 404 example
curl "http://127.0.0.1:8000/metrics/memory?unit=TB" # 422 validation example
```

> On Windows PowerShell, use `curl.exe` instead of `curl`.

## Configuration

| Setting | Location | Default | Purpose |
|---------|----------|---------|---------|
| `MEMORY_DEGRADED_THRESHOLD` | `app/main.py` | `90.0` | RAM usage % above which `/health` reports `degraded` |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Activate.ps1 cannot be loaded because running scripts is disabled` | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `uvicorn is not recognized` | Activate the virtual environment, or use `python -m uvicorn app.main:app --reload` |
| `ModuleNotFoundError: No module named 'app'` | Run the command from the project root folder |
| `address already in use` | Another process is using port 8000. Use `--port 8001` |

## Tech stack

- **[FastAPI](https://fastapi.tiangolo.com/)**: web framework with automatic validation and docs
- **[Uvicorn](https://www.uvicorn.org/)**: ASGI server
- **[psutil](https://github.com/giampaolo/psutil)**: cross-platform system and process utilities

## Roadmap

- [ ] Automated tests with `pytest`
- [ ] Dockerfile and container `HEALTHCHECK`
- [ ] Prometheus-format `/metrics` output
- [ ] Configuration via environment variables

## What I learned

- Building REST endpoints with FastAPI route decorators
- Path parameters, query parameters and type-hint-based validation
- Returning correct HTTP status codes (`200`, `404`, `422`) with `HTTPException`
- Why route order matters for catch-all path parameters
- Isolating dependencies with virtual environments and pinned `requirements.txt`
- How health checks are used by load balancers and orchestrators

---

Built as **Day 1** of a 7-day FastAPI & backend challenge.
