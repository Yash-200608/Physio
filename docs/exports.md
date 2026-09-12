# Research exports

All files are written locally under `RESEARCH_EXPORT_DIR` (default `exports/`). CSV and JSON products are gitignored (`exports/*.csv`, `exports/*.json`). The directory itself is kept in git via `exports/.gitkeep`.

## Interval CSV

When `RESEARCH_LOG_ENABLED` is on, `src/research_log.py` appends rows every `RESEARCH_LOG_INTERVAL_SEC` seconds while a pose is tracked.

Filename: `session_YYYYMMDD_HHMMSS.csv` (one path per process; reset with `reset_session_path()`).

Columns (`RESEARCH_CSV_FIELDS`):

| Field | Source |
| --- | --- |
| `t` | Unix timestamp |
| `status` | Alignment status string |
| `slouch_score` | 0–100 |
| `torso_lean_deg` | Torso lean vs world vertical |
| `shoulder_tilt_deg` | Lateral shoulder tilt |
| `hip_tilt_deg` | Lateral hip tilt |
| `left_knee_angle` | 3D hip–knee–ankle angle |
| `right_knee_angle` | 3D hip–knee–ankle angle |

## Session JSON

On shutdown, `src/clinical_dashboard.py` writes `summary_progress_YYYYMMDD_HHMMSS.json`:

```json
{
  "written_at": 0.0,
  "session_duration_sec": 0.0,
  "total_frames_analyzed": 0,
  "slouch_ratio_percent": 0.0
}
```

`slouch_ratio_percent` is the share of analyzed frames whose status was `SLOUCHING`.
