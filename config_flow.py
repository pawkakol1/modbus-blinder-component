"""Adds config flow for Modbus Blinder Component"""
from __future__ import annotations

from typing import Any

import logging

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow,
    ConfigEntry,
)
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from homeassistant.components.modbus.const import (
    DataType,
    CALL_TYPE_REGISTER_HOLDING,
    CONF_DATA_TYPE,
    CONF_INPUT_TYPE,
    DEFAULT_SLAVE
)

from homeassistant.components.cover import CoverDeviceClass

from homeassistant.const import (
    CONF_ADDRESS,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE
)
from .const import (
    CONF_HUB_NAME,
    CONF_INIT,
    CONF_USER,
    DEFAULT_NAME,
    DOMAIN
)

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_HUB_NAME, default="aac20"): cv.string,
        vol.Required(CONF_SLAVE, default=DEFAULT_SLAVE): cv.positive_int,
        vol.Required(CONF_SCAN_INTERVAL, default=1): cv.positive_int,
        vol.Required(CONF_ADDRESS, default=1000): cv.positive_int,
    }
)


class ModbusBlinderComponentConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Modbus Blinder Component integration."""

    VERSION = 1

    async def async_step_import(self, config: dict[str, Any]):
        """Import a configuration from config.yaml."""

        name = config.get(CONF_NAME, DEFAULT_NAME)
        self._async_abort_entries_match({CONF_NAME: name})
        config[CONF_NAME] = name
        return await self.async_step_user(user_input=config)

    async def async_step_user(self, user_input = None):
        """Handle the initial step."""
        errors = {}

        if user_input:
            #TODO: verification of Modbus Hub name, and verification of each address - if it respods
            
            
            name = user_input.get(CONF_NAME)
            hub_name = user_input.get(CONF_HUB_NAME)
            slave = user_input.get(CONF_SLAVE)
            scan_interval = user_input.get(CONF_SCAN_INTERVAL)
            cur_pos_addr = user_input.get(CONF_ADDRESS)
            input_type = CALL_TYPE_REGISTER_HOLDING
            #dev_class = CoverDeviceClass.BLIND
            

            if not errors:
                await self.async_set_unique_id(f"{name}_{cur_pos_addr}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=DEFAULT_NAME,
                    data={
                        CONF_NAME: name,
                        CONF_HUB_NAME: hub_name,
                        CONF_SLAVE: slave,
                        CONF_SCAN_INTERVAL: scan_interval,
                        CONF_DATA_TYPE: DataType.UINT16.value,
                        CONF_ADDRESS: cur_pos_addr,
                        CONF_INPUT_TYPE: input_type,
                        #CONF_DEVICE_CLASS: dev_class,
                    },
                )

        return self.async_show_form(
            step_id=CONF_USER,
            data_schema=DATA_SCHEMA,
            errors=errors,
        )    
    
    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> ModbusBlinderComponentOptionsFlowHandler:
        """Get the options flow for this handler."""
        return ModbusBlinderComponentOptionsFlowHandler(config_entry)


class ModbusBlinderComponentOptionsFlowHandler(ConfigFlow):
    """Handle options flow handler for ModbusBlinderComponent integration."""

    def __init__(self, config_entry):
        """Initialize ModbusBlinderComponent options flow."""
        _LOGGER.debug(f"Editing0")
        self.config_entry = config_entry
        _LOGGER.debug(f"entry_id: {self.config_entry.entry_id}")

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage basic options."""
        errors = {}
        if user_input is not None:
            _LOGGER.debug(f"Editing1")
            name = user_input.get(CONF_NAME)
            hub_name = user_input.get(CONF_HUB_NAME)
            slave = user_input.get(CONF_SLAVE)
            scan_interval = user_input.get(CONF_SCAN_INTERVAL)
            cur_pos_addr = user_input.get(CONF_ADDRESS)
            input_type = CALL_TYPE_REGISTER_HOLDING
            #dev_class = CoverDeviceClass.BLIND
            _LOGGER.debug(f"Editing2")
            

            if not errors:
                _LOGGER.debug(f"Editing3")
                await self.async_set_unique_id(f"{name}_{cur_pos_addr}")
                _LOGGER.debug(f"Editing4")
                self._abort_if_unique_id_configured()
                _LOGGER.debug(f"Editing5")

                data = {
                        CONF_NAME: name,
                        CONF_HUB_NAME: hub_name,
                        CONF_SLAVE: slave,
                        CONF_SCAN_INTERVAL: scan_interval,
                        CONF_DATA_TYPE: DataType.UINT16.value,
                        CONF_ADDRESS: cur_pos_addr,
                        CONF_INPUT_TYPE: input_type,
                        #CONF_DEVICE_CLASS: dev_class,
                    }
                
                await self.hass.config_entries.async_unload(self.config_entry.entry_id)

                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    title=self.config_entry.title,
                    data=data,
                )
                return self.async_create_entry(title="", data={})
            _LOGGER.debug(f"Editing7")
        
        _LOGGER.debug(f"Config_entry:")
        _LOGGER.debug(f"{self.config_entry}")

        defaults = self.config_entry.data

        return self.async_show_form(
            step_id=CONF_INIT,
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=defaults[CONF_NAME]): cv.string,
                    vol.Required(CONF_HUB_NAME, default=defaults[CONF_HUB_NAME]): cv.string,
                    vol.Required(CONF_SLAVE, default=defaults[CONF_SLAVE]): cv.positive_int,
                    vol.Required(CONF_SCAN_INTERVAL, default=defaults[CONF_SCAN_INTERVAL]): cv.positive_int,
                    vol.Required(CONF_ADDRESS, default=defaults[CONF_ADDRESS]): cv.positive_int,
                }
            ),
            errors=errors,
        )
