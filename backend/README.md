# Aquarium Monitoring Backend

FastAPI, SQLAlchemy/Alembic, PostgreSQL, Paho MQTT và WebSocket.

## Hợp đồng dữ liệu

Đọc payload mẫu và quy tắc lỗi trong [README chính](../README.md#hợp-đồng-mqtt-v2).
Chỉ subscribe `aquarium-monitoring/devices/+/telemetry` và `aquarium-monitoring/devices/+/status`.
Mỗi lần MQTT reconnect, consumer subscribe lại topic.
`schema_version=2`; trạng thái cảm biến tổng hợp phải khớp với các trường đo `null`.

## API

| Endpoint | Chức năng |
| --- | --- |
| GET /health | Kiểm tra database/MQTT |
| GET /api/v1/devices/{id} | Trạng thái thiết bị |
| GET /api/v1/devices/{id}/telemetry/latest | Số đo mới nhất |
| GET /api/v1/devices/{id}/telemetry | Lịch sử: from, to theo ISO 8601; limit 1–1000; mới nhất trước |
| GET /api/v1/devices/{id}/alerts | Cảnh báo: active_only và limit |
| POST /api/v1/devices/{id}/alerts/{alert_id}/acknowledge | Xác nhận cảnh báo thuộc đúng thiết bị; gọi lặp giữ timestamp đầu tiên |
| GET /api/v1/devices/{id}/thresholds | Đọc ngưỡng |
| PUT /api/v1/devices/{id}/thresholds | Ghi ngưỡng cho các mẫu tiếp theo |
| WS /ws?device_id={id} | telemetry/status/alerts; text ping nhận JSON pong |

Ngưỡng mặc định phục vụ demo:
`temperature_min_c=22`, `temperature_max_c=30`, `ph_min=6.5`, `ph_max=8.5`,
`turbidity_warning_pct=60`, `turbidity_critical_pct=80`.
PUT gửi đầy đủ sáu trường nếu muốn giữ các giá trị khác; trường bỏ qua nhận default.
Cần điều chỉnh theo loài và cảm biến thực tế, không sử dụng mặc định như chuẩn chung.
Xác nhận không đóng hoặc mở lại cảnh báo. API trả 404 nếu ID không tồn tại/không thuộc thiết bị.
Thao tác xác nhận/lưu ngưỡng hiện trả kết quả cho client gọi REST; chưa broadcast riêng tới tab khác,
tab khác thấy khi tải lại hoặc nhận đợt telemetry/status tiếp theo.

Luật cảnh báo:
- Nhiệt độ/pH ngoài khoảng cấu hình: warning. Hai cận thuộc khoảng bình thường.
- Độ đục từ ngưỡng warning: warning; từ ngưỡng critical: critical.
- Số đo lỗi: sensor_error critical, thông báo tên chỉ số bị thiếu.
- Bỏ qua luật giá trị của cảm biến đang lỗi; không tự đóng cảnh báo giá trị cũ khi chưa có số đo phục hồi.
- Telemetry hợp lệ hoặc status online đóng offline alert.
- Một cảnh báo đang mở được cập nhật, không tạo lại sau một khoảng cooldown.
- Chưa có bộ giám sát tuổi mẫu phía server: cảnh báo offline hiện dựa trên status/Last Will MQTT.

## Persistence và migration

`0001_initial_schema` giữ nguyên lịch sử. `0002_aquarium_monitoring` thêm ba bảng aquarium, dùng chung devices.
Không chuyển mực nước thành nhiệt độ hoặc lượng mưa thành độ đục.
Để giữ nguyên hạ tầng, DATABASE_URL mặc định vẫn trỏ database tên cũ `flood_monitoring`.

```powershell
docker compose up -d --build backend
docker compose exec backend alembic current
```

Không dùng `Base.metadata.create_all` cho triển khai PostgreSQL; migration là nguồn quản lý schema.
Nếu tạo migration bằng autogenerate sau này, phải loại các bảng ngập lưu trữ khỏi thao tác drop.

## Kiểm thử cục bộ

```powershell
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests -v
```

Test bao gồm schema, luật thuần, ingest/chống trùng, vòng đời cảnh báo, REST/WebSocket,
simulator → ingest → API, xác nhận cảnh báo idempotent/cách ly thiết bị và migration bảo toàn dữ liệu ngập mẫu.
SQLite test không thay thế kiểm thử PostgreSQL thật.

Code chia theo `api → services/domain → repositories`. Hub WebSocket chuyển event từ thread Paho
sang event loop FastAPI; client đọc lại REST khi nhận event để lấy ID/timestamp chuẩn.
