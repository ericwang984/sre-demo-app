# SRE Demo App

A FastAPI application demonstrating production-ready patterns for DevOps/SRE portfolio projects.

## Overview

This is the application component of a two-repository GitOps architecture:
- **sre-demo-app** (this repository): Application code with CI pipeline
- **sre-gitops-platform**: Infrastructure, Kubernetes manifests, Argo CD configuration

## Application Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /` | API information and available endpoints |
| `GET /health` | Liveness probe - minimal health check |
| `GET /ready` | Readiness probe - checks if service can handle traffic |
| `GET /metrics` | Prometheus metrics endpoint |
| `GET /api/orders` | Get list of orders (business logic) |
| `GET /api/orders/{id}` | Get a specific order by ID |
| `GET /api/orders/stats` | Get order statistics |
| `GET /api/slow` | Simulates slow response (incident testing) |
| `GET /api/error` | Simulates 500 error (incident testing) |
| `GET /api/flaky` | Random failures (50% chance, for retry testing) |

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r app/requirements.txt

# Run locally
uvicorn app.main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=app
```

### Docker

```bash
# Build image
docker build -t sre-demo-app .

# Run container
docker run -p 8000:8000 sre-demo-app

# Test health check
curl http://localhost:8000/health
```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) includes:

1. **Test Stage**: Run pytest with coverage
2. **Build Stage**: Build Docker image
3. **Scan Stage**: Trivy vulnerability scan (fails on CRITICAL/HIGH)
4. **Push Stage**: Push to GitHub Container Registry (main branch only)

## Metrics

The application exposes Prometheus metrics at `/metrics`:
- `http_requests_total`: Request counter by method, path, status
- `http_request_duration_seconds`: Request duration histogram
- `http_request_size_bytes`: Request size histogram
- `http_response_size_bytes`: Response size histogram

## Incident Simulation

This application includes endpoints specifically for testing incident response:

```bash
# Simulate high latency (triggers HighLatency alert)
curl http://localhost:8000/api/slow?seconds=10

# Simulate errors (triggers HighErrorRate alert)
curl http://localhost:8000/api/error

# Simulate flaky behavior (for testing retries)
curl http://localhost:8000/api/flaky
```

## Deployment

This application is deployed via GitOps using Argo CD. See the `sre-gitops-platform` repository for:
- Kubernetes manifests
- Argo CD application definitions
- Observability configuration
- Runbooks and incident procedures

## Development

### Project Structure

```
sre-demo-app/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   └── requirements.txt # Python dependencies
├── tests/
│   ├── __init__.py
│   └── test_main.py     # Unit tests
├── Dockerfile            # Multi-stage container build
├── .github/
│   └── workflows/
│       └── ci.yml       # CI/CD pipeline
└── README.md
```

### Adding New Endpoints

1. Add route to `app/main.py`
2. Add corresponding test in `tests/test_main.py`
3. Run `pytest` to verify
4. Commit and push - CI will validate

## License

MIT License
