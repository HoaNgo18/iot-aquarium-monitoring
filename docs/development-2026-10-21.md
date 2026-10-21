# Kết quả phát triển phần mềm và firmware — 21/10/2026

## Phần mềm

Đã thêm form cấu hình sáu ngưỡng theo từng thiết bị, giữ các trường chưa sửa khi lưu,
kiểm tra miền/thứ tự, giữ bản nhập khi lỗi và hủy/bỏ qua phản hồi của thiết bị cũ.
Lưu thành công tải lại đường ngưỡng biểu đồ; cảnh báo áp dụng từ mẫu mới theo API hiện có.

POST /api/v1/devices/{id}/alerts/{alert_id}/acknowledge ghi nhận đã xem cảnh báo,
không kết thúc điều kiện cảnh báo. UPDATE có điều kiện acknowledged_at IS NULL để giữ mốc đầu tiên;
ID sai/không thuộc thiết bị nhận 404. Client gọi REST tự tải lại sau thành công;
chưa phát riêng sự kiện cấu hình/ack sang các tab khác.

Tuổi mẫu lấy measured_at, cập nhật mỗi giây kể cả không nhận telemetry.
Từ 60 giây hiện dữ liệu cũ, giờ mẫu tương lai quá 30 giây hiện lệch thời gian;
giữ số đo cuối và không tự đổi trạng thái MQTT thành offline. Chưa có timeout alert server.

## Firmware

- esp32-sensors: DS18B20 chuyển đổi async, CRC/lỗi qua DallasTemperature, cache tối đa 2.5 giây,
  tự dò lại khi mất đầu dò; chỉ hỗ trợ cấp nguồn ba dây.
- PH-4502C và độ đục: ADC1 mV, cửa sổ 150–3000 mV, lọc 15 mẫu, bỏ ba ở mỗi đầu,
  hai điểm hiệu chuẩn do người thực hiện đo. Thiếu cấu hình/ngoài miền/không có mẫu mới trả null.
- Serial v in raw mV và giá trị đã hiệu chuẩn, chạy cả khi chưa có Wi-Fi/MQTT.
- PIR→LED tùy chọn: GPIO27/26, warmup 60 giây, giữ 15 giây từ lần OUT cao cuối;
  hoạt động cục bộ, không thêm trường schema v2.
- Giữ esp32-fake; esp32-pending-sensors là alias tương thích của esp32-sensors.

Mặc định DS18B20 bật, analog/PIR tắt; tất cả điểm hiệu chuẩn analog chưa điền.
Chưa có thông số điện áp/pinout module độ đục và chưa thực hiện bù nhiệt pH.
Chi tiết cấu hình, giới hạn và phép đối chiếu: hardware-bringup.md.

## Kiểm chứng

| Kiểm tra | Kết quả |
| --- | --- |
| Backend unittest | 34 đạt, gồm thêm idempotence/cách ly thiết bị/cảnh báo đã kết thúc |
| Frontend Node test | 8 đạt, miền ngưỡng và tuổi mẫu/clock skew |
| Frontend type-check/build | Đạt, 85 module |
| Firmware host unittest | 4 đạt, mã C++ và 69 payload qua backend SQLite |
| PlatformIO esp32-fake | Đạt |
| PlatformIO esp32-sensors | Đạt; OneWire 2.3.8 + DallasTemperature 3.11.0 |
| PlatformIO esp32-pending-sensors | Đạt (alias) |
| Docker backend/frontend | Đã build/khởi động lại với PostgreSQL hiện có |
| Smoke test toàn tuyến | Đạt: simulator → MQTT → backend → PostgreSQL → REST/WebSocket, gồm cảnh báo độ đục |
| Bảo toàn dữ liệu đề tài cũ | Số bản ghi và fingerprint của ba bảng flood không thay đổi |

Host test firmware mở rộng kiểm tra hiệu chuẩn thiếu/sai, nội suy/giới hạn độ đục,
lỗi -127°C, offset, filter chưa đủ mẫu/quá tuổi/nhiễu, warmup/hold PIR và millis rollover.
OneWire có warning tiền xử lý trong mã thư viện; không có lỗi build, không sửa thư viện vendor.

Playwright CLI trên hệ thống Docker/PostgreSQL thật, thiết bị thử tank-ui-20261021-r2:

- Lưu đủ trường, kiểm tra GET database, không đổi các trường chưa sửa.
- Cặp ngưỡng sai bị chặn trước PUT.
- Mô phỏng HTTP503 khi lưu: giữ draft và thử lại thành công.
- Mô phỏng lỗi ack: thử lại thành công, cảnh báo vẫn đang xảy ra.
- Trì hoãn GET thiết bị A, đổi sang thiết bị không tồn tại: dữ liệu A không tràn sang B, B không cho lưu.
- Biểu đồ đọc ngưỡng pH mới (6.5/8.1).
- Đồng hồ kiểm thử: trước 60 giây chưa stale, đến 60 giây stale mà không nhận telemetry;
  timestamp tương lai có thông báo và hết khi giờ hợp lệ.
- Desktop 1280px và mobile 360px không tràn ngang, gồm toàn bộ form.

Các HTTP503 và 404 trong log browser là tình huống cố ý kiểm thử, không phải kết luận console không có lỗi.
Lần kiểm tra đồng hồ đầu tiên cài clock sau khi trang tạo timer nên phép thử không hợp lệ;
đã sửa harness để cài trước reload, kiểm tra lại đạt và resume clock sau khi hoàn tất.
Ảnh local: output/playwright/aquarium-features-desktop.png và aquarium-features-mobile.png.

## Chưa được xác minh

Chưa flash ESP32 hoặc đọc DS18B20/PH-4502C/độ đục/SR501 trên phần cứng thật.
Test host/build không thay thế pinout/điện áp, thời gian đáp ứng, sai số, nhiễu thật,
đứt dây analog, mất Wi-Fi/nguồn và chạy liên tục. Các mục này còn VERIFY/TODO trong plan.
Linh kiện đã được người thực hiện xác nhận đặt, chưa xác nhận ngày nhận cụ thể.
