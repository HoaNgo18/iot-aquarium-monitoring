from __future__ import annotations

import asyncio
from collections.abc import Callable
import json
import logging
from typing import Any

from fastapi import WebSocket
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ingest import TOPIC_PATTERN
from app.models import Alert


logger = logging.getLogger(__name__)


class RealtimeHub:
    """Quản lý WebSocket trên event loop FastAPI và nhận sự kiện từ thread MQTT."""

    def __init__(self) -> None:
        self._connections: dict[WebSocket, str | None] = {}
        self._loop: asyncio.AbstractEventLoop | None = None

    def bind_running_loop(self) -> None:
        self._loop = asyncio.get_running_loop()

    def unbind_loop(self) -> None:
        self._loop = None

    async def connect(self, websocket: WebSocket, device_id: str | None = None) -> None:
        await websocket.accept()
        self._connections[websocket] = device_id
        await websocket.send_json(
            {"type": "connected", "device_id": device_id, "data": {"message": "WebSocket connected"}}
        )

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.pop(websocket, None)

    async def broadcast(self, event: dict[str, Any]) -> None:
        failed: list[WebSocket] = []
        for websocket, device_filter in list(self._connections.items()):
            if device_filter is not None and event.get("device_id") != device_filter:
                continue
            try:
                await websocket.send_json(event)
            except Exception:
                failed.append(websocket)

        for websocket in failed:
            self.disconnect(websocket)

    def publish_from_thread(self, event: dict[str, Any]) -> None:
        loop = self._loop
        if loop is None or loop.is_closed():
            logger.debug("Bỏ qua realtime event vì FastAPI event loop chưa sẵn sàng")
            return
        asyncio.run_coroutine_threadsafe(self.broadcast(event), loop)


def build_realtime_events(
    topic: str,
    raw_payload: bytes,
    session_factory: Callable[[], Session],
) -> list[dict[str, Any]]:
    match = TOPIC_PATTERN.fullmatch(topic)
    if match is None:
        return []

    document = json.loads(raw_payload)
    device_id = match.group("device_id")
    events: list[dict[str, Any]] = [
        {
            "type": match.group("kind"),
            "device_id": device_id,
            "data": document,
        }
    ]

    with session_factory() as session:
        alerts = list(
            session.scalars(
                select(Alert)
                .where(Alert.device_id == device_id, Alert.ended_at.is_(None))
                .order_by(Alert.started_at.desc(), Alert.id.desc())
            )
        )

    events.append(
        {
            "type": "alerts",
            "device_id": device_id,
            "data": [
                {
                    "id": alert.id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "message": alert.message,
                    "started_at": alert.started_at.isoformat(),
                }
                for alert in alerts
            ],
        }
    )
    return events
