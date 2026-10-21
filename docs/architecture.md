# Kiến trúc hệ thống giám sát bể nuôi cá

> Cập nhật: 21/10/2026 — phiên bản phần mềm 0.2, hợp đồng MQTT v2.

## 1. Phạm vi

Một bể với ESP32 thu thập pH, nhiệt độ và độ đục tương đối; web hiển thị dữ liệu, lịch sử và cảnh báo.
Cảm biến chuyển động dùng để phát hiện **người** bật LED, thuộc phần mở rộng sau MVP.
Không suy ra chẩn đoán sức khỏe cá từ ba chỉ số nước.

## 2. Luồng dữ liệu

```text
ESP32 (firmware fake/sensors đã build, chưa flash) hoặc simulator Python
  → Wi-Fi / MQTT / Mosquitto
  → FastAPI MQTT consumer
  → validation → repositories → services/domain → PostgreSQL
  → REST + WebSocket
  → Vue dashboard
```

Topic: `aquarium-monitoring/devices/{id}/telemetry` và `/status`.
Topic và payload device_id phải khớp; mã thiết bị bắt đầu bằng chữ/số, tối đa 64 ký tự.

## 3. Dữ liệu v2

| Trường | Quy ước |
| --- | --- |
| schema_version | 2; từ chối v1 và trường lạ |
| timestamp | ISO 8601 có múi giờ; API phản hồi UTC, web hiển thị giờ Việt Nam |
| sequence | Số nguyên từ 1 |
| temperature_c | -55 đến 125 °C hoặc null; đây là miền kỹ thuật, không phải vùng nuôi cá |
| ph | 0–14 hoặc null |
| turbidity_pct | 0–100 hoặc null; 0 trong, 100 đục; không phải NTU |
| signal_strength_dbm | -127 đến 0 |
| sensor_status | normal nếu cả ba số đo có giá trị; error nếu ít nhất một số đo null |

Không nhận NaN/infinity, không đổi số đo lỗi thành 0. Mỗi sensor có thể lỗi riêng bằng null,
vẫn lưu và xử lý các số đo còn lại.
Hiệu chuẩn ADC/điện áp → pH và độ đục nằm ở firmware dự kiến, sau khi chốt đầu dò.
Payload mẫu đầy đủ nằm trong README chính.

Status v2 có timestamp, device_id và connectivity online/offline.
MQTT consumer subscribe lại mỗi lần kết nối; simulator và firmware ESP32 có Last Will.
Firmware chờ đồng bộ NTP, publish QoS 1, tự nối Wi-Fi/MQTT; chưa có kiểm chứng trên board.
Timestamp Last Will thuộc lúc kết nối: cảnh báo offline dùng giờ backend quan sát,
không thay last_seen_at bằng timestamp cũ. Cảnh báo kết nối đóng theo giờ backend nhận phục hồi.
Replay retained status chưa cho biết chính xác thời điểm sự cố trước lúc backend khởi động.
Chưa có bộ phát hiện quá tuổi mẫu phía server hoặc hàng đợi lưu bù dữ liệu thiết bị.

## 4. Persistence và chuyển đổi từ đề tài ngập

- Giữ nguyên revision 0001 và các bảng devices/telemetry/thresholds/alerts cũ.
- Revision 0002 tạo aquarium_telemetry, aquarium_thresholds, aquarium_alerts; dùng chung devices.
- Không copy/đổi nghĩa số đo hay cảnh báo ngập sang bảng mới.
- Unique (device_id, sequence, measured_at) chống trùng. Index hỗ trợ latest/history theo thiết bị và thời gian.
- API và ORM hiện chỉ sử dụng các bảng aquarium và bảng devices.
- Compose project, volume và tên database giữ nguyên để không tạo bộ dữ liệu khác khi nâng cấp.
- Khi autogenerate migration sau này phải loại các bảng lưu trữ ngập khỏi thao tác xóa.

## 5. Cảnh báo

Luật thuần trong domain/alert_rules.py; service đọc threshold rồi áp dụng quyết định qua repository.
Các loại: temperature, ph, turbidity, sensor_error, offline.
Mặc định demo: nhiệt độ 22–30 °C, pH 6.5–8.5, độ đục cảnh báo 60%, critical 80%.
Các giá trị này là cấu hình phát triển, chưa phải ngưỡng thực nghiệm của một loài cá.

- Nhiệt độ/pH ngoài khoảng: warning.
- Độ đục từ warning/critical: mức tương ứng.
- Sensor error: critical; thông báo chỉ số thiếu.
- Không có số đo thì giữ nguyên cảnh báo giá trị đang mở của chỉ số đó.
- Giá trị phục hồi đóng cảnh báo; telemetry hoặc status online đóng offline.
- Cảnh báo liên tục cập nhật cùng bản ghi đang mở, không tạo trùng theo thời gian.
- PUT thresholds tác động các mẫu tiếp theo, chưa tự tính lại toàn bộ lịch sử.

## 6. API và realtime

REST latest/history, device, alerts và GET/PUT thresholds giữ đường dẫn /api/v1/devices/{id}/...
WebSocket /ws có bộ lọc device_id và heartbeat text ping → JSON pong.
Paho chạy thread riêng; hub chuyển broadcast sang event loop FastAPI.
Sau khi transaction commit, telemetry/status và snapshot cảnh báo đang mở được phát cho client.

Frontend dùng REST làm dữ liệu chuẩn, WebSocket làm tín hiệu tải lại.
Giữ cơ chế gộp burst 100 ms, tối đa một đợt tải mỗi giây; reconnect 1/2/4/8/15 giây,
heartbeat 15 giây, timeout pong 10 giây và đồng bộ bù khi mở lại.
useReadings/useAlerts hủy request cũ khi đổi thiết bị; lịch sử cũng hủy khi đổi khoảng thời gian.
Một backend process là phạm vi MVP; chưa đồng bộ hub giữa nhiều instance.

## 7. Dashboard

- Ba ô nhiệt độ/pH/độ đục và trạng thái thiết bị; responsive desktop/mobile.
- Live biểu thị kết nối web, Online/Offline biểu thị thiết bị.
- Số đo cuối vẫn hiển thị khi offline kèm chú thích; null không thành 0.
- WaterQualityHistory tải tối đa 500 mẫu, chọn 1/6/24 giờ và từng chỉ số.
- Biểu đồ sắp mẫu theo thời gian, đọc đường ngưỡng thật từ API; không nối qua mẫu null.
- Có form cấu hình đủ sáu ngưỡng và thao tác xác nhận cảnh báo; xác nhận không kết thúc điều kiện cảnh báo.
- Tuổi mẫu cập nhật mỗi giây, từ 60 giây báo dữ liệu cũ; timestamp tương lai quá 30 giây báo lệch giờ.
  Đây là chỉ báo frontend, chưa tự đổi trạng thái MQTT hoặc tạo timeout alert phía server.

## 8. Kiểm chứng và giới hạn

Backend có test schema, alert, ingest, simulator → API, WebSocket và migration bảo toàn mẫu ngập.
Kiểm thử cục bộ dùng SQLite tạm. Alembic có thể xuất SQL cho PostgreSQL; vẫn cần chạy migration
và smoke test qua Mosquitto/PostgreSQL thật khi Docker Desktop hoạt động.
Chưa có dữ liệu từ cảm biến thật hoặc kết quả hiệu chuẩn.
Firmware có esp32-fake, esp32-sensors và alias esp32-pending-sensors đều build thành công.
Driver DS18B20 không chặn, ADC1 lọc/hiệu chuẩn hai điểm, chẩn đoán raw mV; pH/độ đục chưa hiệu chuẩn trả null.
PIR→LED chạy cục bộ theo cờ bật riêng, không thêm trường vào schema v2.
Bốn test host kiểm tra mã C++ và 69 payload qua schema/ingestion SQLite; chưa thay kiểm chứng board thật.
Xem firmware/README.md, hardware-bringup.md và firmware-test-plan.md.
