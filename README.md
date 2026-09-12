# Physio

Local, vision-only posture monitor. A fixed camera feeds OpenCV frames into MediaPipe Pose; scale-invariant 3D world landmarks drive slouch, lean, and tilt scores. There is no audio, no networking, and no LLM.

This project is a research and training aid. It is **not a medical device** and must not be used to diagnose, treat, or monitor a clinical condition.

## Features

- Live HUD: `ALIGNED`, `SLOUCHING`, `LEANING`, `TILTING` (plus search / occlusion states)
- Slouch score, torso lean, shoulder/hip tilt, and left/right knee extension
- Optional CSV research log and a JSON session summary on exit
- Runs entirely on-device; frames and metrics stay on disk you control

## Quick start

Requires Python 3.10+ and a working camera.

```bash
python -m venv .venv
```

Activate the environment:

- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- macOS / Linux: `source .venv/bin/activate`

```bash
pip install -r requirements.txt
copy .env.example .env
```

On macOS / Linux use `cp .env.example .env` instead of `copy`.

```bash
python src/main.py
```

Press **Esc** to quit. On exit the engine writes a session summary JSON under `exports/` (see [docs/exports.md](docs/exports.md)).

More camera and threshold detail: [docs/getting-started.md](docs/getting-started.md) and [docs/configuration.md](docs/configuration.md).

## Repository layout

| Path | Role |
| --- | --- |
| [`src/`](src/) | Application modules |
| [`tests/`](tests/) | Camera-free unit tests |
| [`docs/`](docs/) | Getting started, configuration, export format |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Runtime model and data flow |

## Documentation

- [Architecture](ARCHITECTURE.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Changelog](CHANGELOG.md)
- [License](LICENSE) (MIT)
