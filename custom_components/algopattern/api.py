"""Asynchronous AlgoPattern server API Client for AlgoPattern."""
from __future__ import annotations

import logging
import time
from typing import Any

import aiohttp

from .const import SUPABASE_ANON_KEY, SUPABASE_URL

_LOGGER = logging.getLogger(__name__)


class AlgoPatternAuthError(Exception):
    """Authentication or token expired error."""


class AlgoPatternApiError(Exception):
    """General AlgoPattern server API error."""


class AlgoPatternApiClient:
    """Async client communicating with AlgoPattern server backend for AlgoPattern."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        base_url: str = SUPABASE_URL,
        anon_key: str = SUPABASE_ANON_KEY,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._anon_key = anon_key

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        access_token: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Execute an asynchronous HTTP request against AlgoPattern server REST/Auth API."""
        url = f"{self._base_url}{endpoint}"
        req_headers = {
            "apikey": self._anon_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        token = access_token or self._anon_key
        req_headers["Authorization"] = f"Bearer {token}"
        if headers:
            req_headers.update(headers)

        try:
            async with self._session.request(
                method, url, json=data if data is not None else None, headers=req_headers, timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                if response.status in (401, 403):
                    err_text = await response.text()
                    _LOGGER.warning("AlgoPattern server auth error (%s): %s", response.status, err_text)
                    raise AlgoPatternAuthError(f"Authentication failed ({response.status}): {err_text}")

                if response.status >= 400:
                    err_text = await response.text()
                    _LOGGER.error("AlgoPattern server API error (%s): %s", response.status, err_text)
                    raise AlgoPatternApiError(f"HTTP {response.status}: {err_text}")

                if response.status == 204:
                    return None

                return await response.json()
        except (aiohttp.ClientError, TimeoutError) as ex:
            _LOGGER.error("Network communication error with AlgoPattern server: %s", ex)
            raise AlgoPatternApiError(f"Network error: {ex}") from ex

    # -------------------------------------------------------------
    # Authentication Methods
    # -------------------------------------------------------------

    async def async_sign_in_email(self, email: str, password: str) -> dict[str, Any]:
        """Sign in with email and password."""
        return await self._request(
            "POST",
            "/auth/v1/token?grant_type=password",
            data={"email": email, "password": password},
        )

    async def async_refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh an expired access token."""
        return await self._request(
            "POST",
            "/auth/v1/token?grant_type=refresh_token",
            data={"refresh_token": refresh_token},
        )

    # -------------------------------------------------------------
    # RPC & Data Retrieval Methods
    # -------------------------------------------------------------

    async def async_get_streak_status(self, user_id: str, access_token: str) -> dict[str, Any]:
        """Get live streak and XP stats from AlgoPattern server RPC."""
        res = await self._request(
            "POST",
            "/rest/v1/rpc/get_streak_status",
            data={"p_user_id": user_id},
            access_token=access_token,
        )
        return res or {
            "xp": 0,
            "active_dates": [],
            "active_today": False,
            "streak_length": 0,
            "completed_today": False,
            "freezes_available": 0,
        }

    async def async_get_profile(self, user_id: str, access_token: str) -> dict[str, Any] | None:
        """Fetch user profile record from profiles table."""
        res = await self._request(
            "GET",
            f"/rest/v1/profiles?id=eq.{user_id}&select=*",
            access_token=access_token,
        )
        if isinstance(res, list) and len(res) > 0:
            return res[0]
        return None

    async def async_get_user_preferences(self, user_id: str, access_token: str) -> dict[str, Any]:
        """Fetch user preferences record from user_preferences table."""
        res = await self._request(
            "GET",
            f"/rest/v1/user_preferences?user_id=eq.{user_id}&select=*",
            access_token=access_token,
        )
        if isinstance(res, list) and len(res) > 0:
            return res[0]
        return {}

    async def async_update_user_preferences(self, user_id: str, access_token: str, updates: dict[str, Any]) -> Any:
        """Update user preferences record in user_preferences table."""
        return await self._request(
            "PATCH",
            f"/rest/v1/user_preferences?user_id=eq.{user_id}",
            data=updates,
            access_token=access_token,
        )

    # -------------------------------------------------------------
    # Aggregated Account Data
    # -------------------------------------------------------------

    async def async_fetch_all_account_data(
        self, user_id: str, access_token: str, refresh_token: str | None = None
    ) -> dict[str, Any]:
        """Fetch consolidated account statistics, streak, preferences, and settings."""
        # 1. Fetch Streak Status
        streak_data: dict[str, Any] = {}
        try:
            streak_data = await self.async_get_streak_status(user_id, access_token)
        except AlgoPatternAuthError:
            # Token might be expired; attempt refresh if refresh_token available
            if refresh_token:
                refreshed = await self.async_refresh_token(refresh_token)
                new_token = refreshed.get("access_token")
                if new_token:
                    access_token = new_token
                    streak_data = await self.async_get_streak_status(user_id, access_token)
            else:
                raise

        # 2. Fetch Profile
        profile_data: dict[str, Any] = {}
        try:
            prof = await self.async_get_profile(user_id, access_token)
            if prof:
                profile_data = prof
        except Exception as ex:
            _LOGGER.debug("Could not fetch profile: %s", ex)

        # 3. Fetch User Preferences
        prefs_data: dict[str, Any] = {}
        try:
            prefs_data = await self.async_get_user_preferences(user_id, access_token)
        except Exception as ex:
            _LOGGER.debug("Could not fetch preferences: %s", ex)

        # Calculate active dates summary
        active_dates = streak_data.get("active_dates", [])
        active_days_count = len(active_dates)
        last_active_date = active_dates[-1] if active_dates else "None"

        # Combine all fields into a single comprehensive data dictionary

        # Extract user name from one of the responses
        user_name = (
            profile_data.get("name") or profile_data.get("full_name") or
            prefs_data.get("name") or prefs_data.get("full_name") or
            streak_data.get("name") or streak_data.get("full_name") or
            "AlgoPattern User"
        )

        return {
            "name": user_name,
            "user_id": user_id,
            "access_token": access_token,
            "xp": streak_data.get("xp", profile_data.get("xp", 0)),
            "is_pro": bool(profile_data.get("is_pro", False)),
            "streak_length": int(streak_data.get("streak_length", 0)),
            "active_today": bool(streak_data.get("active_today", False)),
            "completed_today": bool(streak_data.get("completed_today", False)),
            "freezes_available": int(streak_data.get("freezes_available", 0)),
            "active_dates": active_dates,
            "active_days_count": active_days_count,
            "last_active_date": last_active_date,
            "daily_quiz_day": int(profile_data.get("daily_quiz_day", 0)),
            "experience_level": prefs_data.get("experience_level", "Intermediate"),
            "preparation_goal": prefs_data.get("preparation_goal", "Tech Interview Prep"),
            "daily_reminder_time": prefs_data.get("daily_reminder_time", "17:00"),
            "daily_reminder_enabled": bool(prefs_data.get("daily_reminder_enabled", False)),
            "immediate_quiz_feedback": bool(prefs_data.get("immediate_quiz_feedback", False)),
        }
