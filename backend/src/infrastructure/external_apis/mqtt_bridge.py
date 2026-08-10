"""MQTT transport boundary for ESP32 telemetry, status, and pump control."""
from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone

from pydantic import BaseModel, Field, ValidationError, model_validator
from sqlalchemy import select

from src.core.config import settings
from src.infrastructure.database.base import AsyncSessionLocal
from src.infrastructure.database.models import Device, SensorReading

logger = logging.getLogger(__name__)
TOPIC_PATTERN = re.compile(r"^agriguardian/farm/(?P<device_id>[^/]+)/(?P<kind>telemetry|status)$")


@dataclass(frozen=True)
class PumpCommand:
    device_id: str
    command: str
    duration_seconds: int | None = None


class TelemetryMessage(BaseModel):
    device_id: str = Field(min_length=1, max_length=50)
    timestamp: datetime | None = None
    temperature: float | None = Field(default=None, ge=-50, le=100)
    humidity: float | None = Field(default=None, ge=0, le=100)
    soil_moisture: float | None = Field(default=None, ge=0, le=100)
    rainfall: float | None = Field(default=None, ge=0)
    water_level: float | None = Field(default=None, ge=0, le=100)

    @model_validator(mode="after")
    def require_sensor_value(self):
        if all(value is None for value in (
            self.temperature, self.humidity, self.soil_moisture, self.rainfall, self.water_level,
        )):
            raise ValueError("Telemetry must include at least one sensor value")
        return self


class StatusMessage(BaseModel):
    device_id: str = Field(min_length=1, max_length=50)
    status: str = Field(min_length=1, max_length=20)
    pump_on: bool | None = None


def control_topic(device_id: str) -> str:
    return f"agriguardian/farm/{device_id}/control"


def telemetry_topic(device_id: str) -> str:
    return f"agriguardian/farm/{device_id}/telemetry"


def status_topic(device_id: str) -> str:
    return f"agriguardian/farm/{device_id}/status"


def parse_mqtt_message(topic: str, payload: bytes) -> tuple[str, TelemetryMessage | StatusMessage]:
    """Validate a broker payload before it reaches the database."""
    match = TOPIC_PATTERN.fullmatch(topic)
    if not match:
        raise ValueError("Unsupported MQTT topic")
    try:
        data = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Malformed MQTT JSON") from exc
    if not isinstance(data, dict):
        raise ValueError("MQTT JSON payload must be an object")
    if data.get("device_id") != match.group("device_id"):
        raise ValueError("Payload device_id does not match MQTT topic")
    try:
        if match.group("kind") == "telemetry":
            return "telemetry", TelemetryMessage.model_validate(data)
        return "status", StatusMessage.model_validate(data)
    except ValidationError as exc:
        raise ValueError("Invalid MQTT payload") from exc


async def persist_mqtt_message(topic: str, payload: bytes) -> None:
    """Persist one validated ESP32 telemetry/status event using its MAC device ID."""
    kind, message = parse_mqtt_message(topic, payload)
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Device).where(Device.mac_address == message.device_id))
        device = result.scalars().first()
        if device is None or not device.is_active:
            raise ValueError("Unknown or inactive MQTT device")

        now = datetime.now(timezone.utc)
        device.last_seen_at = now
        if kind == "status":
            device.status = message.status
        else:
            telemetry = message
            device.status = "active"
            session.add(SensorReading(
                device_id=device.id,
                temperature=telemetry.temperature,
                humidity=telemetry.humidity,
                soil_moisture=telemetry.soil_moisture,
                rainfall=telemetry.rainfall,
                water_level=telemetry.water_level,
                recorded_at=telemetry.timestamp or now,
            ))
        await session.commit()


class MqttTelemetrySubscriber:
    """Threaded paho client that forwards validated messages to FastAPI's event loop."""

    def __init__(self) -> None:
        self._client = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def start(self) -> bool:
        if not settings.MQTT_BROKER_HOST:
            logger.info("MQTT subscriber disabled: MQTT_BROKER_HOST is not configured")
            return False
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            logger.warning("MQTT subscriber disabled: paho-mqtt is not installed")
            return False

        self._loop = asyncio.get_running_loop()
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        if settings.MQTT_USERNAME:
            client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD or "")
        client.on_connect = self._on_connect
        client.on_message = self._on_message
        client.connect_async(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, keepalive=60)
        client.loop_start()
        self._client = client
        return True

    def stop(self) -> None:
        if self._client is not None:
            self._client.loop_stop()
            self._client.disconnect()
            self._client = None

    def _on_connect(self, client, _userdata, _flags, reason_code, _properties) -> None:
        if reason_code != 0:
            logger.warning("MQTT connection failed: %s", reason_code)
            return
        client.subscribe("agriguardian/farm/+/telemetry", qos=1)
        client.subscribe("agriguardian/farm/+/status", qos=1)
        logger.info("Subscribed to AgriGuardian telemetry and status topics")

    def _on_message(self, _client, _userdata, message) -> None:
        if self._loop is None:
            return
        future = asyncio.run_coroutine_threadsafe(persist_mqtt_message(message.topic, message.payload), self._loop)
        future.add_done_callback(self._log_persistence_failure)

    @staticmethod
    def _log_persistence_failure(future) -> None:
        try:
            future.result()
        except Exception as exc:  # Broker threads must not crash on bad device payloads.
            logger.warning("Rejected MQTT message: %s", exc)


def publish_pump_command(command: PumpCommand) -> None:
    """Publish a validated command, raising a clear error if MQTT is unavailable."""
    if not settings.MQTT_BROKER_HOST:
        raise RuntimeError("MQTT broker is not configured")
    try:
        from paho.mqtt import publish
    except ImportError as exc:
        raise RuntimeError("paho-mqtt is not installed") from exc
    payload = {"command": command.command}
    if command.duration_seconds is not None:
        payload["duration_seconds"] = command.duration_seconds
    auth = None
    if settings.MQTT_USERNAME:
        auth = {"username": settings.MQTT_USERNAME, "password": settings.MQTT_PASSWORD or ""}
    publish.single(
        control_topic(command.device_id), json.dumps(payload), hostname=settings.MQTT_BROKER_HOST,
        port=settings.MQTT_BROKER_PORT, auth=auth, qos=1,
    )
