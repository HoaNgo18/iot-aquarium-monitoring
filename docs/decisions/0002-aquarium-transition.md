# ADR-0002: Chuyển sang giám sát bể nuôi cá

Ngày: 19/10/2026. Trạng thái: triển khai đợt phần mềm đầu tiên.

## Bối cảnh

Người thực hiện chốt đề tài "Xây dựng hệ thống IoT giám sát bể nuôi cá",
đầu vào pH/độ đục/nhiệt độ. Nền tảng giám sát ngập đã có MQTT, API, PostgreSQL,
WebSocket và Vue; chưa có firmware hay cảm biến thật được tích hợp.

## Quyết định

- Giữ stack FastAPI/PostgreSQL/Vue và hạ tầng hiện có.
- MQTT namespace aquarium-monitoring, payload schema_version 2; không chấp nhận payload ngập v1.
- Các trường temperature_c, ph, turbidity_pct; null biểu thị lỗi từng số đo.
- Độ đục là chỉ số tương đối chuẩn hóa theo đầu dò sau khi hiệu chuẩn, không dùng nhãn NTU.
- Migration 0002 thêm ba bảng aquarium, không sửa revision 0001 hoặc chuyển nghĩa dữ liệu cũ.
- Giữ Compose project, database và volume tên cũ để tiếp tục dùng đúng hạ tầng.
- Ngưỡng phát triển không phải chuẩn nuôi cá; có API cấu hình riêng từng thiết bị.
- PIR phát hiện người bật LED là mở rộng, không theo dõi hành vi cá.

## Hệ quả

Publisher cũ cần nâng schema/topic. Dashboard mặc định tank-001.
API lịch sử hiện chỉ phản ánh dữ liệu aquarium; dữ liệu ngập vẫn nằm trong các bảng cũ.
Không tự đổi tên thư mục hoặc remote Git ở đợt này.
Firmware, hiệu chuẩn, thử nghiệm trên PostgreSQL thật và dữ liệu cảm biến là các bước tiếp theo.
