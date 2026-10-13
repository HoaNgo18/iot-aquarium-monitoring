from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Telemetry
from app.repositories.telemetry import get_history, get_latest
from app.schemas import TelemetryResponse


router = APIRouter(prefix="/api/v1/devices", tags=["telemetry"])


@router.get("/{device_id}/telemetry/latest", response_model=TelemetryResponse)
def latest_telemetry(device_id: str, db: Session = Depends(get_db)) -> Telemetry:
    row = get_latest(db, device_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Thiết bị chưa có telemetry")
    return row


@router.get("/{device_id}/telemetry", response_model=list[TelemetryResponse])
def telemetry_history(
    device_id: str,
    from_time: Annotated[datetime | None, Query(alias="from")] = None,
    to_time: Annotated[datetime | None, Query(alias="to")] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    db: Session = Depends(get_db),
) -> list[Telemetry]:
    return get_history(db, device_id, from_time, to_time, limit)
