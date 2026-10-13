"""Client nhỏ dùng cho smoke test WebSocket trong container backend."""

import asyncio
import json
import os
import time

from websockets.asyncio.client import connect


async def main() -> None:
    device_id = os.getenv("WS_DEVICE_ID", "node-websocket-smoke")
    url = os.getenv("WS_URL", f"ws://127.0.0.1:8000/ws?device_id={device_id}")
    deadline = time.monotonic() + 20
    telemetry_received = False
    alert_received = False

    async with connect(url) as websocket:
        while time.monotonic() < deadline:
            timeout = max(0.1, deadline - time.monotonic())
            event = json.loads(await asyncio.wait_for(websocket.recv(), timeout=timeout))
            print(json.dumps(event, ensure_ascii=False), flush=True)
            telemetry_received |= event.get("type") == "telemetry"
            alert_received |= event.get("type") == "alerts" and any(
                alert.get("alert_type") == "water_level" for alert in event.get("data", []))
            if telemetry_received and alert_received:
                print("PASS: WebSocket nhận telemetry và water_level alert.", flush=True)
                return

    raise RuntimeError("WebSocket không nhận đủ telemetry và alert trong 20 giây")


if __name__ == "__main__":
    asyncio.run(main())
