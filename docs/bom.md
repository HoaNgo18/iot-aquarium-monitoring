# Phần cứng cho hệ thống giám sát bể nuôi cá

> Cập nhật 21/10/2026. Người thực hiện xác nhận đã đặt bốn loại cảm biến, dự kiến vài ngày nữa nhận; chưa xác nhận đã nhận hàng.

## Linh kiện đã có theo người thực hiện

ESP32, breadboard, dây nối và điện trở. Chưa xác nhận chính xác phiên bản board hoặc giá trị điện trở.

## Cảm biến đã đặt cho MVP

| Linh kiện | SL | Khi chốt hàng |
| --- | --- | --- |
| Bộ pH PH-4502C | 1 bộ | Người thực hiện xác nhận model; ảnh đầu dò BNC/mạch hai biến trở; chờ kiểm tra pinout/output thật |
| Bộ cảm biến độ đục chưa rõ mã | 1 bộ | Ảnh đầu đo + mạch đỏ ba chân + dây; chờ xác nhận ngõ analog/digital, phần được ngâm và điện áp output |
| DS18B20 đầu dò chống nước, ba dây | 1 | Kiểm tra pinout thực tế và điện trở kéo lên |

Phần mềm dùng ph, temperature_c và turbidity_pct, chưa phụ thuộc model ADC cụ thể.
Độ đục 0–100 là chỉ số tương đối cần xác lập bằng hiệu chuẩn, chưa công bố NTU.

## Vật tư phụ trợ

- Dung dịch đệm pH theo tài liệu bộ cảm biến; dung dịch bảo quản phù hợp đầu dò.
- Nước cất, cốc riêng cho mẫu và buffer; nhiệt kế tham chiếu.
- Đồng hồ vạn năng để đo output trước khi nối ESP32.
- Cáp USB có dữ liệu, nguồn phù hợp, hộp mạch khô và gá đầu dò.
- Mạch chia áp/đệm tùy điện áp analog thực tế; đối chiếu điện trở đã có.

## Mở rộng phát hiện người bật LED

PIR HC-SR501 (1), LED và mạch điều khiển theo công suất đèn thực tế.
HC-SR501 đã được người thực hiện xác nhận đặt cùng ba cảm biến nước; LED/mạch điều khiển chưa xác nhận đã mua.
PIR quan sát người bên ngoài bể, không theo dõi cá.
Chưa là đầu việc chặn MVP.

Khi nhận hàng, bổ sung model, link mua, ngày nhận, giao tiếp/nguồn/output và ảnh pinout.
Nguồn trạng thái đã đặt là xác nhận trực tiếp ngày 21/10; chưa gán trạng thái đã nhận hoặc đã kiểm thử.
Hướng dẫn cấu hình theo linh kiện đã đặt: [hardware-bringup.md](hardware-bringup.md).
