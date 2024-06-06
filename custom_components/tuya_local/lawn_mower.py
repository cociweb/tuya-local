"""
Setup for different kinds of Tuya lawn mowers
"""

from homeassistant.components.lawn_mower import LawnMowerEntity
from homeassistant.components.lawn_mower.const import (
    SERVICE_DOCK,
    SERVICE_PAUSE,
    SERVICE_START_MOWING,
    LawnMowerActivity as HALawnMowerActivity,
    LawnMowerEntityFeature,
)

from .device import TuyaLocalDevice
from .helpers.config import async_tuya_setup_platform
from .helpers.device_config import TuyaEntityConfig
from .helpers.mixin import TuyaLocalEntity


from enum import Enum

async def async_setup_entry(hass, config_entry, async_add_entities):
    config = {**config_entry.data, **config_entry.options}
    await async_tuya_setup_platform(
        hass,
        async_add_entities,
        config,
        "lawn_mower",
        TuyaLocalLawnMower,
    )



class ExtendedLawnMowerActivity(Enum):
    # Include original constants
    for activity in HALawnMowerActivity:
        locals()[activity.name] = activity.value

    # Add new constants
    CHARGING = "charging"
    """Device is charging at the docking station."""

    CHARGING_WITH_TASK_SUSPEND = "resume after recharged" 
    """Device is charging and it has task meanwhile. It will resume after the battery is fully charged.."""

    STANDBY = "standby"
    """Device is in standby state, waiting for the next task"""

    PARK = "docking"
    """Device is going to it's station."""

    LOCKED = "locked"
    """Incorrect pin is entered and the device get locked for a certain time."""

    FIXED_MOWING = "spot mowing"
    """The mower is working on a fix spot."""

    EMERGENCY = "manually stopped"
    """In an Emergency situation the device is stopped."""

# Reassign the name 'LawnMowerActivity' to the new enum
LawnMowerActivity = ExtendedLawnMowerActivity



class TuyaLocalLawnMower(TuyaLocalEntity, LawnMowerEntity):
    """Representation of a Tuya Lawn Mower"""

    def __init__(self, device: TuyaLocalDevice, config: TuyaEntityConfig):
        """
        Initialise the lawn mower.
        Args:
            device (TuyaLocalDevice): the device API instance.
            config (TuyaEntityConfig): the configuration for this entity
        """
        super().__init__()
        dps_map = self._init_begin(device, config)
        self._activity_dp = dps_map.pop("activity", None)
        self._command_dp = dps_map.pop("command", None)
        self._init_end(dps_map)

        if self._command_dp:
            available_commands = self._command_dp.values(self._device)
            if SERVICE_START_MOWING in available_commands:
                self._attr_supported_features |= LawnMowerEntityFeature.START_MOWING
            if SERVICE_PAUSE in available_commands:
                self._attr_supported_features |= LawnMowerEntityFeature.PAUSE
            if SERVICE_DOCK in available_commands:
                self._attr_supported_features |= LawnMowerEntityFeature.DOCK

    @property
    def activity(self) -> LawnMowerActivity | None:
        """Return the status of the lawn mower."""
        return LawnMowerActivity(self._activity_dp.get_value(self._device))

    async def async_start_mowing(self) -> None:
        """Start mowing the lawn."""
        if self._command_dp:
            await self._command_dp.async_set_value(self._device, SERVICE_START_MOWING)

    async def async_pause(self):
        """Pause lawn mowing."""
        if self._command_dp:
            await self._command_dp.async_set_value(self._device, SERVICE_PAUSE)

    async def async_dock(self):
        """Stop mowing and return to dock."""
        if self._command_dp:
            await self._command_dp.async_set_value(self._device, SERVICE_DOCK)
