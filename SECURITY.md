# Security policy

Physio is a **local** computer-vision tool. It reads a camera you configure, computes posture metrics on-device, and may write CSV/JSON files under `RESEARCH_EXPORT_DIR` (default `exports/`). It does not send frames, landmarks, or metrics to a remote service.

## What this project does not do

- No cloud API, telemetry, or analytics beacons
- No authentication or multi-user accounts
- No LLM or third-party inference endpoint

Treat camera footage and `exports/` as **sensitive personal data**. Do not commit `.env` or export files. Keep the working tree on a machine you trust.

## Supported versions

Security fixes are accepted against the latest `main` branch.

## Reporting a vulnerability

Please use [GitHub private vulnerability reporting](https://github.com/Yash-200608/Physio/security/advisories/new) for this repository.

Include:

- A description of the issue and impact (for example: unexpected file writes, path traversal in export paths, unsafe handling of `CAMERA_URL`)
- Steps to reproduce
- Affected commit or release, if known

Do not open a public issue for exploitable bugs. We will acknowledge reports through the advisory and coordinate a fix before any disclosure.
