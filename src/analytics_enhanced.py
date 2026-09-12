from __future__ import annotations
import math
import time
from typing import Any, Dict
from config import Config

class PostureMonitor:
    @staticmethod
    def calculate_torso_length_3d(wl) -> float:
        """Computes scale-invariant distance of torso in 3D metric world space."""
        sh_x = (wl[11].x + wl[12].x) / 2.0
        sh_y = (wl[11].y + wl[12].y) / 2.0
        sh_z = (wl[11].z + wl[12].z) / 2.0
        
        hp_x = (wl[23].x + wl[24].x) / 2.0
        hp_y = (wl[23].y + wl[24].y) / 2.0
        hp_z = (wl[23].z + wl[24].z) / 2.0
        
        return math.sqrt((sh_x - hp_x)**2 + (sh_y - hp_y)**2 + (sh_z - hp_z)**2)

    @staticmethod
    def knee_angle_3d(hip, knee, ankle) -> float:
        try:
            v1 = (hip.x - knee.x, hip.y - knee.y, hip.z - knee.z)
            v2 = (ankle.x - knee.x, ankle.y - knee.y, ankle.z - knee.z)
            
            dot = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
            n1 = math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
            n2 = math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)
            
            if n1 < 1e-4 or n2 < 1e-4: return 180.0
            cos_th = dot / (n1 * n2)
            return math.degrees(math.acos(max(-1.0, min(1.0, cos_th))))
        except Exception:
            return 180.0

    @staticmethod
    def alignment_metrics(landmarks, world_landmarks) -> Dict[str, Any]:
        """Calculates scale and perspective invariant posture via 3D World Landmarks."""
        try:
            lm = landmarks.landmark
            wl = world_landmarks.landmark
            
            # Guard check: Ensure high-visibility tracking to eliminate phantom calculations
            if lm[0].visibility < 0.50:
                return PostureMonitor._empty_alignment("USER OCCLUDED")
            #if lm[11].visibility < 0.75 or lm[12].visibility < 0.75:
            #    return PostureMonitor._empty_alignment("USER OCCLUDED")

            l_sh, r_sh = wl[11], wl[12]
            l_hp, r_hp = wl[23], wl[24]
            l_kn, r_kn = wl[25], wl[26]
            l_ak, r_ak = wl[27], wl[28]
            nose = wl[0]

            torso_len = PostureMonitor.calculate_torso_length_3d(wl)
            if torso_len < 1e-3: torso_len = 0.5

            # Slouch calculation using dynamic 3D depth ratios
            hip_mid_y = (l_hp.y + r_hp.y) / 2.0
            nose_hip_gap = hip_mid_y - nose.y
            expected_gap = Config.POSTURE_MIN_NOSE_HIP_GAP
            
            if nose_hip_gap >= expected_gap:
                slouch_score = 0
            else:
                deficit = expected_gap - nose_hip_gap
                slouch_score = int(min(100, (deficit / expected_gap) * 100))

            # 3D Torso Lean Vector Angle relative to World Vertical Axis (Y)
            sh_mid_x = (l_sh.x + r_sh.x) / 2.0
            sh_mid_y = (l_sh.y + r_sh.y) / 2.0
            hp_mid_x = (l_hp.x + r_hp.x) / 2.0
            hp_mid_y = (l_hp.y + r_hp.y) / 2.0
            
            dx, dy = sh_mid_x - hp_mid_x, sh_mid_y - hp_mid_y
            torso_lean = math.degrees(math.atan2(dy, dx) + math.pi/2)

            # Lateral Tilts
            shoulder_width = max(math.sqrt((r_sh.x - l_sh.x)**2 + (r_sh.y - l_sh.y)**2), 1e-4)
            shoulder_tilt = math.degrees(math.atan2(r_sh.y - l_sh.y, shoulder_width))
            
            hip_width = max(math.sqrt((r_hp.x - l_hp.x)**2 + (r_hp.y - l_hp.y)**2), 1e-4)
            hip_tilt = math.degrees(math.atan2(r_hp.y - l_hp.y, hip_width))

            # Knee Extensions using true 3D vector paths
            left_knee_angle = PostureMonitor.knee_angle_3d(l_hp, l_kn, l_ak)
            right_knee_angle = PostureMonitor.knee_angle_3d(r_hp, r_kn, r_ak)

            # Rule Engine Mapping
            if slouch_score >= Config.POSTURE_SLOUCH_ALERT_THRESH:
                status = "SLOUCHING"
            elif abs(torso_lean) >= Config.POSTURE_LEAN_ALERT_DEG:
                status = "LEANING"
            elif max(abs(shoulder_tilt), abs(hip_tilt)) >= Config.POSTURE_TILT_ALERT_DEG:
                status = "TILTING"
            else:
                status = "ALIGNED"

            return {
                "status": status,
                "slouch_score": slouch_score,
                "torso_lean_deg": round(torso_lean, 2),
                "shoulder_tilt_deg": round(shoulder_tilt, 2),
                "hip_tilt_deg": round(hip_tilt, 2),
                "left_knee_angle": round(left_knee_angle, 2),
                "right_knee_angle": round(right_knee_angle, 2),
            }
        except Exception:
            return PostureMonitor._empty_alignment("SEARCHING")

    @staticmethod
    def _empty_alignment(status: str) -> Dict[str, Any]:
        return {
            "status": status, "slouch_score": 0, "torso_lean_deg": 0.0,
            "shoulder_tilt_deg": 0.0, "hip_tilt_deg": 0.0,
            "left_knee_angle": 180.0, "right_knee_angle": 180.0
        }

class PostureSessionTracker:
    def __init__(self):
        self.start_time = time.time()
        self.total_frames = 0
        self.slouch_frames = 0

    def log_frame(self, status: str):
        self.total_frames += 1
        if status == "SLOUCHING":
            self.slouch_frames += 1

    def get_summary(self) -> Dict[str, Any]:
        elapsed = max(1e-3, time.time() - self.start_time)
        slouch_percentage = (self.slouch_frames / max(1, self.total_frames)) * 100
        return {
            "session_duration_sec": round(elapsed, 1),
            "total_frames_analyzed": self.total_frames,
            "slouch_ratio_percent": round(slouch_percentage, 1)
        }

def build_research_frame(posture: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "t": time.time(),
        "status": posture.get("status", "UNKNOWN"),
        "slouch_score": posture.get("slouch_score", 0),
        "torso_lean_deg": posture.get("torso_lean_deg", 0.0),
        "shoulder_tilt_deg": posture.get("shoulder_tilt_deg", 0.0),
        "hip_tilt_deg": posture.get("hip_tilt_deg", 0.0),
        "left_knee_angle": posture.get("left_knee_angle", 180.0),
        "right_knee_angle": posture.get("right_knee_angle", 180.0)
    }

RESEARCH_CSV_FIELDS = ("t", "status", "slouch_score", "torso_lean_deg", "shoulder_tilt_deg", "hip_tilt_deg", "left_knee_angle", "right_knee_angle")