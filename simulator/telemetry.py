"""Sinh dữ liệu telemetry có thể tái lập cho các kịch bản thử nghiệm."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import random
from typing import Any, Callable


SCENARIOS = ("normal", "heavy-rain", "flood", "sensor-error", "offline")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


@dataclass
class TelemetryGenerator:
    """Giữ trạng thái mô phỏng giữa các lần lấy mẫu."""

    device_id: str
    scenario: str = "normal"
    seed: int | None = None
    clock: Callable[[], str] = utc_now

    def __post_init__(self) -> None:
        if self.scenario not in SCENARIOS:
            raise ValueError(f"Kịch bản không hợp lệ: {self.scenario}")

        self._random = random.Random(self.seed)
        self._sequence = 0
        self._water_level_cm = {
            "normal": 18.0,
            "heavy-rain": 28.0,
            "flood": 68.0,
            "sensor-error": 20.0,
            "offline": 20.0,
        }[self.scenario]

    def next_payload(self) -> dict[str, Any]:
        """Trả về bản tin telemetry kế tiếp của kịch bản."""

        self._sequence += 1

        if self.scenario == "normal":
            self._water_level_cm = self._bounded(
                self._water_level_cm + self._random.uniform(-0.35, 0.35), 12.0, 25.0
            )
            rainfall_mm = self._random.uniform(0.0, 0.8)
        elif self.scenario == "heavy-rain":
            self._water_level_cm = self._bounded(
                self._water_level_cm + self._random.uniform(0.8, 2.2), 0.0, 100.0
            )
            rainfall_mm = self._random.uniform(8.0, 20.0)
        elif self.scenario == "flood":
            self._water_level_cm = self._bounded(
                self._water_level_cm + self._random.uniform(4.0, 8.0), 0.0, 150.0
            )
            rainfall_mm = self._random.uniform(20.0, 40.0)
        else:
            self._water_level_cm = self._bounded(
                self._water_level_cm + self._random.uniform(-0.2, 0.2), 0.0, 100.0
            )
            rainfall_mm = self._random.uniform(0.0, 1.0)

        sensor_status = "normal"
        water_level_cm: float | None = round(self._water_level_cm, 2)
        if self.scenario == "sensor-error" and self._sequence % 3 == 0:
            sensor_status = "error"
            water_level_cm = None

        return {
            "schema_version": 1,
            "device_id": self.device_id,
            "timestamp": self.clock(),
            "sequence": self._sequence,
            "water_level_cm": water_level_cm,
            "rainfall_mm": round(rainfall_mm, 2),
            "signal_strength_dbm": self._random.randint(-78, -48),
            "sensor_status": sensor_status,
        }

    @staticmethod
    def _bounded(value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(value, maximum))


def status_payload(device_id: str, connectivity: str) -> dict[str, Any]:
    if connectivity not in {"online", "offline"}:
        raise ValueError("connectivity phải là online hoặc offline")

    return {
        "schema_version": 1,
        "device_id": device_id,
        "timestamp": utc_now(),
        "connectivity": connectivity,
    }
