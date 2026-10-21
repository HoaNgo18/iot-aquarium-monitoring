"""CLI gửi dữ liệu cảm biến giả lập tới MQTT broker."""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import threading
import time
from typing import Any

from paho.mqtt import client as mqtt

from telemetry import SCENARIOS, TelemetryGenerator, status_payload


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value is not None else default


def env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return float(value) if value is not None else default


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gửi telemetry pH, nhiệt độ và độ đục tương đối của bể cá qua MQTT."
    )
    parser.add_argument(
        "--scenario",
        choices=SCENARIOS,
        default=os.getenv("SIMULATOR_SCENARIO", "normal"),
    )
    parser.add_argument("--device-id", default=os.getenv("DEVICE_ID", "tank-001"))
    parser.add_argument("--host", default=os.getenv("MQTT_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=env_int("MQTT_PORT", 1884))
    parser.add_argument(
        "--interval",
        type=float,
        default=env_float("PUBLISH_INTERVAL_SECONDS", 5.0),
        help="Khoảng cách giữa hai bản tin, tính bằng giây.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=env_int("SIMULATOR_MESSAGE_COUNT", 0),
        help="Số bản tin cần gửi; 0 nghĩa là chạy liên tục.",
    )
    parser.add_argument("--seed", type=int, default=env_int("SIMULATOR_SEED", 2026))
    args = parser.parse_args()

    if args.interval <= 0:
        parser.error("--interval phải lớn hơn 0")
    if args.count < 0:
        parser.error("--count không được âm")
    if not 1 <= args.port <= 65535:
        parser.error("--port phải nằm trong khoảng 1..65535")
    return args


def encode(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def publish(client: mqtt.Client, topic: str, payload: dict[str, Any], retain: bool) -> None:
    message = encode(payload)
    info = client.publish(topic, message, qos=1, retain=retain)
    info.wait_for_publish(timeout=10)
    print(f"{topic} {message}", flush=True)


def main() -> int:
    args = parse_args()
    telemetry_topic = f"aquarium-monitoring/devices/{args.device_id}/telemetry"
    status_topic = f"aquarium-monitoring/devices/{args.device_id}/status"
    stopped = threading.Event()
    connected = threading.Event()
    offline_published = False

    def request_stop(_signum: int, _frame: object) -> None:
        stopped.set()

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"simulator-{args.device_id}",
        protocol=mqtt.MQTTv311,
    )
    client.will_set(
        status_topic,
        encode(status_payload(args.device_id, "offline")),
        qos=1,
        retain=True,
    )

    def on_connect(
        _client: mqtt.Client,
        _userdata: object,
        _flags: mqtt.ConnectFlags,
        reason_code: mqtt.ReasonCode,
        _properties: mqtt.Properties | None,
    ) -> None:
        if reason_code == 0:
            connected.set()
        else:
            print(f"MQTT từ chối kết nối: {reason_code}", file=sys.stderr, flush=True)

    client.on_connect = on_connect

    try:
        print(f"Kết nối MQTT {args.host}:{args.port}...", flush=True)
        client.connect(args.host, args.port, keepalive=30)
        client.loop_start()
        if not connected.wait(timeout=10):
            raise TimeoutError("Không nhận được xác nhận kết nối MQTT sau 10 giây")

        publish(client, status_topic, status_payload(args.device_id, "online"), True)

        if args.scenario == "offline":
            publish(client, status_topic, status_payload(args.device_id, "offline"), True)
            offline_published = True
            print("Đã mô phỏng thiết bị offline; không gửi telemetry.", flush=True)
            return 0

        generator = TelemetryGenerator(args.device_id, args.scenario, args.seed)
        sent = 0
        while not stopped.is_set() and (args.count == 0 or sent < args.count):
            publish(client, telemetry_topic, generator.next_payload(), False)
            sent += 1
            if args.count == 0 or sent < args.count:
                stopped.wait(args.interval)
        return 0
    except (OSError, RuntimeError, TimeoutError, ValueError) as exc:
        print(f"Simulator lỗi: {exc}", file=sys.stderr, flush=True)
        return 1
    finally:
        if connected.is_set() and not offline_published:
            try:
                publish(client, status_topic, status_payload(args.device_id, "offline"), True)
            except RuntimeError:
                pass
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    raise SystemExit(main())
