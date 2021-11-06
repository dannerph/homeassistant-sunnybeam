"""Support for SMASunnyBeam."""
from __future__ import annotations

import logging

from homeassistant.helpers.entity import Entity

from homeassistant.components.sensor import (
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntity,
    SensorEntityDescription,
)

from homeassistant.const import (
    ENERGY_KILO_WATT_HOUR,
    POWER_KILO_WATT,
)

from . import DOMAIN, SMASunnyBeam

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the SMASunnyBeam sensors."""

    if discovery_info is None:
        return

    sensors = []
    sunnybeam = hass.data[DOMAIN]
    sensors.append(SMASunnyBeamSensor(sunnybeam, SensorEntityDescription(
                key="sunnybeam_power",
                name="power",
                native_unit_of_measurement=POWER_KILO_WATT,
                device_class=DEVICE_CLASS_POWER,
                state_class=STATE_CLASS_MEASUREMENT,
            )))
    sensors.append(SMASunnyBeamSensor(sunnybeam, SensorEntityDescription(
                key="sunnybeam_energy_today",
                name="energy_today",
                native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
                device_class=DEVICE_CLASS_ENERGY,
                state_class=STATE_CLASS_TOTAL_INCREASING,
            )))
    sensors.append(SMASunnyBeamSensor(sunnybeam, SensorEntityDescription(
                key="sunnybeam_energy_total",
                name="energy_total",
                native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
                device_class=DEVICE_CLASS_ENERGY,
                state_class=STATE_CLASS_TOTAL_INCREASING,
            )))

    async_add_entities(sensors)


class SMASunnyBeamSensor(SensorEntity):
    """The entity class for SMA Sunny Beam sensors."""

    _attr_should_poll = False

    def __init__(self, sunnybeam: SMASunnyBeam, description: SensorEntityDescription):
        """Initialize the SMASunnyBeam Sensor."""
        self._sunnybeam = sunnybeam
        self.entity_description = description
        self._attr_name = f"{description.key}"
        self._attr_unique_id = f"{description.key}"

    async def async_update(self):
        """Get latest cached states from the device."""
        
        data = self._sunnybeam.get_data()
        _LOGGER.debug(f"received: {data}")
        if data != 0:
            if "power" in self._attr_name:
                self._attr_native_value = round(int(data[0]) / 1000.0, 3)
            elif "today" in self._attr_name:
                self._attr_native_value = round(float(data[1]), 2)
            else:
                self._attr_native_value = int(data[2])

    def update_callback(self):
        """Schedule a state update."""
        self.async_schedule_update_ha_state(True)

    async def async_added_to_hass(self):
        """Add update callback after being added to hass."""
        self._sunnybeam.add_update_listener(self)
