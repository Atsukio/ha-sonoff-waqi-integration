# AGENTS.md

Guidance for AI coding agents working in this repo.

## What this is

**WAQI Station Uploader**: a Home Assistant custom integration (installed via HACS) that reads PM2.5, PM10, temperature and humidity from any HA sensor entities, averages them over an interval and uploads them to the World Air Quality Index data platform (https://aqicn.org/data-feed/upload-api). It is device-agnostic. It was originally built for a SONOFF AirGuard, but nothing in the code or docs should be device-specific.

- GitHub: https://github.com/Atsukio/waqi-station-uploader (owner `Atsukio`, branch `main`)
- Integration domain and folder: `waqi_station_uploader` (was `sonoff_waqi` before v2.0.0)
- Display name: "WAQI Station Uploader" (also set as the top-level `title` in `strings.json` and `translations/en.json`, which is what HA shows in the UI)
- Current version: see `manifest.json` (v2.0.0 renamed the domain, a breaking change for old installs)

## Layout

```
custom_components/waqi_station_uploader/
  __init__.py      setup/unload, options update listener
  config_flow.py   user step + options flow, validates token against WAQI
  const.py         DOMAIN, CONF_* keys, defaults, SPECIES map (config key -> WAQI specie/unit), STATUS_*
  uploader.py      WaqiUploader: state listeners, averaging window, payload build, scheduled upload
  api.py           HTTP calls (token check, upload); WaqiError / WaqiAuthError / WaqiConnectionError
  entity.py        base entity bound to the uploader
  sensor.py        upload status + last upload sensors
  button.py        "Upload now" button
  strings.json     UI strings (keep identical to translations/en.json)
  translations/en.json
  brand/           icon.png, icon@2x.png, logo.png, logo@2x.png (HA 2026.3+ local brand images)
tests/             pytest-homeassistant-custom-component tests
hacs.json          HACS metadata
```

## Conventions and gotchas

- **Keep `strings.json` and `translations/en.json` identical.** Edit both together.
- **Don't change `DOMAIN` again** without a deliberate breaking release: it orphans users' existing config entries, entity IDs and history. Bump the major version if you do.
- **The WAQI token is a secret.** Never log it or put it in entity attributes. Never open or print `.env` files.
- Keep wording device-agnostic in code, docs and UI strings. Don't reintroduce AirGuard/SONOFF references, apart from historical mentions in the git history.
- Temperature in °F or K is converted to °C. Unknown or unavailable states are skipped. If no sensor has data for a window, the upload is skipped.
- Upload interval is 60-3600 s (`MIN_INTERVAL` / `MAX_INTERVAL`). Station ID is immutable after setup.
- Match the surrounding code style: `from __future__ import annotations`, `Final` constants, type hints, short docstrings.
- Git on Windows prints LF/CRLF warnings. They're harmless.

## Running tests

Tests use `pytest-homeassistant-custom-component` (not installed globally):

```bash
python -m venv venv
./venv/bin/pip install pytest-homeassistant-custom-component   # Windows: venv\Scripts\pip
./venv/bin/python -m pytest
```

`pytest.ini` sets `asyncio_mode = auto`. `venv/` is gitignored. Run the tests after any change to the code or config flow; the earlier renames were not test-verified in this environment.

## Release process

1. Bump `"version"` in `custom_components/waqi_station_uploader/manifest.json` (semver; major for breaking changes).
2. Commit and push to `main`.
3. Tag `vX.Y.Z` (annotated) and push the tag. HACS uses tags and releases.
4. Create the GitHub release with notes. The `gh` CLI may not be installed, in which case use the web UI.

Only commit or push when the user asks.

## Possible follow-ups

- Run the test suite and confirm it passes after the v2.0.0 rename.
- Add a GitHub release for `v2.0.0` with the migration notes (remove the old entry and the old `sonoff_waqi` folder, then re-add).
- Consider adding other WAQI species if the upload API supports them.
