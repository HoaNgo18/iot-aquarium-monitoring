"""Smoke test đa nền tảng cho pipeline MQTT, REST và WebSocket."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PORT = os.getenv("BACKEND_HOST_PORT", "8000")
BASE_URL = f"http://127.0.0.1:{BACKEND_PORT}"


def configure_console() -> None:
    """Giữ log tiếng Việt đọc được trên cả Windows và môi trường CI."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def compose(*args: str, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "compose", *args],
        cwd=PROJECT_ROOT,
        check=True,
        text=True,
        capture_output=capture_output,
    )


def get_json(path: str) -> object:
    with urlopen(f"{BASE_URL}{path}", timeout=10) as response:
        return json.load(response)


def run_simulator(device_id: str, scenario: str, count: int) -> None:
    compose(
        "--profile",
        "simulator",
        "run",
        "--rm",
        "-e",
        f"DEVICE_ID={device_id}",
        "-e",
        f"SIMULATOR_SCENARIO={scenario}",
        "-e",
        f"SIMULATOR_MESSAGE_COUNT={count}",
        "-e",
        "PUBLISH_INTERVAL_SECONDS=0.2",
        "simulator",
    )


def main() -> int:
    suffix = uuid4().hex[:8]
    rest_device = f"node-rest-smoke-{suffix}"
    ws_device = f"node-ws-smoke-{suffix}"

    health = get_json("/health")
    if not isinstance(health, dict) or health.get("database") != "up":
        raise RuntimeError("Backend không kết nối được PostgreSQL.")

    run_simulator(rest_device, "normal", 3)
    time.sleep(0.5)
    latest = get_json(f"/api/v1/devices/{rest_device}/telemetry/latest")
    history = get_json(f"/api/v1/devices/{rest_device}/telemetry?limit=10")
    if not isinstance(latest, dict) or latest.get("device_id") != rest_device:
        raise RuntimeError("API latest trả về sai device_id.")
    if not isinstance(history, list) or len(history) != 3:
        raise RuntimeError(f"API history phải có 3 bản ghi, nhận được {len(history)}.")

    probe = subprocess.Popen(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "-e",
            f"WS_DEVICE_ID={ws_device}",
            "backend",
            "python",
            "scripts/websocket_probe.py",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        time.sleep(0.5)
        run_simulator(ws_device, "turbidity-high", 2)
        output, _ = probe.communicate(timeout=25)
    except Exception:
        probe.kill()
        probe.wait()
        raise

    if probe.returncode != 0:
        raise RuntimeError(f"WebSocket probe thất bại:\n{output}")
    print(output.rstrip())
    print("PASS: simulator -> MQTT -> backend -> PostgreSQL -> REST/WebSocket hoạt động.")
    return 0


if __name__ == "__main__":
    configure_console()
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
