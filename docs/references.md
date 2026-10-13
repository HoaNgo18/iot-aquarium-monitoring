# Dự án và mã nguồn tham khảo

> Khảo sát ngày 09/10/2026.

Các repository dưới đây được dùng để học cách tổ chức và kiểm chứng ý tưởng. Không repository nào khớp hoàn toàn với phạm vi đồ án. Trước khi sử dụng lại code, cần đọc giấy phép, hiểu luồng xử lý và ghi nguồn trong báo cáo.

## 1. Dự án gần với bài toán

### ESP32 water level sensor

- Repository: <https://github.com/decebu/water_level_sensor>
- Phù hợp để tham khảo: PlatformIO, cảm biến siêu âm chống nước, MQTT, giới hạn giá trị cảm biến, timeout, heartbeat, retained message và tiết kiệm năng lượng.
- Điểm đáng học: chỉ bật Wi-Fi khi cần gửi; vẫn gửi heartbeat khi số đo không đổi; cấu hình tách khỏi source code chính.
- Không sao chép nguyên trạng: dự án đo giếng nước bằng một cảm biến và không có backend, database hoặc dashboard riêng.

### ESP32 Flood and Weather Monitoring System

- Repository: <https://github.com/sushanknahar/ESP32-Flood-Weather-Monitoring-System>
- Phù hợp để tham khảo: chia firmware thành module cảm biến, logger và cảnh báo; tài liệu pinout; xử lý khi cảm biến đọc lỗi.
- Điểm đáng học: model dữ liệu cảm biến chung và tách logic cảnh báo khỏi driver phần cứng.
- Hạn chế: dùng cảm biến mưa analog và lưu SD; chưa triển khai luồng MQTT đến web. Cảm biến mưa analog không thay thế phép đo lượng mưa theo milimet.

### Smart Tunnel Monitoring IoT System

- Repository: <https://github.com/Shafwan1902/Smart-Tunnel-Monitoring-IoT-System>
- Phù hợp để tham khảo: kiến trúc nhiều lớp, ESP32 gửi MQTT, Python xử lý dữ liệu, dashboard thời gian thực và cảnh báo Telegram.
- Điểm đáng học: tách lớp thiết bị, truyền thông, xử lý và trình bày; đo độ trễ toàn tuyến.
- Hạn chế: dùng InfluxDB và Grafana thay vì PostgreSQL và web tùy chỉnh; các con số hiệu năng của repository cần tự kiểm chứng.

### FloodWatch

- Repository: <https://github.com/ndg8743/FloodWatch>
- Phù hợp để tham khảo: giao diện mức nguy cơ, biểu đồ lịch sử, trạng thái theo màu, bố cục dashboard và Docker deployment.
- Hạn chế: nhận dữ liệu qua BLE và dịch vụ USGS, không dùng kiến trúc MQTT/backend giống đồ án.

### AWS IoT Monitoring and Control Dashboard

- Repository: <https://github.com/toniminhkhoi/aws-iot-dashboard>
- Phù hợp để tham khảo: cách chia `backend`, `frontend`, `hardware`, kiến trúc FastAPI + React + PostgreSQL và tài liệu song ngữ.
- Hạn chế: kiến trúc AWS lớn hơn nhiều so với nhu cầu đồ án; không nên đưa ALB, Auto Scaling, CloudFront hoặc Kubernetes vào MVP.

## 2. Mã nguồn chính thức theo thành phần

### DFRobot rainfall sensor

- Repository: <https://github.com/DFRobot/DFRobot_RainfallSensor>
- Dùng khi chọn cảm biến gầu lật SEN0575.
- Có driver và ví dụ Arduino cho tổng lượng mưa, lượng mưa theo khoảng thời gian và số lần gầu lật.
- Cần tự kiểm thử cách cửa sổ 1–24 giờ hoạt động; không coi giá trị thư viện là đúng nếu chưa hiệu chuẩn bằng lượng nước biết trước.

### Espressif ESP-MQTT

- Repository: <https://github.com/espressif/esp-mqtt>
- Ví dụ chính thức: <https://github.com/espressif/esp-idf/tree/master/examples/protocols/mqtt>
- Dùng để tham khảo reconnect, QoS, Last Will, TLS, subscribe và publish khi chọn ESP-IDF.
- Nếu dùng Arduino framework, vẫn áp dụng các khái niệm giao thức nhưng chọn thư viện tương thích với PlatformIO/Arduino.

### Eclipse Mosquitto

- Repository: <https://github.com/eclipse-mosquitto/mosquitto>
- Dùng làm MQTT broker cục bộ trong Docker Compose.
- Lưu ý Mosquitto 2 không cho client bên ngoài container kết nối nếu chưa cấu hình listener; môi trường phát triển cũng nên dùng user/password thay vì để anonymous lâu dài.

### Full Stack FastAPI Template

- Repository: <https://github.com/fastapi/full-stack-fastapi-template>
- Phù hợp để tham khảo phần FastAPI, PostgreSQL, validation, migration, test, biến môi trường và Docker Compose.
- Frontend của template dùng React, trong khi đồ án đã chọn Vue 3; không sao chép phần frontend nguyên trạng.
- Không nên bê toàn bộ template vào đồ án ngay từ đầu; chỉ lấy cấu trúc cần thiết để tránh tăng độ phức tạp.

## 3. Thứ tự tham khảo đề xuất

1. Đọc `decebu/water_level_sensor` trước khi thiết kế firmware và heartbeat.
2. Đọc `DFRobot_RainfallSensor` khi đã chốt SEN0575 hoặc cảm biến tương ứng.
3. Đọc ví dụ ESP-MQTT hoặc thư viện MQTT đã chọn trước khi định nghĩa reconnect/QoS/Last Will.
4. Đọc `full-stack-fastapi-template` sau khi chốt stack, chỉ lấy phần cấu trúc và workflow cần thiết.
5. Dùng FloodWatch và Smart Tunnel để tham khảo giao diện, cảnh báo và kịch bản demo.

## 4. Nguyên tắc sử dụng

- Không sao chép code mà không hiểu cách hoạt động.
- Kiểm tra giấy phép tại thời điểm sử dụng.
- Ghi nguồn trong báo cáo nếu thuật toán, sơ đồ hoặc đoạn code có ảnh hưởng trực tiếp.
- Không dùng các ngưỡng cảnh báo từ dự án khác làm kết quả của đồ án; ngưỡng phải đến từ yêu cầu và thực nghiệm của hệ thống này.
- Không thêm cảm biến hoặc hạ tầng chỉ vì repository tham khảo có sử dụng.
