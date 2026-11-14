from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes.health import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "message": "Enterprise AI Knowledge Assistant backend is running"
    }


def test_metrics_endpoint():
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
