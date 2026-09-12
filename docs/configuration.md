# Configuration

Values are loaded from the environment (and `.env` via `python-dotenv`) in `src/config.py`. Copy `.env.example` and change only what you need.

| Variable | Default | Meaning |
| --- | --- | --- |
| `CAMERA_URL` | `0` | Webcam index if the string is all digits; otherwise an OpenCV capture URL/path |
| `POSTURE_MIN_NOSE_HIP_GAP` | `0.10` | Minimum nose-to-hip vertical gap (world Y) before slouch score rises |
| `POSTURE_SLOUCH_ALERT_THRESH` | `55` | Slouch score (0–100) that sets status `SLOUCHING` |
| `POSTURE_LEAN_ALERT_DEG` | `12` | Absolute torso lean (degrees) that sets status `LEANING` |
| `POSTURE_TILT_ALERT_DEG` | `10` | Absolute shoulder or hip tilt (degrees) that sets status `TILTING` |
| `RESEARCH_LOG_ENABLED` | `true` | Write interval CSV rows (`1` / `true` / `yes` / `on`) |
| `RESEARCH_LOG_INTERVAL_SEC` | `0.5` | Minimum seconds between CSV rows |
| `RESEARCH_EXPORT_DIR` | `exports` | Directory for CSV logs and JSON summaries |

Log level is fixed at `logging.INFO` in `Config.LOG_LEVEL` (not an env var).

Status priority in `PostureMonitor.alignment_metrics`: slouch, then lean, then tilt; otherwise `ALIGNED`.
