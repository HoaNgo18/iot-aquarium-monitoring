# Kế hoạch chuyển hướng sang giám sát môi trường bể nuôi cá

> **Lưu trữ lịch sử:** bản nháp 15/10 đã được thay thế bởi [plan hiện hành](plan.md)
> và [ADR-0002](decisions/0002-aquarium-transition.md) từ 19/10.
> Tên chốt là "Xây dựng hệ thống IoT giám sát bể nuôi cá", ba chỉ số pH/nhiệt độ/độ đục.
> Các phương án camera, cổng quyết định 18/10 và schema trong bản nháp bên dưới không còn là kế hoạch triển khai.

> Ngày lập: 15/10/2026
>
> Trạng thái: Bản nháp để trao đổi với giảng viên hướng dẫn, chưa thay thế Phiếu giao nhiệm vụ hiện tại
>
> Mốc cần chốt tên đề tài trên QLĐT: trước 01/11/2026

## 1. Đề xuất phạm vi

Tên đề tài đề xuất:

**Nghiên cứu và xây dựng hệ thống IoT giám sát môi trường bể nuôi cá và cảnh báo điều kiện bất thường**

Không nên dùng tên **giám sát sức khỏe cá** nếu hệ thống chỉ đo môi trường. Nhiệt độ, độ đục hoặc pH chỉ phản ánh điều kiện sống và mức rủi ro, không đủ để kết luận cá khỏe, mắc bệnh hoặc sắp chết. Tên đề xuất vẫn giữ đúng trọng tâm IoT, có thể đánh giá định lượng và phù hợp với phần mềm đã xây dựng.

### MVP đề xuất

- Một nút ESP32 có định danh ổn định.
- Đo nhiệt độ nước.
- Đo độ đục tương đối của nước. Chỉ công bố đơn vị NTU nếu có quy trình và thiết bị tham chiếu đủ tin cậy; nếu không, dùng điện áp, ADC hoặc chỉ số độ đục tương đối.
- Truyền dữ liệu qua Wi-Fi và MQTT.
- Lưu dữ liệu hiện tại và lịch sử trong PostgreSQL.
- Hiển thị dashboard thời gian thực và biểu đồ lịch sử.
- Cảnh báo nhiệt độ ngoài vùng cấu hình, độ đục tăng bất thường, lỗi cảm biến và thiết bị mất kết nối.
- Đánh giá độ trễ, độ ổn định, tỷ lệ mất mẫu và khả năng phát hiện các kịch bản bất thường.

### Ngoài phạm vi MVP

- Chẩn đoán bệnh của cá.
- Đo oxy hòa tan, amoniac hoặc nitrit nếu chưa có thiết bị và dung dịch hiệu chuẩn phù hợp.
- Điều khiển máy bơm, máy sưởi hoặc máy cho ăn tự động.
- Ứng dụng di động, SMS, nhiều bể hoặc triển khai Internet công cộng.
- Mô hình học máy dự đoán sức khỏe cá.

## 2. Phương án phần cứng và điểm quyết định

### Phương án A — cảm biến tối thiểu, khuyến nghị

- ESP32.
- Một cảm biến nhiệt độ nước chống nước.
- Một cảm biến độ đục hoặc mạch quang học tự xây dựng để tạo chỉ số độ đục tương đối.
- Bể nhỏ, nhiệt kế tham chiếu và các mẫu nước có độ đục khác nhau để thử nghiệm.

Phương án này giữ được bản chất IoT và tái sử dụng nhiều nhất phần đã làm. Chỉ chốt model sau khi xác nhận có thể mua hoặc mượn thực tế.

### Phương án B — chỉ có cảm biến nhiệt độ

Vẫn có thể làm prototype truyền dữ liệu và cảnh báo, nhưng khối lượng phần cảm biến và giá trị bài toán khá mỏng. Chỉ dùng khi giảng viên hướng dẫn đồng ý và bổ sung một nguồn dữ liệu thứ hai, ví dụ lịch cho ăn nhập thủ công hoặc trạng thái thiết bị. Không nên lấy đây làm phương án chính.

### Phương án C — không mua được bất kỳ cảm biến nào

Chuyển sang **hệ thống giám sát hoạt động của cá bằng camera và cảnh báo hành vi bất thường**. Webcam hoặc camera điện thoại cung cấp video; một chương trình xử lý ảnh tạo chỉ số vận động và gửi telemetry qua MQTT.

Phương án C không cần cảm biến nước nhưng rủi ro cao hơn: phải xây dựng pipeline video, chọn dữ liệu, định nghĩa hành vi bất thường và đánh giá thuật toán. Chỉ chọn nếu đã xác nhận có camera, bể cá hoặc video hợp lệ và giảng viên chấp nhận hướng xử lý ảnh. Nền tảng backend/frontend vẫn dùng lại được nhưng phần miền nghiệp vụ phải thay nhiều hơn phương án A.

### Cổng quyết định

Chậm nhất ngày **18/10/2026**, cần chốt một trong hai kết quả:

1. Có thể mua/mượn ESP32, cảm biến nhiệt độ nước và giải pháp đo độ đục: chọn phương án A.
2. Không có cảm biến nhưng có nguồn video phù hợp: trao đổi với giảng viên để chọn phương án C.

Không tiếp tục đổi code miền nghiệp vụ trước khi cổng quyết định này hoàn tất.

## 3. Khối lượng đã hoàn thành và khả năng tái sử dụng

### Giữ gần như nguyên vẹn

- Docker Compose, Mosquitto và PostgreSQL.
- FastAPI application factory, cấu hình, kết nối cơ sở dữ liệu và Alembic.
- Luồng MQTT consumer, kiểm tra topic, ingest và chống bản tin trùng.
- Quản lý thiết bị, trạng thái online/offline và thời điểm thấy thiết bị gần nhất.
- REST API latest/history và cấu trúc repository/service.
- WebSocket realtime, heartbeat trình duyệt, reconnect và đồng bộ bù bằng REST.
- Khung Vue 3/TypeScript, chọn thiết bị, trạng thái loading/error/offline và giao diện responsive.
- Danh sách cảnh báo, cơ chế mở/kết thúc cảnh báo và smoke-test end-to-end.

### Cần đổi theo miền bài toán

- Đổi namespace/topic từ `flood-monitoring` sang tên trung tính hoặc `aquarium-monitoring`.
- Đổi schema telemetry từ `water_level_cm`, `rainfall_mm` sang `water_temperature_c` và `turbidity_value` cùng đơn vị rõ ràng.
- Thêm migration mới; không sửa migration `0001` đã tồn tại.
- Thay ngưỡng mực nước/mưa bằng vùng nhiệt độ và ngưỡng/độ biến thiên độ đục.
- Viết lại simulator thành các kịch bản `normal`, `temperature-low`, `temperature-high`, `turbidity-rise`, `sensor-error`, `offline`.
- Thay metric card, nhãn, biểu đồ và nội dung cảnh báo trên frontend.
- Cập nhật README, kiến trúc, BOM, kế hoạch kiểm thử và Phiếu giao nhiệm vụ sau khi giảng viên duyệt.

### Phần chưa làm vẫn phải thực hiện

- Firmware ESP32 và cấu hình Wi-Fi/MQTT.
- Đọc, lọc, kiểm tra lỗi và hiệu chuẩn cảm biến.
- Biểu đồ lịch sử dùng dữ liệu thật.
- Mô hình bể thử và bộ dữ liệu thực nghiệm.
- Đánh giá định lượng, báo cáo, slide và video demo.

### Ước lượng trạng thái sau khi chuyển hướng

- Khoảng **65–75% nền tảng phần mềm** có thể giữ lại.
- Khoảng **25–35% code và tài liệu miền nghiệp vụ** phải đổi.
- Nếu tính cả firmware, phần cứng, thực nghiệm và báo cáo, đề tài mới đang ở khoảng **35–45% tổng khối lượng**, không phải 70% hoàn thành.

Các tỷ lệ trên là ước lượng quản lý, không phải số liệu LOC. Mức hoàn thành cuối cùng phải dựa trên sản phẩm và minh chứng kiểm thử.

## 4. Hợp đồng dữ liệu dự kiến cho phương án A

```json
{
  "schema_version": 2,
  "device_id": "tank-001",
  "timestamp": "2026-10-20T10:00:00Z",
  "sequence": 1,
  "water_temperature_c": 27.4,
  "turbidity_value": 412,
  "turbidity_unit": "adc",
  "signal_strength_dbm": -61,
  "sensor_status": "normal"
}
```

Nguyên tắc:

- Trường đo lỗi nhận `null`, không đổi thành 0.
- `turbidity_unit` phải thể hiện đúng dữ liệu thực tế (`adc`, `voltage`, `relative` hoặc `ntu`).
- Ngưỡng nhiệt độ phải là cấu hình theo đối tượng nuôi hoặc kịch bản thử nghiệm, không hard-code như một chuẩn chung cho mọi loài cá.
- Cảnh báo “độ đục tăng” dựa trên thay đổi trong cửa sổ thời gian sẽ có ý nghĩa hơn một ngưỡng tuyệt đối nếu không có hiệu chuẩn NTU.

## 5. Backlog chuyển đổi

| ID | Ưu tiên | Đầu việc | Kết quả cần có |
| --- | --- | --- | --- |
| TR-001 | P0 | Trao đổi với GVHD về tên và phạm vi mới | GVHD đồng ý tên đề tài, mục tiêu, đầu vào đo và tiêu chí đánh giá |
| TR-002 | P0 | Xác nhận phần cứng thực sự có thể mua/mượn | Ảnh/link/model, giao tiếp, điện áp, ngày có thiết bị; chọn A hoặc C |
| TR-003 | P0 | Cập nhật Phiếu giao nhiệm vụ | Tên, mục tiêu, sản phẩm kỳ vọng và 5 nội dung triển khai khớp đề tài mới trước 01/11 |
| TR-004 | P0 | Chốt schema telemetry v2 | JSON mẫu, đơn vị, miền hợp lệ và quy tắc `null` |
| TR-005 | P0 | Tạo migration database mới | Lưu được trường mới, dữ liệu cũ không bị xóa ngoài ý muốn |
| TR-006 | P0 | Chuyển simulator và test backend | Sáu kịch bản mới; unit/integration test pass |
| TR-007 | P0 | Chuyển luật cảnh báo | Nhiệt độ thấp/cao, độ đục tăng, sensor error và offline |
| TR-008 | P0 | Chuyển dashboard | Metric, cảnh báo và trạng thái đúng miền bể cá |
| TR-009 | P0 | Hoàn thiện biểu đồ lịch sử | Chọn khoảng thời gian, dữ liệu thật và đường ngưỡng cấu hình |
| HW-001 | P0 | Khởi tạo firmware ESP32 | Build, flash, log serial và cấu hình tách khỏi logic |
| HW-002 | P0 | Đọc cảm biến và xử lý lỗi | Giá trị thô/đã lọc, timeout, phạm vi hợp lệ và mã lỗi |
| HW-003 | P0 | MQTT và reconnect | Telemetry/status đúng schema, QoS và Last Will hoạt động |
| EXP-001 | P0 | Viết test plan | Kịch bản, đầu vào, kết quả mong đợi, số lần lặp và tiêu chí đạt |
| EXP-002 | P0 | Hiệu chuẩn/đối chiếu nhiệt độ | Bảng so sánh với nhiệt kế tham chiếu tại nhiều mức |
| EXP-003 | P0 | Đánh giá chỉ số độ đục | Các mức mẫu lặp lại; công bố đúng đơn vị và giới hạn phép đo |
| EXP-004 | P0 | Đánh giá hệ thống | Độ trễ, mất mẫu, reconnect, chạy liên tục và cảnh báo |
| DOC-001 | P0 | Viết báo cáo song song | Hoàn thành từng chương và lưu ảnh/log/CSV ngay khi thử nghiệm |
| OPT-001 | P1 | Xác nhận cảnh báo trên web | Lưu người/thời điểm xác nhận; không chặn MVP |
| OPT-002 | P2 | Điều khiển thiết bị | Chỉ làm sau khi MVP và thực nghiệm đã hoàn tất |

## 6. Lịch triển khai điều chỉnh

| Thời gian | Mục tiêu | Điều kiện hoàn thành |
| --- | --- | --- |
| 15–18/10 | Chốt hướng chuyển đề tài | GVHD đồng ý định hướng; chọn phương án A hoặc C; xác nhận thiết bị/nguồn dữ liệu |
| 19–25/10 | Chuyển hợp đồng dữ liệu và backend | Schema v2, migration, simulator, ingest, API và luật cảnh báo mới có test |
| 26/10–01/11 | Chuyển frontend và hồ sơ đề tài | Dashboard đúng miền mới, biểu đồ lịch sử bản đầu; thông tin QLĐT/PGNV được cập nhật |
| 02–08/11 | Firmware nền | ESP32 kết nối Wi-Fi/MQTT, heartbeat, Last Will và telemetry giả lập tại thiết bị |
| 09–15/11 | Tích hợp cảm biến | Đọc ổn định hai đầu vào, ghi cả dữ liệu thô và đã lọc, phát hiện lỗi |
| 16–22/11 | Tích hợp end-to-end | Cảm biến → ESP32 → MQTT → backend → DB → dashboard/cảnh báo chạy xuyên suốt |
| 23–29/11 | Hiệu chuẩn và test plan | Có thiết kế thí nghiệm, dụng cụ tham chiếu, biểu mẫu ghi dữ liệu và chạy thử |
| 30/11–13/12 | Thực nghiệm chính | Thu dữ liệu độ chính xác/lặp lại, độ trễ, ổn định và các tình huống lỗi |
| 14–20/12 | Phân tích và hoàn thiện sản phẩm | Biểu đồ kết quả, sửa lỗi chính, đóng băng tính năng MVP |
| 21–27/12 | Báo cáo nháp và demo | Quyển nháp đầy đủ, ảnh, video, hướng dẫn chạy; gửi GVHD trước mốc xét bảo vệ 27/12 |
| 28/12–05/01 | Chỉnh sửa và bàn giao kỹ thuật | Code, tài liệu, dữ liệu thực nghiệm và kịch bản demo ổn định |
| 06–12/01 | Hoàn thiện hồ sơ nộp | Quyển, mã nguồn và kết quả kiểm tra trùng lặp sẵn sàng trước 17h ngày 12/01 |

## 7. Tiêu chí hoàn thành MVP

MVP hoàn thành khi có đầy đủ bằng chứng cho chuỗi sau:

```text
Cảm biến thật
  → ESP32
  → Wi-Fi/MQTT
  → FastAPI
  → PostgreSQL
  → REST/WebSocket
  → dashboard, lịch sử và cảnh báo
```

Tối thiểu phải có:

- 30–50 mẫu đối chiếu nhiệt độ ở ít nhất ba vùng giá trị hoặc điều kiện thử.
- Ít nhất ba mức độ đục tương đối, mỗi mức lặp lại nhiều lần; không gắn nhãn NTU nếu chưa hiệu chuẩn được.
- Đo độ trễ end-to-end trên nhiều bản tin và báo cáo trung vị, phân vị cao hoặc giá trị lớn nhất.
- Chạy liên tục tối thiểu 8 giờ để thống kê số bản tin gửi, nhận, trùng, mất và số lần reconnect.
- Kiểm thử mất Wi-Fi, broker dừng, cảm biến lỗi, ESP32 khởi động lại và dữ liệu ngoài miền hợp lệ.
- Lưu log, CSV, ảnh mô hình, ảnh dashboard và video demo làm minh chứng.

## 8. Rủi ro và cách giảm thiểu

| Rủi ro | Tác động | Cách giảm thiểu |
| --- | --- | --- |
| Tiếp tục không mua được cảm biến | Không có dữ liệu thật | Chốt khả năng mua/mượn trước 18/10; kích hoạt phương án camera nếu GVHD duyệt |
| Gọi đầu ra là “sức khỏe cá” quá mức bằng chứng | Bị phản biện về tính khoa học | Giới hạn kết luận ở điều kiện môi trường và cảnh báo rủi ro |
| Công bố NTU khi chỉ có ADC | Kết quả sai đơn vị | Dùng chỉ số tương đối cho đến khi có hiệu chuẩn đáng tin cậy |
| Đổi toàn bộ repository quá sớm | Mất dấu phần đã hoàn thành | Tạo nhánh chuyển đổi sau khi GVHD chốt; giữ commit lịch sử và migration cũ |
| Dồn thực nghiệm đến cuối kỳ | Thiếu dữ liệu cho báo cáo | Chuẩn bị test plan trong tháng 11 và thu dữ liệu từ cuối tháng 11 |
| Thêm AI/điều khiển tự động | Trễ MVP | Đưa toàn bộ tính năng này sang P2 hoặc hướng phát triển tương lai |

## 9. Việc cần làm ngay

1. Gửi GVHD tên đề tài đề xuất, phạm vi MVP và bảng phần đã hoàn thành/tái sử dụng.
2. Trong 48–72 giờ, xác nhận rõ: có ESP32 không, mua/mượn được cảm biến nhiệt độ nước không, có giải pháp độ đục không, ngân sách và ngày nhận.
3. Chỉ sau khi GVHD đồng ý, tạo nhánh chuyển đổi và thực hiện `TR-004` đến `TR-008`.
4. Cập nhật Phiếu giao nhiệm vụ trước hạn QLĐT; không để tên trên hệ thống khác tên trong quyển cuối.
