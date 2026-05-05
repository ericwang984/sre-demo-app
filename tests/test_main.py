import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "SRE Demo API"


def test_health():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_ready():
    """Test readiness check endpoint."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_metrics():
    """Test metrics endpoint exists."""
    response = client.get("/metrics")
    assert response.status_code == 200
    # Prometheus metrics should be present
    content = response.text
    assert "http_requests_total" in content


def test_get_orders():
    """Test getting orders list."""
    response = client.get("/api/orders")
    assert response.status_code == 200
    orders = response.json()
    assert isinstance(orders, list)
    assert len(orders) > 0


def test_get_order_by_id():
    """Test getting a specific order."""
    response = client.get("/api/orders/1")
    assert response.status_code == 200
    order = response.json()
    assert order["id"] == 1
    assert order["customer"] == "Alice"


def test_get_order_not_found():
    """Test getting non-existent order."""
    response = client.get("/api/orders/999")
    assert response.status_code == 404


def test_slow_response():
    """Test slow response endpoint with short delay."""
    response = client.get("/api/slow?seconds=1")
    assert response.status_code == 200
    data = response.json()
    assert data["sleep_duration"] == 1


def test_error_response():
    """Test error endpoint returns 500."""
    response = client.get("/api/error")
    assert response.status_code == 500


def test_order_stats():
    """Test order statistics endpoint."""
    response = client.get("/api/orders/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total_orders" in stats
    assert "total_value" in stats
    assert stats["total_orders"] > 0


def test_orders_limit():
    """Test orders limit parameter."""
    response = client.get("/api/orders?limit=2")
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) == 2


def test_flaky_response():
    """Test flaky endpoint - should return either 200 or 500."""
    response = client.get("/api/flaky")
    assert response.status_code in [200, 500]
