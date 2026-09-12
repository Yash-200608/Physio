# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses semantic versioning aligned with the engine version in `ARCHITECTURE.md`.

## [Unreleased]

### Added

- Open-source scaffolding: `README`, `LICENSE` (MIT), `CONTRIBUTING`, `SECURITY`, `CHANGELOG`, and `.env.example`
- `src/`, `tests/`, and `docs/` layout
- Camera-free unit tests and GitHub Actions CI
- Issue and pull-request templates

## [3.0.0] - 2026-09-12

### Added

- Vision-only posture engine: OpenCV capture, MediaPipe Pose, scale-invariant 3D metrics
- HUD statuses: `ALIGNED`, `SLOUCHING`, `LEANING`, `TILTING`
- Interval CSV research log and JSON session summary on shutdown
