import logging
import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        pass

load_dotenv()

class Config:
    # Camera Configuration
    _CAMERA_URL = os.getenv("CAMERA_URL", "0")
    CAMERA_URL = int(_CAMERA_URL) if _CAMERA_URL.isdigit() else _CAMERA_URL
    LOG_LEVEL: int = logging.INFO

    # Vision-Only Posture Thresholds (Scale-Invariant)
    POSTURE_MIN_NOSE_HIP_GAP: float = float(os.getenv("POSTURE_MIN_NOSE_HIP_GAP", "0.10"))
    POSTURE_SLOUCH_ALERT_THRESH: int = int(os.getenv("POSTURE_SLOUCH_ALERT_THRESH", "55"))
    POSTURE_LEAN_ALERT_DEG: float = float(os.getenv("POSTURE_LEAN_ALERT_DEG", "12"))
    POSTURE_TILT_ALERT_DEG: float = float(os.getenv("POSTURE_TILT_ALERT_DEG", "10"))

    # Research & Export Logistics
    RESEARCH_LOG_ENABLED: bool = os.getenv("RESEARCH_LOG_ENABLED", "true").lower() in ("1", "true", "yes", "on")
    RESEARCH_LOG_INTERVAL_SEC: float = float(os.getenv("RESEARCH_LOG_INTERVAL_SEC", "0.5"))
    RESEARCH_EXPORT_DIR: str = os.getenv("RESEARCH_EXPORT_DIR", "exports")