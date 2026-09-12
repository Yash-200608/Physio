from types import SimpleNamespace

from analytics_enhanced import (
    PostureMonitor,
    PostureSessionTracker,
    build_research_frame,
)


def _xyz(x, y, z=0.0):
    return SimpleNamespace(x=x, y=y, z=z)


def test_empty_alignment_defaults():
    empty = PostureMonitor._empty_alignment("SEARCHING")
    assert empty["status"] == "SEARCHING"
    assert empty["slouch_score"] == 0
    assert empty["torso_lean_deg"] == 0.0
    assert empty["left_knee_angle"] == 180.0
    assert empty["right_knee_angle"] == 180.0


def test_knee_angle_straight_is_180():
    hip = _xyz(0.0, 1.0, 0.0)
    knee = _xyz(0.0, 0.0, 0.0)
    ankle = _xyz(0.0, -1.0, 0.0)
    assert PostureMonitor.knee_angle_3d(hip, knee, ankle) == 180.0


def test_knee_angle_right_angle_is_90():
    hip = _xyz(1.0, 0.0, 0.0)
    knee = _xyz(0.0, 0.0, 0.0)
    ankle = _xyz(0.0, 1.0, 0.0)
    angle = PostureMonitor.knee_angle_3d(hip, knee, ankle)
    assert abs(angle - 90.0) < 1e-6


def test_knee_angle_degenerate_vectors_fallback():
    p = _xyz(0.0, 0.0, 0.0)
    assert PostureMonitor.knee_angle_3d(p, p, p) == 180.0


def test_session_tracker_slouch_ratio():
    tracker = PostureSessionTracker()
    tracker.log_frame("ALIGNED")
    tracker.log_frame("SLOUCHING")
    tracker.log_frame("LEANING")
    summary = tracker.get_summary()
    assert summary["total_frames_analyzed"] == 3
    assert summary["slouch_ratio_percent"] == 33.3
    assert summary["session_duration_sec"] >= 0.0


def test_build_research_frame_fields():
    posture = {
        "status": "ALIGNED",
        "slouch_score": 4,
        "torso_lean_deg": 1.25,
        "shoulder_tilt_deg": -0.5,
        "hip_tilt_deg": 0.1,
        "left_knee_angle": 170.0,
        "right_knee_angle": 172.0,
    }
    row = build_research_frame(posture)
    assert row["status"] == "ALIGNED"
    assert row["slouch_score"] == 4
    assert row["torso_lean_deg"] == 1.25
    assert "t" in row
