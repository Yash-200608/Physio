import csv
import json
from pathlib import Path

from analytics_enhanced import RESEARCH_CSV_FIELDS
from clinical_dashboard import write_session_summary
from config import Config
from research_log import log_research_row, reset_session_path


def test_log_research_row_writes_csv(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "RESEARCH_EXPORT_DIR", str(tmp_path))
    monkeypatch.setattr(Config, "RESEARCH_LOG_ENABLED", True)
    reset_session_path()
    try:
        log_research_row(
            {
                "t": 1.0,
                "status": "ALIGNED",
                "slouch_score": 0,
                "torso_lean_deg": 0.0,
                "shoulder_tilt_deg": 0.0,
                "hip_tilt_deg": 0.0,
                "left_knee_angle": 180.0,
                "right_knee_angle": 180.0,
            }
        )
        csv_files = list(Path(tmp_path).glob("session_*.csv"))
        assert len(csv_files) == 1
        with csv_files[0].open(newline="", encoding="utf-8") as fp:
            rows = list(csv.DictReader(fp))
        assert list(rows[0].keys()) == list(RESEARCH_CSV_FIELDS)
        assert rows[0]["status"] == "ALIGNED"
        assert rows[0]["slouch_score"] == "0"
    finally:
        reset_session_path()


def test_log_research_row_disabled(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "RESEARCH_EXPORT_DIR", str(tmp_path))
    monkeypatch.setattr(Config, "RESEARCH_LOG_ENABLED", False)
    reset_session_path()
    try:
        log_research_row({"t": 1.0, "status": "ALIGNED"})
        assert list(Path(tmp_path).glob("session_*.csv")) == []
    finally:
        reset_session_path()


def test_write_session_summary(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "RESEARCH_EXPORT_DIR", str(tmp_path))
    path = write_session_summary(
        {
            "session_duration_sec": 12.5,
            "total_frames_analyzed": 40,
            "slouch_ratio_percent": 10.0,
        }
    )
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    assert payload["session_duration_sec"] == 12.5
    assert payload["total_frames_analyzed"] == 40
    assert payload["slouch_ratio_percent"] == 10.0
    assert "written_at" in payload
    assert Path(path).name.startswith("summary_progress_")
