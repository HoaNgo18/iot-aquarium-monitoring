# Hệ thống IoT giám sát bể nuôi cá

Đồ án tốt nghiệp của Ngô Tuấn Hòa — MSSV 20225189.

Phiên bản 0.2 chuyển nền tảng giám sát ngập sang giám sát **pH, nhiệt độ nước và độ đục tương đối**.
Đã nạp esp32-fake lên ESP32 thật ngày 22/10; Wi-Fi 2.4 GHz → MQTT → PostgreSQL/REST → web realtime và một chu kỳ cảnh báo độ đục đã đạt.
Driver DS18B20/analog đã build nhưng chưa kiểm chứng cảm biến thật.

Bản nguồn chính duy nhất: `D:\DATN\iot-aquarium`; frontend đã hợp nhất UI AquaSense xanh biển vào Vue.
Xem [biên bản hợp nhất](docs/consolidation-2026-10-23.md). Các preview 4173/4174 đã ngừng; dùng cổng 5173.

## Phạm vi hiện tại

- MQTT ingestion, kiểm tra dữ liệu và chống bản tin trùng.
- PostgreSQL, REST latest/history, trạng thái thiết bị và ngưỡng cấu hình.
- Cảnh báo nhiệt độ/pH ngoài khoảng, độ đục cao, cảm biến lỗi và offline.
- Vue 3 dashboard, ba chỉ số, lịch sử 15 phút/1/6/24 giờ và danh sách cảnh báo.
- WebSocket với heartbeat, reconnect và đồng bộ bù bằng REST.
- Form cấu hình ngưỡng, xác nhận cảnh báo và cảnh báo mẫu quá cũ trên dashboard.
- Firmware có PIR phát hiện người bật LED tùy chọn, mặc định tắt; phần nước vẫn là MVP.

Stack: ESP32/PlatformIO, Mosquitto, FastAPI, SQLAlchemy/Alembic, PostgreSQL, Vue 3/TypeScript, Docker Compose.

## Chạy bằng Docker Compose

Yêu cầu Docker Desktop ở chế độ Linux containers đang chạy.

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
docker compose up -d --build
docker compose ps
```

- Web: http://localhost:5173 — mặc định chọn `tank-demo-001`.
- API: http://localhost:8000/docs.
- Nếu cổng MQTT 1883 đã được dùng, đặt `MQTT_HOST_PORT=1884` trong `.env`.

Repository GitHub và Compose project dùng tên **iot-aquarium-monitoring**.
Repository: [HoaNgo18/iot-aquarium-monitoring](https://github.com/HoaNgo18/iot-aquarium-monitoring).
Các container có tên `iot-aquarium-monitoring-{service}-1`.

Thư mục local hiện tại là `D:\DATN\iot-aquarium`. Database/user được giữ nguyên để bảo toàn dữ liệu.
File local `compose.override.yaml` (không commit) gắn lại hai volume dữ liệu cũ ở chế độ external;
đây là chủ ý bảo toàn dữ liệu, không phải container còn mang tên cũ.
Clone mới không cần override này và sẽ tạo volume theo tên project mới.
Xem [hướng dẫn đổi tên](docs/project-rename-2026-10-22.md); không xóa volume để đổi đề tài.

Khi backend khởi động, Alembic chạy đến `0002_aquarium_monitoring`, tạo ba bảng mới
`aquarium_telemetry`, `aquarium_thresholds`, `aquarium_alerts`.
Các bảng ngập cũ `telemetry`, `thresholds`, `alerts` được giữ nguyên, không đổi đơn vị hoặc xóa dữ liệu.
API hiện tại chỉ đọc bảng aquarium; danh mục thiết bị vẫn dùng chung bảng `devices`.

## Phát dữ liệu giả lập

```powershell
docker compose --profile simulator run --rm -e SIMULATOR_MESSAGE_COUNT=10 -e PUBLISH_INTERVAL_SECONDS=1 simulator
```

Mô phỏng cảnh báo độ đục:

```powershell
docker compose --profile simulator run --rm -e SIMULATOR_SCENARIO=turbidity-high -e SIMULATOR_MESSAGE_COUNT=5 simulator
```

Kịch bản: `normal`, `temperature-low`, `temperature-high`, `ph-low`, `ph-high`,
`turbidity-high`, `sensor-error`, `offline`.
Simulator gửi offline khi dừng; dashboard giữ lại số đo cuối với chú thích.

Nếu `.env` cũ đặt `SIMULATOR_DEVICE_ID=node-001`, đổi thành `tank-001` hoặc chọn đúng mã trên dashboard.
Nếu `.env` đặt kịch bản ngập cũ, đổi thành một kịch bản bên trên.

## Hợp đồng MQTT v2

Firmware và hướng dẫn build/flash: [firmware/README.md](firmware/README.md).
ESP32 fake mặc định dùng `tank-demo-001`, chọn ID đó trên web để tách dữ liệu demo khỏi bể thật.

Topic: `aquarium-monitoring/devices/{device_id}/telemetry`.

```json
{
  "schema_version": 2,
  "device_id": "tank-001",
  "timestamp": "2026-10-19T10:00:00Z",
  "sequence": 1,
  "temperature_c": 27.4,
  "ph": 7.2,
  "turbidity_pct": 18.0,
  "signal_strength_dbm": -61,
  "sensor_status": "normal"
}
```

- `turbidity_pct`: chỉ số tương đối đã chuẩn hóa; 0 là trong, 100 là đục. **Không phải NTU**.
  Việc chuyển ADC/điện áp sang chỉ số này phải hiệu chuẩn sau khi chốt phần cứng.
- Cả ba trường đo bắt buộc có trong payload. Trường lỗi nhận `null`; các trường còn lại vẫn giữ giá trị.
- `sensor_status=error` khi và chỉ khi ít nhất một trường đo là `null`.
- Không chấp nhận NaN, infinity, dữ liệu ngoài miền hợp lệ, trường lạ hoặc schema v1.
- Topic status: `aquarium-monitoring/devices/{device_id}/status`, payload v2 gồm
  `device_id`, `timestamp`, `connectivity=online|offline`.
- Publisher dùng QoS 1; telemetry không retained. Status/Last Will retained.
- Thời điểm mở/đóng cảnh báo kết nối dùng giờ backend tiếp nhận; offline không cập nhật lùi last_seen_at theo timestamp Last Will.
- Ngưỡng mặc định chỉ dùng kiểm thử, chưa phải khuyến nghị nuôi cá.

## Kiểm thử

```powershell
python -m pip install -r backend/requirements-test.txt
cd backend
python -m unittest discover -s tests -v
cd ../simulator
python -m unittest discover -s tests -v
cd ../frontend
npm ci
npm run build
```

Sau khi Compose chạy:

```powershell
python scripts/smoke_test.py
```

Backend/API test dùng SQLite tạm; không thay thế kiểm chứng migration và pipeline trên PostgreSQL/MQTT thật.

## Tài liệu và bước tiếp theo

- [Plan và bàn giao hiện tại](docs/plan.md)
- [Kiến trúc và hợp đồng dữ liệu](docs/architecture.md)
- [Danh sách phần cứng](docs/bom.md)
- [Nhận hàng, đấu nối dự kiến và hiệu chuẩn](docs/hardware-bringup.md)
- [Backend](backend/README.md), [Frontend](frontend/README.md), [Simulator](simulator/README.md)
- [Firmware ESP32](firmware/README.md) và [kiểm thử trên board](docs/firmware-test-plan.md)
- [Quyết định chuyển đổi](docs/decisions/0002-aquarium-transition.md)
- [Nguồn tham khảo](docs/references.md)

Bước tiếp theo: chạy lại Compose/smoke test, flash và xác minh firmware ESP32, tích hợp và hiệu chuẩn cảm biến,
sau đó thu dữ liệu thực nghiệm và viết báo cáo.
