import sys
import os
import ctypes
from ctypes import wintypes
import cv2
import numpy as np

# ==============================================================================
# HỘP THOẠI CHỌN FILE VIDEO CHUẨN WINDOWS (Không cần thư viện ngoài)
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

def open_file_dialog():
    """Mở hộp thoại chọn file video chuẩn của Windows (MP4, AVI, MKV, MOV)."""
    ofn = OPENFILENAME()
    ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
    buffer = ctypes.create_unicode_buffer(1024)
    ofn.lpstrFile = ctypes.cast(buffer, wintypes.LPWSTR)
    ofn.nMaxFile = 1024
    ofn.lpstrFilter = (
        "Video Files (*.mp4;*.avi;*.mkv;*.mov)\0*.mp4;*.avi;*.mkv;*.mov\0"
        "All Files (*.*)\0*.*\0\0"
    )
    ofn.lpstrTitle = "Chon file video"
    ofn.Flags = 0x00080000 | 0x00001000  # OFN_EXPLORER | OFN_FILEMUSTEXIST
    if ctypes.windll.comdlg32.GetOpenFileNameW(ctypes.byref(ofn)):
        return buffer.value
    return None

# ==============================================================================
# GIAO DIỆN KHỞI ĐẦU (MENU CHỌN NGUỒN)
# ==============================================================================
def show_start_menu():
    """
    Hiển thị giao diện khởi đầu bằng OpenCV với 2 lựa chọn:
    1. Webcam Laptop
    2. File video MP4
    Hỗ trợ click chuột trực tiếp hoặc bấm phím 1/2 trên bàn phím.
    """
    menu_window = "Khoi Tao Ung Dung - Chon Nguon Video"
    cv2.namedWindow(menu_window, cv2.WINDOW_AUTOSIZE)

    # Tọa độ các nút (x1, y1, x2, y2)
    btn_webcam = (70, 140, 680, 230)
    btn_file = (70, 260, 680, 350)

    state = {
        "hover": 0,         # 0: none, 1: webcam, 2: file
        "selected": None    # 'webcam', 'file', 'quit'
    }

    def on_mouse(event, x, y, flags, param):
        # Kiểm tra di chuột (hover)
        if btn_webcam[0] <= x <= btn_webcam[2] and btn_webcam[1] <= y <= btn_webcam[3]:
            state["hover"] = 1
        elif btn_file[0] <= x <= btn_file[2] and btn_file[1] <= y <= btn_file[3]:
            state["hover"] = 2
        else:
            state["hover"] = 0

        # Kiểm tra click chuột trái
        if event == cv2.EVENT_LBUTTONDOWN:
            if state["hover"] == 1:
                state["selected"] = "webcam"
            elif state["hover"] == 2:
                state["selected"] = "file"

    cv2.setMouseCallback(menu_window, on_mouse)

    while True:
        # Tạo canvas nền tối hiện đại (750 x 440)
        canvas = np.zeros((440, 750, 3), dtype=np.uint8)
        canvas[:] = (30, 30, 36)  # Màu nền xám than sang trọng

        # Header: Tiêu đề chương trình
        cv2.rectangle(canvas, (0, 0), (750, 95), (20, 20, 24), -1)
        cv2.putText(
            canvas,
            "BAI THUC HANH 2: QUAY VIDEO 90 DO",
            (140, 45),
            cv2.FONT_HERSHEY_DUPLEX,
            0.75,
            (0, 220, 255),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            canvas,
            "Vui long chon nguon phat hinh anh ben duoi de bat dau:",
            (160, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (180, 180, 180),
            1,
            cv2.LINE_AA,
        )

        # NÚT 1: WEBCAM LAPTOP
        bg1 = (60, 80, 40) if state["hover"] == 1 else (45, 55, 35)
        border1 = (0, 255, 120) if state["hover"] == 1 else (70, 120, 60)
        cv2.rectangle(canvas, (btn_webcam[0], btn_webcam[1]), (btn_webcam[2], btn_webcam[3]), bg1, -1)
        cv2.rectangle(canvas, (btn_webcam[0], btn_webcam[1]), (btn_webcam[2], btn_webcam[3]), border1, 2)
        cv2.putText(
            canvas,
            "[ 1 ]  SU DUNG WEBCAM LAPTOP",
            (btn_webcam[0] + 40, btn_webcam[1] + 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 255, 150) if state["hover"] == 1 else (230, 230, 230),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            canvas,
            ">> Mo truc tiep camera mac dinh cua may tinh (Nhan phim 1 hoac click vao day)",
            (btn_webcam[0] + 40, btn_webcam[1] + 68),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (180, 200, 180),
            1,
            cv2.LINE_AA,
        )

        # NÚT 2: FILE VIDEO MP4
        bg2 = (80, 50, 40) if state["hover"] == 2 else (55, 40, 35)
        border2 = (0, 165, 255) if state["hover"] == 2 else (120, 80, 60)
        cv2.rectangle(canvas, (btn_file[0], btn_file[1]), (btn_file[2], btn_file[3]), bg2, -1)
        cv2.rectangle(canvas, (btn_file[0], btn_file[1]), (btn_file[2], btn_file[3]), border2, 2)
        cv2.putText(
            canvas,
            "[ 2 ]  CHON FILE VIDEO (MP4, AVI, MKV...)",
            (btn_file[0] + 40, btn_file[1] + 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 200, 255) if state["hover"] == 2 else (230, 230, 230),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            canvas,
            ">> Mo hop thoai de chon file video tu may (Nhan phim 2 hoac click vao day)",
            (btn_file[0] + 40, btn_file[1] + 68),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (180, 180, 200),
            1,
            cv2.LINE_AA,
        )

        # Footer: Hướng dẫn phím tắt
        cv2.putText(
            canvas,
            "Nhan phim [1] / [2] de chon nhanh  |  Nhan [Q] hoac [ESC] de thoat",
            (170, 400),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (140, 140, 140),
            1,
            cv2.LINE_AA,
        )

        cv2.imshow(menu_window, canvas)
        key = cv2.waitKey(20) & 0xFF

        # Kiểm tra phím bấm
        if key == ord('1'):
            state["selected"] = "webcam"
        elif key == ord('2'):
            state["selected"] = "file"
        elif key == ord('q') or key == ord('Q') or key == 27:
            state["selected"] = "quit"

        # Xử lý khi đã có lựa chọn
        if state["selected"] == "webcam":
            cv2.destroyWindow(menu_window)
            return 0, "Webcam Laptop"
        elif state["selected"] == "file":
            cv2.destroyWindow(menu_window)
            selected_path = open_file_dialog()
            if selected_path:
                file_name = os.path.basename(selected_path)
                return selected_path, f"File: {file_name}"
            else:
                # Nếu người dùng hủy chọn file thì mở lại menu
                return show_start_menu()
        elif state["selected"] == "quit":
            cv2.destroyWindow(menu_window)
            return None, None

# ==============================================================================
# MÀN HÌNH CHƠI VIDEO & XOAY KHUNG HÌNH (BÀI 2)
# ==============================================================================
def play_video(source, source_label):
    """
    Đọc và hiển thị luồng video/webcam.
    - Nhấn phím A: Quay ngược chiều kim đồng hồ 90 độ
    - Nhấn phím D: Quay theo chiều kim đồng hồ 90 độ
    - Nhấn phím M: Quay lại Menu chính để đổi nguồn
    - Nhấn phím Q/ESC: Thoát chương trình
    """
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print(f"[LỖI] Không thể mở nguồn: {source_label}")
        return "menu"

    is_file = isinstance(source, str) and not str(source).isdigit()
    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = int(1000 / fps) if (is_file and fps > 0) else 1
    delay = max(1, delay)

    # Góc quay: 0, 90, 180, 270 (tính theo chiều kim đồng hồ)
    angle = 0
    window_name = f"Video Viewer - {source_label}"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    print("==================================================")
    print(f"Đang phát: {source_label}")
    print(" - Nhấn 'A' / 'a': Quay ngược chiều kim đồng hồ 90°")
    print(" - Nhấn 'D' / 'd': Quay theo chiều kim đồng hồ 90°")
    print(" - Nhấn 'M' / 'm': Quay lại Menu khởi đầu")
    print(" - Nhấn 'Q' / ESC: Thoát chương trình")
    print("==================================================")

    while True:
        ret, frame = cap.read()

        if not ret:
            if is_file:
                # Tự động phát lặp lại nếu là file video
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            else:
                print("[THÔNG BÁO] Kết thúc luồng video/webcam.")
                break

        # Xoay khung hình theo góc hiện tại
        if angle == 90:
            rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            rotated_frame = cv2.rotate(frame, cv2.ROTATE_180)
        elif angle == 270:
            rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        else:
            rotated_frame = frame

        # Vẽ thanh thông tin điều khiển OSD lên đầu khung hình
        display_frame = rotated_frame.copy()
        h, w = display_frame.shape[:2]

        # Lớp nền mờ cho thanh thông tin
        overlay = display_frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 42), (15, 15, 20), -1)
        cv2.addWeighted(overlay, 0.75, display_frame, 0.25, 0, display_frame)

        info_text = (
            f"Nguon: {source_label} | Goc: {angle} do | "
            f"[A]: Quay trai (-90) | [D]: Quay phai (+90) | [M]: Menu | [Q]: Thoat"
        )
        cv2.putText(
            display_frame,
            info_text,
            (12, 27),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 255, 180),
            1,
            cv2.LINE_AA,
        )

        cv2.imshow(window_name, display_frame)

        key = cv2.waitKey(delay) & 0xFF

        # Phím thoát: Q hoặc ESC
        if key == ord('q') or key == ord('Q') or key == 27:
            cap.release()
            cv2.destroyWindow(window_name)
            return "quit"
        # Phím M: Quay về Menu
        elif key == ord('m') or key == ord('M'):
            cap.release()
            cv2.destroyWindow(window_name)
            return "menu"
        # Phím A: Quay ngược chiều kim đồng hồ (-90 độ)
        elif key == ord('a') or key == ord('A'):
            angle = (angle - 90) % 360
            print(f"[ĐIỀU KHIỂN] Nhấn A -> Góc quay: {angle}° (quay ngược chiều kim đồng hồ)")
        # Phím D: Quay cùng chiều kim đồng hồ (+90 độ)
        elif key == ord('d') or key == ord('D'):
            angle = (angle + 90) % 360
            print(f"[ĐIỀU KHIỂN] Nhấn D -> Góc quay: {angle}° (quay cùng chiều kim đồng hồ)")

    cap.release()
    cv2.destroyWindow(window_name)
    return "menu"

# ==============================================================================
# HÀM CHÍNH
# ==============================================================================
def main():
    # Nếu người dùng truyền sẵn tham số file video qua dòng lệnh:
    # Ví dụ: python main.py my_video.mp4
    if len(sys.argv) > 1:
        source_arg = sys.argv[1]
        source = int(source_arg) if source_arg.isdigit() else source_arg
        label = "Webcam" if source == 0 else f"File: {os.path.basename(str(source))}"
        play_video(source, label)
        return

    # Mặc định khởi chạy giao diện lựa chọn ban đầu
    while True:
        source, label = show_start_menu()
        if source is None:
            print("[THOÁT] Đã đóng chương trình.")
            break

        result = play_video(source, label)
        if result == "quit":
            break

if __name__ == "__main__":
    main()
