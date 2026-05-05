from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
import asyncio
import random
from typing import List
import time

app = FastAPI(
    title="SRE Demo API",
    description="A demo API for showcasing DevOps/SRE practices",
    version="1.0.0"
)

# Enable Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Sample data
ORDERS = [
    {"id": 1, "customer": "Alice", "items": ["widget", "gadget"], "total": 99.99},
    {"id": 2, "customer": "Bob", "items": ["widget"], "total": 49.99},
    {"id": 3, "customer": "Charlie", "items": ["gadget", "tool"], "total": 149.99},
]

# Dependency check flag
READY = True


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "SRE Demo API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
        "metrics": "/metrics"
    }


@app.get("/health")
async def health():
    """Liveness probe - minimal check if process is alive."""
    return {"status": "healthy"}


@app.get("/ready")
async def readiness():
    """Readiness probe - checks if service can handle traffic."""
    if READY:
        return {"status": "ready"}
    raise HTTPException(status_code=503, detail="Service not ready")


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint (handled by instrumentator)."""
    pass


@app.get("/api/orders", response_model=List[dict])
async def get_orders(limit: int = 10):
    """Get orders - business logic endpoint."""
    return ORDERS[:limit]


@app.get("/api/orders/{order_id}")
async def get_order(order_id: int):
    """Get a specific order by ID."""
    for order in ORDERS:
        if order["id"] == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")


@app.get("/api/slow")
async def slow_response(seconds: int = 5):
    """
    Simulates slow response for incident testing.
    Sleeps for specified seconds before responding.
    """
    await asyncio.sleep(seconds)
    return {
        "message": f"Response took {seconds} seconds",
        "sleep_duration": seconds
    }


@app.get("/api/error")
async def error_response():
    """Simulates error for incident testing - always returns 500."""
    raise HTTPException(status_code=500, detail="Simulated error for testing")


@app.get("/api/flaky")
async def flaky_response():
    """
    Simulates flaky response - fails 50% of the time.
    Useful for testing retry logic and alert thresholds.
    """
    if random.random() < 0.5:
        raise HTTPException(status_code=500, detail="Random failure (50% chance)")
    return {"message": "Success this time!", "flaky": True}


@app.get("/api/orders/stats")
async def get_order_stats():
    """Get order statistics - demonstrates business logic."""
    total_orders = len(ORDERS)
    total_value = sum(order["total"] for order in ORDERS)
    return {
        "total_orders": total_orders,
        "total_value": total_value,
        "average_value": total_value / total_orders if total_orders > 0 else 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
