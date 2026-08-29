"""Config flow for AlgoPattern integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AlgoPatternApiClient, AlgoPatternAuthError, AlgoPatternApiError
from .const import (
    CONF_ACCESS_TOKEN,
    CONF_EMAIL,
    CONF_EXPIRES_AT,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_REFRESH_TOKEN,
    CONF_USER_ID,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def validate_email_credentials(
    hass: HomeAssistant, email: str, password: str
) -> dict[str, Any]:
    """Validate user email/password credentials against AlgoPattern server."""
    session = async_get_clientsession(hass)
    client = AlgoPatternApiClient(session)
    resp = await client.async_sign_in_email(email, password)
    return resp


async def validate_anonymous_signup(hass: HomeAssistant) -> dict[str, Any]:
    """Validate creating a fresh anonymous guest session on AlgoPattern server."""
    session = async_get_clientsession(hass)
    client = AlgoPatternApiClient(session)
    resp = await client.async_sign_up_anonymous()
    return resp


class AlgoPatternConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AlgoPattern."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            email = user_input[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]

            try:
                auth_data = await validate_email_credentials(self.hass, email, password)
                user_id = auth_data.get("user", {}).get("id", "")
                access_token = auth_data.get("access_token", "")
                refresh_token = auth_data.get("refresh_token", "")

                user_metadata = auth_data.get("user", {}).get("user_metadata", {})
                user_name = user_metadata.get("name") or user_metadata.get("full_name") or email

                await self.async_set_unique_id(user_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"AlgoPattern ({user_name})",
                    data={
                        CONF_USER_ID: user_id,
                        CONF_ACCESS_TOKEN: access_token,
                        CONF_REFRESH_TOKEN: refresh_token,
                        CONF_EMAIL: email,
                        CONF_NAME: user_name,
                    },
                )
            except AlgoPatternAuthError:
                errors["base"] = "invalid_auth"
            except AlgoPatternApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception in email login flow")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
