from typing import Literal

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas import HealthResponse


router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health(request: Request, response: Response, db: Session = Depends(get_db)) -> HealthResponse:
    try:
        db.execute(text("SELECT 1"))
        database: Literal["up", "down"] = "up"
    except SQLAlchemyError:
        database = "down"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    mqtt_state: Literal["connected", "disconnected"] = (
        "connected" if request.app.state.mqtt_consumer.connected.is_set() else "disconnected"
    )
    overall: Literal["healthy", "degraded"] = (
        "healthy" if database == "up" and mqtt_state == "connected" else "degraded"
    )
    return HealthResponse(
        status=overall,
        database=database,
        mqtt=mqtt_state,
        version=get_settings().app_version,
    )
