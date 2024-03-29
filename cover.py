"""Get station's air quality informations"""
from __future__ import annotations

import asyncio
import logging

import functools as ft
from typing import Any
from datetime import datetime

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverEntity, 
    CoverEntityFeature
)
from homeassistant.components.modbus import get_hub
from homeassistant.components.modbus.base_platform import BasePlatform
from homeassistant.components.modbus.const import (
    CALL_TYPE_REGISTER_HOLDING,
    CALL_TYPE_WRITE_REGISTER
)
from homeassistant.components.modbus.modbus import (
    ModbusHub
) 
    

from homeassistant.const import (
    CONF_ADDRESS,
    CONF_NAME
)

from .const import (
    ATTR_LAST_STATE,
    COMMAND_OPEN_VALUE,
    COMMAND_CLOSE_VALUE,
    CONF_HUB_NAME,
    STATE_CONVERT,
    DOMAIN,
    DEFAULT_NAME,
    SW_VERSION,
    STATE_CLOSED_MODBUS_VALUE,
    STATE_OPENING_MODBUS_VALUE,
    STATE_CLOSING_MODBUS_VALUE,
    STATUS_STATES_ARR,
    TIME_FOR_FIRST_CONNECT_TRY_WITH_HUB_IN_SECONS,
    TIME_FOR_NEXTS_CONNECT_TRIES_WITH_HUB_IN_MINUTES,
)
PARALLEL_UPDATES = 1

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_devices: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Modbus Blinder Component covers"""
    _LOGGER.warning(
        "Configuration of the Modbus Blinder Component platform in YAML is deprecated and will be "
        "removed in Home Assistant 2022.4; Your existing configuration "
        "has been imported into the UI automatically and can be safely removed "
        "from your configuration.yaml file"
    )
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data=config,
        )
    )

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> bool:
    hub: ModbusHub | None = None
    #Get modbus hub created in configuration.yaml using its name
    _LOGGER.debug(f"Setup entry - version {SW_VERSION}")
    _LOGGER.debug(f"Remembered HUB name: {entry.data[CONF_HUB_NAME]}")
    waitTime = TIME_FOR_FIRST_CONNECT_TRY_WITH_HUB_IN_SECONS
    while(hub is None):
        try:
            hub = get_hub(hass, entry.data[CONF_HUB_NAME])
        except:
            _LOGGER.warning(f"Modbus HUB named {entry.data[CONF_HUB_NAME]} hasn't started yet. Waiting {waitTime} seconds for next try...")
            await asyncio.sleep(waitTime)
            waitTime = TIME_FOR_NEXTS_CONNECT_TRIES_WITH_HUB_IN_MINUTES * 60
    
    entities = []
    _LOGGER.debug(f"Got HUB: {hub.name}")
    _LOGGER.debug(f"Entry data: {entry.data}")
    entities.append(ModbusBlinderComponentCover(hass, hub, entry.data))
    _LOGGER.debug(f"Create Modbus blinder entry for: {entry.data[CONF_HUB_NAME]}")
    

    async_add_entities(entities, update_before_add=True)


class ModbusBlinderComponentCover(BasePlatform, CoverEntity, RestoreEntity):
    """Representation of a cover."""
    #override
    _attr_supported_features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP | CoverEntityFeature.SET_POSITION
    #new attributes
    _attr_last_state : int = 5
    _attr_setpoint_cover_position: int | None = None


    def __init__(self, hass: HomeAssistant, hub: ModbusHub, config: dict[str, Any]) -> None:
        super().__init__(hass, hub, config)

        #states
        self._attr_is_closed = False

        #Modbus parameters
        self._hub = hub
        self._hub_name = config[CONF_HUB_NAME]
        self._input_type = CALL_TYPE_REGISTER_HOLDING
        self._write_type = CALL_TYPE_WRITE_REGISTER
        self._address = config[CONF_ADDRESS]
        self._address_control = self._address + 1

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
#    def setpoint_cover_position(self) -> int | None:
#        """Return actuall setpoint position of cover.
#
#        0-100
#        """
#        return self._attr_setpoint_cover_position


    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open cover."""
        _LOGGER.debug(f"Write Holding Register address: {(self._address_control)}, with value: {COMMAND_OPEN_VALUE}")
        result = await self._hub.async_pb_call(
            self._slave, (self._address_control), (int(COMMAND_OPEN_VALUE) << 8) | int(self._attr_setpoint_cover_position), self._write_type
        )
        self._attr_available = result is not None
        await self.async_update()

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close cover."""
        _LOGGER.debug(f"Write Holding Register address: {(self._address_control)}, with value: {COMMAND_CLOSE_VALUE}")
        result = await self._hub.async_pb_call(
            self._slave, (self._address_control), (int(COMMAND_CLOSE_VALUE) << 8) | int(self._attr_setpoint_cover_position), self._write_type
        )
        self._attr_available = result is not None
        await self.async_update()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        _LOGGER.debug(f"Write Holding Register address: {self._address_control}, with value: {COMMAND_CLOSE_VALUE}")
        result = await self._hub.async_pb_call(
            self._slave, self._address_control, int(self._attr_setpoint_cover_position), self._write_type
        )
        self._attr_available = result is not None
        await self.async_update()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Move the cover to a specific position."""
        _LOGGER.debug(f"Write Holding Register address: {self._address_control}, with value: {kwargs[ATTR_POSITION]}")
        result = await self._hub.async_pb_call(
            self._slave, self._address_control, kwargs[ATTR_POSITION], self._write_type
        )
        self._attr_available = result is not None
        await self.async_update()
    
    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await self.async_base_added_to_hass()
        if state := await self.async_get_last_state():
            self._set_attr_state(STATE_CONVERT[state.state])
    
    def _set_attr_state(self, value: str | bool | int) -> None:
        """Convert received value to HA state."""
        self._attr_is_opening = value == STATE_OPENING_MODBUS_VALUE
        self._attr_is_closing = value == STATE_CLOSING_MODBUS_VALUE
        self._attr_is_closed = value == STATE_CLOSED_MODBUS_VALUE

    async def async_update(self, now: datetime | None = None) -> None:
        """Update the state of the cover."""
        # remark "now" is a dummy parameter to avoid problems with
        # async_track_time_interval
        # do not allow multiple active calls to the same platform
        _LOGGER.debug(f"Trying: _call_active: {self._call_active}")
        if self._call_active:
            return
        self._call_active = True
        result = await self._hub.async_pb_call(
            self._slave, self._address, int(2), self._input_type
        )
        
        self._call_active = False
        _LOGGER.debug("Request sent")
        if result is None:
            _LOGGER.debug("No result:")
            self._attr_available = False
            self.schedule_update_ha_state()
            return
        _LOGGER.debug("Result:")
        self._attr_available = True

        #current position
        self._attr_current_cover_position = (int(result.registers[0]) & 0x00FF)
        #last status
        self._attr_last_state = (int((result.registers[0]) >> 12) & 0x000F)
        #current status
        self._set_attr_state(int((result.registers[0]) >> 8) & 0x000F)

        self._attr_extra_state_attributes = {
            ATTR_LAST_STATE: STATUS_STATES_ARR[self._attr_last_state]
        }

        #current setpoint
        self._attr_setpoint_cover_position = (int(result.registers[1]) & 0x00FF)

        self.schedule_update_ha_state()
        
        _LOGGER.debug(f"{self._name}-> Current position: {self._attr_current_cover_position}; Setpoint position: {self._attr_setpoint_cover_position}; State: {self.state}")
        _LOGGER.debug(f"{self._name}-> State opening: {self._attr_is_opening}; State closing: {self._attr_is_closing}; State closed: {self._attr_is_closed}")
        _LOGGER.debug(f"{self._name}-> Last state is: {self._attr_last_state}")

