import pytest
from fastapi.testclient import TestClient
from hivemind.api.server import app

client = TestClient(app)

def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_list_debates():
    r = client.get("/api/v1/debates")
    assert r.status_code == 200
