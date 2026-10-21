# Kế hoạch kiểm thử firmware nền

> 19/10/2026. Đây là quy trình cần thực hiện, không phải kết quả thử trên board.

Điều kiện: xác nhận model ESP32, cáp dữ liệu/cổng COM; cấu hình Wi-Fi/NTP/broker;
Compose hoạt động; dùng `tank-demo-001`, không có publisher khác cùng ID.
Ghi phiên bản code, environment, khoảng gửi, thời gian bắt đầu/kết thúc và lỗi phát sinh.
Không ghi mật khẩu Wi-Fi vào log thực nghiệm.

| Mã | Thao tác | Kết quả cần đối chiếu | Lặp / bằng chứng |
| --- | --- | --- | --- |
| F01 | Boot fake, để bình thường | NTP → MQTT → online → ít nhất 12 mẫu; schema v2, đúng ID, sequence tăng; API/web nhận ba số đo | 3 lần boot; log serial + API history |
| F02 | Phím 1..5, mỗi kịch bản ít nhất ba mẫu rồi về 0 | Đúng loại/mức cảnh báo; không tạo nhiều cảnh báo đang mở cùng loại; về 0 đóng cảnh báo | 3 vòng; API alerts và ảnh web |
| F03 | Phím 6 chạy ít nhất chín mẫu | Mẫu 3/6/9 trong chu kỳ lỗi lần lượt một đầu dò; các số còn lại lưu được; biểu đồ ngắt tại null | 3 chu kỳ lỗi; payload + history |
| F04 | Chặn NTP trước khi boot rồi cho phép lại | Không gửi giờ 1970 hoặc mẫu chưa đồng bộ; tiếp tục khi nhận được giờ | 3 lần; serial và thời điểm mẫu đầu |
| F05 | Ngắt Wi-Fi 60 giây rồi bật lại | Last Will offline; tự nối lại, publish online/mẫu mới; web phục hồi; không giả lập dữ liệu trong khoảng mất mạng | 3 lần; thời điểm ngắt/nối, broker/API/serial |
| F06 | Dừng broker rồi khởi động lại | Không reset liên tục, tự thử lại; sau broker hoạt động nhận dữ liệu mới | 3 lần; reconnect log và history |
| F07 | Rút nguồn ESP32 khi đang gửi | Broker phát Last Will; backend ghi offline theo giờ nhận, không kéo last_seen về lúc boot; cắm lại phục hồi | 3 lần; API device/alerts + ghi giờ bằng tay |
| F08 | Chạy liên tục chế độ normal | Sequence/mẫu nhận ổn định, không reboot bất thường; ghi khoảng trống, mất mẫu và độ trễ quan sát được | Ban đầu 1 giờ; sau ổn định tăng lên 24 giờ |
| F09 | Bật từng kênh analog, chưa/đã điền hai điểm hiệu chuẩn | Raw mV đọc được; calibration thiếu trả null; đủ calibration thì đối chiếu buffer/mẫu tham chiếu riêng | 3 lần mỗi mốc; ghi nguồn, mV và nhiệt độ |
| F10 | Đọc DS18B20, rút/cắm lại đầu dò | Không phát -127 như nhiệt độ hợp lệ; lỗi thành null, tự tìm lại và phục hồi | 3 lần; serial v + API history |
| F11 | Bật PIR/LED, thử OUT cao/thấp và mất Wi-Fi | Warmup không bật đèn; chuyển động bật, hết tín hiệu 15 giây tắt; tác động mới gia hạn; vẫn chạy khi mất mạng | 3 chu kỳ; ghi thời gian/ảnh |

Với F03, sequence không reset khi đổi phím; quan sát các sequence chia hết cho 3 tiếp theo,
không mặc định đó là mẫu thứ ba kể từ lúc nhấn phím.
Với F05/F07, quan sát tối đa hai phút và ghi độ trễ thực tế; keepalive 30 giây không có nghĩa web offline ngay lập tức.
F06 không dùng Last Will làm bằng chứng nếu chính broker đang ngừng hoạt động.

Mỗi lượt lưu: mã case, số lần lặp, thời gian, expected, actual, PASS/FAIL, đường dẫn log/ảnh.
Log kiểm thử lưu trong `output/firmware/` (local, không commit). Export dữ liệu trước khi dọn môi trường.
Độ trễ thiết bị → server cần đồng hồ hai phía đồng bộ; PUBACK không thay cho thời điểm lưu database.

Đã kiểm chứng ngày 21/10: ba environment build; bốn test host với hiệu chuẩn/lọc/PIR và backend SQLite.
Pipeline PostgreSQL/MQTT đã kiểm chứng riêng ngày 20/10; chưa phải dữ liệu từ ESP32.
Chưa kiểm chứng: F01–F11 trên ESP32, cảm biến và hiệu chuẩn thật. Xem hardware-bringup.md.
