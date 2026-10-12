# BÀI THỰC HÀNH - THỊ GIÁC MÁY TÍNH (OPENCV & PYTHON)

Dự án tích hợp đầy đủ 4 bài thực hành thị giác máy tính với giao diện điều khiển đồ họa trực quan (OpenCV).

---

## 🌟 TỔNG QUAN CÁC BÀI THỰC HÀNH

### 1. BÀI 2: Đọc Video / Webcam & Xoay Khung Hình 90 Độ
- **Nguồn phát**: Tùy chọn mở trực tiếp từ **Webcam laptop** hoặc **File video (.mp4, .avi, ...)** qua hộp thoại Windows.
- **Phím điều khiển**:
  - `A` / `a`: Quay ngược chiều kim đồng hồ 90° (-90°).
  - `D` / `d`: Quay theo chiều kim đồng hồ 90° (+90°).
  - `M` / `m`: Quay lại Menu chính.
  - `Q` / `ESC`: Thoát.
- **Tính năng phụ**: Hiển thị góc quay thời gian thực (OSD); Tự động lặp lại video khi phát hết file.

### 2. BÀI 3: Nhận Diện Khuôn Mặt Từ Webcam & Lưu Ảnh
- **Mô hình**: Sử dụng bộ nhận diện Haar Cascade (`haarcascade_frontalface_default.xml`).
- **Xử lý**:
  - Vẽ hình chữ nhật màu **xanh Green `(0, 255, 0)`** quanh từng khuôn mặt.
  - Tự động đếm và hiển thị số lượng khuôn mặt đang xuất hiện trong khung hình.
- **Phím điều khiển**:
  - `S` / `s`: Lưu các khuôn mặt đang phát hiện ra các file ảnh riêng biệt: `0.png`, `1.png`, `2.png`, ...
  - `M` / `m`: Quay lại Menu chính.
  - `Q` / `ESC`: Thoát.

### 3. BÀI 4: Đếm Và In Ra Số Bóng Trong Hình
- **Thuật toán**: Sử dụng kỹ thuật hình thái học nâng cao (Morphology), **Distance Transform** và giải thuật **Watershed** để phân tách chính xác các quả bóng dính liền nhau.
- **Kết quả**:
  - Đếm chính xác **12 quả bóng** trong hình ảnh mẫu đề bài.
  - Đánh số thứ tự trực tiếp từ 1 đến 12 vào tâm từng quả bóng.
  - Hỗ trợ nhấn `S` để lưu ảnh kết quả (`balloons_result.png`) và nhấn `O` để chọn ảnh bóng bay khác từ máy tính.

### 4. BÀI 5: Đọc Ảnh Biển Số Xe & Crop Chữ Số Lưu Ra File
- **Thuật toán**: Chuyển đổi mức xám, phân ngưỡng nhị phân Otsu, trích xuất đường bao (Contours) và phân đoạn ký tự theo tỷ lệ chuẩn.
- **Kết quả**:
  - Nhận diện và sắp xếp các chữ số/ký tự theo thứ tự từ trái sang phải.
  - Crop từng chữ số lưu ra thư mục `cropped_characters/` (`char_0.png` ... `char_7.png`) và thư mục gốc (`digit_0.png` ... `digit_7.png`).
  - Hiển thị trực quan toàn bộ biển số xe và dải ảnh xem trước các chữ số đã crop.

---

## 🚀 HƯỚNG DẪN CHẠY CHƯƠNG TRÌNH

### Cách 1: Khởi chạy 1-Click
Nhấp đúp chuột vào file **`run.bat`** trên Windows.

### Cách 2: Chạy bằng Terminal
```bash
python main.py
```
*(Hoặc dùng môi trường ảo: `.\.venv\Scripts\python.exe main.py`)*
