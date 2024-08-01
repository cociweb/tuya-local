"""
Setup for different kinds of Tuya lawn mowers
"""

from .helpers.lawn_mower import LawnMowerEntity

from .helpers.lawn_mower.const import (
    DOMAIN,
    SERVICE_DOCK,
    SERVICE_PAUSE,
    SERVICE_START_MOWING,
    SERVICE_RESUME,
    SERVICE_CANCEL,
    SERVICE_FIXED_MOWING,
    LawnMowerActivity,
    LawnMowerEntityFeature,
)

from .device import TuyaLocalDevice
from .helpers.config import async_tuya_setup_platform
from .helpers.device_config import TuyaEntityConfig
from .helpers.mixin import TuyaLocalEntity


async def async_setup_entry(hass, config_entry, async_add_entities):
    config = {**config_entry.data, **config_entry.options}
    await async_tuya_setup_platform(
        hass,
        async_add_entities,
        config,
        DOMAIN,
        TuyaLocalLawnMower,
    )


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
            if SERVICE_RESUME in available_commands:
                self._attr_supported_features |= LawnMowerEntityFeature.RESUME
            if SERVICE_CANCEL in available_commands:
                self._attr_supported_features |= LawnMowerEntityFeature.CANCEL
            if SERVICE_FIXED_MOWING in available_commands:
                self._attr_supported_features |= LawnMowerEntityFeature.FIXED_MOWING

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

    async def async_resume(self):
        """Resume mowing."""
        if self._command_dp:
            await self._command_dp.async_set_value(self._device, SERVICE_RESUME)

    async def async_cancel(self):
        """Cancel/Stop mowing."""
        if self._command_dp:
            await self._command_dp.async_set_value(self._device, SERVICE_CANCEL)

    async def async_fixed_mowing(self) -> None:
        """Start fixed spot mowing task."""
        if self._command_dp:
            await self._command_dp.async_set_value(self._device, SERVICE_FIXED_MOWING)
