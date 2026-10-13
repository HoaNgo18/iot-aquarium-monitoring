from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Device
from app.repositories.devices import get_device
from app.schemas import DeviceResponse


router = APIRouter(prefix="/api/v1/devices", tags=["devices"])


@router.get("/{device_id}", response_model=DeviceResponse)
def read_device(device_id: str, db: Session = Depends(get_db)) -> Device:
    device = get_device(db, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy thiết bị")
    return device
