# Telemetry simulator

Simulator thay thế tạm thời ESP32 và cảm biến để backend có dữ liệu MQTT trong khi phần cứng chưa sẵn sàng.

## Kịch bản

| Kịch bản | Hành vi |
| --- | --- |
| `normal` | Mực nước ổn định, lượng mưa thấp |
| `heavy-rain` | Mưa lớn và mực nước tăng dần |
| `flood` | Mực nước tăng nhanh, vượt vùng cảnh báo |
| `sensor-error` | Mỗi bản tin thứ ba có `water_level_cm: null` và trạng thái lỗi |
| `offline` | Gửi trạng thái offline rồi ngắt, không gửi telemetry |

## Chạy bằng Docker Compose

Gửi 5 bản tin bình thường rồi dừng:

```powershell
docker compose --profile simulator run --rm `
  -e SIMULATOR_MESSAGE_COUNT=5 `
  -e PUBLISH_INTERVAL_SECONDS=1 `
  simulator
```

Đổi kịch bản bằng biến `SIMULATOR_SCENARIO`, ví dụ:

```powershell
docker compose --profile simulator run --rm `
  -e SIMULATOR_SCENARIO=flood `
  -e SIMULATOR_MESSAGE_COUNT=5 `
  simulator
```

Không đặt `SIMULATOR_MESSAGE_COUNT` hoặc đặt bằng `0` để chạy liên tục. Nhấn `Ctrl+C` để dừng.

## Chạy trực tiếp bằng Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\simulator\requirements.txt
python .\simulator\simulator.py --scenario normal --count 5
```

Mặc định cách chạy trực tiếp kết nối `localhost:1884`, tương ứng cấu hình `.env` hiện tại. Có thể đổi bằng `--host`, `--port` hoặc các biến `MQTT_HOST`, `MQTT_PORT`.

## Kiểm thử bộ sinh dữ liệu

Các test không cần kết nối MQTT:

```powershell
python -m unittest discover -s .\simulator\tests -v
```
