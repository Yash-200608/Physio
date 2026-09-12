import time
import threading
import cv2
from config import Config
from core import global_state, logger

def camera_thread():
    cap = cv2.VideoCapture(Config.CAMERA_URL)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    logger.info(f"Camera thread initialized pointing to: {Config.CAMERA_URL}")
    
    while not global_state.is_shutting_down:
        try:
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (640, 480))
                global_state.set_frame(frame)
            else:
                time.sleep(0.05)
                cap.release()
                cap = cv2.VideoCapture(Config.CAMERA_URL)
        except Exception as e:
            logger.error(f"Camera error: {e}")
            time.sleep(1.0)
            
    cap.release()
    logger.info("Camera thread shut down gracefully.")

def start_io_services():
    threading.Thread(target=camera_thread, daemon=True).start()