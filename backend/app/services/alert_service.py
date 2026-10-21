from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.alert_rules import ThresholdValues, evaluate_connectivity, evaluate_telemetry
from app.repositories.alerts import apply_decision, get_or_create_threshold
from app.schemas import StatusPayload, TelemetryPayload


def evaluate_status_alerts(session: Session, payload: StatusPayload, *, observed_at: datetime) -> None:
    for decision in evaluate_connectivity(payload.connectivity):
        apply_decision(session, payload.device_id, decision, observed_at)


def evaluate_telemetry_alerts(session: Session, payload: TelemetryPayload, *, observed_at: datetime) -> None:
    threshold = get_or_create_threshold(session, payload.device_id)
    thresholds = ThresholdValues(
        temperature_min_c=threshold.temperature_min_c,
        temperature_max_c=threshold.temperature_max_c,
        ph_min=threshold.ph_min,
        ph_max=threshold.ph_max,
        turbidity_warning_pct=threshold.turbidity_warning_pct,
        turbidity_critical_pct=threshold.turbidity_critical_pct,
    )
    for decision in evaluate_telemetry(
        temperature_c=payload.temperature_c,
        ph=payload.ph,
        turbidity_pct=payload.turbidity_pct,
        sensor_status=payload.sensor_status,
        thresholds=thresholds,
    ):
        occurred_at = observed_at if decision.alert_type == "offline" else payload.timestamp
        apply_decision(session, payload.device_id, decision, occurred_at)
