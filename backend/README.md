# Backend

FastAPI nhận telemetry/status từ Mosquitto, kiểm tra schema v1, lưu PostgreSQL và cung cấp REST API.

## Endpoint hiện có

- `GET /health`
- `GET /api/v1/devices/{device_id}`
- `GET /api/v1/devices/{device_id}/telemetry/latest`
- `GET /api/v1/devices/{device_id}/telemetry?from=...&to=...&limit=100`
- `GET /api/v1/devices/{device_id}/alerts?active_only=true`
- `GET/PUT /api/v1/devices/{device_id}/thresholds`
- `WS /ws` hoặc `WS /ws?device_id=node-001`
- Swagger UI: `GET /docs`

Cảnh báo hiện có: mực nước vượt ngưỡng, mực nước tăng nhanh, mưa lớn, lỗi cảm biến và thiết bị offline. Một cảnh báo đang mở sẽ được cập nhật thay vì tạo lặp; khi điều kiện trở lại bình thường, backend điền `ended_at`.

WebSocket gửi sự kiện `telemetry`, `status` và `alerts` sau khi bản tin MQTT đã được kiểm tra và lưu thành công. Sự kiện `alerts` chứa snapshot các cảnh báo đang mở của thiết bị, giúp frontend đồng bộ lại trạng thái mà không phải tự ghép các thay đổi.

Smoke-test client nằm tại `scripts/websocket_probe.py`; script chờ telemetry và cảnh báo mực nước trong tối đa 20 giây. Toàn bộ pipeline được kiểm tra từ thư mục gốc bằng `python scripts/smoke_test.py`.

## Cấu trúc mã nguồn

- `app/api/`: REST và WebSocket route.
- `app/domain/`: quy tắc cảnh báo thuần, không truy cập database.
- `app/repositories/`: truy vấn và ghi dữ liệu SQLAlchemy.
- `app/services/`: điều phối quy tắc nghiệp vụ với persistence.
- `app/ingest.py`: điều phối xử lý một bản tin MQTT.
- `app/main.py`: application factory và vòng đời các background service.
- `tests/`: test tự động; `scripts/`: công cụ kiểm tra thủ công.

## Chạy bằng Docker Compose

```powershell
docker compose up -d --build backend
docker compose ps
Invoke-RestMethod http://localhost:8000/health
```

Gửi dữ liệu thử bằng simulator:

```powershell
docker compose --profile simulator run --rm `
  -e SIMULATOR_MESSAGE_COUNT=5 `
  -e PUBLISH_INTERVAL_SECONDS=0.5 `
  simulator

Invoke-RestMethod http://localhost:8000/api/v1/devices/node-001/telemetry/latest
```

Migration được chạy tự động bằng `alembic upgrade head` trước khi API khởi động.
