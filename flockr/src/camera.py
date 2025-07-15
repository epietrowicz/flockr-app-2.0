import cv2
import glob
import os
import threading
import time

_frame = None
_lock = threading.Lock()
_running = False
_thread = None
_camera_path = None


def find_available_camera():
    """
    Automatically find an available camera device.
    Returns the first working camera device path or None if none found.
    """
    video_devices = glob.glob("/dev/video*")
    if not video_devices:
        print("No video devices found")
        return None

    video_devices.sort()
    print(f"Found video devices: {video_devices}")

    for device in video_devices:
        try:
            cap = cv2.VideoCapture(device)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"Found working camera: {device}")
                    cap.release()
                    return device
                cap.release()
        except Exception as e:
            print(f"Error testing {device}: {e}")
            continue

    print("No working camera found")
    return None


def get_camera_port():
    """
    Get the camera port, either from environment variable or auto-detect.
    """
    global _camera_path
    if _camera_path:
        return _camera_path

    env_port = os.getenv("CAMERA_PORT")
    if env_port:
        print(f"Using camera port from environment: {env_port}")
        _camera_path = env_port
        return env_port

    print("Getting camera port...")
    detected = find_available_camera()
    if detected:
        _camera_path = detected
        return detected

    print("No camera found, using default /dev/video0")
    _camera_path = "/dev/video0"
    return _camera_path


def _reader():
    global _frame, _running
    cam = get_camera_port()
    cap = cv2.VideoCapture(cam)
    if not cap.isOpened():
        print(f"ERROR: Could not open camera at {cam}")
        _running = False
        return

    while _running:
        ret, frame = cap.read()
        if ret:
            with _lock:
                _frame = frame
        time.sleep(0.01)

    cap.release()


def start_camera():
    """
    Starts a background thread that continuously reads frames from the camera.
    """
    global _running, _thread
    if _running:
        return
    _running = True
    _thread = threading.Thread(target=_reader, daemon=True)
    _thread.start()
    print("Camera thread started.")


def get_latest_frame():
    """
    Returns the most recent frame captured by the shared camera thread.
    """
    with _lock:
        return _frame.copy() if _frame is not None else None


def stop_camera():
    """
    Gracefully stops the shared camera thread.
    """
    global _running, _thread
    _running = False
    if _thread:
        _thread.join()
        _thread = None
    print("Camera thread stopped.")
