"""Support for SMASunnyBeam."""
import logging

from homeassistant.helpers.entity import Entity

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the SMASunnyBeam sensors."""

    if discovery_info is None:
        return

    sensors = []
    sunnybeam = hass.data[DOMAIN]
    sensors.append(SMASunnyBeamSensor("power", sunnybeam))
    sensors.append(SMASunnyBeamSensor("energy_today", sunnybeam))
    sensors.append(SMASunnyBeamSensor("energy_total", sunnybeam))

    async_add_entities(sensors)


class SMASunnyBeamSensor(Entity):
    """The entity class for energy_today charging stations sensors."""

    def __init__(self, name, sunnybeam):
        """Initialize the SMASunnyBeam Sensor."""
        self._name = name
        self._sunnybeam = sunnybeam
        self._state = None

    @property
    def unique_id(self):
        """Return the unique ID of the binary sensor."""
        return f"sunnybeam_{self._name}"

    @property
    def name(self):
        """Return the name of the device."""
        return f"sunnybeam_{self._name.capitalize()}"

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        
        if "energy" in self._name:
            return "mdi:gauge"
        else:
            return "mdi:flash"


    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Get the unit of measurement."""

        if "energy" in self._name:
            return "kWh"
        else:
            return "kW"

    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state.

        False if entity pushes its state to HA.
        """
        return False

    async def async_update(self):
        """Get latest cached states from the device."""
        
        data = self._sunnybeam.get_data()
        _LOGGER.debug(data)
        if data != 0:
            if "power" in self._name:
                self._state = round(int(data[0]) / 1000.0, 3)
            elif "today" in self._name:
                self._state = round(float(data[1]), 2)
            else:
                self._state = round(float(data[2]), 2)

    def update_callback(self):
        """Schedule a state update."""
        self.async_schedule_update_ha_state(True)

    async def async_added_to_hass(self):
        """Add update callback after being added to hass."""
        self._sunnybeam.add_update_listener(self)
