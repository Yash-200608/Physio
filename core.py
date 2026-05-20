import logging
import threading
from typing import Any, Dict, Optional
from config import Config

def setup_logger():
    logger = logging.getLogger("AI_Mobility_Vision")
    logger.setLevel(Config.LOG_LEVEL)
    formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(ch)
    return logger

logger = setup_logger()

class SystemState:
    def __init__(self):
        self._lock = threading.RLock()
        self.is_shutting_down: bool = False
        self.latest_frame = None
        self._last_posture_metrics: Optional[Dict[str, Any]] = None

    def set_posture_metrics(self, metrics: Optional[Dict[str, Any]]):
        with self._lock:
            self._last_posture_metrics = dict(metrics) if metrics else None

    def get_posture_metrics(self) -> Optional[Dict[str, Any]]:
        with self._lock:
            return dict(self._last_posture_metrics) if self._last_posture_metrics else None

    def get_frame(self):
        with self._lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None

    def set_frame(self, frame):
        with self._lock:
            self.latest_frame = frame

global_state = SystemState()