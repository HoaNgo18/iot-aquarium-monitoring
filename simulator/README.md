# Aquarium telemetry simulator v2

Phát dữ liệu giả qua MQTT để phát triển khi chưa có cảm biến.

## Docker

```powershell
docker compose --profile simulator run --rm -e SIMULATOR_SCENARIO=normal -e SIMULATOR_MESSAGE_COUNT=10 simulator
```

## Python

```powershell
python -m pip install -r simulator/requirements.txt
python simulator/simulator.py --host localhost --port 1884 --device-id tank-001 --scenario ph-high --count 5 --interval 1
python -m unittest discover -s simulator/tests -v
```

Port phải khớp MQTT_HOST_PORT. Không dùng localhost làm host trong firmware ESP32; dùng IPv4 LAN của máy chủ.

| Kịch bản | Hành vi |
| --- | --- |
| normal | Nhiệt độ 26–28 °C, pH 6.8–7.4, độ đục 10–25% |
| temperature-low / temperature-high | Nhiệt độ ngoài ngưỡng demo |
| ph-low / ph-high | pH ngoài ngưỡng demo |
| turbidity-high | Độ đục tương đối 85–95% |
| sensor-error | Mỗi mẫu thứ ba có một chỉ số null; luân phiên pH/nhiệt độ/độ đục |
| offline | Chỉ gửi trạng thái offline, không có telemetry |

SCENARIO default normal; DEVICE_ID default tank-001; interval default 5 giây; count=0 chạy liên tục.
Seed default 2026 giúp tái lập số đo. Timestamp dùng UTC; sequence tăng từ 1 mỗi phiên.

Topic telemetry/status: aquarium-monitoring/devices/{device_id}/telemetry và /status.
Payload schema v2 xem [README chính](../README.md).
Telemetry QoS 1, không retained. Status online/offline và Last Will retained; khi thoát gửi offline.
Không publish vào namespace flood-monitoring cũ.
