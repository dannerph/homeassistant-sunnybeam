"""Support for SMASunnyBeam."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    DOMAIN,
    ENTRY_COORDINATOR,
    ENTRY_SERIAL_NUMBER,
    KEY_ENERGY_TODAY,
    KEY_ENERGY_TOTAL,
    KEY_POWER,
)

SENSORS = [
    SensorEntityDescription(
        key=KEY_POWER,
        translation_key=KEY_POWER,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=KEY_ENERGY_TODAY,
        translation_key=KEY_ENERGY_TODAY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key=KEY_ENERGY_TOTAL,
        translation_key=KEY_ENERGY_TOTAL,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SMA Sunny Beam sensors."""
    entry = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = entry[ENTRY_COORDINATOR]
    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry[ENTRY_SERIAL_NUMBER])},
        manufacturer="SMA",
        model="Sunny Beam",
    )
    async_add_entities(
        [
            SMASunnyBeamSensor(
                coordinator,
                device_info,
                description,
            )
            for description in SENSORS
        ]
    )


class SMASunnyBeamSensor(CoordinatorEntity, SensorEntity):
    """The entity class for SMA Sunny Beam sensors."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        device_info: DeviceInfo,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the SMASunnyBeam Sensor."""
        super().__init__(coordinator, context=description.key)
        self._attr_device_info = device_info
        self.entity_description = description
        self._attr_unique_id = description.key

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data[self.entity_description.key]
        self.async_write_ha_state()
