# AquaSense design tokens

## Màu sắc

| Token | Giá trị | Vai trò |
|---|---:|---|
| `--background` | `#0B0F14` | Nền ứng dụng |
| `--background-soft` | `#10161D` | Nền khu vực lồng nhau |
| `--surface` | `#141B23` | Card và input |
| `--surface-elevated` | `#18212B` | Thành phần nổi |
| `--border` | `#283440` | Viền mặc định |
| `--text` | `#EEF2F5` | Chữ chính |
| `--text-secondary` | `#B8C2CB` | Chữ phụ, đạt tương phản AA trên surface |
| `--text-muted` | `#8996A3` | Metadata và nhãn nhỏ |
| `--accent` | `#3B82F6` | Hành động chính, phần tử đang chọn |
| `--success` | `#60A5FA` | Bình thường / online |
| `--warning` | `#D9A84F` | Cảnh báo |
| `--danger` | `#E16D73` | Nguy hiểm |
| `--neutral` | `#84919D` | Offline / không dữ liệu |
| `--temperature` | `#5D9FD6` | Chuỗi nhiệt độ |
| `--ph` | `#9D83CE` | Chuỗi pH |
| `--turbidity` | `#D4A75D` | Chuỗi độ đục tương đối |

## Typography và hình học

| Nhóm | Token / giá trị |
|---|---|
| Font | `Be Vietnam Pro`, fallback `Inter`, `system-ui` |
| Cỡ chữ cơ sở | `14px`, line-height `1.5` |
| Số liệu | `font-variant-numeric: tabular-nums` |
| Spacing | `4, 8, 12, 16, 20, 24, 32px` |
| Radius | `5, 7, 9, 12px` |
| Shadow | Chỉ dùng cho toast; card và panel phẳng |

Màu trạng thái luôn đi cùng chữ hoặc biểu tượng; focus ring dùng accent bán trong suốt và chỉ xuất hiện với điều hướng bàn phím.
