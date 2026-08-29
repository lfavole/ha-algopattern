"""DataUpdateCoordinator for AlgoPattern."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AlgoPatternApiClient, AlgoPatternAuthError, AlgoPatternApiError
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_REFRESH_TOKEN,
    CONF_USER_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class AlgoPatternDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching AlgoPattern data from AlgoPattern server backend."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        api: AlgoPatternApiClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self.api = api
        self.config_entry = entry
        self.user_id = entry.data.get(CONF_USER_ID, "")
        self.access_token = entry.data.get(CONF_ACCESS_TOKEN, "")
        self.refresh_token = entry.data.get(CONF_REFRESH_TOKEN, "")

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.user_id}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch all account statistics, streak, and preferences from AlgoPattern server."""
        try:
            data = await self.api.async_fetch_all_account_data(
                user_id=self.user_id,
                access_token=self.access_token,
                refresh_token=self.refresh_token,
            )
            # Ensure name from config entry is used if API didn't fetch one
            if not data.get("name") or data.get("name") == "AlgoPattern User":
                data["name"] = self.config_entry.data.get("name", "AlgoPattern User")
            # Update access token if refreshed
            new_token = data.get("access_token")
            if new_token and new_token != self.access_token:
                self.access_token = new_token
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={**self.config_entry.data, CONF_ACCESS_TOKEN: new_token},
                )
            return data
        except AlgoPatternAuthError as err:
            _LOGGER.warning("Authentication failed during coordinator update: %s", err)
            raise ConfigEntryAuthFailed(f"AlgoPattern auth expired: {err}") from err
        except AlgoPatternApiError as err:
            _LOGGER.error("API error during coordinator update: %s", err)
            raise UpdateFailed(f"Error communicating with AlgoPattern API: {err}") from err
        except Exception as err:
            _LOGGER.exception("Unexpected error communicating with AlgoPattern: %s", err)
            raise UpdateFailed(f"Unexpected error: {err}") from err
