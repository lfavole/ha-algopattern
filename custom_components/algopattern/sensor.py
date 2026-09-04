"""Sensor platform for AlgoPattern integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SENSOR_DAILY_QUIZ_QUESTIONS_COMPLETED,
    SENSOR_FREEZES_AVAILABLE,
    SENSOR_LAST_ACTIVE_DATE,
    SENSOR_QUIZZES_COMPLETED,
    SENSOR_STREAK_LENGTH,
    SENSOR_TOTAL_ACTIVE_DAYS,
    SENSOR_USER_ID,
    SENSOR_USER_NAME,
    SENSOR_XP,
)
from .coordinator import AlgoPatternDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class AlgoPatternSensorEntityDescription(SensorEntityDescription):
    """Describes an AlgoPattern sensor entity."""

    value_fn: Callable[[dict[str, Any]], Any]
    extra_attrs_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None


# Definition of all sensor entities:
# Pertinent information (streak, XP, streak freezes) is enabled by default.
# Diagnostic and configuration metadata is available in the entity registry but disabled by default.
SENSOR_DESCRIPTIONS: tuple[AlgoPatternSensorEntityDescription, ...] = (
    # --- PERTINENT SENSORS (ENABLED BY DEFAULT) ---
    AlgoPatternSensorEntityDescription(
        key=SENSOR_STREAK_LENGTH,
        translation_key=SENSOR_STREAK_LENGTH,
        name="Streak Length",
        icon="mdi:fire",
        native_unit_of_measurement="days",
        state_class=SensorStateClass.TOTAL,
        entity_registry_enabled_default=True,
        value_fn=lambda data: data.get("streak_length", 0),
        extra_attrs_fn=lambda data: {
            "active_dates": data.get("active_dates", []),
            "active_today": data.get("active_today", False),
            "completed_today": data.get("completed_today", False),
            "freezes_available": data.get("freezes_available", 0),
            "active_days_count": data.get("active_days_count", 0),
            "last_active_date": data.get("last_active_date", "None"),
        },
    ),
    AlgoPatternSensorEntityDescription(
        key=SENSOR_XP,
        translation_key=SENSOR_XP,
        name="Total XP",
        icon="mdi:star-circle",
        native_unit_of_measurement="XP",
        state_class=SensorStateClass.TOTAL,
        entity_registry_enabled_default=True,
        value_fn=lambda data: data.get("xp", 0),
        extra_attrs_fn=lambda data: {
            "daily_quiz_day": data.get("daily_quiz_day", 0),
        },
    ),
    AlgoPatternSensorEntityDescription(
        key=SENSOR_DAILY_QUIZ_QUESTIONS_COMPLETED,
        translation_key=SENSOR_DAILY_QUIZ_QUESTIONS_COMPLETED,
        name="Daily Quiz Questions Completed",
        icon="mdi:help-box-multiple",
        native_unit_of_measurement="questions",
        state_class=SensorStateClass.TOTAL,
        entity_registry_enabled_default=True,
        value_fn=lambda data: data.get("daily_quiz_questions_completed", 0),
    ),
    AlgoPatternSensorEntityDescription(
        key=SENSOR_FREEZES_AVAILABLE,
        translation_key=SENSOR_FREEZES_AVAILABLE,
        name="Streak Freezes Available",
        icon="mdi:snowflake",
        native_unit_of_measurement="freezes",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        value_fn=lambda data: data.get("freezes_available", 0),
    ),
    # --- DIAGNOSTIC & CONFIGURATION SENSORS (AVAILABLE, DISABLED BY DEFAULT) ---
    AlgoPatternSensorEntityDescription(
        key=SENSOR_TOTAL_ACTIVE_DAYS,
        translation_key=SENSOR_TOTAL_ACTIVE_DAYS,
        name="Total Active Days",
        icon="mdi:calendar-check",
        native_unit_of_measurement="days",
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.get("active_days_count", len(data.get("active_dates", []))),
    ),
    AlgoPatternSensorEntityDescription(
        key=SENSOR_LAST_ACTIVE_DATE,
        translation_key=SENSOR_LAST_ACTIVE_DATE,
        name="Last Active Date",
        icon="mdi:calendar-clock",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.get("last_active_date", "None"),
    ),
    AlgoPatternSensorEntityDescription(
        key=SENSOR_QUIZZES_COMPLETED,
        translation_key=SENSOR_QUIZZES_COMPLETED,
        name="Quizzes Completed",
        icon="mdi:checkbox-multiple-marked-circle-outline",
        native_unit_of_measurement="quizzes",
        state_class=SensorStateClass.TOTAL,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.get("daily_quiz_day", 0),
    ),
    AlgoPatternSensorEntityDescription(
        key=SENSOR_USER_ID,
        translation_key=SENSOR_USER_ID,
        name="User ID",
        icon="mdi:account-key",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.get("user_id", ""),
    ),
    AlgoPatternSensorEntityDescription(
        key=SENSOR_USER_NAME,
        translation_key=SENSOR_USER_NAME,
        name="User Name",
        icon="mdi:account",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("name", ""),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AlgoPattern sensors from a config entry."""
    coordinator: AlgoPatternDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        AlgoPatternSensorEntity(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class AlgoPatternSensorEntity(
    CoordinatorEntity[AlgoPatternDataUpdateCoordinator], SensorEntity
):
    """Representation of an AlgoPattern sensor."""

    entity_description: AlgoPatternSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AlgoPatternDataUpdateCoordinator,
        description: AlgoPatternSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
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
    def native_value(self) -> Any:
        """Return the state value from coordinator data."""
        if not self.coordinator.data:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional state attributes if defined."""
        if (
            self.entity_description.extra_attrs_fn
            and self.coordinator.data is not None
        ):
            return self.entity_description.extra_attrs_fn(self.coordinator.data)
        return None
