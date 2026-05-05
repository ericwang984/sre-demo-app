#!/usr/bin/env python3
"""
Test script to verify all API endpoints are working.
Run this after starting the application with docker-compose up.
"""

import requests
import sys
from typing import Tuple, Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_result(test_name: str, success: bool, message: str = ""):
    """Print test result with color coding."""
    status = f"{GREEN}✓ PASS{RESET}" if success else f"{RED}✗ FAIL{RESET}"
    print(f"{status} - {test_name}")
    if message:
        print(f"  {message}")


def test_root() -> bool:
    """Test root endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        success = response.status_code == 200
        if success:
            data = response.json()
            assert data["message"] == "SRE Demo API"
        print_result("Root endpoint (/)", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result("Root endpoint (/)", False, str(e))
        return False


def test_health() -> bool:
    """Test health check endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        success = response.status_code == 200
        if success:
            data = response.json()
            assert data["status"] == "healthy"
        print_result("Health check (/health)", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result("Health check (/health)", False, str(e))
        return False


def test_ready() -> bool:
    """Test readiness check endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/ready", timeout=TIMEOUT)
        success = response.status_code == 200
        if success:
            data = response.json()
            assert data["status"] == "ready"
        print_result("Readiness check (/ready)", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result("Readiness check (/ready)", False, str(e))
        return False


def test_metrics() -> bool:
    """Test Prometheus metrics endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/metrics", timeout=TIMEOUT)
        success = response.status_code == 200
        if success:
            content = response.text
            assert "http_requests_total" in content
        print_result("Metrics endpoint (/metrics)", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result("Metrics endpoint (/metrics)", False, str(e))
        return False


def test_get_orders() -> bool:
    """Test getting orders list."""
    try:
        response = requests.get(f"{BASE_URL}/api/orders", timeout=TIMEOUT)
        success = response.status_code == 200
        if success:
            orders = response.json()
            assert isinstance(orders, list)
            assert len(orders) > 0
        print_result("Get orders (/api/orders)", success, f"Status: {response.status_code}, Count: {len(orders)}")
        return success
    except Exception as e:
        print_result("Get orders (/api/orders)", False, str(e))
        return False


def test_get_order_by_id() -> bool:
    """Test getting a specific order."""
    try:
        response = requests.get(f"{BASE_URL}/api/orders/1", timeout=TIMEOUT)
        success = response.status_code == 200
        if success:
            order = response.json()
            assert order["id"] == 1
            assert order["customer"] == "Alice"
        print_result("Get order by ID (/api/orders/1)", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result("Get order by ID (/api/orders/1)", False, str(e))
        return False


def test_get_order_not_found() -> bool:
    """Test getting non-existent order returns 404."""
    try:
        response = requests.get(f"{BASE_URL}/api/orders/999", timeout=TIMEOUT)
        success = response.status_code == 404
        print_result("Get non-existent order (/api/orders/999)", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result("Get non-existent order (/api/orders/999)", False, str(e))
        return False


def test_order_stats() -> bool:
    """Test order statistics endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/api/orders/stats", timeout=TIMEOUT)
        success = response.status_code == 200
        if success:
            stats = response.json()
            assert "total_orders" in stats
            assert "total_value" in stats
            assert stats["total_orders"] > 0
        print_result("Order statistics (/api/orders/stats)", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result("Order statistics (/api/orders/stats)", False, str(e))
        return False


def test_orders_limit() -> bool:
    """Test orders limit parameter."""
    try:
        response = requests.get(f"{BASE_URL}/api/orders?limit=2", timeout=TIMEOUT)
        success = response.status_code == 200
        if success:
            orders = response.json()
            assert len(orders) == 2
        print_result("Orders with limit (/api/orders?limit=2)", success, f"Status: {response.status_code}, Count: {len(orders)}")
        return success
    except Exception as e:
        print_result("Orders with limit (/api/orders?limit=2)", False, str(e))
        return False


def test_slow_response() -> bool:
    """Test slow response endpoint with short delay."""
    try:
        response = requests.get(f"{BASE_URL}/api/slow?seconds=1", timeout=TIMEOUT)
        success = response.status_code == 200
        if success:
            data = response.json()
            assert data["sleep_duration"] == 1
        print_result("Slow response (/api/slow?seconds=1)", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_result("Slow response (/api/slow?seconds=1)", False, str(e))
        return False


def test_error_response() -> bool:
    """Test error endpoint returns 500."""
    try:
        response = requests.get(f"{BASE_URL}/api/error", timeout=TIMEOUT)
        success = response.status_code == 500
        print_result("Error response (/api/error)", success, f"Status: {response.status_code} (expected 500)")
        return success
    except Exception as e:
        print_result("Error response (/api/error)", False, str(e))
        return False


def test_flaky_response() -> bool:
    """Test flaky endpoint - should return either 200 or 500."""
    try:
        response = requests.get(f"{BASE_URL}/api/flaky", timeout=TIMEOUT)
        success = response.status_code in [200, 500]
        print_result("Flaky response (/api/flaky)", success, f"Status: {response.status_code} (expected 200 or 500)")
        return success
    except Exception as e:
        print_result("Flaky response (/api/flaky)", False, str(e))
        return False


def main():
    """Run all endpoint tests."""
    print(f"\n{YELLOW}Testing SRE Demo API Endpoints{RESET}")
    print(f"Base URL: {BASE_URL}\n")

    tests = [
        test_root,
        test_health,
        test_ready,
        test_metrics,
        test_get_orders,
        test_get_order_by_id,
        test_get_order_not_found,
        test_order_stats,
        test_orders_limit,
        test_slow_response,
        test_error_response,
        test_flaky_response,
    ]

    results = [test() for test in tests]

    print(f"\n{'='*60}")
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"{GREEN}All tests passed! ({passed}/{total}){RESET}\n")
        return 0
    else:
        print(f"{RED}Some tests failed: {passed}/{total} passed{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
