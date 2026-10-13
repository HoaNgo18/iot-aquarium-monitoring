from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.alert_rules import AlertDecision
from app.models import Alert, Threshold


def get_or_create_threshold(session: Session, device_id: str) -> Threshold:
    threshold = session.get(Threshold, device_id)
    if threshold is None:
        threshold = Threshold(device_id=device_id)
        session.add(threshold)
        session.flush()
    return threshold


def get_active_alert(session: Session, device_id: str, alert_type: str) -> Alert | None:
    return session.scalar(
        select(Alert)
        .where(
            Alert.device_id == device_id,
            Alert.alert_type == alert_type,
            Alert.ended_at.is_(None),
        )
        .order_by(Alert.started_at.desc(), Alert.id.desc())
        .limit(1)
    )


def apply_decision(
    session: Session,
    device_id: str,
    decision: AlertDecision,
    occurred_at: datetime,
) -> None:
    current = get_active_alert(session, device_id, decision.alert_type)
    if decision.active:
        if current is None:
            session.add(
                Alert(
                    device_id=device_id,
                    alert_type=decision.alert_type,
                    severity=decision.severity,
                    message=decision.message,
                    started_at=occurred_at,
                )
            )
        else:
            current.severity = decision.severity
            current.message = decision.message
    elif current is not None:
        current.ended_at = occurred_at


def list_alerts(
    session: Session,
    device_id: str,
    active_only: bool,
    limit: int,
) -> list[Alert]:
    statement = select(Alert).where(Alert.device_id == device_id)
    if active_only:
        statement = statement.where(Alert.ended_at.is_(None))
    statement = statement.order_by(Alert.started_at.desc(), Alert.id.desc()).limit(limit)
    return list(session.scalars(statement))
