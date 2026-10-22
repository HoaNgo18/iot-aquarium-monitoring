# Bản dự án chính — 23/10/2026

- GitHub: https://github.com/HoaNgo18/iot-aquarium-monitoring (branch main).
- Repo local duy nhất: D:\DATN\iot-aquarium.
- Frontend chính: frontend/ trong repo trên; Vue/Vite, UI AquaSense xanh biển.
- Chạy toàn hệ thống bằng Compose; web http://localhost:5173/?device_id=tank-demo-001.
- API http://localhost:8000; MQTT LAN 1884 theo cấu hình máy hiện tại.

Thư mục đã đổi thành iot-aquarium; các volume đang dùng mang tiền tố iot-aquarium.
Dữ liệu đã được sao chép khi dịch vụ dừng và kiểm chứng trước khi khởi động lại. Volume trước đổi tên chỉ giữ làm backup, không được mount vào dịch vụ.
Đề tài, GitHub, Compose project và dữ liệu phục vụ API đều là bể cá.
Các bảng ngập cũ là dữ liệu lưu trữ, không phải phiên bản đang chạy.

## Hợp nhất

UI từng nằm riêng tại D:\ĐATN\iot-aquarium đã chuyển vào frontend/src/dashboard.
DashboardView.vue quản lý vòng đời và dùng useRealtime.ts hiện hữu cho WebSocket,
heartbeat/reconnect và gộp sự kiện REST. Polling 5 giây chỉ dự phòng khi socket mất kết nối.
DOM renderer được tách thành module có mount/dispose; timer, listener, ResizeObserver và
request được dọn khi component unmount. Template là tài nguyên build tin cậy, chuỗi API được escape.
Không thêm dependency. Không đổi schema/backend, MQTT hoặc firmware.

Các component giao diện cũ không còn được dùng đã lưu bản sao trước khi loại khỏi nguồn hoạt động.
Các thay đổi tài liệu bring-up ESP32 đang có trong repo được giữ và đồng bộ cùng lần này.
Nguồn standalone và bản frontend trước hợp nhất được lưu tại D:\DATN\_archives (ngoài repo).
Đường dẫn cũ D:\ĐATN\iot-aquarium chỉ còn là junction trỏ đến repo chính sau bàn giao.
Các preview 4173/4174/4175 được dừng; dùng 5173.

## Kiểm chứng

- 11 unit test frontend đạt; vue-tsc và Vite production build đạt.
- 10 kiểm tra browser với mock: null, nguy hiểm, ô trống, lỗi lưu giữ draft,
  PUT sáu field, acknowledge, lỗi API, đổi thiết bị nhanh, mobile và form cuối trang.
- Đọc backend thật thấy health healthy/database up/MQTT connected; tank-demo-001 offline.
- Thao tác ghi của bộ browser test dùng mock, không thay đổi ngưỡng thiết bị thực.

Mở workspace D:\DATN\iot-aquarium cho các phiên tiếp theo.
Tiếp tục docs/plan.md: kiểm thử reconnect/Last Will trên board, nhận cảm biến và hiệu chuẩn.
