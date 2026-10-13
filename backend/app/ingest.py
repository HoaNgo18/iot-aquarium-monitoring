import json
import logging
from enum import StrEnum
from typing import Callable

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.repositories.devices import get_or_create_device
from app.repositories.telemetry import add_telemetry, get_previous, is_duplicate
from app.schemas import StatusPayload, TelemetryPayload
from app.services.alert_service import evaluate_status_alerts, evaluate_telemetry_alerts
from app.topics import TOPIC_PATTERN


logger = logging.getLogger(__name__)


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
        device = get_or_create_device(session, payload.device_id)
        device.last_seen_at = payload.timestamp

        if isinstance(payload, StatusPayload):
            device.connectivity = payload.connectivity
            evaluate_status_alerts(session, payload)
            session.commit()
            return IngestResult.STORED

        if is_duplicate(session, payload):
            return IngestResult.DUPLICATE

        previous = get_previous(session, payload)
        device.connectivity = "online"
        device.sensor_status = payload.sensor_status
        add_telemetry(session, payload)
        evaluate_telemetry_alerts(session, payload, previous)
        session.commit()
        return IngestResult.STORED


def log_invalid_message(topic: str, exc: ValueError | ValidationError) -> None:
    logger.warning("Bỏ qua bản tin MQTT không hợp lệ trên %s: %s", topic, exc)
