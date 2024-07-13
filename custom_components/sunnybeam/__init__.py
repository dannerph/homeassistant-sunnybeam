"""The SMA Sunny Beam integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry, ConfigEntryError
from homeassistant.const import CONF_SCAN_INTERVAL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from sunnybeamtool.sunnybeamtool import SunnyBeam

from .const import DOMAIN, ENTRY_COORDINATOR, ENTRY_SERIAL_NUMBER

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SMA Sunny Beam from a config entry."""

    s_beam = SunnyBeam()
    try:
        serial_number = await s_beam.get_serial_number()
    except ConnectionError as err:
        raise ConfigEntryError("Could not connect to Sunny Beam") from err

    async def async_update_data():
        """Fetch data from API endpoint."""
        try:
            data = await s_beam.get_measurements()
        except ConnectionError as error:
            raise UpdateFailed("Could not fetch data from Sunny Beam") from error
        _LOGGER.debug("Data fetched from Sunny Beam: %s", data)
        return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=ENTRY_COORDINATOR,
        update_method=async_update_data,
        update_interval=timedelta(seconds=entry.options.get(CONF_SCAN_INTERVAL, 10)),
    )

    await coordinator.async_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        ENTRY_COORDINATOR: coordinator,
        ENTRY_SERIAL_NUMBER: serial_number,
    }

    async def update_listener(hass: HomeAssistant, entry):
        """Handle options update."""

        coordinator.update_interval = timedelta(
            seconds=entry.options.get(CONF_SCAN_INTERVAL, 10)
        )
        _LOGGER.debug(
            "Update interval changed to %d seconds",
            coordinator.update_interval.total_seconds(),
        )

    entry.async_on_unload(entry.add_update_listener(update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
