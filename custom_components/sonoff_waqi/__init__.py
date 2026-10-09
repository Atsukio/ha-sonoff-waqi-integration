"""SONOFF AirGuard (SAWF-07P) to WAQI uploader."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .uploader import WaqiConfigEntry, WaqiUploader

PLATFORMS: list[Platform] = [Platform.BUTTON, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: WaqiConfigEntry) -> bool:
    """Set up the uploader from a config entry."""
    uploader = WaqiUploader(hass, entry)
    await uploader.async_start()
    entry.runtime_data = uploader
    entry.async_on_unload(uploader.async_stop)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: WaqiConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: WaqiConfigEntry) -> None:
    """Reload when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
