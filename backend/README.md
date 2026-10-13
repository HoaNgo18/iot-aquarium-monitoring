# Backend

FastAPI nhận telemetry/status từ Mosquitto, kiểm tra schema v1, lưu PostgreSQL và cung cấp REST API.

## Endpoint hiện có

- `GET /health`
- `GET /api/v1/devices/{device_id}`
- `GET /api/v1/devices/{device_id}/telemetry/latest`
- `GET /api/v1/devices/{device_id}/telemetry?from=...&to=...&limit=100`
- `GET /api/v1/devices/{device_id}/alerts?active_only=true`
- `GET/PUT /api/v1/devices/{device_id}/thresholds`
- Swagger UI: `GET /docs`

Cảnh báo hiện có: mực nước vượt ngưỡng, mực nước tăng nhanh, mưa lớn, lỗi cảm biến và thiết bị offline. Một cảnh báo đang mở sẽ được cập nhật thay vì tạo lặp; khi điều kiện trở lại bình thường, backend điền `ended_at`.

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
