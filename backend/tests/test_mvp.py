"""Focused MVP tests: database, auth, protected routes, irrigation AI."""

import asyncio
import os
import sqlite3

import httpx
import pytest

os.environ.setdefault("PYTHONPATH", ".")


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture(scope="module")
def client():
    from src.api.main import app

    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


def test_health(client):
    async def _test():
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    _run(_test())


def test_database_file_exists():
    db_path = os.path.join(os.path.dirname(__file__), "..", "agri_guardian.db")
    assert os.path.exists(db_path), "agri_guardian.db should exist after migrations/seed"
    conn = sqlite3.connect(db_path)
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    for table in ("users", "farms", "devices", "recommendations", "sensor_readings"):
        assert table in tables


def test_authentication_flow(client):
    async def _test():
        r = await client.post(
            "/api/v1/auth/token",
            data={"username": "demo@agriguardian.com", "password": "Demo@12345"},
        )
        assert r.status_code == 200, r.text
        token = r.json()["access_token"]
        assert token

        r = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["email"] == "demo@agriguardian.com"

    _run(_test())


def test_protected_farm_endpoint(client):
    async def _test():
        r = await client.post(
            "/api/v1/auth/token",
            data={"username": "demo@agriguardian.com", "password": "Demo@12345"},
        )
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        r = await client.get("/api/v1/farm/", headers=headers)
        assert r.status_code == 200
        farms = r.json()["farms"]
        assert len(farms) >= 1
        assert farms[0]["name"] == "Green Horizon Farm"

    _run(_test())


def test_dashboard_endpoint(client):
    async def _test():
        r = await client.post(
            "/api/v1/auth/token",
            data={"username": "demo@agriguardian.com", "password": "Demo@12345"},
        )
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        r = await client.get("/api/v1/dashboard/", headers=headers)
        assert r.status_code == 200
        body = r.json()
        assert body["source"] == "database"
        assert body["farm"]["primary_crop"] == "Wheat"

    _run(_test())


def test_irrigation_ai_endpoint(client):
    async def _test():
        payload = {
            "temperature": 32.5,
            "humidity": 45.0,
            "soil_moisture": 22.0,
            "rainfall_prev_day": 0.0,
        }
        r = await client.post("/api/v1/recommendation/irrigation", json=payload)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["status"] == "success"
        assert body["prediction"] in (0, 1)
        assert body["recommendation"] in ("IRRIGATE NOW", "SKIP IRRIGATION")
        assert "confidence" in body

    _run(_test())


def test_invalid_login(client):
    async def _test():
        r = await client.post(
            "/api/v1/auth/token",
            data={"username": "demo@agriguardian.com", "password": "wrong-password"},
        )
        assert r.status_code == 401

    _run(_test())


def test_irrigation_service_loads_model():
    from src.infrastructure.ai_engine.irrigation_service import predict_irrigation, FEATURE_ORDER

    assert FEATURE_ORDER == ("temperature", "humidity", "soil_moisture", "rainfall_prev_day")
    result = predict_irrigation(
        temperature=35,
        humidity=40,
        soil_moisture=15,
        rainfall_prev_day=0,
    )
    assert result["prediction"] in (0, 1)
    assert result["model_type"] == "XGBClassifier"
