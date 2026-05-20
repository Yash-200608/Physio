import time
from collections import deque
from typing import Dict, Optional

class GaitAnalyser:
    def __init__(self):
        # We store tuples of (timestamp, relative_y_velocity, z_depth)
        self.l_heel_samples = deque(maxlen=3)   
        self.r_heel_samples = deque(maxlen=3)
        self.l_peak_times = deque(maxlen=10)    
        self.r_peak_times = deque(maxlen=10)    
        self.step_times = deque(maxlen=20)      
        self.last_alert_time = 0.0

    def process_vision(self, landmarks, world_landmarks) -> Dict:
        """
        Processes gait metrics using world_landmarks (coordinates in meters).
        Falls back safely if lower extremities are occluded.
        """
        t = time.time()
        events = []

        if not landmarks or not world_landmarks:
            return self._empty_response("Searching for User...")

        wl = world_landmarks.landmark
        lm = landmarks.landmark

        # Guard check: Ensure lower body visibility to prevent tracking garbage
        # Left Heel: 29, Right Heel: 30
        if lm[29].visibility < 0.75 or lm[30].visibility < 0.75:
            return self._empty_response("Legs Occluded - Stand Back")

        # Base frame of reference: mid-hip in world coordinates
        mid_hip_y = (wl[23].y + wl[24].y) / 2.0

        # Left foot tracking (Relative vertical position in meters)
        l_rel_y = wl[29].y - mid_hip_y
        self.l_heel_samples.append((t, l_rel_y))
        
        if len(self.l_heel_samples) == 3:
            (t0, y0), (t1, y1), (t2, y2) = self.l_heel_samples
            # In MediaPipe, positive Y points downwards. 
            # A heel strike peak occurs when the foot reaches maximum depth relative to hip
            if y1 > y0 and y1 > y2:
                events.append("L_FOOT")
                self.l_peak_times.append(t1)
                self.step_times.append(t1)

        # Right foot tracking
        r_rel_y = wl[30].y - mid_hip_y
        self.r_heel_samples.append((t, r_rel_y))
        
        if len(self.r_heel_samples) == 3:
            (t0, y0), (t1, y1), (t2, y2) = self.r_heel_samples
            if y1 > y0 and y1 > y2:
                events.append("R_FOOT")
                self.r_peak_times.append(t1)
                self.step_times.append(t1)

        # Compute stride durations
        l_avg = 0.0
        if len(self.l_peak_times) >= 2:
            l_diffs = [self.l_peak_times[i] - self.l_peak_times[i-1] for i in range(1, len(self.l_peak_times))]
            l_avg = sum(l_diffs) / len(l_diffs)
            
        r_avg = 0.0
        if len(self.r_peak_times) >= 2:
            r_diffs = [self.r_peak_times[i] - self.r_peak_times[i-1] for i in range(1, len(self.r_peak_times))]
            r_avg = sum(r_diffs) / len(r_diffs)

        # Symmetry calculation
        symmetry = 100
        if l_avg > 0 and r_avg > 0:
            symmetry = int((min(l_avg, r_avg) / max(l_avg, r_avg)) * 100)
        elif l_avg == 0 and r_avg == 0:
            symmetry = 0
        else:
            symmetry = 0

        # Cadence windowed inside last 10 seconds
        recent_steps = [s for s in self.step_times if t - s < 10.0]
        cadence = len(recent_steps) * 6  
        
        if len(recent_steps) >= 2:
            step_interval = (recent_steps[-1] - recent_steps[0]) / (len(recent_steps) - 1)
        else:
            step_interval = 0.0

        return {
            "events": events,
            "symmetry": symmetry,
            "cadence": cadence,
            "step_interval_sec": round(step_interval, 3),
            "left_stride_interval_sec": round(l_avg, 3),
            "right_stride_interval_sec": round(r_avg, 3),
            "pattern": "Active Walking" if cadence > 10 else "Standing/Idle",
        }

    def _empty_response(self, pattern: str) -> Dict:
        return {
            "events": [],
            "pattern": pattern,
            "symmetry": 0,
            "cadence": 0,
            "step_interval_sec": 0.0,
            "left_stride_interval_sec": 0.0,
            "right_stride_interval_sec": 0.0,
        }

    def get_alert(self, metrics: Dict) -> Optional[str]:
        from config import Config
        t = time.time()
        if t - self.last_alert_time < Config.GAIT_ALERT_COOLDOWN:
            return None

        sym = metrics.get("symmetry", 100)
        cad = metrics.get("cadence", 0)
        pattern = metrics.get("pattern", "")

        if "Occluded" in pattern or "Searching" in pattern:
            return None

        if sym < 70 and cad > 0:
            self.last_alert_time = t
            return "Step asymmetry detected. Try to equalize your steps."
        if 0 < cad < 40:
            self.last_alert_time = t
            return "Cadence is low. Keep a steady pace."
            
        return None