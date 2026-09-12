# Getting started

Run the engine from the repository root after installing dependencies and copying `.env.example` to `.env`. See the README for venv commands.

```bash
python src/main.py
```

## Camera

`CAMERA_URL` is either a numeric OpenCV index or a device/URL string. `0` is the default webcam.

- Try `1` or `2` if the wrong camera opens.
- A path or stream URL is passed through to `cv2.VideoCapture` when the value is not all digits.

Capture is resized to **640×480** in `src/io_services.py` before the display loop reads frames.

## Window and shutdown

- Window title: `Vision Posture Workspace`
- **Esc** quits the OpenCV loop
- **Ctrl+C** also stops the process

On a clean exit the engine:

1. Sets `global_state.is_shutting_down` so the camera thread stops
2. Writes a JSON session summary via `write_session_summary`
3. Destroys OpenCV windows and closes the MediaPipe pose model

If no body is visible, the HUD stays in `SEARCHING` (or `USER OCCLUDED` when the nose landmark is too weak). Stand back so shoulders and hips are in frame.

## Exports

CSV rows (when enabled) and the final JSON summary land under `RESEARCH_EXPORT_DIR` (default `exports/`). Details: [exports.md](exports.md).
