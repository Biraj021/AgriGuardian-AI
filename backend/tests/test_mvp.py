"""Focused MVP tests: database, auth, protected routes, irrigation AI."""

import asyncio
import os
import sqlite3
from unittest.mock import patch

import httpx
import pytest

os.environ.setdefault("PYTHONPATH", ".")


def _run(coro):
    return asyncio.run(coro)


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


def test_sqlite_foreign_keys_are_enabled():
    async def _test():
        from sqlalchemy import text
        from src.infrastructure.database.base import engine

        async with engine.connect() as connection:
            result = await connection.execute(text("PRAGMA foreign_keys"))
            assert result.scalar_one() == 1

    _run(_test())


def test_public_health_weather_and_market_endpoints(client):
    async def _test():
        api_health = await client.get("/api/v1/health/")
        assert api_health.status_code == 200
        weather = await client.get("/api/v1/weather/current")
        assert weather.status_code == 200
        assert weather.json()["source"] in {"demo", "live"}
        market = await client.get("/api/v1/market/prices")
        assert market.status_code == 200
        assert market.json()["source"] in {"demo", "live"}

    _run(_test())


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
        headers = await _auth_headers(client)

        r = await client.get("/api/v1/farm/", headers=headers)
        assert r.status_code == 200
        farms = r.json()["farms"]
        assert len(farms) >= 1
        assert farms[0]["name"] == "Green Horizon Farm"

    _run(_test())


async def _auth_headers(client):
    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "demo@agriguardian.com", "password": "Demo@12345"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_dashboard_endpoint(client):
    async def _test():
        headers = await _auth_headers(client)

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
        headers = await _auth_headers(client)
        r = await client.post("/api/v1/recommendation/irrigation", json=payload, headers=headers)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["status"] == "success"
        assert body["prediction"] in (0, 1)
        assert body["recommendation"] in ("IRRIGATE NOW", "SKIP IRRIGATION")
        assert "confidence" in body
        assert body["recommendation_id"]
        history = await client.get("/api/v1/recommendation/history", headers=headers)
        assert history.status_code == 200
        assert any(item["id"] == body["recommendation_id"] for item in history.json()["recommendations"])

    _run(_test())


def test_protected_routes_reject_anonymous_requests(client):
    async def _test():
        for path in ("/api/v1/dashboard/", "/api/v1/sensor/recent", "/api/v1/device/", "/api/v1/analytics/overview"):
            response = await client.get(path)
            assert response.status_code == 401, f"{path}: {response.text}"

    _run(_test())


def test_sensor_ingestion_recent_readings_and_device_status(client):
    async def _test():
        headers = await _auth_headers(client)
        devices = await client.get("/api/v1/device/", headers=headers)
        assert devices.status_code == 200
        device = devices.json()["devices"][0]
        response = await client.post(
            "/api/v1/sensor/ingest",
            headers=headers,
            json={
                "device_id": device["id"], "temperature": 31, "humidity": 47,
                "soil_moisture": 24, "rainfall": 1.5, "water_level": 72,
            },
        )
        assert response.status_code == 201, response.text
        recent = await client.get("/api/v1/sensor/recent", headers=headers)
        assert recent.status_code == 200
        assert recent.json()["count"] <= 10
        stored = next(item for item in recent.json()["readings"] if item["id"] == response.json()["reading_id"])
        assert stored["rainfall"] == 1.5
        assert stored["water_level"] == 72
        updated_devices = await client.get("/api/v1/device/", headers=headers)
        updated = next(item for item in updated_devices.json()["devices"] if item["id"] == device["id"])
        assert updated["status"] == "active"
        assert updated["last_seen_at"] is not None

    _run(_test())


def test_mqtt_payload_validation_is_topic_bound():
    from src.infrastructure.external_apis.mqtt_bridge import parse_mqtt_message

    kind, message = parse_mqtt_message(
        "agriguardian/farm/AA:BB:CC:DD:EE:FF/telemetry",
        b'{"device_id":"AA:BB:CC:DD:EE:FF","temperature":30,"rainfall":1,"water_level":60}',
    )
    assert kind == "telemetry"
    assert message.rainfall == 1
    assert message.water_level == 60

    with pytest.raises(ValueError):
        parse_mqtt_message(
            "agriguardian/farm/AA:BB:CC:DD:EE:FF/telemetry",
            b'{"device_id":"another-device","temperature":30}',
        )


def test_mqtt_telemetry_and_status_persist_for_known_device(client):
    async def _test():
        from src.infrastructure.external_apis.mqtt_bridge import persist_mqtt_message

        headers = await _auth_headers(client)
        devices = await client.get("/api/v1/device/", headers=headers)
        device = devices.json()["devices"][0]
        mac = device["mac_address"]
        await persist_mqtt_message(
            f"agriguardian/farm/{mac}/telemetry",
            (
                f'{{"device_id":"{mac}","temperature":29,"humidity":55,'
                '"soil_moisture":38,"rainfall":2,"water_level":68}'
            ).encode(),
        )
        await persist_mqtt_message(
            f"agriguardian/farm/{mac}/status",
            f'{{"device_id":"{mac}","status":"online","pump_on":false}}'.encode(),
        )
        recent = await client.get("/api/v1/sensor/recent", headers=headers)
        stored = next(item for item in recent.json()["readings"] if item["device_mac"] == mac)
        assert stored["rainfall"] == 2
        assert stored["water_level"] == 68
        updated_devices = await client.get("/api/v1/device/", headers=headers)
        assert next(item for item in updated_devices.json()["devices"] if item["id"] == device["id"])["status"] == "online"

    _run(_test())


def test_device_control_and_analytics(client):
    async def _test():
        audit_db = sqlite3.connect(os.path.join(os.path.dirname(__file__), "..", "agri_guardian.db"))
        audit_before = audit_db.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0]
        audit_db.close()
        headers = await _auth_headers(client)
        devices = await client.get("/api/v1/device/", headers=headers)
        device_id = devices.json()["devices"][0]["id"]
        with patch("src.api.v1.routers.device.publish_pump_command") as publish:
            response = await client.post(
                f"/api/v1/device/{device_id}/control",
                headers=headers,
                json={"command": "PUMP_ON", "duration_seconds": 30},
            )
        assert response.status_code == 202, response.text
        publish.assert_called_once()
        audit_db = sqlite3.connect(os.path.join(os.path.dirname(__file__), "..", "agri_guardian.db"))
        audit_after = audit_db.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0]
        audit_db.close()
        assert audit_after == audit_before + 1
        analytics = await client.get("/api/v1/analytics/overview", headers=headers)
        assert analytics.status_code == 200
        assert analytics.json()["source"] == "database"
        assert analytics.json()["sensor_readings_count"] >= 1

    _run(_test())


def test_latest_sensor_ai_recommendation(client):
    async def _test():
        headers = await _auth_headers(client)
        recent = await client.get("/api/v1/sensor/recent", headers=headers)
        latest = recent.json()["readings"][0]
        response = await client.post("/api/v1/recommendation/irrigation/latest", headers=headers)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["status"] == "success"
        assert body["recommendation_id"]
        assert body["inputs"]["temperature"] == latest["temperature"]
        assert body["inputs"]["humidity"] == latest["humidity"]
        assert body["inputs"]["soil_moisture"] == latest["soil_moisture"]
        assert body["inputs"]["rainfall_prev_day"] == (latest["rainfall"] or 0)
        assert body["feature_order"] == ["temperature", "humidity", "soil_moisture", "rainfall_prev_day"]
        history = await client.get("/api/v1/recommendation/history", headers=headers)
        assert any(item["id"] == body["recommendation_id"] for item in history.json()["recommendations"])

    _run(_test())


def test_unconfigured_mqtt_control_returns_service_unavailable(client):
    async def _test():
        headers = await _auth_headers(client)
        devices = await client.get("/api/v1/device/", headers=headers)
        device_id = devices.json()["devices"][0]["id"]
        response = await client.post(
            f"/api/v1/device/{device_id}/control",
            headers=headers,
            json={"command": "PUMP_OFF"},
        )
        assert response.status_code == 503
        assert response.json()["detail"] == "MQTT broker is not configured"

    _run(_test())


def test_dry_and_wet_ai_inputs_use_real_model_and_persist(client):
    async def _test():
        headers = await _auth_headers(client)
        for payload in (
            {"temperature": 32, "humidity": 45, "soil_moisture": 25, "rainfall_prev_day": 0},
            {"temperature": 20, "humidity": 70, "soil_moisture": 65, "rainfall_prev_day": 0},
        ):
            response = await client.post("/api/v1/recommendation/irrigation", headers=headers, json=payload)
            assert response.status_code == 200, response.text
            result = response.json()
            assert result["model_type"] == "XGBClassifier"
            assert result["feature_order"] == ["temperature", "humidity", "soil_moisture", "rainfall_prev_day"]
            assert result["normalized_inputs"]["soil_moisture"] == payload["soil_moisture"] / 100
            history = await client.get("/api/v1/recommendation/history", headers=headers)
            assert any(item["id"] == result["recommendation_id"] for item in history.json()["recommendations"])

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
