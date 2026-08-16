import pytest
from starlette.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_read_root():
    """Test the root health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["service"] == "AMA Backend API Gateway"

def test_trigger_analysis_endpoint():
    """Test triggering a background analysis job"""
    job_id = "test_job_123"
    payload = {"topic": "Mỹ phẩm thuần chay"}
    response = client.post(f"/api/analyze/{job_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "started"
    assert data["job_id"] == job_id
    assert data["topic"] == "Mỹ phẩm thuần chay"
