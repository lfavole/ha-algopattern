"""Time platform for AlgoPattern integration."""
from __future__ import annotations

import datetime
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.time import (
    TimeEntity,
    TimeEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
)
from .coordinator import AlgoPatternDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class AlgoPatternTimeEntityDescription(TimeEntityDescription):
    """Describes an AlgoPattern time entity."""

    value_fn: Callable[[dict[str, Any]], datetime.time | None]
    update_fn: Callable[[AlgoPatternDataUpdateCoordinator, datetime.time], Coroutine[Any, Any, None]]


def _parse_time(time_str: str | None) -> datetime.time | None:
    """Parse time string like HH:MM to datetime.time."""
    if not time_str:
        return None
    try:
        parts = time_str.split(":")
        return datetime.time(hour=int(parts[0]), minute=int(parts[1]))
    except (ValueError, IndexError):
        return None


TIME_DESCRIPTIONS: tuple[AlgoPatternTimeEntityDescription, ...] = (
    AlgoPatternTimeEntityDescription(
        key="daily_reminder_time",
        translation_key="daily_reminder_time",
        name="Daily Reminder Time",
        icon="mdi:clock-outline",
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda data: _parse_time(data.get("daily_reminder_time", "17:00")),
        update_fn=lambda coordinator, value: coordinator.api.async_update_user_preferences(
            coordinator.user_id, coordinator.access_token, {"daily_reminder_time": value.strftime("%H:%M")}
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AlgoPattern time entities from a config entry."""
    coordinator: AlgoPatternDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        AlgoPatternTimeEntity(coordinator, description)
        for description in TIME_DESCRIPTIONS
    )


class AlgoPatternTimeEntity(
    CoordinatorEntity[AlgoPatternDataUpdateCoordinator], TimeEntity
):
    """Representation of an AlgoPattern time entity."""

    entity_description: AlgoPatternTimeEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AlgoPatternDataUpdateCoordinator,
        description: AlgoPatternTimeEntityDescription,
    ) -> None:
        """Initialize the time entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.user_id}_{description.key}"
        user_name = coordinator.data.get("name") if coordinator.data else "AlgoPattern User"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.user_id)},
            name=user_name,
            entry_type=None,
        )

    @property
    def native_value(self) -> datetime.time | None:
        """Return the native value of the time entity."""
        if not self.coordinator.data:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    async def async_set_value(self, value: datetime.time) -> None:
        """Update the time value."""
        await self.entity_description.update_fn(self.coordinator, value)
        await self.coordinator.async_request_refresh()
