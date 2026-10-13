from sqlalchemy.orm import Session

from app.models import Device


def get_device(session: Session, device_id: str) -> Device | None:
    return session.get(Device, device_id)


def get_or_create_device(session: Session, device_id: str) -> Device:
    device = get_device(session, device_id)
    if device is None:
        device = Device(id=device_id)
        session.add(device)
    return device
