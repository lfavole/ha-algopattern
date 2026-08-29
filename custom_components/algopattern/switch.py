"""Switch platform for AlgoPattern integration."""
from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
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
class AlgoPatternSwitchEntityDescription(SwitchEntityDescription):
    """Describes an AlgoPattern switch entity."""

    is_on_fn: Callable[[dict[str, Any]], bool]
    update_fn: Callable[[AlgoPatternDataUpdateCoordinator, bool], Coroutine[Any, Any, None]]


SWITCH_DESCRIPTIONS: tuple[AlgoPatternSwitchEntityDescription, ...] = (
    AlgoPatternSwitchEntityDescription(
        key="daily_reminder_enabled",
        translation_key="daily_reminder_enabled",
        name="Daily Reminder Enabled",
        icon="mdi:bell-ring",
        entity_category=EntityCategory.CONFIG,
        is_on_fn=lambda data: bool(data.get("daily_reminder_enabled", False)),
        update_fn=lambda coordinator, value: coordinator.api.async_update_user_preferences(
            coordinator.user_id, coordinator.access_token, {"daily_reminder_enabled": value}
        ),
    ),
    AlgoPatternSwitchEntityDescription(
        key="immediate_quiz_feedback",
        translation_key="immediate_quiz_feedback",
        name="Immediate Quiz Feedback",
        icon="mdi:message-badge-outline",
        entity_category=EntityCategory.CONFIG,
        is_on_fn=lambda data: bool(data.get("immediate_quiz_feedback", False)),
        update_fn=lambda coordinator, value: coordinator.api.async_update_user_preferences(
            coordinator.user_id, coordinator.access_token, {"immediate_quiz_feedback": value}
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AlgoPattern switches from a config entry."""
    coordinator: AlgoPatternDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        AlgoPatternSwitchEntity(coordinator, description)
        for description in SWITCH_DESCRIPTIONS
    )


class AlgoPatternSwitchEntity(
    CoordinatorEntity[AlgoPatternDataUpdateCoordinator], SwitchEntity
):
    """Representation of an AlgoPattern switch."""

    entity_description: AlgoPatternSwitchEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AlgoPatternDataUpdateCoordinator,
        description: AlgoPatternSwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
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
    def is_on(self) -> bool:
        """Return True if the switch is on."""
        if not self.coordinator.data:
            return False
        return self.entity_description.is_on_fn(self.coordinator.data)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.entity_description.update_fn(self.coordinator, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.entity_description.update_fn(self.coordinator, False)
        await self.coordinator.async_request_refresh()
