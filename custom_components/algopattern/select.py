"""Select platform for AlgoPattern integration."""
from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.select import (
    SelectEntity,
    SelectEntityDescription,
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
class AlgoPatternSelectEntityDescription(SelectEntityDescription):
    """Describes an AlgoPattern select entity."""

    current_option_fn: Callable[[dict[str, Any]], str | None]
    update_fn: Callable[[AlgoPatternDataUpdateCoordinator, str], Coroutine[Any, Any, None]]


SELECT_DESCRIPTIONS: tuple[AlgoPatternSelectEntityDescription, ...] = (
    AlgoPatternSelectEntityDescription(
        key="experience_level",
        translation_key="experience_level",
        name="Experience Level",
        icon="mdi:school",
        entity_category=EntityCategory.CONFIG,
        options=["Beginner", "Intermediate", "Advanced"],
        current_option_fn=lambda data: data.get("experience_level", "Intermediate"),
        update_fn=lambda coordinator, value: coordinator.api.async_update_user_preferences(
            coordinator.user_id, coordinator.access_token, {"experience_level": value}
        ),
    ),
    AlgoPatternSelectEntityDescription(
        key="preparation_goal",
        translation_key="preparation_goal",
        name="Preparation Goal",
        icon="mdi:target",
        entity_category=EntityCategory.CONFIG,
        options=["Tech Interview Prep", "Competitive Programming", "General Improvement"],
        current_option_fn=lambda data: data.get("preparation_goal", "Tech Interview Prep"),
        update_fn=lambda coordinator, value: coordinator.api.async_update_user_preferences(
            coordinator.user_id, coordinator.access_token, {"preparation_goal": value}
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AlgoPattern selects from a config entry."""
    coordinator: AlgoPatternDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        AlgoPatternSelectEntity(coordinator, description)
        for description in SELECT_DESCRIPTIONS
    )


class AlgoPatternSelectEntity(
    CoordinatorEntity[AlgoPatternDataUpdateCoordinator], SelectEntity
):
    """Representation of an AlgoPattern select."""

    entity_description: AlgoPatternSelectEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AlgoPatternDataUpdateCoordinator,
        description: AlgoPatternSelectEntityDescription,
    ) -> None:
        """Initialize the select."""
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
    def current_option(self) -> str | None:
        """Return the current option."""
        if not self.coordinator.data:
            return None
        return self.entity_description.current_option_fn(self.coordinator.data)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.entity_description.update_fn(self.coordinator, option)
        await self.coordinator.async_request_refresh()
