# Nhận linh kiện và cấu hình firmware

> Cập nhật 22/10/2026. ESP32 fake đã chạy toàn tuyến trên board thật; chưa lắp/kiểm chứng các cảm biến thật.
> Người thực hiện xác nhận đã đặt DS18B20, PH-4502C, bộ độ đục và HC-SR501; dự kiến nhận trong vài ngày.

## Cấu hình ban đầu

Profile hiện dành cho ESP32-WROOM/esp32dev thông thường; cần xác nhận board trước khi flash.
Tạo hai file local từ bản example trong firmware/include; các file local đã được Git bỏ qua:

- config.local.h: Wi-Fi, IP LAN máy chạy Docker, MQTT_PORT=1884 theo mapping hiện tại.
- sensors_config.local.h: cờ bật cảm biến, GPIO, điểm hiệu chuẩn và tùy chọn PIR/LED.

Build `esp32-sensors`; `esp32-pending-sensors` là alias tương thích.
`esp32-fake` vẫn giữ dữ liệu nước giả và ID tank-demo-001; sensors dùng tank-001.
Không chạy hai publisher cùng mã thiết bị.

| Tín hiệu | GPIO dự kiến trên ESP32 cổ điển | Mặc định |
| --- | --- | --- |
| DS18B20 DQ | 4 | ENABLE_TEMPERATURE=true |
| PH-4502C ngõ analog qua mạch phù hợp | 34 (ADC1) | ENABLE_PH=false |
| Độ đục ngõ analog qua mạch phù hợp | 35 (ADC1) | ENABLE_TURBIDITY=false |
| HC-SR501 OUT | 27 | ENABLE_PIR_LED=false |
| LED thử công suất nhỏ qua điện trở | 26 | Cùng cờ PIR/LED |

Đây là chân GPIO trên ESP32, không phải thứ tự chân của module. Đối chiếu chữ in trên board nhận được.
Mọi mạch nối chung GND khi phù hợp nguồn đã kiểm tra. Đèn công suất cần mạch điều khiển riêng, không cấp trực tiếp từ GPIO.

## Trình tự khi hàng về

1. Chụp hai mặt module, ghi nguồn/nhãn chân theo hướng dẫn người bán, kiểm tra đầu dò/dây đã đủ.
2. Thử riêng DS18B20 ba dây trước: VDD 3.3 V, GND, DQ GPIO4; điện trở kéo DQ lên 3.3 V thường dùng 4.7 kΩ.
   Xác nhận pinout của đầu dò thực tế, không suy ra chỉ từ màu dây. Không dùng parasite power trong driver này.
3. Cấp nguồn PH-4502C và độ đục theo thông số module; đo ngõ tín hiệu trước khi nối ADC.
   Không nối ngõ 5 V trực tiếp vào ESP32. Kiểm tra/chọn chia áp hoặc đệm theo điện áp thật.
4. Bật từng kênh analog sau khi xác nhận đầu ra là analog và điện áp tại GPIO phù hợp.
   Cửa sổ phần mềm hiện 150–3000 mV; giá trị ngoài cửa sổ là null, không phải mạch bảo vệ quá áp.
5. Mở serial 115200, nhấn `v` để xem raw mV. Có thể thực hiện trước khi cấu hình Wi-Fi;
   chưa hiệu chuẩn vẫn đọc raw nhưng chưa phát pH/độ đục hợp lệ.
6. Hiệu chuẩn từng kênh, đối chiếu lại bằng mẫu độc lập; ghi log, nhiệt độ, cấu hình và kết quả.
7. Kiểm tra toàn tuyến MQTT → database → web. Sau đó mới bật thử PIR/LED và chạy firmware-test-plan.md.

## PH-4502C

Model được người thực hiện xác nhận ngày 21/10. Ảnh là đầu dò BNC với mạch hai biến trở;
chưa xác nhận thứ tự chân, điện áp đầu ra hoặc chế độ ngâm đầu dò từ ảnh.
Chọn ngõ analog theo nhãn/tài liệu module (thường ký hiệu PO/AO); ngõ so sánh digital không thay cho số đo pH.

Firmware không gán hệ số pH mặc định. Sau khi nguồn, phần chia áp và chỉnh mạch đã cố định:

1. Dùng hai dung dịch buffer có giá trị biết rõ, theo hướng dẫn đầu dò; ghi đúng giá trị in trên buffer.
2. Với mỗi buffer, đợi ổn định và ghi nhiều lần raw mV tại **chân ESP32**, sau toàn bộ mạch chia áp/đệm.
3. Điền PH_POINT_A_MV/PH_POINT_A_VALUE và PH_POINT_B_MV/PH_POINT_B_VALUE.
   Hai điện áp phải cách nhau ít nhất 10 mV, nằm trong cửa sổ ADC; hai pH khác nhau và thuộc 0–14.
4. Build lại, thử lại hai mốc và một mẫu đối chiếu khác; ghi sai số. Không lấy số thử trong test C++ làm điểm hiệu chuẩn thật.

Đổi nguồn, điện trở chia áp, biến trở trên module hoặc đầu dò thì cần đối chiếu/hiệu chuẩn lại.
Chưa bù nhiệt pH; DS18B20 chỉ cung cấp nhiệt độ riêng. Cần giữ/ghi điều kiện nhiệt độ khi hiệu chuẩn và thực nghiệm.

## Bộ độ đục

Ảnh người thực hiện gửi: đầu đo kèm mạch đỏ ba chân và cáp, chưa có mã sản phẩm.
Chưa kết luận chân S là analog hoặc digital, chưa xác nhận điện áp và phần được phép ngâm.
Nếu chỉ có đầu ra digital thì không tạo được thang độ đục liên tục từ đầu ra đó; cần kiểm tra lại module trước khi bật driver ADC.

Sau khi xác nhận ngõ analog, cố định nguồn/mạch tín hiệu và cách đặt đầu đo:

- TURBIDITY_CLEAR_MV: mV của mẫu trong tham chiếu, được gán 0%.
- TURBIDITY_CLOUDY_REFERENCE_MV: mV của mẫu đục tham chiếu có thể tái lập, được gán 100%.
- Nội suy hai mốc và giới hạn kết quả 0–100%; điện áp ngoài cửa sổ ADC vẫn là null.

Đây là thang tương đối theo hai mẫu của mô hình, không phải NTU và không dùng công thức của module khác.
Lưu mô tả mẫu tham chiếu/cách chuẩn bị, điều kiện ánh sáng, vị trí đầu đo và các lần đo lặp.
Rút dây analog có thể để chân ADC nổi trong miền hợp lệ; kiểm tra miền/hiệu chuẩn không đảm bảo phát hiện mọi trường hợp đứt dây.

## HC-SR501 → LED (tùy chọn)

Chỉ bật ENABLE_PIR_LED sau khi kiểm tra nguồn, GND, OUT và mạch LED thử.
Driver chờ 60 giây từ boot để ổn định; sau đó OUT cao bật LED, OUT thấp liên tục đủ 15 giây tắt LED.
Nếu OUT cao trở lại, bộ đếm 15 giây bắt đầu lại. Trễ chỉnh trên module cộng với thời gian giữ của firmware.
Chức năng hoạt động cả lúc Wi-Fi/MQTT mất kết nối, không theo dõi cá và không thay đổi schema nước.

## Những phần còn phải xác minh

Model board/cổng COM; nguồn/pinout thực tế; giá trị điện trở đang có; hiệu chuẩn PH-4502C/độ đục;
lỗi mất đầu dò, mất mạng, độ ổn định, sai số và thời gian chạy liên tục trên mô hình thật.
Build và test host đạt không thay cho các kết quả này.
