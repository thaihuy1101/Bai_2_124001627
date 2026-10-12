import sys
import os
import traceback
import ctypes
from ctypes import wintypes
import cv2
import numpy as np

# Cấu hình UTF-8 an toàn cho terminal Windows
if sys.platform.startswith('win'):
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Thư mục chứa script hiện tại
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

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
# GIAO DIỆN CHỌN NGUỒN ẢNH (Ảnh mẫu hoặc Chọn từ máy tính)
# ==============================================================================
def choose_image_source(title_text, sample_desc, file_filter, dialog_title):
    """Hiển thị menu con cho phép chọn: [1] Dùng ảnh mẫu, [2] Chọn ảnh từ máy tính."""
    win = f"{title_text} - Chon Nguon Anh"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)

    btn1 = (60, 95, 540, 165)
    btn2 = (60, 185, 540, 255)
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
                state["choice"] = "sample"
            elif state["hover"] == 2:
                state["choice"] = "custom"

    cv2.setMouseCallback(win, on_mouse)

    while True:
        canvas = np.zeros((320, 600, 3), dtype=np.uint8)
        canvas[:] = (35, 35, 42)

        cv2.putText(canvas, title_text.upper(), (130, 48),
                    cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 220, 255), 1, cv2.LINE_AA)

        # Nút 1: Dùng ảnh mẫu
        bg1 = (60, 90, 45) if state["hover"] == 1 else (45, 60, 35)
        border1 = (0, 255, 120) if state["hover"] == 1 else (70, 120, 60)
        cv2.rectangle(canvas, (btn1[0], btn1[1]), (btn1[2], btn1[3]), bg1, -1)
        cv2.rectangle(canvas, (btn1[0], btn1[1]), (btn1[2], btn1[3]), border1, 2)
        cv2.putText(canvas, "[ 1 ] DUNG ANH MAU DE BAI", (btn1[0] + 25, btn1[1] + 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.62, (240, 240, 240), 2, cv2.LINE_AA)
        cv2.putText(canvas, f">> {sample_desc}", (btn1[0] + 25, btn1[1] + 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 200, 180), 1, cv2.LINE_AA)

        # Nút 2: Chọn từ máy tính
        bg2 = (80, 55, 45) if state["hover"] == 2 else (55, 45, 35)
        border2 = (0, 180, 255) if state["hover"] == 2 else (120, 80, 60)
        cv2.rectangle(canvas, (btn2[0], btn2[1]), (btn2[2], btn2[3]), bg2, -1)
        cv2.rectangle(canvas, (btn2[0], btn2[1]), (btn2[2], btn2[3]), border2, 2)
        cv2.putText(canvas, "[ 2 ] CHON ANH TU MAY TINH...", (btn2[0] + 25, btn2[1] + 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.62, (240, 240, 240), 2, cv2.LINE_AA)
        cv2.putText(canvas, ">> Mo hop thoai de chon bat ky file anh nao", (btn2[0] + 25, btn2[1] + 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 180, 200), 1, cv2.LINE_AA)

        cv2.putText(canvas, "Nhan phim [1] / [2] de chon  |  [ESC] Quay lai", (140, 295),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1, cv2.LINE_AA)

        cv2.imshow(win, canvas)
        key = cv2.waitKey(20) & 0xFF

        if key == ord('1'):
            state["choice"] = "sample"
        elif key == ord('2'):
            state["choice"] = "custom"
        elif key == 27 or key == ord('q'):
            cv2.destroyWindow(win)
            return None

        if state["choice"] == "sample":
            cv2.destroyWindow(win)
            return "sample"
        elif state["choice"] == "custom":
            cv2.destroyWindow(win)
            path = open_file_dialog(file_filter, dialog_title)
            return path

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

        bg1 = (60, 90, 45) if state["hover"] == 1 else (45, 60, 35)
        border1 = (0, 255, 120) if state["hover"] == 1 else (70, 120, 60)
        cv2.rectangle(canvas, (btn1[0], btn1[1]), (btn1[2], btn1[3]), bg1, -1)
        cv2.rectangle(canvas, (btn1[0], btn1[1]), (btn1[2], btn1[3]), border1, 2)
        cv2.putText(canvas, "[ 1 ] WEBCAM LAPTOP", (btn1[0] + 30, btn1[1] + 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (240, 240, 240), 2, cv2.LINE_AA)

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
    try:
        source, source_label = choose_video_source()
        if source is None:
            return

        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print(f"[LOI] Khong the mo nguon: {source_label}")
            return

        is_file = isinstance(source, str) and not str(source).isdigit()
        fps = cap.get(cv2.CAP_PROP_FPS)
        delay = int(1000 / fps) if (is_file and fps > 0) else 1
        delay = max(1, delay)

        angle = 0
        win = "Bai 2 - Doc Video & Xoay 90 do"
        cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)

        print("\n--- BAI 2: DANG CHAY ---")
        print(f"Nguon: {source_label}")
        print(" - Phim A: Quay nguoc chieu kim dong ho 90 do")
        print(" - Phim D: Quay theo chieu kim dong ho 90 do")
        print(" - Phim M: Quay ve Menu chinh")
        print(" - Phim Q / ESC: Dong bai tap\n")

        while True:
            ret, frame = cap.read()
            if not ret:
                if is_file:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    break

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
                print(f"[BAI 2] Nhan A -> Goc quay: {angle} do")
            elif key == ord('d') or key == ord('D'):
                angle = (angle + 90) % 360
                print(f"[BAI 2] Nhan D -> Goc quay: {angle} do")

        cap.release()
        cv2.destroyWindow(win)
    except Exception as e:
        print(f"[LOI BAI 2] {e}")
        traceback.print_exc()

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
    try:
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        short_cascade_path = get_short_path(cascade_path)
        face_cascade = cv2.CascadeClassifier(short_cascade_path)

        if face_cascade.empty():
            print("[LOI] Khong the nap mo hinh Haar Cascade nhan dien khuon mat!")
            return

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[LOI] Khong the mo webcam laptop!")
            return

        win = "Bai 3 - Nhan Dien Khuon Mat & Luu Phim S"
        cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)

        saved_message_counter = 0
        saved_info_text = ""

        print("\n--- BAI 3: DANG CHAY ---")
        print(" - Dang nhan dien khuon mat tu Webcam laptop...")
        print(" - Nhan 'S' / 's': Luu cac khuon mat hien tai ra file 0.png, 1.png, ...")
        print(" - Nhan 'M' / 'm': Quay ve Menu chinh")
        print(" - Nhan 'Q' / ESC: Thoat\n")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("[THONG BAO] Khong nhan duoc tin hieu tu webcam.")
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

            h_f, w_f = display.shape[:2]
            overlay = display.copy()
            cv2.rectangle(overlay, (0, 0), (w_f, 45), (15, 15, 20), -1)
            cv2.addWeighted(overlay, 0.75, display, 0.25, 0, display)

            info = f"So khuon mat: {face_count}  |  Nhan [S] de luu anh  |  [M]: Menu  |  [Q]: Thoat"
            cv2.putText(display, info, (15, 29), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)

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
            elif key == ord('s') or key == ord('S'):
                if face_count == 0:
                    saved_info_text = "Khong phat hien khuon mat nao de luu!"
                    saved_message_counter = 45
                    print(f"[BAI 3] {saved_info_text}")
                else:
                    saved_list = []
                    for i, (x, y, w, h) in enumerate(faces):
                        pad_y = int(0.1 * h)
                        pad_x = int(0.1 * w)
                        y1 = max(0, y - pad_y)
                        y2 = min(h_f, y + h + pad_y)
                        x1 = max(0, x - pad_x)
                        x2 = min(w_f, x + w + pad_x)

                        face_crop = frame[y1:y2, x1:x2]
                        out_name = os.path.join(SCRIPT_DIR, f"{i}.png")
                        cv2_imwrite(out_name, face_crop)
                        saved_list.append(f"{i}.png")

                    saved_info_text = f"DA LUU {face_count} KHUON MAT: " + ", ".join(saved_list)
                    saved_message_counter = 60
                    print(f"[BAI 3 THANH CONG] {saved_info_text}")

        cap.release()
        cv2.destroyWindow(win)
    except Exception as e:
        print(f"[LOI BAI 3] {e}")
        traceback.print_exc()

# ==============================================================================
# BÀI 4: ĐẾM VÀ IN RA SỐ BÓNG TRONG HÌNH
# ==============================================================================
def process_balloons(img_path, title_label="Anh Bong Bay"):
    """Thực hiện đếm bóng bay bằng Watershed & Distance Transform trên file ảnh bất kỳ."""
    img = cv2_imread(img_path)
    if img is None:
        print(f"[LOI] Khong the doc anh: {img_path}")
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
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                x, y, w, h = cv2.boundingRect(cnts[0])
                cX, cY = x + w // 2, y + h // 2

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

    print(f"\n--- BAI 4: KET QUA ({title_label}) ---")
    print(f"Tong so bong dem duoc: {balloon_count} qua bong.")
    print(" - Nhan 'O' / 'o': Chon anh bong bay khac tu may tinh")
    print(" - Nhan 'S' / 's': Luu anh ket qua (balloons_result.png)")
    print(" - Nhan 'M' / ESC: Quay lai Menu chinh\n")

    win = "Bai 4 - Dem So Bong Trong Hinh"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)

    h_r, w_r = result_img.shape[:2]
    banner = np.zeros((70, max(w_r, 450), 3), dtype=np.uint8)
    banner[:] = (25, 25, 30)
    cv2.putText(
        banner,
        f"KET QUA: DEM DUOC {balloon_count} QUA BONG ({title_label})",
        (15, 30),
        cv2.FONT_HERSHEY_DUPLEX,
        0.52,
        (0, 220, 255),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        banner,
        "[O]: CHON ANH KHAC  |  [S]: Luu ket qua  |  [M]: Menu  |  [ESC]: Thoat",
        (15, 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.42,
        (0, 255, 150),
        1,
        cv2.LINE_AA,
    )

    if w_r < banner.shape[1]:
        padded_img = cv2.copyMakeBorder(result_img, 0, 0, 0, banner.shape[1] - w_r, cv2.BORDER_CONSTANT, value=[25, 25, 30])
        combined = np.vstack([banner, padded_img])
    else:
        combined = np.vstack([banner, result_img])

    while True:
        cv2.imshow(win, combined)
        key = cv2.waitKey(0) & 0xFF

        # Phím O: Chọn ảnh bóng bay khác từ máy tính
        if key == ord('o') or key == ord('O'):
            cv2.destroyWindow(win)
            flt = "Image Files (*.png;*.jpg;*.jpeg;*.bmp)\0*.png;*.jpg;*.jpeg;*.bmp\0All Files (*.*)\0*.*\0\0"
            new_path = open_file_dialog(flt, "Chon anh bong bay khac")
            if new_path:
                process_balloons(new_path, os.path.basename(new_path))
            return
        elif key == ord('s') or key == ord('S'):
            out_path = os.path.join(SCRIPT_DIR, "balloons_result.png")
            cv2_imwrite(out_path, combined)
            print(f"[BAI 4] Da luu anh ket qua vao file '{out_path}'!")
        elif key == ord('m') or key == ord('M') or key == 27 or key == ord('q'):
            break

    cv2.destroyWindow(win)

def run_bai_4():
    """Menu chọn nguồn cho Bài 4: Ảnh mẫu đề bài hoặc Chọn ảnh từ máy tính."""
    try:
        sample_path = os.path.join(SCRIPT_DIR, "sample_balloons.png")
        flt = "Image Files (*.png;*.jpg;*.jpeg;*.bmp)\0*.png;*.jpg;*.jpeg;*.bmp\0All Files (*.*)\0*.*\0\0"
        
        choice = choose_image_source(
            "Bai 4: Dem So Bong Trong Hinh",
            "Anh mau de bai (12 qua bong dính nhau)",
            flt,
            "Chon file anh bong bay (Bai 4)"
        )
        
        if choice is None:
            return
        elif choice == "sample":
            process_balloons(sample_path, "Anh mau de bai")
        else:
            process_balloons(choice, os.path.basename(choice))
    except Exception as e:
        print(f"[LOI BAI 4] {e}")
        traceback.print_exc()

# ==============================================================================
# BÀI 5: ĐỌC ẢNH BIỂN SỐ XE VÀ CROP CÁC CHỮ SỐ LƯU RA FILE ẢNH
# ==============================================================================
def process_license_plate(img_path, title_label="Bien So Xe"):
    """Thực hiện phát hiện và crop các chữ số trên biển số xe bất kỳ."""
    img = cv2_imread(img_path)
    if img is None:
        print(f"[LOI] Khong the doc anh: {img_path}")
        return

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    h_img, w_img = img.shape[:2]
    chars = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if (0.25 * h_img < h < 0.95 * h_img) and (5 < w < 0.45 * w_img):
            chars.append((x, y, w, h))

    chars.sort(key=lambda c: c[0])

    out_dir = os.path.join(SCRIPT_DIR, "cropped_characters")
    os.makedirs(out_dir, exist_ok=True)

    result_plate = img.copy()
    cropped_images = []
    saved_files = []

    for i, (x, y, w, h) in enumerate(chars):
        pad = 2
        y1 = max(0, y - pad)
        y2 = min(h_img, y + h + pad)
        x1 = max(0, x - pad)
        x2 = min(w_img, x + w + pad)

        char_crop = img[y1:y2, x1:x2]
        file_name = os.path.join(out_dir, f"char_{i}.png")
        cv2_imwrite(file_name, char_crop)
        saved_files.append(file_name)
        
        # Lưu file digit_i.png ngay thư mục gốc
        cv2_imwrite(os.path.join(SCRIPT_DIR, f"digit_{i}.png"), char_crop)

        cv2.rectangle(result_plate, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(
            result_plate,
            str(i),
            (x + 2, max(15, y - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 0, 0),
            2,
            cv2.LINE_AA,
        )

        aspect = w / float(h) if h > 0 else 0.5
        new_w = max(10, int(100 * aspect))
        resized_char = cv2.resize(char_crop, (new_w, 100))
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

    print(f"\n--- BAI 5: KET QUA ({title_label}) ---")
    print(f"Da phat hien va crop thanh cong {len(chars)} chu so/ky tu tren bien so!")
    print(f"Cac file da luu vao thu muc '{out_dir}/' va cac file digit_0.png, digit_1.png... o thu muc goc.")
    print(" - Nhan 'O' / 'o': Chon anh bien so xe khac tu may tinh")
    print(" - Nhan 'M' / ESC: Quay lai Menu chinh\n")

    if cropped_images:
        strip_crops = np.hstack(cropped_images)
    else:
        strip_crops = np.zeros((135, 300, 3), dtype=np.uint8)

    margin = 25
    max_content_w = max(result_plate.shape[1], strip_crops.shape[1])
    canvas_w = max(max_content_w + 2 * margin, 720)
    canvas_h = 75 + result_plate.shape[0] + 50 + strip_crops.shape[0] + 35

    canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
    canvas[:] = (30, 30, 35)

    # Header
    cv2.putText(
        canvas,
        f"BAI 5: DA CROP {len(chars)} CHU SO TREN BIEN SO ({title_label})",
        (20, 32),
        cv2.FONT_HERSHEY_DUPLEX,
        0.58,
        (0, 220, 255),
        1,
        cv2.LINE_AA,
    )
    cv2.putText(
        canvas,
        "[O]: CHON ANH KHAC  |  Cac file: digit_0..png  |  [M]: Menu  |  [ESC]: Thoat",
        (20, 58),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.43,
        (0, 255, 150),
        1,
        cv2.LINE_AA,
    )

    y_p = 80
    canvas[y_p : y_p + result_plate.shape[0], margin : margin + result_plate.shape[1]] = result_plate

    y_strip_title = y_p + result_plate.shape[0] + 35
    cv2.putText(
        canvas,
        "CAC CHU SO DA CROP:",
        (margin, y_strip_title),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 120),
        2,
        cv2.LINE_AA,
    )

    y_strip = y_strip_title + 10
    canvas[y_strip : y_strip + strip_crops.shape[0], margin : margin + strip_crops.shape[1]] = strip_crops

    win = "Bai 5 - Crop Chu So Tren Bien So Xe"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)

    while True:
        cv2.imshow(win, canvas)
        key = cv2.waitKey(0) & 0xFF

        # Phím O: Chọn ảnh biển số xe khác từ máy tính
        if key == ord('o') or key == ord('O'):
            cv2.destroyWindow(win)
            flt = "Image Files (*.png;*.jpg;*.jpeg;*.bmp)\0*.png;*.jpg;*.jpeg;*.bmp\0All Files (*.*)\0*.*\0\0"
            new_path = open_file_dialog(flt, "Chon anh bien so xe khac")
            if new_path:
                process_license_plate(new_path, os.path.basename(new_path))
            return
        elif key == ord('m') or key == ord('M') or key == 27 or key == ord('q'):
            break

    cv2.destroyWindow(win)

def run_bai_5():
    """Menu chọn nguồn cho Bài 5: Ảnh mẫu đề bài hoặc Chọn ảnh từ máy tính."""
    try:
        sample_path = os.path.join(SCRIPT_DIR, "sample_plate.png")
        flt = "Image Files (*.png;*.jpg;*.jpeg;*.bmp)\0*.png;*.jpg;*.jpeg;*.bmp\0All Files (*.*)\0*.*\0\0"

        choice = choose_image_source(
            "Bai 5: Crop Chu So Bien So Xe",
            "Anh mau de bai (Bien so 75A-145.19)",
            flt,
            "Chon file anh bien so xe (Bai 5)"
        )

        if choice is None:
            return
        elif choice == "sample":
            process_license_plate(sample_path, "Anh mau 75A-145.19")
        else:
            process_license_plate(choice, os.path.basename(choice))
    except Exception as e:
        print(f"[LOI BAI 5] {e}")
        traceback.print_exc()

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
         "sub": "Phan doan va dem chinh xac so qua bong trong hinh. Ho tro anh mau & chon anh tu may"},
        {"id": 4, "rect": (btn_x, 395, btn_x + btn_w, 395 + btn_h),
         "title": "[ 4 ]  BAI 5: CROP CHU SO TREN BIEN SO XE",
         "sub": "Doc bien so xe, crop tung chu so/ky tu luu ra file. Ho tro anh mau & chon anh tu may"},
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

        for btn in buttons:
            bid = btn["id"]
            r = btn["rect"]
            is_hover = (state["hover"] == bid)

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
            print("[THOAT] Cam on ban da su dung chuong trinh!")
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
