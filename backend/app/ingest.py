import json
import logging
import re
from enum import StrEnum
from typing import Callable

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.alerts import evaluate_status, evaluate_telemetry
from app.models import Device, Telemetry
from app.schemas import StatusPayload, TelemetryPayload


logger = logging.getLogger(__name__)
TOPIC_PATTERN = re.compile(
    r"^flood-monitoring/devices/(?P<device_id>[A-Za-z0-9][A-Za-z0-9_-]{0,63})/(?P<kind>telemetry|status)$"
)


class IngestResult(StrEnum):
    STORED = "stored"
    DUPLICATE = "duplicate"


def ingest_message(
    topic: str,
    raw_payload: bytes,
    session_factory: Callable[[], Session],
) -> IngestResult:
    match = TOPIC_PATTERN.fullmatch(topic)
    if match is None:
        raise ValueError(f"Topic không hợp lệ: {topic}")

    try:
        document = json.loads(raw_payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Payload không phải JSON UTF-8 hợp lệ") from exc

    kind = match.group("kind")
    payload = (
        TelemetryPayload.model_validate(document)
        if kind == "telemetry"
        else StatusPayload.model_validate(document)
    )
    if payload.device_id != match.group("device_id"):
        raise ValueError("device_id trong topic và payload không khớp")

    with session_factory() as session:
        device = session.get(Device, payload.device_id)
        if device is None:
            device = Device(id=payload.device_id)
            session.add(device)

        device.last_seen_at = payload.timestamp

        if isinstance(payload, StatusPayload):
            device.connectivity = payload.connectivity
            evaluate_status(session, payload)
            session.commit()
            return IngestResult.STORED

        duplicate = session.scalar(
            select(Telemetry.id).where(
                Telemetry.device_id == payload.device_id,
                Telemetry.sequence == payload.sequence,
                Telemetry.measured_at == payload.timestamp,
            )
        )
        if duplicate is not None:
            return IngestResult.DUPLICATE

        previous = session.scalar(
            select(Telemetry)
            .where(
                Telemetry.device_id == payload.device_id,
                Telemetry.measured_at < payload.timestamp,
            )
            .order_by(Telemetry.measured_at.desc())
            .limit(1)
        )

        device.connectivity = "online"
        device.sensor_status = payload.sensor_status
        session.add(
            Telemetry(
                device_id=payload.device_id,
                sequence=payload.sequence,
                measured_at=payload.timestamp,
                water_level_cm=payload.water_level_cm,
                rainfall_mm=payload.rainfall_mm,
                signal_strength_dbm=payload.signal_strength_dbm,
                sensor_status=payload.sensor_status,
            )
        )
        evaluate_telemetry(session, payload, previous)
        session.commit()
        return IngestResult.STORED


def log_invalid_message(topic: str, exc: ValueError | ValidationError) -> None:
    logger.warning("Bỏ qua bản tin MQTT không hợp lệ trên %s: %s", topic, exc)
