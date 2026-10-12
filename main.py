import sys
import os
import ctypes
from ctypes import wintypes
import cv2
import numpy as np

# ==============================================================================
# HÀM HỖ TRỢ ĐỌC/GHI FILE VÀ ĐƯỜNG DẪN UNICODE TRÊN WINDOWS
# ==============================================================================
def get_short_path(path):
    """Chuyển đổi đường dẫn sang dạng 8.3 short path để OpenCV tránh lỗi đường dẫn tiếng Việt (như 'Máy tính')."""
    try:
        buf = ctypes.create_unicode_buffer(1024)
        res = ctypes.windll.kernel32.GetShortPathNameW(path, buf, 1024)
        return buf.value if res > 0 else path
    except Exception:
        return path

def cv2_imread(filename, flags=cv2.IMREAD_COLOR):
    """Đọc ảnh an toàn kể cả khi đường dẫn có dấu tiếng Việt."""
    try:
        data = np.fromfile(filename, dtype=np.uint8)
        return cv2.imdecode(data, flags)
    except Exception:
        return cv2.imread(filename, flags)

def cv2_imwrite(filename, img):
    """Lưu ảnh an toàn kể cả khi đường dẫn có dấu tiếng Việt."""
    try:
        ext = os.path.splitext(filename)[1]
        if not ext:
            ext = ".png"
            filename += ext
        ret, buf = cv2.imencode(ext, img)
        if ret:
            buf.tofile(filename)
            return True
        return False
    except Exception:
        return cv2.imwrite(filename, img)

# ==============================================================================
# HỘP THOẠI CHỌN FILE CHUẨN WINDOWS (Không cần cài thêm thư viện)
# ==============================================================================
class OPENFILENAME(ctypes.Structure):
    _fields_ = [
        ("lStructSize", wintypes.DWORD),
        ("hwndOwner", wintypes.HWND),
        ("hInstance", wintypes.HINSTANCE),
        ("lpstrFilter", wintypes.LPCWSTR),
        ("lpstrCustomFilter", wintypes.LPWSTR),
        ("nMaxCustFilter", wintypes.DWORD),
        ("nFilterIndex", wintypes.DWORD),
        ("lpstrFile", wintypes.LPWSTR),
        ("nMaxFile", wintypes.DWORD),
        ("lpstrFileTitle", wintypes.LPWSTR),
        ("nMaxFileTitle", wintypes.DWORD),
        ("lpstrInitialDir", wintypes.LPCWSTR),
        ("lpstrTitle", wintypes.LPCWSTR),
        ("Flags", wintypes.DWORD),
        ("nFileOffset", wintypes.WORD),
        ("nFileExtension", wintypes.WORD),
        ("lpstrDefExt", wintypes.LPCWSTR),
        ("lCustData", wintypes.LPARAM),
        ("lpfnHook", ctypes.c_void_p),
        ("lpTemplateName", wintypes.LPCWSTR),
        ("pvReserved", ctypes.c_void_p),
        ("dwReserved", wintypes.DWORD),
        ("FlagsEx", wintypes.DWORD)
    ]

def open_file_dialog(file_filter=None, title="Chon file"):
    """Mở hộp thoại chọn file của Windows."""
    if file_filter is None:
        file_filter = "All Files (*.*)\0*.*\0\0"
    ofn = OPENFILENAME()
    ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
    buffer = ctypes.create_unicode_buffer(1024)
    ofn.lpstrFile = ctypes.cast(buffer, wintypes.LPWSTR)
    ofn.nMaxFile = 1024
    ofn.lpstrFilter = file_filter
    ofn.lpstrTitle = title
    ofn.Flags = 0x00080000 | 0x00001000  # OFN_EXPLORER | OFN_FILEMUSTEXIST
    if ctypes.windll.comdlg32.GetOpenFileNameW(ctypes.byref(ofn)):
        return buffer.value
    return None

# ==============================================================================
# BÀI 2: ĐỌC VIDEO / WEBCAM VÀ XOAY 90 ĐỘ (PHÍM A, D)
# ==============================================================================
def choose_video_source():
    """Menu chọn nguồn cho Bài 2: Webcam hoặc File video."""
    win = "Bai 2 - Chon Nguon Phat"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)

    btn1 = (60, 100, 540, 170)
    btn2 = (60, 190, 540, 260)
    state = {"hover": 0, "choice": None}

    def on_mouse(event, x, y, flags, param):
        if btn1[0] <= x <= btn1[2] and btn1[1] <= y <= btn1[3]:
            state["hover"] = 1
        elif btn2[0] <= x <= btn2[2] and btn2[1] <= y <= btn2[3]:
            state["hover"] = 2
        else:
            state["hover"] = 0

        if event == cv2.EVENT_LBUTTONDOWN:
            if state["hover"] == 1:
                state["choice"] = "webcam"
            elif state["hover"] == 2:
                state["choice"] = "file"

    cv2.setMouseCallback(win, on_mouse)

    while True:
        canvas = np.zeros((320, 600, 3), dtype=np.uint8)
        canvas[:] = (35, 35, 42)

        cv2.putText(canvas, "BAI 2: CHON NGUON VIDEO", (140, 50),
                    cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 220, 255), 1, cv2.LINE_AA)

        # Nút 1: Webcam
        bg1 = (60, 90, 45) if state["hover"] == 1 else (45, 60, 35)
        border1 = (0, 255, 120) if state["hover"] == 1 else (70, 120, 60)
        cv2.rectangle(canvas, (btn1[0], btn1[1]), (btn1[2], btn1[3]), bg1, -1)
        cv2.rectangle(canvas, (btn1[0], btn1[1]), (btn1[2], btn1[3]), border1, 2)
        cv2.putText(canvas, "[ 1 ] WEBCAM LAPTOP", (btn1[0] + 30, btn1[1] + 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 2, cv2.LINE_AA)

        # Nút 2: File Video
        bg2 = (80, 55, 45) if state["hover"] == 2 else (55, 45, 35)
        border2 = (0, 180, 255) if state["hover"] == 2 else (120, 80, 60)
        cv2.rectangle(canvas, (btn2[0], btn2[1]), (btn2[2], btn2[3]), bg2, -1)
        cv2.rectangle(canvas, (btn2[0], btn2[1]), (btn2[2], btn2[3]), border2, 2)
        cv2.putText(canvas, "[ 2 ] CHON FILE VIDEO (MP4, AVI...)", (btn2[0] + 30, btn2[1] + 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 2, cv2.LINE_AA)

        cv2.putText(canvas, "Nhan [1] / [2] de chon  |  [ESC] Quay lai", (140, 295),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1, cv2.LINE_AA)

        cv2.imshow(win, canvas)
        key = cv2.waitKey(20) & 0xFF

        if key == ord('1'):
            state["choice"] = "webcam"
        elif key == ord('2'):
            state["choice"] = "file"
        elif key == 27 or key == ord('q'):
            cv2.destroyWindow(win)
            return None, None

        if state["choice"] == "webcam":
            cv2.destroyWindow(win)
            return 0, "Webcam Laptop"
        elif state["choice"] == "file":
            cv2.destroyWindow(win)
            flt = "Video Files (*.mp4;*.avi;*.mkv;*.mov)\0*.mp4;*.avi;*.mkv;*.mov\0All Files (*.*)\0*.*\0\0"
            path = open_file_dialog(flt, "Chon file video")
            if path:
                return path, f"File: {os.path.basename(path)}"
            return None, None

def run_bai_2():
    """Thực thi Bài 2: Đọc video/webcam và xoay 90 độ theo phím A, D."""
    source, source_label = choose_video_source()
    if source is None:
        return

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"[LỖI] Không thể mở nguồn: {source_label}")
        return

    is_file = isinstance(source, str) and not str(source).isdigit()
    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = int(1000 / fps) if (is_file and fps > 0) else 1
    delay = max(1, delay)

    angle = 0
    win = "Bai 2 - Doc Video & Xoay 90 do"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)

    print("\n--- BÀI 2: ĐANG CHẠY ---")
    print(f"Nguồn: {source_label}")
    print(" - Phím A: Quay ngược chiều kim đồng hồ 90°")
    print(" - Phím D: Quay theo chiều kim đồng hồ 90°")
    print(" - Phím M: Quay về Menu chính")
    print(" - Phím Q / ESC: Đóng bài tập\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            if is_file:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            else:
                break

        # Xoay khung hình theo góc
        if angle == 90:
            rotated = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            rotated = cv2.rotate(frame, cv2.ROTATE_180)
        elif angle == 270:
            rotated = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            rotated = frame

        display = rotated.copy()
        h, w = display.shape[:2]

        # Thanh tiêu đề OSD
        overlay = display.copy()
        cv2.rectangle(overlay, (0, 0), (w, 42), (15, 15, 20), -1)
        cv2.addWeighted(overlay, 0.75, display, 0.25, 0, display)

        info = f"Goc: {angle} do | [A]: Quay trai (-90) | [D]: Quay phai (+90) | [M]: Menu | [Q]: Thoat"
        cv2.putText(display, info, (12, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 200), 1, cv2.LINE_AA)

        cv2.imshow(win, display)
        key = cv2.waitKey(delay) & 0xFF

        if key == ord('q') or key == ord('Q') or key == 27:
            break
        elif key == ord('m') or key == ord('M'):
            break
        elif key == ord('a') or key == ord('A'):
            angle = (angle - 90) % 360
            print(f"[BÀI 2] Nhấn A -> Góc quay: {angle}°")
        elif key == ord('d') or key == ord('D'):
            angle = (angle + 90) % 360
            print(f"[BÀI 2] Nhấn D -> Góc quay: {angle}°")

    cap.release()
    cv2.destroyWindow(win)

# ==============================================================================
# BÀI 3: ĐỌC WEBCAM, NHẬN DIỆN KHUÔN MẶT, VẼ HỘP XANH GREEN, ĐẾM & LƯU PHÍM S
# ==============================================================================
def run_bai_3():
    """
    Thực thi Bài 3:
    - Đọc webcam.
    - Nhận diện khuôn mặt, vẽ hình chữ nhật màu xanh Green quanh khuôn mặt.
    - Đếm số khuôn mặt có trong hình.
    - Nhấn phím S: lưu các khuôn mặt ra các file 0.png, 1.png, 2.png...
    """
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    short_cascade_path = get_short_path(cascade_path)
    face_cascade = cv2.CascadeClassifier(short_cascade_path)

    if face_cascade.empty():
        print("[LỖI] Không thể nạp mô hình Haar Cascade nhận diện khuôn mặt!")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[LỖI] Không thể mở webcam laptop!")
        return

    win = "Bai 3 - Nhan Dien Khuon Mat & Luu Phim S"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)

    saved_message_counter = 0
    saved_info_text = ""

    print("\n--- BÀI 3: ĐANG CHẠY ---")
    print(" - Đang nhận diện khuôn mặt từ Webcam laptop...")
    print(" - Nhấn 'S' / 's': Lưu các khuôn mặt hiện tại ra file 0.png, 1.png, ...")
    print(" - Nhấn 'M' / 'm': Quay về Menu chính")
    print(" - Nhấn 'Q' / ESC: Thoát\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[THÔNG BÁO] Không nhận được tín hiệu từ webcam.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.15,
            minNeighbors=5,
            minSize=(35, 35)
        )

        display = frame.copy()
        face_count = len(faces)

        # Vẽ hình chữ nhật màu XANH GREEN (0, 255, 0) quanh từng khuôn mặt
        for i, (x, y, w, h) in enumerate(faces):
            cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                display,
                f"Face #{i}",
                (x, max(15, y - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

        # Vẽ thanh thông tin OSD trên cùng
        h_f, w_f = display.shape[:2]
        overlay = display.copy()
        cv2.rectangle(overlay, (0, 0), (w_f, 45), (15, 15, 20), -1)
        cv2.addWeighted(overlay, 0.75, display, 0.25, 0, display)

        info = f"So khuon mat: {face_count}  |  Nhan [S] de luu anh  |  [M]: Menu  |  [Q]: Thoat"
        cv2.putText(display, info, (15, 29), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)

        # Hiển thị thông báo khi vừa nhấn S lưu ảnh
        if saved_message_counter > 0:
            cv2.putText(
                display,
                saved_info_text,
                (15, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
            saved_message_counter -= 1

        cv2.imshow(win, display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == ord('Q') or key == 27:
            break
        elif key == ord('m') or key == ord('M'):
            break
        # Nhấn phím S: Lưu các khuôn mặt ra 0.png, 1.png, 2.png...
        elif key == ord('s') or key == ord('S'):
            if face_count == 0:
                saved_info_text = "Khong phat hien khuon mat nao de luu!"
                saved_message_counter = 45
                print(f"[BÀI 3] {saved_info_text}")
            else:
                saved_list = []
                for i, (x, y, w, h) in enumerate(faces):
                    # Thêm chút viền lề nhỏ nếu có thể
                    pad_y = int(0.1 * h)
                    pad_x = int(0.1 * w)
                    y1 = max(0, y - pad_y)
                    y2 = min(h_f, y + h + pad_y)
                    x1 = max(0, x - pad_x)
                    x2 = min(w_f, x + w + pad_x)

                    face_crop = frame[y1:y2, x1:x2]
                    out_name = f"{i}.png"
                    cv2_imwrite(out_name, face_crop)
                    saved_list.append(out_name)

                saved_info_text = f"DA LUU {face_count} KHUON MAT: " + ", ".join(saved_list)
                saved_message_counter = 60
                print(f"[BÀI 3 THÀNH CÔNG] {saved_info_text}")

    cap.release()
    cv2.destroyWindow(win)

# ==============================================================================
# BÀI 4: ĐẾM VÀ IN RA SỐ BÓNG TRONG HÌNH
# ==============================================================================
def run_bai_4():
    """
    Thực thi Bài 4:
    - Đọc ảnh quả bóng (mặc định dùng ảnh mẫu sample_balloons.png hoặc mở file khác).
    - Sử dụng thuật toán Distance Transform & Watershed để phân tách chính xác các quả bóng dính nhau.
    - Đánh số và đếm số lượng bóng, in ra màn hình.
    """
    sample_path = "sample_balloons.png"
    img_path = sample_path

    if not os.path.exists(img_path):
        flt = "Image Files (*.png;*.jpg;*.jpeg;*.bmp)\0*.png;*.jpg;*.jpeg;*.bmp\0All Files (*.*)\0*.*\0\0"
        img_path = open_file_dialog(flt, "Chon anh bong bay (Bai 4)")
        if not img_path:
            return

    img = cv2_imread(img_path)
    if img is None:
        print(f"[LỖI] Không thể đọc ảnh: {img_path}")
        return

    # Phân đoạn và đếm bóng bay
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    sure_bg = cv2.dilate(opening, kernel, iterations=3)

    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist_transform, 0.4 * dist_transform.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)

    unknown = cv2.subtract(sure_bg, sure_fg)

    _, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0

    markers = cv2.watershed(img.copy(), markers)

    # Lấy danh sách nhãn các quả bóng (bỏ nhãn 1 là nền và -1 là đường biên)
    labels = [l for l in np.unique(markers) if l > 1]
    balloon_count = len(labels)

    result_img = img.copy()

    # Tìm tâm của từng quả bóng và đánh số thứ tự
    for idx, label in enumerate(labels, 1):
        mask = (markers == label).astype(np.uint8)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts:
            # Vẽ đường viền quanh quả bóng
            cv2.drawContours(result_img, cnts, -1, (0, 255, 0), 2)
            # Tính trọng tâm để ghi số
            M = cv2.moments(cnts[0])
            if M["m00"] > 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                x, y, w, h = cv2.boundingRect(cnts[0])
                cX, cY = x + w // 2, y + h // 2

            # Vẽ vòng tròn tâm và số thứ tự
            cv2.circle(result_img, (cX, cY), 12, (255, 255, 255), -1)
            cv2.circle(result_img, (cX, cY), 12, (0, 0, 0), 1)
            cv2.putText(
                result_img,
                str(idx),
                (cX - 7 if idx >= 10 else cX - 4, cY + 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 0, 0),
                2,
                cv2.LINE_AA,
            )

    print("\n--- BÀI 4: KẾT QUẢ ---")
    print(f"Tổng số bóng đếm được trong hình: {balloon_count} quả bóng.")
    print(" - Nhấn 'S' / 's': Lưu ảnh kết quả (balloons_result.png)")
    print(" - Nhấn 'O' / 'o': Mở file ảnh bóng bay khác từ máy tính")
    print(" - Nhấn 'M' / ESC: Quay lại Menu chính\n")

    win = "Bai 4 - Dem So Bong Trong Hinh"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)

    h_r, w_r = result_img.shape[:2]
    # Tạo banner hiển thị kết quả
    banner = np.zeros((70, w_r, 3), dtype=np.uint8)
    banner[:] = (25, 25, 30)
    cv2.putText(
        banner,
        f"KET QUA: DEM DUOC {balloon_count} QUA BONG TRONG HINH",
        (15, 30),
        cv2.FONT_HERSHEY_DUPLEX,
        0.55,
        (0, 255, 255),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        banner,
        "[S]: Luu ket qua  |  [O]: Chon anh khac  |  [M] hoac [ESC]: Menu",
        (15, 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.42,
        (180, 180, 180),
        1,
        cv2.LINE_AA,
    )

    combined = np.vstack([banner, result_img])

    while True:
        cv2.imshow(win, combined)
        key = cv2.waitKey(0) & 0xFF

        if key == ord('s') or key == ord('S'):
            cv2_imwrite("balloons_result.png", combined)
            print("[BÀI 4] Đã lưu ảnh kết quả vào file 'balloons_result.png'!")
        elif key == ord('o') or key == ord('O'):
            cv2.destroyWindow(win)
            flt = "Image Files (*.png;*.jpg;*.jpeg;*.bmp)\0*.png;*.jpg;*.jpeg;*.bmp\0All Files (*.*)\0*.*\0\0"
            new_path = open_file_dialog(flt, "Chon anh bong bay khac")
            if new_path:
                run_bai_4_custom(new_path)
            return
        elif key == ord('m') or key == ord('M') or key == 27 or key == ord('q'):
            break

    cv2.destroyWindow(win)

def run_bai_4_custom(custom_path):
    """Xử lý bài 4 với ảnh tùy chọn."""
    if not os.path.exists(custom_path):
        return
    img = cv2_imread(custom_path)
    if img is None:
        return
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    sure_bg = cv2.dilate(opening, kernel, iterations=3)
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist_transform, 0.4 * dist_transform.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)
    _, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0
    markers = cv2.watershed(img.copy(), markers)
    labels = [l for l in np.unique(markers) if l > 1]
    balloon_count = len(labels)
    result_img = img.copy()

    for idx, label in enumerate(labels, 1):
        mask = (markers == label).astype(np.uint8)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if cnts:
            cv2.drawContours(result_img, cnts, -1, (0, 255, 0), 2)
            M = cv2.moments(cnts[0])
            if M["m00"] > 0:
                cX, cY = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
            else:
                x, y, w, h = cv2.boundingRect(cnts[0])
                cX, cY = x + w // 2, y + h // 2
            cv2.circle(result_img, (cX, cY), 12, (255, 255, 255), -1)
            cv2.circle(result_img, (cX, cY), 12, (0, 0, 0), 1)
            cv2.putText(result_img, str(idx), (cX - 4, cY + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 2)

    win = "Bai 4 - Ket Qua Anh Moi"
    banner = np.zeros((65, result_img.shape[1], 3), dtype=np.uint8)
    banner[:] = (25, 25, 30)
    cv2.putText(banner, f"DEM DUOC {balloon_count} QUA BONG  |  [S]: Luu  |  [ESC]: Dong", (15, 38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1, cv2.LINE_AA)
    combined = np.vstack([banner, result_img])
    cv2.imshow(win, combined)
    k = cv2.waitKey(0) & 0xFF
    if k == ord('s') or k == ord('S'):
        cv2_imwrite("balloons_result.png", combined)
    cv2.destroyWindow(win)

# ==============================================================================
# BÀI 5: ĐỌC ẢNH BIỂN SỐ XE VÀ CROP CÁC CHỮ SỐ LƯU RA FILE ẢNH
# ==============================================================================
def run_bai_5():
    """
    Thực thi Bài 5:
    - Đọc ảnh biển số xe (mặc định sample_plate.png hoặc chọn file khác).
    - Tách ngưỡng và tìm contour từng chữ số/ký tự trên biển.
    - Sắp xếp từ trái qua phải.
    - Crop từng chữ số ra file ảnh (char_0.png, char_1.png, ...) và lưu vào thư mục 'cropped_characters/'.
    - Hiển thị kết quả trực quan trên màn hình.
    """
    sample_path = "sample_plate.png"
    img_path = sample_path

    if not os.path.exists(img_path):
        flt = "Image Files (*.png;*.jpg;*.jpeg;*.bmp)\0*.png;*.jpg;*.jpeg;*.bmp\0All Files (*.*)\0*.*\0\0"
        img_path = open_file_dialog(flt, "Chon anh bien so xe (Bai 5)")
        if not img_path:
            return

    img = cv2_imread(img_path)
    if img is None:
        print(f"[LỖI] Không thể đọc ảnh: {img_path}")
        return

    # Tiền xử lý ảnh
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Ngưỡng nhị phân Otsu (chữ đen thành trắng 255, nền trắng thành đen 0)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Tìm contours các ký tự
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    h_img, w_img = img.shape[:2]
    chars = []

    # Lọc các contour phù hợp với kích thước chữ số trên biển
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # Chiều cao ký tự thường chiếm từ 30% đến 90% chiều cao biển số
        if (0.3 * h_img < h < 0.9 * h_img) and (10 < w < 0.4 * w_img):
            chars.append((x, y, w, h))

    # Sắp xếp các ký tự từ trái sang phải theo tọa độ x
    chars.sort(key=lambda c: c[0])

    # Tạo thư mục lưu kết quả crop
    out_dir = "cropped_characters"
    os.makedirs(out_dir, exist_ok=True)

    result_plate = img.copy()
    cropped_images = []
    saved_files = []

    for i, (x, y, w, h) in enumerate(chars):
        # Mở rộng lề crop nhẹ
        pad = 2
        y1 = max(0, y - pad)
        y2 = min(h_img, y + h + pad)
        x1 = max(0, x - pad)
        x2 = min(w_img, x + w + pad)

        char_crop = img[y1:y2, x1:x2]
        file_name = os.path.join(out_dir, f"char_{i}.png")
        cv2_imwrite(file_name, char_crop)
        saved_files.append(file_name)
        # Đồng thời lưu ra thư mục gốc f"digit_{i}.png" để tiện nộp bài
        cv2_imwrite(f"digit_{i}.png", char_crop)

        # Vẽ bounding box quanh chữ số trên biển số xe
        cv2.rectangle(result_plate, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(
            result_plate,
            str(i),
            (x + 2, y - 6),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 0, 0),
            2,
            cv2.LINE_AA,
        )

        # Chuẩn bị ảnh crop để hiển thị xem trước (resize cùng chiều cao 100px)
        aspect = w / float(h)
        new_w = max(10, int(100 * aspect))
        resized_char = cv2.resize(char_crop, (new_w, 100))
        # Thêm viền trắng bao quanh cho đẹp
        bordered_char = cv2.copyMakeBorder(resized_char, 10, 25, 10, 10, cv2.BORDER_CONSTANT, value=[240, 240, 240])
        cv2.putText(
            bordered_char,
            f"#{i}",
            (12, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )
        cropped_images.append(bordered_char)

    print("\n--- BÀI 5: KẾT QUẢ ---")
    print(f"Đã phát hiện và crop thành công {len(chars)} chữ số/ký tự trên biển số!")
    print(f"Các file đã lưu vào thư mục '{out_dir}/' và các file digit_0.png, digit_1.png... ở thư mục gốc.")
    print(" - Nhấn 'O' / 'o': Chọn ảnh biển số xe khác")
    print(" - Nhấn 'M' / ESC: Quay lại Menu chính\n")

    # Ghép dải ảnh các chữ số đã crop
    if cropped_images:
        strip_crops = np.hstack(cropped_images)
    else:
        strip_crops = np.zeros((135, 300, 3), dtype=np.uint8)

    # Ghép thành 1 khung hình hiển thị hoàn chỉnh
    max_w = max(result_plate.shape[1], strip_crops.shape[1], 650)
    canvas = np.zeros((result_plate.shape[0] + strip_crops.shape[0] + 120, max_w, 3), dtype=np.uint8)
    canvas[:] = (30, 30, 35)

    # Header
    cv2.putText(
        canvas,
        f"BAI 5: DA CROP {len(chars)} CHU SO TREN BIEN SO XE",
        (20, 35),
        cv2.FONT_HERSHEY_DUPLEX,
        0.65,
        (0, 220, 255),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        canvas,
        f"Cac file da luu: digit_0.png ... digit_{len(chars)-1}.png | Nhan [M] hoac [ESC] de ve Menu",
        (20, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (180, 180, 180),
        1,
        cv2.LINE_AA,
    )

    # Đặt ảnh biển số
    canvas[75:75 + result_plate.shape[0], 20:20 + result_plate.shape[1]] = result_plate

    # Tiêu đề phần crop
    y_strip_title = 85 + result_plate.shape[0]
    cv2.putText(
        canvas,
        "CAC CHU SO DA CROP:",
        (20, y_strip_title),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 120),
        2,
        cv2.LINE_AA,
    )

    # Đặt dải ảnh crop
    y_strip = y_strip_title + 10
    canvas[y_strip:y_strip + strip_crops.shape[0], 20:20 + strip_crops.shape[1]] = strip_crops

    win = "Bai 5 - Crop Chu So Tren Bien So Xe"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)

    while True:
        cv2.imshow(win, canvas)
        key = cv2.waitKey(0) & 0xFF
        if key == ord('o') or key == ord('O'):
            cv2.destroyWindow(win)
            flt = "Image Files (*.png;*.jpg;*.jpeg;*.bmp)\0*.png;*.jpg;*.jpeg;*.bmp\0All Files (*.*)\0*.*\0\0"
            new_path = open_file_dialog(flt, "Chon anh bien so xe khac")
            if new_path:
                run_bai_5_custom(new_path)
            return
        elif key == ord('m') or key == ord('M') or key == 27 or key == ord('q'):
            break

    cv2.destroyWindow(win)

def run_bai_5_custom(custom_path):
    """Xử lý bài 5 với ảnh tùy chọn."""
    if not os.path.exists(custom_path):
        return
    img = cv2_imread(custom_path)
    if img is None:
        return
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    h_img, w_img = img.shape[:2]
    chars = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if (0.25 * h_img < h < 0.95 * h_img) and (5 < w < 0.5 * w_img):
            chars.append((x, y, w, h))
    chars.sort(key=lambda c: c[0])

    out_dir = "cropped_characters"
    os.makedirs(out_dir, exist_ok=True)
    res = img.copy()
    for i, (x, y, w, h) in enumerate(chars):
        char_crop = img[y:y+h, x:x+w]
        cv2_imwrite(os.path.join(out_dir, f"custom_char_{i}.png"), char_crop)
        cv2.rectangle(res, (x, y), (x + w, y + h), (0, 0, 255), 2)

    win = "Bai 5 - Bien So Moi"
    cv2.imshow(win, res)
    cv2.waitKey(0)
    cv2.destroyWindow(win)

# ==============================================================================
# GIAO DIỆN KHỞI ĐẦU CHÍNH: BÀI THỰC HÀNH (OPENCV)
# ==============================================================================
def show_master_menu():
    """
    Giao diện khởi đầu tổng hợp:
    1. Bài 2: Đọc video/webcam & xoay 90 độ (phím A, D)
    2. Bài 3: Đọc webcam, nhận diện khuôn mặt, vẽ hộp xanh, đếm & lưu phím S
    3. Bài 4: Đếm và in ra số bóng trong hình
    4. Bài 5: Đọc ảnh biển số xe và crop các chữ số lưu file ảnh
    """
    win = "Bai Thuc Hanh - Thi Giac May Tinh (OpenCV)"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)

    # Tọa độ 4 nút chọn bài
    btn_w = 680
    btn_h = 75
    btn_x = 60

    buttons = [
        {"id": 1, "rect": (btn_x, 110, btn_x + btn_w, 110 + btn_h),
         "title": "[ 1 ]  BAI 2: DOC VIDEO / WEBCAM & XOAY 90 DO",
         "sub": "Xoay video 90 do khi nhan phim A (trai) hoac D (phai). Ho tro Webcam & MP4"},
        {"id": 2, "rect": (btn_x, 205, btn_x + btn_w, 205 + btn_h),
         "title": "[ 2 ]  BAI 3: NHAN DIEN KHUON MAT TU WEBCAM",
         "sub": "Phat hien mat tu Webcam, ve hop xanh Green, dem so mat, nhan S de luu 0.png, 1.png..."},
        {"id": 3, "rect": (btn_x, 300, btn_x + btn_w, 300 + btn_h),
         "title": "[ 3 ]  BAI 4: DEM SO BONG TRONG HINH",
         "sub": "Phan doan va dem chinh xac so qua bong trong hinh (Distance Transform & Watershed)"},
        {"id": 4, "rect": (btn_x, 395, btn_x + btn_w, 395 + btn_h),
         "title": "[ 4 ]  BAI 5: CROP CHU SO TREN BIEN SO XE",
         "sub": "Doc bien so xe, nhan dien va crop tung chu so/ky tu luu thanh cac file anh rieng biet"},
    ]

    state = {"hover": 0, "choice": None}

    def on_mouse(event, x, y, flags, param):
        hovered = 0
        for btn in buttons:
            r = btn["rect"]
            if r[0] <= x <= r[2] and r[1] <= y <= r[3]:
                hovered = btn["id"]
                break
        state["hover"] = hovered

        if event == cv2.EVENT_LBUTTONDOWN and hovered > 0:
            state["choice"] = hovered

    cv2.setMouseCallback(win, on_mouse)

    while True:
        canvas = np.zeros((540, 800, 3), dtype=np.uint8)
        canvas[:] = (28, 28, 34)

        # Header chung cho Bài thực hành
        cv2.rectangle(canvas, (0, 0), (800, 85), (20, 20, 24), -1)
        cv2.putText(
            canvas,
            "BAI THUC HANH - THI GIAC MAY TINH (OPENCV)",
            (110, 42),
            cv2.FONT_HERSHEY_DUPLEX,
            0.75,
            (0, 220, 255),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            canvas,
            "Chon bai thuc hanh can chay (Click chuot hoac bam phim tuong ung):",
            (155, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (170, 170, 170),
            1,
            cv2.LINE_AA,
        )

        # Vẽ 4 nút chức năng
        for btn in buttons:
            bid = btn["id"]
            r = btn["rect"]
            is_hover = (state["hover"] == bid)

            # Màu sắc phân biệt theo bài
            if bid == 1:
                bg = (55, 75, 40) if is_hover else (38, 50, 30)
                border = (0, 255, 120) if is_hover else (60, 100, 50)
                text_col = (0, 255, 160) if is_hover else (235, 235, 235)
            elif bid == 2:
                bg = (40, 70, 75) if is_hover else (30, 48, 52)
                border = (0, 240, 255) if is_hover else (50, 100, 110)
                text_col = (0, 240, 255) if is_hover else (235, 235, 235)
            elif bid == 3:
                bg = (75, 50, 65) if is_hover else (50, 35, 45)
                border = (230, 100, 255) if is_hover else (100, 60, 90)
                text_col = (240, 140, 255) if is_hover else (235, 235, 235)
            else:
                bg = (80, 60, 35) if is_hover else (52, 42, 28)
                border = (0, 180, 255) if is_hover else (110, 85, 50)
                text_col = (0, 200, 255) if is_hover else (235, 235, 235)

            cv2.rectangle(canvas, (r[0], r[1]), (r[2], r[3]), bg, -1)
            cv2.rectangle(canvas, (r[0], r[1]), (r[2], r[3]), border, 2)

            cv2.putText(
                canvas,
                btn["title"],
                (r[0] + 30, r[1] + 33),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                text_col,
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                canvas,
                ">> " + btn["sub"],
                (r[0] + 30, r[1] + 58),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.42,
                (175, 175, 175),
                1,
                cv2.LINE_AA,
            )

        # Footer hướng dẫn
        cv2.putText(
            canvas,
            "Nhan phim [1] - [4] de chon bai  |  Nhan [Q] hoac [ESC] de thoat chuong trinh",
            (135, 505),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (140, 140, 140),
            1,
            cv2.LINE_AA,
        )

        cv2.imshow(win, canvas)
        key = cv2.waitKey(20) & 0xFF

        if key == ord('1'):
            state["choice"] = 1
        elif key == ord('2'):
            state["choice"] = 2
        elif key == ord('3'):
            state["choice"] = 3
        elif key == ord('4'):
            state["choice"] = 4
        elif key == ord('q') or key == ord('Q') or key == 27:
            state["choice"] = "quit"

        if state["choice"]:
            choice = state["choice"]
            cv2.destroyWindow(win)
            return choice

# ==============================================================================
# HÀM CHÍNH ĐIỀU PHỐI (MAIN)
# ==============================================================================
def main():
    while True:
        choice = show_master_menu()
        if choice == "quit" or choice is None:
            print("[THOÁT] Cảm ơn bạn đã sử dụng chương trình!")
            break
        elif choice == 1:
            run_bai_2()
        elif choice == 2:
            run_bai_3()
        elif choice == 3:
            run_bai_4()
        elif choice == 4:
            run_bai_5()

if __name__ == "__main__":
    main()
