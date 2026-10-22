# Kiểm chứng Docker/PostgreSQL — 20/10/2026

Ngày theo múi giờ Asia/Saigon. Payload và log container dùng UTC.
Repository: D:\DATN\iot-aquarium. Docker Engine 29.0.1, API phiên bản 0.2.0.

## Môi trường và nâng cấp

Đã build lại backend/frontend/simulator và chạy `docker compose up -d --wait --wait-timeout 120`.
Bốn dịch vụ mqtt, db, backend, frontend đều healthy. Giữ nguyên project/database/volume cũ.
Broker cũ không chạy sau lần đổi thư mục; Compose đã tạo lại container với bind mount từ đường dẫn mới.
Không dùng down -v, xóa database hoặc reset Git.

Trước nâng cấp đã dùng pg_dump định dạng custom và chép backup ra host:
`D:\DATN\.codex_tmp\aquarium-pre-v2-20261020.dump`.
Backup là file cục bộ ngoài repository; giữ lại để phục hồi nếu cần.

## Bảo toàn dữ liệu

Alembic xác nhận `0002_aquarium_monitoring`; có đủ aquarium_telemetry, aquarium_thresholds, aquarium_alerts.
Ngay sau migration và trước phát mẫu mới, count/fingerprint của cả bốn bảng cũ khớp hoàn toàn:

| Bảng | Số bản ghi | MD5 nội dung sắp xếp theo JSON từng dòng |
| --- | ---: | --- |
| devices | 16 | 6e8f3d2ff61a4688599e5457cc655b1a |
| telemetry | 51 | 7ab1e227e61411b217041ada60f4ff73 |
| thresholds | 12 | c65056e83cc941854769ce4c985d881a |
| alerts | 39 | f72a86cf0e30b2a7996eed34ab50afbd |

Sau tất cả kiểm thử, count/fingerprint của telemetry/thresholds/alerts cũ tiếp tục khớp.
Devices dùng chung nên có thêm các thiết bị kiểm thử aquarium sau migration.

## Pipeline và luật cảnh báo

`python scripts/smoke_test.py` đạt:

- node-rest-smoke-1e3f1488: nhận đủ ba mẫu qua API latest/history.
- node-ws-smoke-1e3f1488: WebSocket nhận telemetry v2 và cảnh báo turbidity critical.

Probe MQTT trực tiếp trong container backend dùng thiết bị riêng tank-probe-6aab7a7e,
đọc kết quả qua REST sau khi commit PostgreSQL; đạt 15 kiểm tra:

1. Số đo bình thường không mở cảnh báo thông số.
2. Phát lại cùng payload chỉ lưu một bản ghi.
3. Nhiệt độ thấp mở cảnh báo.
4. Nhiệt độ cao mở/cập nhật cảnh báo.
5. Vi phạm nhiệt độ liên tục dùng cùng ID cảnh báo đang mở.
6. pH thấp mở cảnh báo và số đo nhiệt độ phục hồi đóng cảnh báo nhiệt độ.
7. pH cao cập nhật cảnh báo pH.
8. pH null mở sensor_error và giữ cảnh báo pH chưa có số đo phục hồi.
9. Nhiệt độ null được lưu độc lập; pH phục hồi đóng cảnh báo pH.
10. Độ đục null được lưu độc lập.
11. Độ đục 90% mở critical và đóng sensor_error đã phục hồi.
12. Tất cả số đo bình thường đóng cảnh báo thông số.
13. Status offline mở cảnh báo kết nối.
14. Last Will có timestamp cũ không kéo lùi last_seen hoặc ghi thời điểm mở offline về lúc kết nối.
15. Telemetry mới đóng cảnh báo offline; history có đúng 11 mẫu.

Đây là probe tích hợp trực tiếp trong phiên kiểm chứng, không phải 15 unit test bổ sung.
Khi kết thúc probe, gửi offline và đóng MQTT client; không để thiết bị thử ở trạng thái online giả.

## Dashboard trên Docker thật

Dùng Playwright CLI, không thay API bằng fixture hoặc SQLite:

- Chọn tank-preview-001 từ ô mã thiết bị, kiểm tra số đo/lịch sử đúng thiết bị.
- Đổi biểu đồ sang pH và khoảng 6 giờ, hiển thị đường ngưỡng cấu hình.
- Khi simulator phát mẫu pH null, giao diện tự cập nhật qua WebSocket mà không nhấn tải lại:
  pH hiển thị --, thông báo lỗi, hai số đo còn lại vẫn có giá trị và có cảnh báo sensor_error.
- Phát số đo bình thường: pH và mô tả phục hồi, cảnh báo sensor_error đóng.
- Kiểm tra desktop 1280×900 và mobile 360×800; mobile scrollWidth=innerWidth=360.
- Console quan sát cuối phiên: 0 errors, 0 warnings. Trình duyệt kiểm thử đã đóng.

Ảnh cục bộ (output/playwright bị Git bỏ qua):

- output/playwright/aquarium-docker-desktop.png
- output/playwright/aquarium-docker-mobile-fault.png

## Trạng thái bàn giao

Bốn dịch vụ Docker vẫn chạy. API http://localhost:8000/health trả healthy/database up/mqtt connected.
Web demo: http://localhost:5173/?device_id=tank-preview-001.
Broker cho ESP32: IP LAN của máy chạy Docker, cổng 1884 (bên trong Docker là mqtt:1883).

Thiết bị tank-preview-001 có 13 mẫu giả (5 normal + 3 sensor-error + 5 recovery).
Simulator đã chạy xong và gửi Offline; dashboard giữ số đo cuối và lịch sử là đúng thiết kế.
Chưa flash ESP32, chưa thử mất Wi-Fi/nguồn trên board, chưa tích hợp hoặc hiệu chuẩn cảm biến thật.
Ngưỡng đang dùng chỉ phục vụ demo; chỉ số độ đục không phải NTU.

Việc tiếp theo: xác nhận model ESP32/cổng COM, cấu hình Wi-Fi/broker và thực hiện firmware-test-plan.md.
