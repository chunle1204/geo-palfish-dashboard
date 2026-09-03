# GEO PalFish VN — Dashboard theo dõi kiểm tra AI

Dashboard Streamlit đọc **trực tiếp** tab `4a Nhat ky luot chay` của Google Sheet.
Sheet cập nhật → dashboard tự cập nhật (cache 2 phút + nút *Làm mới* + tự refresh).

## Chạy

```bash
cd du-an/geo-dashboard
pip install -r requirements.txt
streamlit run app.py
```

Mở trình duyệt ở địa chỉ Streamlit in ra (mặc định http://localhost:8501).

## Điều kiện

Google Sheet phải cho xem công khai (chỉ cần quyền xem, không cần sửa):

> Sheet → **Chia sẻ** → *Bất kỳ ai có đường liên kết* → **Người xem**

Nếu chưa mở, dashboard sẽ báo lỗi "Google trả về trang HTML (đăng nhập)".

Mặc định đọc sheet `172WzrO4...GeaDBbNY`, tab gid `1347201081`. Đổi nguồn bằng ô
**⚙️ Nguồn dữ liệu → Link Google Sheet** ở sidebar (dán link có `#gid=`).

## Nội dung

| Khu vực | Nội dung |
|---|---|
| Hàng KPI | Tổng số lượt prompt · Trả lời Đúng · Đúng một phần · Sai · Tổng số lỗi |
| Bộ lọc (sidebar) | Mốc · Nền tảng · Nhóm prompt · Loại tài khoản · **Khoảng ngày chạy** · **Lỗi (mã PF)** |
| Tổng quan | Độ chính xác theo nền tảng · tỷ lệ trích palfish.vn · xu hướng theo mốc |
| Theo prompt | Heatmap số lỗi Prompt × Nền tảng · số lỗi theo nhóm prompt |
| Lỗi PF | Tần suất PF-xxx + mức P0/P1/P2 + nền tảng/prompt dính |
| Nguồn | Domain AI hay trích · nguồn thông tin sai hay gặp · % trích palfish.vn theo nền tảng |
| Chi tiết | Bảng lượt chạy + xem 1 lượt (câu trả lời, đoạn có vấn đề, ghi chú, bằng chứng) |
| Báo cáo tuần | Nháp bản cập nhật tuần tự sinh, tải `.md` |

## Ghi chú

- Mức ưu tiên lỗi (P0/P1/P2) khai trong `PF_MUC` ở đầu `app.py` (sheet 4a không có cột này).
- Chỉ tính các dòng có `Prompt ID` dạng `Pxx` và cột *Câu trả lời đầy đủ* có nội dung.
- Deploy được lên Streamlit Community Cloud (miễn phí) trỏ vào cùng repo/sheet.
