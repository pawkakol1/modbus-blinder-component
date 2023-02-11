"""Adds config flow for Modbus Blinder Component"""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from homeassistant.components.modbus import (
    DEFAULT_HUB,
)
from homeassistant.components.modbus.const import (
    DataType,
    CALL_TYPE_REGISTER_HOLDING,
    CONF_DATA_TYPE,
    CONF_INPUT_TYPE,
    CONF_LAZY_ERROR,
    DEFAULT_HUB,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE,
    MODBUS_DOMAIN,
)

from homeassistant.components.cover import (
    DEVICE_CLASS_BLIND
)

from homeassistant.const import (
    CONF_ADDRESS,
    CONF_DEVICE_CLASS,
    CONF_NAME,
    CONF_ID,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE,
    TEMP_CELSIUS,
)
from .const import (
    CONF_HUB_NAME,
    DEFAULT_NAME,
    DOMAIN,
)


class ModbusBlinderComponentConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Modbus Blinder Component integration."""

    VERSION = 1

    async def async_step_import(self, config: dict[str, Any]) -> FlowResult:
        """Import a configuration from config.yaml."""

        name = config.get(CONF_NAME, DEFAULT_NAME)
        self._async_abort_entries_match({CONF_NAME: name})
        config[CONF_NAME] = name
        return await self.async_step_user(user_input=config)

    async def async_step_user(self, user_input = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        data_schema = vol.Schema(
            {
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
                vol.Required(CONF_HUB_NAME, default="aac20"): cv.string,
                vol.Required(CONF_SLAVE, default=DEFAULT_SLAVE): cv.positive_int,
                vol.Required(CONF_SCAN_INTERVAL, default=1): cv.positive_int,
                vol.Required(CONF_ADDRESS, default=1100): cv.positive_int,
            }
        )

        if user_input:
            #TODO: verification of Modbus Hub name, and verification of each address - if it respods
            
            
            name = user_input.get(CONF_NAME)
            hub_name = user_input.get(CONF_HUB_NAME)
            slave = user_input.get(CONF_SLAVE)
            scan_interval = user_input.get(CONF_SCAN_INTERVAL)
            cur_pos_addr = user_input.get(CONF_ADDRESS)
            input_type = CALL_TYPE_REGISTER_HOLDING
            #dev_class = DEVICE_CLASS_BLIND
            

            if not errors:
                await self.async_set_unique_id(name)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_NAME: name,
                        CONF_HUB_NAME: hub_name,
                        CONF_SLAVE: slave,
                        CONF_SCAN_INTERVAL: scan_interval,
                        CONF_DATA_TYPE: DataType.UINT16.value,
                        CONF_ADDRESS: cur_pos_addr,
                        CONF_INPUT_TYPE: input_type,
                        CONF_LAZY_ERROR: 0,
                        #CONF_DEVICE_CLASS: dev_class,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
