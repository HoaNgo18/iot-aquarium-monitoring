from sqlalchemy.orm import Session

from app.domain.alert_rules import PreviousReading, ThresholdValues, evaluate_connectivity, evaluate_telemetry
from app.models import Telemetry
from app.repositories.alerts import apply_decision, get_or_create_threshold
from app.schemas import StatusPayload, TelemetryPayload


def evaluate_status_alerts(session: Session, payload: StatusPayload) -> None:
    for decision in evaluate_connectivity(payload.connectivity):
        apply_decision(session, payload.device_id, decision, payload.timestamp)


def evaluate_telemetry_alerts(
    session: Session,
    payload: TelemetryPayload,
    previous: Telemetry | None,
) -> None:
    threshold = get_or_create_threshold(session, payload.device_id)
    thresholds = ThresholdValues(
        water_warning_cm=threshold.water_warning_cm,
        water_critical_cm=threshold.water_critical_cm,
        rise_rate_cm_per_min=threshold.rise_rate_cm_per_min,
        rainfall_warning_mm=threshold.rainfall_warning_mm,
    )
    previous_reading = (
        PreviousReading(previous.measured_at, previous.water_level_cm)
        if previous is not None
        else None
    )
    decisions = evaluate_telemetry(
        measured_at=payload.timestamp,
        water_level_cm=payload.water_level_cm,
        rainfall_mm=payload.rainfall_mm,
        sensor_status=payload.sensor_status,
        thresholds=thresholds,
        previous=previous_reading,
    )
    for decision in decisions:
        apply_decision(session, payload.device_id, decision, payload.timestamp)
