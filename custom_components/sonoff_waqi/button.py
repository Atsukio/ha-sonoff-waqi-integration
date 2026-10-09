"""Manual upload button."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import WaqiUploaderEntity
from .uploader import WaqiConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: WaqiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button."""
    async_add_entities([UploadNowButton(entry.runtime_data, "upload_now")])


class UploadNowButton(WaqiUploaderEntity, ButtonEntity):
    """Push the current averaging window to WAQI immediately."""

    async def async_press(self) -> None:
        await self.uploader.async_upload()
