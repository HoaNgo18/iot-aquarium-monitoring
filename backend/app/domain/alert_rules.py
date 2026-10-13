from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class ThresholdValues:
    water_warning_cm: float
    water_critical_cm: float
    rise_rate_cm_per_min: float
    rainfall_warning_mm: float


@dataclass(frozen=True)
class PreviousReading:
    measured_at: datetime
    water_level_cm: float | None


@dataclass(frozen=True)
class AlertDecision:
    alert_type: str
    active: bool
    severity: str
    message: str


def evaluate_connectivity(connectivity: str) -> list[AlertDecision]:
    return [
        AlertDecision(
            alert_type="offline",
            active=connectivity == "offline",
            severity="warning",
            message="Thiết bị đã mất kết nối.",
        )
    ]


def evaluate_telemetry(
    *,
    measured_at: datetime,
    water_level_cm: float | None,
    rainfall_mm: float,
    sensor_status: str,
    thresholds: ThresholdValues,
    previous: PreviousReading | None,
) -> list[AlertDecision]:
    decisions = [
        AlertDecision(
            alert_type="sensor_error",
            active=sensor_status == "error",
            severity="critical",
            message="Cảm biến mực nước trả về dữ liệu không hợp lệ.",
        )
    ]

    if water_level_cm is not None:
        if water_level_cm >= thresholds.water_critical_cm:
            water_active, water_severity = True, "critical"
        elif water_level_cm >= thresholds.water_warning_cm:
            water_active, water_severity = True, "warning"
        else:
            water_active, water_severity = False, "warning"
        decisions.append(
            AlertDecision(
                alert_type="water_level",
                active=water_active,
                severity=water_severity,
                message=f"Mực nước hiện tại là {water_level_cm:.2f} cm.",
            )
        )

    decisions.append(
        AlertDecision(
            alert_type="heavy_rain",
            active=rainfall_mm >= thresholds.rainfall_warning_mm,
            severity="warning",
            message=f"Lượng mưa trong chu kỳ là {rainfall_mm:.2f} mm.",
        )
    )

    rise_rate = calculate_rise_rate(measured_at, water_level_cm, previous)
    if rise_rate is not None:
        decisions.append(
            AlertDecision(
                alert_type="rapid_rise",
                active=rise_rate >= thresholds.rise_rate_cm_per_min,
                severity=(
                    "critical" if rise_rate >= thresholds.rise_rate_cm_per_min * 2 else "warning"
                ),
                message=f"Mực nước đang tăng {rise_rate:.2f} cm/phút.",
            )
        )
    return decisions


def calculate_rise_rate(
    measured_at: datetime,
    water_level_cm: float | None,
    previous: PreviousReading | None,
) -> float | None:
    if water_level_cm is None or previous is None or previous.water_level_cm is None:
        return None

    previous_time = previous.measured_at
    if previous_time.tzinfo is None:
        previous_time = previous_time.replace(tzinfo=timezone.utc)
    elapsed_seconds = (measured_at - previous_time).total_seconds()
    if elapsed_seconds < 1 or elapsed_seconds > 15 * 60:
        return None
    return max(0.0, water_level_cm - previous.water_level_cm) / elapsed_seconds * 60
