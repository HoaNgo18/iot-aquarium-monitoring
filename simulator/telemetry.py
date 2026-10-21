"""Sinh telemetry bể cá v2 có thể tái lập; không giả lập đơn vị NTU."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import random
from typing import Any, Callable


SCENARIOS = (
    "normal", "temperature-low", "temperature-high",
    "ph-low", "ph-high", "turbidity-high", "sensor-error", "offline",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


@dataclass
class TelemetryGenerator:
    device_id: str
    scenario: str = "normal"
    seed: int | None = None
    clock: Callable[[], str] = utc_now

    def __post_init__(self) -> None:
        if self.scenario not in SCENARIOS:
            raise ValueError(f"Kịch bản không hợp lệ: {self.scenario}")
        self._random = random.Random(self.seed)
        self._sequence = 0

    def next_payload(self) -> dict[str, Any]:
        self._sequence += 1
        temperature: float | None = round(self._random.uniform(26.0, 28.0), 2)
        ph: float | None = round(self._random.uniform(6.8, 7.4), 2)
        turbidity: float | None = round(self._random.uniform(10.0, 25.0), 2)
        if self.scenario == "temperature-low":
            temperature = round(self._random.uniform(17.0, 19.0), 2)
        elif self.scenario == "temperature-high":
            temperature = round(self._random.uniform(33.0, 35.0), 2)
        elif self.scenario == "ph-low":
            ph = round(self._random.uniform(5.0, 5.8), 2)
        elif self.scenario == "ph-high":
            ph = round(self._random.uniform(9.0, 10.0), 2)
        elif self.scenario == "turbidity-high":
            turbidity = round(self._random.uniform(85.0, 95.0), 2)

        status = "normal"
        if self.scenario == "sensor-error" and self._sequence % 3 == 0:
            status = "error"
            # Rotate failed probes; keep the remaining measurements valid.
            probe = (self._sequence // 3 - 1) % 3
            if probe == 0:
                ph = None
            elif probe == 1:
                temperature = None
            else:
                turbidity = None

        return {
            "schema_version": 2,
            "device_id": self.device_id,
            "timestamp": self.clock(),
            "sequence": self._sequence,
            "temperature_c": temperature,
            "ph": ph,
            "turbidity_pct": turbidity,
            "signal_strength_dbm": self._random.randint(-78, -48),
            "sensor_status": status,
        }


def status_payload(device_id: str, connectivity: str) -> dict[str, Any]:
    if connectivity not in {"online", "offline"}:
        raise ValueError("connectivity phải là online hoặc offline")
    return {
        "schema_version": 2,
        "device_id": device_id,
        "timestamp": utc_now(),
        "connectivity": connectivity,
    }
