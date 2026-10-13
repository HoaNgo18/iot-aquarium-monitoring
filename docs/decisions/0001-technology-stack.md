# ADR-0001: Lựa chọn công nghệ cho MVP

- Trạng thái: Chấp nhận
- Ngày quyết định: 09/10/2026

## Bối cảnh

Dự án cần hoàn thành một hệ thống IoT xuyên suốt từ ESP32, MQTT, backend, database đến dashboard web trong thời gian giới hạn. Công nghệ cần dễ học, có tài liệu tốt, chạy được trên máy cá nhân và hỗ trợ kiểm thử độc lập bằng dữ liệu giả lập.

## Quyết định

- Dùng PlatformIO với Arduino framework cho firmware ESP32.
- Dùng Eclipse Mosquitto làm MQTT broker.
- Dùng FastAPI cho REST API, WebSocket và xử lý nghiệp vụ backend.
- Dùng SQLAlchemy và Alembic để truy cập và quản lý schema PostgreSQL.
- Dùng PostgreSQL để lưu thiết bị, telemetry, ngưỡng và cảnh báo.
- Dùng Vue 3, TypeScript và Vite cho frontend.
- Dùng Pinia cho trạng thái ứng dụng, Axios cho REST API và Apache ECharts cho biểu đồ.
- Dùng Docker Compose để chạy các dịch vụ cục bộ.

## Lý do

- FastAPI có validation dựa trên type và tự tạo tài liệu OpenAPI, giúp giảm thời gian viết mã nền và kiểm thử API.
- Python thuận lợi cho xử lý dữ liệu thực nghiệm và tính toán sai số trong giai đoạn đánh giá.
- Vue có cú pháp gần HTML, phù hợp để dựng dashboard nhanh với phạm vi giao diện vừa phải.
- Mosquitto và PostgreSQL đủ nhẹ để chạy cục bộ nhưng vẫn thể hiện đúng kiến trúc của hệ thống.
- PlatformIO giúp quản lý thư viện, môi trường build và cấu trúc firmware tốt hơn một file Arduino đơn lẻ.

## Hệ quả

- Dự án sử dụng Python ở backend và TypeScript ở frontend thay vì một ngôn ngữ duy nhất.
- MQTT consumer phải được tích hợp sao cho không chặn event loop của FastAPI; có thể tách thành process/service riêng nếu cần.
- Frontend không thể sao chép trực tiếp từ các template React đã khảo sát.
- Mọi thành phần cần có lệnh chạy và kiểm thử được ghi trong README tương ứng.

## Không chọn

- Node.js/Express: đơn giản ở endpoint đầu tiên nhưng cần tự ghép thêm validation, tài liệu API và quy ước cấu trúc.
- React: hệ sinh thái lớn nhưng độ dốc học ban đầu cao hơn Vue đối với dashboard của đồ án.
- ESP-IDF thuần: kiểm soát phần cứng tốt hơn nhưng tăng khối lượng học và cấu hình so với nhu cầu MVP.
