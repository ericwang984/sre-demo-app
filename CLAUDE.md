# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a demonstration FastAPI application for DevOps/SRE portfolio projects. It's part of a two-repository GitOps architecture:
- **sre-demo-app** (this repo): Application code with CI pipeline
- **sre-gitops-platform**: Infrastructure, Kubernetes manifests, Argo CD configuration

## Development Commands

```bash
# Install dependencies
pip install -r app/requirements.txt

# Run locally with hot reload
uvicorn app.main:app --reload

# Run unit tests
pytest

# Run unit tests with coverage report
pytest --cov=app

# Test all endpoints manually (Python version - requires requests library)
./test_endpoints.py

# Test all endpoints manually (Bash version - no dependencies)
./test_endpoints.sh

# Or test endpoints against a different URL
./test_endpoints.sh http://localhost:8000

# Build and run with Docker Compose (recommended for local testing)
docker-compose up

# Build and run in background
docker-compose up -d

# Rebuild after code changes
docker-compose up --build

# Stop containers
docker-compose down

# Or build and run Docker image manually
docker build -t sre-demo-app .
docker run -p 8000:8000 sre-demo-app
```

## Application Architecture

**Single-file application pattern**: All FastAPI routes, middleware, and business logic are in `app/main.py`. This is intentional for demo purposes.

**Prometheus metrics integration**: The app uses `prometheus-fastapi-instrumentator` to automatically expose metrics at `/metrics`:
- `http_requests_total`: Request counter by method, path, status
- `http_request_duration_seconds`: Request duration histogram
- `http_request_size_bytes`: Request size histogram
- `http_response_size_bytes`: Response size histogram

**Health check endpoints**:
- `/health`: Liveness probe - minimal check if process is alive
- `/ready`: Readiness probe - checks if service can handle traffic (uses `READY` flag)

## Incident Simulation Endpoints

The application includes special endpoints for testing incident response and observability tooling:

- `GET /api/slow?seconds=N`: Simulates high latency (use for testing SLO/latency alerts)
- `GET /api/error`: Always returns 500 (use for testing error rate alerts)
- `GET /api/flaky`: Returns 500 50% of the time (use for testing retry logic and alert thresholds)

When modifying these endpoints, consider that alerts in the GitOps platform repository are configured based on their behavior.

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs in stages:

1. **Test Stage**: pytest with coverage, uploads to Codecov
2. **Build & Scan Stage**: Builds Docker image, runs Trivy vulnerability scan (fails on CRITICAL/HIGH severity)
3. **Push Stage**: Pushes to GitHub Container Registry as `latest` and `{sha}` tags (main branch only)

Pipeline gates are sequential - build/scan only runs if tests pass.

## Adding New Endpoints

When adding new API endpoints:

1. Add route handler to `app/main.py`
2. Add corresponding test in `tests/test_main.py`
3. Run `pytest` locally to verify
4. Commit and push - CI will run tests and vulnerability scan

All new endpoints automatically get Prometheus metrics (instrumentation is global).

## Docker Build

Multi-stage build pattern:
- **Stage 1 (builder)**: Python 3.12 slim, installs dependencies to `/root/.local`
- **Stage 2 (runtime)**: Python 3.12 slim, creates non-root user (`appuser`), copies only installed dependencies and app code

The container includes a HEALTHCHECK that calls `/health` every 30s (starts after 5s grace period).

## GitOps Deployment Context

This application is deployed via Argo CD from a separate repository (`sre-gitops-platform`). That repository contains:
- Kubernetes manifests and Helm charts
- Argo CD Application resources
- Prometheus alerts and recording rules
- Grafana dashboards
- Runbooks and incident procedures

Changes here are automatically deployed after CI pushes the image to GHCR.
