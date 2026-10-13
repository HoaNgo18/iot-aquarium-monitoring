from datetime import datetime
from typing import Annotated, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator


DeviceId = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")]


class TelemetryPayload(BaseModel):
    schema_version: Literal[1]
    device_id: DeviceId
    timestamp: AwareDatetime
    sequence: Annotated[int, Field(ge=1)]
    water_level_cm: Annotated[float | None, Field(ge=0, le=1000)]
    rainfall_mm: Annotated[float, Field(ge=0, le=1000)]
    signal_strength_dbm: Annotated[int, Field(ge=-127, le=0)]
    sensor_status: Literal["normal", "error"]

    @model_validator(mode="after")
    def validate_sensor_value(self) -> "TelemetryPayload":
        if self.sensor_status == "normal" and self.water_level_cm is None:
            raise ValueError("water_level_cm là bắt buộc khi sensor_status=normal")
        if self.sensor_status == "error" and self.water_level_cm is not None:
            raise ValueError("water_level_cm phải là null khi sensor_status=error")
        return self


class StatusPayload(BaseModel):
    schema_version: Literal[1]
    device_id: DeviceId
    timestamp: AwareDatetime
    connectivity: Literal["online", "offline"]


class TelemetryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    sequence: int
    measured_at: datetime
    received_at: datetime
    water_level_cm: float | None
    rainfall_mm: float
    signal_strength_dbm: int
    sensor_status: str


class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    connectivity: str
    sensor_status: str
    last_seen_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    alert_type: str
    severity: str
    message: str
    started_at: datetime
    ended_at: datetime | None
    acknowledged_at: datetime | None


class ThresholdUpdate(BaseModel):
    water_warning_cm: Annotated[float, Field(ge=0, le=1000)] = 50.0
    water_critical_cm: Annotated[float, Field(gt=0, le=1000)] = 70.0
    rise_rate_cm_per_min: Annotated[float, Field(gt=0, le=1000)] = 10.0
    rainfall_warning_mm: Annotated[float, Field(ge=0, le=1000)] = 20.0

    @model_validator(mode="after")
    def validate_water_thresholds(self) -> "ThresholdUpdate":
        if self.water_critical_cm <= self.water_warning_cm:
            raise ValueError("water_critical_cm phải lớn hơn water_warning_cm")
        return self


class ThresholdResponse(ThresholdUpdate):
    model_config = ConfigDict(from_attributes=True)

    device_id: str
    updated_at: datetime


class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded"]
    database: Literal["up", "down"]
    mqtt: Literal["connected", "disconnected"]
    version: str
