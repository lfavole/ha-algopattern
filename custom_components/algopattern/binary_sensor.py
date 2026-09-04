"""Binary sensor platform for AlgoPattern integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    BINARY_SENSOR_ACTIVE_TODAY,
    BINARY_SENSOR_COMPLETED_TODAY,
    DOMAIN,
)
from .coordinator import AlgoPatternDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class AlgoPatternBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes an AlgoPattern binary sensor entity."""

    is_on_fn: Callable[[dict[str, Any]], bool]


# Definition of binary sensor entities:
# Pertinent daily activity sensors are enabled by default.
# Diagnostic flags are available in entity registry but disabled by default.
BINARY_SENSOR_DESCRIPTIONS: tuple[AlgoPatternBinarySensorEntityDescription, ...] = (
    # --- PERTINENT BINARY SENSORS (ENABLED BY DEFAULT) ---
    AlgoPatternBinarySensorEntityDescription(
        key=BINARY_SENSOR_COMPLETED_TODAY,
        translation_key=BINARY_SENSOR_COMPLETED_TODAY,
        name="Daily Challenge Completed",
        icon="mdi:check-decagram",
        entity_registry_enabled_default=True,
        is_on_fn=lambda data: bool(data.get("completed_today", False)),
    ),
    AlgoPatternBinarySensorEntityDescription(
        key=BINARY_SENSOR_ACTIVE_TODAY,
        translation_key=BINARY_SENSOR_ACTIVE_TODAY,
        name="Active Today",
        icon="mdi:calendar-today",
        entity_registry_enabled_default=True,
        is_on_fn=lambda data: bool(data.get("active_today", False)),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AlgoPattern binary sensors from a config entry."""
    coordinator: AlgoPatternDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        AlgoPatternBinarySensorEntity(coordinator, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class AlgoPatternBinarySensorEntity(
    CoordinatorEntity[AlgoPatternDataUpdateCoordinator], BinarySensorEntity
):
    """Representation of an AlgoPattern binary sensor."""

    entity_description: AlgoPatternBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AlgoPatternDataUpdateCoordinator,
        description: AlgoPatternBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
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
        """Return True if the binary sensor is on."""
        if not self.coordinator.data:
            return False
        return self.entity_description.is_on_fn(self.coordinator.data)
