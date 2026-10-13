# Kế hoạch và tiến độ thực tế

> Cập nhật lần cuối: 14/10/2026
>
> Hạn hoàn thành theo phiếu giao nhiệm vụ: 05/01/2027
>
> Trạng thái hiện tại: Dashboard đã hiển thị số đo và trạng thái thiết bị qua REST; bước tiếp theo là danh sách cảnh báo và WebSocket frontend

Tài liệu này là nguồn thông tin chính về tiến độ thực tế. Sau mỗi buổi làm việc, cập nhật trạng thái đầu việc và mục **Bàn giao cho phiên làm việc tiếp theo**.

## 1. Cách tiếp tục dự án trong một chat mới

Yêu cầu chat mới thực hiện lần lượt:

1. Đọc `README.md`, `docs/architecture.md`, `docs/plan.md` và `docs/references.md`.
2. Chạy `git status` và kiểm tra cấu trúc repository, không giả định nội dung trong tài liệu đã được triển khai.
3. Đối chiếu mục **Tiến độ thực tế** với file và code đang tồn tại.
4. Thực hiện đầu việc đầu tiên có trạng thái `READY` trong **Backlog chi tiết**.
5. Sau khi kiểm chứng kết quả, cập nhật file này với ngày, trạng thái và bằng chứng.

## 2. Quy ước trạng thái

| Trạng thái | Ý nghĩa |
| --- | --- |
| `DONE` | Đã hoàn thành và có file, code, ảnh hoặc kết quả kiểm thử làm bằng chứng |
| `IN PROGRESS` | Đang thực hiện |
| `READY` | Đủ thông tin để bắt đầu ngay |
| `BLOCKED` | Không thể tiếp tục nếu chưa giải quyết phụ thuộc ghi kèm |
| `TODO` | Chưa đến thời điểm hoặc chưa đủ thông tin |

Không chuyển một đầu việc sang `DONE` chỉ vì đã thảo luận hoặc đã lập kế hoạch.

## 3. Tiến độ thực tế

### Đã hoàn thành

- `DONE` Xác định đề tài: hệ thống IoT quan sát và cảnh báo sớm nguy cơ ngập cục bộ.
- `DONE` Tạo repository `iot-flood-monitoring`.
- `DONE` Tạo README giới thiệu phạm vi, chức năng và kiến trúc cấp cao.
- `DONE` Tạo tài liệu kiến trúc ban đầu, luồng dữ liệu và MQTT topic dự kiến.
- `DONE` Khảo sát các repository và tài liệu mã nguồn có thể tham khảo.
- `DONE` Chốt stack: PlatformIO/Arduino, Mosquitto, FastAPI, PostgreSQL và Vue 3/TypeScript.
- `DONE` Tạo và kiểm thử Docker Compose cho Mosquitto và PostgreSQL.
- `DONE` Smoke test PostgreSQL và MQTT publish/subscribe trên máy phát triển.
- `DONE` Tạo telemetry simulator với năm kịch bản và kiểm thử end-to-end qua Mosquitto.
- `DONE` Tạo khung FastAPI, migration PostgreSQL, MQTT ingestion và REST API latest/history.
- `DONE` Chạy 7 unit test backend trong Docker, tất cả đều pass ngày 13/10/2026.
- `DONE` Smoke test luồng simulator → MQTT → backend → PostgreSQL → REST API ngày 13/10/2026.
- `DONE` Triển khai và kiểm thử cảnh báo mực nước, tăng nhanh, mưa lớn, lỗi cảm biến và offline.
- `DONE` WebSocket phát telemetry, status và snapshot cảnh báo theo thời gian thực.
- `DONE` Khởi tạo Vue 3/TypeScript/Vite và bố cục dashboard responsive.
- `DONE` Refactor backend theo lớp `api → services/domain → repositories`; `main.py` chỉ còn application factory và lifecycle.
- `DONE` Tách frontend thành view, component và kiểu dữ liệu dùng chung.
- `DONE` Chuyển WebSocket probe sang `backend/scripts/` và tạo smoke test Python đa nền tảng.
- `DONE` FE-003: dashboard đọc số đo gần nhất qua REST, hiển thị mực nước/lượng mưa và thời gian lấy mẫu theo giờ Việt Nam.
- `DONE` FE-004: hiển thị online/offline, trạng thái cảm biến và RSSI mẫu gần nhất; chọn thiết bị và cập nhật thủ công.
- `DONE` Kiểm tra dashboard bằng Playwright với REST thật và phản hồi giả lập cho các trạng thái lỗi/loading/cảm biến; kiểm tra desktop và mobile.
- `DONE` Thiết kế lại dashboard theo bố cục giám sát gọn; chỉ đổi template/CSS, giữ nguyên script, kiểm tra responsive 360px và production build đạt.
- `DONE` Chia và commit mã nguồn, hạ tầng, smoke test và tài liệu thành các nhóm riêng ngày 14/10/2026.

### Chưa hoàn thành

- Chưa chốt cảm biến mực nước và cảm biến lượng mưa sẽ mua.
- Chưa xác nhận tình trạng mua linh kiện.
- Chưa tạo source code firmware.
- Frontend chưa có danh sách cảnh báo, biểu đồ lịch sử hoặc cập nhật tự động qua WebSocket. Số đo/trạng thái hiện cập nhật bằng REST khi mở trang, đổi thiết bị hoặc bấm **Cập nhật**.
- Chưa có dữ liệu cảm biến, kết quả hiệu chuẩn hoặc mô hình thử nghiệm.

## 4. Phạm vi MVP bắt buộc

MVP được xem là hoàn thành khi chứng minh được luồng sau:

```text
Cảm biến hoặc bộ giả lập
    -> ESP32/MQTT publisher
    -> MQTT broker
    -> Backend
    -> PostgreSQL
    -> REST API/WebSocket
    -> Giao diện web và cảnh báo
```

MVP gồm:

- Một nút đo có định danh ổn định.
- Giá trị mực nước theo centimet và lượng mưa theo milimet.
- Dữ liệu thời gian thực và lịch sử.
- Trạng thái online/offline của thiết bị.
- Cảnh báo vượt ngưỡng mực nước.
- Cảnh báo tốc độ tăng mực nước.
- Cảnh báo mất kết nối hoặc dữ liệu cảm biến không hợp lệ.
- Mô hình thử nghiệm và kết quả đánh giá định lượng.

LoRa, bản đồ, nhiều nút đo, SMS, ứng dụng di động và dự báo bằng máy học không thuộc MVP.

## 5. Mốc thời gian điều chỉnh

| Thời gian | Mục tiêu | Điều kiện hoàn thành |
| --- | --- | --- |
| 09–12/10 | Khóa phạm vi và khởi tạo kỹ thuật | Chốt stack, BOM, hợp đồng dữ liệu và commit đầu tiên |
| 13–19/10 | Firmware nền và MQTT | ESP32 hoặc simulator gửi được telemetry và heartbeat |
| 20–26/10 | Cảm biến và hiệu chuẩn bước đầu | Đọc ổn định hai cảm biến, phát hiện giá trị lỗi |
| 27/10–02/11 | Backend tiếp nhận dữ liệu | Backend subscribe MQTT, kiểm tra payload và lưu PostgreSQL |
| 03–09/11 | API và cảnh báo | Có API latest/history và ba loại cảnh báo cơ bản |
| 10–16/11 | Frontend dữ liệu hiện tại | Dashboard hiển thị số đo, trạng thái và cảnh báo |
| 17–23/11 | Lịch sử và thời gian thực | Biểu đồ lịch sử và cập nhật WebSocket hoạt động |
| 24–30/11 | Tích hợp MVP | Luồng cảm biến đến giao diện chạy xuyên suốt |
| 01–07/12 | Ổn định hệ thống | Có reconnect, logging, cấu hình và xử lý lỗi |
| 08–14/12 | Mô hình và kịch bản kiểm thử | Hoàn thành bể thử, dụng cụ đo chuẩn và test plan |
| 15–21/12 | Thực nghiệm | Thu đủ dữ liệu độ chính xác, độ trễ và độ ổn định |
| 22–28/12 | Đóng băng sản phẩm | Hoàn thiện code, tài liệu, ảnh, biểu đồ và báo cáo nháp |
| 29/12–05/01 | Dự phòng và bàn giao | Báo cáo cuối, slide, video và kịch bản demo |

Trong hai tuần đầu nên dành 16–18 giờ/tuần để bù phần khởi động chậm. Sau khi có MVP nền, duy trì tối thiểu 12 giờ/tuần.

## 6. Backlog chi tiết

### 6.1. Quyết định và quản lý dự án

| ID | Trạng thái | Đầu việc | Kết quả cần có |
| --- | --- | --- | --- |
| PM-001 | `DONE` | Chốt stack công nghệ | Quyết định được ghi trong architecture và ADR-0001 |
| PM-002 | `READY` | Chốt danh sách linh kiện và ngân sách | BOM có model, số lượng, giá dự kiến và trạng thái mua |
| PM-003 | `DONE` | Đưa README và tài liệu vào Git | README và tài liệu được lưu trong commit tài liệu riêng ngày 14/10/2026 |
| PM-004 | `TODO` | Tạo nhật ký tiến độ tuần | Mỗi tuần có việc đã làm, vấn đề, số giờ và kế hoạch tuần sau |
| PM-005 | `TODO` | Theo dõi rủi ro | Bảng rủi ro phần cứng, thời gian, dữ liệu và tích hợp |

### 6.2. Firmware và phần cứng

| ID | Trạng thái | Đầu việc | Kết quả cần có |
| --- | --- | --- | --- |
| FW-001 | `DONE` | Chọn môi trường firmware | PlatformIO với Arduino framework |
| FW-002 | `TODO` | Khởi tạo project ESP32 | Build và nạp được chương trình hello/serial |
| FW-003 | `TODO` | Tạo module cấu hình | Wi-Fi, MQTT, device ID và chu kỳ gửi không hard-code vào logic |
| FW-004 | `TODO` | Đọc cảm biến mực nước | Có giá trị cm, timeout, giới hạn hợp lệ và log lỗi |
| FW-005 | `TODO` | Đọc cảm biến lượng mưa | Có tổng mm và lượng mưa theo cửa sổ thời gian |
| FW-006 | `TODO` | Lọc và hiệu chuẩn | Ghi dữ liệu thô, giá trị đã lọc và hệ số hiệu chuẩn |
| FW-007 | `TODO` | Publish MQTT | Telemetry đúng schema, QoS được chốt, reconnect hoạt động |
| FW-008 | `TODO` | Heartbeat và trạng thái | Backend xác định được online/offline |
| FW-009 | `TODO` | Cảnh báo cục bộ | LED/buzzer hoạt động với ngưỡng thử nghiệm |

### 6.3. Hạ tầng phát triển

| ID | Trạng thái | Đầu việc | Kết quả cần có |
| --- | --- | --- | --- |
| INF-001 | `DONE` | Tạo Docker Compose nền | Mosquitto và PostgreSQL đều healthy; smoke test đã pass ngày 13/10/2026 |
| INF-002 | `TODO` | Cấu hình Mosquitto cho phát triển | Có listener, user/password và volume dữ liệu |
| INF-003 | `DONE` | Tạo telemetry simulator | Năm kịch bản; 5 unit test và MQTT end-to-end đã pass ngày 13/10/2026 |
| INF-004 | `DONE` | Quản lý biến môi trường | Có `.env.example`, `.env` được bỏ qua bởi Git |
| INF-005 | `TODO` | Thêm kiểm tra tự động | Có lệnh lint/test/build tối thiểu cho từng thành phần |

### 6.4. Backend và cơ sở dữ liệu

| ID | Trạng thái | Đầu việc | Kết quả cần có |
| --- | --- | --- | --- |
| BE-001 | `DONE` | Khởi tạo FastAPI | Container healthy và `/health` trả 200 ngày 13/10/2026 |
| BE-002 | `DONE` | Thiết kế schema database | Migration `0001_initial_schema` đã chạy trên PostgreSQL |
| BE-003 | `DONE` | MQTT consumer | Nhận telemetry/status thật từ Mosquitto trong smoke test |
| BE-004 | `DONE` | Lưu telemetry an toàn | Lưu đủ timestamp server/device; khóa chống trùng và unit test duplicate đã pass |
| BE-005 | `DONE` | API dữ liệu hiện tại | Endpoint latest và trạng thái thiết bị hoạt động |
| BE-006 | `DONE` | API lịch sử | Endpoint history trả đúng 3 mẫu và hỗ trợ lọc thời gian/limit |
| BE-007 | `DONE` | Bộ luật cảnh báo | Luật thuần tách khỏi DB; flood/sensor-error/đóng cảnh báo đã pass end-to-end ngày 13/10/2026 |
| BE-008 | `DONE` | WebSocket | Client thật nhận telemetry/alert từ kịch bản flood ngày 13/10/2026 |
| BE-009 | `DONE` | Kiểm thử backend | 20 unit/integration test pass trong Docker ngày 13/10/2026 |

### 6.5. Frontend

| ID | Trạng thái | Đầu việc | Kết quả cần có |
| --- | --- | --- | --- |
| FE-001 | `DONE` | Khởi tạo Vue 3 + TypeScript + Vite | Type-check/build pass; container healthy tại cổng 5173 ngày 13/10/2026 |
| FE-002 | `DONE` | Tạo bố cục dashboard | Có view/component/type riêng; type-check và production build pass ngày 13/10/2026 |
| FE-003 | `DONE` | Hiển thị số đo mới nhất | REST thật khớp mực nước/lượng mưa/timestamp; null không hiển thị thành 0; build và browser check pass ngày 13/10/2026 |
| FE-004 | `DONE` | Hiển thị trạng thái thiết bị | Online/offline, cảm biến và RSSI mẫu gần nhất; trạng thái offline giữ số đo đã lưu có chú thích |
| FE-005 | `TODO` | Biểu đồ lịch sử | Chọn khoảng thời gian và hiển thị đúng đơn vị |
| FE-006 | `READY` | Danh sách cảnh báo | Mức độ, nguyên nhân, thời gian và trạng thái xử lý |
| FE-007 | `READY` | Cập nhật WebSocket | Giao diện cập nhật không cần tải lại trang |
| FE-008 | `IN PROGRESS` | Trạng thái lỗi giao diện | REST đã có loading/API lỗi/404/thử lại; còn trạng thái lỗi lịch sử/cảnh báo và reconnect WebSocket |

### 6.6. Kiểm thử, thực nghiệm và báo cáo

| ID | Trạng thái | Đầu việc | Kết quả cần có |
| --- | --- | --- | --- |
| TEST-001 | `TODO` | Thiết kế mô hình thử nghiệm | Sơ đồ, kích thước bể, vị trí cảm biến và phương pháp tạo mưa |
| TEST-002 | `TODO` | Viết test plan | Ma trận kịch bản, đầu vào, kết quả mong đợi và tiêu chí đạt |
| TEST-003 | `TODO` | Đánh giá độ chính xác | So sánh cảm biến với thước/ống đong tại nhiều mức |
| TEST-004 | `TODO` | Đánh giá độ trễ | Đo từ lúc lấy mẫu đến lúc giao diện cập nhật/cảnh báo |
| TEST-005 | `TODO` | Đánh giá độ ổn định | Chạy liên tục và thống kê mất mẫu, reconnect, lỗi |
| TEST-006 | `TODO` | Kiểm thử tình huống lỗi | Mất Wi-Fi, broker dừng, cảm biến lỗi và thiết bị khởi động lại |
| DOC-001 | `IN PROGRESS` | Viết kiến trúc và tài liệu kỹ thuật | Cập nhật cùng code, không chờ đến cuối kỳ |
| DOC-002 | `TODO` | Viết báo cáo theo chương | Có bản nháp từng chương từ giai đoạn triển khai |
| DOC-003 | `TODO` | Chuẩn bị minh chứng | Ảnh lắp đặt, log, dữ liệu CSV, biểu đồ và video demo |

## 7. Tiêu chí hoàn thành toàn bộ đồ án

- Repository có hướng dẫn chạy lại hệ thống từ đầu.
- Người khác có thể dùng Docker Compose để chạy các dịch vụ phần mềm.
- Thiết bị gửi dữ liệu thật và hệ thống vẫn có simulator để kiểm thử.
- Không lưu Wi-Fi password, token hoặc mật khẩu database trong Git.
- Các giá trị hiển thị có đơn vị, timestamp và trạng thái chất lượng dữ liệu.
- Cảnh báo có lý do rõ ràng và tái hiện được bằng kịch bản kiểm thử.
- Báo cáo có phương pháp hiệu chuẩn, số liệu gốc và cách tính các chỉ số.
- Demo có phương án dự phòng bằng dữ liệu ghi sẵn hoặc video.

## 8. Bàn giao cho phiên làm việc tiếp theo

### Việc cần làm ngay

1. Thực hiện `PM-002`: chốt BOM và xác nhận linh kiện đã mua/chưa mua.
2. Tiếp tục phần mềm với `FE-006`: nối REST danh sách cảnh báo, sau đó `FE-007`: WebSocket và reconnect. `FE-003`/`FE-004` đã hoàn thành.
3. Thêm biểu đồ lịch sử `FE-005` và đọc ngưỡng thật từ backend; các đường ngưỡng hiện chỉ minh họa.

### Thông tin cần người thực hiện xác nhận

- Đã mua ESP32 và cảm biến nào hay chưa.
- Máy phát triển đã có Docker Desktop và PlatformIO hay chưa.
- Có thể dành bao nhiêu giờ mỗi tuần trong hai tuần tới.

### Bằng chứng hiện có

- `README.md`
- `docs/architecture.md`
- `docs/references.md`
- `docs/decisions/0001-technology-stack.md`
- `compose.yaml`, `.env.example` và cấu hình Mosquitto
- `scripts/infra-smoke-test.ps1`
- `simulator/` gồm bộ sinh dữ liệu, MQTT publisher, Dockerfile, hướng dẫn và unit test.
- Runtime local ngày 13/10/2026: PostgreSQL tại `127.0.0.1:5432`; Docker Mosquitto tại cổng host `1884` vì dịch vụ Mosquitto của Windows đang dùng `1883`.
- PostgreSQL và Docker Mosquitto đều healthy; smoke test đã pass.
- Simulator đã publish thành công kịch bản `flood` và `sensor-error`; subscriber nhận đủ telemetry, trạng thái online/offline và giá trị lỗi `null`.
- `backend/` gồm FastAPI, SQLAlchemy models, Alembic migration, MQTT consumer, REST API và 7 unit test đã pass.
- `scripts/smoke_test.py` đã pass ngày 13/10/2026 trên Windows; REST trả đúng 3 mẫu và WebSocket nhận telemetry cùng water-level alert.
- Alembic ở revision `0001_initial_schema`; backend, PostgreSQL và Mosquitto đều healthy sau kiểm thử.
- Backend có 12 unit test pass. Kịch bản `flood` tạo water-level, rapid-rise, heavy-rain và offline alert; `sensor-error` tạo sensor-error alert; dữ liệu normal đóng các cảnh báo đã hết điều kiện.
- Backend có tổng cộng 20 unit/integration test pass sau refactor. WebSocket client lọc theo device đã nhận status, telemetry và snapshot water-level alert từ luồng MQTT thật.
- Frontend dùng Vue 3.5, TypeScript, Vite và Nginx; `npm run build` pass, container healthy, trang `/` trả 200 và reverse proxy `/api` gọi được backend.
- Frontend đã kết nối REST device/latest qua Axios và `useReadings`; Vite có proxy `/api` và `/ws` cho development. Chưa có kết nối WebSocket frontend; firmware chưa có source code.
- Browser check FE-003/FE-004 đã pass: `node-001` từ simulator thật hiển thị 17,64 cm, 0,48 mm, timestamp đúng và offline; chọn thiết bị không tồn tại trả trạng thái trống. Phản hồi giả lập kiểm tra loading, online, cảm biến lỗi/null, thiết bị chỉ có status, API 500 và phục hồi.
- Ảnh kiểm tra local tại `output/playwright/fe003-desktop.png` và `output/playwright/fe003-mobile.png`; script `output/playwright/rest-dashboard-check.js`. Các artifact này được bỏ qua bởi Git.
- Dashboard mới đã qua type-check/build và Playwright desktop/360px, gồm trường hợp trống, cảm biến lỗi và số đo lớn. Checksum các khối script Vue trước/sau thiết kế lại khớp nhau.
- Commit `14907c2`: refactor backend; `1da5934`: smoke test đa nền tảng; `e182901`: frontend REST/dashboard; `405777b`: tích hợp hạ tầng frontend và loại artifact khỏi Git/build. Đợt này chỉ commit local, chưa push.
