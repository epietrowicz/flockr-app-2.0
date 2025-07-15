import cv2
import glob
import os

def find_available_camera():
    """
    Automatically find an available camera device.
    Returns the first working camera device path or None if none found.
    """
    # Try common video device paths
    video_devices = glob.glob("/dev/video*")
    
    if not video_devices:
        print("No video devices found")
        return None
    
    # Sort devices to ensure consistent ordering
    video_devices.sort()
    print(f"Found video devices: {video_devices}")
    
    for device in video_devices:
        try:
            cap = cv2.VideoCapture(device)
            if cap.isOpened():
                # Test if we can actually read a frame
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
    # Check if camera port is set in environment
    camera_port = os.getenv('CAMERA_PORT')
    if camera_port:
        print(f"Using camera port from environment: {camera_port}")
        return camera_port
    print("Getting camera port...")
    # Auto-detect camera
    camera_port = find_available_camera()
    if camera_port:
        return camera_port
    
    # Fallback to default
    print("No camera found, using default /dev/video0")
    return "/dev/video0"