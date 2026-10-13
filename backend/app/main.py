from contextlib import asynccontextmanager
from datetime import datetime
import logging
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.alerts import get_or_create_threshold
from app.models import Alert, Device, Telemetry, Threshold
from app.mqtt_consumer import MqttConsumer
from app.schemas import (
    AlertResponse,
    DeviceResponse,
    HealthResponse,
    TelemetryResponse,
    ThresholdResponse,
    ThresholdUpdate,
)


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
settings = get_settings()


def create_app(start_background_services: bool = True) -> FastAPI:
    consumer = MqttConsumer(settings)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        if start_background_services:
            consumer.start()
        yield
        if start_background_services:
            consumer.stop()

    app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
    app.state.mqtt_consumer = consumer

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    def health(response: Response, db: Session = Depends(get_db)) -> HealthResponse:
        try:
            db.execute(text("SELECT 1"))
            database = "up"
        except SQLAlchemyError:
            database = "down"
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        mqtt_state = "connected" if consumer.connected.is_set() else "disconnected"
        overall = "healthy" if database == "up" and mqtt_state == "connected" else "degraded"
        return HealthResponse(
            status=overall,
            database=database,
            mqtt=mqtt_state,
            version=settings.app_version,
        )

    @app.get("/api/v1/devices/{device_id}", response_model=DeviceResponse, tags=["devices"])
    def get_device(device_id: str, db: Session = Depends(get_db)) -> Device:
        device = db.get(Device, device_id)
        if device is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy thiết bị")
        return device

    @app.get(
        "/api/v1/devices/{device_id}/telemetry/latest",
        response_model=TelemetryResponse,
        tags=["telemetry"],
    )
    def latest_telemetry(device_id: str, db: Session = Depends(get_db)) -> Telemetry:
        row = db.scalar(
            select(Telemetry)
            .where(Telemetry.device_id == device_id)
            .order_by(Telemetry.measured_at.desc(), Telemetry.id.desc())
            .limit(1)
        )
        if row is None:
            raise HTTPException(status_code=404, detail="Thiết bị chưa có telemetry")
        return row

    @app.get(
        "/api/v1/devices/{device_id}/telemetry",
        response_model=list[TelemetryResponse],
        tags=["telemetry"],
    )
    def telemetry_history(
        device_id: str,
        from_time: Annotated[datetime | None, Query(alias="from")] = None,
        to_time: Annotated[datetime | None, Query(alias="to")] = None,
        limit: Annotated[int, Query(ge=1, le=1000)] = 100,
        db: Session = Depends(get_db),
    ) -> list[Telemetry]:
        statement = select(Telemetry).where(Telemetry.device_id == device_id)
        if from_time is not None:
            statement = statement.where(Telemetry.measured_at >= from_time)
        if to_time is not None:
            statement = statement.where(Telemetry.measured_at <= to_time)
        statement = statement.order_by(Telemetry.measured_at.desc()).limit(limit)
        return list(db.scalars(statement))

    @app.get(
        "/api/v1/devices/{device_id}/alerts",
        response_model=list[AlertResponse],
        tags=["alerts"],
    )
    def alert_history(
        device_id: str,
        active_only: bool = False,
        limit: Annotated[int, Query(ge=1, le=1000)] = 100,
        db: Session = Depends(get_db),
    ) -> list[Alert]:
        statement = select(Alert).where(Alert.device_id == device_id)
        if active_only:
            statement = statement.where(Alert.ended_at.is_(None))
        statement = statement.order_by(Alert.started_at.desc(), Alert.id.desc()).limit(limit)
        return list(db.scalars(statement))

    @app.get(
        "/api/v1/devices/{device_id}/thresholds",
        response_model=ThresholdResponse,
        tags=["alerts"],
    )
    def get_thresholds(device_id: str, db: Session = Depends(get_db)) -> Threshold:
        if db.get(Device, device_id) is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy thiết bị")
        threshold = get_or_create_threshold(db, device_id)
        db.commit()
        db.refresh(threshold)
        return threshold

    @app.put(
        "/api/v1/devices/{device_id}/thresholds",
        response_model=ThresholdResponse,
        tags=["alerts"],
    )
    def update_thresholds(
        device_id: str,
        update: ThresholdUpdate,
        db: Session = Depends(get_db),
    ) -> Threshold:
        if db.get(Device, device_id) is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy thiết bị")
        threshold = get_or_create_threshold(db, device_id)
        for field, value in update.model_dump().items():
            setattr(threshold, field, value)
        db.commit()
        db.refresh(threshold)
        return threshold

    return app


app = create_app()
