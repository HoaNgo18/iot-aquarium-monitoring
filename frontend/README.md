# Frontend

Vue 3 + TypeScript + Vite cho dashboard giám sát ngập.

## Chạy local

```powershell
npm install
npm run dev
```

Backend cần chạy tại `http://127.0.0.1:8000`. Vite chuyển tiếp `/api` và `/ws` tới backend để tránh cấu hình CORS riêng cho môi trường phát triển.

## Kiểm tra và build

```powershell
npm run type-check
npm run build
```

## Chạy bằng Docker Compose

```powershell
docker compose up -d --build frontend
```

Mở `http://localhost:5173`. Nginx chuyển tiếp `/api/` và `/ws` tới backend trong mạng Compose.

## Dữ liệu trên dashboard

Dashboard tải số đo gần nhất và trạng thái của `node-001` khi mở trang. Có thể nhập mã thiết bị khác hoặc dùng URL `http://localhost:5173/?device_id=node-001`. Nút **Cập nhật** đọc lại dữ liệu; hiện chưa tự cập nhật qua WebSocket.

- Hiển thị mực nước (cm), lượng mưa theo chu kỳ (mm), thời gian lấy mẫu theo giờ Việt Nam, online/offline, trạng thái cảm biến và RSSI của mẫu gần nhất.
- Thời gian lấy mẫu hiển thị tương đối; hover để xem giờ tuyệt đối. Nhãn tương đối cập nhật khi tải lại dữ liệu.
- Khi offline, giao diện vẫn hiển thị số đo đã lưu và ghi rõ trạng thái offline.
- Khi cảm biến lỗi và mực nước là `null`, giao diện hiển thị `-- cm` cùng nguyên nhân.
- Xử lý riêng trạng thái đang tải, thiết bị chưa tồn tại, chưa có telemetry và API lỗi; có thể thử lại bằng nút **Cập nhật**.
- Biểu đồ lịch sử và danh sách cảnh báo đang là trạng thái trống; đường ngưỡng nét đứt chỉ minh họa, chưa lấy ngưỡng thật từ backend.

`src/api/monitoring.ts` quản lý Axios client; `src/composables/useReadings.ts` quản lý yêu cầu và hủy yêu cầu cũ khi đổi thiết bị. `views/` ghép bố cục; `components/` chỉ nhận dữ liệu để hiển thị.
