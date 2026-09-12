import sys
import time
from pathlib import Path

_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import cv2
import mediapipe as mp

from analytics_enhanced import PostureMonitor, PostureSessionTracker, build_research_frame
from clinical_dashboard import write_session_summary
from config import Config
from core import global_state, logger
from io_services import start_io_services
from research_log import log_research_row

try:
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6)
except Exception:
    mp_pose = None
    pose = None

session_tracker = PostureSessionTracker()
last_research_log_t = 0.0

def render_visual_hud(frame, p_metrics: dict, fps: float):
    h, w = frame.shape[:2]
    status = p_metrics["status"]
    
    # Text Color Settings based on posture state
    if status == "ALIGNED":
        status_color = (0, 255, 0) # Green
    elif status in ["SLOUCHING", "LEANING", "TILTING"]:
        status_color = (0, 165, 255) # Orange
    else:
        status_color = (128, 128, 128) # Grey

    # Top Status Bar
    cv2.putText(frame, "ENGINE: VISION-ONLY POSTURE PROFILE", (10, 30), 0, 0.6, (255, 255, 0), 2)
    cv2.putText(frame, f"POSTURE STATUS: {status}", (10, 60), 0, 0.6, status_color, 2)
    cv2.putText(frame, f"FPS: {int(fps)}", (w - 100, 30), 0, 0.6, (200, 200, 200), 2)

    # Technical Metric Sub-panels (Bottom Overlay)
    cv2.putText(frame, f"Slouch Score: {p_metrics['slouch_score']}/100", (10, h - 110), 0, 0.5, (200, 220, 200), 1)
    cv2.putText(
        frame,
        f"Lean Axis: {p_metrics['torso_lean_deg']:.1f}deg | Shoulder Tilt: {p_metrics['shoulder_tilt_deg']:.1f}deg | Hip Tilt: {p_metrics['hip_tilt_deg']:.1f}deg",
        (10, h - 80), 0, 0.5, (180, 210, 220), 1
    )
    cv2.putText(
        frame,
        f"Knee Extensions -> Left: {p_metrics['left_knee_angle']:.1f}deg | Right: {p_metrics['right_knee_angle']:.1f}deg",
        (10, h - 50), 0, 0.5, (180, 200, 180), 1
    )
    
    # Visible Screen Warning Banner if alignment drops
    if status in ["SLOUCHING", "LEANING", "TILTING"]:
        cv2.rectangle(frame, (0, h - 30), (w, h), (0, 0, 255), cv2.FILLED)
        cv2.putText(frame, f"POSTURE WARNING: {status} DETECTED", (int(w/2) - 150, h - 10), 0, 0.5, (255, 255, 255), 2)

    return frame

def main():
    global last_research_log_t

    logger.info("Starting Vision-Only Posture Assessment Engine...")
    start_io_services()

    prev_time, fps = time.time(), 0.0

    try:
        while True:
            time.sleep(0.005)
            frame = global_state.get_frame()

            if frame is None:
                continue

            posture_data = PostureMonitor._empty_alignment("SEARCHING")

            if pose:
                try:
                    res = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    
                    if res.pose_landmarks and res.pose_world_landmarks:
                        # Draw structural lines onto frame using traditional screen space
                        mp.solutions.drawing_utils.draw_landmarks(
                            frame, res.pose_landmarks, mp_pose.POSE_CONNECTIONS
                        )

                        # Evaluate body transformations using metric 3D points
                        posture_data = PostureMonitor.alignment_metrics(res.pose_landmarks, res.pose_world_landmarks)
                        global_state.set_posture_metrics(posture_data)
                        
                        session_tracker.log_frame(posture_data["status"])

                        # Handle local disk log intervals
                        now = time.time()
                        if now - last_research_log_t >= Config.RESEARCH_LOG_INTERVAL_SEC:
                            row = build_research_frame(posture_data)
                            log_research_row(row)
                            last_research_log_t = now
                    else:
                        if res.pose_landmarks:
                            l_sh_vis = res.pose_landmarks.landmark[11].visibility
                            r_sh_vis = res.pose_landmarks.landmark[12].visibility
                            print(f"[DEBUG] Pose found! Shoulder Vis -> Left: {l_sh_vis:.2f}, Right: {r_sh_vis:.2f}")
                        else:
                            print("[DEBUG] MediaPipe Pose detected absolutely zero body shapes in this frame.")
                        global_state.set_posture_metrics(None)
                except Exception as e:
                    logger.warning(f"MediaPipe step breakdown: {e}")
                    global_state.set_posture_metrics(None)
            else:
                global_state.set_posture_metrics(None)

            # Refresh graphics pipeline
            curr = time.time()
            if curr - prev_time > 0.01:
                fps = 0.9 * fps + 0.1 * (1 / (curr - prev_time))
            prev_time = curr

            frame = render_visual_hud(frame, posture_data, fps)
            cv2.imshow("Vision Posture Workspace", frame)

            if cv2.waitKey(1) == 27:
                break
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Executing video pipeline termination cleanup...")
        global_state.is_shutting_down = True
        try:
            sp = write_session_summary(session_tracker.get_summary())
            logger.info(f"Session metrics summary filed: {sp}")
        except Exception as e:
            logger.warning(f"File drop failure: {e}")
        cv2.destroyAllWindows()
        if pose:
            pose.close()

if __name__ == "__main__":
    main()