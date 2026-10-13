from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Device(Base):
    __tablename__ = "devices"
    __table_args__ = (
        CheckConstraint("connectivity IN ('online', 'offline')", name="ck_devices_connectivity"),
        CheckConstraint("sensor_status IN ('normal', 'error')", name="ck_devices_sensor_status"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    connectivity: Mapped[str] = mapped_column(String(16), default="offline", nullable=False)
    sensor_status: Mapped[str] = mapped_column(String(16), default="normal", nullable=False)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    telemetry: Mapped[list[Telemetry]] = relationship(back_populates="device")
    threshold: Mapped[Threshold | None] = relationship(back_populates="device")


class Telemetry(Base):
    __tablename__ = "telemetry"
    __table_args__ = (
        UniqueConstraint(
            "device_id", "sequence", "measured_at", name="uq_telemetry_device_sample"
        ),
        Index("ix_telemetry_device_measured", "device_id", "measured_at"),
        CheckConstraint("sensor_status IN ('normal', 'error')", name="ck_telemetry_sensor_status"),
        CheckConstraint("water_level_cm IS NULL OR water_level_cm >= 0", name="ck_water_level_nonnegative"),
        CheckConstraint("rainfall_mm >= 0", name="ck_rainfall_nonnegative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    water_level_cm: Mapped[float | None] = mapped_column(Float)
    rainfall_mm: Mapped[float] = mapped_column(Float, nullable=False)
    signal_strength_dbm: Mapped[int] = mapped_column(Integer, nullable=False)
    sensor_status: Mapped[str] = mapped_column(String(16), nullable=False)

    device: Mapped[Device] = relationship(back_populates="telemetry")


class Threshold(Base):
    __tablename__ = "thresholds"
    __table_args__ = (
        CheckConstraint("water_warning_cm >= 0", name="ck_threshold_warning_nonnegative"),
        CheckConstraint("water_critical_cm > water_warning_cm", name="ck_threshold_critical_gt_warning"),
    )

    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), primary_key=True)
    water_warning_cm: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    water_critical_cm: Mapped[float] = mapped_column(Float, default=70.0, nullable=False)
    rise_rate_cm_per_min: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    rainfall_warning_mm: Mapped[float] = mapped_column(Float, default=20.0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    device: Mapped[Device] = relationship(back_populates="threshold")


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        CheckConstraint("severity IN ('warning', 'critical')", name="ck_alerts_severity"),
        Index("ix_alerts_device_started", "device_id", "started_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), nullable=False)
    alert_type: Mapped[str] = mapped_column(String(32), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
