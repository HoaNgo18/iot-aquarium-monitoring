# Đổi tên dự án — 22/10/2026

Tên theo đề tài hiện tại: **iot-aquarium-monitoring**.

- GitHub: https://github.com/HoaNgo18/iot-aquarium-monitoring.
- Git remote origin cập nhật sang URL mới, không tạo repository khác.
- Compose project mặc định và `.env` local: iot-aquarium-monitoring.
- Container: iot-aquarium-monitoring-db-1, mqtt-1, backend-1 và frontend-1.
- Package frontend: iot-aquarium-monitoring-frontend; tên trong package-lock đồng bộ.
- Chưa đổi thư mục local D:\DATN\iot-aquarium, database flood_monitoring hoặc user flood_app.
- Tại bước đổi tên chỉ cập nhật repository/origin; các thay đổi chức năng được chia commit và push riêng sau đó theo yêu cầu người thực hiện.

## Bảo toàn dữ liệu trên máy hiện tại

Hai volume đã tồn tại được giữ nguyên:

- iot-aquarium_postgres_data.
- iot-aquarium_mqtt_data.

`compose.override.yaml` local khai báo external và chỉ rõ hai tên trên.
Compose tự đọc file này cùng compose.yaml; đổi tên project không làm tạo database rỗng.
File override bị Git bỏ qua để máy clone mới vẫn tạo volume mới theo tên dự án mới.
External volume không bị Compose xóa khi down; không dùng volume prune/rm với dữ liệu này.

`compose.legacy-volumes.example.yaml` là bản mẫu cho máy có đúng hai volume cũ.
Không copy bản mẫu khi cài mới hoặc chưa xác minh tên volume thực tế.
Khi di chuyển thư mục local, giữ cả `.env` và `compose.override.yaml`.

Trình tự chuyển: dừng frontend/backend/MQTT cũ, chụp fingerprint và sao lưu PostgreSQL,
gỡ container/network cũ không dùng `-v`, khởi động database mới gắn volume cũ,
đối chiếu dữ liệu trước khi bật backend và chạy kiểm tra toàn tuyến.

Bản sao PostgreSQL trước chuyển tên: D:\DATN\.codex_tmp\aquarium-pre-rename-20261022.dump.

## Trạng thái kiểm tra

- GitHub API trả đúng repository ID 1410451370 với full_name HoaNgo18/iot-aquarium-monitoring.
- `git ls-remote origin HEAD` đọc được URL mới; tại thời điểm kiểm tra đổi tên chưa commit/push thay đổi chức năng.
- Compose chỉ còn project iot-aquarium-monitoring, bốn container healthy; không còn container thuộc project cũ.
- Đã build ba image backend/frontend/simulator dưới tiền tố iot-aquarium-monitoring.
- Đã đối chiếu số lượng và fingerprint của đủ tám bảng trước khi khởi động backend: khớp hoàn toàn.
  Số bản ghi tại mốc chuyển: alembic_version 1, devices 24, telemetry 51, thresholds 12,
  alerts 39, aquarium_telemetry 40, aquarium_thresholds 8, aquarium_alerts 20.
- Bản dump trước chuyển: 26713 byte; SHA256 A9D20AD103B4200A03B6ADB52B3B1908A788692634BF55717F5426937579F5CC.
- Kiểm tra mount xác nhận PostgreSQL và MQTT dùng đúng hai volume cũ.
- Smoke test simulator → MQTT → backend → PostgreSQL → REST/WebSocket đạt, gồm cảnh báo độ đục.
  Kiểm tra này tạo thêm thiết bị và dữ liệu thử sau mốc đối chiếu, nên số bản ghi tiếp tục tăng là bình thường.
- API health: database up, MQTT connected; frontend HTTP200 với tiêu đề bể cá.
- `docker compose config --quiet` và `git diff --check` đạt.
