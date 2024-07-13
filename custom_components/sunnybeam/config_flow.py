"""Config flow for SMA Sunny Beam."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.config_entry_flow import DiscoveryFlowHandler
from sunnybeamtool.sunnybeamtool import SunnyBeam

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def _async_has_devices(hass: HomeAssistant) -> bool:
    """Return if there are devices that can be discovered."""
    try:
        s_beam = SunnyBeam()
        await s_beam.get_serial_number()
    except ConnectionError as err:
        _LOGGER.info(str(err))
        return False
    _LOGGER.info("Sunny Beam found")
    return True


# config_entry_flow.register_discovery_flow(DOMAIN, "SMA Sunny Beam", _async_has_devices)


class SunConfigFlow(DiscoveryFlowHandler, domain=DOMAIN):
    """Discovery flow with options for Wemo."""

    def __init__(self) -> None:
        """Init discovery flow."""
        super().__init__(DOMAIN, "SMA Sunny Beam", _async_has_devices)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(OptionsFlow):
    """Handle a option flow for Sunny Beam."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(CONF_SCAN_INTERVAL, 10),
                    ): vol.All(int, vol.Range(min=7, max=120))
                }
            ),
        )
