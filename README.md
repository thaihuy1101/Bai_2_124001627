# Bài Thực Hành 2: Đọc Video / Webcam và Xoay Khung Hình 90 Độ

Chương trình xử lý hình ảnh và video sử dụng **Python** và **OpenCV**.

---

## 📌 Tính năng chính

- **Giao diện khởi đầu (Menu trực quan)**:
  - Cho phép lựa chọn giữa **Webcam laptop** hoặc **File video (.mp4, .avi, .mkv...)**.
  - Hỗ trợ thao tác bằng **click chuột** (hiệu ứng hover) hoặc phím tắt **[1]** / **[2]**.
  - Tích hợp hộp thoại chọn file video chuẩn của Windows.
- **Xoay video thời gian thực (Real-time Rotation)**:
  - Nhấn phím **`A`** / **`a`**: Quay ngược chiều kim đồng hồ 90° (-90°).
  - Nhấn phím **`D`** / **`d`**: Quay thuận chiều kim đồng hồ 90° (+90°).
  - Nhấn phím **`M`** / **`m`**: Quay trở lại màn hình Menu khởi đầu để đổi nguồn video/webcam.
  - Nhấn phím **`Q`** / phím **`ESC`**: Thoát chương trình.
- **Hiển thị thông tin (OSD - On-Screen Display)**:
  - Hiển thị góc quay hiện tại và hướng dẫn phím bấm trực tiếp trên khung hình.
- **Tự động lặp lại video**: Nếu phát từ file video, khi hết file sẽ tự động phát lại từ đầu.

---

## 🛠️ Cài đặt & Hướng dẫn sử dụng

### 1. Cài đặt thư viện cần thiết
```bash
pip install -r requirements.txt
```

### 2. Khởi chạy chương trình
- **Cách 1**: Chạy trực tiếp script chính:
  ```bash
  python main.py
  ```
- **Cách 2**: Chạy nhanh bằng cách nhấp đúp vào file `run.bat` trên Windows.
- **Cách 3 (tùy chọn)**: Truyền trực tiếp đường dẫn file video qua dòng lệnh:
  ```bash
  python main.py "duong_dan_video.mp4"
  ```
