# Dashboard giám sát bể nuôi cá

Vue 3, TypeScript, Vite và Axios.

```powershell
npm ci
npm run dev
npm run build
npm test
```

Vite proxy /api và /ws đến backend tại 127.0.0.1:8000.
Docker dùng Nginx để phục vụ production build và proxy backend.

- Thiết bị mặc định: tank-001; chọn bằng ô mã hoặc query device_id.
- Ba ô số đo: nhiệt độ (°C), pH, độ đục tương đối (%), cùng ô trạng thái thiết bị.
- Số đo null hiển thị thiếu dữ liệu/lỗi; không đổi thành 0.
- Lịch sử dùng REST thật, chọn nhiệt độ/pH/độ đục và 1/6/24 giờ.
- Biểu đồ đọc ngưỡng từ backend, ngắt đường ở mẫu null và giới hạn 500 mẫu gần nhất.
- Độ đục là chỉ số tương đối 0–100, không phải NTU. Ngưỡng mặc định phục vụ demo.
- Danh sách cảnh báo có bộ lọc đang xảy ra/gần đây, thời gian bắt đầu/kết thúc.
- WebSocket trigger REST refresh, gộp burst và reconnect; mở lại socket sẽ đồng bộ bù.
- Live là kết nối web; Online/Offline là trạng thái thiết bị. Khi offline vẫn giữ số đo cuối có chú thích.
- Thời gian hiển thị theo giờ Việt Nam.
- Form ghi đủ sáu ngưỡng, kiểm tra miền/thứ tự, giữ bản nhập khi API lỗi; phản hồi thiết bị cũ bị bỏ qua khi chuyển thiết bị.
- Lưu ngưỡng cập nhật đường ngưỡng biểu đồ; luật cảnh báo áp dụng từ mẫu mới tiếp theo.
- Xác nhận cảnh báo ghi acknowledged_at, không đóng cảnh báo đang xảy ra; có xử lý lỗi và thử lại.
- Tuổi mẫu cập nhật mỗi giây dù không có telemetry mới; từ 60 giây hiện Dữ liệu cũ, giờ mẫu vượt 30 giây về tương lai có thông báo riêng.
- Kiểm tra tuổi mẫu ở trình duyệt không tự đổi Online thành Offline và chưa tạo cảnh báo timeout phía server.
- npm test cần Node >=22.6 (strip-types), có tám kiểm thử miền ngưỡng/tuổi mẫu; không thêm thư viện test frontend.
