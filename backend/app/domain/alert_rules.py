from dataclasses import dataclass


@dataclass(frozen=True)
class ThresholdValues:
    temperature_min_c: float
    temperature_max_c: float
    ph_min: float
    ph_max: float
    turbidity_warning_pct: float
    turbidity_critical_pct: float


@dataclass(frozen=True)
class AlertDecision:
    alert_type: str
    active: bool
    severity: str
    message: str


def evaluate_connectivity(connectivity: str) -> list[AlertDecision]:
    return [AlertDecision("offline", connectivity == "offline", "warning", "Thiết bị đã mất kết nối.")]


def evaluate_telemetry(
    *,
    temperature_c: float | None,
    ph: float | None,
    turbidity_pct: float | None,
    sensor_status: str,
    thresholds: ThresholdValues,
) -> list[AlertDecision]:
    missing = [
        label for label, value in (
            ("nhiệt độ", temperature_c), ("pH", ph), ("độ đục", turbidity_pct)
        ) if value is None
    ]
    decisions = [
        AlertDecision(
            "sensor_error", sensor_status == "error", "critical",
            "Không có số đo hợp lệ: " + ", ".join(missing) if missing else "Cảm biến hoạt động bình thường.",
        ),
        *evaluate_connectivity("online"),
    ]
    # Unknown measurements must not close an existing value-based alert.
    if temperature_c is not None:
        decisions.append(AlertDecision(
            "temperature",
            temperature_c < thresholds.temperature_min_c or temperature_c > thresholds.temperature_max_c,
            "warning",
            f"Nhiệt độ nước {temperature_c:.2f} °C; khoảng cấu hình "
            f"{thresholds.temperature_min_c:g}–{thresholds.temperature_max_c:g} °C.",
        ))
    if ph is not None:
        decisions.append(AlertDecision(
            "ph", ph < thresholds.ph_min or ph > thresholds.ph_max, "warning",
            f"pH {ph:.2f}; khoảng cấu hình {thresholds.ph_min:g}–{thresholds.ph_max:g}.",
        ))
    if turbidity_pct is not None:
        decisions.append(AlertDecision(
            "turbidity", turbidity_pct >= thresholds.turbidity_warning_pct,
            "critical" if turbidity_pct >= thresholds.turbidity_critical_pct else "warning",
            f"Chỉ số độ đục tương đối {turbidity_pct:.2f}%; không phải NTU.",
        ))
    return decisions
