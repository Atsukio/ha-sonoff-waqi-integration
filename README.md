# WAQI Station Uploader

Home Assistant custom integration that takes readings from any PM2.5, PM10, temperature and humidity sensor entities (developed with a SONOFF AirGuard SAWF-07P paired locally via Matter) and uploads them to the [World Air Quality Index data platform](https://aqicn.org/data-feed/upload-api) on a schedule.

## How it works

1. The AirGuard is a Matter-over-Wi-Fi device, so Home Assistant's built-in **Matter** integration talks to it locally and creates PM2.5, PM10, temperature and humidity sensor entities.
2. This integration listens to those entities. Each time they change during the upload window, it records the new value.
3. At every interval (60 s by default), it averages the window and `POST`s it to `https://aqicn.org/sensor/upload/`. The upload includes `min`, `max`, `median` and `stddev` when the window has more than one sample, plus `averaging` set to the interval in seconds.

Temperature in °F or K is converted to °C. If a sensor is `unknown` or `unavailable` for the whole window, its reading is left out. If no sensor has data, the upload is skipped.

## Requirements

- Home Assistant 2024.11 or newer.
- The AirGuard added to Home Assistant via the Matter integration (Settings → Devices & services → Add integration → Matter, then add the device with its Matter pairing code). Third-party Matter use needs the AirGuard's Matter pairing code; if it was set up in eWeLink first, share it to Home Assistant from there.
- A WAQI token from <https://aqicn.org/data-platform/token/>.

## Installation

### HACS (custom repository)

[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Atsukio&repository=waqi-station-uploader&category=integration)

Or add it manually:

1. In Home Assistant, open **HACS** → the three-dot menu (top right) → **Custom repositories**.
2. Paste `https://github.com/Atsukio/waqi-station-uploader`, set the type to **Integration**, and click **Add**.
3. Find **WAQI Station Uploader** in HACS, click **Download**, then restart Home Assistant.

### Manual

 copy `custom_components/sonoff_waqi` into your Home Assistant `config/custom_components/` folder and restart.

## Setup

Settings → Devices & services → Add integration → **WAQI Station Uploader**.

| Field | Notes |
|---|---|
| Station ID | Private, unique ID on WAQI. Can't be changed later. |
| WAQI token | Validated against the WAQI API on save. |
| Station name | Public name on the WAQI map. |
| Latitude / Longitude | Defaults to your Home Assistant location. Enter both or neither. |
| PM2.5 sensor | Required. |
| PM10 / Temperature / Humidity | Optional. |
| Upload interval | 60–3600 s. Default 60 s, which WAQI recommends. |

Everything except the station ID can be changed later under **Configure**.

After the first successful upload, verify and publish the station at <https://aqicn.org/data-feed/verification/>.

## Entities

| Entity | Description |
|---|---|
| `sensor.waqi_uploader_<name>_upload_status` | `pending` / `ok` / `error` / `skipped`. Attributes: `last_error`, `last_readings`, `last_attempt`, `interval_seconds`. |
| `sensor.waqi_uploader_<name>_last_upload` | Timestamp of the last successful upload. |
| `button.waqi_uploader_<name>_upload_now` | Uploads the current window immediately. |

Example alert:

```yaml
automation:
  - alias: WAQI upload failing
    triggers:
      - trigger: state
        entity_id: sensor.waqi_uploader_sonoff_airguard_upload_status
        to: error
        for: "00:10:00"
    actions:
      - action: notify.notify
        data:
          message: >
            WAQI upload failing: {{ state_attr(trigger.entity_id, 'last_error') }}
```

## Debug logging

```yaml
logger:
  logs:
    custom_components.sonoff_waqi: debug
```

The token is never logged or exposed in entity attributes.

## Development

```bash
python -m venv venv && ./venv/bin/pip install pytest-homeassistant-custom-component
./venv/bin/python -m pytest
```
