"""Get station's air quality informations"""
from __future__ import annotations

import logging

import functools as ft
from typing import Any
from datetime import datetime

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from homeassistant.components.cover import (
    ATTR_CURRENT_POSITION,
    ATTR_POSITION,
    CoverEntity, 
    CoverEntityFeature,
)
from homeassistant.components.modbus import get_hub
from homeassistant.components.modbus.base_platform import BasePlatform
from homeassistant.components.modbus.const import (
    CONF_DATA_TYPE,
    CONF_INPUT_TYPE,
    CONF_WRITE_TYPE,
    CALL_TYPE_REGISTER_HOLDING,
    CALL_TYPE_WRITE_REGISTER,
)
from homeassistant.components.modbus.modbus import ModbusHub
    

from homeassistant.const import (
    CONF_ADDRESS,
    CONF_COVERS,
    CONF_DEVICE_CLASS,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE,
    STATE_CLOSED,
    STATE_CLOSING,
    STATE_OPEN,
    STATE_OPENING,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)

from .const import (
    ATTR_CONTROL_UP_DOWN_ADDRESS,
    ATTR_CURRENT_POSITION_ADDRESS,
    ATTR_LAST_STATE,
    ATTR_SETPOINT_COVER_POSITION,
    ATTR_SETPOINT_POSITION_ADDRESS,
    COMMAND_STOP_VALUE,
    COMMAND_OPEN_VALUE,
    COMMAND_CLOSE_VALUE,
    CONF_HUB_NAME,
    DOMAIN,
    DEFAULT_NAME,
    SW_VERSION,
    STATE_CLOSED_MODBUS_VALUE,
    STATE_OPEN_MODBUS_VALUE,
    STATE_OPENING_MODBUS_VALUE,
    STATE_CLOSING_MODBUS_VALUE,
)
PARALLEL_UPDATES = 1

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> bool:

    #Get modbus hub created in configuration.yaml using its name
    hub: ModbusHub = get_hub(hass, entry.data[CONF_HUB_NAME])
    entities = []
    _LOGGER.debug(f"Got HUB: {hub.name}")
    entities.append(ModbusBlinderComponentCover(hub, entry.data))
    _LOGGER.debug(f"Create Modbus blinder entry for: {entry.data[CONF_HUB_NAME]}")
    

    async_add_entities(entities, update_before_add=True)


class ModbusBlinderComponentCover(BasePlatform, CoverEntity, RestoreEntity):
    """Representation of a cover."""
    #override
    _attr_supported_features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP | CoverEntityFeature.SET_POSITION
    #new attributes
    _attr_up_down_state: int | None
    _attr_last_state : None = None
    _attr_setpoint_cover_position: int | None = None


    def __init__(self, hub: ModbusHub, config: dict[str, Any]) -> None:
        super().__init__(hub, config)

        #states
        self._state = None
        self._attr_is_closed = False

        #Modbus parameters
        self._hub_name = config[CONF_HUB_NAME]
        self._input_type = CALL_TYPE_REGISTER_HOLDING
        self._write_type = CALL_TYPE_WRITE_REGISTER
        self._address = config[CONF_ADDRESS]
        self._address_setpoint = self._address + 1
        self._address_updown = self._address + 2

        #name
        if config[CONF_NAME]:
            self._name = config[CONF_NAME]
        else:
            self._name = f"{DEFAULT_NAME}_{self._input_type}_{self._address}"
        self._attr_name = self._name
        self._attr_unique_id = f"{self._hub_name}_{self._name}"

        #device
        self._attr_device_info = DeviceInfo(
            identifiers = {(DOMAIN, self._attr_unique_id)},
            manufacturer = "@pawkakol1",
            model = f"{self._hub_name}",
            sw_version = SW_VERSION,
            name = self._name
        )

        #additional attributes



#    @property
#    def last_state(self) -> int | None:
#        """Return last known state.
#
#        None, opening, closing, open, closed
#        """
#        return self._attr_last_state

#    @property
#    def setpoint_cover_position(self) -> int | None:
#        """Return actuall setpoint position of cover.
#
#        0-100
#        """
#        return self._attr_setpoint_cover_position


    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open cover."""
        _LOGGER.debug(f"Write Holding Register address: {self._address_updown}, with value: {COMMAND_OPEN_VALUE}")
        result = await self._hub.async_pymodbus_call(
            self._slave, self._address_updown, COMMAND_OPEN_VALUE, self._write_type
        )
        self._attr_available = result is not None
        await self.async_update()

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close cover."""
        _LOGGER.debug(f"Write Holding Register address: {self._address_updown}, with value: {COMMAND_CLOSE_VALUE}")
        result = await self._hub.async_pymodbus_call(
            self._slave, self._address_updown, COMMAND_CLOSE_VALUE, self._write_type
        )
        self._attr_available = result is not None
        await self.async_update()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        _LOGGER.debug(f"Write Holding Register address: {self._address_updown}, with value: {COMMAND_CLOSE_VALUE}")
        result = await self._hub.async_pymodbus_call(
            self._slave, self._address_updown, COMMAND_STOP_VALUE, self._write_type
        )
        self._attr_available = result is not None
        await self.async_update()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Move the cover to a specific position."""
        _LOGGER.debug(f"Write Holding Register address: {self._address_setpoint}, with value: {kwargs[ATTR_POSITION]}")
        result = await self._hub.async_pymodbus_call(
            self._slave, self._address_setpoint, kwargs[ATTR_POSITION], self._write_type
        )
        self._attr_available = result is not None
        await self.async_update()
        #await self.hass.async_add_executor_job(
        #    ft.partial(self.set_cover_position, **kwargs)
        #)
    
    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await self.async_base_added_to_hass()
        if state := await self.async_get_last_state():
            convert = {
                STATE_CLOSED: STATE_CLOSED_MODBUS_VALUE,
                STATE_CLOSING: STATE_CLOSING_MODBUS_VALUE,
                STATE_OPENING: STATE_OPENING_MODBUS_VALUE,
                STATE_OPEN: STATE_OPEN_MODBUS_VALUE,
                STATE_UNAVAILABLE: None,
                STATE_UNKNOWN: None,
            }
            self._set_attr_state(convert[state.state])
    
    def _set_attr_state(self, value: str | bool | int) -> None:
        """Convert received value to HA state."""
        self._attr_is_opening = value == STATE_OPENING_MODBUS_VALUE
        self._attr_is_closing = value == STATE_CLOSING_MODBUS_VALUE
        self._attr_is_closed = value == STATE_CLOSED_MODBUS_VALUE
    
#    def convert_modbus_status_to_state(self, value: int) -> str | None:
#        if value == STATE_CLOSED_MODBUS_VALUE:
#            return STATE_CLOSED
#        elif value == STATE_OPEN_MODBUS_VALUE:
#            return STATE_OPEN
#        elif value == STATE_OPENING_MODBUS_VALUE:
#            return STATE_OPENING
#        elif value == STATE_CLOSING_MODBUS_VALUE:
#            return STATE_CLOSING
#        else:
#            return None

    async def async_update(self, now: datetime | None = None) -> None:
        """Update the state of the cover."""
        # remark "now" is a dummy parameter to avoid problems with
        # async_track_time_interval
        # do not allow multiple active calls to the same platform
        _LOGGER.debug(f"Trying: _call_active: {self._call_active}")
        if self._call_active:
            return
        self._call_active = True
        result = await self._hub.async_pymodbus_call(
            self._slave, self._address, 4, self._input_type
        )
        self._call_active = False
        _LOGGER.debug("Request sent")
        if result is None:
            _LOGGER.debug("No result:")
            if self._lazy_errors:
                self._lazy_errors -= 1
                return
            self._lazy_errors = self._lazy_error_count
            self._attr_available = False
            self.schedule_update_ha_state()
            #self.async_write_ha_state()
            return
        _LOGGER.debug("Result:")
        self._lazy_errors = self._lazy_error_count
        self._attr_available = True

        #current position
        self._attr_current_cover_position = int(result.registers[0])
        #current setpoint
        self._attr_setpoint_cover_position = int(result.registers[1])

        self._set_attr_state(int(result.registers[3]))
        #self._set_attr_state(self.convert_modbus_status_to_state(int(result.registers[3])))
        self.schedule_update_ha_state()
        #self.async_write_ha_state()
        #_LOGGER.debug(f"{self._name}-> Current position: {self._attr_current_cover_position}; Setpoint position: {self._attr_setpoint_cover_position}; State: {self._state}")
        _LOGGER.debug(f"{self._name}-> Current position: {self._attr_current_cover_position}; Setpoint position: {self._attr_setpoint_cover_position}; State: {result.registers[3]}")
        _LOGGER.debug(f"{self._name}-> State opening: {self._attr_is_opening}; State closing: {self._attr_is_closing}; State closed: {self._attr_is_closed}")
        _LOGGER.debug(f"{self._name}-> State opening: {self.is_opening}; State closing: {self.is_closing}; State closed: {self.is_closed}")
