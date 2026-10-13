# Backend

FastAPI nhận telemetry/status từ Mosquitto, kiểm tra schema v1, lưu PostgreSQL và cung cấp REST API.

## Endpoint hiện có

- `GET /health`
- `GET /api/v1/devices/{device_id}`
- `GET /api/v1/devices/{device_id}/telemetry/latest`
- `GET /api/v1/devices/{device_id}/telemetry?from=...&to=...&limit=100`
- Swagger UI: `GET /docs`

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
