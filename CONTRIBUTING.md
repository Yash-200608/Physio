# Contributing

Thanks for helping improve Physio. Keep the engine **local-only**: no network calls, telemetry, or LLM integrations.

## Development setup

```bash
python -m venv .venv
```

Activate `.venv`, then:

```bash
pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env
```

On macOS / Linux use `cp .env.example .env`.

Run the app from the repository root:

```bash
python src/main.py
```

## Tests

Tests must not open a camera or import `src/main.py` (that module constructs MediaPipe at import time).

```bash
pytest
```

`pytest.ini` adds `src/` to `pythonpath`.

## Pull requests

1. Branch from `main` with a short, descriptive name.
2. Keep changes focused. Prefer small PRs over mixed refactors.
3. Add or update camera-free tests when you change metrics, config, or export logic.
4. Update `CHANGELOG.md` under `[Unreleased]` when the change is user-visible.
5. Fill in `.github/pull_request_template.md` (include a camera check if you touched capture or the HUD).

## Coding notes

- Posture math lives in `src/analytics_enhanced.py`. Prefer 3D world landmarks over 2D image points.
- Configuration belongs in `src/config.py` and `.env.example`. Do not hard-code new thresholds.
- Session CSV/JSON writes go through `src/research_log.py` and `src/clinical_dashboard.py`.
- `src/analytics.py` (`GaitAnalyser`) is unused by the live loop; leave it unwired unless a change is explicitly about gait.
