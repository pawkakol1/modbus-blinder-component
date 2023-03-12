"""Constants for the Modbus Blinder Component integration."""

from homeassistant.const import (
    Platform
)
from typing import Final



DOMAIN = "modbus_blinder_component"
PLATFORMS = [Platform.COVER]
SW_VERSION = "0.0.9"

ATTR_CONTROL_UP_DOWN_ADDRESS: Final = "control_up_down_address"
ATTR_CURRENT_COVER_POSITION: Final = "current_cover_position"
ATTR_CURRENT_POSITION_ADDRESS: Final = "current_position_address"
ATTR_LAST_STATE: Final = "last_state"
ATTR_SETPOINT_COVER_POSITION: Final = "setpoint_cover_position"
ATTR_SETPOINT_POSITION_ADDRESS: Final = "setpoint_position_address"
CONF_HUB_NAME: Final = "hub_name"

DEFAULT_NAME = 'blinder'

COMMAND_STOP_VALUE = 0
COMMAND_OPEN_VALUE = 1
COMMAND_CLOSE_VALUE = 2

STATE_OPEN_MODBUS_VALUE = 0
STATE_OPENING_MODBUS_VALUE = 1
STATE_CLOSING_MODBUS_VALUE = 2
STATE_CLOSED_MODBUS_VALUE = 3

TIME_FOR_FIRST_CONNECT_TRY_WITH_HUB_IN_SECONS = 10
TIME_FOR_NEXTS_CONNECT_TRIES_WITH_HUB_IN_MINUTES = 10