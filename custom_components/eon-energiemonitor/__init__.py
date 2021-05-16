"""Support for SMASunnyBeam."""
from sunnybeamtool.sunnybeamtool import SunnyBeam
import logging

import voluptuous as vol

from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

DOMAIN = "sunnybeam"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_SCAN_INTERVAL, default=10): cv.positive_int, # seconds
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass, config):
    """Set up parameters."""
    
    scan_interval = config[DOMAIN][CONF_SCAN_INTERVAL]

    sunnybeam = SMASunnyBeam(hass, scan_interval)
    hass.data[DOMAIN] = sunnybeam

    # initial update
    await sunnybeam.update()

    # Load sensors
    hass.async_create_task(
        discovery.async_load_platform(hass, "sensor", DOMAIN, {}, config)
    )

    return True


class SMASunnyBeam():
    """Representation of a SMASunnyBeam."""

    def __init__(self, hass, scan_interval):
        """Initialize SMASunnyBeam."""

        self._hass = hass
        self._data = {}
        self._s_beam = SunnyBeam()

        self._update_listeners = []
        self._scan_interval = scan_interval

    def get_data(self):
        """Get SMASunnyBeam."""

        return self._data.get()

    async def update(self, *args):
        """Fetch new data from SMASunnyBeam."""

        self._data = await self._s_beam.get_measurements()
        if self._data == 0:
            _LOGGER.warning("New data could not be fetched, try again next time.")

        self._notify_listeners()

    def add_update_listener(self, listener):
        """Add a listener for update notifications."""

        self._update_listeners.append(listener)
        _LOGGER.debug(f"registered sensor: {listener.entity_id}")
        
        # initial data is already loaded, thus update the component
        listener.update_callback()

    def _notify_listeners(self):

        # Inform entities about updated values
        for listener in self._update_listeners:
            listener.update_callback()
        _LOGGER.debug("Notifying all listeners")