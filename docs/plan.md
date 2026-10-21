# Kế hoạch và tiến độ thực tế

> Cập nhật: 22/10/2026.
> Đề tài chốt với người thực hiện: **Xây dựng hệ thống IoT giám sát bể nuôi cá**.
> Hạn kỹ thuật trong Phiếu giao nhiệm vụ: 05/01/2027.
> Lịch trong timeline.txt: thông tin đề tài đến 01/11; xét bảo vệ 27/12; nộp đến 17h 12/01/2027.
> Đây là plan hiện hành; bản transition-plan-fish-monitoring.md ngày 15/10 chỉ còn là tài liệu lịch sử.
> Thư mục làm việc hiện tại: D:\DATN\iot-flood-monitoring.
> Tên repository GitHub và Compose project: iot-aquarium-monitoring; thư mục local giữ nguyên.
> Ưu tiên hiện tại: nhận linh kiện, xác nhận board/pinout/điện áp, flash và hiệu chuẩn theo hardware-bringup.md; phần mềm và driver đã phát triển thêm ngày 21/10.

## 1. Phạm vi

MVP: một bể, ESP32 đo pH/nhiệt độ/độ đục tương đối, MQTT, database, web realtime/lịch sử và cảnh báo.
Phát hiện người bằng PIR để bật LED là mở rộng sau khi MVP chạy ổn định, không đo chuyển động của cá.
Không thêm camera/AI, chẩn đoán bệnh, cho ăn hay điều khiển máy bơm vào MVP.

Trạng thái: DONE có bằng chứng; READY đủ điều kiện làm; TODO chưa triển khai;
VERIFY đã có code nhưng chưa kiểm chứng trên môi trường đích; IN PROGRESS đã làm một phần.

## 2. Tiến độ kế thừa

Đến 14/10, nền tảng đề tài ngập đã có Docker Compose/Mosquitto/PostgreSQL,
FastAPI MQTT ingestion, chống trùng, API latest/history, quản lý cảnh báo,
WebSocket, dashboard Vue và xử lý loading/error/reconnect.
Các minh chứng kiểm thử ngày 13–14/10 thuộc **phiên bản ngập cũ**,
không được tính là kiểm chứng cho dữ liệu cảm biến bể cá.

Ngày 17/10 đã sửa trực tiếp bản Phiếu giao nhiệm vụ duy nhất:
tên ngắn, ba thông số nước và chức năng cốt lõi.
Người thực hiện đã có ESP32, breadboard, dây và điện trở; ngày 19/10 xác nhận sẽ mua cảm biến,
ngày 21/10 xác nhận đã đặt DS18B20, PH-4502C, độ đục và SR501, dự kiến vài ngày nữa nhận.
Ảnh độ đục là đầu đo kèm mạch đỏ ba chân, chưa có mã/pinout/output; chưa xác nhận đã nhận hàng.
Việc GVHD duyệt và cập nhật QLĐT vẫn cần người thực hiện xác nhận.

## 3. Đợt chuyển đổi phần mềm đầu tiên — 19/10

| ID | Trạng thái | Kết quả |
| --- | --- | --- |
| AQ-001 | DONE | Schema v2: temperature_c, ph, turbidity_pct; kiểm tra miền giá trị, timestamp và null |
| AQ-002 | DONE | Topic aquarium-monitoring; backend và simulator thống nhất namespace |
| AQ-003 | DONE | Migration 0002 đạt trên PostgreSQL thật ngày 20/10; đối chiếu số lượng và fingerprint cả bốn bảng cũ ngay sau migration đều giữ nguyên; có backup trước nâng cấp |
| AQ-004 | DONE | Simulator tám kịch bản, bao gồm lỗi từng cảm biến và offline |
| AQ-005 | DONE | Cảnh báo nhiệt độ/pH/độ đục, cảm biến lỗi, offline; cập nhật/đóng bản ghi và giữ cảnh báo khi số đo chưa phục hồi |
| AQ-006 | DONE | Dashboard ba chỉ số, đơn vị mới và trạng thái thiết bị |
| AQ-007 | DONE | Biểu đồ lịch sử REST 1/6/24 giờ, đổi chỉ số, đường ngưỡng cấu hình, ngắt đường tại null |
| AQ-008 | DONE | Ngày 21/10: 34 test backend, 8 test logic frontend, 4 test firmware host/69 payload đạt; frontend build đạt. 5 test simulator đã đạt từ đợt trước; chưa thay kiểm chứng board thật |
| AQ-009 | DONE | Đã kiểm tra SQLite tạm; ngày 20/10 bổ sung Playwright trên Docker/PostgreSQL thật: đổi thiết bị, biểu đồ pH/6 giờ, lỗi pH tự cập nhật, phục hồi, desktop 1280px/mobile 360px |
| AQ-010 | DONE | Compose rebuild đạt, bốn dịch vụ healthy; smoke MQTT → PostgreSQL → REST/WebSocket và 15 kiểm tra live về cảnh báo/null/chống trùng/Last Will đạt ngày 20/10 |
| AQ-011 | DONE | Form ghi đủ sáu ngưỡng, xác nhận cảnh báo idempotent, chỉ báo mẫu cũ từ 60 giây/lệch giờ tương lai trên web; đã kiểm tra browser với PostgreSQL thật ngày 21/10 |

Ngày 20/10 xác nhận thư mục gốc đã đổi từ D:\ĐATN sang D:\DATN; thư mục repository vẫn là iot-flood-monitoring.
Tại thời điểm 20/10 giữ nguyên tên Compose project, database và volume để sử dụng lại dữ liệu đã có.
Ngày 22/10 đổi tên project/container và repository GitHub sang iot-aquarium-monitoring;
database/user và volume cũ được gắn lại bằng local override external, không khởi tạo lại dữ liệu.
Ngưỡng hiện tại chỉ dùng demo; độ đục tương đối 0–100 chưa phải NTU.
Ngày 20/10 Docker đã hoạt động, migration 0002 và pipeline MQTT/PostgreSQL thật đã được xác minh.
Bản sao trước nâng cấp nằm tại D:\DATN\.codex_tmp\aquarium-pre-v2-20261020.dump.
Chi tiết minh chứng và trạng thái demo: [docker-verification-2026-10-20.md](docker-verification-2026-10-20.md).

Minh chứng browser nằm trong output/playwright/aquarium-desktop.png và aquarium-mobile-error.png
(thư mục local bị Git bỏ qua). Bộ test backend nằm trong backend/tests; test simulator trong simulator/tests.
docker compose config --quiet và git diff --check đã đạt.

## 4. Backlog tiếp theo

| Ưu tiên | ID | Trạng thái | Đầu việc / điều kiện hoàn thành |
| --- | --- | --- | --- |
| P0 | HW-001 | VERIFY | Ba environment fake/sensors/alias build đạt cho esp32dev; còn xác nhận đúng board, flash và log serial |
| P0 | FW-001 | VERIFY | Firmware fake v2, NTP, Wi-Fi/MQTT reconnect và Last Will; bốn test host/69 payload đạt; chưa thử mạng trên board |
| P0 | HW-002 | IN PROGRESS | Đã đặt đủ bốn loại; chốt DS18B20/PH-4502C/SR501, có ảnh độ đục; còn ngày nhận, mã độ đục và mức áp/pinout thật |
| P0 | FW-002 | VERIFY | Có driver DS18B20 không chặn, ADC1 lọc/hiệu chuẩn hai điểm và chẩn đoán mV; chưa thử đầu dò thật, analog chưa hiệu chuẩn vẫn null |
| P0 | CAL-001 | TODO | Hiệu chuẩn pH bằng buffer, đối chiếu nhiệt độ, xác lập chỉ số độ đục tương đối |
| P0 | TEST-001 | IN PROGRESS | Có F01–F11 và hardware-bringup.md; cần bổ sung dụng cụ tham chiếu/biểu mẫu kết quả theo linh kiện nhận được |
| P0 | TEST-002 | TODO | Tích hợp cảm biến thật → MQTT → PostgreSQL → dashboard; chụp ảnh/lưu log |
| P0 | TEST-003 | TODO | Thực nghiệm sai số, độ lặp lại, độ trễ, mất mẫu, reconnect và chạy liên tục |
| P0 | DOC-001 | IN PROGRESS | Kiến trúc/hướng dẫn vận hành và nhận hàng đã cập nhật; quyển đồ án/kết quả thực nghiệm chưa hoàn thành |
| P1 | WEB-001 | DONE | Form ngưỡng, xử lý lỗi API/đổi thiết bị, xác nhận cảnh báo và tuổi mẫu web đã kiểm thử; không tự tạo timeout alert phía server |
| P1 | LED-001 | VERIFY | Có PIR→LED tùy chọn, warmup 60 giây/giữ 15 giây; mặc định tắt, host test đạt, chưa thử SR501/LED thật |
| P2 | EXT-001 | TODO | Mở rộng khác chỉ khi MVP và thực nghiệm đã hoàn tất |

## 5. Mốc điều chỉnh

| Thời gian | Kết quả cần có |
| --- | --- |
| 19–25/10 | Đã đạt Docker v2, form ngưỡng/ack/tuổi mẫu và firmware fake/sensors build; đã đặt linh kiện; tiếp theo flash board, nhận hàng và bắt đầu đọc DS18B20 |
| 26/10–01/11 | Xác minh Compose thật, ổn định dashboard; chốt hồ sơ đề tài với GVHD |
| 02–08/11 | Firmware nền chạy ổn định; tích hợp đầu vào có sẵn |
| 09–15/11 | Đọc được cả ba cảm biến thật và hiệu chuẩn bước đầu, phụ thuộc ngày nhận hàng |
| 16–22/11 | Tích hợp toàn tuyến bằng dữ liệu thật |
| 23–29/11 | Chốt mô hình, dụng cụ tham chiếu, test plan và chạy thử thực nghiệm |
| 30/11–13/12 | Thu dữ liệu thực nghiệm chính; viết kết quả song song |
| 14–20/12 | Phân tích dữ liệu, sửa lỗi chính và đóng băng MVP |
| 21–27/12 | Quyển nháp đầy đủ và demo để GVHD xem xét |
| 28/12–05/01 | Hoàn thiện kỹ thuật và tài liệu |
| 06–12/01 | Chỉnh quyển và hồ sơ nộp theo lịch đã cung cấp |

## 6. Bàn giao

Bắt đầu phiên sau bằng git status, README, tài liệu kiến trúc và file này.
Có các thay đổi chưa commit từ trước đợt chuyển đổi; không reset hoặc ghi đè phần không liên quan.
Mở repository tại D:\DATN\iot-flood-monitoring trong Codex/IDE. Nếu phiên vẫn cấp quyền cho D:\ĐATN,
cần mở lại workspace theo đường dẫn mới để thao tác bình thường.

1. Pipeline Docker v2 đã đạt; kiểm tra health nếu khởi động lại môi trường.
2. Xác nhận model ESP32/cổng COM, điền firmware/include/config.local.h và flash esp32-fake; thực hiện firmware-test-plan.md. Broker hiện mở cổng LAN 1884; dùng IP LAN máy chạy Docker, không dùng localhost trên ESP32.
3. Khi nhận hàng, xác nhận pinout/nguồn/đầu ra, cập nhật BOM và thực hiện docs/hardware-bringup.md; firmware sensors có sẵn nhưng chưa hiệu chuẩn.
4. Cấu hình ngưỡng sau khi chọn loài cá và hiệu chuẩn. Không lấy ngưỡng mặc định làm kết luận sinh học.

## 7. Firmware nền — 19/10

Đã thêm firmware ESP32, build hai environment esp32-fake và esp32-pending-sensors.
Fake dùng tank-demo-001 riêng; bảy kịch bản và phím serial để thử cảnh báo.
Pending chưa đọc cảm biến, trả null cho ba chỉ số. Driver/hiệu chuẩn vẫn nằm trong FW-002/CAL-001.
Chờ NTP trước khi gửi; QoS 1, status retained, Last Will, reconnect và hàng đợi RAM có giới hạn.
Bốn test host biên dịch mã C++ và đưa 67 payload qua schema/ingestion; kiểm tra chống trùng và cảnh báo đạt.
Sửa backend để timestamp Last Will không kéo lùi last_seen hoặc mở cảnh báo offline từ lúc boot.
Hai test hồi quy bổ sung cho Last Will/last_seen; tổng backend hiện có 31 test.
Tại thời điểm hoàn thành firmware ngày 19/10, Docker chưa hoạt động; ngày 20/10 đã xác minh pipeline như bên dưới.
Chưa flash, chưa kiểm chứng F01–F08 trên board thật.

## 8. Việc tiếp theo — cập nhật 20/10

Các kết quả 31/5/4 test là minh chứng đã có từ đợt triển khai firmware.
Ngày 20/10 đã build lại Docker, chạy migration thật, smoke test, probe 15 kiểm tra và browser QA;
không tính các probe này thành số unit test mới. Báo cáo nằm trong docker-verification-2026-10-20.md.
Đã xác nhận đặt hàng/model như BOM cập nhật 21/10; chưa có model ESP32/cổng COM, cấu hình mạng,
ngày nhận cụ thể, điện áp đầu ra độ đục hoặc kết quả flash.

1. **AQ-010 / AQ-003 — DONE:** Compose, migration PostgreSQL và smoke test v2 đã đạt;
   dữ liệu ngập giữ nguyên. Giữ bốn dịch vụ đang chạy để tiếp tục nối ESP32.
2. **HW-001 / FW-001:** xác nhận model board và cổng COM, tạo config.local.h với Wi-Fi/IP LAN broker,
   nạp esp32-fake. Hoàn thành khi serial ghi nhận đồng bộ NTP/PUBACK và web tank-demo-001 hiển thị dữ liệu.
3. **FW-001:** thực hiện F01–F08 trong firmware-test-plan.md; thử ngưỡng, null riêng từng đầu dò,
   mất Wi-Fi, broker khởi động lại, ngắt nguồn và chạy liên tục. Lưu log/ảnh, ghi rõ PASS/FAIL thực tế.
4. **HW-002 / FW-002 / CAL-001:** driver đã build; khi nhận hàng thử lần lượt DS18B20 → PH-4502C → độ đục,
   kiểm tra nguồn/output trước khi nối, hiệu chuẩn và đối chiếu. esp32-pending-sensors hiện là alias của esp32-sensors.
5. **WEB-001 — DONE / DOC-001:** đã có form ngưỡng, ack và tuổi mẫu; tiếp tục viết quyển yêu cầu/kiến trúc
   và bổ sung dữ liệu thực nghiệm khi có phần cứng thật.

PIR phát hiện người bật LED tiếp tục là phần mở rộng sau khi MVP và kiểm thử chính đã ổn định.

## 9. Kết quả Docker thực tế — 20/10

- Docker Engine 29.0.1; mqtt/db/backend/frontend đều healthy, API 0.2.0 báo database up và mqtt connected.
- Migration ở 0002_aquarium_monitoring. Trước/sau migration: devices 16, telemetry cũ 51,
  thresholds cũ 12, alerts cũ 39; fingerprint từng bảng giống hệt. Sau kiểm thử, ba bảng dữ liệu ngập vẫn giữ nguyên.
- Smoke test REST/history và WebSocket telemetry/cảnh báo đạt; probe riêng tank-probe-6aab7a7e lưu đúng 11 mẫu,
  chống trùng và đạt cả 15 kiểm tra cảnh báo/phục hồi/null/Last Will.
- Dashboard Docker cập nhật lỗi pH và phục hồi qua WebSocket; mobile không tràn ngang, console không có lỗi/warning được ghi nhận.
- Có 13 mẫu demo tại tank-preview-001. Simulator đã kết thúc nên trạng thái Offline là mong đợi;
  dữ liệu và lịch sử vẫn xem được tại http://localhost:5173/?device_id=tank-preview-001.
- Không có firmware được flash trong đợt này. HW-001/FW-001 vẫn VERIFY, cảm biến/hiệu chuẩn vẫn TODO.

## 10. Phần mềm/firmware chuẩn bị nhận hàng — 21/10

- Backend có POST acknowledge, kiểm tra cảnh báo thuộc thiết bị, gọi lặp giữ mốc xác nhận;
  không đóng cảnh báo. Không đổi schema/migration và không sửa bảng ngập lưu trữ.
- Web lưu đủ sáu ngưỡng, kiểm tra miền/thứ tự, xử lý lỗi/thử lại và phản hồi cũ khi chuyển thiết bị;
  cập nhật biểu đồ sau lưu. Tuổi mẫu tự tăng mỗi giây, từ 60 giây hiện dữ liệu cũ,
  timestamp tương lai quá 30 giây có thông báo; đây là chỉ báo trình duyệt, chưa phải server timeout.
- Firmware sensors đọc DS18B20 async, ADC1 lọc 15 mẫu/hiệu chuẩn hai điểm;
  thiếu calibration/ngoài miền/quá tuổi cache thành null riêng từng kênh. Serial v hỗ trợ raw mV khi chưa có mạng.
- Thêm PIR SR501→LED cục bộ tùy chọn, mặc định tắt, warmup 60 giây và giữ đèn 15 giây từ lần OUT cao cuối.
- 34 test backend, 8 test frontend, 4 test host firmware đạt; ba cấu hình ESP32 build đạt.
  Browser Docker/PostgreSQL kiểm tra lưu ngưỡng, lỗi API, ack, đổi thiết bị, tuổi mẫu và mobile đạt.
  Chi tiết: development-2026-10-21.md; hướng dẫn phần cứng: hardware-bringup.md.
- Chưa flash hoặc thử các chức năng với linh kiện thật; CAL-001 và TEST-002/003 còn chờ nhận hàng.
