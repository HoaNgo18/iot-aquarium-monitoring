from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Alert, Telemetry, Threshold
from app.schemas import StatusPayload, TelemetryPayload


def get_or_create_threshold(session: Session, device_id: str) -> Threshold:
    threshold = session.get(Threshold, device_id)
    if threshold is None:
        threshold = Threshold(device_id=device_id)
        session.add(threshold)
        session.flush()
    return threshold


def evaluate_status(session: Session, payload: StatusPayload) -> None:
    _set_alert(
        session=session,
        device_id=payload.device_id,
        alert_type="offline",
        active=payload.connectivity == "offline",
        severity="warning",
        message="Thiết bị đã mất kết nối.",
        occurred_at=payload.timestamp,
    )


def evaluate_telemetry(
    session: Session,
    payload: TelemetryPayload,
    previous: Telemetry | None,
) -> None:
    threshold = get_or_create_threshold(session, payload.device_id)

    _set_alert(
        session=session,
        device_id=payload.device_id,
        alert_type="sensor_error",
        active=payload.sensor_status == "error",
        severity="critical",
        message="Cảm biến mực nước trả về dữ liệu không hợp lệ.",
        occurred_at=payload.timestamp,
    )

    if payload.water_level_cm is not None:
        if payload.water_level_cm >= threshold.water_critical_cm:
            water_active, water_severity = True, "critical"
        elif payload.water_level_cm >= threshold.water_warning_cm:
            water_active, water_severity = True, "warning"
        else:
            water_active, water_severity = False, "warning"

        _set_alert(
            session=session,
            device_id=payload.device_id,
            alert_type="water_level",
            active=water_active,
            severity=water_severity,
            message=f"Mực nước hiện tại là {payload.water_level_cm:.2f} cm.",
            occurred_at=payload.timestamp,
        )

    _set_alert(
        session=session,
        device_id=payload.device_id,
        alert_type="heavy_rain",
        active=payload.rainfall_mm >= threshold.rainfall_warning_mm,
        severity="warning",
        message=f"Lượng mưa trong chu kỳ là {payload.rainfall_mm:.2f} mm.",
        occurred_at=payload.timestamp,
    )

    rise_rate = _calculate_rise_rate(payload, previous)
    if rise_rate is not None:
        _set_alert(
            session=session,
            device_id=payload.device_id,
            alert_type="rapid_rise",
            active=rise_rate >= threshold.rise_rate_cm_per_min,
            severity="critical" if rise_rate >= threshold.rise_rate_cm_per_min * 2 else "warning",
            message=f"Mực nước đang tăng {rise_rate:.2f} cm/phút.",
            occurred_at=payload.timestamp,
        )


def _calculate_rise_rate(
    payload: TelemetryPayload,
    previous: Telemetry | None,
) -> float | None:
    if payload.water_level_cm is None or previous is None or previous.water_level_cm is None:
        return None

    previous_time = previous.measured_at
    if previous_time.tzinfo is None:
        previous_time = previous_time.replace(tzinfo=timezone.utc)
    elapsed_seconds = (payload.timestamp - previous_time).total_seconds()
    if elapsed_seconds < 1 or elapsed_seconds > 15 * 60:
        return None

    return max(0.0, payload.water_level_cm - previous.water_level_cm) / elapsed_seconds * 60


def _set_alert(
    session: Session,
    device_id: str,
    alert_type: str,
    active: bool,
    severity: str,
    message: str,
    occurred_at: datetime,
) -> None:
    current = session.scalar(
        select(Alert).where(
            Alert.device_id == device_id,
            Alert.alert_type == alert_type,
            Alert.ended_at.is_(None),
        )
    )

    if active:
        if current is None:
            session.add(
                Alert(
                    device_id=device_id,
                    alert_type=alert_type,
                    severity=severity,
                    message=message,
                    started_at=occurred_at,
                )
            )
        else:
            current.severity = severity
            current.message = message
    elif current is not None:
        current.ended_at = occurred_at
