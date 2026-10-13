from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alert, Threshold
from app.repositories.alerts import get_or_create_threshold, list_alerts
from app.repositories.devices import get_device
from app.schemas import AlertResponse, ThresholdResponse, ThresholdUpdate


router = APIRouter(prefix="/api/v1/devices", tags=["alerts"])


@router.get("/{device_id}/alerts", response_model=list[AlertResponse])
def alert_history(
    device_id: str,
    active_only: bool = False,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    db: Session = Depends(get_db),
) -> list[Alert]:
    return list_alerts(db, device_id, active_only, limit)


@router.get("/{device_id}/thresholds", response_model=ThresholdResponse)
def get_thresholds(device_id: str, db: Session = Depends(get_db)) -> Threshold:
    if get_device(db, device_id) is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy thiết bị")
    threshold = get_or_create_threshold(db, device_id)
    db.commit()
    db.refresh(threshold)
    return threshold


@router.put("/{device_id}/thresholds", response_model=ThresholdResponse)
def update_thresholds(
    device_id: str,
    update: ThresholdUpdate,
    db: Session = Depends(get_db),
) -> Threshold:
    if get_device(db, device_id) is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy thiết bị")
    threshold = get_or_create_threshold(db, device_id)
    for field, value in update.model_dump().items():
        setattr(threshold, field, value)
    db.commit()
    db.refresh(threshold)
    return threshold
