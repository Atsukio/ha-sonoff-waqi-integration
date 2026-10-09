"""Base entity for the WAQI uploader."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .uploader import WaqiUploader


class WaqiUploaderEntity(Entity):
    """Common device info and update wiring."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, uploader: WaqiUploader, key: str) -> None:
        self.uploader = uploader
        entry_id = uploader.entry.entry_id
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=f"WAQI uploader {uploader.station_name}",
            manufacturer="World Air Quality Index Project",
            model="Data upload API",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://aqicn.org/data-feed/verification/",
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.uploader.async_add_listener(self.async_write_ha_state))
